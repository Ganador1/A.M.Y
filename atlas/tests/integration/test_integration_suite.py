"""
Integration Test Suite - Nuevas Funcionalidades
===============================================

Test suite comprehensivo que valida la integración de todas las
nuevas funcionalidades implementadas: Lean4, Uncertainty Quantification
y Quantum Computing avanzado.

Tests incluidos:
- Smoke tests de todos los nuevos endpoints
- Tests de integración cross-funcional
- Validación de consistency entre servicios
- Performance benchmarks básicos
"""

import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from app.main import app


client = TestClient(app)


class TestSmokeTests:
    """Smoke tests para verificar que todos los endpoints respondan"""
    
    def test_lean4_endpoints_smoke(self):
        """Smoke test para todos los endpoints de Lean4"""
        endpoints = [
            ("GET", "/api/lean4/detect", None),
            ("POST", "/api/lean4/validate", None),
            ("GET", "/api/lean4/system-info", None),
            ("POST", "/api/lean4/diagnose", {
                "error_message": "test error",
                "include_system_info": False
            })
        ]
        
        for method, endpoint, payload in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=payload)
            
            # Debe responder (aunque falle por dependencias)
            assert response.status_code in [200, 400, 422, 500], f"Failed: {method} {endpoint}"
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict), f"Invalid response format: {endpoint}"
    
    def test_uncertainty_endpoints_smoke(self):
        """Smoke test para todos los endpoints de uncertainty quantification"""
        endpoints = [
            ("/api/uncertainty-quantification/methods", "GET", None),
            ("/api/uncertainty-quantification/monte-carlo", "POST", {
                "test_data": [[1, 2], [3, 4]],
                "num_samples": 10,
                "dropout_rate": 0.1
            }),
            ("/api/uncertainty-quantification/ensemble", "POST", {
                "test_data": [[1, 2], [3, 4]],
                "ensemble_size": 3
            }),
            ("/api/uncertainty-quantification/bootstrap", "POST", {
                "test_data": [[1, 2], [3, 4]],
                "num_samples": 10
            }),
            ("/api/uncertainty-quantification/conformal", "POST", {
                "X_train": [[1, 2], [3, 4], [5, 6]],
                "y_train": [3, 7, 11],
                "X_test": [[2, 3]],
                "method": "split"
            }),
            ("/api/uncertainty-quantification/compare-methods", "POST", {
                "test_data": [[1, 2]],
                "methods": ["dropout", "ensemble"]
            })
        ]
        
        for endpoint, method, payload in endpoints:
            if method == "GET":
                response = client.get(endpoint)
            else:
                response = client.post(endpoint, json=payload)
            
            assert response.status_code in [200, 400, 422, 500], f"Failed: {method} {endpoint}"
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict), f"Invalid response format: {endpoint}"
    
    def test_quantum_endpoints_smoke(self):
        """Smoke test para endpoints cuánticos avanzados"""
        endpoints = [
            ("/api/quantum-computing/grover-search", {
                "qubits": 2,
                "parameters": {
                    "database_size": 4,
                    "marked_items": [3]
                }
            }),
            ("/api/quantum-computing/shor-factorization", {
                "qubits": 4,
                "parameters": {
                    "N": 9
                }
            }),
            ("/api/quantum-computing/noisy-simulation", {
                "qubits": 2,
                "parameters": {
                    "circuit_type": "bell",
                    "noise_model": "depolarizing",
                    "noise_strength": 0.01
                }
            })
        ]
        
        for endpoint, payload in endpoints:
            response = client.post(endpoint, json=payload)
            
            assert response.status_code in [200, 400, 422, 500], f"Failed: {endpoint}"
            
            if response.status_code == 200:
                data = response.json()
                assert 'success' in data, f"Missing success field: {endpoint}"
                assert 'data' in data, f"Missing data field: {endpoint}"


