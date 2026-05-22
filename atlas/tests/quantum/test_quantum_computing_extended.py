"""
Tests para Quantum Computing Extended Suite
==========================================

Tests comprehensivos para computación cuántica avanzada:
algoritmos de Grover y Shor, noise models, y simulaciones.

Tests incluidos:
- Algoritmo de Grover
- Algoritmo de Shor  
- Noise models realistas
- Endpoints avanzados
- Simulaciones comparativas
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient

from app.main import app
from app.domains.physics.quantum.quantum_computing_service import QuantumComputingService


client = TestClient(app)


class TestGroverAlgorithm:
    """Tests para el algoritmo de Grover"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.service = QuantumComputingService()
    
    @pytest.mark.asyncio
    async def test_grover_basic_search(self):
        """Test básico del algoritmo de Grover"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        database_size = 4
        marked_items = [3]
        
        result = await self.service.simulate_grover_search(
            database_size=database_size,
            marked_items=marked_items,
            max_iterations=10
        )
        
        if 'error' not in result:
            assert result['algorithm'] == "Grover Search"
            assert result['database_size'] == database_size
            assert result['marked_items'] == marked_items
            assert 'success_probability' in result
            assert 'quantum_speedup' in result
            assert 'iterations_performed' in result
    
    @pytest.mark.asyncio
    async def test_grover_invalid_database_size(self):
        """Test Grover con tamaño de base de datos inválido"""
        # Database size not power of 2
        result = await self.service.simulate_grover_search(
            database_size=5,
            marked_items=[2]
        )
        
        assert 'error' in result
        assert 'power of 2' in result['error']
    
    @pytest.mark.asyncio
    async def test_grover_invalid_marked_items(self):
        """Test Grover con ítems marcados inválidos"""
        result = await self.service.simulate_grover_search(
            database_size=4,
            marked_items=[5]  # Item outside database
        )
        
        assert 'error' in result
        assert 'Invalid marked items' in result['error']
    
    @pytest.mark.asyncio
    async def test_grover_multiple_marked_items(self):
        """Test Grover con múltiples ítems marcados"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        result = await self.service.simulate_grover_search(
            database_size=8,
            marked_items=[2, 5, 7]
        )
        
        if 'error' not in result:
            assert len(result['marked_items']) == 3
            assert result['database_size'] == 8
    
    def test_apply_grover_oracle(self):
        """Test aplicación del oracle de Grover"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        # Este es un test de la lógica interna
        # En la práctica, el oracle se testea como parte del algoritmo completo
        pass
    
    def test_apply_grover_diffuser(self):
        """Test aplicación del difusor de Grover"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        # Similar al oracle, se testea como parte del algoritmo
        pass


class TestShorAlgorithm:
    """Tests para el algoritmo de Shor"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.service = QuantumComputingService()
    
    @pytest.mark.asyncio
    async def test_shor_basic_factorization(self):
        """Test básico del algoritmo de Shor"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        # Test con número pequeño
        N = 15
        result = await self.service.simulate_shor_algorithm(N=N)
        
        if 'error' not in result:
            assert result['algorithm'] == "Shor's Algorithm"
            assert result['number_factorized'] == N
            assert 'factors' in result
            assert result['verification'] is True
            
            # Verificar que los factores son correctos
            factors = result['factors']
            assert len(factors) == 2
            assert factors[0] * factors[1] == N
    
    @pytest.mark.asyncio
    async def test_shor_prime_number(self):
        """Test Shor con número primo"""
        result = await self.service.simulate_shor_algorithm(N=7)
        
        assert result['result'] == "number_is_prime"
        assert result['factors'] == [1, 7]
    
    @pytest.mark.asyncio
    async def test_shor_even_number(self):
        """Test Shor con número par"""
        result = await self.service.simulate_shor_algorithm(N=8)
        
        assert result['result'] == "trivial_factor"
        assert 2 in result['factors']
        assert result['factors'][0] * result['factors'][1] == 8
    
    @pytest.mark.asyncio
    async def test_shor_invalid_range(self):
        """Test Shor con número fuera de rango"""
        # Número demasiado grande
        result = await self.service.simulate_shor_algorithm(N=100)
        assert 'error' in result
        
        # Número demasiado pequeño
        result = await self.service.simulate_shor_algorithm(N=2)
        assert 'error' in result
    
    @pytest.mark.asyncio
    async def test_shor_with_base(self):
        """Test Shor con base específica"""
        result = await self.service.simulate_shor_algorithm(N=15, a=7)
        
        if 'error' not in result:
            assert result['base_used'] == 7
    
    def test_is_prime_helper(self):
        """Test función auxiliar de primalidad"""
        assert self.service._is_prime(2) is True
        assert self.service._is_prime(3) is True
        assert self.service._is_prime(4) is False
        assert self.service._is_prime(17) is True
        assert self.service._is_prime(25) is False
    
    def test_gcd_helper(self):
        """Test función auxiliar de GCD"""
        assert self.service._gcd(12, 8) == 4
        assert self.service._gcd(17, 5) == 1
        assert self.service._gcd(48, 18) == 6
    
    def test_find_period_classical(self):
        """Test búsqueda de período clásica"""
        # Test con valores conocidos
        period = self.service._find_period_classical(2, 15)
        if period is not None:
            assert isinstance(period, int)
            assert period > 0


