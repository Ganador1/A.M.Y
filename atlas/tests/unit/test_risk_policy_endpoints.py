from fastapi.testclient import TestClient
from main import app

def test_get_and_update_risk_policy():
    client = TestClient(app)
    r = client.get("/api/integrity/risk/policy")
    assert r.status_code == 200
    body = r.json()
    assert body["success"]
    assert "policy" in body
    # original policy fetched; ensuring update changes values below

    update_payload = {"signature_levels": ["CRITICAL"], "thresholds": {"low": 3}}
    r2 = client.put("/api/integrity/risk/policy", json=update_payload)
    assert r2.status_code == 200
    body2 = r2.json()
    assert body2["success"]
    assert body2["policy"]["signature_levels"] == ["CRITICAL"]
    assert body2["policy"]["thresholds"]["low"] == 3
