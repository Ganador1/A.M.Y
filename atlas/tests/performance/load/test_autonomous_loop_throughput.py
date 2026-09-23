"""Load testing for autonomous loops throughput and performance."""
import asyncio
import time
import statistics
from typing import Dict, List, Any
import pytest
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.autonomous.pipelines.biology_loop import BiologyLoop
from app.autonomous.pipelines.chemistry_loop import ChemistryLoop
from app.autonomous.pipelines.quantum_loop import QuantumLoop
from app.autonomous.pipelines.mathematics_loop import MathematicsLoop


class LoadTestMetrics:
    """Collects and analyzes load test metrics."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.durations: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.success_count = 0
        self.error_count = 0
        self.errors: List[str] = []
    
    def start(self):
        """Start timing the load test."""
        self.start_time = time.time()
    
    def end(self):
        """End timing the load test."""
        self.end_time = time.time()
    
    def record_iteration(self, duration: float, success: bool, error: str = None):
        """Record metrics for a single iteration."""
        self.durations.append(duration)
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
            if error:
                self.errors.append(error)
    
    def record_system_metrics(self):
        """Record current system resource usage."""
        process = psutil.Process(os.getpid())
        self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        self.cpu_usage.append(process.cpu_percent())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the load test."""
        if not self.durations:
            return {"error": "No iterations recorded"}
        
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        return {
            "total_iterations": len(self.durations),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / len(self.durations) * 100,
            "total_time": total_time,
            "throughput_rps": len(self.durations) / total_time if total_time > 0 else 0,
            "duration_stats": {
                "mean": statistics.mean(self.durations),
                "median": statistics.median(self.durations),
                "p95": self._percentile(self.durations, 95),
                "p99": self._percentile(self.durations, 99),
                "min": min(self.durations),
                "max": max(self.durations),
            },
            "memory_stats": {
                "mean_mb": statistics.mean(self.memory_usage) if self.memory_usage else 0,
                "max_mb": max(self.memory_usage) if self.memory_usage else 0,
            },
            "cpu_stats": {
                "mean_percent": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
                "max_percent": max(self.cpu_usage) if self.cpu_usage else 0,
            },
            "errors": self.errors[:10],  # First 10 errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


def run_biology_iteration(loop: BiologyLoop, iteration_data: Dict[str, Any] = None) -> tuple[bool, float, str]:
    """Run a single biology loop iteration and return success, duration, error."""
    start_time = time.time()
    try:
        result = loop.run_iteration(top_n=3, iteration_data=iteration_data)
        duration = time.time() - start_time
        return True, duration, None
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e)


def run_chemistry_iteration(loop: ChemistryLoop, application: str = "drug_discovery") -> tuple[bool, float, str]:
    """Run a single chemistry loop iteration and return success, duration, error."""
    start_time = time.time()
    try:
        result = loop.run_iteration(top_n=3, application=application)
        duration = time.time() - start_time
        return True, duration, None
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e)


def run_quantum_iteration(loop: QuantumLoop, max_candidates: int = 5) -> tuple[bool, float, str]:
    """Run a single quantum loop iteration and return success, duration, error."""
    start_time = time.time()
    try:
        result = loop.run_iteration(max_candidates=max_candidates)
        duration = time.time() - start_time
        return True, duration, None
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e)


def run_mathematics_iteration(loop: MathematicsLoop, domain: str = "number_theory") -> tuple[bool, float, str]:
    """Run a single mathematics loop iteration and return success, duration, error."""
    start_time = time.time()
    try:
        result = loop.run_iteration(domain=domain)
        duration = time.time() - start_time
        return True, duration, None
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e)


