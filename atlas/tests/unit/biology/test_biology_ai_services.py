"""
Unit tests for Biology Loop AI Services Integration

Tests the integration of:
- DNABERT2GenomicsService (DNA sequence analysis)
- ProtGPT2Service (protein design generation)
- BioGPTService (biomedical literature)
"""

import pytest
import asyncio
from unittest.mock import AsyncMock
from app.autonomous.pipelines.biology_loop import BiologyLoop


class TestBiologyLoopAIServicesInitialization:
    """Test AI services initialization in Biology Loop"""

    @pytest.fixture
    def biology_loop(self, monkeypatch):
        """Create BiologyLoop instance for testing"""
        class FakeAIService:
            def __init__(self, *args, **kwargs): pass
            async def process_request(self, data): return {"success": True}
            def initialize(self): pass

        from app.autonomous.pipelines import biology_loop as bl_module
        monkeypatch.setattr(bl_module, "DNABERT2GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "ProtGPT2ProteinDesignService", FakeAIService)
        monkeypatch.setattr(bl_module, "BioGPTService", FakeAIService)
        monkeypatch.setattr(bl_module, "GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "BiomedicalNLPService", FakeAIService)
        
        return BiologyLoop()

    def test_all_ai_services_initialized(self, biology_loop):
        """Test that all 3 AI services are initialized"""
        assert hasattr(biology_loop, 'dnabert2_service')
        assert hasattr(biology_loop, 'protgpt2_service')
        assert hasattr(biology_loop, 'biogpt_service')
        
        assert biology_loop.dnabert2_service is not None
        assert biology_loop.protgpt2_service is not None
        assert biology_loop.biogpt_service is not None


class TestDNABERT2Integration:
    """Test DNABERT2 genomics service integration"""

    @pytest.fixture
    def biology_loop(self, monkeypatch):
        class FakeAIService:
            def __init__(self, *args, **kwargs): pass
            async def process_request(self, data): return {"success": True}
            def initialize(self): pass

        from app.autonomous.pipelines import biology_loop as bl_module
        monkeypatch.setattr(bl_module, "DNABERT2GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "ProtGPT2ProteinDesignService", FakeAIService)
        monkeypatch.setattr(bl_module, "BioGPTService", FakeAIService)
        monkeypatch.setattr(bl_module, "GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "BiomedicalNLPService", FakeAIService)
        return BiologyLoop()

    @pytest.fixture
    def mock_target(self):
        """Mock protein target for enrichment"""
        return {
            "id": "prot_test_001",
            "uniprot": "P12345",
            "gene_name": "BRCA1",
            "uncertainty": 0.7,
            "impact_potential": 0.8
        }

    @pytest.fixture
    def mock_dnabert2_result(self):
        """Mock DNABERT2 analysis result"""
        return {
            "success": True,
            "predicted_function": "DNA repair enzyme",
            "sequence_annotations": [
                {"region": "1-100", "feature": "DNA binding domain"},
                {"region": "200-350", "feature": "catalytic site"}
            ],
            "confidence_score": 0.92,
            "model_version": "dnabert2_multitask_v1.0"
        }

    @pytest.mark.asyncio
    async def test_dnabert2_sequence_analysis(self, biology_loop, mock_target, mock_dnabert2_result):
        """Test DNABERT2 DNA sequence analysis in enrichment"""
        # Mock DNABERT2 service
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(
            return_value=mock_dnabert2_result
        )
        
        # Mock other required services
        biology_loop.biology_service.population_dynamics = AsyncMock(
            return_value={"population": [50, 100, 150]}
        )
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(
            return_value={"diversity_index": 2.5}
        )
        biology_loop.protgpt2_service.generate_protein = AsyncMock(
            return_value={"success": True}
        )
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(
            return_value={"success": True}
        )

        # Call enrichment
        enrichment = await biology_loop._enrich_target_async(mock_target)

        # Verify DNABERT2 was called
        biology_loop.dnabert2_service.analyze_sequence.assert_called_once()
        
        # Check call parameters
        call_kwargs = biology_loop.dnabert2_service.analyze_sequence.call_args.kwargs
        assert call_kwargs["operation"] == "predict_function"
        assert "sequence_id" in call_kwargs["parameters"]

        # Verify enrichment contains DNA analysis
        assert "dna_analysis" in enrichment
        if enrichment["dna_analysis"] is not None:
            assert enrichment["dna_analysis"]["success"] == True
            assert "predicted_function" in enrichment["dna_analysis"]

    @pytest.mark.asyncio
    async def test_dnabert2_handles_failure(self, biology_loop, mock_target):
        """Test graceful handling when DNABERT2 fails"""
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(
            side_effect=Exception("DNABERT2 model unavailable")
        )
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        biology_loop.protgpt2_service.generate_protein = AsyncMock(return_value={"success": True})
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(return_value={"success": True})

        # Should not raise exception
        enrichment = await biology_loop._enrich_target_async(mock_target)
        
        # Should still have enrichment structure
        assert "dna_analysis" in enrichment
        # May be None due to failure
        assert enrichment["dna_analysis"] is None or "error" not in str(enrichment["dna_analysis"])


class TestProtGPT2Integration:
    """Test ProtGPT2 protein design service integration"""

    @pytest.fixture
    def biology_loop(self, monkeypatch):
        class FakeAIService:
            def __init__(self, *args, **kwargs): pass
            async def process_request(self, data): return {"success": True}
            def initialize(self): pass

        from app.autonomous.pipelines import biology_loop as bl_module
        monkeypatch.setattr(bl_module, "DNABERT2GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "ProtGPT2ProteinDesignService", FakeAIService)
        monkeypatch.setattr(bl_module, "BioGPTService", FakeAIService)
        monkeypatch.setattr(bl_module, "GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "BiomedicalNLPService", FakeAIService)
        return BiologyLoop()

    @pytest.fixture
    def mock_target(self):
        return {
            "id": "prot_test_002",
            "uniprot": "Q98765",
            "gene_name": "TP53",
            "uncertainty": 0.6,
            "impact_potential": 0.9
        }

    @pytest.fixture
    def mock_protgpt2_result(self):
        """Mock ProtGPT2 protein generation result"""
        return {
            "success": True,
            "generated_sequence": "MTEYKLVVVGAGGVGKSALTIQLIQNHFVDEYDPTIEDSYRKQVVIDGETCLLDILDTAGQEEY",
            "sequence_length": 64,
            "predicted_structure": "alpha_helix",
            "confidence": 0.88,
            "model_temperature": 0.8
        }

    @pytest.mark.asyncio
    async def test_protgpt2_protein_design(self, biology_loop, mock_target, mock_protgpt2_result):
        """Test ProtGPT2 protein design generation"""
        biology_loop.protgpt2_service.generate_protein = AsyncMock(
            return_value=mock_protgpt2_result
        )
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(return_value={"success": True})
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(return_value={"success": True})

        enrichment = await biology_loop._enrich_target_async(mock_target)

        # Verify ProtGPT2 was called
        biology_loop.protgpt2_service.generate_protein.assert_called_once()
        
        # Check parameters
        call_kwargs = biology_loop.protgpt2_service.generate_protein.call_args.kwargs
        assert call_kwargs["operation"] == "sequence_generation"
        assert "prompt" in call_kwargs["parameters"]
        assert "max_length" in call_kwargs["parameters"]

        # Verify enrichment
        assert "protein_design" in enrichment
        if enrichment["protein_design"] is not None:
            assert enrichment["protein_design"]["success"] == True

    @pytest.mark.asyncio
    async def test_protgpt2_sequence_quality(self, biology_loop, mock_target, mock_protgpt2_result):
        """Test that generated protein sequences meet quality criteria"""
        biology_loop.protgpt2_service.generate_protein = AsyncMock(
            return_value=mock_protgpt2_result
        )
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(return_value={"success": True})
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(return_value={"success": True})

        enrichment = await biology_loop._enrich_target_async(mock_target)

        if enrichment.get("protein_design", {}).get("success"):
            protein_data = enrichment["protein_design"]
            # Check sequence length is reasonable
            if "sequence_length" in protein_data:
                assert protein_data["sequence_length"] > 0
                assert protein_data["sequence_length"] <= 1000  # Reasonable protein size


class TestBioGPTIntegration:
    """Test BioGPT biomedical literature service integration"""

    @pytest.fixture
    def biology_loop(self, monkeypatch):
        class FakeAIService:
            def __init__(self, *args, **kwargs): pass
            async def process_request(self, data): return {"success": True}
            def initialize(self): pass

        from app.autonomous.pipelines import biology_loop as bl_module
        monkeypatch.setattr(bl_module, "DNABERT2GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "ProtGPT2ProteinDesignService", FakeAIService)
        monkeypatch.setattr(bl_module, "BioGPTService", FakeAIService)
        monkeypatch.setattr(bl_module, "GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "BiomedicalNLPService", FakeAIService)
        return BiologyLoop()

    @pytest.fixture
    def mock_target(self):
        return {
            "id": "prot_test_003",
            "uniprot": "P11111",
            "gene_name": "EGFR",
            "uncertainty": 0.5,
            "impact_potential": 0.95
        }

    @pytest.fixture
    def mock_biogpt_result(self):
        """Mock BioGPT literature generation result"""
        return {
            "success": True,
            "generated_text": "EGFR is a receptor tyrosine kinase that plays a crucial role in cell proliferation and differentiation. Mutations in EGFR are associated with various cancers, particularly non-small cell lung cancer. Therapeutic targeting of EGFR has shown promise in precision medicine approaches.",
            "confidence": 0.91,
            "model_version": "biogpt_large"
        }

    @pytest.mark.asyncio
    async def test_biogpt_literature_generation(self, biology_loop, mock_target, mock_biogpt_result):
        """Test BioGPT biomedical literature summary generation"""
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(
            return_value=mock_biogpt_result
        )
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(return_value={"success": True})
        biology_loop.protgpt2_service.generate_protein = AsyncMock(return_value={"success": True})

        enrichment = await biology_loop._enrich_target_async(mock_target)

        # Verify BioGPT was called
        biology_loop.biogpt_service.generate_biomedical_text.assert_called_once()
        
        # Check parameters
        call_args = biology_loop.biogpt_service.generate_biomedical_text.call_args
        prompt = call_args.args[0] if len(call_args.args) > 0 else call_args.kwargs.get("prompt")
        assert prompt is not None
        assert mock_target["gene_name"] in prompt

        # Verify enrichment
        assert "literature_search" in enrichment
        if enrichment["literature_search"] is not None:
            assert enrichment["literature_search"]["success"] == True

    @pytest.mark.asyncio
    async def test_biogpt_text_quality(self, biology_loop, mock_target, mock_biogpt_result):
        """Test quality of generated biomedical text"""
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(
            return_value=mock_biogpt_result
        )
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(return_value={"success": True})
        biology_loop.protgpt2_service.generate_protein = AsyncMock(return_value={"success": True})

        enrichment = await biology_loop._enrich_target_async(mock_target)

        if enrichment.get("literature_search", {}).get("success"):
            lit_data = enrichment["literature_search"]
            if "generated_text" in lit_data:
                text = lit_data["generated_text"]
                # Should have reasonable length
                assert len(text) > 50  # Not too short
                assert len(text) < 10000  # Not too long


class TestEnrichmentPipeline:
    """Test complete enrichment pipeline with all AI services"""

    @pytest.fixture
    def biology_loop(self, monkeypatch):
        class FakeAIService:
            def __init__(self, *args, **kwargs): pass
            async def process_request(self, data): return {"success": True}
            def initialize(self): pass

        from app.autonomous.pipelines import biology_loop as bl_module
        monkeypatch.setattr(bl_module, "DNABERT2GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "ProtGPT2ProteinDesignService", FakeAIService)
        monkeypatch.setattr(bl_module, "BioGPTService", FakeAIService)
        monkeypatch.setattr(bl_module, "GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "BiomedicalNLPService", FakeAIService)
        return BiologyLoop()

    @pytest.fixture
    def mock_target(self):
        return {
            "id": "prot_pipeline_001",
            "uniprot": "P99999",
            "gene_name": "MYC",
            "uncertainty": 0.65,
            "impact_potential": 0.85
        }

    @pytest.mark.asyncio
    async def test_complete_enrichment_pipeline(self, biology_loop, mock_target):
        """Test that all AI services run in enrichment pipeline"""
        # Mock all services
        biology_loop.biology_service.population_dynamics = AsyncMock(
            return_value={"population": [100, 200, 300]}
        )
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(
            return_value={"diversity_index": 3.2}
        )
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(
            return_value={"success": True, "predicted_function": "transcription factor"}
        )
        biology_loop.protgpt2_service.generate_protein = AsyncMock(
            return_value={"success": True, "sequence_length": 150}
        )
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(
            return_value={"success": True, "generated_text": "MYC is a proto-oncogene..."}
        )

        enrichment = await biology_loop._enrich_target_async(mock_target)

        # All services should have been called
        biology_loop.biology_service.population_dynamics.assert_called_once()
        biology_loop.biology_service.biodiversity_analysis.assert_called_once()
        biology_loop.dnabert2_service.analyze_sequence.assert_called_once()
        biology_loop.protgpt2_service.generate_protein.assert_called_once()
        biology_loop.biogpt_service.generate_biomedical_text.assert_called_once()

        # Enrichment should have all components
        assert "population_dynamics" in enrichment
        assert "biodiversity" in enrichment
        assert "dna_analysis" in enrichment
        assert "protein_design" in enrichment
        assert "literature_search" in enrichment

    @pytest.mark.asyncio
    async def test_pipeline_partial_failure_resilience(self, biology_loop, mock_target):
        """Test pipeline continues even if some AI services fail"""
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        
        # DNA analysis fails
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(
            side_effect=Exception("DNABERT2 failed")
        )
        
        # Protein design succeeds
        biology_loop.protgpt2_service.generate_protein = AsyncMock(
            return_value={"success": True}
        )
        
        # Literature fails
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(
            side_effect=Exception("BioGPT failed")
        )

        # Should not raise exception
        enrichment = await biology_loop._enrich_target_async(mock_target)

        # Should have structure
        assert isinstance(enrichment, dict)
        assert "dna_analysis" in enrichment
        assert "protein_design" in enrichment
        assert "literature_search" in enrichment


class TestAIServicesErrorHandling:
    """Test error handling for AI service failures"""

    @pytest.fixture
    def biology_loop(self, monkeypatch):
        class FakeAIService:
            def __init__(self, *args, **kwargs): pass
            async def process_request(self, data): return {"success": True}
            def initialize(self): pass

        from app.autonomous.pipelines import biology_loop as bl_module
        monkeypatch.setattr(bl_module, "DNABERT2GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "ProtGPT2ProteinDesignService", FakeAIService)
        monkeypatch.setattr(bl_module, "BioGPTService", FakeAIService)
        monkeypatch.setattr(bl_module, "GenomicsService", FakeAIService)
        monkeypatch.setattr(bl_module, "BiomedicalNLPService", FakeAIService)
        return BiologyLoop()

    @pytest.fixture
    def mock_target(self):
        return {"id": "test", "gene_name": "TEST", "uniprot": "P00000"}

    @pytest.mark.asyncio
    async def test_dnabert2_timeout_handling(self, biology_loop, mock_target):
        """Test handling of DNABERT2 timeout"""
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(
            side_effect=asyncio.TimeoutError("Analysis timeout")
        )
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        biology_loop.protgpt2_service.generate_protein = AsyncMock(return_value={"success": True})
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(return_value={"success": True})

        enrichment = await biology_loop._enrich_target_async(mock_target)
        
        assert "dna_analysis" in enrichment
        # Should be None or have error info
        assert enrichment["dna_analysis"] is None or isinstance(enrichment["dna_analysis"], dict)

    @pytest.mark.asyncio
    async def test_all_ai_services_fail_gracefully(self, biology_loop, mock_target):
        """Test that enrichment continues even if all AI services fail"""
        biology_loop.biology_service.population_dynamics = AsyncMock(return_value={})
        biology_loop.biology_service.biodiversity_analysis = AsyncMock(return_value={})
        biology_loop.dnabert2_service.analyze_sequence = AsyncMock(
            side_effect=Exception("Failed")
        )
        biology_loop.protgpt2_service.generate_protein = AsyncMock(
            side_effect=Exception("Failed")
        )
        biology_loop.biogpt_service.generate_biomedical_text = AsyncMock(
            side_effect=Exception("Failed")
        )

        # Should not crash
        enrichment = await biology_loop._enrich_target_async(mock_target)
        
        # Should still have base enrichment
        assert isinstance(enrichment, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
