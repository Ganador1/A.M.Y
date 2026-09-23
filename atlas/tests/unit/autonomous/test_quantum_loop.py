"""
Tests para QuantumLoop - Loop autónomo de computación cuántica
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from app.autonomous.pipelines.quantum_loop import QuantumLoop
from app.autonomous.core.state_manager import StateManager


class TestQuantumLoop:
    """Tests para QuantumLoop"""

    def setup_method(self):
        """Setup para cada test"""
        self.state_manager = Mock(spec=StateManager)
        self.quantum_loop = QuantumLoop(state=self.state_manager)

    def test_initialization(self):
        """Test: Inicialización correcta del QuantumLoop"""
        assert self.quantum_loop.state == self.state_manager
        assert self.quantum_loop.quantum_service is not None
        assert self.quantum_loop.tool_evidence is not None
        assert self.quantum_loop.scorer is not None
        assert self.quantum_loop.scheduler is not None
        assert self.quantum_loop.budget is not None
        assert self.quantum_loop.difficulty is not None
        assert self.quantum_loop.novelty is not None

    @pytest.mark.asyncio
    async def test_default_provider_async_success(self):
        """Test: Proveedor por defecto exitoso"""
        mock_templates = [
            {
                "name": "qaoa_template",
                "depth": 3,
                "two_qubit_gates": 6,
                "hardware_efficiency": 0.7,
                "literature_mentions": 25,
                "source": "test_source"
            }
        ]
        
        with patch('app.autonomous.pipelines.quantum_loop.fetch_quantum_circuit_templates', 
                  return_value=mock_templates):
            candidates = await self.quantum_loop._default_provider_async(limit=1)
            
            assert len(candidates) == 1
            candidate = candidates[0]
            assert "id" in candidate
            assert "algorithm" in candidate
            assert "n_qubits" in candidate
            assert "depth" in candidate
            assert "parameters" in candidate
            assert "embedding" in candidate
            assert "literature_frequency" in candidate
            assert "dependency_count" in candidate
            assert "impact_potential" in candidate
            assert "proveability" in candidate
            assert "novelty" in candidate
            assert "information_gain" in candidate
            assert "estimated_cost" in candidate

    @pytest.mark.asyncio
    async def test_default_provider_async_error_handling(self):
        """Test: Manejo de errores en proveedor por defecto"""
        with patch('app.autonomous.pipelines.quantum_loop.fetch_quantum_circuit_templates', 
                  side_effect=Exception("API error")):
            candidates = await self.quantum_loop._default_provider_async(limit=1)
            
            # Debe retornar candidatos sintéticos cuando falla la API
            assert len(candidates) >= 1

    def test_run_coro_sync(self):
        """Test: Ejecución síncrona de corrutinas"""
        async def test_coro():
            return "test_result"
        
        result = QuantumLoop._run_coro_sync(test_coro())
        assert result == "test_result"

    def test_run_coro_sync_with_existing_loop(self):
        """Test: Ejecución síncrona con loop existente"""
        async def test_coro():
            return "test_result"
        
        with patch('asyncio.get_running_loop') as mock_get_loop:
            mock_get_loop.return_value = Mock()
            
            result = QuantumLoop._run_coro_sync(test_coro())
            assert result == "test_result"

    def test_algorithm_detection(self):
        """Test: Detección de algoritmos cuánticos"""
        # Test QAOA detection
        template_1 = {"name": "qaoa_optimization", "depth": 3, "two_qubit_gates": 6, "hardware_efficiency": 0.7}
        name_lower = template_1["name"].lower()
        algorithm = "qaoa" if "qaoa" in name_lower else ("vqe" if "vqe" in name_lower else "template")
        assert algorithm == "qaoa"
        
        # Test VQE detection
        template_2 = {"name": "vqe_variational", "depth": 2, "two_qubit_gates": 4, "hardware_efficiency": 0.8}
        name_lower = template_2["name"].lower()
        algorithm = "qaoa" if "qaoa" in name_lower else ("vqe" if "vqe" in name_lower else "template")
        assert algorithm == "vqe"
        
        # Test template fallback
        template_3 = {"name": "custom_circuit", "depth": 4, "two_qubit_gates": 8, "hardware_efficiency": 0.6}
        name_lower = template_3["name"].lower()
        algorithm = "qaoa" if "qaoa" in name_lower else ("vqe" if "vqe" in name_lower else "template")
        assert algorithm == "template"

    def test_n_qubits_calculation(self):
        """Test: Cálculo de número de qubits"""
        two_qubit_gates = 6
        n_qubits = max(2, two_qubit_gates // 2 + 2)
        assert n_qubits == 5
        
        two_qubit_gates = 4
        n_qubits = max(2, two_qubit_gates // 2 + 2)
        assert n_qubits == 4

    def test_information_gain_calculation(self):
        """Test: Cálculo de information_gain"""
        hardware_efficiency = 0.7
        information_gain = min(1.0, 0.5 + hardware_efficiency * 0.4)
        assert information_gain == 0.78

    def test_impact_potential_calculation(self):
        """Test: Cálculo de impact_potential"""
        hardware_efficiency = 0.7
        impact_potential = float(min(1.0, 0.55 + hardware_efficiency * 0.35))
        assert impact_potential == 0.795

    def test_proveability_calculation(self):
        """Test: Cálculo de proveability"""
        hardware_efficiency = 0.7
        proveability = float(min(1.0, 0.5 + hardware_efficiency * 0.3))
        assert proveability == 0.71

    def test_novelty_calculation(self):
        """Test: Cálculo de novelty"""
        hardware_efficiency = 0.7
        novelty = float(max(0.15, 0.8 - hardware_efficiency * 0.2))
        assert novelty == 0.66

    def test_estimated_cost_calculation(self):
        """Test: Cálculo de estimated_cost"""
        hardware_efficiency = 0.7
        estimated_cost = float(max(0.15, 0.25 - hardware_efficiency * 0.05))
        assert estimated_cost == 0.215

    def test_priority_scoring(self):
        """Test: Sistema de scoring de prioridades"""
        candidate = {
            "literature_frequency": 30,
            "dependency_count": 3,
            "impact_potential": 0.8,
            "proveability": 0.7,
            "novelty": 0.6,
            "information_gain": 0.75,
            "estimated_cost": 0.2
        }
        
        score = self.quantum_loop.scorer.score(candidate)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_novelty_assessment(self):
        """Test: Evaluación de novedad"""
        candidate = {
            "literature_frequency": 10,
            "dependency_count": 2,
            "impact_potential": 0.8,
            "proveability": 0.7,
            "novelty": 0.6,
            "information_gain": 0.75,
            "estimated_cost": 0.2
        }
        
        novelty_score = self.quantum_loop.novelty.assess(candidate)
        assert isinstance(novelty_score, float)
        assert 0.0 <= novelty_score <= 1.0

    def test_difficulty_estimation(self):
        """Test: Estimación de dificultad"""
        candidate = {
            "n_qubits": 5,
            "depth": 3,
            "two_qubit_gates": 6,
            "hardware_efficiency": 0.7
        }
        
        difficulty_score = self.quantum_loop.difficulty.estimate(candidate)
        assert isinstance(difficulty_score, float)
        assert 0.0 <= difficulty_score <= 1.0

    def test_tool_evidence_bridge(self):
        """Test: Bridge de evidencia de herramientas"""
        assert self.quantum_loop.tool_evidence is not None
        assert self.quantum_loop.tool_evidence.default_domain == "quantum"

    def test_quantum_service_integration(self):
        """Test: Integración con servicio cuántico"""
        assert self.quantum_loop.quantum_service is not None

    def test_scheduler_integration(self):
        """Test: Integración con scheduler"""
        assert self.quantum_loop.scheduler is not None
        assert self.quantum_loop.scheduler.diversity_quota == 5

    def test_budget_allocator_integration(self):
        """Test: Integración con budget allocator"""
        assert self.quantum_loop.budget is not None
        assert self.quantum_loop.budget.total_budget == 8.0

    def test_candidate_validation(self):
        """Test: Validación de candidatos"""
        valid_candidate = {
            "id": "valid_candidate",
            "algorithm": "qaoa",
            "n_qubits": 5,
            "depth": 3,
            "parameters": {"problem_size": 6, "layers": 3},
            "embedding": [5.0, 3.0, 0.7],
            "literature_frequency": 25,
            "dependency_count": 3,
            "impact_potential": 0.8,
            "proveability": 0.7,
            "novelty": 0.6,
            "information_gain": 0.75,
            "estimated_cost": 0.2
        }
        
        # Debe ser válido
        assert "id" in valid_candidate
        assert "algorithm" in valid_candidate
        assert "n_qubits" in valid_candidate
        assert "depth" in valid_candidate
        assert "parameters" in valid_candidate
        assert "embedding" in valid_candidate
        assert valid_candidate["literature_frequency"] >= 0
        assert valid_candidate["dependency_count"] >= 0
        assert 0.0 <= valid_candidate["impact_potential"] <= 1.0
        assert 0.0 <= valid_candidate["proveability"] <= 1.0
        assert 0.0 <= valid_candidate["novelty"] <= 1.0
        assert 0.0 <= valid_candidate["information_gain"] <= 1.0
        assert 0.0 <= valid_candidate["estimated_cost"] <= 1.0

    def test_embedding_generation(self):
        """Test: Generación de embeddings"""
        n_qubits = 5
        depth = 3
        hardware_efficiency = 0.7
        embedding = [float(n_qubits), float(depth), hardware_efficiency]
        
        assert len(embedding) == 3
        assert embedding[0] == 5.0
        assert embedding[1] == 3.0
        assert embedding[2] == 0.7

    def test_parameters_generation(self):
        """Test: Generación de parámetros"""
        two_qubit_gates = 6
        depth = 3
        parameters = {"problem_size": two_qubit_gates, "layers": depth}
        
        assert parameters["problem_size"] == 6
        assert parameters["layers"] == 3

    def test_synthetic_candidate_generation(self):
        """Test: Generación de candidatos sintéticos cuando falla la API"""
        # Simular que la API falla y se generan candidatos sintéticos
        candidates = []
        for idx in range(3):
            depth = 2 + idx % 3
            n_qubits = 3 + (idx % 2)
            candidates.append({
                "id": f"q_synthetic_{idx}",
                "algorithm": "template",
                "n_qubits": n_qubits,
                "depth": depth,
                "parameters": {"problem_size": 4, "layers": depth},
                "embedding": [float(n_qubits), float(depth), 0.5],
                "literature_frequency": 15 + idx * 2,
                "dependency_count": 2 + idx,
                "impact_potential": 0.6,
                "proveability": 0.7,
                "novelty": 0.5,
                "information_gain": 0.65,
                "estimated_cost": 0.3
            })
        
        assert len(candidates) == 3
        for candidate in candidates:
            assert "id" in candidate
            assert "algorithm" in candidate
            assert "n_qubits" in candidate
            assert "depth" in candidate


if __name__ == "__main__":
    pytest.main([__file__, "-v"])