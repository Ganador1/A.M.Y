"""Explicit session closure preserves evidence without claiming scientific success."""
import copy,json
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from test_goal_focus import harness,start
from cognition.goal_stack import GoalStatus

def closing():
    return {'action_type':'finish_session','content':'FINAL SYNTHESIS: fixture assertion, not verified.',
            'session_summary':{'reason':'No further justified work in this fixture','experiment_ids':[],
                               'unresolved':['Scientific objective remains unresolved'],'next_steps':['Another experiment']},
            'new_facts':[{'subject':'fixture','predicate':'claims','object':'2+2=5','confidence':1.0}]}

async def test_native_loop_finishes_after_learning_without_auxiliary_models_or_goal_completion(harness):
    h=harness;hb=h.heartbeat;await start(h);root=hb.goal_stack.mission_id
    hb.config.update(allowed_actions=['think_more','finish_session'],continuous_mission=True,
                     max_cycles=5,max_cycles_before_reflection=1,base_interval_seconds=0,
                     focused_interval_seconds=0,idle_interval_seconds=0)
    hb._current_interval=0;hb.ctx.cycle_number=0;hb._mission_complete_streak=2
    hb._perceive=AsyncMock(return_value=[]) # only unused external sensors replaced
    hb.breakthrough_detector=SimpleNamespace(evaluate=AsyncMock(side_effect=AssertionError('unexpected breakthrough call')))
    worker=SimpleNamespace(close=AsyncMock());hb._atlas_tools=worker
    h.transport.reply=closing()
    await hb.run()
    assert hb.ctx.cycle_number==1 and hb._running is False and len(h.transport.calls)==1
    assert hb.goal_stack.mission_id==root and hb.goal_stack.goals[root].status is GoalStatus.ACTIVE
    assert hb.semantic_memory.facts=={} and len(hb.semantic_memory.claims)==1
    assert next(iter(hb.semantic_memory.claims.values()))['interpretation_verified'] is False
    worker.close.assert_awaited_once();hb.breakthrough_detector.evaluate.assert_not_awaited()
    episodes=await hb.episodic_memory.get_recent(n=50)
    assert any(e['event_type']=='cognitive_cycle' and e['content']==closing()['content'] for e in episodes)
    events=[json.loads(l) for l in h.evidence.events_path.read_text().splitlines()]
    stop,=[e for e in events if e['kind']=='run.session_finish']
    learned=next(e for e in events if e['kind']=='heartbeat.learn.end')
    assert learned['sequence']<stop['sequence']
    p=json.loads((h.evidence.path/stop['payload']['path']).read_text())
    assert p['scientific_goal_verified_complete'] is False
    assert p['action_result']['summary']['unresolved']==closing()['session_summary']['unresolved']
    assert not any(e['kind'] in ('mission.proposal.begin','reflection.pattern_extraction.begin','run.limit') for e in events)
    system=h.transport.calls[0]['messages'][0]['content']
    assert 'Enabled Session Actions' in system and 'finish_session closes this bounded session' in system

@pytest.mark.parametrize('allowlist',[None,['think_more']])
async def test_closure_requires_explicit_operator_action_allowlist(harness,allowlist):
    hb=harness.heartbeat
    if allowlist is not None:hb.config['allowed_actions']=allowlist
    hb._running=True
    result=await hb._act(closing())
    assert result['success'] is False and hb._running

@pytest.mark.parametrize('mutation',[
    {'session_summary':None}, {'content':''},
    {'session_summary':{'reason':'stop','experiment_ids':'not list','unresolved':[],'next_steps':[]}},
    {'session_summary':{'reason':'stop','experiment_ids':['fabricated'],'unresolved':[],'next_steps':[]}},
    {'session_summary':{'reason':'stop','experiment_ids':[],'unresolved':[None],'next_steps':[]}},
    {'session_summary':{'reason':'stop','experiment_ids':[],'unresolved':[],'next_steps':[],'success':True}},
])
async def test_bad_or_unknown_closure_evidence_keeps_session_running(harness,mutation):
    hb=harness.heartbeat;hb.config['allowed_actions']=['finish_session'];hb._running=True
    result=await hb._act({**closing(),**mutation})
    assert result['success'] is False and hb._running

async def test_accepted_summary_detached_and_close_not_applied_until_learning(harness):
    hb=harness.heartbeat;hb.config['allowed_actions']=['finish_session'];hb._running=True
    thought=closing();result=await hb._act(thought)
    assert result['success'] is True and hb._running
    thought['session_summary']['unresolved'].clear()
    assert result['summary']['unresolved']==['Scientific objective remains unresolved']
    assert result['scientific_goal_verified_complete'] is False and result['interpretation_verified'] is False
