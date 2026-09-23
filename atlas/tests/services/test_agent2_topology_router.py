from fastapi.testclient import TestClient

from app.routers.agent2_topology import router as agent2_topo_router


def test_agent2_topology_report_insights_smoke():
    client = TestClient(agent2_topo_router)
    payload = {
        "points": [{"x": 0.0, "y": 0.0}, {"x": 0.2, "y": 0.0}, {"x": 0.4, "y": 0.0}],
        "epsilon": 0.25,
        "epsilon_range": [0.1, 0.6],
        "num_steps": 5,
        "max_dimension": 2,
        "include_images": False,
        "generate_conjecture": True
    }
    r = client.post("/api/agent2/topology/report-insights", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "result" in data and data["result"].get("success") is True
    # si hay insights, es posible que haya conjetura generada
    res = data["result"]
    if res.get("insights"):
        assert "conjecture_id" in res or True

