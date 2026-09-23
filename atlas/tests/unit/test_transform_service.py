"""
Tests for Transform Service
"""

import pytest
from app.services.transform_service import TransformService


class TestTransformService:
    """Test cases for TransformService"""

    @pytest.fixture
    def service(self):
        """Create a TransformService instance"""
        return TransformService()

    def test_fourier_transform_simple(self, service):
        """Test basic Fourier transform"""
        result = service.fourier_transform("1", "t", "f")
        assert "error" not in result
        assert "fourier_transform" in result

    def test_laplace_transform_simple(self, service):
        """Test basic Laplace transform"""
        result = service.laplace_transform("1", "t", "s")
        assert "error" not in result
        assert "laplace_transform" in result

    def test_discrete_fourier_transform(self, service):
        """Test DFT with simple signal"""
        signal = [1.0, 0.0, 1.0, 0.0]
        result = service.discrete_fourier_transform(signal)
        assert "error" not in result
        assert "dft_coefficients" in result
        assert "magnitude" in result
        assert "phase" in result
        assert len(result["magnitude"]) == len(signal)

    def test_inverse_discrete_fourier_transform(self, service):
        """Test IDFT"""
        dft_coeffs = [2.0+0j, 0.0+0j, 0.0+0j, 0.0+0j]
        result = service.inverse_discrete_fourier_transform(dft_coeffs)
        assert "error" not in result
        assert "reconstructed_signal" in result
        assert len(result["reconstructed_signal"]) == len(dft_coeffs)

    def test_get_transform_pairs_fourier(self, service):
        """Test getting Fourier transform pairs"""
        result = service.get_transform_pairs("fourier")
        assert "error" not in result
        assert "pairs" in result
        assert "rectangular" in result["pairs"]

    def test_get_transform_pairs_laplace(self, service):
        """Test getting Laplace transform pairs"""
        result = service.get_transform_pairs("laplace")
        assert "error" not in result
        assert "pairs" in result
        assert "unit_step" in result["pairs"]

    def test_invalid_transform_type(self, service):
        """Test invalid transform type"""
        result = service.get_transform_pairs("invalid")
        assert "error" in result

    def test_fourier_transform_with_error(self, service):
        """Test Fourier transform with invalid expression"""
        result = service.fourier_transform("1/0", "t", "f")  # Division by zero should cause error
        assert "error" in result

    def test_laplace_transform_with_error(self, service):
        """Test Laplace transform with invalid expression"""
        result = service.laplace_transform("invalid_syntax+++", "t", "s")  # Invalid syntax should cause error
        assert "error" in result
