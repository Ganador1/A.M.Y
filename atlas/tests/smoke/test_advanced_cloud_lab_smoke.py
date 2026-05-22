"""
Smoke tests for Advanced Cloud Lab endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.advanced_cloud_lab import router


client = TestClient(router)


def test_advanced_cloud_lab_health():
    """Test advanced cloud lab health endpoint"""
    response = client.get("/api/advanced-cloud-lab/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "AdvancedCloudLab"
    assert data["status"] == "operational"
    assert data["simulation_mode"] == True
    assert "protocols_available" in data


def test_get_available_protocols():
    """Test get available protocols endpoint"""
    response = client.get("/api/advanced-cloud-lab/protocols")
    assert response.status_code == 200
    data = response.json()
    
    assert "available_protocols" in data
    assert "total_protocols" in data
    assert "protocols" in data
    assert len(data["available_protocols"]) == data["total_protocols"]
    assert "mass_spec_analysis" in data["available_protocols"]
    assert "protein_expression" in data["available_protocols"]


def test_submit_experiment():
    """Test experiment submission"""
    payload = {
        "protocol_name": "mass_spec_analysis",
        "samples": [
            {
                "id": "MS_sample_1",
                "volume_ul": 50,
                "sample_type": "protein",
                "storage_conditions": "4C"
            }
        ],
        "parameters": {
            "ionization_mode": "ESI",
            "mass_range": [100, 2000],
            "resolution": "high"
        }
    }
    
    response = client.post("/api/advanced-cloud-lab/experiments/submit", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "experiment_id" in data
    assert data["protocol_name"] == "mass_spec_analysis"
    assert data["samples_submitted"] == 1
    assert data["status"] in ["running", "submitted"]
    assert "estimated_completion" in data
    assert "estimated_cost_usd" in data


def test_cost_estimate():
    """Test cost estimation endpoint"""
    response = client.get("/api/advanced-cloud-lab/cost-estimate?protocol_name=protein_expression&samples_count=2")
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "protein_expression"
    assert data["samples_count"] == 2
    assert "base_cost_usd" in data
    assert "total_cost_usd" in data
    assert "cost_per_sample_usd" in data
    assert "estimated_duration_hours" in data


def test_experiment_history():
    """Test experiment history endpoint"""
    response = client.get("/api/advanced-cloud-lab/experiments/history?limit=10")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_experiments" in data
    assert "recent_experiments" in data
    assert "running_experiments" in data
    assert "completed_experiments" in data


def test_mass_spec_shortcut():
    """Test mass spectrometry shortcut"""
    payload = [
        {
            "id": "protein_1",
            "volume_ul": 25,
            "sample_type": "protein"
        }
    ]
    
    response = client.post("/api/advanced-cloud-lab/experiments/mass-spec", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "mass_spec_analysis"
    assert data["samples_submitted"] == 1


def test_protein_expression_shortcut():
    """Test protein expression shortcut"""
    payload = [
        {
            "id": "plasmid_1",
            "sample_type": "plasmid"
        }
    ]
    
    response = client.post("/api/advanced-cloud-lab/experiments/protein-expression", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "protein_expression"
    assert data["samples_submitted"] == 1


def test_ngs_sequencing_shortcut():
    """Test NGS sequencing shortcut"""
    payload = [
        {
            "id": "dna_library_1",
            "volume_ul": 15,
            "sample_type": "dna_library"
        }
    ]
    
    response = client.post("/api/advanced-cloud-lab/experiments/ngs-sequencing", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "ngs_sequencing"
    assert data["samples_submitted"] == 1


def test_flow_cytometry_shortcut():
    """Test flow cytometry shortcut"""
    payload = [
        {
            "id": "cells_1",
            "volume_ul": 100,
            "sample_type": "cells"
        }
    ]
    
    response = client.post("/api/advanced-cloud-lab/experiments/flow-cytometry", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "flow_cytometry"
    assert data["samples_submitted"] == 1


def test_drug_screening_shortcut():
    """Test drug screening shortcut"""
    payload = [
        {
            "id": "cell_line_1",
            "sample_type": "cell_line"
        }
    ]
    
    response = client.post("/api/advanced-cloud-lab/experiments/drug-screening", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "drug_screening"
    assert data["samples_submitted"] == 1


def test_monitor_experiment():
    """Test experiment monitoring"""
    # First submit an experiment to get an ID
    payload = {
        "protocol_name": "mass_spec_analysis",
        "samples": [
            {
                "id": "monitor_test",
                "volume_ul": 30,
                "sample_type": "protein"
            }
        ]
    }
    
    submit_response = client.post("/api/advanced-cloud-lab/experiments/submit", json=payload)
    assert submit_response.status_code == 200
    experiment_id = submit_response.json()["experiment_id"]
    
    # Now monitor the experiment
    response = client.get(f"/api/advanced-cloud-lab/experiments/{experiment_id}/status")
    assert response.status_code == 200
    data = response.json()
    
    assert data["experiment_id"] == experiment_id
    assert "status" in data
    assert "progress_percent" in data
    assert "elapsed_hours" in data


def test_get_experiment_results():
    """Test getting experiment results"""
    # First submit an experiment
    payload = {
        "protocol_name": "flow_cytometry",
        "samples": [
            {
                "id": "results_test",
                "volume_ul": 50,
                "sample_type": "cells"
            }
        ]
    }
    
    submit_response = client.post("/api/advanced-cloud-lab/experiments/submit", json=payload)
    assert submit_response.status_code == 200
    experiment_id = submit_response.json()["experiment_id"]
    
    # Try to get results (might not be completed yet in simulation)
    response = client.get(f"/api/advanced-cloud-lab/experiments/{experiment_id}/results")
    assert response.status_code == 200
    data = response.json()
    
    # Either results or error about experiment still running
    assert "experiment_id" in data or "error" in data


def test_invalid_protocol_submission():
    """Test submission with invalid protocol"""
    payload = {
        "protocol_name": "nonexistent_protocol",
        "samples": [
            {
                "id": "invalid_test",
                "sample_type": "unknown"
            }
        ]
    }
    
    response = client.post("/api/advanced-cloud-lab/experiments/submit", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "no disponible" in data["error"]


def test_cost_estimate_invalid_protocol():
    """Test cost estimate with invalid protocol"""
    response = client.get("/api/advanced-cloud-lab/cost-estimate?protocol_name=invalid_protocol&samples_count=1")
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "no encontrado" in data["error"]
