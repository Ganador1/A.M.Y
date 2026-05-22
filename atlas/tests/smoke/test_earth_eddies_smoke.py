"""
Smoke tests for Earth Sciences Light eddies endpoint
"""
import pytest
from fastapi.testclient import TestClient
from app.routers.earth_sciences_light import router


client = TestClient(router)


def test_eddies_2d_detection():
    """Test 2D eddies detection endpoint"""
    payload = {
        "grid": [
            [0.1, 0.06, -0.07],
            [0.02, -0.08, 0.09],
            [0.05, -0.12, 0.03]
        ],
        "threshold": 0.05
    }
    response = client.post("/api/earth-light/eddies-2d", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "threshold" in data
    assert "cyclonic_count" in data
    assert "anticyclonic_count" in data
    assert isinstance(data["cyclonic_count"], int)
    assert isinstance(data["anticyclonic_count"], int)


def test_eddies_2d_invalid_grid():
    """Test eddies detection with invalid grid"""
    payload = {
        "grid": [],
        "threshold": 0.05
    }
    response = client.post("/api/earth-light/eddies-2d", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "error" in data


def test_eddies_2d_default_threshold():
    """Test eddies detection with default threshold"""
    payload = {
        "grid": [
            [0.1, 0.06, -0.07],
            [0.02, -0.08, 0.09]
        ]
    }
    response = client.post("/api/earth-light/eddies-2d", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["threshold"] == 0.05
