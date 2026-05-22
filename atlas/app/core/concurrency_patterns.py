"""
Optimized Concurrency Patterns for AXIOM ATLAS.

This module provides optimized patterns for async operations including
batching, semaphores, worker pools, and circuit breakers.
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

T = TypeVar('T')
R = TypeVar('R')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    success_threshold: int = 3
    timeout: float = 30.0


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance."""
    
    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to HALF_OPEN")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            # Execute function with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            # Success
            self._on_success()
            return result
            
        except asyncio.TimeoutError:
            self._on_failure("Timeout")
            raise
        except Exception as e:
            self._on_failure(str(e))
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return True
        
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation."""
        self.success_count += 1
        self.last_success_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info("Circuit breaker reset to CLOSED")
    
    def _on_failure(self, error: str):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures: {error}")


class RateLimiter:
    """Rate limiter using token bucket algorithm."""
    
    def __init__(self, rate: float, capacity: int):
        """
        Initialize rate limiter.
        
        Args:
            rate: Tokens per second
            capacity: Maximum tokens in bucket
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from the bucket."""
        async with self._lock:
            now = time.time()
            # Add tokens based on elapsed time
            elapsed = now - self.last_update
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            else:
                return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> float:
        """Wait until tokens are available and return wait time."""
        start_time = time.time()
        
        while not await self.acquire(tokens):
            await asyncio.sleep(0.01)  # Small delay
        
        return time.time() - start_time


class BatchProcessor:
    """Batch processor for efficient async operations."""
    
    def __init__(self, batch_size: int = 10, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending_items = []
        self.last_flush = time.time()
        self._lock = asyncio.Lock()
        self._flush_task = None
    
    async def add_item(self, item: T) -> None:
        """Add item to batch."""
        async with self._lock:
            self.pending_items.append(item)
            
            # Flush if batch is full
            if len(self.pending_items) >= self.batch_size:
                await self._flush()
    
    async def _flush(self) -> List[T]:
        """Flush pending items."""
        if not self.pending_items:
            return []
        
        items = self.pending_items.copy()
        self.pending_items.clear()
        self.last_flush = time.time()
        
        return items
    
    async def process_batch(self, processor: Callable[[List[T]], R]) -> R:
        """Process current batch with given processor function."""
        items = await self._flush()
        if items:
            return await processor(items)
        return None


class WorkerPool:
    """Worker pool for concurrent task processing."""
    
    def __init__(self, num_workers: int = 5, queue_size: int = 1000):
        self.num_workers = num_workers
        self.queue_size = queue_size
        self.queue = asyncio.Queue(maxsize=queue_size)
        self.workers = []
        self.running = False
        self.stats = {
            "tasks_processed": 0,
            "tasks_failed": 0,
            "avg_processing_time": 0.0,
        }
    
    async def start(self):
        """Start worker pool."""
        if self.running:
            return
        
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker(f"worker-{i}"))
            for i in range(self.num_workers)
        ]
        
        logger.info(f"Started worker pool with {self.num_workers} workers")
    
    async def stop(self):
        """Stop worker pool."""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel all workers
        for worker in self.workers:
            worker.cancel()
        
        # Wait for workers to finish
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Worker pool stopped")
    
    async def submit_task(self, task: Callable, *args, **kwargs) -> None:
        """Submit task to worker pool."""
        await self.queue.put((task, args, kwargs))
    
    async def _worker(self, worker_id: str):
        """Worker coroutine."""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # Get task from queue
                task, args, kwargs = await asyncio.wait_for(
                    self.queue.get(),
                    timeout=1.0
                )
                
                # Process task
                start_time = time.time()
                try:
                    if asyncio.iscoroutinefunction(task):
                        await task(*args, **kwargs)
                    else:
                        task(*args, **kwargs)
                    
                    self.stats["tasks_processed"] += 1
                    
                except Exception as e:
                    self.stats["tasks_failed"] += 1
                    logger.error(f"Worker {worker_id} task failed: {e}")
                
                # Update stats
                processing_time = time.time() - start_time
                self.stats["avg_processing_time"] = (
                    (self.stats["avg_processing_time"] * (self.stats["tasks_processed"] - 1) + processing_time) /
                    self.stats["tasks_processed"]
                )
                
                # Mark task as done
                self.queue.task_done()
                
            except asyncio.TimeoutError:
                # No task available, continue
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
                await asyncio.sleep(0.1)
        
        logger.info(f"Worker {worker_id} stopped")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get worker pool statistics."""
        return {
            "running": self.running,
            "num_workers": self.num_workers,
            "queue_size": self.queue.qsize(),
            "stats": self.stats.copy(),
        }


