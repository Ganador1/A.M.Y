"""Bounded, replayable scientific tools. No cloud calls and no novelty claims."""
from __future__ import annotations

from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BEST = ROOT / 'output/amy-audit-20260912/best-candidate.json'
BEST_SHA256 = 'b519e9ec0120174b06c0eb3e51613a5117b977f128d42f9cfaeb5f64f3e12e5b'


def describe():
    return {
        'ar1_benchmark': 'Parameters window:64|128, detrend:none|linear, seed_block:0..9. Paired raw baseline; 128 calibration and 128 held-out evaluation trajectories per arm; null stationary phi=.6, nuisance positive deterministic trend, positive increasing phi=.2..9. Empirical benchmark, not proof or discovery.',
        'ssh_fixed_resource': 'Parameters hoppings:list of exactly21 rational strings, each in[1/4,7/4], exact sum21. Optional iterations:0..8. Maximizes certified squared finite-chain half-filling gap under fixed resource; no rescaling permitted, no topology/novelty claim.',
        'autocorrelation_search': 'Parameters mode:all|pair_split|warm_all, iterations:1..20, seconds:1..30. Actual LP proposal search from frozen best1920cell witness; exact independent verification. A lower bound, not global optimality or novelty.',
    }


def _integer(value, lower, upper, name):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f'{name} must be integer in [{lower},{upper}]')
    return value


def _rate(count, n):
    p = count / n
    z = 1.959963984540054
    den = 1 + z*z/n
    center = (p + z*z/(2*n))/den
    radius = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return {'count': int(count), 'n': n, 'rate': p,
            'wilson95': [float(center-radius), float(center+radius)]}


def _series(seed, arm, n=512):
    rng = np.random.default_rng(seed)
    # Stationary burn-in precedes all arms; paired innovations across arms.
    innovations = rng.normal(size=(128, n+256))
    x = np.zeros_like(innovations)
    for t in range(1, n+256):
        phi = .6 if arm != 'increasing_phi' else (.2 + .7*max(0, t-256)/(n-1))
        x[:, t] = phi*x[:, t-1] + innovations[:, t]
    x = x[:, 256:]
    if arm == 'positive_trend':
        x = x + np.linspace(0, 8, n)
    return x


def _scores(x, window, detrend):
    vals = []
    grid = np.arange(window, dtype=float)
    grid -= grid.mean()
    for start in range(0, x.shape[1]-window+1, 16):
        y = x[:, start:start+window].copy()
        y -= y.mean(axis=1, keepdims=True)
        if detrend == 'linear':
            y -= ((y@grid)/(grid@grid))[:, None]*grid
        a, b = y[:, :-1], y[:, 1:]
        a = a-a.mean(axis=1, keepdims=True)
        b = b-b.mean(axis=1, keepdims=True)
        vals.append((a*b).sum(axis=1)/np.sqrt((a*a).sum(axis=1)*(b*b).sum(axis=1)))
    lag1 = np.array(vals).T
    time = np.linspace(0, 1, lag1.shape[1]); time -= time.mean()
    return lag1@time/(time@time)


def ar1_benchmark(p):
    if set(p)-{'window','detrend','seed_block'}:
        raise ValueError('unknown AR1 parameter')
    window = p.get('window', 64)
    if type(window) is not int or window not in (64, 128):
        raise ValueError('window must be64 or128')
    detrend = p.get('detrend', 'linear')
    if detrend not in ('none', 'linear'):
        raise ValueError('unknown detrending')
    block = _integer(p.get('seed_block', 0), 0, 9, 'seed_block')
    cal_seed, eval_seed = 190000+2*block, 190001+2*block
    cal = _series(cal_seed, 'stationary_null')
    arms = {arm: _series(eval_seed, arm) for arm in ('stationary_null','positive_trend','increasing_phi')}
    results = {}
    for method in dict.fromkeys([detrend, 'none']):
        calibration = _scores(cal, window, method)
        # Strict exceedance of conservative empirical 95th percentile.
        threshold = float(np.quantile(calibration, .95, method='higher'))
        evaluation = {arm: _scores(x, window, method) for arm, x in arms.items()}
        results[method] = {'threshold': threshold, 'calibration_scores': calibration.tolist(),
                           'evaluation_scores': {k: v.tolist() for k,v in evaluation.items()},
                           'rates': {k: _rate(int((v>threshold).sum()),len(v)) for k,v in evaluation.items()}}
    return {'success': True, 'kind': 'simulation_benchmark', 'parameters': {'window':window,'detrend':detrend,'seed_block':block},
            'calibration_seed':cal_seed,'evaluation_seed':eval_seed,'trajectories_per_arm':128,
            'definition': 'OLS slope of overlapping rolling lag1 Pearson correlations; stride16; independently calibrated threshold per method; strict exceedance.',
            'results':results, 'novelty_established':False,
            'scope':'Finite Monte Carlo estimates, not exact certificates. Within-run seeds held out; adaptive comparisons across repeated blocks are exploratory, not a fresh confirmatory holdout. Positive deterministic trend is a nuisance null; increasing phi is the positive control.'}


