"""Explicit final envelopes do not inherit escaped prose JSON parser state."""
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from cognition.reasoning import DecisionSchemaError, ReasoningEngine, _parse_decision_json, _parse_reflection_json


def decision(**kw):
    return {'action_type':'think_more', 'content':'Fixture only', **kw}


def test_real_flash_campaign02_final_envelope():
    fixture = json.loads((Path(__file__).parent/'fixtures/glmflash-campaign02-response.json').read_text())
    response = fixture['response']
    assert response['done_reason'] == 'stop'
    text = response['message']['content']
    assert text.find('</think>') == 4732
    result = _parse_decision_json(text)
    assert result['action_type'] == 'run_scientific_tool'
    assert result['action_details']['tool_name'] == 'ar1_benchmark'
    assert json.loads(result['action_details']['tool_input']) == {'window':64,'detrend':'none','seed_block':0}


@pytest.mark.parametrize('fenced',[False,True])
def test_escaped_example_does_not_trap_final_scanner(fenced):
    obj = decision(quantitative_assessment={'retained':True})
    tail = json.dumps(obj)
    if fenced:
        tail = '```json\n'+tail+'\n```'
    text = 'Tool input example "{\\"window\\":64}". </think>'+tail
    assert _parse_decision_json(text) == obj


def test_tags_inside_valid_json_strings_are_data():
    obj = decision(content='Quoted </think> and <think> delimiters are literal text.')
    assert _parse_decision_json(json.dumps(obj)) == obj
    assert _parse_decision_json('```json\n'+json.dumps(obj)+'\n```') == obj


@pytest.mark.parametrize('text',[
    'Prose </think>{"action_type":"think_more","content":"unfinished',
    'Prose </think>'+json.dumps(decision())+json.dumps(decision()),
    'Prose </think>'+json.dumps(decision())+' arbitrary trailing prose',
    'Prose </think> first </think>'+json.dumps(decision()),
    json.dumps(decision())+'</think>'+json.dumps(decision()),
    '{"broken":"</think>'+json.dumps(decision()),
    'Prose </think>'+json.dumps([decision()]),
    'Prose </think>{"action_type":"think_more","content":"a","content":"b"}',
])
def test_ambiguous_or_incomplete_envelopes_rejected(text):
    with pytest.raises(DecisionSchemaError):
        _parse_decision_json(text)


@pytest.mark.asyncio
async def test_explicit_envelope_never_bypasses_truncation_gate():
    engine = object.__new__(ReasoningEngine)
    engine.config = {'reasoner':{}}
    engine.reasoner_model,engine.reasoner_ctx = 'fixture',32768
    engine._build_reasoning_prompt = lambda *args: []
    async def chat(**kwargs):
        return {'done':True,'done_reason':'length','message':{'content':'Prose </think>'+json.dumps(decision())}}
    engine.client=SimpleNamespace(chat=chat)
    assert (await engine.reason({}, {}, None))['reasoning_failure'] == 'output_truncated'


def test_reflection_uses_same_strict_envelope_policy():
    obj = {'new_subgoals':[], 'knowledge_gaps':[], 'diagnosis':'Fixture only'}
    assert _parse_reflection_json('Escaped "{\\"p\\":1}" </think>'+json.dumps(obj)) == obj


def test_real_glm_unique_final_without_delimiter():
    fixture=json.loads((Path(__file__).parent/'fixtures/glm53-unique-final-response.json').read_text())
    obj=_parse_decision_json(fixture['response']['message']['content'])
    assert obj['action_type']=='run_scientific_tool'
    assert obj['action_details']['tool_name']=='ar1_benchmark'


def test_quoted_json_string_is_not_a_decision_candidate():
    encoded_example=json.dumps(json.dumps(decision(content='quoted data only')))
    obj=decision(content='actual final')
    assert _parse_decision_json('Quoted example '+encoded_example+' Final '+json.dumps(obj))==obj


@pytest.mark.parametrize('text', ['x'*(256*1024+1), 'prose '+'{'*300,
                                 'prose '+'['*1500+'0'+']'*1500])
def test_adversarial_nesting_and_input_size_are_bounded(text):
    with pytest.raises(DecisionSchemaError):
        _parse_decision_json(text)
