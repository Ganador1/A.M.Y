"""
Smoke tests for Cloud Lab router
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.cloud_lab import router


client = TestClient(router)


def test_cloud_lab_health():
    """Test cloud lab health endpoint"""
    response = client.get("/api/cloud-lab/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "ECL"
    assert data["mode"] == "stub"
    assert data["configured"] == False


def test_submit_experiment_stub():
    """Test experiment submission stub"""
    payload = {
        "name": "test_experiment",
        "instructions": [{"op": "noop"}]
    }
    response = client.post("/api/cloud-lab/submit", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "submitted" in data


def test_mass_spec_mock():
    """Test mass spectrometry mock endpoint"""
    response = client.post("/api/cloud-lab/mass-spec/mock?sample_id=S1")
    assert response.status_code == 200
    data = response.json()
    assert data["experiment_id"] == "mock-ms-0001"
    assert data["status"] == "completed"
    assert "peaks" in data
    assert "total_ion_current" in data


def test_protein_expression_mock():
    """Test protein expression mock endpoint"""
    response = client.post("/api/cloud-lab/protein-expression/mock?plasmid_id=P123")
    assert response.status_code == 200
    data = response.json()
    assert data["experiment_id"] == "mock-expr-0001"
    assert "protein_yield_mg" in data
    assert "purity_percent" in data
    assert "expression_level" in data