class TestAutonomousLoopThroughput:
    """Load tests for autonomous loop throughput and performance."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_biology_loop_throughput(self):
        """Test biology loop throughput under load."""
        loop = BiologyLoop()
        metrics = LoadTestMetrics()
        
        # Test parameters
        concurrent_iterations = 10
        total_iterations = 50
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_iterations) as executor:
            futures = []
            
            for i in range(total_iterations):
                iteration_data = {
                    "iteration_id": i,
                    "target_pathway": f"pathway_{i % 5}",
                    "gene_interactions": f"interactions_{i % 3}",
                }
                future = executor.submit(run_biology_iteration, loop, iteration_data)
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error = future.result()
                metrics.record_iteration(duration, success, error)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 80.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 1.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["duration_stats"]["p95"] <= 30.0, f"P95 latency too high: {summary['duration_stats']['p95']:.2f}s"
        assert summary["memory_stats"]["max_mb"] <= 1000, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Biology Loop Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_chemistry_loop_throughput(self):
        """Test chemistry loop throughput under load."""
        loop = ChemistryLoop()
        metrics = LoadTestMetrics()
        
        # Test parameters
        concurrent_iterations = 8
        total_iterations = 40
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_iterations) as executor:
            futures = []
            
            applications = ["drug_discovery", "materials_science", "catalysis"]
            for i in range(total_iterations):
                application = applications[i % len(applications)]
                future = executor.submit(run_chemistry_iteration, loop, application)
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error = future.result()
                metrics.record_iteration(duration, success, error)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 80.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 1.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["duration_stats"]["p95"] <= 25.0, f"P95 latency too high: {summary['duration_stats']['p95']:.2f}s"
        assert summary["memory_stats"]["max_mb"] <= 800, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Chemistry Loop Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_quantum_loop_throughput(self):
        """Test quantum loop throughput under load."""
        loop = QuantumLoop()
        metrics = LoadTestMetrics()
        
        # Test parameters
        concurrent_iterations = 6
        total_iterations = 30
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_iterations) as executor:
            futures = []
            
            for i in range(total_iterations):
                max_candidates = 3 + (i % 3)  # 3-5 candidates
                future = executor.submit(run_quantum_iteration, loop, max_candidates)
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error = future.result()
                metrics.record_iteration(duration, success, error)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 80.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 0.5, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["duration_stats"]["p95"] <= 40.0, f"P95 latency too high: {summary['duration_stats']['p95']:.2f}s"
        assert summary["memory_stats"]["max_mb"] <= 600, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Quantum Loop Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_mathematics_loop_throughput(self):
        """Test mathematics loop throughput under load."""
        loop = MathematicsLoop()
        metrics = LoadTestMetrics()
        
        # Test parameters
        concurrent_iterations = 8
        total_iterations = 40
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_iterations) as executor:
            futures = []
            
            domains = ["number_theory", "algebra", "topology", "analysis"]
            for i in range(total_iterations):
                domain = domains[i % len(domains)]
                future = executor.submit(run_mathematics_iteration, loop, domain)
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error = future.result()
                metrics.record_iteration(duration, success, error)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 80.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 1.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["duration_stats"]["p95"] <= 20.0, f"P95 latency too high: {summary['duration_stats']['p95']:.2f}s"
        assert summary["memory_stats"]["max_mb"] <= 500, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Mathematics Loop Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_mixed_loops_concurrent_load(self):
        """Test mixed autonomous loops running concurrently."""
        loops = {
            "biology": BiologyLoop(),
            "chemistry": ChemistryLoop(),
            "quantum": QuantumLoop(),
            "mathematics": MathematicsLoop(),
        }
        
        metrics = LoadTestMetrics()
        
        # Test parameters
        total_iterations = 20  # 5 per loop
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            
            # Submit mixed iterations
            for i in range(total_iterations):
                if i % 4 == 0:
                    future = executor.submit(run_biology_iteration, loops["biology"])
                elif i % 4 == 1:
                    future = executor.submit(run_chemistry_iteration, loops["chemistry"])
                elif i % 4 == 2:
                    future = executor.submit(run_quantum_iteration, loops["quantum"])
                else:
                    future = executor.submit(run_mathematics_iteration, loops["mathematics"])
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error = future.result()
                metrics.record_iteration(duration, success, error)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 75.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 0.5, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["memory_stats"]["max_mb"] <= 1200, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Mixed Loops Concurrent Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
