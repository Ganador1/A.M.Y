"""
AXIOM Advanced Async Processing System
High-performance asynchronous processing with intelligent concurrency management
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
from enum import Enum
import os

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4

class TaskType(Enum):
    """Task type categories"""
    CPU_INTENSIVE = "cpu_intensive"
    IO_INTENSIVE = "io_intensive"
    GPU_INTENSIVE = "gpu_intensive"
    MEMORY_INTENSIVE = "memory_intensive"
    NETWORK_INTENSIVE = "network_intensive"

@dataclass
class AsyncTask:
    """Represents an asynchronous task"""
    task_id: str
    task_type: TaskType
    priority: TaskPriority
    coroutine: Callable[[], Awaitable[Any]]
    created_at: float
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkerPool:
    """Worker pool configuration"""
    pool_type: str
    max_workers: int
    current_workers: int = 0
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_execution_time: float = 0.0

@dataclass
class AsyncMetrics:
    """Asynchronous processing metrics"""
    total_tasks: int = 0
    active_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_execution_time: float = 0.0
    peak_concurrency: int = 0
    queue_size: int = 0
    worker_utilization: Dict[str, float] = field(default_factory=dict)

class AdvancedAsyncProcessor:
    """Advanced asynchronous processor with intelligent concurrency management"""

    def __init__(self):
        self.task_queue: asyncio.Queue[AsyncTask] = asyncio.Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, Any] = {}
        self.failed_tasks: Dict[str, Exception] = {}
        self.task_dependencies: Dict[str, List[str]] = {}
        self.metrics = AsyncMetrics()

        # Worker pools
        cpu_count = self._safe_cpu_count()
        self.worker_pools = {
            "cpu": WorkerPool("cpu", max_workers=self._calculate_optimal_cpu_workers()),
            "io": WorkerPool("io", max_workers=50),  # IO-bound tasks
            "gpu": WorkerPool("gpu", max_workers=4),  # GPU tasks
            "process": WorkerPool("process", max_workers=max(1, cpu_count // 2))
        }

        # Executors
        self.thread_executor = ThreadPoolExecutor(max_workers=self.worker_pools["cpu"].max_workers)
        try:
            self.process_executor = ProcessPoolExecutor(
                max_workers=self.worker_pools["process"].max_workers
            )
        except Exception as exc:  # pragma: no cover - entornos restringidos
            logger.warning(
                "No se pudo inicializar ProcessPoolExecutor: %s. Se usará solo ThreadPool.",
                exc,
            )
            self.process_executor = None
            self.worker_pools["process"].max_workers = 0

        # Control flags
        self.running = False
        self.shutdown_event = asyncio.Event()

        logger.info("Advanced Async Processor initialized")

    def _calculate_optimal_cpu_workers(self) -> int:
        """Calculate optimal number of CPU workers based on system resources"""
        cpu_count = self._safe_cpu_count()
        memory_gb = self._safe_memory_total_gb()

        # Conservative approach: use 75% of available CPUs
        optimal = max(1, int(cpu_count * 0.75))

        # Adjust based on memory (each worker needs ~100MB)
        memory_based = max(1, int(memory_gb / 0.1)) if memory_gb > 0 else optimal

        return min(optimal, memory_based, 32)  # Cap at 32 workers

    @staticmethod
    def _safe_cpu_count(default: int = 4) -> int:
        try:
            count = psutil.cpu_count(logical=True)
            if count is None:
                raise ValueError("cpu_count returned None")
            return count
        except Exception as exc:  # pragma: no cover - entorno restringido
            logger.warning("psutil.cpu_count falló (%s); usando os.cpu_count()", exc)
            return os.cpu_count() or default

    @staticmethod
    def _safe_memory_total_gb() -> float:
        try:
            memory = psutil.virtual_memory()
            return memory.total / (1024**3)
        except Exception as exc:  # pragma: no cover
            logger.warning("psutil.virtual_memory falló (%s); usando valor por defecto 0", exc)
            env_override = os.getenv("AXIOM_SYSTEM_MEMORY_GB")
            try:
                return float(env_override) if env_override else 0.0
            except ValueError:
                return 0.0

    async def start(self):
        """Start the async processor"""
        if self.running:
            return

        self.running = True
        self.shutdown_event.clear()

        # Start worker tasks
        workers = []
        for pool_name, pool in self.worker_pools.items():
            for i in range(pool.max_workers):
                worker = asyncio.create_task(self._worker_loop(pool_name))
                workers.append(worker)

        # Start task scheduler
        scheduler = asyncio.create_task(self._task_scheduler())

        # Start metrics updater
        metrics_updater = asyncio.create_task(self._metrics_updater())

        logger.info(f"Started {len(workers)} workers across {len(self.worker_pools)} pools")

        # Wait for shutdown
        await self.shutdown_event.wait()

        # Cleanup
        for worker in workers:
            worker.cancel()
        scheduler.cancel()
        metrics_updater.cancel()

        await asyncio.gather(*workers, scheduler, metrics_updater, return_exceptions=True)

    async def stop(self):
        """Stop the async processor"""
        self.running = False
        self.shutdown_event.set()
        logger.info("Async processor stopping...")

    async def submit_task(self, task: AsyncTask) -> str:
        """Submit a task for execution"""
        # Check dependencies
        if task.dependencies:
            for dep in task.dependencies:
                if dep not in self.completed_tasks and dep not in self.failed_tasks:
                    raise ValueError(f"Dependency {dep} not completed")

        await self.task_queue.put(task)
        self.metrics.total_tasks += 1
        self.metrics.queue_size = self.task_queue.qsize()

        logger.info(f"Task {task.task_id} submitted (type: {task.task_type.value}, priority: {task.priority.name})")
        return task.task_id

    async def _task_scheduler(self):
        """Task scheduler that prioritizes tasks"""
        while self.running:
            try:
                # Get next task with priority consideration
                task = await self._get_next_task()
                if task:
                    await self._execute_task(task)
            except Exception as e:
                logger.error(f"Task scheduler error: {e}")
                await asyncio.sleep(0.1)

    async def _get_next_task(self) -> Optional[AsyncTask]:
        """Get next task considering priority and resource availability"""
        if self.task_queue.empty():
            return None

        # Simple priority queue implementation
        tasks = []
        try:
            while not self.task_queue.empty():
                task = self.task_queue.get_nowait()
                tasks.append(task)
        except asyncio.QueueEmpty:
            pass

        if not tasks:
            return None

        # Sort by priority (higher priority first)
        tasks.sort(key=lambda t: t.priority.value, reverse=True)

        # Find first task that can be executed
        for task in tasks:
            if self._can_execute_task(task):
                # Put back the other tasks
                for other_task in tasks:
                    if other_task != task:
                        await self.task_queue.put(other_task)
                return task

        # If no task can be executed, put them all back
        for task in tasks:
            await self.task_queue.put(task)

        return None

    def _can_execute_task(self, task: AsyncTask) -> bool:
        """Check if a task can be executed based on resource availability"""
        pool = self.worker_pools.get(task.task_type.value.split('_')[0])
        if not pool:
            return True  # Default pool

        return pool.active_tasks < pool.max_workers

    async def _execute_task(self, task: AsyncTask):
        """Execute a task"""
        pool_name = task.task_type.value.split('_')[0]
        pool = self.worker_pools.get(pool_name, self.worker_pools["cpu"])

        pool.active_tasks += 1
        self.metrics.active_tasks += 1

        try:
            # Create asyncio task
            asyncio_task = asyncio.create_task(self._run_task_with_timeout(task))
            self.active_tasks[task.task_id] = asyncio_task

            # Wait for completion
            result = await asyncio_task

            # Store result
            self.completed_tasks[task.task_id] = result
            pool.completed_tasks += 1
            self.metrics.completed_tasks += 1

            logger.info(f"Task {task.task_id} completed successfully")

        except Exception as e:
            self.failed_tasks[task.task_id] = e
            pool.failed_tasks += 1
            self.metrics.failed_tasks += 1
            logger.error(f"Task {task.task_id} failed: {e}")

        finally:
            pool.active_tasks -= 1
            self.metrics.active_tasks -= 1
            self.active_tasks.pop(task.task_id, None)

    async def _run_task_with_timeout(self, task: AsyncTask) -> Any:
        """Run task with timeout handling"""
        if task.timeout:
            try:
                return await asyncio.wait_for(task.coroutine(), timeout=task.timeout)
            except asyncio.TimeoutError:
                raise TimeoutError(f"Task {task.task_id} timed out after {task.timeout}s")
        else:
            return await task.coroutine()

    async def _worker_loop(self, pool_name: str):
        """Worker loop for processing tasks"""
        while self.running:
            try:
                # Wait for work
                await asyncio.sleep(0.01)  # Small delay to prevent busy waiting
            except asyncio.CancelledError:
                break

    async def _metrics_updater(self):
        """Update metrics periodically"""
        while self.running:
            try:
                # Update worker utilization
                for pool_name, pool in self.worker_pools.items():
                    if pool.max_workers > 0:
                        utilization = (pool.active_tasks / pool.max_workers) * 100
                        self.metrics.worker_utilization[pool_name] = utilization

                # Update peak concurrency
                current_concurrency = sum(pool.active_tasks for pool in self.worker_pools.values())
                self.metrics.peak_concurrency = max(self.metrics.peak_concurrency, current_concurrency)

                await asyncio.sleep(1.0)  # Update every second

            except Exception as e:
                logger.error(f"Metrics updater error: {e}")
                await asyncio.sleep(1.0)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a specific task"""
        if task_id in self.completed_tasks:
            return {"status": "completed", "result": self.completed_tasks[task_id]}
        elif task_id in self.failed_tasks:
            return {"status": "failed", "error": str(self.failed_tasks[task_id])}
        elif task_id in self.active_tasks:
            return {"status": "running"}
        else:
            return {"status": "not_found"}

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "running": self.running,
            "metrics": {
                "total_tasks": self.metrics.total_tasks,
                "active_tasks": self.metrics.active_tasks,
                "completed_tasks": self.metrics.completed_tasks,
                "failed_tasks": self.metrics.failed_tasks,
                "queue_size": self.metrics.queue_size,
                "peak_concurrency": self.metrics.peak_concurrency,
                "worker_utilization": self.metrics.worker_utilization
            },
            "worker_pools": {
                name: {
                    "max_workers": pool.max_workers,
                    "active_tasks": pool.active_tasks,
                    "completed_tasks": pool.completed_tasks,
                    "failed_tasks": pool.failed_tasks
                }
                for name, pool in self.worker_pools.items()
            }
        }

    async def wait_for_task(self, task_id: str, timeout: Optional[float] = None) -> Any:
        """Wait for a task to complete"""
        start_time = time.time()

        while task_id not in self.completed_tasks and task_id not in self.failed_tasks:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Wait for task {task_id} timed out")

            await asyncio.sleep(0.1)

        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]
        elif task_id in self.failed_tasks:
            raise self.failed_tasks[task_id]
        else:
            raise ValueError(f"Task {task_id} not found")

# Global async processor instance
async_processor = AdvancedAsyncProcessor()

def get_async_processor() -> AdvancedAsyncProcessor:
    """Get the global async processor instance"""
    return async_processor

# Convenience functions
async def submit_async_task(
    task_id: str,
    coroutine: Callable[[], Awaitable[Any]],
    task_type: TaskType = TaskType.CPU_INTENSIVE,
    priority: TaskPriority = TaskPriority.NORMAL,
    timeout: Optional[float] = None,
    dependencies: Optional[List[str]] = None
) -> str:
    """Convenience function to submit an async task"""
    task = AsyncTask(
        task_id=task_id,
        task_type=task_type,
        priority=priority,
        coroutine=coroutine,
        created_at=time.time(),
        timeout=timeout,
        dependencies=dependencies or []
    )

    return await async_processor.submit_task(task)

async def run_scientific_task(
    task_id: str,
    operation: Callable[[], Any],
    task_type: TaskType = TaskType.CPU_INTENSIVE
) -> str:
    """Run a scientific task with automatic resource management"""
    async def wrapper():
        return await asyncio.get_event_loop().run_in_executor(None, operation)

    return await submit_async_task(task_id, wrapper, task_type)