class SemaphoreManager:
    """Manager for semaphores with different limits."""
    
    def __init__(self):
        self.semaphores = {}
        self._lock = asyncio.Lock()
    
    async def get_semaphore(self, name: str, limit: int) -> asyncio.Semaphore:
        """Get or create semaphore with given limit."""
        async with self._lock:
            if name not in self.semaphores:
                self.semaphores[name] = asyncio.Semaphore(limit)
            return self.semaphores[name]
    
    async def acquire(self, name: str, limit: int) -> asyncio.Semaphore:
        """Acquire semaphore."""
        semaphore = await self.get_semaphore(name, limit)
        await semaphore.acquire()
        return semaphore
    
    def release(self, semaphore: asyncio.Semaphore):
        """Release semaphore."""
        semaphore.release()


# Global instances
circuit_breakers = {}
rate_limiters = {}
semaphore_manager = SemaphoreManager()


def get_circuit_breaker(name: str, config: CircuitBreakerConfig = None) -> CircuitBreaker:
    """Get or create circuit breaker."""
    if name not in circuit_breakers:
        circuit_breakers[name] = CircuitBreaker(config)
    return circuit_breakers[name]


def get_rate_limiter(name: str, rate: float, capacity: int) -> RateLimiter:
    """Get or create rate limiter."""
    if name not in rate_limiters:
        rate_limiters[name] = RateLimiter(rate, capacity)
    return rate_limiters[name]


# Utility functions
async def batch_process(
    items: List[T],
    processor: Callable[[T], R],
    batch_size: int = 10,
    max_concurrent: int = 5
) -> List[R]:
    """Process items in batches with concurrency control."""
    results = []
    
    # Create semaphore for concurrency control
    semaphore = await semaphore_manager.get_semaphore("batch_processing", max_concurrent)
    
    async def process_batch(batch: List[T]) -> List[R]:
        async with semaphore:
            batch_results = []
            for item in batch:
                try:
                    if asyncio.iscoroutinefunction(processor):
                        result = await processor(item)
                    else:
                        result = processor(item)
                    batch_results.append(result)
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    batch_results.append(None)
            return batch_results
    
    # Process in batches
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = await process_batch(batch)
        results.extend(batch_results)
    
    return results


async def parallel_execute(
    tasks: List[Callable],
    max_concurrent: int = 10,
    return_exceptions: bool = True
) -> List[Any]:
    """Execute tasks in parallel with concurrency control."""
    semaphore = await semaphore_manager.get_semaphore("parallel_execution", max_concurrent)
    
    async def execute_with_semaphore(task):
        async with semaphore:
            if asyncio.iscoroutinefunction(task):
                return await task()
            else:
                return task()
    
    # Execute all tasks
    results = await asyncio.gather(
        *[execute_with_semaphore(task) for task in tasks],
        return_exceptions=return_exceptions
    )
    
    return results


async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0
) -> Any:
    """Retry function with exponential backoff."""
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func()
            else:
                return func()
        except Exception as e:
            last_exception = e
            
            if attempt == max_retries:
                break
            
            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base ** attempt), max_delay)
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.1f}s")
            await asyncio.sleep(delay)
    
    raise last_exception


# Example usage
if __name__ == "__main__":
    async def test_circuit_breaker():
        """Test circuit breaker."""
        cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=2))
        
        async def failing_function():
            raise Exception("Service unavailable")
        
        # Test failures
        for i in range(3):
            try:
                await cb.call(failing_function)
            except Exception as e:
                print(f"Call {i+1} failed: {e}")
        
        print(f"Circuit state: {cb.state}")
    
    async def test_rate_limiter():
        """Test rate limiter."""
        limiter = RateLimiter(rate=2.0, capacity=5)
        
        for i in range(10):
            acquired = await limiter.acquire()
            print(f"Request {i+1}: {'Allowed' if acquired else 'Rate limited'}")
            await asyncio.sleep(0.1)
    
    async def test_worker_pool():
        """Test worker pool."""
        pool = WorkerPool(num_workers=3)
        await pool.start()
        
        async def test_task(task_id: int):
            print(f"Processing task {task_id}")
            await asyncio.sleep(0.1)
            return f"Task {task_id} completed"
        
        # Submit tasks
        for i in range(10):
            await pool.submit_task(test_task, i)
        
        # Wait a bit
        await asyncio.sleep(2)
        
        # Stop pool
        await pool.stop()
        print(f"Pool stats: {pool.get_stats()}")
    
    async def main():
        """Test main function."""
        print("Testing Circuit Breaker:")
        await test_circuit_breaker()
        
        print("\nTesting Rate Limiter:")
        await test_rate_limiter()
        
        print("\nTesting Worker Pool:")
        await test_worker_pool()
    
    # Run tests
    asyncio.run(main())
