"""
Tests para ChemistryLoop - Loop autónomo de química computacional
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from app.autonomous.pipelines.chemistry_loop import ChemistryLoop
from app.autonomous.core.state_manager import StateManager
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry


class TestChemistryLoop:
    """Tests para ChemistryLoop"""

    def setup_method(self):
        """Setup para cada test"""
        self.state_manager = Mock(spec=StateManager)
        self.telemetry = Mock(spec=AutonomousTelemetry)
        self.chemistry_loop = ChemistryLoop(state=self.state_manager, telemetry=self.telemetry)

    def test_initialization(self):
        """Test: Inicialización correcta del ChemistryLoop"""
        assert self.chemistry_loop.state == self.state_manager
        assert self.chemistry_loop.telemetry == self.telemetry
        assert self.chemistry_loop.iteration == 0
        assert self.chemistry_loop.chemistry_service is not None
        assert self.chemistry_loop.materials_service is not None
        assert self.chemistry_loop.tool_evidence is not None

    def test_seed_synthetic_candidates(self):
        """Test: Generación de candidatos sintéticos"""
        candidates = self.chemistry_loop._seed_synthetic_candidates(k=3)
        
        assert len(candidates) == 3
        for candidate in candidates:
            assert "id" in candidate
            assert "smiles" in candidate
            assert "composition" in candidate
            assert "source" in candidate
            assert "literature_frequency" in candidate
            assert "dependency_count" in candidate
            assert "impact_potential" in candidate
            assert "proveability" in candidate
            assert "novelty" in candidate
            assert "information_gain" in candidate
            assert "estimated_cost" in candidate
            assert "suitability_score" in candidate

    def test_synthetic_candidates_smiles_format(self):
        """Test: Formato SMILES en candidatos sintéticos"""
        candidates = self.chemistry_loop._seed_synthetic_candidates(k=5)
        
        for i, candidate in enumerate(candidates):
            expected_smiles = f"C{i}H{i*2+2}"
            assert candidate["smiles"] == expected_smiles
            assert candidate["composition"] == expected_smiles

    @pytest.mark.asyncio
    async def test_fetch_domain_candidates_async_success(self):
        """Test: Obtención exitosa de candidatos de dominio"""
        # Mock del servicio de materiales
        mock_candidate = Mock()
        mock_candidate.composition = Mock()
        mock_candidate.composition.formula = "LiCoO2"
        mock_candidate.suitability_score = 0.8
        mock_candidate.properties = Mock()
        mock_candidate.properties.band_gap = 1.5
        mock_candidate.properties.stability_score = 0.9
        mock_candidate.properties.electrical_conductivity = 5.0
        
        with patch.object(self.chemistry_loop.materials_service, 'discover_materials_for_application', 
                         return_value=[mock_candidate]):
            candidates = await self.chemistry_loop._fetch_domain_candidates_async(k=1, application="battery_cathode")
            
            assert len(candidates) == 1
            candidate = candidates[0]
            assert "id" in candidate
            assert "composition" in candidate
            assert "impact_potential" in candidate

    @pytest.mark.asyncio
    async def test_fetch_domain_candidates_async_error_handling(self):
        """Test: Manejo de errores en obtención de candidatos de dominio"""
        with patch.object(self.chemistry_loop.materials_service, 'discover_materials_for_application', 
                         side_effect=RuntimeError("Service error")):
            candidates = await self.chemistry_loop._fetch_domain_candidates_async(k=1)
            
            assert len(candidates) == 0

    def test_run_coro_sync(self):
        """Test: Ejecución síncrona de corrutinas"""
        async def test_coro():
            return "test_result"
        
        result = ChemistryLoop._run_coro_sync(test_coro())
        assert result == "test_result"

    def test_priority_scoring(self):
        """Test: Sistema de scoring de prioridades"""
        candidate = {
            "literature_frequency": 50,
            "dependency_count": 5,
            "impact_potential": 0.8,
            "proveability": 0.7,
            "novelty": 0.6,
            "information_gain": 0.75,
            "estimated_cost": 0.2,
            "suitability_score": 0.8
        }
        
        score = self.chemistry_loop.priority.score(candidate)
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
            "estimated_cost": 0.2,
            "suitability_score": 0.8
        }
        
        novelty_score = self.chemistry_loop.novelty.assess(candidate)
        assert isinstance(novelty_score, float)
        assert 0.0 <= novelty_score <= 1.0

    def test_tool_evidence_bridge(self):
        """Test: Bridge de evidencia de herramientas"""
        assert self.chemistry_loop.tool_evidence is not None
        assert self.chemistry_loop.tool_evidence.default_domain == "chemistry"

    def test_random_seed_consistency(self):
        """Test: Consistencia del seed aleatorio"""
        loop1 = ChemistryLoop()
        loop2 = ChemistryLoop()
        
        assert loop1.random.getstate() == loop2.random.getstate()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])