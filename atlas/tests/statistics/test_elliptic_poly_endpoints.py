from fastapi.testclient import TestClient

from app.routers.elliptic import router as elliptic_router
from app.routers.polynomial import router as polynomial_router


def test_elliptic_invariants_endpoint():
    client = TestClient(elliptic_router)
    r = client.post("/api/elliptic/invariants", json={"A": -1, "B": 0})
    assert r.status_code == 200
    data = r.json()
    assert "invariants" in data and "j_invariant" in data["invariants"]


def test_polynomial_invariants_endpoint():
    client = TestClient(polynomial_router)
    # x^2 - 1
    r = client.post("/api/polynomial/invariants", json={"coeffs": [1, 0, -1]})
    assert r.status_code == 200
    data = r.json()
    assert "invariants" in data and "degree" in data["invariants"]


