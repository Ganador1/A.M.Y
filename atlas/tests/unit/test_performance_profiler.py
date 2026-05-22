#!/usr/bin/env python3
"""
Unit tests for AXIOM Performance Profiler Service
"""

import pytest
import time
import threading
from unittest.mock import patch
from app.performance_profiler import PerformanceProfiler

class TestPerformanceProfiler:
    """Test cases for PerformanceProfiler"""

    @pytest.fixture
    def profiler(self):
        """Create a test profiler instance"""
        return PerformanceProfiler()

    def test_profiler_initialization(self, profiler):
        """Test profiler initialization"""
        assert profiler.metrics == {}
        assert profiler.active_profilers == {}
        assert profiler.lock is not None

    def test_context_manager_profiling(self, profiler):
        """Test context manager profiling"""
        with profiler.profile_operation("test_operation") as operation_id:
            assert operation_id is not None
            time.sleep(0.01)  # Small delay

        # Check that operation was recorded
        assert "test_operation" in profiler.metrics
        assert len(profiler.metrics["test_operation"]) == 1

        operation_data = profiler.metrics["test_operation"][0]
        assert operation_data["operation"] == "test_operation"
        assert "duration" in operation_data
        assert "memory_delta" in operation_data
        assert operation_data["completed"] is True

    def test_function_decorator(self, profiler):
        """Test function decorator profiling"""
        @profiler.profile_function("decorated_function")
        def test_function(x, y):
            time.sleep(0.01)
            return x + y

        result = test_function(5, 3)
        assert result == 8

        # Check profiling data
        assert "decorated_function" in profiler.metrics
        assert len(profiler.metrics["decorated_function"]) == 1

    def test_automatic_function_naming(self, profiler):
        """Test automatic function naming in decorator"""
        @profiler.profile_function()
        def another_test_function():
            return "test"

        result = another_test_function()
        assert result == "test"

        # Should use module + function name
        expected_name = f"{another_test_function.__module__}.{another_test_function.__name__}"
        assert expected_name in profiler.metrics

    def test_operation_stats(self, profiler):
        """Test operation statistics calculation"""
        # Add some test data
        profiler.metrics["test_op"] = [
            {
                "duration": 0.1,
                "memory_delta": 10.0,
                "cpu_usage": 5.0,
                "completed": True
            },
            {
                "duration": 0.2,
                "memory_delta": 20.0,
                "cpu_usage": 10.0,
                "completed": True
            }
        ]

        stats = profiler.get_operation_stats("test_op")

        assert stats["total_calls"] == 2
        assert stats["avg_duration"] == 0.15
        assert stats["min_duration"] == 0.1
        assert stats["max_duration"] == 0.2
        assert stats["avg_memory_delta"] == 15.0
        assert stats["max_memory_delta"] == 20.0
        assert stats["avg_cpu_usage"] == 7.5

    def test_operation_stats_no_data(self, profiler):
        """Test operation stats with no data"""
        stats = profiler.get_operation_stats("nonexistent")

        assert "error" in stats
        assert "No data" in stats["error"]

    def test_all_stats(self, profiler):
        """Test getting all operation statistics"""
        # Add test data for multiple operations
        profiler.metrics["op1"] = [{"duration": 0.1, "memory_delta": 5.0, "cpu_usage": 2.0, "completed": True}]
        profiler.metrics["op2"] = [{"duration": 0.2, "memory_delta": 10.0, "cpu_usage": 4.0, "completed": True}]

        all_stats = profiler.get_all_stats()

        assert "op1" in all_stats
        assert "op2" in all_stats
        assert all_stats["op1"]["total_calls"] == 1
        assert all_stats["op2"]["total_calls"] == 1

    def test_performance_report_generation(self, profiler):
        """Test performance report generation"""
        # Add test data
        profiler.metrics["fast_operation"] = [
            {"duration": 0.01, "memory_delta": 1.0, "cpu_usage": 1.0, "completed": True}
        ]
        profiler.metrics["slow_operation"] = [
            {"duration": 2.0, "memory_delta": 50.0, "cpu_usage": 20.0, "completed": True}
        ]

        report = profiler.get_performance_report()

        assert "🚀 AXIOM Performance Report" in report
        assert "fast_operation" in report
        assert "slow_operation" in report
        assert "💡 Performance Recommendations" in report
        assert "Consider optimization" in report  # For slow_operation

    def test_concurrent_profiling(self, profiler):
        """Test concurrent profiling operations"""
        results = []

        def worker_operation(worker_id):
            with profiler.profile_operation(f"worker_{worker_id}"):
                time.sleep(0.01)
                results.append(worker_id)

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker_operation, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check results
        assert len(results) == 5
        assert set(results) == {0, 1, 2, 3, 4}

        # Check profiling data
        for i in range(5):
            assert f"worker_{i}" in profiler.metrics
            assert len(profiler.metrics[f"worker_{i}"]) == 1

    def test_memory_and_cpu_tracking(self, profiler):
        """Test memory and CPU usage tracking"""
        with profiler.profile_operation("resource_test"):
            # Consume some memory
            _ = [0] * 10000
            time.sleep(0.01)

        operation_data = profiler.metrics["resource_test"][0]

        # Should have tracked memory and CPU
        assert "start_memory" in operation_data
        assert "end_memory" in operation_data
        assert "memory_delta" in operation_data
        assert "start_cpu" in operation_data
        assert "end_cpu" in operation_data
        assert "cpu_usage" in operation_data

    def test_metadata_storage(self, profiler):
        """Test metadata storage in profiling"""
        metadata = {"user": "test_user", "request_id": "12345"}

        with profiler.profile_operation("metadata_test", metadata):
            pass

        operation_data = profiler.metrics["metadata_test"][0]
        assert operation_data["metadata"] == metadata

    def test_active_profilers_tracking(self, profiler):
        """Test tracking of active profilers"""
        with profiler.profile_operation("active_test") as op_id:
            # Check that profiler is marked as active
            assert op_id in profiler.active_profilers
            assert profiler.active_profilers[op_id]["operation"] == "active_test"

        # Should be removed after context
        assert op_id not in profiler.active_profilers

    def test_metrics_cleanup(self, profiler):
        """Test metrics cleanup"""
        # Add some test data
        profiler.metrics["test_cleanup"] = [{"duration": 0.1, "completed": True}]

        # Clear metrics
        profiler.clear_metrics()

        assert profiler.metrics == {}
        assert profiler.active_profilers == {}

    @patch('psutil.Process')
    def test_error_handling(self, mock_process, profiler):
        """Test error handling in profiling"""
        # Mock psutil to raise exception
        mock_process.return_value.memory_info.side_effect = Exception("Test error")

        # Should not raise exception
        with profiler.profile_operation("error_test"):
            pass

        # Should still record the operation
        assert "error_test" in profiler.metrics

    def test_p95_calculation(self, profiler):
        """Test 95th percentile calculation"""
        # Add multiple duration values
        durations = [0.1, 0.2, 0.3, 0.4, 0.5]
        profiler.metrics["p95_test"] = [
            {"duration": d, "memory_delta": 0, "cpu_usage": 0, "completed": True}
            for d in durations
        ]

        stats = profiler.get_operation_stats("p95_test")

        # P95 should be the 95th percentile (5th value in sorted list)
        assert stats["p95_duration"] == 0.5

if __name__ == "__main__":
    pytest.main([__file__])
