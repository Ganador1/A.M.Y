"""
Smoke tests for Advanced Lab Automation endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.advanced_lab_automation import router


client = TestClient(router)


def test_advanced_lab_health():
    """Test advanced lab automation health endpoint"""
    response = client.get("/api/advanced-lab/health")
    assert response.status_code == 200
    data = response.json()
    
    assert data["service"] == "AdvancedLabAutomation"
    assert data["status"] == "operational"
    assert data["simulation_mode"] == True
    assert "instruments_available" in data


def test_initialize_instruments():
    """Test instruments initialization"""
    response = client.post("/api/advanced-lab/initialize")
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] == True
    assert "instruments_initialized" in data
    assert "details" in data
    assert data["laboratory_ready"] == True


def test_get_instruments_status():
    """Test instruments status endpoint"""
    response = client.get("/api/advanced-lab/instruments/status")
    assert response.status_code == 200
    data = response.json()
    
    assert "instruments" in data
    assert "total_instruments" in data
    assert "ready_instruments" in data
    assert "simulation_mode" in data


def test_get_protocol_templates():
    """Test protocol templates endpoint"""
    response = client.get("/api/advanced-lab/protocols/templates")
    assert response.status_code == 200
    data = response.json()
    
    assert "available_protocols" in data
    assert "total_protocols" in data
    assert "protocols" in data
    assert len(data["available_protocols"]) == data["total_protocols"]
    assert "pcr_standard" in data["available_protocols"]
    assert "elisa_96well" in data["available_protocols"]


def test_run_automated_protocol():
    """Test automated protocol execution"""
    payload = {
        "protocol_name": "pcr_standard",
        "samples": [
            {
                "id": "sample_1",
                "volume_ul": 20,
                "sample_type": "DNA"
            },
            {
                "id": "sample_2", 
                "volume_ul": 25,
                "sample_type": "DNA"
            }
        ],
        "parameters": {
            "cycles": 30,
            "annealing_temp": 58
        }
    }
    
    response = client.post("/api/advanced-lab/protocols/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "protocol_id" in data
    assert data["protocol_name"] == "pcr_standard"
    assert data["samples_processed"] == 2
    assert data["status"] in ["completed", "running"]
    assert "steps_completed" in data
    assert "instruments_used" in data


def test_run_pcr_protocol_shortcut():
    """Test PCR protocol shortcut"""
    payload = [
        {
            "id": "pcr_sample_1",
            "volume_ul": 15,
            "sample_type": "cDNA"
        }
    ]
    
    response = client.post("/api/advanced-lab/protocols/pcr", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "pcr_standard"
    assert data["samples_processed"] == 1


def test_run_elisa_protocol_shortcut():
    """Test ELISA protocol shortcut"""
    payload = [
        {
            "id": "elisa_sample_1",
            "volume_ul": 100,
            "sample_type": "serum"
        },
        {
            "id": "elisa_sample_2",
            "volume_ul": 100,
            "sample_type": "plasma"
        }
    ]
    
    response = client.post("/api/advanced-lab/protocols/elisa", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "elisa_96well"
    assert data["samples_processed"] == 2


def test_run_dna_extraction():
    """Test DNA extraction protocol"""
    payload = [
        {
            "id": "cell_sample_1",
            "volume_ul": 200,
            "sample_type": "cells"
        }
    ]
    
    response = client.post("/api/advanced-lab/protocols/dna-extraction", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "dna_extraction"
    assert data["samples_processed"] == 1


def test_run_cell_culture():
    """Test cell culture protocol"""
    payload = [
        {
            "id": "culture_1",
            "volume_ul": 200,
            "sample_type": "cells"
        }
    ]
    
    response = client.post("/api/advanced-lab/protocols/cell-culture", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["protocol_name"] == "cell_culture"
    assert data["samples_processed"] == 1


def test_get_protocol_history():
    """Test protocol history endpoint"""
    response = client.get("/api/advanced-lab/protocols/history?limit=5")
    assert response.status_code == 200
    data = response.json()
    
    assert "total_protocols_run" in data
    assert "recent_protocols" in data
    assert "successful_protocols" in data
    assert "failed_protocols" in data


def test_invalid_protocol_name():
    """Test with invalid protocol name"""
    payload = {
        "protocol_name": "nonexistent_protocol",
        "samples": [
            {
                "id": "sample_1",
                "volume_ul": 20,
                "sample_type": "unknown"
            }
        ]
    }
    
    response = client.post("/api/advanced-lab/protocols/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "no encontrado" in data["error"]


def test_empty_samples_list():
    """Test with empty samples list"""
    payload = {
        "protocol_name": "pcr_standard",
        "samples": []
    }
    
    response = client.post("/api/advanced-lab/protocols/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["samples_processed"] == 0
