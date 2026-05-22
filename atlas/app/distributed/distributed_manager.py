"""
AXIOM Distributed Computing System
Advanced distributed computing capabilities for scientific workloads
"""

# Optional torch import for deep learning support
try:
    import torch
    import torch.distributed as dist
    import torch.multiprocessing as mp
    from torch.nn.parallel import DistributedDataParallel as DDP
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
    dist = None  # type: ignore
    mp = None  # type: ignore
    DDP = None  # type: ignore
import os
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import psutil
import numpy as np
import asyncio

from app.core.config import settings
from app.distributed.gpu_manager import gpu_manager
from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class DistributedConfig:
    """Configuration for distributed computing"""
    world_size: int
    rank: int
    backend: str
    master_addr: str
    master_port: int
    gpu_available: bool
    device_count: int

@dataclass
class ComputationResult:
    """Result of distributed computation"""
    result: Any
    execution_time: float
    worker_id: int
    success: bool
    error_message: Optional[str] = None

class DistributedManager:
    """Manager for distributed computing operations"""

    def __init__(self):
        self.config = self._setup_distributed_config()
        self.is_initialized = False
        self.process_pool: Optional[ProcessPoolExecutor] = None
        self.thread_pool: Optional[ThreadPoolExecutor] = None

        if settings.enable_distributed:
            self._initialize_distributed()

    def _setup_distributed_config(self) -> DistributedConfig:
        """Setup distributed configuration"""
        gpu_info = gpu_manager.get_device_info()

        return DistributedConfig(
            world_size=settings.world_size,
            rank=settings.rank,
            backend=settings.distributed_backend,
            master_addr=settings.master_addr,
            master_port=settings.master_port,
            gpu_available=gpu_info['device_available'],
            device_count=gpu_info['device_count']
        )

    def _initialize_distributed(self):
        """Initialize distributed computing environment"""
        try:
            if self.config.world_size > 1:
                # Set environment variables for distributed training
                settings.MASTER_ADDR = self.config.master_addr
                settings.MASTER_PORT = str(self.config.master_port)
                settings.WORLD_SIZE = str(self.config.world_size)
                settings.RANK = str(self.config.rank)

                # Initialize the process group
                if self.config.gpu_available and self.config.backend == 'nccl':
                    dist.init_process_group(
                        backend=self.config.backend,
                        rank=self.config.rank,
                        world_size=self.config.world_size
                    )
                else:
                    dist.init_process_group(
                        backend='gloo',
                        rank=self.config.rank,
                        world_size=self.config.world_size
                    )

                self.is_initialized = True
                logger.info(f"✅ Distributed computing initialized: rank {self.config.rank}/{self.config.world_size}")
            else:
                logger.info("⚠️  Distributed computing disabled (world_size=1)")

        except Exception as e:
            logger.error(f"❌ Failed to initialize distributed computing: {e}")
            self.is_initialized = False

    def initialize_pools(self):
        """Initialize process and thread pools for parallel computation"""
        cpu_count = psutil.cpu_count(logical=True)

        # Process pool for CPU-intensive tasks
        self.process_pool = ProcessPoolExecutor(
            max_workers=min(cpu_count, 8),  # Limit to reasonable number
            mp_context=mp.get_context('spawn')
        )

        # Thread pool for I/O bound tasks
        self.thread_pool = ThreadPoolExecutor(
            max_workers=min(cpu_count * 2, 16)
        )

        logger.info(f"✅ Initialized pools: {self.process_pool._max_workers} processes, {self.thread_pool._max_workers} threads")

    async def parallel_compute(self, func: Callable, data_list: List[Any], use_processes: bool = True) -> List[ComputationResult]:
        """Execute function in parallel across multiple workers (async)"""
        if not self.process_pool and not self.thread_pool:
            self.initialize_pools()

        results = []
        start_time = time.time()

        try:
            if use_processes and self.process_pool:
                # Use process pool for CPU-intensive tasks
                loop = asyncio.get_event_loop()
                futures = [loop.run_in_executor(self.process_pool, self._execute_with_timing, func, data, i)
                          for i, data in enumerate(data_list)]
            elif self.thread_pool:
                # Use thread pool for I/O bound tasks
                loop = asyncio.get_event_loop()
                futures = [loop.run_in_executor(self.thread_pool, self._execute_with_timing, func, data, i)
                          for i, data in enumerate(data_list)]
            else:
                # Fallback to sequential execution
                logger.warning("⚠️  No pools available, falling back to sequential execution")
                return [self._execute_with_timing(func, data, i) for i, data in enumerate(data_list)]

            # Collect results
            for future in futures:
                try:
                    result = await future
                    results.append(result)
                except Exception as e:
                    logger.error(f"❌ Task execution failed: {e}")
                    results.append(ComputationResult(
                        result=None,
                        execution_time=time.time() - start_time,
                        worker_id=-1,
                        success=False,
                        error_message=str(e)
                    ))

        except Exception as e:
            logger.error(f"❌ Parallel computation failed: {e}")
            return []

        total_time = time.time() - start_time
        logger.info(f"✅ Parallel computation completed: {len(results)} tasks in {total_time:.2f}s")

        return results

    def _execute_with_timing(self, func: Callable, data: Any, worker_id: int) -> ComputationResult:
        """Execute function with timing and error handling"""
        start_time = time.time()

        try:
            result = func(data)
            execution_time = time.time() - start_time

            return ComputationResult(
                result=result,
                execution_time=execution_time,
                worker_id=worker_id,
                success=True
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Worker {worker_id} failed: {e}")

            return ComputationResult(
                result=None,
                execution_time=execution_time,
                worker_id=worker_id,
                success=False,
                error_message=str(e)
            )

    async def distributed_matrix_multiply(self, matrices_a: List[np.ndarray], matrices_b: List[np.ndarray]) -> List[np.ndarray]:
        """Distributed matrix multiplication (async)"""
        if not self.is_initialized or len(matrices_a) != len(matrices_b):
            # Fallback to local computation
            return [np.dot(a, b) for a, b in zip(matrices_a, matrices_b)]

        def matrix_multiply_task(data):
            a, b = data
            return np.dot(a, b)

        data_list = list(zip(matrices_a, matrices_b))
        results = await self.parallel_compute(matrix_multiply_task, data_list, use_processes=True)

        return [r.result for r in results if r.success]

    def distributed_scientific_computation(self, computation_func: Callable, data_sets: List[Any]) -> List[Any]:
        """Execute scientific computations in distributed manner"""
        if not self.is_initialized:
            logger.info("⚠️  Distributed computing not available, using parallel processing")

        results = self.parallel_compute(computation_func, data_sets, use_processes=True)
        return [r.result for r in results if r.success]

    def get_system_status(self) -> Dict:
        """Get distributed system status"""
        return {
            "distributed_enabled": self.is_initialized,
            "world_size": self.config.world_size,
            "rank": self.config.rank,
            "backend": self.config.backend,
            "gpu_available": self.config.gpu_available,
            "device_count": self.config.device_count,
            "process_pool_active": self.process_pool is not None,
            "thread_pool_active": self.thread_pool is not None,
            "cpu_count": psutil.cpu_count(logical=True),
            "memory_gb": psutil.virtual_memory().total / (1024**3)
        }

    def cleanup(self):
        """Cleanup distributed resources"""
        if self.is_initialized:
            dist.destroy_process_group()
            self.is_initialized = False

        if self.process_pool:
            self.process_pool.shutdown(wait=True)

        if self.thread_pool:
            self.thread_pool.shutdown(wait=True)

        logger.info("✅ Distributed computing resources cleaned up")

# Global distributed manager instance
distributed_manager = DistributedManager()

def get_distributed_manager() -> DistributedManager:
    """Get the global distributed manager instance"""
    return distributed_manager

def is_distributed_available() -> bool:
    """Check if distributed computing is available"""
    return distributed_manager.is_initialized
