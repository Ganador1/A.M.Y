import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture(autouse=True)
def disable_auth(monkeypatch):
    # Desactivar el guard de Bearer para tests
    monkeypatch.setenv("ENABLE_AUTH_ROUTES", "false")
    yield


def test_get_all_experiments_graph_endpoint():
    client = TestClient(app)
    resp = client.get("/api/provenance/experiments", params={"render_html": False})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("success") is True
    assert "graph" in data
