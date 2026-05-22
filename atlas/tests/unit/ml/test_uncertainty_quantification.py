"""
Unit tests for Uncertainty Quantification Service

Tests the uncertainty quantification functionality for PINN solutions,
including fiducial inference, bootstrap sampling, Monte Carlo dropout,
and ensemble methods.
"""

import asyncio
import pytest
import numpy as np
from unittest.mock import Mock

from app.uncertainty_quantification import (
    UncertaintyQuantificationService,
    UncertaintyConfig,
    UncertaintyResult,
    FiducialInferenceQuantifier,
    BootstrapQuantifier,
    MonteCarloDropoutQuantifier,
    EnsembleQuantifier
)


class TestUncertaintyConfig:
    """Test UncertaintyConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = UncertaintyConfig()
        assert config.method == "fiducial"
        assert config.num_samples == 1000
        assert config.confidence_level == 0.95
        assert config.pde_type == "heat"


class TestUncertaintyQuantificationService:
    """Test UncertaintyQuantificationService class"""

    @pytest.fixture
    def service(self):
        """Create service instance"""
        return UncertaintyQuantificationService()

    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service.name == "UncertaintyQuantificationService"
        assert 'fiducial' in service.quantifiers

    @pytest.mark.asyncio
    async def test_get_available_methods(self, service):
        """Test getting available methods"""
        methods = await service.get_available_methods()
        expected_methods = ['fiducial', 'bootstrap', 'dropout', 'ensemble']
        assert set(methods) == set(expected_methods)

    @pytest.mark.asyncio
    async def test_process_request_success(self, service):
        """Test successful request processing"""
        request_data = {
            'method': 'fiducial',
            'pde_type': 'heat',
            'num_samples': 10,
            'confidence_level': 0.95,
            'num_test_points': 5
        }

        result = await service.process_request(request_data)

        assert result['status'] == 'success'
        assert result['method'] == 'fiducial'
        assert 'mean_prediction' in result
