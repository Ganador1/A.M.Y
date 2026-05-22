import pytest

from app.services.model_management_service import ModelManagementService


@pytest.fixture(autouse=True)
def clean_registry(tmp_path, monkeypatch):
    # Redirigir el registro a un tmp durante tests
    reg = tmp_path / "models_registry.json"
    monkeypatch.setattr("app.services.model_management_service.REGISTRY_PATH", reg, raising=False)
    svc = ModelManagementService()
    yield svc


def test_register_and_get(clean_registry):
    svc = clean_registry
    r1 = svc.register_model({"name": "test-model", "version": "1.0", "task": "nlp", "uri": "file:///tmp/model"})
    assert r1["success"] is True
    ls = svc.list_models()
    assert ls["count"] == 1
    got = svc.get_model({"name": "test-model"})
    assert got["success"] is True


def test_update(clean_registry):
    svc = clean_registry
    svc.register_model({"name": "m", "version": "v1", "task": "cv"})
    up = svc.update_model({"name": "m", "version": "v1", "updates": {"metadata": {"acc": 0.9}}})
    assert up["success"] is True
    got = svc.get_model({"name": "m", "version": "v1"})
    assert got["success"] is True
    assert got["models"][0].get("metadata", {}).get("acc") == 0.9
