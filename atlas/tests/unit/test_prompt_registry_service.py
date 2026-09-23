from app.services.prompting.prompt_registry_service import prompt_registry_service, REGISTRY_PATH, RENDERS_LOG


def setup_function(_):
    # Reset files
    if REGISTRY_PATH.exists():
        REGISTRY_PATH.unlink()
    if RENDERS_LOG.exists():
        RENDERS_LOG.unlink()
    prompt_registry_service.__init__()  # reinit


def test_register_and_list():
    r = prompt_registry_service.register(name="hypothesis_gen", version="v1", template="Idea: {{ topic }}", variables=["topic"], metadata={"role": "generator"})
    assert r["success"]
    lst = prompt_registry_service.list()
    assert lst["count"] == 1


def test_register_duplicate():
    prompt_registry_service.register(name="hypothesis_gen", version="v1", template="Idea: {{ topic }}")
    r2 = prompt_registry_service.register(name="hypothesis_gen", version="v1", template="Idea: {{ topic }}")
    assert not r2["success"]


def test_render_success():
    prompt_registry_service.register(name="lit_review", version="v1", template="Search: {{ query }}", variables=["query"], metadata={})
    out = prompt_registry_service.render(name="lit_review", version="v1", context={"query": "genomics"})
    assert out["success"]
    assert "genomics" in out["rendered"]
    assert RENDERS_LOG.exists()


def test_render_missing_var():
    prompt_registry_service.register(name="lit_review", version="v1", template="Search: {{ query }}", variables=["query"], metadata={})
    out = prompt_registry_service.render(name="lit_review", version="v1", context={})
    assert not out["success"]
    assert "Faltan variables" in out["error"]


def test_get_versions():
    prompt_registry_service.register(name="peer_review", version="v1", template="Review: {{ text }}", variables=["text"], metadata={})
    prompt_registry_service.register(name="peer_review", version="v2", template="Critique: {{ text }}", variables=["text"], metadata={})
    res = prompt_registry_service.get(name="peer_review")
    assert res["success"] and len(res["prompts"]) == 2
