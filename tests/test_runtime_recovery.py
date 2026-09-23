"""Recovery regression tests; real local sandbox, model boundary fixtures, no network."""
import copy
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from test_goal_focus import harness, start
from core import provenance
from core.provenance import ProvenanceManager
from core.runtime_receipts import ReceiptStore, action_succeeded
from core.memory_checkpoint import MemoryCheckpoints, reconstruct


async def test_code_receipt_is_visible_to_reasoning_reflection_and_restart(harness, tmp_path, monkeypatch):
    h=harness; hb=h.heartbeat
    monkeypatch.setattr(provenance,'_provenance',ProvenanceManager(tmp_path/'experiments'))
    hb.config['sandbox']={'use_docker':False,'max_execution_time':5,'max_memory_mb':256}
    await start(h)
    result=await hb._act_experiment({'hypothesis':'A fixed arithmetic fixture prints 42', 'code':'print(6*7)'})
    assert action_succeeded(result)
    identifier=result['result']['experiment_id'];receipt=hb._experiment_receipts[identifier]
    assert receipt['operational_observation']['output']['text'].strip()=='42'
    assert not receipt['certificate_verified'] and not receipt['scientific_truth_verified']
    await hb._think({'content':'Review actual measurement','source':'goal_stack','type':'goal'})
    assert identifier in json.dumps(h.last_context())
    h.transport.reply={'insights':[],'new_subgoals':[]}
    await hb._reflect()
    assert identifier in json.dumps(h.transport.calls[-1]['messages'])
    restored=ReceiptStore(hb._receipt_store.path)
    assert restored.index[identifier]==receipt
    assert restored.index[identifier]['retained_execution']['stdout']['sha256']


async def test_script_receipt_persists_even_failed_execution(harness,tmp_path):
    hb=harness.heartbeat;hb.config['sandbox']={'use_docker':False,'max_execution_time':5,'max_memory_mb':256}
    result=await hb._act_run_script({'script':'print(42)\nraise ValueError("control failure")','language':'python','purpose':'failure control'})
    assert not action_succeeded(result)
    rid=result['result']['experiment_id']
    assert hb._experiment_receipts[rid]['execution_success'] is False
    assert 'control failure' in hb._experiment_receipts[rid]['operational_observation']['stderr']['text']
    assert rid in ReceiptStore(hb._receipt_store.path).index


async def test_budget_retirement_does_not_turn_execution_into_verified_goal(harness):
    hb=harness.heartbeat;stack,ids=await start(harness,children=1);goal=stack.goals[ids[0]]
    for _ in range(goal.max_attempts):
        await hb._learn({'goal_id':goal.id,'action_type':'experiment','new_facts':[], 'content':'42 observed'},
                        {'type':'experiment','result':{'success':True}})
    assert goal.status.value=='deferred' and goal.completed_at is None
    assert 'execution_success=True' in goal.retirement_reason
    assert stack.goals[stack.mission_id].status.value=='active'


async def test_circuit_stops_before_another_action_or_reflection(harness):
    hb=harness.heartbeat;await start(harness)
    hb.config.update(max_consecutive_decision_failures=3,max_total_decision_failures=6,
                     max_cycles_before_reflection=100,focused_interval_seconds=0,idle_interval_seconds=0)
    hb._perceive=AsyncMock(return_value=[]);hb._attend=AsyncMock(return_value={'content':'fixture'})
    hb._think=AsyncMock(return_value={'action_type':'think_more','reasoning_failure':'transport','new_facts':[]})
    hb._act=AsyncMock(return_value={'type':'think_more'});hb._learn=AsyncMock(return_value=None);hb._check_breakthrough=AsyncMock(return_value=None);hb._reflect=AsyncMock(return_value=None)
    hb._running=True
    for n in range(3):hb.ctx.cycle_number=n+1;await hb._beat()
    assert not hb._running and hb.stop_reason=='decision_failure_circuit_open'
    assert hb._act.await_count==2 and hb._reflect.await_count==0


async def test_truncation_recovery_changes_request_not_model_or_config(harness):
    engine=harness.heartbeat.reasoning;before=copy.deepcopy(engine.config);calls=[]
    async def chat(**kwargs):
        calls.append(kwargs)
        if len(calls)==1:return {'done':True,'done_reason':'length','message':{'content':'{"action_type":"experiment"}'}}
        return {'done':True,'done_reason':'stop','message':{'content':'{"action_type":"think_more","content":"Recovered complete decision","new_facts":[]}'}}
    engine.client.chat=chat
    first=await engine.reason({},{});second=await engine.reason({},{})
    assert first['reasoning_failure']=='output_truncated'
    assert 'reasoning_failure' not in second
    assert calls[1]['think'] is False and calls[1]['max_tokens']<=8192
    assert calls[1]['model']==calls[0]['model'] and engine.config==before
    assert '4000 characters' in calls[1]['messages'][-1]['content']


def test_delta_removes_and_changes_entries_and_saves_space():
    recorder=MemoryCheckpoints(20);state={'cycle':0,'facts':{str(i):'x'*100 for i in range(100)}}
    first=recorder.encode(state);state['cycle']=1;del state['facts']['0'];state['facts']['1']='changed'
    second=recorder.encode(state)
    assert reconstruct(reconstruct(None,first),second)==state
    assert len(json.dumps(second))<len(json.dumps(first))/5
    second['maps']['facts']['upsert']['1']='tampered'
    with pytest.raises(ValueError,match='hash'):reconstruct(first['state'],second)


def test_receipt_store_rejects_tampering(tmp_path):
    p=tmp_path/'receipts.jsonl';store=ReceiptStore(p)
    store.add({'experiment_id':'test','execution_success':True,'certificate_verified':False})
    p.write_text(p.read_text().replace('"execution_success":true','"execution_success":false'))
    with pytest.raises(ValueError,match='integrity'):ReceiptStore(p)


async def test_reflection_can_disable_thinking_independently(harness):
    hb=harness.heartbeat;await start(harness)
    await hb.episodic_memory.record(event_type='observation',content='Fixture: arithmetic output 42')
    hb.reasoning.reasoner_think=True
    hb.reasoning.config['reflection']={'max_tokens':4096,'think':False}
    harness.transport.reply={'insights':[],'new_subgoals':[]}
    await hb._reflect()
    call=harness.transport.calls[-1]
    assert call['think'] is False and call['max_tokens']==4096
    assert hb.reasoning.reasoner_think is True
