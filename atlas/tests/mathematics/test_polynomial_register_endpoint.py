from fastapi.testclient import TestClient

from app.routers.polynomial import router


def test_polynomial_register():
    client = TestClient(router)
    r = client.post("/api/polynomial/register", json={"name": "p1", "coeffs": [1, 0, -1]})
    assert r.status_code == 200
    data = r.json()
    assert "object_id" in data


