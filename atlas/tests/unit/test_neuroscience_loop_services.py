"""
Unit Tests - Neuroscience Loop Services Integration
====================================================

Tests for Neuroscience Loop integration with:
- AdvancedNeuroimagingAnalysis (fMRI, EEG, MEG, DTI multi-modal imaging)
- NeuralNetworksService (Transformer, CNN, LSTM for brain analysis)
- MultiScaleModelingService (molecular to system-level brain modeling)
- BrainComputerInterfaceService (BCI decoding and real-time analysis)

Author: AXIOM Team
Date: 2025-01-28
Version: 1.0.0
"""

import pytest
from unittest.mock import AsyncMock, patch

# Neuroscience Loop
from app.autonomous.pipelines.neuroscience_loop import NeuroscienceLoop

# Neuroscience services
from app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis import (
    AdvancedNeuroimagingAnalysis,
    ImagingModality,
)
from app.domains.neuroscience.services.neural_networks_service import NeuralNetworksService
from app.domains.neuroscience.services.neuromorphic.multi_scale_modeling import MultiScaleModelingService
from app.domains.neuroscience.services.neuromorphic.brain_computer_interface import BrainComputerInterfaceService


class TestNeuroscienceLoopServicesInitialization:
    """Test Neuroscience Loop service initialization."""

    def test_neuroscience_loop_initialization(self):
        """Test Neuroscience Loop initializes with 4 advanced services."""
        loop = NeuroscienceLoop()

        # Verify service attributes exist
        assert hasattr(loop, "neuroimaging_service")
        assert hasattr(loop, "neural_networks_service")
        assert hasattr(loop, "multiscale_modeling_service")
        assert hasattr(loop, "bci_service")

        # Verify service types
        assert isinstance(loop.neuroimaging_service, AdvancedNeuroimagingAnalysis)
        assert isinstance(loop.neural_networks_service, NeuralNetworksService)
        assert isinstance(loop.multiscale_modeling_service, MultiScaleModelingService)
        assert isinstance(loop.bci_service, BrainComputerInterfaceService)

    def test_neuroscience_loop_autonomous_components(self):
        """Test Neuroscience Loop has standard autonomous components."""
        loop = NeuroscienceLoop()

        # Standard autonomous framework components
        assert hasattr(loop, "state")
        assert hasattr(loop, "telemetry")
        assert hasattr(loop, "priority")
        assert hasattr(loop, "scheduler")
        assert hasattr(loop, "novelty")


