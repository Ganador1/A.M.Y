import json
import pytest
from experiments.multimodel_recovery_20260919 import labs

def test_fixed_cells_and_canonical_distances():
    assert labs.normalized('h2_validation',{'distance_angstrom':'.7400'})=={'distance_angstrom':'0.74'}
    for p in ({'distance_angstrom':True},{'distance_angstrom':'0.8'},{'distance_angstrom':'1e99'}):
        with pytest.raises(ValueError):labs.normalized('h2_validation',p)
    with pytest.raises(ValueError):labs.normalized('ar1_benchmark',{'window':64,'detrend':'none','seed_block':False})

@pytest.mark.parametrize('distance',['0.5','0.74','1.5'])
def test_real_h2_and_corruption_guard(tmp_path,distance):
    r=labs.run('h2_validation',{'distance_angstrom':distance},tmp_path/'study')
    assert r['success'] and r['numerical_consistency_verified'] and r['corrupted_energy_rejected']
    assert not r['rigorous_interval_bound'] and not r['independent_integral_engine']
    negative=json.loads((tmp_path/'study/negative-control.json').read_text())
    assert not negative['audit']['valid'] and negative['audit']['failures']


def test_quantitative_gate_rejects_invented_energy_and_false_scope():
    results=[{'summary':{'total_energy_hartree':-1.1},'effective_input':{'distance_angstrom':'0.74'}}]
    valid={'distance_at_minimum_sampled_energy_angstrom':'0.74','minimum_sampled_energy_hartree':-1.1,'rigorous_physical_proof':False,'independent_integral_engine':False}
    assert labs.assessment_errors('h2_validation',valid,results)==[]
    assert labs.assessment_errors('h2_validation',{**valid,'minimum_sampled_energy_hartree':-2},results)
    assert labs.assessment_errors('h2_validation',{**valid,'independent_integral_engine':True},results)


def test_quantitative_gate_rejects_wrong_method_counts():
    results=[{'effective_input':{'window':64,'detrend':'linear','seed_block':0},'results':{'linear':{'rates':{'stationary_null':{'count':10}}},'none':{'rates':{'stationary_null':{'count':7}}}}}]
    valid={'stationary_null_counts':{'64:linear:0':10},'trajectories_per_cell':128,'novelty_established':False}
    assert labs.assessment_errors('ar1_benchmark',valid,results)==[]
    assert labs.assessment_errors('ar1_benchmark',{**valid,'stationary_null_counts':{'64:linear:0':7}},results)
