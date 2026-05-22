"""
Smoke tests for Neuro Simulation router
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.neuro_simulation import router


client = TestClient(router)


def test_neuro_sim_health():
    """Test neuro simulation health endpoint"""
    response = client.get("/api/neuro-sim/health")
    assert response.status_code == 200
    data = response.json()
    assert "brian2_available" in data
    assert "neuron_available" in data


def test_brian2_simulation():
    """Test Brian2 simulation endpoint"""
    payload = {
        "num_neurons": 50,
        "sim_time_ms": 200,
        "connectivity": 0.1
    }
    response = client.post("/api/neuro-sim/brian2", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should return either success or error about missing dependencies
    assert "error" in data or "simulation_results" in data


def test_neuron_model():
    """Test NEURON model endpoint"""
    payload = {
        "soma_length": 30.0,
        "soma_diameter": 30.0,
        "current_amplitude": 0.1
    }
    response = client.post("/api/neuro-sim/neuron", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Should return either success or error about missing dependencies
    assert "error" in data or "model_results" in data
