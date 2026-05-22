from fastapi.testclient import TestClient

from app.routers.topology import router
from app.routers.topology_reports import router as topo_report_router


def test_topology_invariants_endpoint():
    client = TestClient(router)
    payload = {"points": [[0.0, 0.0], [0.1, 0.0], [1.0, 1.0]], "epsilon": 0.2}
    r = client.post("/api/topology/invariants", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "invariants" in data and "avg_degree" in data["invariants"]


def test_topology_persistence_diagram_image():
    client = TestClient(router)
    payload = {
        "points": [{"x": 0.0, "y": 0.0}, {"x": 0.2, "y": 0.0}, {"x": 0.4, "y": 0.0}],
        "epsilon_range": [0.1, 0.6],
        "num_steps": 5,
        "max_dimension": 2
    }
    r = client.post("/api/topology/persistence-diagram", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("image_base64"), str) and len(data["image_base64"]) > 10


def test_topology_betti_curve_image():
    client = TestClient(router)
    payload = {
        "points": [{"x": 0.0, "y": 0.0}, {"x": 0.2, "y": 0.0}, {"x": 0.4, "y": 0.0}],
        "epsilon_range": [0.1, 0.6],
        "num_steps": 5,
        "max_dimension": 2
    }
    r = client.post("/api/topology/betti-curve", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("image_base64"), str) and len(data["image_base64"]) > 10


def test_topology_degree_histogram_image():
    client = TestClient(router)
    payload = {
        "points": [{"x": 0.0, "y": 0.0}, {"x": 0.2, "y": 0.0}, {"x": 0.4, "y": 0.0}],
        "epsilon": 0.25
    }
    r = client.post("/api/topology/degree-histogram", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data.get("image_base64"), str) and len(data["image_base64"]) > 10


def test_topology_report_endpoint():
    client = TestClient(topo_report_router)
    payload = {
        "points": [{"x": 0.0, "y": 0.0}, {"x": 0.2, "y": 0.0}, {"x": 0.4, "y": 0.0}],
        "epsilon": 0.25,
        "epsilon_range": [0.1, 0.6],
        "num_steps": 5,
        "max_dimension": 2,
        "include_images": True
    }
    r = client.post("/api/topology/report", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "invariants" in data and "persistence" in data
    if data.get("images"):
        assert "persistence_diagram_base64" in data["images"]


