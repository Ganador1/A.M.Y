"""Fixed-cell cross-model calibration; numerical tools, no model calls."""
import json
from fractions import Fraction
from pathlib import Path
from experiments.recovery_campaign_20260919 import labs as previous

AR1_CELLS = [dict(window=64,detrend='none',seed_block=0),dict(window=64,detrend='linear',seed_block=0),dict(window=128,detrend='linear',seed_block=1)]
H2_CELLS = [dict(distance_angstrom=d) for d in ('0.5','0.74','1.5')]

def describe():
    return {
      'ar1_benchmark': previous.describe()['ar1_benchmark']+' This comparison requires exactly the following three cells, in any order: '+json.dumps(AR1_CELLS)+'. Every request is one of these JSON objects. No additional fields. Each cell includes all control arms automatically; do not supply regime. No novelty claim.',
      'h2_validation': 'Fixed H2 RHF/STO-3G numerical-consistency study. Exactly these three requests in any order: '+json.dumps(H2_CELLS)+'. One field distance_angstrom only. Compare recorded energies only at these sampled geometries; never claim global equilibrium, exact physical energy, chemical accuracy, novelty, or fully independent integrals. Verifier uses independent algebra but shares supplied PySCF integrals. Each call also checks rejection of a deliberately corrupted total-energy certificate (negative control).'
    }

def normalized(name,p):
    if not isinstance(p,dict):raise ValueError('parameters must be object')
    if name=='ar1_benchmark':
        if set(p)!={'window','detrend','seed_block'} or type(p['window']) is not int or type(p['seed_block']) is not int or p not in AR1_CELLS:raise ValueError('Select one exact preregistered AR1 cell: '+json.dumps(AR1_CELLS))
        return p.copy()
    if name=='h2_validation':
        if set(p)!={'distance_angstrom'} or type(p['distance_angstrom']) not in (str,int,float):raise ValueError('Only distance_angstrom is accepted')
        raw=str(p['distance_angstrom'])
        if len(raw)>32 or 'e' in raw.lower():raise ValueError('Use short fixed decimal distance')
        try:value=Fraction(raw)
        except (ValueError,ZeroDivisionError):raise ValueError('Invalid distance')
        for cell in H2_CELLS:
            if Fraction(cell['distance_angstrom'])==value:return cell.copy()
        raise ValueError('Select distance_angstrom 0.5, 0.74 or 1.5')
    raise ValueError('unknown comparison tool')

def run(name,parameters,output_dir):
    import copy
    output=Path(output_dir);output.mkdir(parents=True,exist_ok=False)
    request={'name':name,'parameters':parameters}
    (output/'request.json').write_text(json.dumps(request,sort_keys=True,allow_nan=False)+'\n')
    try:
        p=normalized(name,parameters)
        if name=='ar1_benchmark':result=previous.ar1_benchmark(p)
        else:
            from atlas.app.h2_rhf_certificate import produce_h2_rhf_certificate
            from atlas.app.h2_rhf_verifier import verify_h2_rhf_certificate
            cert=produce_h2_rhf_certificate(p);audit=verify_h2_rhf_certificate(cert)
            altered=copy.deepcopy(cert);altered['state']['total_energy']+=0.1
            rejected=verify_h2_rhf_certificate(altered)
            (output/'certificate.json').write_text(json.dumps(cert,sort_keys=True,allow_nan=False)+'\n')
            (output/'audit.json').write_text(json.dumps(audit,sort_keys=True,allow_nan=False)+'\n')
            (output/'negative-control.json').write_text(json.dumps({'mutation':'state.total_energy += 0.1 Hartree','audit':rejected},sort_keys=True,allow_nan=False)+'\n')
            if not audit['valid'] or rejected['valid']:raise ValueError('Numerical verification or corruption control failed')
            result={'success':True,'parameters':p,'summary':cert['summary'],'numerical_consistency_verified':True,
                    'corrupted_energy_rejected':True,'rigorous_interval_bound':False,'independent_integral_engine':False,
                    'novelty_established':False,'scope':audit['scope'],'verification_failures':audit['failures']}
        result['effective_input']=p
    except (ValueError,TypeError,KeyError) as exc:result={'success':False,'error':str(exc)}
    (output/'result.json').write_text(json.dumps(result,sort_keys=True,allow_nan=False)+'\n')
    return result


def assessment_contract(branch):
    if branch=='h2_validation':
        return (' At finish_session include an additional TOP-LEVEL assessment object, separate from session_summary, with exactly these keys: '
                'distance_at_minimum_sampled_energy_angstrom (canonical string), minimum_sampled_energy_hartree (number), rigorous_physical_proof (false), independent_integral_engine (false). '
                'First select the recorded measurement with the smallest total_energy_hartree, then copy THAT SAME measurement’s distance_angstrom and energy into the two fields. Do not report the smallest distance independently of its energy. This is not a global optimum.')
    return (' At finish_session include an additional TOP-LEVEL assessment object, separate from session_summary, with exactly these keys: '
            'stationary_null_counts (object mapping "64:none:0", "64:linear:0", "128:linear:1" to their integer detection counts), '
            'trajectories_per_cell (128), novelty_established (false). Use the selected method of each cell, not the paired raw comparison. '
            'Do not pool repeated trajectories across cells as independent samples.')


def assessment_errors(branch, assessment, results):
    """Check a small typed claim, not freeform prose or scientific novelty."""
    import math
    if not isinstance(assessment,dict):return ['Missing top-level assessment. '+assessment_contract(branch)]
    try:
        if branch=='h2_validation':
            if set(assessment)!={'distance_at_minimum_sampled_energy_angstrom','minimum_sampled_energy_hartree','rigorous_physical_proof','independent_integral_engine'}:return ['Invalid H2 assessment keys. '+assessment_contract(branch)]
            best=min(results,key=lambda r:r['summary']['total_energy_hartree'])
            val=assessment['minimum_sampled_energy_hartree']
            if (type(val) not in (int,float) or not math.isfinite(val) or abs(val-best['summary']['total_energy_hartree'])>2e-8):return ['Minimum energy does not match recorded measurements to 2e-8 Hartree.']
            if assessment['distance_at_minimum_sampled_energy_angstrom']!=best['effective_input']['distance_angstrom']:return ['Distance must come from the same measurement as the minimum recorded energy, not from the smallest sampled distance.']
            if assessment['rigorous_physical_proof'] is not False or assessment['independent_integral_engine'] is not False:return ['Scope flags overstate numerical evidence.']
        else:
            if set(assessment)!={'stationary_null_counts','trajectories_per_cell','novelty_established'}:return ['Invalid AR1 assessment keys. '+assessment_contract(branch)]
            expected={f"{r['effective_input']['window']}:{r['effective_input']['detrend']}:{r['effective_input']['seed_block']}":r['results'][r['effective_input']['detrend']]['rates']['stationary_null']['count'] for r in results}
            counts=assessment['stationary_null_counts']
            if not isinstance(counts,dict) or any(type(v) is not int for v in counts.values()) or counts!=expected:return ['Stationary null counts do not match each selected method/cell.']
            if type(assessment['trajectories_per_cell']) is not int or assessment['trajectories_per_cell']!=128 or assessment['novelty_established'] is not False:return ['Invalid sample count or novelty assertion.']
    except (KeyError,ValueError,TypeError) as exc:return ['Incomplete/malformed measured assessment: '+str(exc)]
    return []
