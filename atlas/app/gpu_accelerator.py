"""
Wrapper module for GPUAccelerator
"""

from app.distributed.gpu_accelerator import GPUAccelerator, get_gpu_accelerator, accelerate_scientific_operation

__all__ = ['GPUAccelerator', 'get_gpu_accelerator', 'accelerate_scientific_operation']