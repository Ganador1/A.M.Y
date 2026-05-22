from fastapi.testclient import TestClient
from fastapi import FastAPI
from app.routers.neuroscience_light import router as neuro_router

app = FastAPI()
app.include_router(neuro_router)
client = TestClient(app)


def test_neuro_connectivity_smoke():
    payload = {
        "sampling_rate_hz": 1000,
        "data": [
            [0, 1, 0, -1, 0, 1, 0, -1],
            [0.1, 0.2, 0.1, 0.0, -0.1, -0.2, -0.1, 0.0]
        ]
    }
    r = client.post("/api/neuro-light/connectivity", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data.get("n_channels") == 2
    assert "bands" in data and "matrices" in data

