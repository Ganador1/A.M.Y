from fastapi.testclient import TestClient

from app.routers.topology import router as topo_router
from app.routers.sequence_analyze import router as seq_router


def test_topology_vietoris_rips_endpoint():
    client = TestClient(topo_router)
    payload = {"points": [[0.0, 0.0], [0.1, 0.0], [1.0, 1.0]], "epsilon": 0.2}
    r = client.post("/api/topology/vietoris-rips", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "invariants" in data and "components_est" in data["invariants"]


def test_topology_graph_stats_endpoint():
    client = TestClient(topo_router)
    points = [{"x": 0.0, "y": 0.0}, {"x": 0.1, "y": 0.0}, {"x": 0.3, "y": 0.0}, {"x": 5.0, "y": 5.0}]
    payload = {"points": points, "epsilon": 0.2}
    r = client.post("/api/topology/graph-stats", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["epsilon"] == 0.2
    assert data["n_points"] == 4
    assert "n_edges" in data and "components" in data and isinstance(data.get("degree_hist"), dict)


def test_sequences_analyze_endpoint_smoke():
    client = TestClient(seq_router)
    payload = {"terms": [1, 1, 2, 3, 5, 8], "deep_analysis": False}
    r = client.post("/api/sequences/analyze", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, dict)


def test_sequences_analyze_batch_endpoint_smoke():
    client = TestClient(seq_router)
    batch = {
        "sequences": [
            [1, 1, 2, 3, 5, 8],
            [2, 4, 8, 16]
        ],
        "deep_analysis": False
    }
    r = client.post("/api/sequences/analyze-batch", json=batch)
    assert r.status_code == 200
    data = r.json()
    assert "batch_results" in data and isinstance(data["count"], int)

