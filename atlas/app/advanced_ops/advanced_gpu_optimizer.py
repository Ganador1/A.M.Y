"""
AXIOM Advanced GPU Optimization System
CUDA Streams, Memory Pooling, Multi-GPU Support, and GPU Profiling
"""

# Optional torch import for deep learning support
try:
    import torch
    import torch.cuda as cuda
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
    cuda = None # type: ignore
import threading
import time
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import psutil
import numpy as np

from app.distributed.gpu_manager import gpu_manager

logger = logging.getLogger(__name__)

@dataclass
class GPUStream:
    """GPU stream configuration"""
    stream: torch.cuda.Stream
    device_id: int
    priority: int
    active_operations: int = 0

@dataclass
class MemoryPool:
    """GPU memory pool for efficient allocation"""
    device_id: int
    total_memory: int
    allocated_memory: int = 0
    peak_memory: int = 0
    allocations: Dict[str, int] = None

    def __post_init__(self):
        if self.allocations is None:
            self.allocations = {}

@dataclass
class GPUProfileMetrics:
    """Detailed GPU profiling metrics"""
    device_id: int
    kernel_time: float
    memory_bandwidth: float
    compute_utilization: float
    memory_utilization: float
    power_consumption: Optional[float]
    temperature: Optional[float]
    timestamp: float

