from fastapi.testclient import TestClient
from main import app

def test_validation_matrix_endpoint():
    client = TestClient(app)
    r = client.get("/api/validation/matrix")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    matrix = body["matrix"]
    assert "score" in matrix
    assert 0 <= matrix["score"] <= 100
    assert "artifact_count" in matrix
    assert "service_count" in matrix
    assert isinstance(matrix.get("flags"), list)
