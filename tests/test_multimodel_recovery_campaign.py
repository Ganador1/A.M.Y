import asyncio
import copy
import json
import pytest
from experiments.multimodel_recovery_20260919 import campaign,labs


def test_frozen_five_models_two_identical_tasks_isolated(tmp_path):
    root=tmp_path/'campaign';plan=campaign.prepare(root);campaign.check_plan(root)
    assert len(plan['workers'])==10
    configs={name:json.loads((root/name/'effective_config.json').read_text()) for name,_,_ in campaign.WORKERS}
    for branch in ('ar1_benchmark','h2_validation'):
        selected=[configs[name] for name,_,b in campaign.WORKERS if b==branch]
        assert len({c['mission']['goal'] for c in selected})==1
        assert {c['llm']['reasoner']['model'] for c in selected}==set(campaign.MODELS)
        for c in selected:
            assert c['heartbeat']['max_cycles']==10
            assert c['heartbeat']['operating_contract']==c['mission']['goal']
            assert c['llm']['reasoner']['think'] is False
            assert c['llm']['reasoner']['max_tokens']==8192
            assert c['llm']['reflection']=={'max_tokens':4096,'think':False}
            assert c['evidence']['provenance_per_run'] is True
    assert len({c['memory']['mission_memory_root'] for c in configs.values()})==10
    p=root/'worker-01/protocol.json';p.write_text(p.read_text()+' ')
    with pytest.raises(ValueError,match='Frozen source'):campaign.check_plan(root)


def test_ar1_fixed_cells_and_typed_synthesis(tmp_path):
    cell=tmp_path/'worker';cell.mkdir();lab=campaign.Laboratory(cell,'ar1_benchmark')
    async def perform():
        rejected=json.loads(await lab.run_scientific_tool('ar1_benchmark','{"regime":"null"}'))
        assert rejected['success'] is False
        assert (cell/'studies/m0001/result.json').exists()
        for parameters in labs.AR1_CELLS:
            result=json.loads(await lab.run_scientific_tool('ar1_benchmark',json.dumps(parameters)))
            assert result['success'] is True
        assert len(lab.successful_results)==3
    asyncio.run(perform())
    counts={f"{r['effective_input']['window']}:{r['effective_input']['detrend']}:{r['effective_input']['seed_block']}":
            r['results'][r['effective_input']['detrend']]['rates']['stationary_null']['count'] for r in lab.successful_results}
    thought={'session_summary':{'experiment_ids':['a','b','c']},'assessment':{'stationary_null_counts':counts,'trajectories_per_cell':128,'novelty_established':False}}
    result=lab.validate(thought,[])
    assert result['passed'] and result['quantified_fields_verified']
    assert result['assessment']==thought['assessment']
    thought['assessment']['stationary_null_counts']['64:none:0']+=1
    result=lab.validate(thought,[])
    assert not result['passed'] and not result['quantified_fields_verified']


def test_semantic_h2_duplicate_rejected_before_computation(tmp_path,monkeypatch):
    cell=tmp_path/'worker';cell.mkdir();lab=campaign.Laboratory(cell,'h2_validation');calls=[]
    async def fake(name,params,path):
        path.mkdir(parents=True);calls.append(params)
        result={'success':True,'effective_input':labs.normalized(name,params)}
        (path/'result.json').write_text(json.dumps(result));return result
    monkeypatch.setattr(lab,'_compute',fake)
    async def perform():
        first=json.loads(await lab.run_scientific_tool('h2_validation','{"distance_angstrom":"0.74"}'))
        second=json.loads(await lab.run_scientific_tool('h2_validation','{"distance_angstrom":"0.7400"}'))
        assert first['success'] is True and second['success'] is False
        assert 'Duplicate' in second['error'] and len(calls)==1
    asyncio.run(perform())
