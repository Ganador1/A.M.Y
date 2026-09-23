"""
Tests de smoke para validación estadística rigurosa
"""

import pytest
from fastapi.testclient import TestClient
from app.routers.statistical_validation import router

# Cliente de test
client = TestClient(router)


def test_validate_hypothesis_smoke():
    """Test básico de validación de hipótesis"""
    data = {
        "data": [1.2, 1.8, 2.1, 2.3, 2.4, 2.6, 2.9, 3.1, 3.4, 3.7],
        "hypothesis_type": "one_sample_ttest",
        "mu": 2.0,
        "confidence_level": 0.95,
        "alpha": 0.05,
        "power": 0.8
    }
    
    response = client.post("/validate-hypothesis", json=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "is_valid" in result
    assert "power_analysis" in result
    assert "effect_sizes" in result
    assert "assumptions_check" in result
    assert "recommendations" in result


def test_power_analysis_smoke():
    """Test básico de análisis de poder"""
    data = {
        "effect_size": 0.5,
        "sample_size": 30,
        "alpha": 0.05
    }
    
    response = client.post("/power-analysis", json=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "effect_size" in result
    assert "calculated" in result
    assert "interpretation" in result


def test_multiple_testing_smoke():
    """Test básico de corrección múltiple"""
    data = {
        "p_values": [0.01, 0.03, 0.08, 0.002, 0.15],
        "method": "bonferroni",
        "alpha": 0.05
    }
    
    response = client.post("/multiple-testing", json=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "corrected_p_values" in result
    assert "rejected_hypotheses" in result
    assert "significant_before" in result
    assert "significant_after" in result


def test_effect_sizes_smoke():
    """Test básico de tamaños de efecto"""
    data = {
        "data1": [2.1, 2.3, 2.2, 2.4, 2.1, 2.5],
        "data2": [2.8, 3.1, 2.9, 3.2, 3.0, 3.3],
        "test_type": "cohen_d"
    }
    
    response = client.post("/effect-sizes", json=data)
    assert response.status_code == 200
    
    result = response.json()
    assert "effect_sizes" in result
    assert "interpretation" in result
    assert "sample_info" in result


def test_validation_config_smoke():
    """Test de configuración disponible"""
    response = client.get("/validation-config")
    assert response.status_code == 200
    
    result = response.json()
    assert "hypothesis_types" in result
    assert "multiple_testing_methods" in result
    assert "effect_size_types" in result
    assert "default_config" in result
    assert "dependencies" in result


def test_hypothesis_validation_edge_cases():
    """Test de casos límite"""
    # Datos insuficientes
    data = {
        "data": [1.0, 2.0],  # Solo 2 datos
        "hypothesis_type": "one_sample_ttest"
    }
    
    response = client.post("/validate-hypothesis", json=data)
    assert response.status_code == 400


def test_multiple_testing_edge_cases():
    """Test de casos límite para corrección múltiple"""
    # Solo un valor p
    data = {
        "p_values": [0.05],
        "method": "bonferroni"
    }
    
    response = client.post("/multiple-testing", json=data)
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__])