class TestCrossServiceIntegration:
    """Tests de integración entre servicios"""
    
    def test_lean4_to_uncertainty_workflow(self):
        """Test workflow: detectar Lean4 → usar uncertainty en resultados"""
        # 1. Detectar estado de Lean4
        response = client.get("/api/lean4/detect")
        assert response.status_code == 200
        lean4_info = response.json()
        
        # 2. Simular usar uncertainty para evaluar confianza en detección
        confidence_data = [[1.0 if lean4_info['is_supported_system'] else 0.0]]
        
        uc_response = client.post("/api/uncertainty-quantification/monte-carlo", json={
            "test_data": confidence_data,
            "num_samples": 10
        })
        
        assert uc_response.status_code == 200
        uc_result = uc_response.json()
        assert 'uncertainty_metrics' in uc_result
    
    def test_quantum_to_uncertainty_workflow(self):
        """Test workflow: simular quantum → uncertainty en resultados"""
        # 1. Ejecutar simulación cuántica con ruido
        quantum_response = client.post("/api/quantum-computing/noisy-simulation", json={
            "qubits": 2,
            "parameters": {
                "circuit_type": "bell",
                "noise_strength": 0.05
            }
        })
        
        if quantum_response.status_code == 200:
            quantum_data = quantum_response.json()
            
            # 2. Usar fidelity como entrada para uncertainty analysis
            if 'data' in quantum_data and 'comparison_metrics' in quantum_data['data']:
                fidelity = quantum_data['data']['comparison_metrics'].get('fidelity', 0.5)
                
                uc_response = client.post("/api/uncertainty-quantification/bootstrap", json={
                    "test_data": [[fidelity, 1-fidelity]],
                    "num_samples": 10
                })
                
                assert uc_response.status_code == 200
    
    def test_error_propagation_across_services(self):
        """Test propagación de errores entre servicios"""
        # Test con datos inválidos que deberían fallar consistentemente
        invalid_payloads = [
            # Lean4 con mensaje de error vacío
            ("POST", "/api/lean4/diagnose", {"error_message": ""}),
            
            # Uncertainty con datos vacíos  
            ("POST", "/api/uncertainty-quantification/monte-carlo", {"test_data": []}),
            
            # Quantum con parámetros inválidos
            ("POST", "/api/quantum-computing/grover-search", {
                "qubits": 2,
                "parameters": {"database_size": 3}  # Not power of 2
            })
        ]
        
        for method, endpoint, payload in invalid_payloads:
            response = client.post(endpoint, json=payload)
            
            # Todos deben manejar errores gracefully
            assert response.status_code in [400, 422, 500]
            
            if response.status_code in [400, 500]:
                error_data = response.json()
                assert 'detail' in error_data or 'message' in error_data


class TestConsistencyValidation:
    """Validación de consistencia entre servicios"""
    
    def test_response_format_consistency(self):
        """Verificar consistencia en formato de respuestas"""
        # Obtener respuestas exitosas de cada servicio
        responses = []
        
        # Lean4
        lean4_response = client.get("/api/lean4/detect")
        if lean4_response.status_code == 200:
            responses.append(("lean4", lean4_response.json()))
        
        # Uncertainty
        uc_response = client.post("/api/uncertainty-quantification/monte-carlo", json={
            "test_data": [[1, 2]],
            "num_samples": 10
        })
        if uc_response.status_code == 200:
            responses.append(("uncertainty", uc_response.json()))
        
        # Quantum
        quantum_response = client.post("/api/quantum-computing/grover-search", json={
            "qubits": 2,
            "parameters": {"database_size": 4, "marked_items": [3]}
        })
        if quantum_response.status_code == 200:
            responses.append(("quantum", quantum_response.json()))
        
        # Verificar consistencia (al menos en estructura básica)
        for service_name, response in responses:
            assert isinstance(response, dict), f"{service_name}: not a dict"
            # Diferentes servicios pueden tener diferentes estructuras,
            # pero deben ser objetos JSON válidos
    
    def test_error_format_consistency(self):
        """Verificar consistencia en formato de errores"""
        error_endpoints = [
            ("POST", "/api/lean4/diagnose", {"error_message": ""}),
            ("POST", "/api/uncertainty-quantification/monte-carlo", {"test_data": []}),
            ("POST", "/api/quantum-computing/grover-search", {
                "qubits": 2, 
                "parameters": {"database_size": 3}
            })
        ]
        
        for method, endpoint, payload in error_endpoints:
            response = client.post(endpoint, json=payload)
            
            if response.status_code == 422:  # Validation error
                error_data = response.json()
                assert 'detail' in error_data
            elif response.status_code in [400, 500]:
                error_data = response.json()
                # Debe tener algún campo de error
                assert any(key in error_data for key in ['detail', 'message', 'error'])