def ssh_fixed_resource(p):
    from atlas.app.ssh_certificate_tool import ssh_gap_certificate, decode_gap_certificate
    from atlas.app.ssh_spectral_certificate import verify_gap_certificate
    if set(p)-{'hoppings','iterations'}:
        raise ValueError('unknown SSH parameter')
    raw = p.get('hoppings')
    if not isinstance(raw,list) or len(raw)!=21:
        raise ValueError('exactly21 hoppings (22sites) required')
    if any(type(v) not in (str,int) or len(str(v))>64 for v in raw):
        raise ValueError('bounded rational strings or integers required')
    # Reject huge exponents before Fraction allocation.
    if any('e' in str(v).lower() for v in raw):
        raise ValueError('use integer, decimal, or numerator/denominator without exponent')
    hops = [F(v) for v in raw]
    if any(not F(1,4)<=v<=F(7,4) or max(v.numerator.bit_length(),v.denominator.bit_length())>64 for v in hops):
        raise ValueError('each hopping must lie in[1/4,7/4] with64bit rationals')
    if sum(hops)!=21:
        raise ValueError('fixed resource requires exact sum21; rescaling rejected')
    iterations = _integer(p.get('iterations',4),0,8,'iterations')
    response = ssh_gap_certificate(json.dumps({'hoppings':[str(v) for v in hops],'iterations':iterations}))
    if response.startswith('Error:'):
        raise ValueError(response)
    result = json.loads(response)
    exact = decode_gap_certificate(result['certificate'])
    if exact['hoppings'] != hops or not verify_gap_certificate(exact):
        raise ValueError('independent exact verification failed')
    result.update(fixed_resource={'hoppings':21,'sites':22,'sum':'21','minimum':'1/4','maximum':'7/4'},
                  independent_verified=True, squared_gap_lower=str(exact['gap_squared_lower']),
                  squared_gap_upper=str(exact['gap_squared_upper']),novelty_established=False)
    return result


def autocorrelation_search(p, output):
    from experiments.autocorrelation_resilient_20260909.engine import run as search
    from experiments.autocorrelation_exact_20260906.verifier import verify_document
    if set(p)-{'mode','iterations','seconds'}:
        raise ValueError('unknown autocorrelation parameter')
    mode = p.get('mode','pair_split')
    if mode not in ('all','pair_split','warm_all'):
        raise ValueError('unknown search mode')
    iterations = _integer(p.get('iterations',4),1,20,'iterations')
    seconds = _integer(p.get('seconds',10),1,30,'seconds')
    raw = BEST.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=BEST_SHA256:
        raise ValueError('frozen best witness changed')
    baseline = verify_document(json.loads(raw))
    result = search(BEST,output/'search',factor=1,seconds=seconds,iterations=iterations,mode=mode)
    candidate = json.loads((output/'search/candidate.json').read_text())
    checked = verify_document(candidate)
    ratio = checked['exact_ratio']
    if ratio!=F(result['exact_ratio']):
        raise ValueError('reported ratio differs from independent exact result')
    result.update(success=True, independent_verified=True, source_sha256=BEST_SHA256,
                  baseline_exact_ratio=str(baseline['exact_ratio']),strict_improvement=ratio>baseline['exact_ratio'],
                  candidate_path=str((output/'search/candidate.json').resolve()))
    return result


def run(name, parameters, output_dir):
    """Persist exact request and result; caller should retain/hash all output artifacts."""
    if name not in describe() or not isinstance(parameters,dict):
        raise ValueError('unknown tool or non-object parameters')
    output = Path(output_dir)
    output.mkdir(parents=True,exist_ok=False)
    request = {'name':name,'parameters':parameters}
    (output/'request.json').write_text(json.dumps(request,sort_keys=True,indent=2)+'\n')
    try:
        result = autocorrelation_search(parameters,output) if name=='autocorrelation_search' else globals()[name](parameters)
    except (ValueError,TypeError,KeyError,ZeroDivisionError) as exc:
        result = {'success':False,'error_type':type(exc).__name__,'error':str(exc)}
    (output/'result.json').write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n')
    return result
