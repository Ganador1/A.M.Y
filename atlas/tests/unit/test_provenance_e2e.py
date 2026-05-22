import pytest
from fastapi.testclient import TestClient

from main import app
from app.routers.experiment_tracking import experiment_service
from app.routers.data_versioning import data_versioning_service


@pytest.fixture(autouse=True)
def disable_auth(monkeypatch):
    monkeypatch.setenv("ENABLE_AUTH_ROUTES", "false")
    yield


@pytest.mark.asyncio
async def test_provenance_graph_single_experiment_e2e(tmp_path, monkeypatch):
    client = TestClient(app)

    # 1) Crear experimento real
    start = await experiment_service.process_request({
        "action": "start_experiment",
        "name": "e2e-prov-exp",
        "parameters": {"alpha": 0.5, "workflow_steps": ["load", {"name": "train", "after": "wf:load"}, "evaluate"]},
        "tags": {"stage": "test"}
    })
    assert start["success"]
    exp_id = start["experiment_id"]

    # 2) Crear un artefacto y versionarlo
    artifact_dir = tmp_path / "artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact = artifact_dir / "result.txt"
    artifact.write_text("artifact-data")

    # Permitir versionar el archivo del tmp fuera del root por test (modo no estricto)
    monkeypatch.setenv("STRICT_DATA_PATHS", "0")
    vres = await data_versioning_service.process_request({
        "action": "version_data",
        "data_path": str(artifact),
        "metadata": {"exp": exp_id}
    })
    assert vres["success"]

    # 3) Asociar el artefacto al experimento
    lres = await experiment_service.process_request({
        "action": "log_artifact",
        "experiment_id": exp_id,
        "artifact_path": str(artifact)
    })
    assert lres["success"]

    # 4) Llamar endpoint por experiment_id
    resp = client.get(f"/api/provenance/experiment/{exp_id}", params={"render_html": False})
    assert resp.status_code == 200
    payload = resp.json()
    assert payload.get("success") is True
    graph = payload.get("graph", {})
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    # Debe incluir el nodo del experimento y el artefacto
    assert any(n.get("type") == "experiment" for n in nodes)
    assert any(n.get("type") == "artifact" for n in nodes)
    # Debe existir al menos una arista produces
    assert any(e.get("label") == "produces" for e in edges)