class TestPerformanceBenchmarks:
    """Benchmarks básicos de performance"""
    
    def test_lean4_detection_performance(self):
        """Benchmark de detección de Lean4"""
        start_time = time.time()
        
        response = client.get("/api/lean4/detect")
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed < 5.0, f"Lean4 detection too slow: {elapsed:.2f}s"
    
    def test_uncertainty_monte_carlo_performance(self):
        """Benchmark de Monte Carlo Dropout"""
        start_time = time.time()
        
        response = client.post("/api/uncertainty-quantification/monte-carlo", json={
            "test_data": [[i, i+1] for i in range(10)],
            "num_samples": 50  # Reduced for performance
        })
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            assert elapsed < 10.0, f"Monte Carlo too slow: {elapsed:.2f}s"
    
    def test_quantum_simulation_performance(self):
        """Benchmark de simulación cuántica"""
        start_time = time.time()
        
        response = client.post("/api/quantum-computing/grover-search", json={
            "qubits": 2,
            "parameters": {
                "database_size": 4,
                "marked_items": [3]
            }
        })
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            assert elapsed < 15.0, f"Quantum simulation too slow: {elapsed:.2f}s"
    
    def test_concurrent_requests_handling(self):
        """Test manejo de requests concurrentes"""
        def make_request():
            return client.get("/api/lean4/detect")
        
        # Ejecutar 5 requests concurrentes
        with ThreadPoolExecutor(max_workers=5) as executor:
            start_time = time.time()
            futures = [executor.submit(make_request) for _ in range(5)]
            responses = [f.result() for f in futures]
            elapsed = time.time() - start_time
        
        # Todas deben responder
        assert all(r.status_code == 200 for r in responses)
        
        # No debe tomar demasiado tiempo
        assert elapsed < 10.0, f"Concurrent requests too slow: {elapsed:.2f}s"


class TestDataFlowValidation:
    """Validación de flujo de datos entre servicios"""
    
    def test_numerical_data_consistency(self):
        """Verificar consistencia de datos numéricos"""
        # Generar datos de prueba
        test_data = np.random.randn(5, 2).tolist()
        
        # Usar los mismos datos en uncertainty quantification
        responses = []
        
        methods = ["monte-carlo", "ensemble", "bootstrap"]
        for method in methods:
            endpoint = f"/api/uncertainty-quantification/{method}"
            payload = {"test_data": test_data}
            if method == "ensemble":
                payload["ensemble_size"] = 3
            elif method == "monte-carlo":
                payload["num_samples"] = 10
            
            response = client.post(endpoint, json=payload)
            if response.status_code == 200:
                responses.append((method, response.json()))
        
        # Verificar que todos procesan los mismos datos correctamente
        for method, response_data in responses:
            # Debe haber procesado el número correcto de puntos
            if 'predictions' in response_data:
                predictions = response_data['predictions']
                if isinstance(predictions, dict) and 'mean' in predictions:
                    assert len(predictions['mean']) == len(test_data)
    
    def test_quantum_state_validation(self):
        """Verificar validez de estados cuánticos"""
        response = client.post("/api/quantum-computing/noisy-simulation", json={
            "qubits": 2,
            "parameters": {
                "circuit_type": "bell",
                "noise_model": "depolarizing",
                "noise_strength": 0.01,
                "shots": 100
            }
        })
        
        if response.status_code == 200:
            data = response.json()
            
            if 'data' in data and 'ideal_results' in data['data']:
                ideal_results = data['data']['ideal_results']
                
                # Verificar que las probabilidades suman 1
                if isinstance(ideal_results, dict):
                    total_prob = sum(ideal_results.values())
                    assert abs(total_prob - 1.0) < 0.01, f"Probabilities don't sum to 1: {total_prob}"


