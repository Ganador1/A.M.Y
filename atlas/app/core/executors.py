"""
Async executors for CPU-bound and I/O-bound operations.

This module provides executors to run blocking operations without blocking
the event loop, using process pools for CPU-bound tasks and thread pools
for I/O-bound tasks.
"""

import asyncio
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ExecutorManager:
    """Manages executor pools for different types of operations."""
    
    def __init__(self):
        self._cpu_executor: Optional[ProcessPoolExecutor] = None
        self._io_executor: Optional[ThreadPoolExecutor] = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """Initialize executors if not already done."""
        if self._initialized:
            return
        
        # CPU-bound: use processes (isolated memory, true parallelism)
        cpu_count = multiprocessing.cpu_count()
        self._cpu_executor = ProcessPoolExecutor(
            max_workers=max(1, cpu_count - 1),  # Leave one core for the main process
            mp_context=multiprocessing.get_context('spawn')  # More reliable on all platforms
        )
        
        # I/O-bound: use threads (shared memory, good for I/O waits)
        self._io_executor = ThreadPoolExecutor(
            max_workers=20,  # Reasonable limit for I/O operations
            thread_name_prefix="io-worker"
        )
        
        self._initialized = True
        logger.info(f"Initialized executors: CPU={cpu_count-1} workers, I/O=20 workers")
    
    async def run_cpu_bound(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute CPU-bound function in a separate process.
        
        Use this for:
        - Mathematical computations (SymPy, NumPy)
        - Machine learning training/inference
        - Image processing
        - Cryptographic operations
        - Any CPU-intensive task
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function execution
        """
        self._ensure_initialized()
        
        if self._cpu_executor is None:
            raise RuntimeError("CPU executor not initialized")
        
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._cpu_executor,
                func,
                *args,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"CPU-bound execution failed: {e}")
            raise
    
    async def run_io_bound(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute I/O-bound function in a thread pool.
        
        Use this for:
        - File I/O operations
        - Database queries (sync drivers)
        - HTTP requests (sync libraries like requests)
        - Network operations
        - Any I/O wait operation
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Result of the function execution
        """
        self._ensure_initialized()
        
        if self._io_executor is None:
            raise RuntimeError("I/O executor not initialized")
        
        loop = asyncio.get_event_loop()
        try:
            result = await loop.run_in_executor(
                self._io_executor,
                func,
                *args,
                **kwargs
            )
            return result
        except Exception as e:
            logger.error(f"I/O-bound execution failed: {e}")
            raise
    
    async def run_batch_cpu_bound(self, tasks: list[tuple[Callable, tuple, dict]]) -> list[Any]:
        """
        Execute multiple CPU-bound tasks concurrently.
        
        Args:
            tasks: List of (function, args, kwargs) tuples
            
        Returns:
            List of results in the same order as tasks
        """
        if not tasks:
            return []
        
        # Create tasks
        coroutines = [
            self.run_cpu_bound(func, *args, **kwargs)
            for func, args, kwargs in tasks
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch CPU task {i} failed: {result}")
        
        return results
    
    async def run_batch_io_bound(self, tasks: list[tuple[Callable, tuple, dict]]) -> list[Any]:
        """
        Execute multiple I/O-bound tasks concurrently.
        
        Args:
            tasks: List of (function, args, kwargs) tuples
            
        Returns:
            List of results in the same order as tasks
        """
        if not tasks:
            return []
        
        # Create tasks
        coroutines = [
            self.run_io_bound(func, *args, **kwargs)
            for func, args, kwargs in tasks
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*coroutines, return_exceptions=True)
        
        # Check for exceptions
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Batch I/O task {i} failed: {result}")
        
        return results
    
    def shutdown(self):
        """Shutdown all executors."""
        if self._cpu_executor:
            self._cpu_executor.shutdown(wait=True)
            self._cpu_executor = None
        
        if self._io_executor:
            self._io_executor.shutdown(wait=True)
            self._io_executor = None
        
        self._initialized = False
        logger.info("Executors shutdown complete")


# Global executor manager instance
executor_manager = ExecutorManager()


# Convenience functions for backward compatibility
async def run_cpu_bound(func: Callable, *args, **kwargs) -> Any:
    """Execute CPU-bound function in process pool."""
    return await executor_manager.run_cpu_bound(func, *args, **kwargs)


async def run_io_bound(func: Callable, *args, **kwargs) -> Any:
    """Execute I/O-bound function in thread pool."""
    return await executor_manager.run_io_bound(func, *args, **kwargs)


async def run_batch_cpu_bound(tasks: list[tuple[Callable, tuple, dict]]) -> list[Any]:
    """Execute multiple CPU-bound tasks concurrently."""
    return await executor_manager.run_batch_cpu_bound(tasks)


async def run_batch_io_bound(tasks: list[tuple[Callable, tuple, dict]]) -> list[Any]:
    """Execute multiple I/O-bound tasks concurrently."""
    return await executor_manager.run_batch_io_bound(tasks)


def shutdown_executors():
    """Shutdown all executors."""
    executor_manager.shutdown()


# Context manager for automatic cleanup
class ExecutorContext:
    """Context manager for executor lifecycle."""
    
    def __init__(self):
        self.manager = ExecutorManager()
    
    async def __aenter__(self):
        return self.manager
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.manager.shutdown()


# Example usage and testing functions
def _example_cpu_bound_function(n: int) -> int:
    """Example CPU-bound function for testing."""
    result = 0
    for i in range(n):
        result += i ** 2
    return result


async def _example_io_bound_function(duration: float) -> str:
    """Example I/O-bound function for testing."""
    import asyncio
    await asyncio.sleep(duration)
    return f"Slept for {duration} seconds"


async def test_executors():
    """Test function to verify executors work correctly."""
    print("Testing CPU-bound executor...")
    result = await run_cpu_bound(_example_cpu_bound_function, 1000000)
    print(f"CPU result: {result}")
    
    print("Testing I/O-bound executor...")
    result = await run_io_bound(_example_io_bound_function, 0.1)
    print(f"I/O result: {result}")
    
    print("Testing batch CPU operations...")
    tasks = [
        (_example_cpu_bound_function, (100000,), {}),
        (_example_cpu_bound_function, (200000,), {}),
        (_example_cpu_bound_function, (300000,), {}),
    ]
    results = await run_batch_cpu_bound(tasks)
    print(f"Batch CPU results: {results}")
    
    print("Testing batch I/O operations...")
    tasks = [
        (_example_io_bound_function, (0.1,), {}),
        (_example_io_bound_function, (0.2,), {}),
        (_example_io_bound_function, (0.1,), {}),
    ]
    results = await run_batch_io_bound(tasks)
    print(f"Batch I/O results: {results}")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_executors())
