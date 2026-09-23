"""Frozen producer functions for deterministic replay; not an independent statistical method."""
import numpy as np

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
