"""Subset selection and execution guards for the native multimodel launcher."""
import asyncio
import json
from pathlib import Path
import types
import pytest

from experiments.multimodel_recovery_20260919 import campaign as campaign_module
SUBSET=['worker-03','worker-04','worker-05','worker-06']

@pytest.fixture
def campaign():
    return campaign_module


def test_default_and_subset_prepare(campaign,tmp_path):
    assert len(campaign.selected_workers())==10
    root=tmp_path/'four';plan=campaign.prepare(root,SUBSET)
    assert [w[0] for w in plan['workers']]==SUBSET
    assert plan['max_workers']==4
    assert sorted(p.name for p in root.glob('worker-*'))==SUBSET
    assert campaign.check_plan(root)['workers']==[list(w) for w in plan['workers']]


@pytest.mark.parametrize('names',[[],['worker-03','worker-03'],['worker-11'],['worker-03','bad'],'worker-03',[None]])
def test_invalid_selection_rejected_before_directory_creation(campaign,tmp_path,names):
    root=tmp_path/'invalid'
    with pytest.raises(ValueError):campaign.prepare(root,names)
    assert not root.exists()


@pytest.mark.parametrize('mutation',['duplicate','wrong_model','empty','max_workers'])
def test_plan_identity_guards(campaign,tmp_path,mutation):
    root=tmp_path/'four';campaign.prepare(root,SUBSET)
    plan=json.loads((root/'plan.json').read_text())
    if mutation=='duplicate':plan['workers'][1]=plan['workers'][0]
    if mutation=='wrong_model':plan['workers'][0][1]='kimi'
    if mutation=='empty':plan['workers']=[]
    if mutation=='max_workers':plan['max_workers']=10
    (root/'plan.json').write_text(json.dumps(plan))
    with pytest.raises(ValueError,match='worker subset'):campaign.check_plan(root)


def test_execute_refuses_nonselected_valid_worker(campaign,tmp_path):
    root=tmp_path/'four';campaign.prepare(root,SUBSET)
    with pytest.raises(ValueError,match='unknown worker'):asyncio.run(campaign.execute(root,'worker-01'))
    assert not (root/'worker-01').exists()


def test_coordinator_spawns_only_frozen_subset(campaign,tmp_path,monkeypatch):
    root=tmp_path/'four';campaign.prepare(root,SUBSET);started=[]
    class Child:
        returncode=None
        def __init__(self,pid):self.pid=pid
        async def wait(self):self.returncode=0;return 0
        def terminate(self):self.returncode=-15
        def kill(self):self.returncode=-9
    async def create(*args,**kwargs):
        started.append(args[args.index('--name')+1]);return Child(len(started))
    monkeypatch.setattr(campaign.asyncio,'create_subprocess_exec',create)
    async def run():
        monkeypatch.setattr(asyncio.get_running_loop(),'add_signal_handler',lambda *a:None)
        return await campaign.coordinate(root)
    result=asyncio.run(run())
    assert started==SUBSET
    assert set(result['workers'])==set(SUBSET)
    assert all(w['exit_code']==0 for w in result['workers'].values())
