from fastapi.testclient import TestClient

from app.routers.elliptic import router as elliptic_router
from app.routers.polynomial import router as polynomial_router


def test_elliptic_invariants_persist():
    client = TestClient(elliptic_router)
    r = client.post("/api/elliptic/invariants-persist", json={"name": "E1", "A": -1, "B": 0})
    assert r.status_code == 200
    data = r.json()
    assert "object_id" in data and "invariants" in data


def test_polynomial_invariants_batch():
    client = TestClient(polynomial_router)
    r = client.post("/api/polynomial/invariants-batch", json={"items": [[1, 0, -1], [1, 0, 1]]})
    assert r.status_code == 200
    data = r.json()
    assert data.get("count") == 2
    assert isinstance(data.get("items"), list)


