from fastapi.testclient import TestClient

from app.routers.elliptic import router


def test_elliptic_advanced_invariants_endpoint():
    client = TestClient(router)
    r = client.post("/api/elliptic/advanced-invariants", json={"A": 1, "B": 1})
    assert r.status_code == 200
    data = r.json()
    assert "curve" in data and "sage" in data
    # Puede devolver error si Sage no está disponible; verificar estructura
    assert isinstance(data["sage"], dict)