class AdvancedGPUOptimizer:
    """Advanced GPU optimization system with streams, memory pooling, and profiling"""

    def __init__(self):
        self.streams: Dict[int, List[GPUStream]] = {}
        self.memory_pools: Dict[int, MemoryPool] = {}
        self.profiling_data: List[GPUProfileMetrics] = []
        self.lock = threading.Lock()

        self._initialize_gpu_streams()
        self._initialize_memory_pools()
        self._start_profiling_thread()

        logger.info("✅ Advanced GPU Optimizer initialized")

    def _initialize_gpu_streams(self):
        """Initialize CUDA streams for parallel execution"""
        if not gpu_manager.is_gpu_available():
            logger.warning("⚠️  No GPU available, skipping stream initialization")
            return

        gpu_info = gpu_manager.get_device_info()

        if gpu_info['device_type'] == 'cuda':
            device_count = gpu_info['device_count']

            for device_id in range(device_count):
                with torch.cuda.device(device_id):
                    self.streams[device_id] = []

                    # Create streams with different priorities
                    for priority in [-1, 0, 1]:  # Low, Normal, High priority
                        try:
                            stream = torch.cuda.current_stream(device_id)
                            if priority != 0:  # Create new stream for non-default priority
                                stream = torch.cuda.Stream(device=device_id, priority=priority)

                            gpu_stream = GPUStream(
                                stream=stream,
                                device_id=device_id,
                                priority=priority
                            )
                            self.streams[device_id].append(gpu_stream)

                        except Exception as e:
                            logger.warning(f"❌ Failed to create stream for device {device_id}, priority {priority}: {e}")

            logger.info(f"✅ Initialized CUDA streams for {device_count} device(s)")

        elif gpu_info['device_type'] == 'mps':
            # MPS has limited stream support
            logger.info("ℹ️  MPS detected - limited stream support available")

    def _initialize_memory_pools(self):
        """Initialize memory pools for efficient allocation"""
        if not gpu_manager.is_gpu_available():
            return

        gpu_info = gpu_manager.get_device_info()

        if gpu_info['device_type'] == 'cuda':
            device_count = gpu_info['device_count']

            for device_id in range(device_count):
                try:
                    with torch.cuda.device(device_id):
                        total_memory = torch.cuda.get_device_properties(device_id).total_memory
                        self.memory_pools[device_id] = MemoryPool(
                            device_id=device_id,
                            total_memory=total_memory
                        )

                        # Enable memory pooling
                        torch.cuda.set_per_process_memory_fraction(0.9, device_id)
                        torch.cuda.empty_cache()

                except Exception as e:
                    logger.warning(f"❌ Failed to initialize memory pool for device {device_id}: {e}")

            logger.info(f"✅ Initialized memory pools for {device_count} device(s)")

    def _start_profiling_thread(self):
        """
        Start background profiling thread.
        
        NOTE: Uses daemon thread (threading.Thread with daemon=True).
        This is acceptable because:
        - Daemon threads run in separate OS threads
        - They do NOT interfere with asyncio event loop
        - time.sleep() in the thread does NOT block the main event loop
        - Appropriate for low-frequency monitoring (10Hz)
        
        TODO (ROADMAP 5): Consider asyncio.create_task if profiling needs
        to coordinate with other async operations, but current implementation
        is correct for independent background monitoring.
        """
        if not gpu_manager.is_gpu_available():
            return

        gpu_info = gpu_manager.get_device_info()
        if gpu_info['device_type'] == 'cuda':
            profiling_thread = threading.Thread(target=self._profiling_worker, daemon=True)
            profiling_thread.start()
            logger.info("✅ GPU profiling thread started")

    def _profiling_worker(self):
        """
        Background worker for GPU profiling.
        
        NOTE: Runs in daemon thread (separate OS thread).
        time.sleep() here does NOT block asyncio event loop.
        """
        while True:
            try:
                gpu_info = gpu_manager.get_device_info()

                if gpu_info['device_type'] == 'cuda':
                    device_count = gpu_info['device_count']

                    for device_id in range(device_count):
                        try:
                            with torch.cuda.device(device_id):
                                # Get GPU utilization
                                utilization = torch.cuda.utilization(device_id)

                                # Get memory info
                                memory_info = torch.cuda.mem_get_info(device_id)
                                memory_used = memory_info[1] - memory_info[0]
                                memory_total = memory_info[1]
                                memory_utilization = (memory_used / memory_total) * 100

                                # Create profiling metrics
                                metrics = GPUProfileMetrics(
                                    device_id=device_id,
                                    kernel_time=time.time(),
                                    memory_bandwidth=0.0,  # Would need NVML for accurate measurement
                                    compute_utilization=float(utilization),
                                    memory_utilization=memory_utilization,
                                    power_consumption=None,  # Would need NVML
                                    temperature=None,  # Would need NVML
                                    timestamp=time.time()
                                )

                                with self.lock:
                                    self.profiling_data.append(metrics)

                                    # Keep only last 1000 measurements
                                    if len(self.profiling_data) > 1000:
                                        self.profiling_data = self.profiling_data[-1000:]

                        except Exception as e:
                            logger.debug(f"Profiling error for device {device_id}: {e}")

                time.sleep(0.1)  # 10Hz profiling (safe in daemon thread)

            except Exception as e:
                logger.error(f"Profiling worker error: {e}")
                time.sleep(1.0)  # Error backoff (safe in daemon thread)

    @contextmanager
    def gpu_stream_context(self, device_id: int = 0, priority: int = 0):
        """Context manager for GPU stream execution"""
        if device_id not in self.streams:
            # Fallback to default stream
            yield torch.cuda.current_stream(device_id) if torch.cuda.is_available() else None
            return

        # Find stream with matching priority
        stream = None
        for gpu_stream in self.streams[device_id]:
            if gpu_stream.priority == priority:
                stream = gpu_stream
                break

        if stream is None:
            # Fallback to first available stream
            stream = self.streams[device_id][0]

        with torch.cuda.stream(stream.stream):
            stream.active_operations += 1
            try:
                yield stream.stream
            finally:
                stream.active_operations -= 1

    def allocate_gpu_memory(self, size_bytes: int, device_id: int = 0, allocation_id: str = None) -> torch.Tensor:
        """Allocate GPU memory with pooling"""
        if device_id not in self.memory_pools:
            # Fallback to direct allocation
            return torch.empty(size_bytes, dtype=torch.uint8, device=f'cuda:{device_id}')

        pool = self.memory_pools[device_id]

        with self.lock:
            if pool.allocated_memory + size_bytes > pool.total_memory * 0.9:
                # Memory pressure - trigger garbage collection
                torch.cuda.empty_cache()
                torch.cuda.synchronize(device_id)

            try:
                tensor = torch.empty(size_bytes, dtype=torch.uint8, device=f'cuda:{device_id}')
                pool.allocated_memory += size_bytes
                pool.peak_memory = max(pool.peak_memory, pool.allocated_memory)

                if allocation_id:
                    pool.allocations[allocation_id] = size_bytes

                return tensor

            except torch.cuda.OutOfMemoryError:
                # Emergency cleanup
                torch.cuda.empty_cache()
                raise

    def free_gpu_memory(self, tensor: torch.Tensor, allocation_id: str = None):
        """Free GPU memory and update pool"""
        if not tensor.is_cuda:
            return

        device_id = tensor.device.index
        size_bytes = tensor.numel() * tensor.element_size()

        if device_id in self.memory_pools:
            pool = self.memory_pools[device_id]

            with self.lock:
                pool.allocated_memory = max(0, pool.allocated_memory - size_bytes)

                if allocation_id and allocation_id in pool.allocations:
                    del pool.allocations[allocation_id]

        # Explicitly free the tensor
        del tensor

    def parallel_gpu_computation(self, operations: List[Callable], device_id: int = 0) -> List[Any]:
        """Execute operations in parallel using GPU streams"""
        if device_id not in self.streams or len(self.streams[device_id]) < 2:
            # Fallback to sequential execution
            return [op() for op in operations]

        results = []
        streams = self.streams[device_id][:len(operations)]  # Use available streams

        for i, (op, stream) in enumerate(zip(operations, streams)):
            with torch.cuda.stream(stream.stream):
                result = op()
                results.append(result)

        # Synchronize all streams
        for stream in streams:
            stream.stream.synchronize()

        return results

    def get_memory_stats(self) -> Dict[int, Dict]:
        """Get detailed memory statistics for all GPUs"""
        stats = {}

        for device_id, pool in self.memory_pools.items():
            with self.lock:
                stats[device_id] = {
                    'total_memory_gb': pool.total_memory / (1024**3),
                    'allocated_memory_gb': pool.allocated_memory / (1024**3),
                    'peak_memory_gb': pool.peak_memory / (1024**3),
                    'available_memory_gb': (pool.total_memory - pool.allocated_memory) / (1024**3),
                    'utilization_percent': (pool.allocated_memory / pool.total_memory) * 100,
                    'allocation_count': len(pool.allocations)
                }

        return stats

    def get_profiling_stats(self, device_id: Optional[int] = None, last_n: int = 100) -> List[GPUProfileMetrics]:
        """Get recent profiling statistics"""
        with self.lock:
            if device_id is not None:
                return [m for m in self.profiling_data[-last_n:] if m.device_id == device_id]
            else:
                return self.profiling_data[-last_n:]

    def get_stream_stats(self) -> Dict[int, List[Dict]]:
        """Get statistics for all GPU streams"""
        stats = {}

        for device_id, streams in self.streams.items():
            stats[device_id] = []
            for stream in streams:
                stats[device_id].append({
                    'priority': stream.priority,
                    'active_operations': stream.active_operations,
                    'stream_id': id(stream.stream)
                })

        return stats

    def optimize_memory_usage(self):
        """Optimize memory usage across all GPUs"""
        for device_id in self.memory_pools.keys():
            try:
                with torch.cuda.device(device_id):
                    torch.cuda.empty_cache()
                    torch.cuda.synchronize(device_id)
            except Exception as e:
                logger.warning(f"Memory optimization failed for device {device_id}: {e}")

        logger.info("✅ Memory optimization completed")

    def get_system_status(self) -> Dict:
        """Get comprehensive GPU optimization system status"""
        gpu_info = gpu_manager.get_device_info()

        return {
            "gpu_available": gpu_info['device_available'],
            "device_type": gpu_info['device_type'],
            "device_count": gpu_info['device_count'],
            "streams_initialized": len(self.streams) > 0,
            "memory_pools_initialized": len(self.memory_pools) > 0,
            "profiling_active": len(self.profiling_data) > 0,
            "memory_stats": self.get_memory_stats(),
            "stream_stats": self.get_stream_stats(),
            "recent_profiling": len(self.get_profiling_stats(last_n=10))
        }

# Global advanced GPU optimizer instance
advanced_gpu_optimizer = AdvancedGPUOptimizer()

def get_advanced_gpu_optimizer() -> AdvancedGPUOptimizer:
    """Get the global advanced GPU optimizer instance"""
    return advanced_gpu_optimizer
