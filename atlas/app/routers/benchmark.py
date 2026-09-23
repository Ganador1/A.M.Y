"""
Benchmark Management Router

FastAPI router for comprehensive performance benchmarking and algorithm comparison
in the AXIOM scientific computing platform. Provides REST API endpoints for
benchmark execution, performance analysis, and comparative algorithm evaluation.

This router offers advanced benchmarking capabilities for:
- Algorithm performance comparison across different implementations
- Scalability testing with configurable workload parameters
- Statistical analysis of benchmark results and performance metrics
- Comparative analysis of mathematical and scientific algorithms
- Performance regression detection and optimization validation
- Multi-threaded and distributed benchmark execution
- Custom benchmark creation and management

The router integrates with the BenchmarkHarnessService to provide
scientists and engineers with tools for evaluating computational performance,
identifying bottlenecks, and optimizing algorithms for scientific computing workloads.

Endpoints:
- GET /benchmark/list: List all available benchmarks and their configurations
- POST /benchmark/run/{name}: Execute specific benchmark with configurable repetitions

Dependencies:
- BenchmarkHarnessService: Core benchmarking execution and result collection
- PerformanceMetrics: Statistical analysis and performance measurement tools
- AlgorithmRegistry: Registry of available algorithms for benchmarking
- ResultStorage: Persistent storage for benchmark results and historical data
- Logging: Comprehensive logging for benchmark execution and results

Usage:
    Benchmarks support configurable repetitions for statistical significance.
    Results include execution time, memory usage, and performance metrics.
    Comparative analysis helps identify optimal algorithms for specific use cases.
"""

from fastapi import APIRouter
from app.services.benchmark_harness_service import benchmark_harness_service

router = APIRouter(prefix="/benchmark", tags=["benchmark"])

@router.get("/list")
def list_benchmarks():
    """List all available benchmarks.

    Returns a dictionary containing the list of benchmark names and their configurations.
    """
    return {"benchmarks": benchmark_harness_service.list_benchmarks()}

@router.post("/run/{name}")
def run_benchmark(name: str, repeats: int = 1):
    """Run a specific benchmark.

    Executes the benchmark with the given name for the specified number of repetitions.

    Args:
        name: The name of the benchmark to run.
        repeats: Number of times to repeat the benchmark (default: 1).

    Returns:
        The results of the benchmark execution.
    """
    return benchmark_harness_service.run(name, repeats=repeats)
