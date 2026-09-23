#!/usr/bin/env python3
"""
AXIOM Performance Profiler Demo
Demonstrates the advanced performance profiling system
"""

import asyncio
import numpy as np
from app.performance_profiler import profiler, profile_function

# Example functions to profile
@profile_function("matrix_multiplication")
def matrix_multiplication(size: int = 1000):
    """Simulate matrix multiplication"""
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    return np.dot(A, B)

@profile_function("fibonacci_recursive")
def fibonacci_recursive(n: int = 30):
    """Recursive Fibonacci calculation"""
    if n <= 1:
        return n
    return fibonacci_recursive(n-1) + fibonacci_recursive(n-2)

@profile_function("data_processing")
def data_processing(data_size: int = 1000000):
    """Simulate data processing"""
    data = np.random.rand(data_size)
    return {
        "mean": np.mean(data),
        "std": np.std(data),
        "min": np.min(data),
        "max": np.max(data)
    }

@profile_function("scientific_computation")
def scientific_computation(iterations: int = 10000):
    """Simulate scientific computation"""
    result = 0
    for i in range(iterations):
        result += np.sin(i) * np.cos(i) ** 2
    return result

async def async_demo():
    """Demonstrate profiling with async operations"""
    with profiler.profile_operation("async_matrix_ops"):
        # Simulate async matrix operations
        await asyncio.sleep(0.1)
        matrix_multiplication(500)

    with profiler.profile_operation("async_data_processing"):
        await asyncio.sleep(0.05)
        data_processing(500000)

def main():
    """Main demo function"""
    print("🚀 AXIOM Performance Profiler Demo")
    print("=" * 50)

    # Clear any previous metrics
    profiler.clear_metrics()

    print("\n📊 Running performance tests...")

    # Test 1: Matrix operations
    print("\n1️⃣ Matrix Multiplication Tests")
    for size in [500, 1000, 1500]:
        print(f"   Testing {size}x{size} matrix...")
        matrix_multiplication(size)

    # Test 2: Recursive computations
    print("\n2️⃣ Fibonacci Recursive Tests")
    for n in [25, 30, 35]:
        print(f"   Computing Fibonacci({n})...")
        fibonacci_recursive(n)

    # Test 3: Data processing
    print("\n3️⃣ Data Processing Tests")
    for size in [500000, 1000000, 2000000]:
        print(f"   Processing {size} data points...")
        data_processing(size)

    # Test 4: Scientific computations
    print("\n4️⃣ Scientific Computation Tests")
    for iterations in [5000, 10000, 20000]:
        print(f"   Running {iterations} iterations...")
        scientific_computation(iterations)

    # Test 5: Async operations
    print("\n5️⃣ Async Operations Test")
    asyncio.run(async_demo())

    # Generate performance report
    print("\n📈 Performance Report")
    print("=" * 30)
    report = profiler.get_performance_report()
    print(report)

    # Get detailed stats
    print("\n🔍 Detailed Statistics")
    print("=" * 25)
    all_stats = profiler.get_all_stats()
    for operation, stats in all_stats.items():
        if "error" not in stats:
            print(f"\n{operation}:")
            print(f"  Calls: {stats['total_calls']}")
            print(".2f")
            print(".2f")
            print(".2f")

    print("\n✅ Performance profiling demo completed!")

if __name__ == "__main__":
    main()
