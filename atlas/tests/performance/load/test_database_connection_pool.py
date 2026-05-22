"""Load testing for database connection pool performance."""
import asyncio
import time
import statistics
from typing import Dict, List, Any
import pytest
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import sqlite3
from contextlib import contextmanager

from app.compliance.ethics_decision_store import EthicsDecisionStore


class DatabaseLoadMetrics:
    """Collects metrics for database load testing."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.durations: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.success_count = 0
        self.error_count = 0
        self.errors: List[str] = []
        self.connection_times: List[float] = []
        self.query_times: List[float] = []
        self.lock = threading.Lock()
    
    def start(self):
        """Start timing the load test."""
        self.start_time = time.time()
    
    def end(self):
        """End timing the load test."""
        self.end_time = time.time()
    
    def record_iteration(self, duration: float, success: bool, error: str = None, 
                        connection_time: float = None, query_time: float = None):
        """Record metrics for a single iteration."""
        with self.lock:
            self.durations.append(duration)
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
                if error:
                    self.errors.append(error)
            if connection_time is not None:
                self.connection_times.append(connection_time)
            if query_time is not None:
                self.query_times.append(query_time)
    
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
        
        summary = {
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
        
        if self.connection_times:
            summary["connection_stats"] = {
                "mean_ms": statistics.mean(self.connection_times) * 1000,
                "p95_ms": self._percentile(self.connection_times, 95) * 1000,
                "max_ms": max(self.connection_times) * 1000,
            }
        
        if self.query_times:
            summary["query_stats"] = {
                "mean_ms": statistics.mean(self.query_times) * 1000,
                "p95_ms": self._percentile(self.query_times, 95) * 1000,
                "max_ms": max(self.query_times) * 1000,
            }
        
        return summary
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


@contextmanager
def temp_database():
    """Create a temporary database for testing."""
    import tempfile
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name
    
    try:
        yield db_path
    finally:
        try:
            os.unlink(db_path)
        except OSError:
            pass


def test_database_connection(db_path: str) -> tuple[bool, float, str, float, float]:
    """Test database connection and basic operations."""
    start_time = time.time()
    connection_time = 0
    query_time = 0
    
    try:
        # Test connection
        conn_start = time.time()
        conn = sqlite3.connect(db_path)
        connection_time = time.time() - conn_start
        
        # Test basic query
        query_start = time.time()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        query_time = time.time() - query_start
        
        conn.close()
        duration = time.time() - start_time
        
        return True, duration, None, connection_time, query_time
        
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e), connection_time, query_time


def test_ethics_decision_store_operations(store: EthicsDecisionStore, operation_id: int) -> tuple[bool, float, str]:
    """Test ethics decision store operations."""
    start_time = time.time()
    
    try:
        from app.compliance.ethics_gate import ExperimentRequest
        
        # Create a test request
        request = ExperimentRequest(
            domain="computational_biology",
            description=f"Load test experiment {operation_id}",
            data_sensitivity="low",
            intent="research",
            keywords=["load_test", f"experiment_{operation_id}"],
            user_id=f"load_test_user_{operation_id}",
            metadata={"test_id": operation_id}
        )
        
        # Test store operation
        decision = store.store_decision(
            request=request,
            decision_id=f"test_decision_{operation_id}",
            risk_level="LOW",
            risk_score=2.0,
            allowed=True,
            requires_signature=False,
            escalation_reasons=[],
            recommended_actions=[]
        )
        
        # Test retrieval
        retrieved = store.get_decision(f"test_decision_{operation_id}")
        assert retrieved is not None
        
        # Test statistics
        stats = store.get_statistics()
        assert stats is not None
        
        duration = time.time() - start_time
        return True, duration, None
        
    except Exception as e:
        duration = time.time() - start_time
        return False, duration, str(e)


class TestDatabaseConnectionPool:
    """Load tests for database connection pool performance."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_sqlite_connection_pool_load(self):
        """Test SQLite connection performance under load."""
        with temp_database() as db_path:
            # Initialize database
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, data TEXT)")
            conn.commit()
            conn.close()
            
            metrics = DatabaseLoadMetrics()
            
            # Test parameters
            concurrent_connections = 20
            total_connections = 100
            
            metrics.start()
            
            with ThreadPoolExecutor(max_workers=concurrent_connections) as executor:
                futures = []
                
                for i in range(total_connections):
                    future = executor.submit(test_database_connection, db_path)
                    futures.append(future)
                
                for future in as_completed(futures):
                    success, duration, error, conn_time, query_time = future.result()
                    metrics.record_iteration(duration, success, error, conn_time, query_time)
                    metrics.record_system_metrics()
            
            metrics.end()
            summary = metrics.get_summary()
            
            # Assertions
            assert summary["success_rate"] >= 95.0, f"Success rate too low: {summary['success_rate']:.1f}%"
            assert summary["throughput_rps"] >= 50.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
            assert summary["duration_stats"]["p95"] <= 0.1, f"P95 latency too high: {summary['duration_stats']['p95']:.3f}s"
            assert summary["memory_stats"]["max_mb"] <= 100, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
            
            if "connection_stats" in summary:
                assert summary["connection_stats"]["p95_ms"] <= 10.0, f"Connection time too high: {summary['connection_stats']['p95_ms']:.1f}ms"
            
            print(f"SQLite Connection Pool Load Test Results:")
            print(f"  Success Rate: {summary['success_rate']:.1f}%")
            print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
            print(f"  P95 Latency: {summary['duration_stats']['p95']:.3f}s")
            print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
            if "connection_stats" in summary:
                print(f"  P95 Connection Time: {summary['connection_stats']['p95_ms']:.1f}ms")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_ethics_decision_store_load(self):
        """Test ethics decision store performance under load."""
        with temp_database() as db_path:
            store = EthicsDecisionStore(db_path=db_path)
            metrics = DatabaseLoadMetrics()
            
            # Test parameters
            concurrent_operations = 15
            total_operations = 75
            
            metrics.start()
            
            with ThreadPoolExecutor(max_workers=concurrent_operations) as executor:
                futures = []
                
                for i in range(total_operations):
                    future = executor.submit(test_ethics_decision_store_operations, store, i)
                    futures.append(future)
                
                for future in as_completed(futures):
                    success, duration, error = future.result()
                    metrics.record_iteration(duration, success, error)
                    metrics.record_system_metrics()
            
            metrics.end()
            summary = metrics.get_summary()
            
            # Assertions
            assert summary["success_rate"] >= 90.0, f"Success rate too low: {summary['success_rate']:.1f}%"
            assert summary["throughput_rps"] >= 10.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
            assert summary["duration_stats"]["p95"] <= 1.0, f"P95 latency too high: {summary['duration_stats']['p95']:.3f}s"
            assert summary["memory_stats"]["max_mb"] <= 150, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
            
            print(f"Ethics Decision Store Load Test Results:")
            print(f"  Success Rate: {summary['success_rate']:.1f}%")
            print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
            print(f"  P95 Latency: {summary['duration_stats']['p95']:.3f}s")
            print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_read_write_operations(self):
        """Test concurrent read and write operations on database."""
        with temp_database() as db_path:
            store = EthicsDecisionStore(db_path=db_path)
            metrics = DatabaseLoadMetrics()
            
            # Test parameters
            concurrent_operations = 12
            total_operations = 60
            
            metrics.start()
            
            with ThreadPoolExecutor(max_workers=concurrent_operations) as executor:
                futures = []
                
                for i in range(total_operations):
                    if i % 3 == 0:
                        # Write operation
                        future = executor.submit(test_ethics_decision_store_operations, store, i)
                    else:
                        # Read operation (simulate by creating and immediately retrieving)
                        future = executor.submit(test_ethics_decision_store_operations, store, i)
                    futures.append(future)
                
                for future in as_completed(futures):
                    success, duration, error = future.result()
                    metrics.record_iteration(duration, success, error)
                    metrics.record_system_metrics()
            
            metrics.end()
            summary = metrics.get_summary()
            
            # Assertions
            assert summary["success_rate"] >= 85.0, f"Success rate too low: {summary['success_rate']:.1f}%"
            assert summary["throughput_rps"] >= 8.0, f"Throughput too low: {summary['throughput_rps']:.2f} RPS"
            assert summary["memory_stats"]["max_mb"] <= 200, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
            
            print(f"Concurrent Read/Write Operations Test Results:")
            print(f"  Success Rate: {summary['success_rate']:.1f}%")
            print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
            print(f"  P95 Latency: {summary['duration_stats']['p95']:.3f}s")
            print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_database_memory_usage_under_load(self):
        """Test database memory usage under sustained load."""
        with temp_database() as db_path:
            store = EthicsDecisionStore(db_path=db_path)
            metrics = DatabaseLoadMetrics()
            
            # Test parameters - sustained load
            concurrent_operations = 8
            total_operations = 200  # More operations to test memory stability
            
            metrics.start()
            
            with ThreadPoolExecutor(max_workers=concurrent_operations) as executor:
                futures = []
                
                for i in range(total_operations):
                    future = executor.submit(test_ethics_decision_store_operations, store, i)
                    futures.append(future)
                
                for future in as_completed(futures):
                    success, duration, error = future.result()
                    metrics.record_iteration(duration, success, error)
                    metrics.record_system_metrics()
            
            metrics.end()
            summary = metrics.get_summary()
            
            # Assertions
            assert summary["success_rate"] >= 80.0, f"Success rate too low: {summary['success_rate']:.1f}%"
            assert summary["memory_stats"]["max_mb"] <= 300, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
            
            # Check for memory leaks (max should not be significantly higher than mean)
            memory_ratio = summary["memory_stats"]["max_mb"] / summary["memory_stats"]["mean_mb"] if summary["memory_stats"]["mean_mb"] > 0 else 1
            assert memory_ratio <= 3.0, f"Potential memory leak detected: max/mean ratio = {memory_ratio:.2f}"
            
            print(f"Database Memory Usage Under Load Test Results:")
            print(f"  Success Rate: {summary['success_rate']:.1f}%")
            print(f"  Throughput: {summary['throughput_rps']:.2f} RPS")
            print(f"  Mean Memory: {summary['memory_stats']['mean_mb']:.1f}MB")
            print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
            print(f"  Memory Ratio: {memory_ratio:.2f}")