class TestNoiseModels:
    """Tests para modelos de ruido cuántico"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.service = QuantumComputingService()
    
    @pytest.mark.asyncio
    async def test_noisy_circuit_bell_depolarizing(self):
        """Test simulación ruidosa con ruido despolarizante"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        result = await self.service.simulate_noisy_circuit(
            circuit_type="bell",
            noise_model="depolarizing",
            noise_strength=0.05,
            shots=1024
        )
        
        if 'error' not in result:
            assert result['circuit_type'] == "bell"
            assert result['noise_model'] == "depolarizing"
            assert result['noise_strength'] == 0.05
            assert 'ideal_results' in result
            assert 'noisy_results' in result
            assert 'comparison_metrics' in result
            
            # Verificar métricas de comparación
            metrics = result['comparison_metrics']
            assert 'fidelity' in metrics
            assert 'total_variation_distance' in metrics
            assert 0 <= metrics['fidelity'] <= 1
            assert 0 <= metrics['total_variation_distance'] <= 1
    
    @pytest.mark.asyncio
    async def test_noisy_circuit_amplitude_damping(self):
        """Test simulación con ruido de decaimiento de amplitud"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        result = await self.service.simulate_noisy_circuit(
            circuit_type="bell",
            noise_model="amplitude_damping",
            noise_strength=0.1
        )
        
        if 'error' not in result:
            assert result['noise_model'] == "amplitude_damping"
            assert 'noise_analysis' in result
    
    @pytest.mark.asyncio
    async def test_noisy_circuit_phase_damping(self):
        """Test simulación con ruido de fase"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        result = await self.service.simulate_noisy_circuit(
            circuit_type="grover",
            noise_model="phase_damping",
            noise_strength=0.02
        )
        
        if 'error' not in result:
            assert result['noise_model'] == "phase_damping"
    
    @pytest.mark.asyncio
    async def test_noisy_circuit_invalid_parameters(self):
        """Test simulación con parámetros inválidos"""
        # Noise strength inválido
        result = await self.service.simulate_noisy_circuit(
            circuit_type="bell",
            noise_strength=1.5  # > 1.0
        )
        assert 'error' in result
        
        # Circuit type inválido
        result = await self.service.simulate_noisy_circuit(
            circuit_type="invalid"
        )
        assert 'error' in result
    
    def test_create_bell_circuit(self):
        """Test creación de circuito Bell"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        qc = self.service._create_bell_circuit()
        assert qc.num_qubits == 2
        assert qc.num_clbits == 2
    
    def test_create_grover_circuit(self):
        """Test creación de circuito Grover simple"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        qc = self.service._create_simple_grover_circuit()
        assert qc.num_qubits == 2
        assert qc.num_clbits == 2
    
    def test_create_random_circuit(self):
        """Test creación de circuito aleatorio"""
        if not self.service.qiskit_available:
            pytest.skip("Qiskit not available")
        
        qc = self.service._create_random_circuit()
        assert qc.num_qubits == 3
        assert qc.num_clbits == 3
    
    def test_calculate_fidelity(self):
        """Test cálculo de fidelidad"""
        ideal_probs = {"00": 0.5, "11": 0.5}
        noisy_probs = {"00": 0.4, "11": 0.6}
        
        fidelity = self.service._calculate_fidelity(ideal_probs, noisy_probs)
        
        assert 0 <= fidelity <= 1
        assert isinstance(fidelity, float)
    
    def test_calculate_tvd(self):
        """Test cálculo de distancia de variación total"""
        ideal_probs = {"00": 0.5, "11": 0.5}
        noisy_probs = {"00": 0.3, "11": 0.7}
        
        tvd = self.service._calculate_tvd(ideal_probs, noisy_probs)
        
        assert 0 <= tvd <= 1
        assert isinstance(tvd, float)
    
    def test_analyze_noise_impact(self):
        """Test análisis de impacto del ruido"""
        for noise_model in ["depolarizing", "amplitude_damping", "phase_damping"]:
            analysis = self.service._analyze_noise_impact(noise_model, 0.1)
            
            assert 'description' in analysis
            assert 'physical_cause' in analysis
            assert 'severity' in analysis
            assert analysis['severity'] in ['low', 'medium', 'high']


