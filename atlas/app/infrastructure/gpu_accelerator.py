"""
Compatibility shim for legacy imports of GPU accelerator utilities.
Re-exports the GPUAccelerator API from the distributed module.
"""
from app.distributed.gpu_accelerator import (
    GPUAccelerator,
    GPUOperation,
    GPUMemoryManager,
    GPUMemoryStats,
    GPUPerformanceMetrics,
    gpu_accelerator,
    get_gpu_accelerator,
    accelerate_scientific_operation,
)

__all__ = [
    "GPUAccelerator",
    "GPUOperation",
    "GPUMemoryManager",
    "GPUMemoryStats",
    "GPUPerformanceMetrics",
    "gpu_accelerator",
    "get_gpu_accelerator",
    "accelerate_scientific_operation",
]