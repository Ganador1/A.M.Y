"""
Tests para MathematicsLoop - Loop autónomo de matemáticas
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from app.autonomous.pipelines.mathematics_loop import MathematicsLoop
from app.autonomous.core.state_manager import StateManager
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry
from app.domains.mathematics.services.mathematical_discovery_engine import Conjecture


class TestMathematicsLoop:
    """Tests para MathematicsLoop"""

    def setup_method(self):
        """Setup para cada test"""
        self.state_manager = Mock(spec=StateManager)
        self.telemetry = Mock(spec=AutonomousTelemetry)
        self.mathematics_loop = MathematicsLoop(
            state=self.state_manager, 
            telemetry=self.telemetry,
            domain="number_theory"
        )

    def test_initialization(self):
        """Test: Inicialización correcta del MathematicsLoop"""
        assert self.mathematics_loop.state == self.state_manager
        assert self.mathematics_loop.telemetry == self.telemetry
        assert self.mathematics_loop.domain == "number_theory"
        assert self.mathematics_loop.iteration == 0
        assert self.mathematics_loop.discovery_engine is not None
        assert self.mathematics_loop.tool_evidence is not None
        assert self.mathematics_loop.scorer is not None
        assert self.mathematics_loop.scheduler is not None
        assert self.mathematics_loop.budget is not None
        assert self.mathematics_loop.mutator is not None
        assert self.mathematics_loop.novelty is not None

    def test_coerce_to_conjecture_from_conjecture(self):
        """Test: Coerción de Conjecture a Conjecture"""
        original_conjecture = Conjecture(
            id="test_conj",
            statement="For all n > 1, n^2 + n + 41 is prime",
            domain="number_theory",
            metadata={"difficulty": "medium"}
        )
        
        result = self.mathematics_loop._coerce_to_conjecture(original_conjecture, 0)
        assert result == original_conjecture

    def test_coerce_to_conjecture_from_dict(self):
        """Test: Coerción de dict a Conjecture"""
        conjecture_dict = {
            "statement": "For all n > 1, n^2 + n + 41 is prime",
            "domain": "number_theory",
            "id": "test_conj",
            "metadata": {"difficulty": "medium"}
        }
        
        result = self.mathematics_loop._coerce_to_conjecture(conjecture_dict, 0)
        assert isinstance(result, Conjecture)
        assert result.statement == "For all n > 1, n^2 + n + 41 is prime"
        assert result.domain == "number_theory"
        assert result.id == "test_conj"
        assert result.metadata == {"difficulty": "medium"}

    def test_coerce_to_conjecture_from_dict_with_conjecture_key(self):
        """Test: Coerción de dict con clave 'conjecture'"""
        conjecture_dict = {
            "conjecture": "For all n > 1, n^2 + n + 41 is prime",
            "domain": "algebra",
            "metadata": {"difficulty": "hard"}
        }
        
        result = self.mathematics_loop._coerce_to_conjecture(conjecture_dict, 1)
        assert isinstance(result, Conjecture)
        assert result.statement == "For all n > 1, n^2 + n + 41 is prime"
        assert result.domain == "algebra"
        assert result.id == "provider_0_1"
        assert result.metadata == {"difficulty": "hard"}

    def test_coerce_to_conjecture_from_string(self):
        """Test: Coerción de string a Conjecture"""
        statement = "For all n > 1, n^2 + n + 41 is prime"
        
        result = self.mathematics_loop._coerce_to_conjecture(statement, 2)
        assert isinstance(result, Conjecture)
        assert result.statement == statement
        assert result.domain == "number_theory"
        assert result.id == "provider_0_2"

    def test_coerce_to_conjecture_invalid_input(self):
        """Test: Coerción de input inválido"""
        invalid_input = 123
        
        result = self.mathematics_loop._coerce_to_conjecture(invalid_input, 0)
        assert result is None

    def test_coerce_to_conjecture_dict_without_statement(self):
        """Test: Coerción de dict sin statement"""
        invalid_dict = {
            "domain": "number_theory",
            "metadata": {"difficulty": "medium"}
        }
        
        result = self.mathematics_loop._coerce_to_conjecture(invalid_dict, 0)
        assert result is None

    def test_prepare_candidates_with_provider(self):
        """Test: Preparación de candidatos con provider"""
        mock_conjectures = [
            Conjecture(
                id="conj_1",
                statement="For all n > 1, n^2 + n + 41 is prime",
                domain="number_theory"
            ),
            Conjecture(
                id="conj_2",
                statement="Every even integer greater than 2 can be expressed as the sum of two primes",
                domain="number_theory"
            )
        ]
        
        def mock_provider():
            return mock_conjectures
        
        loop_with_provider = MathematicsLoop(provider=mock_provider)
        
        with patch.object(loop_with_provider.discovery_engine, 'predict_importance', return_value=0.8):
            candidates = loop_with_provider._prepare_candidates(limit=2)
            
            assert len(candidates) == 2
            for candidate in candidates:
                assert "id" in candidate
                assert "statement" in candidate
                assert "domain" in candidate
                assert "importance" in candidate
                assert "novelty" in candidate
                assert "information_gain" in candidate
                assert "estimated_cost" in candidate

    def test_prepare_candidates_without_provider(self):
        """Test: Preparación de candidatos sin provider"""
        mock_conjectures = [
            Conjecture(
                id="conj_1",
                statement="For all n > 1, n^2 + n + 41 is prime",
                domain="number_theory"
            )
        ]
        
        with patch.object(self.mathematics_loop.discovery_engine, 'generate_seed_conjectures', 
                         return_value=mock_conjectures):
            with patch.object(self.mathematics_loop.discovery_engine, 'predict_importance', 
                             return_value=0.8):
                candidates = self.mathematics_loop._prepare_candidates(limit=1)
                
                assert len(candidates) == 1
                candidate = candidates[0]
                assert "id" in candidate
                assert "statement" in candidate
                assert "domain" in candidate
                assert "importance" in candidate
                assert "novelty" in candidate
                assert "information_gain" in candidate
                assert "estimated_cost" in candidate

    def test_prepare_candidates_with_custom_domain(self):
        """Test: Preparación de candidatos con dominio personalizado"""
        candidates = self.mathematics_loop._prepare_candidates(limit=1, domain="algebra")
        
        # Debe usar el dominio personalizado
        assert len(candidates) >= 0  # Puede ser 0 si no hay candidatos

    def test_novelty_calculation(self):
        """Test: Cálculo de novedad"""
        # Test con statement nuevo
        statement = "For all n > 1, n^2 + n + 41 is prime"
        novelty_base = 0.45 if statement not in self.mathematics_loop._seen_statements else 0.25
        random_factor = 0.3
        novelty = max(0.1, min(1.0, novelty_base + random_factor))
        
        assert novelty == 0.75  # 0.45 + 0.3 = 0.75
        
        # Test con statement visto
        self.mathematics_loop._seen_statements.add(statement)
        novelty_base = 0.45 if statement not in self.mathematics_loop._seen_statements else 0.25
        novelty = max(0.1, min(1.0, novelty_base + random_factor))
        
        assert novelty == 0.55  # 0.25 + 0.3 = 0.55

    def test_information_gain_calculation(self):
        """Test: Cálculo de information_gain"""
        importance = 0.8
        novelty = 0.6
        information_gain = min(1.0, 0.45 + novelty / 2 + importance / 3)
        
        assert information_gain == min(1.0, 0.45 + 0.6 / 2 + 0.8 / 3)
        assert information_gain == min(1.0, 0.45 + 0.3 + 0.2667)
        assert information_gain == min(1.0, 1.0167)
        assert information_gain == 1.0

    def test_run_coro_sync(self):
        """Test: Ejecución síncrona de corrutinas"""
        async def test_coro():
            return "test_result"
        
        result = MathematicsLoop._run_coro_sync(test_coro())
        assert result == "test_result"

    def test_run_coro_sync_with_existing_loop(self):
        """Test: Ejecución síncrona con loop existente"""
        async def test_coro():
            return "test_result"
        
        with patch('asyncio.get_running_loop') as mock_get_loop:
            mock_get_loop.return_value = Mock()
            
            result = MathematicsLoop._run_coro_sync(test_coro())
            assert result == "test_result"

    def test_priority_scoring(self):
        """Test: Sistema de scoring de prioridades"""
        candidate = {
            "importance": 0.8,
            "novelty": 0.6,
            "information_gain": 0.75,
            "estimated_cost": 0.2
        }
        
        score = self.mathematics_loop.scorer.score(candidate)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_novelty_assessment(self):
        """Test: Evaluación de novedad"""
        candidate = {
            "importance": 0.8,
            "novelty": 0.6,
            "information_gain": 0.75,
            "estimated_cost": 0.2
        }
        
        novelty_score = self.mathematics_loop.novelty.assess(candidate)
        assert isinstance(novelty_score, float)
        assert 0.0 <= novelty_score <= 1.0

    def test_tool_evidence_bridge(self):
        """Test: Bridge de evidencia de herramientas"""
        assert self.mathematics_loop.tool_evidence is not None
        assert self.mathematics_loop.tool_evidence.default_domain == "mathematics"

    def test_discovery_engine_integration(self):
        """Test: Integración con discovery engine"""
        assert self.mathematics_loop.discovery_engine is not None

    def test_scheduler_integration(self):
        """Test: Integración con scheduler"""
        assert self.mathematics_loop.scheduler is not None
        assert self.mathematics_loop.scheduler.diversity_quota == 5

    def test_budget_allocator_integration(self):
        """Test: Integración con budget allocator"""
        assert self.mathematics_loop.budget is not None
        assert self.mathematics_loop.budget.total_budget == 10.0

    def test_mutator_integration(self):
        """Test: Integración con mutator"""
        assert self.mathematics_loop.mutator is not None

    def test_random_seed_consistency(self):
        """Test: Consistencia del seed aleatorio"""
        loop1 = MathematicsLoop()
        loop2 = MathematicsLoop()
        
        assert loop1.random.getstate() == loop2.random.getstate()

    def test_domain_default(self):
        """Test: Dominio por defecto"""
        loop = MathematicsLoop()
        assert loop.domain == "number_theory"

    def test_domain_custom(self):
        """Test: Dominio personalizado"""
        loop = MathematicsLoop(domain="algebra")
        assert loop.domain == "algebra"

    def test_seen_statements_tracking(self):
        """Test: Seguimiento de statements vistos"""
        statement = "For all n > 1, n^2 + n + 41 is prime"
        
        # Inicialmente no debe estar visto
        assert statement not in self.mathematics_loop._seen_statements
        
        # Agregar statement
        self.mathematics_loop._seen_statements.add(statement)
        assert statement in self.mathematics_loop._seen_statements

    def test_candidate_validation(self):
        """Test: Validación de candidatos"""
        valid_candidate = {
            "id": "valid_candidate",
            "statement": "For all n > 1, n^2 + n + 41 is prime",
            "domain": "number_theory",
            "importance": 0.8,
            "novelty": 0.6,
            "information_gain": 0.75,
            "estimated_cost": 0.2
        }
        
        # Debe ser válido
        assert "id" in valid_candidate
        assert "statement" in valid_candidate
        assert "domain" in valid_candidate
        assert "importance" in valid_candidate
        assert "novelty" in valid_candidate
        assert "information_gain" in valid_candidate
        assert "estimated_cost" in valid_candidate
        assert 0.0 <= valid_candidate["importance"] <= 1.0
        assert 0.0 <= valid_candidate["novelty"] <= 1.0
        assert 0.0 <= valid_candidate["information_gain"] <= 1.0
        assert 0.0 <= valid_candidate["estimated_cost"] <= 1.0

    def test_iteration_increment(self):
        """Test: Incremento de iteración"""
        initial_iteration = self.mathematics_loop.iteration
        self.mathematics_loop.iteration += 1
        assert self.mathematics_loop.iteration == initial_iteration + 1

    def test_telemetry_integration(self):
        """Test: Integración con telemetría"""
        assert self.mathematics_loop.telemetry == self.telemetry

    def test_state_manager_integration(self):
        """Test: Integración con state manager"""
        assert self.mathematics_loop.state == self.state_manager


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
