"""
GPU Acceleration Demo
Demonstrates advanced GPU acceleration capabilities for scientific computing
"""

import asyncio
import torch
import numpy as np
import time
from app.gpu_accelerator import accelerate_scientific_operation, get_gpu_accelerator
from app.gpu_manager import get_gpu_manager

async def demo_matrix_operations():
    """Demo matrix multiplication acceleration"""
    print("🚀 Demo: Matrix Operations Acceleration")
    print("=" * 50)

    # Create large matrices
    size = 1000
    a = torch.randn(size, size)
    b = torch.randn(size, size)

    print(f"Matrix size: {size}x{size}")
    print(f"Memory requirement: ~{a.numel() * a.element_size() / (1024**2):.1f} MB per matrix")

    # GPU accelerated operation
    start_time = time.time()
    result_gpu = await accelerate_scientific_operation(
        "matrix_multiply",
        [a, b],
        return_cpu=True
    )
    gpu_time = time.time() - start_time

    # CPU operation for comparison
    start_time = time.time()
    result_cpu = torch.matmul(a, b)
    cpu_time = time.time() - start_time

    print(f"GPU time: {gpu_time:.4f}s")
    print(f"CPU time: {cpu_time:.4f}s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    return result_gpu, result_cpu

async def demo_vector_operations():
    """Demo vector operations acceleration"""
    print("
🔢 Demo: Vector Operations Acceleration")
    print("=" * 50)

    # Create large vector
    size = 1000000
    vector = torch.randn(size)

    print(f"Vector size: {size}")
    print(f"Memory requirement: ~{vector.numel() * vector.element_size() / (1024**2):.1f} MB")

    # GPU accelerated normalization
    start_time = time.time()
    normalized_gpu = await accelerate_scientific_operation(
        "vector_ops",
        vector,
        sub_operation="normalize",
        return_cpu=True
    )
    gpu_time = time.time() - start_time

    # CPU operation
    start_time = time.time()
    normalized_cpu = torch.nn.functional.normalize(vector, dim=-1)
    cpu_time = time.time() - start_time

    print(f"GPU time: {gpu_time:.4f}s")
    print(f"CPU time: {cpu_time:.4f}s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    return normalized_gpu, normalized_cpu

async def demo_scientific_computing():
    """Demo scientific computing acceleration (FFT)"""
    print("
🧪 Demo: Scientific Computing Acceleration")
    print("=" * 50)

    # Create signal data
    sample_rate = 1000
    duration = 1.0
    t = torch.linspace(0, duration, int(sample_rate * duration))
    signal = torch.sin(2 * torch.pi * 50 * t) + 0.5 * torch.sin(2 * torch.pi * 120 * t)

    print(f"Signal length: {len(signal)} samples")
    print(f"Duration: {duration}s at {sample_rate}Hz")

    # GPU accelerated FFT
    start_time = time.time()
    fft_gpu = await accelerate_scientific_operation(
        "scientific",
        signal,
        sub_operation="fft",
        return_cpu=True
    )
    gpu_time = time.time() - start_time

    # CPU FFT
    start_time = time.time()
    fft_cpu = torch.fft.fft(signal)
    cpu_time = time.time() - start_time

    print(f"GPU time: {gpu_time:.4f}s")
    print(f"CPU time: {cpu_time:.4f}s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    return fft_gpu, fft_cpu

async def demo_memory_management():
    """Demo GPU memory management"""
    print("
💾 Demo: GPU Memory Management")
    print("=" * 50)

    accelerator = get_gpu_accelerator()
    gpu_manager = get_gpu_manager()

    print("Initial memory stats:")
    memory_stats = accelerator.memory_manager.get_memory_stats()
    print(f"  Allocated: {memory_stats.allocated_mb:.1f} MB")
    print(f"  Reserved: {memory_stats.reserved_mb:.1f} MB")
    print(f"  Available: {memory_stats.available_mb:.1f} MB")

    # Perform memory-intensive operation
    large_matrix = torch.randn(2000, 2000)
    result = await accelerate_scientific_operation(
        "matrix_multiply",
        [large_matrix, large_matrix],
        return_cpu=False  # Keep on GPU
    )

    print("
After large operation:")
    memory_stats = accelerator.memory_manager.get_memory_stats()
    print(f"  Allocated: {memory_stats.allocated_mb:.1f} MB")
    print(f"  Reserved: {memory_stats.reserved_mb:.1f} MB")
    print(f"  Available: {memory_stats.available_mb:.1f} MB")

    # Clean up
    accelerator.memory_manager.optimize_memory()

    print("
After memory optimization:")
    memory_stats = accelerator.memory_manager.get_memory_stats()
    print(f"  Allocated: {memory_stats.allocated_mb:.1f} MB")
    print(f"  Reserved: {memory_stats.reserved_mb:.1f} MB")
    print(f"  Available: {memory_stats.available_mb:.1f} MB")

async def demo_workload_optimization():
    """Demo workload-specific optimization"""
    print("
⚡ Demo: Workload-Specific Optimization")
    print("=" * 50)

    accelerator = get_gpu_accelerator()

    print("Optimizing for scientific workload...")
    accelerator.optimize_for_workload("scientific")

    print("GPU settings optimized for scientific computing")
    print("- CuDNN benchmark: Enabled")
    print("- Memory threshold: 90%")
    print("- Deterministic operations: Disabled")

async def run_gpu_acceleration_demo():
    """Run complete GPU acceleration demonstration"""
    print("🎯 AXIOM GPU Acceleration Demo")
    print("=" * 60)

    # Check GPU availability
    gpu_manager = get_gpu_manager()
    device_info = gpu_manager.get_device_info()

    print(f"GPU Available: {device_info['device_available']}")
    print(f"Device Type: {device_info['device_type']}")
    print(f"Device Count: {device_info['device_count']}")
    print(f"Device Names: {', '.join(device_info['device_names'])}")
    if device_info['memory_gb']:
        print(f"Memory: {device_info['memory_gb']:.1f} GB")
    print()

    if not device_info['device_available']:
        print("⚠️  No GPU detected. Demo will use CPU fallback.")
        print()

    try:
        # Run demos
        await demo_matrix_operations()
        await demo_vector_operations()
        await demo_scientific_computing()
        await demo_memory_management()
        await demo_workload_optimization()

        # Final performance stats
        accelerator = get_gpu_accelerator()
        stats = accelerator.get_performance_stats()

        print("
📊 Final Performance Statistics")
        print("=" * 50)
        print(f"Operations completed: {stats['performance_metrics']['operations_completed']}")
        print(f"Total compute time: {stats['performance_metrics']['total_compute_time_sec']:.4f}s")
        print(f"Average operation time: {stats['performance_metrics']['average_operation_time_sec']:.4f}s")
        print(f"Average memory utilization: {stats['performance_metrics']['average_memory_utilization']:.1f}%")

        print("
Demo completed successfully! 🎉")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_gpu_acceleration_demo())

import asyncio
import torch
import numpy as np
import time
from app.gpu_accelerator import accelerate_scientific_operation, get_gpu_accelerator
from app.gpu_manager import get_gpu_manager

async def demo_matrix_operations():
    """Demo matrix multiplication acceleration"""
    print("🚀 Demo: Matrix Operations Acceleration")
    print("=" * 50)

    # Create large matrices
    size = 1000
    a = torch.randn(size, size)
    b = torch.randn(size, size)

    print(f"Matrix size: {size}x{size}")
    print(f"Memory requirement: ~{a.numel() * a.element_size() / (1024**2):.1f} MB per matrix")

    # GPU accelerated operation
    start_time = time.time()
    result_gpu = await accelerate_scientific_operation(
        "matrix_multiply",
        [a, b],
        return_cpu=True
    )
    gpu_time = time.time() - start_time

    # CPU operation for comparison
    start_time = time.time()
    result_cpu = torch.matmul(a, b)
    cpu_time = time.time() - start_time

    print(f"GPU time: {gpu_time:.4f}s")
    print(f"CPU time: {cpu_time:.4f}s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    return result_gpu, result_cpu

async def demo_vector_operations():
    """Demo vector operations acceleration"""
    print("\n🔢 Demo: Vector Operations Acceleration")
    print("=" * 50)

    # Create large vector
    size = 1000000
    vector = torch.randn(size)

    print(f"Vector size: {size}")
    print(f"Memory requirement: ~{vector.numel() * vector.element_size() / (1024**2):.1f} MB")

    # GPU accelerated normalization
    start_time = time.time()
    normalized_gpu = await accelerate_scientific_operation(
        "vector_ops",
        vector,
        sub_operation="normalize",
        return_cpu=True
    )
    gpu_time = time.time() - start_time

    # CPU operation
    start_time = time.time()
    normalized_cpu = torch.nn.functional.normalize(vector, dim=-1)
    cpu_time = time.time() - start_time

    print(f"GPU time: {gpu_time:.4f}s")
    print(f"CPU time: {cpu_time:.4f}s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")

    return normalized_gpu, normalized_cpu

async def demo_scientific_computing():
    """Demo scientific computing acceleration (FFT)"""
    print("\n🧪 Demo: Scientific Computing Acceleration")
    print("=" * 50)

    # Create signal data
    sample_rate = 1000
    duration = 1.0
    t = torch.linspace(0, duration, int(sample_rate * duration))
    signal = torch.sin(2 * torch.pi * 50 * t) + 0.5 * torch.sin(2 * torch.pi * 120 * t)

    print(f"Signal length: {len(signal)} samples")
    print(f"Duration: {duration}s at {sample_rate}Hz")

    # GPU accelerated FFT
    start_time = time.time()
    fft_gpu = await accelerate_scientific_operation(
        "scientific",
        signal,
        sub_operation="fft",
        return_cpu=True
    )
    gpu_time = time.time() - start_time

    # CPU FFT
    start_time = time.time()
    fft_cpu = torch.fft.fft(signal)
    cpu_time = time.time() - start_time

    print(".4f"    print(".4f"    print(".2f"
    return fft_gpu, fft_cpu

async def demo_memory_management():
    """Demo GPU memory management"""
    print("\n💾 Demo: GPU Memory Management")
    print("=" * 50)

    accelerator = get_gpu_accelerator()
    gpu_manager = get_gpu_manager()

    print("Initial memory stats:")
    memory_stats = accelerator.memory_manager.get_memory_stats()
    print(f"  Allocated: {memory_stats.allocated_mb:.1f} MB")
    print(f"  Reserved: {memory_stats.reserved_mb:.1f} MB")
    print(f"  Available: {memory_stats.available_mb:.1f} MB")

    # Perform memory-intensive operation
    large_matrix = torch.randn(2000, 2000)
    result = await accelerate_scientific_operation(
        "matrix_multiply",
        [large_matrix, large_matrix],
        return_cpu=False  # Keep on GPU
    )

    print("\nAfter large operation:")
    memory_stats = accelerator.memory_manager.get_memory_stats()
    print(f"  Allocated: {memory_stats.allocated_mb:.1f} MB")
    print(f"  Reserved: {memory_stats.reserved_mb:.1f} MB")
    print(f"  Available: {memory_stats.available_mb:.1f} MB")

    # Clean up
    accelerator.memory_manager.optimize_memory()

    print("\nAfter memory optimization:")
    memory_stats = accelerator.memory_manager.get_memory_stats()
    print(f"  Allocated: {memory_stats.allocated_mb:.1f} MB")
    print(f"  Reserved: {memory_stats.reserved_mb:.1f} MB")
    print(f"  Available: {memory_stats.available_mb:.1f} MB")

async def demo_workload_optimization():
    """Demo workload-specific optimization"""
    print("\n⚡ Demo: Workload-Specific Optimization")
    print("=" * 50)

    accelerator = get_gpu_accelerator()

    print("Optimizing for scientific workload...")
    accelerator.optimize_for_workload("scientific")

    print("GPU settings optimized for scientific computing")
    print("- CuDNN benchmark: Enabled")
    print("- Memory threshold: 90%")
    print("- Deterministic operations: Disabled")

async def run_gpu_acceleration_demo():
    """Run complete GPU acceleration demonstration"""
    print("🎯 AXIOM GPU Acceleration Demo")
    print("=" * 60)

    # Check GPU availability
    gpu_manager = get_gpu_manager()
    device_info = gpu_manager.get_device_info()

    print(f"GPU Available: {device_info['device_available']}")
    print(f"Device Type: {device_info['device_type']}")
    print(f"Device Count: {device_info['device_count']}")
    print(f"Device Names: {', '.join(device_info['device_names'])}")
    if device_info['memory_gb']:
        print(".1f"
    print()

    if not device_info['device_available']:
        print("⚠️  No GPU detected. Demo will use CPU fallback.")
        print()

    try:
        # Run demos
        await demo_matrix_operations()
        await demo_vector_operations()
        await demo_scientific_computing()
        await demo_memory_management()
        await demo_workload_optimization()

        # Final performance stats
        accelerator = get_gpu_accelerator()
        stats = accelerator.get_performance_stats()

        print("\n📊 Final Performance Statistics")
        print("=" * 50)
        print(f"Operations completed: {stats['performance_metrics']['operations_completed']}")
        print(".4f"        print(".4f"        print(".1f"
        print("Demo completed successfully! 🎉")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_gpu_acceleration_demo())
