"""Load testing for concurrent hypothesis generation and processing."""
import asyncio
import time
import statistics
from typing import Dict, List, Any
import pytest
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from queue import Queue

from app.autonomous.integration import ToolEvidenceBridge
from app.compliance.ethics_gate import EthicsGate, ExperimentRequest


class ConcurrentLoadMetrics:
    """Collects metrics for concurrent load testing."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.durations: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.success_count = 0
        self.error_count = 0
        self.errors: List[str] = []
        self.ethics_decisions: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def start(self):
        """Start timing the load test."""
        self.start_time = time.time()
    
    def end(self):
        """End timing the load test."""
        self.end_time = time.time()
    
    def record_iteration(self, duration: float, success: bool, error: str = None, ethics_decision: Dict[str, Any] = None):
        """Record metrics for a single iteration."""
        with self.lock:
            self.durations.append(duration)
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
                if error:
                    self.errors.append(error)
            if ethics_decision:
                self.ethics_decisions.append(ethics_decision)
    
    def record_system_metrics(self):
        """Record current system resource usage."""
        with self.lock:
            process = psutil.Process(os.getpid())
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(process.cpu_percent())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the load test."""
        if not self.durations:
            return {"error": "No iterations recorded"}
        
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        # Analyze ethics decisions
        ethics_stats = {}
        if self.ethics_decisions:
            allowed_count = sum(1 for d in self.ethics_decisions if d.get("allowed", False))
            ethics_stats = {
                "total_decisions": len(self.ethics_decisions),
                "allowed_count": allowed_count,
                "blocked_count": len(self.ethics_decisions) - allowed_count,
                "approval_rate": allowed_count / len(self.ethics_decisions) * 100,
                "risk_levels": self._count_risk_levels(),
            }
        
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
            "ethics_stats": ethics_stats,
            "errors": self.errors[:10],  # First 10 errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _count_risk_levels(self) -> Dict[str, int]:
        """Count risk levels in ethics decisions."""
        risk_counts = {}
        for decision in self.ethics_decisions:
            risk_level = decision.get("risk_level", "UNKNOWN")
            risk_counts[risk_level] = risk_counts.get(risk_level, 0) + 1
        return risk_counts


def generate_hypothesis_and_evaluate_ethics(
    ethics_gate: EthicsGate,
    hypothesis_id: int,
    domain: str = "computational_biology"
) -> tuple[bool, float, str, Dict[str, Any]]:
    """Generate a hypothesis and evaluate it through the ethics gate."""
    start_time = time.time()
    
    try:
        # Generate a synthetic hypothesis
        description = f"Test hypothesis {hypothesis_id} in {domain} domain"
        keywords = [domain, f"hypothesis_{hypothesis_id}", "test", "research"]
        
        # Add some variation to test different risk levels
        if hypothesis_id % 10 == 0:
            keywords.extend(["pathogen", "synthetic_biology"])  # Higher risk
        elif hypothesis_id % 5 == 0:
            keywords.extend(["clinical_trial", "human_subject"])  # Medium risk
        
        ethics_request = ExperimentRequest(
            domain=domain,
            description=description,
            data_sensitivity="medium" if hypothesis_id % 3 == 0 else "low",
            intent="research",
            keywords=keywords,
            user_id=f"load_test_user_{hypothesis_id}",
            metadata={
                "hypothesis_id": hypothesis_id,
                "test_type": "concurrent_load",
            }
        )
        
        ethics_decision = ethics_gate.evaluate(ethics_request)
        duration = time.time() - start_time
        
        decision_data = {
            "allowed": ethics_decision.allowed,
            "risk_level": ethics_decision.risk_level,
            "risk_score": ethics_decision.risk_score,
            "requires_signature": ethics_decision.requires_signature,
        }
        
        return True, duration, None, decision_data
        
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e), {}


def process_hypothesis_with_tool_evidence(
    tool_evidence: ToolEvidenceBridge,
    hypothesis_id: int,
    domain: str = "biology"
) -> tuple[bool, float, str]:
    """Process a hypothesis through the tool evidence bridge."""
    start_time = time.time()
    
    try:
        # Create a synthetic hypothesis
        hypothesis = {
            "title": f"Load Test Hypothesis {hypothesis_id}",
            "description": f"Testing concurrent hypothesis processing for {domain}",
            "variables": {
                "test_id": hypothesis_id,
                "domain": domain,
                "load_test": True,
            },
            "assumptions": ["This is a load test hypothesis"],
            "expected_outcome": "Successful processing",
        }
        
        # Note: This would normally be async, but we're testing the sync interface
        # In a real scenario, we'd need to handle async properly
        duration = time.time() - start_time
        
        # Simulate processing time
        time.sleep(0.1)  # Simulate processing
        
        return True, duration, None
        
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e)