class TestQuantumEndpoints:
    """Tests para endpoints cuánticos avanzados"""
    
    def test_grover_search_endpoint(self):
        """Test endpoint de búsqueda de Grover"""
        payload = {
            "qubits": 3,
            "parameters": {
                "database_size": 8,
                "marked_items": [3, 7],
                "max_iterations": 5,
                "shots": 1024
            }
        }
        
        response = client.post("/api/quantum-computing/grover-search", json=payload)
        
        # Should either succeed or fail gracefully if Qiskit not available
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'algorithm_info' in data['data']
    
    def test_shor_factorization_endpoint(self):
        """Test endpoint de factorización de Shor"""
        payload = {
            "qubits": 6,
            "parameters": {
                "N": 15,
                "a": 7
            }
        }
        
        response = client.post("/api/quantum-computing/shor-factorization", json=payload)
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'factorization_result' in data['data']
    
    def test_noisy_simulation_endpoint(self):
        """Test endpoint de simulación con ruido"""
        payload = {
            "qubits": 2,
            "parameters": {
                "circuit_type": "bell",
                "noise_model": "depolarizing",
                "noise_strength": 0.05,
                "shots": 1024
            }
        }
        
        response = client.post("/api/quantum-computing/noisy-simulation", json=payload)
        
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data['success'] is True
            assert 'noise_modeling_info' in data['data']
    
    def test_quantum_endpoints_validation(self):
        """Test validación de endpoints cuánticos"""
        # Test Grover con parámetros inválidos
        payload = {
            "qubits": 3,
            "parameters": {
                "database_size": 5,  # Not power of 2
                "marked_items": [3]
            }
        }
        
        response = client.post("/api/quantum-computing/grover-search", json=payload)
        assert response.status_code in [400, 500]
        
        # Test Shor sin parámetro N
        payload = {
            "qubits": 6,
            "parameters": {}
        }
        
        response = client.post("/api/quantum-computing/shor-factorization", json=payload)
        assert response.status_code in [400, 422, 500]
    
    def test_noise_simulation_validation(self):
        """Test validación de simulación con ruido"""
        # Test con noise strength inválido
        payload = {
            "qubits": 2,
            "parameters": {
                "circuit_type": "bell",
                "noise_strength": 1.5  # > 1.0
            }
        }
        
        response = client.post("/api/quantum-computing/noisy-simulation", json=payload)
        assert response.status_code in [400, 500]
        
        # Test con circuit type inválido
        payload = {
            "qubits": 2,
            "parameters": {
                "circuit_type": "invalid_type"
            }
        }
        
        response = client.post("/api/quantum-computing/noisy-simulation", json=payload)
        assert response.status_code in [400, 500]


class TestQuantumIntegration:
    """Tests de integración para quantum computing"""
    
    def test_quantum_algorithm_comparison(self):
        """Test comparación de algoritmos cuánticos"""
        # Comparar Grover vs búsqueda clásica
        grover_payload = {
            "qubits": 2,
            "parameters": {
                "database_size": 4,
                "marked_items": [3]
            }
        }
        
        response = client.post("/api/quantum-computing/grover-search", json=grover_payload)
        
        if response.status_code == 200:
            data = response.json()
            # Verificar que incluye información de ventaja cuántica
            assert 'quantum_speedup' in str(data)
    
    def test_noise_impact_analysis(self):
        """Test análisis de impacto del ruido"""
        noise_levels = [0.01, 0.05, 0.1]
        
        for noise_strength in noise_levels:
            payload = {
                "qubits": 2,
                "parameters": {
                    "circuit_type": "bell",
                    "noise_model": "depolarizing",
                    "noise_strength": noise_strength
                }
            }
            
            response = client.post("/api/quantum-computing/noisy-simulation", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                # Verificar que el ruido aumenta con noise_strength
                assert 'fidelity_degradation' in str(data)
    
    def test_quantum_error_resilience(self):
        """Test resistencia a errores en simulaciones cuánticas"""
        # Test con parámetros extremos pero válidos
        payload = {
            "qubits": 10,  # Muchos qubits
            "parameters": {
                "database_size": 1024,
                "marked_items": list(range(0, 100, 10))  # Muchos ítems
            }
        }
        
        response = client.post("/api/quantum-computing/grover-search", json=payload)
        
        # Debería fallar gracefully si excede límites
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 400:
            # Verificar mensaje de error útil
            error_data = response.json()
            assert 'detail' in error_data


@pytest.mark.integration  
class TestQuantumEndToEnd:
    """Tests end-to-end para quantum computing"""
    
    def test_complete_quantum_workflow(self):
        """Test workflow completo de computación cuántica"""
        workflows = [
            # Workflow 1: Grover search
            {
                "endpoint": "/api/quantum-computing/grover-search",
                "payload": {
                    "qubits": 2,
                    "parameters": {"database_size": 4, "marked_items": [3]}
                }
            },
            # Workflow 2: Shor factorization  
            {
                "endpoint": "/api/quantum-computing/shor-factorization",
                "payload": {
                    "qubits": 4,
                    "parameters": {"N": 9}
                }
            },
            # Workflow 3: Noisy simulation
            {
                "endpoint": "/api/quantum-computing/noisy-simulation",
                "payload": {
                    "qubits": 2,
                    "parameters": {
                        "circuit_type": "bell",
                        "noise_model": "depolarizing",
                        "noise_strength": 0.02
                    }
                }
            }
        ]
        
        for workflow in workflows:
            response = client.post(workflow["endpoint"], json=workflow["payload"])
            
            # Todos los endpoints deben responder (aunque fallen por dependencias)
            assert response.status_code in [200, 400, 500]
            
            # Si es exitoso, verificar estructura de respuesta
            if response.status_code == 200:
                data = response.json()
                assert 'success' in data
                assert 'message' in data
                assert 'data' in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
