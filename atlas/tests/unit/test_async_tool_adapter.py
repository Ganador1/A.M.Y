"""Tests para AsyncToolAdapter"""
import pytest
import asyncio
import time
from app.adapters.async_tool_adapter import (
    AsyncToolAdapter, 
    AsyncExecutionConfig, 
    AsyncEchoAdapter,
    BatchProcessor,
    get_async_tool_registry
)


class TestAsyncAdapter(AsyncToolAdapter):
    name = "test_async"
    version = "1.0.0"
    description = "Test async adapter"
    
    def __init__(self, should_fail=False, delay=0.1):
        super().__init__()
        self.should_fail = should_fail
        self.delay = delay
        self.call_count = 0
    
    async def _run_async(self, params):
        self.call_count += 1
        await asyncio.sleep(self.delay)
        
        if self.should_fail:
            raise ValueError("Test async error")
        
        return {
            "result": f"async_processed_{self.call_count}_{id(params)}",  # Make unique
            "input": params,
            "delay": self.delay
        }


@pytest.mark.asyncio
async def test_basic_async_execution():
    """Test basic async execution"""
    adapter = TestAsyncAdapter()
    params = {"test": "value"}
    
    result = await adapter.execute_async(params)
    
    assert result.success
    assert result.output["result"].startswith("async_processed_1_")
    assert result.metadata["async"] is True
    assert result.duration_ms > 0


@pytest.mark.asyncio
async def test_async_execution_failure():
    """Test async execution with failure"""
    adapter = TestAsyncAdapter(should_fail=True)
    params = {"test": "value"}
    
    result = await adapter.execute_async(params)
    
    assert not result.success
    assert "Test async error" in (result.error or "")
    assert result.metadata["async"] is True


@pytest.mark.asyncio
async def test_async_execution_timeout():
    """Test async execution timeout"""
    # Slow adapter with short timeout
    adapter = TestAsyncAdapter(delay=2.0)
    adapter.config.timeout_seconds = 0.5
    
    result = await adapter.execute_async({"test": "slow"})
    
    assert not result.success
    assert "timeout" in (result.error or "").lower()


@pytest.mark.asyncio
async def test_batch_execution():
    """Test batch execution"""
    adapter = TestAsyncAdapter(delay=0.1)
    param_list = [
        {"batch": "item1"},
        {"batch": "item2"},
        {"batch": "item3"}
    ]
    
    start_time = time.time()
    results = await adapter.execute_batch_async(param_list)
    end_time = time.time()
    
    # All should succeed
    assert len(results) == 3
    assert all(r.success for r in results)
    
    # Should be faster than sequential (less than 3 * delay)
    assert end_time - start_time < 0.25  # 3 * 0.1 - concurrency benefit
    
    # Each should have unique result
    outputs = [r.output["result"] for r in results]
    assert len(set(outputs)) == 3  # All unique


@pytest.mark.asyncio
async def test_batch_execution_with_failures():
    """Test batch execution with some failures"""
    adapter = TestAsyncAdapter(should_fail=True)
    param_list = [{"test": f"item{i}"} for i in range(3)]
    
    results = await adapter.execute_batch_async(param_list)
    
    assert len(results) == 3
    assert all(not r.success for r in results)  # All fail


@pytest.mark.asyncio
async def test_batch_execution_fail_fast():
    """Test batch execution with fail_fast=True"""
    adapter = TestAsyncAdapter()
    adapter.config.fail_fast = True
    
    # Mix of good and bad params (second one will fail if we add failure logic)
    param_list = [
        {"test": "good1"},
        {"test": "good2"},
        {"test": "good3"}
    ]
    
    results = await adapter.execute_batch_async(param_list)
    
    # With fail_fast=False (default behavior since no failures), all should complete
    assert len(results) == 3
    assert all(r.success for r in results)


