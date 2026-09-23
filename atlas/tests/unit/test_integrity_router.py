import os
import pytest
from fastapi.testclient import TestClient

# Config env (si la app necesita DB para otros routers no usados aquí)
os.environ.setdefault('ENABLE_DATABASE', 'false')

from main import app  # noqa

client = TestClient(app)


def test_register_and_verify_artifact():
    payload = {
        "artifact_type": "model",
        "data": {"weights": [1,2,3]},
        "metadata": {"model_type": "toy"},
        "blockchain": False
    }
    r = client.post("/api/integrity/artifacts/register", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["success"]
    artifact_id = data["artifact_id"]

    # list
    r_list = client.get("/api/integrity/artifacts")
    assert r_list.status_code == 200
    assert any(it["artifact_id"] == artifact_id for it in r_list.json()["items"]) or any(it.get("artifact_id") == artifact_id for it in r_list.json()["items"])  # fallback por formato

    # verify
    r_ver = client.get(f"/api/integrity/artifacts/{artifact_id}/verify")
    assert r_ver.status_code == 200
    ver = r_ver.json()
    assert ver["success"]
    assert ver["status"]["integrity_ok"] is True


def test_lineage_link():
    # registrar padre
    p1 = client.post("/api/integrity/artifacts/register", json={"artifact_type":"dataset","data":[1,2,3],"blockchain":False})
    c1 = client.post("/api/integrity/artifacts/register", json={"artifact_type":"result","data":{"v":42},"blockchain":False})
    pid = p1.json()["artifact_id"]
    cid = c1.json()["artifact_id"]

    link = client.post("/api/integrity/artifacts/link", json={"parent_id": pid, "child_id": cid})
    assert link.status_code == 200
    assert link.json()["success"]
    lineage = client.get(f"/api/integrity/artifacts/{pid}/lineage")
    assert lineage.status_code == 200
    children = lineage.json()["lineage"]["children"]
    assert cid in children


def test_services_listing():
    r = client.get("/api/integrity/services")
    assert r.status_code == 200
    body = r.json()
    assert body["success"]
    assert isinstance(body["services"], list)
    assert len(body["services"]) > 0


def test_risk_assess_endpoint():
    payload = {
        "domain": "plasma_physics",
        "description": "Estudio pathogen virus avanzado",
        "declared_intent": "research"
    }
    r = client.post("/api/integrity/risk/assess", json=payload)
    if r.status_code == 503:  # módulo opcional
        pytest.skip("Risk assessment module not available")
    assert r.status_code == 200
    body = r.json()
    assert body["success"]
    assert body["risk_level"] in ("LOW","MEDIUM","HIGH","CRITICAL")
