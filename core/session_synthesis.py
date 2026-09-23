"""An optional application validator can reject a session conclusion before closure.

The callback receives detached JSON snapshots, performs bounded synchronous checks,
and returns a scoped result. Neither this hook nor passing it completes a scientific
goal or verifies arbitrary prose. The application must pin its validator sources.
"""
import json
from core.execution_evidence import evidence_span


def check_session_synthesis(validator, thought, history):
    with evidence_span('heartbeat.synthesis_validation', {'thought': thought, 'tool_history': history}) as span:
        try:
            if not callable(validator):
                raise ValueError('required session synthesis validator is unavailable')
            detached = json.loads(json.dumps({'thought': thought, 'history': history}, allow_nan=False))
            result = validator(detached['thought'], detached['history'])
            if (not isinstance(result, dict) or type(result.get('passed')) is not bool
                    or not isinstance(result.get('scope'), str) or not result['scope'].strip()
                    or not isinstance(result.get('errors'), list)
                    or any(not isinstance(e, str) or not e.strip() for e in result['errors'])
                    or (result['passed'] and result['errors'])):
                raise ValueError('validator must return passed(boolean), scope(string), errors(list); passing requires no errors')
            raw = json.dumps(result, allow_nan=False)
            if len(raw.encode()) > 65536:
                raise ValueError('session synthesis validation exceeds 65536 bytes')
            result = json.loads(raw)
        except Exception as exc:
            result = {'passed': False, 'errors': [type(exc).__name__ + ': ' + str(exc)],
                      'scope': 'Required session conclusion validation did not pass'}
        result.update(scientific_goal_verified_complete=False, all_prose_verified=False)
        return span.result(result)