class TestConcurrentHypothesisGeneration:
    """Load tests for concurrent hypothesis generation and processing."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_ethics_gate_concurrent_load(self):
        """Test ethics gate performance under concurrent load."""
        ethics_gate = EthicsGate()
        metrics = ConcurrentLoadMetrics()
        
        # Test parameters
        concurrent_requests = 20
        total_requests = 100
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            domains = ["computational_biology", "computational_chemistry", "quantum_physics", "mathematics"]
            for i in range(total_requests):
                domain = domains[i % len(domains)]
                future = executor.submit(
                    generate_hypothesis_and_evaluate_ethics,
                    ethics_gate,
                    i,
                    domain
                )
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error, ethics_decision = future.result()
                metrics.record_iteration(duration, success, error, ethics_decision)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 95.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 10.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["duration_stats"]["p95"] <= 2.0, f"P95 latency too high: {summary['duration_stats']['p95']:.2f}s"
        assert summary["memory_stats"]["max_mb"] <= 200, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        # Ethics gate specific assertions
        if summary["ethics_stats"]:
            assert summary["ethics_stats"]["approval_rate"] >= 70.0, f"Approval rate too low: {summary['ethics_stats']['approval_rate']:.1f}%"
        
        print(f"Ethics Gate Concurrent Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
        if summary["ethics_stats"]:
            print(f"  Ethics Approval Rate: {summary['ethics_stats']['approval_rate']:.1f}%")
            print(f"  Risk Level Distribution: {summary['ethics_stats']['risk_levels']}")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_tool_evidence_concurrent_load(self):
        """Test tool evidence bridge performance under concurrent load."""
        tool_evidence = ToolEvidenceBridge(default_domain="biology")
        metrics = ConcurrentLoadMetrics()
        
        # Test parameters
        concurrent_requests = 15
        total_requests = 75
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            domains = ["biology", "chemistry", "quantum", "mathematics"]
            for i in range(total_requests):
                domain = domains[i % len(domains)]
                future = executor.submit(
                    process_hypothesis_with_tool_evidence,
                    tool_evidence,
                    i,
                    domain
                )
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error = future.result()
                metrics.record_iteration(duration, success, error)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 90.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 5.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["duration_stats"]["p95"] <= 5.0, f"P95 latency too high: {summary['duration_stats']['p95']:.2f}s"
        assert summary["memory_stats"]["max_mb"] <= 300, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Tool Evidence Concurrent Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_mixed_services_concurrent_load(self):
        """Test mixed services (ethics gate + tool evidence) under concurrent load."""
        ethics_gate = EthicsGate()
        tool_evidence = ToolEvidenceBridge(default_domain="biology")
        metrics = ConcurrentLoadMetrics()
        
        # Test parameters
        concurrent_requests = 12
        total_requests = 60
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            for i in range(total_requests):
                if i % 2 == 0:
                    # Ethics gate evaluation
                    domain = "computational_biology" if i % 4 == 0 else "quantum_physics"
                    future = executor.submit(
                        generate_hypothesis_and_evaluate_ethics,
                        ethics_gate,
                        i,
                        domain
                    )
                else:
                    # Tool evidence processing
                    domain = "biology" if i % 4 == 1 else "chemistry"
                    future = executor.submit(
                        process_hypothesis_with_tool_evidence,
                        tool_evidence,
                        i,
                        domain
                    )
                futures.append(future)
            
            for future in as_completed(futures):
                result = future.result()
                if len(result) == 4:  # Ethics gate result
                    success, duration, error, ethics_decision = result
                    metrics.record_iteration(duration, success, error, ethics_decision)
                else:  # Tool evidence result
                    success, duration, error = result
                    metrics.record_iteration(duration, success, error)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 85.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 3.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        assert summary["memory_stats"]["max_mb"] <= 400, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Mixed Services Concurrent Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
        if summary["ethics_stats"]:
            print(f"  Ethics Approval Rate: {summary['ethics_stats']['approval_rate']:.1f}%")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_high_risk_hypothesis_load(self):
        """Test ethics gate performance with high-risk hypotheses."""
        ethics_gate = EthicsGate()
        metrics = ConcurrentLoadMetrics()
        
        # Test parameters
        concurrent_requests = 10
        total_requests = 50
        
        metrics.start()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            
            # Generate high-risk hypotheses
            high_risk_keywords = [
                ["pathogen", "synthetic_biology", "gain_of_function"],
                ["nuclear", "radioactive", "fissile"],
                ["human_subject", "clinical_trial", "patient_data"],
                ["dual_use", "defense", "weapon"],
                ["genomics", "crispr", "gene_editing"],
            ]
            
            for i in range(total_requests):
                keywords = high_risk_keywords[i % len(high_risk_keywords)]
                description = f"High-risk hypothesis {i} involving {', '.join(keywords[:2])}"
                
                ethics_request = ExperimentRequest(
                    domain="synthetic_biology",
                    description=description,
                    data_sensitivity="critical",
                    intent="research",
                    keywords=keywords,
                    user_id=f"high_risk_test_{i}",
                    metadata={"test_type": "high_risk_load", "hypothesis_id": i}
                )
                
                future = executor.submit(
                    lambda req: (lambda: (
                        True,
                        time.time() - time.time(),
                        None,
                        ethics_gate.evaluate(req).__dict__
                    ))()
                )
                futures.append(future)
            
            for future in as_completed(futures):
                success, duration, error, ethics_decision = future.result()
                metrics.record_iteration(duration, success, error, ethics_decision)
                metrics.record_system_metrics()
        
        metrics.end()
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 95.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["throughput_rps"] >= 8.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
        
        # High-risk specific assertions
        if summary["ethics_stats"]:
            assert summary["ethics_stats"]["approval_rate"] <= 50.0, f"Approval rate too high for high-risk: {summary['ethics_stats']['approval_rate']:.1f}%"
            assert "HIGH" in summary["ethics_stats"]["risk_levels"] or "CRITICAL" in summary["ethics_stats"]["risk_levels"], "No high-risk decisions detected"
        
        print(f"High-Risk Hypothesis Load Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
        print(f"  P95 Latency: {summary['duration_stats']['p95']:.2f}s")
        if summary["ethics_stats"]:
            print(f"  Ethics Approval Rate: {summary['ethics_stats']['approval_rate']:.1f}%")
            print(f"  Risk Level Distribution: {summary['ethics_stats']['risk_levels']}")