@pytest.mark.integration
class TestFullSystemIntegration:
    """Tests de integración del sistema completo"""
    
    def test_end_to_end_scientific_workflow(self):
        """Test workflow científico completo usando todas las funcionalidades"""
        workflow_results = {}
        
        # 1. Fase de Setup: Verificar herramientas disponibles
        lean4_status = client.get("/api/lean4/detect")
        workflow_results['lean4_detection'] = lean4_status.status_code == 200
        
        # 2. Fase de Simulación: Ejecutar simulación cuántica
        quantum_result = client.post("/api/quantum-computing/grover-search", json={
            "qubits": 2,
            "parameters": {"database_size": 4, "marked_items": [3]}
        })
        workflow_results['quantum_simulation'] = quantum_result.status_code == 200
        
        # 3. Fase de Análisis: Quantificar incertidumbre en resultados
        if quantum_result.status_code == 200:
            # Usar resultados de quantum para uncertainty analysis
            uc_result = client.post("/api/uncertainty-quantification/monte-carlo", json={
                "test_data": [[0.8, 0.2], [0.9, 0.1]],  # Simulated quantum results
                "num_samples": 20
            })
            workflow_results['uncertainty_analysis'] = uc_result.status_code == 200
        
        # 4. Fase de Validación: Diagnosticar cualquier problema
        if not all(workflow_results.values()):
            diagnosis = client.post("/api/lean4/diagnose", json={
                "error_message": "workflow validation failed",
                "include_system_info": True
            })
            workflow_results['error_diagnosis'] = diagnosis.status_code == 200
        
        # Al menos el 50% del workflow debe funcionar
        success_rate = sum(workflow_results.values()) / len(workflow_results)
        assert success_rate >= 0.5, f"Workflow success rate too low: {success_rate:.2f}"
    
    def test_system_resilience_under_load(self):
        """Test resilencia del sistema bajo carga"""
        # Definir batería de tests
        test_battery = [
            ("GET", "/api/lean4/detect", None),
            ("POST", "/api/uncertainty-quantification/methods", None),
            ("POST", "/api/uncertainty-quantification/monte-carlo", {
                "test_data": [[1, 2]], "num_samples": 5
            }),
            ("GET", "/api/lean4/system-info", None)
        ]
        
        # Ejecutar múltiples veces
        results = []
        for _ in range(3):  # 3 iterations para no sobrecargar
            for method, endpoint, payload in test_battery:
                try:
                    if method == "GET":
                        response = client.get(endpoint)
                    else:
                        response = client.post(endpoint, json=payload)
                    
                    results.append(response.status_code in [200, 400])
                except Exception:
                    results.append(False)
        
        # Al menos 80% debe funcionar
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.8, f"System resilience too low: {success_rate:.2f}"


class TestDocumentationConsistency:
    """Verificar consistencia con documentación"""
    
    def test_endpoint_availability(self):
        """Verificar que endpoints documentados estén disponibles"""
        documented_endpoints = [
            # Lean4 Management
            "/api/lean4/detect",
            "/api/lean4/validate", 
            "/api/lean4/system-info",
            "/api/lean4/diagnose",
            
            # Uncertainty Quantification
            "/api/uncertainty-quantification/methods",
            "/api/uncertainty-quantification/monte-carlo",
            "/api/uncertainty-quantification/ensemble",
            "/api/uncertainty-quantification/conformal",
            "/api/uncertainty-quantification/bootstrap",
            "/api/uncertainty-quantification/compare-methods",
            
            # Quantum Computing
            "/api/quantum-computing/grover-search",
            "/api/quantum-computing/shor-factorization",
            "/api/quantum-computing/noisy-simulation"
        ]
        
        for endpoint in documented_endpoints:
            # Verificar que al menos responda (no 404)
            if endpoint.endswith(('/detect', '/methods', '/system-info')):
                response = client.get(endpoint)
            else:
                # POST endpoints con payload mínimo
                response = client.post(endpoint, json={})
            
            assert response.status_code != 404, f"Endpoint not found: {endpoint}"


if __name__ == "__main__":
    # Ejecutar todos los tests
    pytest.main([__file__, "-v", "--tb=short"])
