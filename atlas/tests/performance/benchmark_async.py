"""
Async Performance Benchmarking Suite for AXIOM ATLAS.

This module provides comprehensive benchmarking tools to measure the impact
of async optimizations on system performance.
"""

import asyncio
import time
import statistics
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Import services to benchmark
from app.services.literature_mining_service import LiteratureMiningService
from app.connectors.astronomical_data_connector import AstronomicalDataConnector
from app.core.executors import run_cpu_bound, run_io_bound


class AsyncBenchmarkSuite:
    """Comprehensive async performance benchmarking suite."""
    
    def __init__(self, output_dir: str = "reports/performance"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results = {}
        
    def _measure_system_resources(self) -> Dict[str, float]:
        """Measure current system resource usage."""
        process = psutil.Process(os.getpid())
        return {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "threads": process.num_threads(),
        }
    
    def _calculate_percentiles(self, data: List[float]) -> Dict[str, float]:
        """Calculate percentiles for performance data."""
        if not data:
            return {}
        
        sorted_data = sorted(data)
        return {
            "p50": sorted_data[int(len(sorted_data) * 0.5)],
            "p90": sorted_data[int(len(sorted_data) * 0.9)],
            "p95": sorted_data[int(len(sorted_data) * 0.95)],
            "p99": sorted_data[int(len(sorted_data) * 0.99)],
            "min": min(sorted_data),
            "max": max(sorted_data),
            "mean": statistics.mean(sorted_data),
            "std": statistics.stdev(sorted_data) if len(sorted_data) > 1 else 0,
        }
    
    async def benchmark_literature_mining_service(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark literature mining service async performance."""
        print(f"🔬 Benchmarking Literature Mining Service ({iterations} iterations)...")
        
        service = LiteratureMiningService()
        durations = []
        memory_usage = []
        cpu_usage = []
        
        # Test data
        test_texts = [
            "Machine learning algorithms for drug discovery in computational biology",
            "Quantum computing applications in molecular dynamics simulations",
            "Neural networks for protein structure prediction using AlphaFold",
            "Deep learning approaches to synthetic biology and genetic engineering",
            "Artificial intelligence in medical imaging and clinical diagnosis",
        ]
        
        start_time = time.time()
        
        for i in range(iterations):
            text = test_texts[i % len(test_texts)]
            
            # Measure resources before
            resources_before = self._measure_system_resources()
            
            # Execute async function
            iteration_start = time.time()
            try:
                result = await service.extract_key_concepts(text)
                iteration_duration = time.time() - iteration_start
                durations.append(iteration_duration)
                
                # Measure resources after
                resources_after = self._measure_system_resources()
                memory_usage.append(resources_after["memory_mb"])
                cpu_usage.append(resources_after["cpu_percent"])
                
            except Exception as e:
                print(f"⚠️  Error in iteration {i}: {e}")
                continue
        
        total_time = time.time() - start_time
        
        return {
            "service": "literature_mining_service",
            "iterations": len(durations),
            "total_time": total_time,
            "throughput_rps": len(durations) / total_time if total_time > 0 else 0,
            "duration_stats": self._calculate_percentiles(durations),
            "memory_stats": self._calculate_percentiles(memory_usage),
            "cpu_stats": self._calculate_percentiles(cpu_usage),
            "success_rate": len(durations) / iterations * 100,
        }
    
    async def benchmark_astronomical_connector(self, iterations: int = 50) -> Dict[str, Any]:
        """Benchmark astronomical data connector async performance."""
        print(f"🌌 Benchmarking Astronomical Data Connector ({iterations} iterations)...")
        
        connector = AstronomicalDataConnector()
        durations = []
        memory_usage = []
        cpu_usage = []
        
        # Test queries
        test_queries = [
            "HD 209458",
            "51 Peg",
            "Kepler-452b",
            "TRAPPIST-1",
            "Proxima Centauri",
        ]
        
        start_time = time.time()
        
        for i in range(iterations):
            object_name = test_queries[i % len(test_queries)]
            
            # Measure resources before
            resources_before = self._measure_system_resources()
            
            # Execute async function
            iteration_start = time.time()
            try:
                result = await connector.query_simbad(object_name)
                iteration_duration = time.time() - iteration_start
                durations.append(iteration_duration)
                
                # Measure resources after
                resources_after = self._measure_system_resources()
                memory_usage.append(resources_after["memory_mb"])
                cpu_usage.append(resources_after["cpu_percent"])
                
            except Exception as e:
                print(f"⚠️  Error in iteration {i}: {e}")
                continue
        
        total_time = time.time() - start_time
        
        return {
            "service": "astronomical_data_connector",
            "iterations": len(durations),
            "total_time": total_time,
            "throughput_rps": len(durations) / total_time if total_time > 0 else 0,
            "duration_stats": self._calculate_percentiles(durations),
            "memory_stats": self._calculate_percentiles(memory_usage),
            "cpu_stats": self._calculate_percentiles(cpu_usage),
            "success_rate": len(durations) / iterations * 100,
        }
    
    async def benchmark_executor_performance(self, iterations: int = 100) -> Dict[str, Any]:
        """Benchmark CPU and I/O executor performance."""
        print(f"⚡ Benchmarking Executor Performance ({iterations} iterations)...")
        
        # CPU-bound test function
        def cpu_intensive_task(n: int) -> int:
            """Simulate CPU-intensive computation."""
            result = 0
            for i in range(n):
                result += i ** 2
            return result
        
        # I/O-bound test function
        def io_intensive_task(duration: float) -> str:
            """Simulate I/O-intensive operation."""
            time.sleep(duration)
            return f"Completed after {duration}s"
        
        # Benchmark CPU executor
        cpu_durations = []
        cpu_start = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            try:
                result = await run_cpu_bound(cpu_intensive_task, 100000)
                iteration_duration = time.time() - iteration_start
                cpu_durations.append(iteration_duration)
            except Exception as e:
                print(f"⚠️  CPU executor error in iteration {i}: {e}")
                continue
        
        cpu_total_time = time.time() - cpu_start
        
        # Benchmark I/O executor
        io_durations = []
        io_start = time.time()
        
        for i in range(iterations):
            iteration_start = time.time()
            try:
                result = await run_io_bound(io_intensive_task, 0.01)  # 10ms I/O
                iteration_duration = time.time() - iteration_start
                io_durations.append(iteration_duration)
            except Exception as e:
                print(f"⚠️  I/O executor error in iteration {i}: {e}")
                continue
        
        io_total_time = time.time() - io_start
        
        return {
            "service": "executors",
            "iterations": iterations,
            "cpu_executor": {
                "total_time": cpu_total_time,
                "throughput_rps": len(cpu_durations) / cpu_total_time if cpu_total_time > 0 else 0,
                "duration_stats": self._calculate_percentiles(cpu_durations),
                "success_rate": len(cpu_durations) / iterations * 100,
            },
            "io_executor": {
                "total_time": io_total_time,
                "throughput_rps": len(io_durations) / io_total_time if io_total_time > 0 else 0,
                "duration_stats": self._calculate_percentiles(io_durations),
                "success_rate": len(io_durations) / iterations * 100,
            },
        }
    
    async def benchmark_concurrent_operations(self, concurrent_tasks: int = 20, iterations: int = 5) -> Dict[str, Any]:
        """Benchmark concurrent async operations."""
        print(f"🔄 Benchmarking Concurrent Operations ({concurrent_tasks} tasks, {iterations} iterations)...")
        
        service = LiteratureMiningService()
        all_durations = []
        all_throughput = []
        
        for iteration in range(iterations):
            # Create concurrent tasks
            tasks = []
            for i in range(concurrent_tasks):
                text = f"Concurrent test {i} - machine learning and artificial intelligence research"
                task = service.extract_key_concepts(text)
                tasks.append(task)
            
            # Execute concurrently
            iteration_start = time.time()
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                iteration_duration = time.time() - iteration_start
                
                # Count successful results
                successful_results = [r for r in results if not isinstance(r, Exception)]
                throughput = len(successful_results) / iteration_duration
                
                all_durations.append(iteration_duration)
                all_throughput.append(throughput)
                
            except Exception as e:
                print(f"⚠️  Concurrent operation error in iteration {iteration}: {e}")
                continue
        
        return {
            "service": "concurrent_operations",
            "concurrent_tasks": concurrent_tasks,
            "iterations": len(all_durations),
            "duration_stats": self._calculate_percentiles(all_durations),
            "throughput_stats": self._calculate_percentiles(all_throughput),
            "avg_throughput": statistics.mean(all_throughput) if all_throughput else 0,
        }
    
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive async performance benchmark."""
        print("🚀 Starting Comprehensive Async Performance Benchmark...")
        print("=" * 60)
        
        start_time = time.time()
        
        # Run all benchmarks
        benchmarks = {
            "literature_mining": await self.benchmark_literature_mining_service(50),
            "astronomical_connector": await self.benchmark_astronomical_connector(20),
            "executors": await self.benchmark_executor_performance(50),
            "concurrent_operations": await self.benchmark_concurrent_operations(10, 3),
        }
        
        total_time = time.time() - start_time
        
        # Compile results
        results = {
            "benchmark_info": {
                "timestamp": datetime.now().isoformat(),
                "total_duration": total_time,
                "system_info": {
                    "cpu_count": psutil.cpu_count(),
                    "memory_gb": psutil.virtual_memory().total / (1024**3),
                    "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
                }
            },
            "benchmarks": benchmarks,
            "summary": self._generate_summary(benchmarks),
        }
        
        # Save results
        output_file = self.output_dir / f"async_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📄 Results saved to: {output_file}")
        return results
    
    def _generate_summary(self, benchmarks: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary of benchmark results."""
        summary = {
            "overall_throughput": 0,
            "avg_latency_p95": 0,
            "success_rate": 0,
            "performance_grade": "F",
        }
        
        # Calculate overall metrics
        throughputs = []
        latencies = []
        success_rates = []
        
        for benchmark_name, benchmark_data in benchmarks.items():
            if "throughput_rps" in benchmark_data:
                throughputs.append(benchmark_data["throughput_rps"])
            elif "avg_throughput" in benchmark_data:
                throughputs.append(benchmark_data["avg_throughput"])
            
            if "duration_stats" in benchmark_data and "p95" in benchmark_data["duration_stats"]:
                latencies.append(benchmark_data["duration_stats"]["p95"])
            
            if "success_rate" in benchmark_data:
                success_rates.append(benchmark_data["success_rate"])
        
        # Calculate averages
        if throughputs:
            summary["overall_throughput"] = statistics.mean(throughputs)
        if latencies:
            summary["avg_latency_p95"] = statistics.mean(latencies)
        if success_rates:
            summary["success_rate"] = statistics.mean(success_rates)
        
        # Performance grading
        if summary["success_rate"] >= 95 and summary["avg_latency_p95"] <= 1.0:
            summary["performance_grade"] = "A"
        elif summary["success_rate"] >= 90 and summary["avg_latency_p95"] <= 2.0:
            summary["performance_grade"] = "B"
        elif summary["success_rate"] >= 80 and summary["avg_latency_p95"] <= 5.0:
            summary["performance_grade"] = "C"
        elif summary["success_rate"] >= 70:
            summary["performance_grade"] = "D"
        else:
            summary["performance_grade"] = "F"
        
        return summary
    
    def print_results(self, results: Dict[str, Any]):
        """Print benchmark results in a readable format."""
        print("\n" + "=" * 60)
        print("📊 ASYNC PERFORMANCE BENCHMARK RESULTS")
        print("=" * 60)
        
        # System info
        system_info = results["benchmark_info"]["system_info"]
        print(f"🖥️  System: {system_info['cpu_count']} CPUs, {system_info['memory_gb']:.1f}GB RAM")
        print(f"🐍 Python: {system_info['python_version']}")
        print(f"⏱️  Total Duration: {results['benchmark_info']['total_duration']:.2f}s")
        
        # Summary
        summary = results["summary"]
        print(f"\n📈 SUMMARY:")
        print(f"  Overall Throughput: {summary['overall_throughput']:.2f} RPS")
        print(f"  Average P95 Latency: {summary['avg_latency_p95']:.3f}s")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Performance Grade: {summary['performance_grade']}")
        
        # Individual benchmarks
        print(f"\n🔬 INDIVIDUAL BENCHMARKS:")
        for benchmark_name, benchmark_data in results["benchmarks"].items():
            print(f"\n  {benchmark_name.upper()}:")
            
            if "throughput_rps" in benchmark_data:
                print(f"    Throughput: {benchmark_data['throughput_rps']:.2f} RPS")
            elif "avg_throughput" in benchmark_data:
                print(f"    Throughput: {benchmark_data['avg_throughput']:.2f} RPS")
            
            if "duration_stats" in benchmark_data:
                stats = benchmark_data["duration_stats"]
                print(f"    P95 Latency: {stats.get('p95', 0):.3f}s")
                print(f"    Mean Latency: {stats.get('mean', 0):.3f}s")
            
            if "success_rate" in benchmark_data:
                print(f"    Success Rate: {benchmark_data['success_rate']:.1f}%")
            
            if "iterations" in benchmark_data:
                print(f"    Iterations: {benchmark_data['iterations']}")


async def main():
    """Main entry point for async benchmarking."""
    suite = AsyncBenchmarkSuite()
    
    try:
        results = await suite.run_comprehensive_benchmark()
        suite.print_results(results)
        
        # Check if performance meets targets
        summary = results["summary"]
        if summary["performance_grade"] in ["A", "B"]:
            print("\n✅ Performance targets met!")
        else:
            print("\n⚠️  Performance below targets - optimization needed")
        
        return 0
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
