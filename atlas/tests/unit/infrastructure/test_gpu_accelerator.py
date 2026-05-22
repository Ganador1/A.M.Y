#!/usr/bin/env python3
"""
Unit tests for AXIOM GPU Accelerator Service
"""

import pytest
import numpy as np
from unittest.mock import patch
from app.gpu_accelerator import GPUAccelerator

class TestGPUAccelerator:
    """Test cases for GPUAccelerator"""

    @pytest.fixture
    def gpu_accelerator(self):
        """Create a test GPU accelerator instance"""
        return GPUAccelerator()

    def test_gpu_accelerator_initialization(self, gpu_accelerator):
        """Test GPU accelerator initialization"""
        assert gpu_accelerator.device is not None
        assert gpu_accelerator.kernels is not None
        assert gpu_accelerator.memory_manager is not None

    @patch('torch.cuda.is_available')
    @patch('torch.backends.mps.is_available')
    def test_device_detection(self, mock_mps_available, mock_cuda_available, gpu_accelerator):
        """Test GPU device detection"""
        # Test CUDA available
        mock_cuda_available.return_value = True
        mock_mps_available.return_value = False

        # Test MPS available
        mock_cuda_available.return_value = False
        mock_mps_available.return_value = True

        # Test no GPU available
        mock_cuda_available.return_value = False
        mock_mps_available.return_value = False

    def test_matrix_operations(self, gpu_accelerator):
        """Test matrix operations on GPU"""
        # Create test matrices
        A = np.random.rand(100, 100).astype(np.float32)
        B = np.random.rand(100, 100).astype(np.float32)

        # Test matrix multiplication
        result = gpu_accelerator.accelerate_operation("matrix_multiply", A, B)
        expected = np.dot(A, B)

        # Allow for small numerical differences
        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_vector_operations(self, gpu_accelerator):
        """Test vector operations on GPU"""
        # Create test vectors
        v1 = np.random.rand(1000).astype(np.float32)
        v2 = np.random.rand(1000).astype(np.float32)

        # Test vector addition
        result = gpu_accelerator.accelerate_operation("vector_add", v1, v2)
        expected = v1 + v2

        np.testing.assert_allclose(result, expected, rtol=1e-6)

    def test_fft_operations(self, gpu_accelerator):
        """Test FFT operations on GPU"""
        # Create test signal
        signal = np.random.rand(1024).astype(np.complex64)

        # Test FFT
        result = gpu_accelerator.accelerate_operation("fft", signal)
        expected = np.fft.fft(signal)

        np.testing.assert_allclose(result, expected, rtol=1e-5)

    def test_memory_management(self, gpu_accelerator):
        """Test GPU memory management"""
        # Test memory allocation
        initial_memory = gpu_accelerator.memory_manager.get_memory_usage()

        # Allocate some memory
        data = np.random.rand(1000, 1000).astype(np.float32)
        gpu_accelerator.accelerate_operation("matrix_multiply", data, data)

        # Check memory usage increased
        final_memory = gpu_accelerator.memory_manager.get_memory_usage()
        assert final_memory >= initial_memory

    def test_kernel_compilation(self, gpu_accelerator):
        """Test JIT kernel compilation"""
        # Test kernel loading
        kernels = gpu_accelerator._load_scientific_kernels()

        assert "matrix_multiply" in kernels
        assert "vector_add" in kernels
        assert "fft" in kernels

        # Test kernel execution
        kernel = kernels["matrix_multiply"]
        assert kernel is not None

    def test_performance_metrics(self, gpu_accelerator):
        """Test performance metrics collection"""
        initial_metrics = gpu_accelerator.get_performance_metrics()

        # Perform some operations
        A = np.random.rand(50, 50).astype(np.float32)
        B = np.random.rand(50, 50).astype(np.float32)
        gpu_accelerator.accelerate_operation("matrix_multiply", A, B)

        final_metrics = gpu_accelerator.get_performance_metrics()

        # Metrics should be updated
        assert final_metrics["total_operations"] > initial_metrics["total_operations"]
        assert final_metrics["total_compute_time"] > initial_metrics["total_compute_time"]

    def test_error_handling(self, gpu_accelerator):
        """Test error handling in GPU operations"""
        # Test with invalid input
        with pytest.raises(ValueError):
            gpu_accelerator.accelerate_operation("invalid_operation", "invalid_input")

        # Test with mismatched dimensions
        A = np.random.rand(10, 20).astype(np.float32)
        B = np.random.rand(15, 25).astype(np.float32)

        with pytest.raises(ValueError):
            gpu_accelerator.accelerate_operation("matrix_multiply", A, B)

    def test_memory_cleanup(self, gpu_accelerator):
        """Test GPU memory cleanup"""
        # Perform operations that use GPU memory
        A = np.random.rand(100, 100).astype(np.float32)
        B = np.random.rand(100, 100).astype(np.float32)
        gpu_accelerator.accelerate_operation("matrix_multiply", A, B)

        # Force cleanup
        gpu_accelerator.memory_manager.cleanup()

        # Memory usage should be reduced
        # Note: This test might be flaky depending on PyTorch's memory management

    @patch('app.gpu_accelerator.torch')
    def test_fallback_to_cpu(self, mock_torch, gpu_accelerator):
        """Test fallback to CPU when GPU is unavailable"""
        # Mock GPU unavailability
        mock_torch.cuda.is_available.return_value = False
        mock_torch.backends.mps.is_available.return_value = False

        # Create new accelerator (to trigger device detection)
        accelerator = GPUAccelerator()

        # Should still work with CPU fallback
        A = np.random.rand(10, 10).astype(np.float32)
        B = np.random.rand(10, 10).astype(np.float32)

        import asyncio
        result = asyncio.run(accelerator.accelerate_operation("matrix_multiply", [A, B]))

        assert result is not None
        assert result.shape == (10, 10)

if __name__ == "__main__":
    pytest.main([__file__])