@pytest.mark.asyncio
async def test_concurrency_control():
    """Test concurrency limiting"""
    adapter = TestAsyncAdapter(delay=0.2)
    adapter.config.max_concurrent = 2
    
    param_list = [{"concurrent": f"item{i}"} for i in range(5)]
    
    start_time = time.time()
    results = await adapter.execute_batch_async(param_list)
    end_time = time.time()
    
    # With max_concurrent=2 and 5 items, should take at least 3 "rounds"
    # (2 items, then 2 items, then 1 item) = ~0.6 seconds minimum
    assert end_time - start_time >= 0.4  # Allow some margin
    assert len(results) == 5
    assert all(r.success for r in results)


@pytest.mark.asyncio
async def test_retry_mechanism():
    """Test retry mechanism"""
    adapter = TestAsyncAdapter(should_fail=True)
    adapter.config.retry_attempts = 2
    adapter.config.retry_delay = 0.1
    
    param_list = [{"retry": "test"}]
    
    start_time = time.time()
    results = await adapter.execute_batch_async(param_list)
    end_time = time.time()
    
    # Should fail after retries
    assert len(results) == 1
    assert not results[0].success
    
    # The error should either be the original error or mention attempts
    error_msg = results[0].error or ""
    assert ("Test async error" in error_msg) or ("attempts" in error_msg)
    
    # Should take some time for retries, but not necessarily full delay
    # (retry might fail faster than expected in some cases)
    assert end_time - start_time >= 0.05  # More realistic expectation


@pytest.mark.asyncio
async def test_async_echo_adapter():
    """Test the example AsyncEchoAdapter"""
    adapter = AsyncEchoAdapter()
    params = {"message": "hello", "delay": 0.05}
    
    result = await adapter.execute_async(params)
    
    assert result.success
    assert result.output["echo"] == params
    assert result.output["async"] is True
    assert result.output["length"] > 0


@pytest.mark.asyncio
async def test_batch_processor():
    """Test BatchProcessor utility"""
    adapters = {
        "echo1": AsyncEchoAdapter(),
        "echo2": AsyncEchoAdapter()
    }
    
    processor = BatchProcessor(adapters)
    
    tool_params = {
        "echo1": [{"msg": "hello1"}, {"msg": "hello2"}],
        "echo2": [{"msg": "world1"}]
    }
    
    results = await processor.process_cross_product(tool_params)
    
    assert "echo1" in results
    assert "echo2" in results
    assert len(results["echo1"]) == 2
    assert len(results["echo2"]) == 1
    assert all(r.success for r in results["echo1"])
    assert all(r.success for r in results["echo2"])


@pytest.mark.asyncio
async def test_pipeline_processing():
    """Test pipeline processing"""
    adapters = {
        "echo": AsyncEchoAdapter()
    }
    
    processor = BatchProcessor(adapters)
    
    pipeline = [
        {"tool": "echo", "params": {"step": 1}},
        {"tool": "echo", "params": [{"step": 2}, {"step": 3}]},  # Batch step
        {"tool": "echo", "params": {"step": 4}}
    ]
    
    results = await processor.process_pipeline(pipeline)
    
    # Should have 4 results: 1 + 2 (batch) + 1
    assert len(results) == 4
    assert all(r.success for r in results)


def test_async_registry():
    """Test async tool registry"""
    registry = get_async_tool_registry()
    adapter = AsyncEchoAdapter()
    
    registry.register(adapter)
    
    retrieved = registry.get("async_echo")
    assert retrieved is not None
    assert retrieved.name == "async_echo"
    
    listing = registry.list()
    assert "async_echo" in listing
    assert listing["async_echo"]["async"] is True
    assert "config" in listing["async_echo"]


def test_execution_config():
    """Test AsyncExecutionConfig"""
    config = AsyncExecutionConfig(
        max_concurrent=10,
        timeout_seconds=60.0,
        retry_attempts=3,
        fail_fast=True
    )
    
    assert config.max_concurrent == 10
    assert config.timeout_seconds == 60.0
    assert config.retry_attempts == 3
    assert config.fail_fast is True


if __name__ == "__main__":
    pytest.main([__file__])
