from app.services.multi_agent_coordinator import MultiAgentCoordinator


def test_multi_agent_pipeline_smoke(monkeypatch):
    """Smoke test: ejecuta pipeline con objetivo simple y verifica artefacto."""
    # Monkeypatch wrappers to return respuestas deterministas sin invocar modelos reales
    class DummyWrapper:
        def __init__(self, model):
            self.model = model
        def generate(self, prompt, max_new_tokens=128, temperature=0.7):
            if 'JSON' in prompt and 'Hipótesis' not in prompt and 'Revisión' not in prompt:
                return '{"steps":["h1","d1","v1","r1","p1"]}'
            if 'Formato JSON' in prompt:
                return '{"title":"Test H","description":"Desc","variables":["x","y"],"expected_outcome":"Aumenta x","assumptions":["linear"]}'
            if 'Plan:' in prompt:
                return '```python\n# plan experimental\nprint("simulate")\n```'
            if 'Respuesta JSON' in prompt:
                return '{"verdict":"approve","weaknesses":[],"improvements":[],"risk_level":"low"}'
            if 'INFORME:' in prompt:
                return 'INFORME: Resumen...'
            return 'OK'

    mac = MultiAgentCoordinator()
    # Reemplazar wrappers
    for r in mac.wrappers:
        mac.wrappers[r] = DummyWrapper(mac.role_models[r])  # type: ignore

    result = mac.run_pipeline('Objetivo de prueba mínimo')
    assert result['success'] is True
    artifact = result['artifact']
    assert 'hypothesis' in artifact
    assert 'publication' in artifact
    assert artifact['steps'] == len(mac.history)
