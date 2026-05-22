"""
GPU Acceleration Demo
Demonstrates advanced GPU acceleration capabilities for scientific computing
"""

import asyncio
import torch
import time
from app.gpu_accelerator import accelerate_scientific_operation, get_gpu_accelerator
from app.gpu_manager import get_gpu_manager

async def demo_basic():
    """Demo basic GPU acceleration"""
    print("GPU Acceleration Demo")
    print("=" * 30)

    # Check GPU availability
    gpu_manager = get_gpu_manager()
    device_info = gpu_manager.get_device_info()

    print(f"GPU Available: {device_info['device_available']}")
    print(f"Device Type: {device_info['device_type']}")

    if device_info['device_available']:
        # Simple matrix operation
        a = torch.randn(100, 100)
        b = torch.randn(100, 100)

        start_time = time.time()
        result = await accelerate_scientific_operation(
            "matrix_multiply",
            [a, b],
            return_cpu=True
        )
        gpu_time = time.time() - start_time

        print(f"GPU operation completed in {gpu_time:.4f}s")
        print(f"Result shape: {result.shape}")

        # Get performance stats
        accelerator = get_gpu_accelerator()
        stats = accelerator.get_performance_stats()
        print(f"Operations completed: {stats['performance_metrics']['operations_completed']}")

    print("Demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_basic())