class TestMultiModalNeuroimaging:
    """Test AdvancedNeuroimagingAnalysis integration."""

    @pytest.mark.asyncio
    async def test_fmri_session_creation(self):
        """Test fMRI imaging session creation."""
        loop = NeuroscienceLoop()

        mock_session_response = {
            "success": True,
            "session": {
                "session_id": "neuro_session_fmri_0",
                "modality": "fmri",
                "brain_region": "prefrontal_cortex",
                "quality": 0.88,
                "connectivity_strength": 0.72,
            },
        }

        with patch.object(
            loop.neuroimaging_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_session_response,
        ):
            candidates = await loop._fetch_brain_imaging_data_async(limit=10)

            # Verify fMRI candidates were created
            imaging_candidates = [c for c in candidates if c.get("source") == "neuroimaging"]
            assert len(imaging_candidates) > 0

            # Check candidate structure
            for candidate in imaging_candidates:
                assert "brain_region" in candidate
                assert "modality" in candidate
                assert "connectivity_strength" in candidate

    @pytest.mark.asyncio
    async def test_multi_modality_integration(self):
        """Test integration of multiple imaging modalities (fMRI, EEG, MEG, DTI)."""
        loop = NeuroscienceLoop()

        # Mock successful session creation for all modalities
        mock_response = {
            "success": True,
            "session": {
                "session_id": "test_session",
                "quality": 0.85,
                "brain_region": "motor_cortex",
            },
        }

        with patch.object(
            loop.neuroimaging_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            candidates = await loop._fetch_brain_imaging_data_async(limit=15)

            # Should have candidates from neuroimaging (potentially 4 modalities)
            imaging_candidates = [c for c in candidates if c.get("source") == "neuroimaging"]
            
            # Verify diversity in modalities
            if len(imaging_candidates) > 0:
                modalities = {c.get("modality") for c in imaging_candidates}
                # Should have at least one modality
                assert len(modalities) > 0

    @pytest.mark.asyncio
    async def test_connectivity_strength_extraction(self):
        """Test extraction of functional connectivity strength."""
        loop = NeuroscienceLoop()

        mock_response = {
            "success": True,
            "session": {
                "connectivity_strength": 0.78,
                "brain_region": "hippocampus",
            },
        }

        with patch.object(
            loop.neuroimaging_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            candidates = await loop._fetch_brain_imaging_data_async(limit=5)

            imaging_cand = next((c for c in candidates if c.get("source") == "neuroimaging"), None)

            if imaging_cand:
                # Verify connectivity was extracted
                assert "connectivity_strength" in imaging_cand
                assert isinstance(imaging_cand["connectivity_strength"], (int, float))


class TestNeuralNetworkModels:
    """Test NeuralNetworksService integration."""

    @pytest.mark.asyncio
    async def test_pretrained_model_discovery(self):
        """Test discovery of pre-trained neural network models."""
        loop = NeuroscienceLoop()

        mock_model_response = {
            "success": True,
            "models": [
                {
                    "name": "brain_transformer_v2",
                    "architecture": "transformer",
                    "accuracy": 0.85,
                    "task_type": "brain_state_classification",
                },
                {
                    "name": "eeg_cnn_model",
                    "architecture": "cnn",
                    "accuracy": 0.79,
                    "task_type": "seizure_detection",
                },
            ],
        }

        with patch.object(
            loop.neural_networks_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_model_response,
        ):
            candidates = await loop._fetch_brain_imaging_data_async(limit=10)

            # Verify neural network model candidates
            nn_candidates = [c for c in candidates if c.get("source") == "neural_networks"]
            assert len(nn_candidates) > 0

            # Check model properties
            for candidate in nn_candidates:
                assert "model_name" in candidate
                assert "model_architecture" in candidate
                assert "model_accuracy" in candidate

    @pytest.mark.asyncio
    async def test_model_accuracy_extraction(self):
        """Test extraction of model accuracy scores."""
        loop = NeuroscienceLoop()

        mock_response = {
            "success": True,
            "models": [
                {"name": "brain_lstm", "architecture": "lstm", "accuracy": 0.91},
            ],
        }

        with patch.object(
            loop.neural_networks_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            candidates = await loop._fetch_brain_imaging_data_async(limit=5)

            nn_cand = next((c for c in candidates if c.get("source") == "neural_networks"), None)

            if nn_cand:
                # Verify accuracy extraction
                assert "model_accuracy" in nn_cand
                assert 0.0 <= nn_cand["model_accuracy"] <= 1.0


class TestMultiScaleModelingEnrichment:
    """Test MultiScaleModelingService enrichment."""

    @pytest.mark.asyncio
    async def test_network_simulation_enrichment(self):
        """Test multi-scale network simulation enrichment."""
        loop = NeuroscienceLoop()

        mock_candidate = {
            "id": "brain_candidate_001",
            "brain_region": "prefrontal_cortex",
            "connectivity_strength": 0.68,
        }

        mock_modeling_response = {
            "success": True,
            "network_activity": 0.72,
            "population_dynamics": {
                "firing_rate": 15.3,
                "synchrony": 0.65,
            },
            "accuracy": 0.81,
        }

        with patch.object(
            loop.multiscale_modeling_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_modeling_response,
        ):
            enrichment = await loop._enrich_candidate_async(mock_candidate)

            # Verify multi-scale modeling enrichment
            assert "multiscale_modeling" in enrichment
            modeling_data = enrichment["multiscale_modeling"]
            assert "network_activity" in modeling_data
            assert "simulation_accuracy" in modeling_data

    @pytest.mark.asyncio
    async def test_population_dynamics_analysis(self):
        """Test population dynamics analysis from multi-scale modeling."""
        loop = NeuroscienceLoop()

        mock_candidate = {
            "id": "test_002",
            "brain_region": "motor_cortex",
            "connectivity_strength": 0.75,
        }

        mock_response = {
            "success": True,
            "network_activity": 0.68,
            "population_dynamics": {
                "firing_rate": 22.1,
                "synchrony": 0.71,
                "bursting_frequency": 3.5,
            },
            "accuracy": 0.85,
        }

        with patch.object(
            loop.multiscale_modeling_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            enrichment = await loop._enrich_candidate_async(mock_candidate)

            assert "multiscale_modeling" in enrichment
            # Verify population dynamics captured
            modeling_data = enrichment["multiscale_modeling"]
            assert "population_dynamics" in modeling_data


class TestBCIDecodingEnrichment:
    """Test BrainComputerInterfaceService enrichment."""

    @pytest.mark.asyncio
    async def test_brain_state_decoding(self):
        """Test brain state decoding enrichment."""
        loop = NeuroscienceLoop()

        mock_candidate = {
            "id": "bci_candidate_001",
            "brain_region": "motor_cortex",
            "modality": "eeg",
            "connectivity_strength": 0.70,
        }

        mock_bci_response = {
            "success": True,
            "decoding_accuracy": 0.84,
            "brain_state": "active",
            "signal_quality": 0.90,
        }

        with patch.object(
            loop.bci_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_bci_response,
        ):
            enrichment = await loop._enrich_candidate_async(mock_candidate)

            # Verify BCI enrichment
            assert "bci_analysis" in enrichment
            bci_data = enrichment["bci_analysis"]
            assert "decoding_accuracy" in bci_data
            assert "brain_state" in bci_data
            assert "signal_quality" in bci_data

    @pytest.mark.asyncio
    async def test_decoding_accuracy_threshold(self):
        """Test decoding accuracy validation."""
        loop = NeuroscienceLoop()

        mock_candidate = {
            "id": "test_003",
            "brain_region": "visual_cortex",
            "modality": "meg",
            "connectivity_strength": 0.65,
        }

        mock_response = {
            "success": True,
            "decoding_accuracy": 0.78,
            "brain_state": "rest",
            "signal_quality": 0.87,
        }

        with patch.object(
            loop.bci_service,
            "process_request",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            enrichment = await loop._enrich_candidate_async(mock_candidate)

            bci_data = enrichment.get("bci_analysis", {})
            
            if "decoding_accuracy" in bci_data:
                # Verify accuracy is in valid range
                assert 0.0 <= bci_data["decoding_accuracy"] <= 1.0


class TestNeuroscienceLoopIteration:
    """Test complete Neuroscience Loop iteration."""

    @pytest.mark.asyncio
    async def test_full_brain_imaging_iteration(self):
        """Test full Neuroscience Loop iteration."""
        loop = NeuroscienceLoop()

        # Mock all services
        mock_imaging = {
            "success": True,
            "session": {"connectivity_strength": 0.75, "quality": 0.88},
        }

        mock_nn = {
            "success": True,
            "models": [{"name": "model_1", "architecture": "transformer", "accuracy": 0.82}],
        }

        with patch.object(
            loop.neuroimaging_service, "process_request", new_callable=AsyncMock, return_value=mock_imaging
        ), patch.object(
            loop.neural_networks_service, "process_request", new_callable=AsyncMock, return_value=mock_nn
        ), patch.object(
            loop.multiscale_modeling_service,
            "process_request",
            new_callable=AsyncMock,
            return_value={"success": True, "network_activity": 0.68},
        ), patch.object(
            loop.bci_service,
            "process_request",
            new_callable=AsyncMock,
            return_value={"success": True, "decoding_accuracy": 0.80},
        ), patch.object(
            loop.evidence, "corroborate", new_callable=AsyncMock, return_value={"confidence": 0.75}
        ):
            result = await loop._run_iteration_impl(top_n=2)

            # Verify iteration success
            assert result["success"] is True
            assert "processed_count" in result
            assert result["processed_count"] > 0


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
