#!/usr/bin/env python3
"""
Unit tests for AXIOM Async Processor Service
"""

import pytest
import asyncio
import time
from app.async_processor import AdvancedAsyncProcessor

class TestAdvancedAsyncProcessor:
    """Test cases for AdvancedAsyncProcessor"""

    @pytest.fixture
    def async_processor(self):
        """Create a test async processor instance"""
        return AdvancedAsyncProcessor()

    def test_async_processor_initialization(self, async_processor):
        """Test async processor initialization"""
        assert async_processor.executor is not None
        assert async_processor.workers is not None
        assert len(async_processor.workers) == 4  # Default 4 pools
        assert async_processor.metrics is not None

    def test_worker_pool_creation(self, async_processor):
        """Test worker pool creation"""
        # Check that all worker pools are created
        for pool_name, pool in async_processor.workers.items():
            assert pool is not None
            assert hasattr(pool, 'submit')

        # Check pool names
        expected_pools = ['cpu_intensive', 'io_bound', 'gpu_accelerated', 'scientific']
        assert set(async_processor.workers.keys()) == set(expected_pools)

    @pytest.mark.asyncio
    async def test_async_task_submission(self, async_processor):
        """Test async task submission"""
        # Simple test function
        def test_function(x, y):
            return x + y

        # Submit task
        task_id = await async_processor.submit_async_task(
            test_function,
            args=(5, 3),
            pool_name='cpu_intensive'
        )

        assert task_id is not None
        assert isinstance(task_id, str)

        # Wait for result
        result = await async_processor.get_task_result(task_id)
        assert result == 8

    @pytest.mark.asyncio
    async def test_task_with_kwargs(self, async_processor):
        """Test task submission with keyword arguments"""
        def test_function(x, y=10, multiplier=2):
            return (x + y) * multiplier

        task_id = await async_processor.submit_async_task(
            test_function,
            args=(5,),
            kwargs={'y': 3, 'multiplier': 4},
            pool_name='cpu_intensive'
        )

        result = await async_processor.get_task_result(task_id)
        assert result == 32  # (5 + 3) * 4

    @pytest.mark.asyncio
    async def test_multiple_pools(self, async_processor):
        """Test task distribution across different pools"""
        results = {}

        # Submit tasks to different pools
        for pool_name in async_processor.workers.keys():
            task_id = await async_processor.submit_async_task(
                lambda x: f"result_from_{x}",
                args=(pool_name,),
                pool_name=pool_name
            )
            results[pool_name] = task_id

        # Get results from all pools
        for pool_name, task_id in results.items():
            result = await async_processor.get_task_result(task_id)
            assert result == f"result_from_{pool_name}"

    @pytest.mark.asyncio
    async def test_task_timeout(self, async_processor):
        """Test task timeout handling"""
        def slow_function():
            time.sleep(2)  # Sleep for 2 seconds
            return "done"

        # Submit task with short timeout
        task_id = await async_processor.submit_async_task(
            slow_function,
            timeout=1,  # 1 second timeout
            pool_name='cpu_intensive'
        )

        # Should timeout
        with pytest.raises(asyncio.TimeoutError):
            await async_processor.get_task_result(task_id, timeout=1)

    @pytest.mark.asyncio
    async def test_task_cancellation(self, async_processor):
        """Test task cancellation"""
        def slow_function():
            time.sleep(5)
            return "done"

        task_id = await async_processor.submit_async_task(
            slow_function,
            pool_name='cpu_intensive'
        )

        # Cancel task
        cancelled = await async_processor.cancel_task(task_id)
        assert cancelled is True

        # Should not get result
        with pytest.raises(asyncio.TimeoutError):
            await async_processor.get_task_result(task_id, timeout=0.1)

    def test_task_queue_management(self, async_processor):
        """Test task queue management"""
        # Check initial queue state
        initial_stats = async_processor.get_queue_stats()

        assert 'cpu_intensive' in initial_stats
        assert 'queue_size' in initial_stats['cpu_intensive']
        assert 'active_tasks' in initial_stats['cpu_intensive']

    @pytest.mark.asyncio
    async def test_concurrent_tasks(self, async_processor):
        """Test concurrent task execution"""
        async def run_concurrent_tasks():
            tasks = []
            for i in range(10):
                task_id = await async_processor.submit_async_task(
                    lambda x: x * 2,
                    args=(i,),
                    pool_name='cpu_intensive'
                )
                tasks.append(async_processor.get_task_result(task_id))

            results = await asyncio.gather(*tasks)
            return results

        results = await run_concurrent_tasks()
        expected = [i * 2 for i in range(10)]
        assert results == expected

    def test_performance_metrics(self, async_processor):
        """Test performance metrics collection"""
        initial_metrics = async_processor.get_performance_metrics()

        # Metrics should have expected structure
        assert 'total_tasks' in initial_metrics
        assert 'completed_tasks' in initial_metrics
        assert 'failed_tasks' in initial_metrics
        assert 'average_execution_time' in initial_metrics
        assert 'pool_utilization' in initial_metrics

    @pytest.mark.asyncio
    async def test_error_handling(self, async_processor):
        """Test error handling in tasks"""
        def failing_function():
            raise ValueError("Test error")

        task_id = await async_processor.submit_async_task(
            failing_function,
            pool_name='cpu_intensive'
        )

        # Should get exception
        with pytest.raises(ValueError, match="Test error"):
            await async_processor.get_task_result(task_id)

    @pytest.mark.asyncio
    async def test_task_priorities(self, async_processor):
        """Test task priority handling"""
        # Submit high priority task
        high_priority_id = await async_processor.submit_async_task(
            lambda: "high_priority",
            priority=10,
            pool_name='cpu_intensive'
        )

        # Submit low priority task
        low_priority_id = await async_processor.submit_async_task(
            lambda: "low_priority",
            priority=1,
            pool_name='cpu_intensive'
        )

        # High priority should complete first (in most cases)
        high_result = await async_processor.get_task_result(high_priority_id)
        low_result = await async_processor.get_task_result(low_priority_id)

        assert high_result == "high_priority"
        assert low_result == "low_priority"

    def test_resource_optimization(self, async_processor):
        """Test resource optimization"""
        # Test CPU optimization
        async_processor.optimize_for_workload('cpu_intensive')
        assert async_processor.current_optimization == 'cpu_intensive'

        # Test memory optimization
        async_processor.optimize_for_workload('memory_intensive')
        assert async_processor.current_optimization == 'memory_intensive'

    def test_cleanup(self, async_processor):
        """Test cleanup functionality"""
        # Should not raise exceptions
        async_processor.cleanup()

        # Executor should be shutdown
        assert async_processor.executor is None

if __name__ == "__main__":
    pytest.main([__file__])
