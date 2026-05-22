from app.services.multi_agent_coordinator import MultiAgentCoordinator


def test_yaml_roles_loaded_and_reload(tmp_path, monkeypatch):
    # Copiar config original a tmp para no afectar repo
    cfg_dir = tmp_path / 'config'
    cfg_dir.mkdir()
    agents_yaml = cfg_dir / 'agents.yaml'
    agents_yaml.write_text('''roles:\n  orchestrator:\n    model: llama3:8b\n    params:\n      temperature: 0.11\n  reviewer:\n    model: qwen:7b\n    params:\n      temperature: 0.22\n''', encoding='utf-8')
    monkeypatch.setenv('AXIOM_CONFIG_DIR', str(cfg_dir))

    c = MultiAgentCoordinator()
    assert c.role_models['orchestrator'] == 'llama3:8b'
    # Verificar parámetros cargados
    assert 'orchestrator' in c.role_params
    assert c.role_params['orchestrator']['temperature'] == 0.11

    # Modificar YAML y recargar
    agents_yaml.write_text('''roles:\n  orchestrator:\n    model: llama3:8b\n    params:\n      temperature: 0.33\n  reviewer:\n    model: qwen:7b\n    params:\n      temperature: 0.44\n  bio_hypothesis:\n    model: mistral:7b\n''', encoding='utf-8')

    diff = c.reload_configuration()
    assert diff['success']
    # Nuevo rol incorporado
    assert 'bio_hypothesis' in c.role_models
    # Parámetro actualizado
    assert c.role_params['orchestrator']['temperature'] == 0.33

    # Ejecutar rol para asegurar uso de params (mock generate? aquí solo ver que no falla)
    resp = c.plan('Test objetivo científico')
    # La respuesta puede ser placeholder de error si LLM no configurado; lo importante es no excepción
    assert isinstance(resp, str)

