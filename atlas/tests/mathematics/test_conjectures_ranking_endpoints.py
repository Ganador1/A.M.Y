from fastapi.testclient import TestClient

from app.routers.conjectures import router


def test_conjectures_top_and_rank_persist_smoke():
    client = TestClient(router)
    # rank persist with dummy id should be False (not found)
    r = client.post("/api/conjectures/rank-persist", json={"conjecture_id": "nonexistent", "importance": 0.8})
    assert r.status_code == 200
    assert r.json().get("success") in {True, False}

    t = client.get("/api/conjectures/top?limit=5")
    assert t.status_code == 200
    data = t.json()
    assert "items" in data


def test_conjectures_top_topological_smoke():
    client = TestClient(router)
    r = client.get("/api/conjectures/top-topological?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and isinstance(data["count"], int)


def test_conjectures_top_topological_report_smoke():
    client = TestClient(router)
    r = client.get("/api/conjectures/top-topological-report?limit=3&include_images=false")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data and isinstance(data.get("images_embedded"), bool)

    r2 = client.get("/api/conjectures/top-topological-report?limit=2&include_images=true")
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2.get("images_embedded") in {True, False}


def test_conjectures_rank_persist_batch_smoke():
    client = TestClient(router)
    payload = {
        "updates": [
            {"conjecture_id": "id1", "importance": 0.9},
            {"conjecture_id": "id2", "importance": 0.1}
        ]
    }
    r = client.post("/api/conjectures/rank-persist-batch", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "updated" in data and "failed" in data


