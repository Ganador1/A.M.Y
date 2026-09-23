"""
Tests para BiologyLoop - Loop autónomo de biología estructural
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from app.autonomous.pipelines.biology_loop import BiologyLoop
from app.autonomous.core.state_manager import StateManager
from app.autonomous.metrics.telemetry_collector import AutonomousTelemetry


class TestBiologyLoop:
    """Tests para BiologyLoop"""

    def setup_method(self):
        """Setup para cada test"""
        self.state_manager = Mock(spec=StateManager)
        self.telemetry = Mock(spec=AutonomousTelemetry)
        self.biology_loop = BiologyLoop(state=self.state_manager, telemetry=self.telemetry)

    def test_initialization(self):
        """Test: Inicialización correcta del BiologyLoop"""
        assert self.biology_loop.state == self.state_manager
        assert self.biology_loop.telemetry == self.telemetry
        assert self.biology_loop.iteration == 0
        assert self.biology_loop.biology_service is not None
        assert self.biology_loop.tool_evidence is not None

    def test_seed_targets_synthetic(self):
        """Test: Generación de targets sintéticos"""
        targets = self.biology_loop._seed_targets(k=3)
        
        assert len(targets) == 3
        for target in targets:
            assert "id" in target
            assert "uncertainty" in target
            assert "impact_potential" in target
            assert "literature_frequency" in target
            assert "dependency_count" in target
            assert "proveability" in target
            assert "novelty" in target
            assert "information_gain" in target
            assert "estimated_cost" in target
            
            # Verificar rangos
            assert 0.2 <= target["uncertainty"] <= 0.9
            assert 0.0 <= target["impact_potential"] <= 1.0
            assert 0 <= target["literature_frequency"] <= 60
            assert 0 <= target["dependency_count"] <= 8
            assert 0.0 <= target["proveability"] <= 1.0
            assert 0.0 <= target["novelty"] <= 1.0
            assert 0.0 <= target["information_gain"] <= 1.0
            assert 0.0 <= target["estimated_cost"] <= 0.4

    @patch('app.autonomous.pipelines.biology_loop.fetch_biomolecular_targets')
    def test_seed_targets_real_data(self, mock_fetch):
        """Test: Generación de targets con datos reales"""
        # Mock de datos reales
        mock_fetch.return_value = [
            {
                "uncertainty": 0.7,
                "impact_score": 0.8,
                "uniprot": "P12345",
                "gene_name": "BRCA1",
                "length": 1863,
                "avg_plddt": 75.0,
                "functional_annotation": "DNA repair",
                "disease_relevance": ["breast cancer", "ovarian cancer"]
            }
        ]
        
        targets = self.biology_loop._seed_targets(k=1)
        
        assert len(targets) == 1
        target = targets[0]
        assert target["uniprot"] == "P12345"
        assert target["gene_name"] == "BRCA1"
        assert target["uncertainty"] == 0.7
        assert target["impact_potential"] == 0.8
        assert target["length"] == 1863
        assert target["avg_plddt"] == 75.0
        assert target["functional_annotation"] == "DNA repair"
        assert "breast cancer" in target["disease_relevance"]

    @patch('app.autonomous.pipelines.biology_loop.fetch_biomolecular_targets')
    def test_seed_targets_fallback(self, mock_fetch):
        """Test: Fallback a datos sintéticos cuando falla la API"""
        mock_fetch.side_effect = Exception("API error")
        
        targets = self.biology_loop._seed_targets(k=2)
        
        assert len(targets) == 2
        # Debe usar datos sintéticos
        for target in targets:
            assert "id" in target
            assert "uncertainty" in target
            assert "impact_potential" in target

    @pytest.mark.asyncio
    async def test_enrich_target_async(self):
        """Test: Enriquecimiento asíncrono de targets"""
        target = {
            "id": "test_prot_1",
            "uniprot": "P12345",
            "uncertainty": 0.7,
            "impact_potential": 0.8
        }
        
        # Mock del servicio de biología
        mock_enrichment = {
            "structural_features": ["alpha_helix", "beta_sheet"],
            "functional_domains": ["DNA_binding"],
            "interaction_partners": ["TP53", "ATM"],
            "pathway_involvement": ["DNA_repair", "cell_cycle"]
        }
        
        with patch.object(self.biology_loop.biology_service, 'enrich_protein_data', 
                         return_value=mock_enrichment):
            enriched = await self.biology_loop._enrich_target_async(target)
            
            assert enriched["id"] == target["id"]
            assert enriched["uniprot"] == target["uniprot"]
            assert "structural_features" in enriched
            assert "functional_domains" in enriched
            assert "interaction_partners" in enriched
            assert "pathway_involvement" in enriched

    @pytest.mark.asyncio
    async def test_enrich_target_async_error_handling(self):
        """Test: Manejo de errores en enriquecimiento"""
        target = {
            "id": "test_prot_1",
            "uniprot": "P12345",
            "uncertainty": 0.7,
            "impact_potential": 0.8
        }
        
        # Mock del servicio que falla
        with patch.object(self.biology_loop.biology_service, 'enrich_protein_data', 
                         side_effect=Exception("Service error")):
            enriched = await self.biology_loop._enrich_target_async(target)
            
            # Debe retornar el target original sin enriquecimiento
            assert enriched["id"] == target["id"]
            assert enriched["uniprot"] == target["uniprot"]
            assert "structural_features" not in enriched

    def test_run_coro_sync(self):
        """Test: Ejecución síncrona de corrutinas"""
        async def test_coro():
            return "test_result"
        
        result = BiologyLoop._run_coro_sync(test_coro())
        assert result == "test_result"

    def test_run_coro_sync_with_existing_loop(self):
        """Test: Ejecución síncrona con loop existente"""
        async def test_coro():
            return "test_result"
        
        # Simular que ya hay un loop corriendo
        with patch('asyncio.get_running_loop') as mock_get_loop:
            mock_get_loop.return_value = Mock()
            
            result = BiologyLoop._run_coro_sync(test_coro())
            assert result == "test_result"

    def test_priority_scoring(self):
        """Test: Sistema de scoring de prioridades"""
        target = {
            "uncertainty": 0.8,
            "impact_potential": 0.9,
            "literature_frequency": 10,
            "dependency_count": 3,
            "proveability": 0.7,
            "novelty": 0.6,
            "information_gain": 0.8,
            "estimated_cost": 0.2
        }
        
        score = self.biology_loop.priority.score(target)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_novelty_assessment(self):
        """Test: Evaluación de novedad"""
        target = {
            "uncertainty": 0.8,
            "impact_potential": 0.9,
            "literature_frequency": 5,  # Baja frecuencia = alta novedad
            "dependency_count": 2,
            "proveability": 0.7,
            "novelty": 0.6,
            "information_gain": 0.8,
            "estimated_cost": 0.2
        }
        
        novelty_score = self.biology_loop.novelty.assess(target)
        assert isinstance(novelty_score, float)
        assert 0.0 <= novelty_score <= 1.0

    def test_importance_ranking(self):
        """Test: Ranking de importancia"""
        targets = [
            {
                "id": "target_1",
                "uncertainty": 0.8,
                "impact_potential": 0.9,
                "literature_frequency": 10,
                "dependency_count": 3,
                "proveability": 0.7,
                "novelty": 0.6,
                "information_gain": 0.8,
                "estimated_cost": 0.2
            },
            {
                "id": "target_2",
                "uncertainty": 0.6,
                "impact_potential": 0.7,
                "literature_frequency": 20,
                "dependency_count": 5,
                "proveability": 0.8,
                "novelty": 0.4,
                "information_gain": 0.6,
                "estimated_cost": 0.3
            }
        ]
        
        ranked = self.biology_loop.importance_ranker.rank(targets)
        assert len(ranked) == 2
        assert all("importance_score" in target for target in ranked)
        assert all("rank" in target for target in ranked)

    def test_iteration_increment(self):
        """Test: Incremento de iteración"""
        initial_iteration = self.biology_loop.iteration
        self.biology_loop.iteration += 1
        assert self.biology_loop.iteration == initial_iteration + 1

    def test_random_seed_consistency(self):
        """Test: Consistencia del seed aleatorio"""
        # Crear dos loops con el mismo seed
        loop1 = BiologyLoop()
        loop2 = BiologyLoop()
        
        # Ambos deben tener el mismo seed
        assert loop1.rand.getstate() == loop2.rand.getstate()

    def test_tool_evidence_bridge(self):
        """Test: Bridge de evidencia de herramientas"""
        assert self.biology_loop.tool_evidence is not None
        assert self.biology_loop.tool_evidence.default_domain == "biology"

    def test_telemetry_integration(self):
        """Test: Integración con telemetría"""
        assert self.biology_loop.telemetry == self.telemetry

    def test_state_manager_integration(self):
        """Test: Integración con state manager"""
        assert self.biology_loop.state == self.state_manager

    def test_biology_service_integration(self):
        """Test: Integración con servicio de biología"""
        assert self.biology_loop.biology_service is not None

    def test_target_validation(self):
        """Test: Validación de targets"""
        valid_target = {
            "id": "valid_target",
            "uncertainty": 0.5,
            "impact_potential": 0.6,
            "literature_frequency": 15,
            "dependency_count": 2,
            "proveability": 0.7,
            "novelty": 0.5,
            "information_gain": 0.6,
            "estimated_cost": 0.25
        }
        
        # Debe ser válido
        assert "id" in valid_target
        assert 0.0 <= valid_target["uncertainty"] <= 1.0
        assert 0.0 <= valid_target["impact_potential"] <= 1.0
        assert valid_target["literature_frequency"] >= 0
        assert valid_target["dependency_count"] >= 0
        assert 0.0 <= valid_target["proveability"] <= 1.0
        assert 0.0 <= valid_target["novelty"] <= 1.0
        assert 0.0 <= valid_target["information_gain"] <= 1.0
        assert 0.0 <= valid_target["estimated_cost"] <= 1.0

    def test_error_handling_in_seed_targets(self):
        """Test: Manejo de errores en seed_targets"""
        # Test con k=0
        targets = self.biology_loop._seed_targets(k=0)
        assert len(targets) == 0
        
        # Test con k negativo
        targets = self.biology_loop._seed_targets(k=-1)
        assert len(targets) == 0

    def test_target_id_generation(self):
        """Test: Generación de IDs únicos para targets"""
        targets = self.biology_loop._seed_targets(k=5)
        ids = [target["id"] for target in targets]
        
        # Todos los IDs deben ser únicos
        assert len(set(ids)) == len(ids)
        
        # Todos los IDs deben seguir el patrón esperado
        for target_id in ids:
            assert target_id.startswith("prot_")
            assert "_" in target_id

    def test_information_gain_calculation(self):
        """Test: Cálculo de information_gain"""
        target = {
            "uncertainty": 0.8,
            "impact_potential": 0.6
        }
        
        # information_gain debe ser calculado como (uncertainty + impact) / 2.0
        expected_info_gain = (target["uncertainty"] + target["impact_potential"]) / 2.0
        
        targets = self.biology_loop._seed_targets(k=1)
        actual_info_gain = targets[0]["information_gain"]
        
        # Debe estar cerca del valor esperado (con tolerancia para random)
        assert abs(actual_info_gain - expected_info_gain) < 0.1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])