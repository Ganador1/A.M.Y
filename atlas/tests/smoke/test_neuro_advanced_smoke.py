"""
Smoke tests for Advanced Neuroscience endpoints
"""
import pytest
import numpy as np
from fastapi.testclient import TestClient
from app.routers.neuroscience_light import router


client = TestClient(router)


def test_whole_brain_simulation():
    """Test whole brain simulation endpoint"""
    # Matriz de conectividad pequeña para prueba
    connectivity_matrix = [
        [0.0, 0.5, 0.3],
        [0.5, 0.0, 0.4],
        [0.3, 0.4, 0.0]
    ]
    
    payload = {
        "connectivity_matrix": connectivity_matrix,
        "simulation_time_ms": 2000
    }
    
    response = client.post("/api/neuro-light/whole-brain-simulation", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "n_regions" in data
    assert "simulation_time_ms" in data
    assert "phases" in data
    assert "order_parameter" in data
    assert "mean_synchronization" in data
    assert "functional_connectivity" in data
    assert "synchronization_level" in data
    
    assert data["n_regions"] == 3
    assert data["simulation_time_ms"] == 2000
    assert isinstance(data["mean_synchronization"], float)
    assert data["synchronization_level"] in ["low", "medium", "high"]


def test_brain_networks_analysis():
    """Test brain networks analysis endpoint"""
    # Matriz de conectividad para análisis de red
    connectivity_matrix = [
        [0.0, 0.8, 0.6, 0.2],
        [0.8, 0.0, 0.7, 0.3],
        [0.6, 0.7, 0.0, 0.4],
        [0.2, 0.3, 0.4, 0.0]
    ]
    
    payload = {
        "connectivity_matrix": connectivity_matrix,
        "threshold": 0.5
    }
    
    response = client.post("/api/neuro-light/brain-networks", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "n_nodes" in data
    assert "threshold" in data
    assert "mean_degree" in data
    assert "mean_clustering" in data
    assert "network_efficiency" in data
    assert "degree_centrality" in data
    assert "clustering_coefficients" in data
    assert "network_type" in data
    
    assert data["n_nodes"] == 4
    assert data["threshold"] == 0.5
    assert isinstance(data["mean_degree"], float)
    assert isinstance(data["mean_clustering"], float)
    assert isinstance(data["network_efficiency"], float)
    assert len(data["degree_centrality"]) == 4
    assert len(data["clustering_coefficients"]) == 4
    assert data["network_type"] in ["small_world", "random"]


def test_whole_brain_simulation_invalid_matrix():
    """Test whole brain simulation with invalid matrix"""
    # Matriz no cuadrada
    invalid_matrix = [
        [0.0, 0.5],
        [0.5, 0.0],
        [0.3, 0.4]
    ]
    
    payload = {
        "connectivity_matrix": invalid_matrix,
        "simulation_time_ms": 1000
    }
    
    response = client.post("/api/neuro-light/whole-brain-simulation", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "cuadrada" in data["error"]


def test_brain_networks_empty_matrix():
    """Test brain networks with empty matrix"""
    payload = {
        "connectivity_matrix": [],
        "threshold": 0.3
    }
    
    response = client.post("/api/neuro-light/brain-networks", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "error" in data
    assert "vacía" in data["error"]


def test_whole_brain_simulation_default_time():
    """Test whole brain simulation with default simulation time"""
    connectivity_matrix = [
        [0.0, 0.6],
        [0.6, 0.0]
    ]
    
    payload = {
        "connectivity_matrix": connectivity_matrix
        # No especificar simulation_time_ms para usar default
    }
    
    response = client.post("/api/neuro-light/whole-brain-simulation", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["simulation_time_ms"] == 10000  # Valor por defecto


def test_brain_networks_default_threshold():
    """Test brain networks with default threshold"""
    connectivity_matrix = [
        [0.0, 0.7],
        [0.7, 0.0]
    ]
    
    payload = {
        "connectivity_matrix": connectivity_matrix
        # No especificar threshold para usar default
    }
    
    response = client.post("/api/neuro-light/brain-networks", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["threshold"] == 0.3  # Valor por defecto
