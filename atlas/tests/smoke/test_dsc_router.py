from fastapi import FastAPI
from fastapi.testclient import TestClient

# Aislar el router DSC para evitar dependencias de main.py en tests
from app.routers.differential_scanning_calorimetry import router as dsc_router

test_app = FastAPI()
test_app.include_router(dsc_router, prefix="/api")
client = TestClient(test_app)


def test_dsc_thermogram_ok():
    payload = {
        "sample_id": "polymer_sample_001",
        "sample_mass": 5.2,
        "heating_rate": 10.0,
        "temperature_range": [25.0, 500.0],
        "atmosphere": "nitrogen",
        "simulate": True,
    }
    resp = client.post("/api/dsc/thermogram", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"
    assert "thermogram" in data
    assert "temperature_data" in data["thermogram"]
    assert "heat_flow_data" in data["thermogram"]
    assert data["data_points"] > 0


def test_dsc_analyze_ok():
    payload = {
        "sample_id": "polymer_sample_002",
        "sample_mass": 4.0,
        "heating_rate": 15.0,
        "temperature_range": [30.0, 450.0],
        "atmosphere": "nitrogen",
    }
    resp = client.post("/api/dsc/analyze", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"
    assert "analysis_id" in data
    assert "summary" in data
    assert "transitions" in data


def test_dsc_kinetics_ok():
    payload = {
        "heating_rates": [5.0, 10.0, 20.0, 30.0],
        "peak_temps": [320.5, 328.2, 336.1, 342.7],
        "reaction_type": "decomposition",
    }
    resp = client.post("/api/dsc/kinetics", json=payload)
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "success"
    assert "kinetics" in data
    assert "activation_energy" in data["kinetics"]
    assert "correlation_coefficient" in data["kinetics"]