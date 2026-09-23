"""Consumer-specific selection of complete model JSON, without byte repair."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from cognition.reasoning import (DecisionSchemaError, ReasoningEngine, _extract_content,
    _parse_decision_json, _parse_json_robust, _parse_reflection_json)


def decision(**updates):
    return {'action_type': 'think_more', 'content': 'Unverified fixture thought', **updates}


def test_actual_glm_response_rejects_ambiguous_draft_and_final_objects():
    retained = json.loads((Path(__file__).parent / 'fixtures/glm53-response-replay.json').read_text())
    response = retained['response']
    assert response.get('done') is not False and response.get('done_reason') != 'length'
    text = _extract_content(response)
    # The generic parser remains untouched: it incorrectly served this consumer.
    assert _parse_json_robust(text) == {'window': 64, 'detrend': 'none', 'seed_block': 0}
    # Complete strict scanning now finds a draft and final decision without an
    # explicit boundary. V1 accepted this only because its scanner missed one.
    with pytest.raises(DecisionSchemaError, match='exactly one'):
        _parse_decision_json(text, ['run_scientific_tool', 'finish_session'])



@pytest.mark.parametrize('text', [
    '{}', '{"window":64}', 'null', json.dumps({'action_type':'think_more'}),
    json.dumps(decision(content='  ')), json.dumps(decision(action_type='invented')),
    json.dumps(decision()) + json.dumps(decision()),
    '{"action_type":"think_more","content":"unterminated',
    '{"action_type":"think_more","content":"x",}',
    '{"action_type":"think_more","content":"x","content":"y"}',
    json.dumps({'wrapper': decision()}), json.dumps([decision()]),
])
def test_invalid_or_ambiguous_objects_fail_closed(text):
    with pytest.raises(DecisionSchemaError):
        _parse_decision_json(text)


def test_strings_nested_parameters_and_enabled_actions():
    obj = decision(content='Literal brace } and escaped quote " are ordinary strings.',
                   action_details={'tool_input': '{"action_type":"example"}'},
                   quantitative_assessment={'counts': [3, 7], 'interpretation': 'fixture only'})
    assert _parse_decision_json('Example {"p":1}. ```json\n' + json.dumps(obj) + '\n```') == obj
    with pytest.raises(DecisionSchemaError, match='disabled'):
        _parse_decision_json(json.dumps(decision(action_type='finish_session')), ['think_more'])


@pytest.mark.asyncio
@pytest.mark.parametrize('done,reason', [(False,'stop'), (True,'length')])
async def test_incomplete_envelope_never_executes_complete_decision(done,reason):
    engine = object.__new__(ReasoningEngine)
    engine.config = {'reasoner': {}}
    engine.reasoner_model, engine.reasoner_ctx = 'fixture', 32768
    engine._build_reasoning_prompt = lambda *args: []
    async def chat(**kwargs):
        return {'done':done, 'done_reason':reason, 'message': {'content':json.dumps(decision())}}
    engine.client = SimpleNamespace(chat=chat)
    result = await engine.reason({}, {}, None)
    assert result['reasoning_failure'] == 'output_truncated'
    assert result['action_type'] == 'think_more'


@pytest.mark.asyncio
async def test_parameter_only_response_is_typed_failure_not_successful_thought():
    engine = object.__new__(ReasoningEngine)
    engine.config = {'reasoner': {}}
    engine.reasoner_model, engine.reasoner_ctx = 'fixture', 32768
    engine._build_reasoning_prompt = lambda *args: []
    async def chat(**kwargs):
        return {'done':True,'done_reason':'stop','message':{'content':'{"window":64}'}}
    engine.client = SimpleNamespace(chat=chat)
    result = await engine.reason({}, {}, None)
    assert result['reasoning_failure'] == 'decision_schema_error'


def test_reflection_selects_schema_not_parameter_example():
    obj = {'diagnosis':'Fixture only','new_subgoals':[], 'insights':[]}
    assert _parse_reflection_json('{"window":64}\n' + json.dumps(obj)) == obj
    for raw in ('{"window":64}', json.dumps(obj)*2, '{"new_subgoals":"not a list"}'):
        with pytest.raises(ValueError):
            _parse_reflection_json(raw)
