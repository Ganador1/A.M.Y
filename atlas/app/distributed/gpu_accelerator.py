"""
AXIOM Advanced GPU Acceleration System
High-performance GPU acceleration for scientific computations
"""

# Optional torch import for deep learning support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore
import logging
import asyncio
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from contextlib import contextmanager
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import gc

from app.distributed.gpu_manager import gpu_manager, get_optimal_device

logger = logging.getLogger(__name__)

@dataclass
class GPUOperation:
    """Represents a GPU operation with metadata"""
    operation_id: str
    operation_type: str
    device: torch.device
    start_time: float
    estimated_memory_mb: float
    priority: int = 1
    callback: Optional[Callable] = None

@dataclass
class GPUMemoryStats:
    """GPU memory statistics"""
    allocated_mb: float
    reserved_mb: float
    total_mb: float
    available_mb: float
    fragmentation_ratio: float

@dataclass
class GPUPerformanceMetrics:
    """GPU performance metrics"""
    operations_completed: int = 0
    total_compute_time: float = 0.0
    memory_transfers: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    average_memory_utilization: float = 0.0

class GPUMemoryManager:
    """Advanced GPU memory management system"""

    def __init__(self, device: torch.device):
        self.device = device
        self.memory_threshold = 0.85  # 85% memory usage threshold
        self.allocation_history: List[Dict] = []
        self.memory_pool: Dict[str, torch.Tensor] = {}

    def get_memory_stats(self) -> GPUMemoryStats:
        """Get current GPU memory statistics"""
        if self.device.type == "cuda":
            allocated = torch.cuda.memory_allocated(self.device) / (1024**2)
            reserved = torch.cuda.memory_reserved(self.device) / (1024**2)
            total = torch.cuda.get_device_properties(self.device).total_memory / (1024**2)
            available = total - reserved
            fragmentation = allocated / reserved if reserved > 0 else 0.0
        elif self.device.type == "mps":
            # MPS memory info is limited
            allocated = 0.0
            reserved = 0.0
            total = gpu_manager.system_info.gpu_info.memory_gb * 1024 if gpu_manager.system_info.gpu_info.memory_gb else 0.0
            available = total
            fragmentation = 0.0
        else:
            return GPUMemoryStats(0, 0, 0, 0, 0)

        return GPUMemoryStats(
            allocated_mb=allocated,
            reserved_mb=reserved,
            total_mb=total,
            available_mb=available,
            fragmentation_ratio=fragmentation
        )

    def should_gc(self) -> bool:
        """Check if garbage collection should be triggered"""
        stats = self.get_memory_stats()
        if stats.total_mb == 0:
            return False
        usage_ratio = stats.reserved_mb / stats.total_mb
        return usage_ratio > self.memory_threshold

    def optimize_memory(self):
        """Optimize GPU memory usage"""
        if self.device.type == "cuda":
            torch.cuda.empty_cache()
        elif self.device.type == "mps":
            # MPS memory management is automatic
            pass

        # Force Python garbage collection
        gc.collect()

        logger.info(f"GPU memory optimized for device {self.device}")

    @contextmanager
    def memory_context(self, operation_name: str, estimated_mb: float):
        """Context manager for memory-aware operations"""
        start_time = time.time()
        initial_stats = self.get_memory_stats()

        try:
            yield
        finally:
            end_time = time.time()
            final_stats = self.get_memory_stats()

            # Record memory usage
            memory_used = final_stats.allocated_mb - initial_stats.allocated_mb
            duration = end_time - start_time

            self.allocation_history.append({
                "operation": operation_name,
                "memory_used_mb": memory_used,
                "duration_sec": duration,
                "timestamp": end_time
            })

            # Clean up old history (keep last 1000 entries)
            if len(self.allocation_history) > 1000:
                self.allocation_history = self.allocation_history[-1000:]

class GPUAccelerator:
    """Advanced GPU acceleration system for scientific computations"""

    def __init__(self):
        self.device = get_optimal_device()
        self.memory_manager = GPUMemoryManager(self.device)
        self.operation_queue: List[GPUOperation] = []
        self.active_operations: Dict[str, GPUOperation] = {}
        self.metrics = GPUPerformanceMetrics()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._lock = threading.Lock()

        # Scientific operation accelerators
        self.scientific_kernels = self._load_scientific_kernels()

        logger.info(f"GPU Accelerator initialized on device: {self.device}")

    def _load_scientific_kernels(self) -> Dict[str, Callable]:
        """Load optimized kernels for scientific operations"""
        kernels = {}

        # Matrix operations kernel
        @torch.jit.script
        def matrix_multiply_kernel(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
            return torch.matmul(a, b)

        kernels["matrix_multiply"] = matrix_multiply_kernel

        # Vector operations kernel
        @torch.jit.script
        def vector_operations_kernel(v: torch.Tensor, operation: str) -> torch.Tensor:
            if operation == "normalize":
                return torch.nn.functional.normalize(v, dim=-1)
            elif operation == "square":
                return torch.square(v)
            elif operation == "sqrt":
                return torch.sqrt(v)
            else:
                return v

        kernels["vector_ops"] = vector_operations_kernel

        # Scientific computing kernel
        @torch.jit.script
        def scientific_kernel(data: torch.Tensor, operation: str) -> torch.Tensor:
            if operation == "fft":
                return torch.fft.fft(data)
            elif operation == "ifft":
                return torch.fft.ifft(data)
            elif operation == "gradient":
                return torch.gradient(data, dim=0)[0]
            else:
                return data

        kernels["scientific"] = scientific_kernel

        return kernels

    async def accelerate_operation(self, operation_type: str, data: Any,
                                 **kwargs) -> Any:
        """Accelerate a scientific operation using GPU"""
        operation_id = f"{operation_type}_{time.time()}_{id(data)}"

        # Estimate memory requirements
        estimated_memory = self._estimate_memory_requirement(operation_type, data)

        operation = GPUOperation(
            operation_id=operation_id,
            operation_type=operation_type,
            device=self.device,
            start_time=time.time(),
            estimated_memory_mb=estimated_memory,
            priority=kwargs.get('priority', 1)
        )

        with self.memory_manager.memory_context(operation_id, estimated_memory):
            try:
                # Move data to GPU if needed
                gpu_data = self._prepare_data_for_gpu(data)

                # Execute operation
                result = await self._execute_gpu_operation(operation_type, gpu_data, **kwargs)

                # Move result back to CPU if needed
                result = self._prepare_data_for_cpu(result, kwargs.get('return_cpu', True))

                # Update metrics
                self._update_metrics(operation, success=True)

                return result

            except Exception as e:
                logger.error(f"GPU operation failed: {e}")
                self._update_metrics(operation, success=False)
                raise

    def _estimate_memory_requirement(self, operation_type: str, data: Any) -> float:
        """Estimate memory requirements for operation"""
        if isinstance(data, torch.Tensor):
            size_mb = data.numel() * data.element_size() / (1024**2)
        elif isinstance(data, np.ndarray):
            size_mb = data.nbytes / (1024**2)
        elif isinstance(data, list):
            # Estimate for list of tensors/arrays
            size_mb = sum(
                (item.numel() * item.element_size() / (1024**2))
                if isinstance(item, torch.Tensor)
                else (item.nbytes / (1024**2) if isinstance(item, np.ndarray) else 1)
                for item in data
            )
        else:
            size_mb = 10  # Default estimate

        # Add overhead based on operation type
        overhead_factors = {
            "matrix_multiply": 3.0,
            "fft": 2.5,
            "gradient": 2.0,
            "scientific": 2.0,
            "vector_ops": 1.5
        }

        factor = overhead_factors.get(operation_type, 1.5)
        return size_mb * factor

    def _prepare_data_for_gpu(self, data: Any) -> Any:
        """Prepare data for GPU computation"""
        if isinstance(data, torch.Tensor):
            if data.device != self.device:
                return data.to(self.device)
            return data
        elif isinstance(data, np.ndarray):
            return torch.from_numpy(data).to(self.device)
        elif isinstance(data, list):
            return [self._prepare_data_for_gpu(item) for item in data]
        else:
            return data

    def _prepare_data_for_cpu(self, data: Any, return_cpu: bool = True) -> Any:
        """Prepare data for CPU usage"""
        if not return_cpu:
            return data

        if isinstance(data, torch.Tensor):
            if data.device != torch.device("cpu"):
                return data.cpu()
            return data
        elif isinstance(data, list):
            return [self._prepare_data_for_cpu(item, return_cpu) for item in data]
        else:
            return data

    async def _execute_gpu_operation(self, operation_type: str, data: Any, **kwargs) -> Any:
        """Execute GPU operation in thread pool"""
        loop = asyncio.get_event_loop()

        if operation_type in self.scientific_kernels:
            kernel = self.scientific_kernels[operation_type]
            if operation_type == "matrix_multiply" and isinstance(data, list) and len(data) == 2:
                # Special handling for matrix multiply with two tensors
                return await loop.run_in_executor(
                    self.executor,
                    lambda: kernel(data[0], data[1])
                )
            else:
                return await loop.run_in_executor(
                    self.executor,
                    lambda: kernel(data, kwargs.get('sub_operation', ''))
                )
        else:
            # Generic GPU operation
            return await loop.run_in_executor(
                self.executor,
                self._generic_gpu_operation,
                data, operation_type, kwargs
            )

    def _generic_gpu_operation(self, data: Any, operation_type: str, kwargs: Dict) -> Any:
        """Generic GPU operation handler"""
        try:
            if operation_type == "matrix_multiply":
                if isinstance(data, list) and len(data) == 2:
                    return torch.matmul(data[0], data[1])
                else:
                    return data

            elif operation_type == "vector_ops":
                sub_op = kwargs.get('sub_operation', 'normalize')
                if sub_op == "normalize":
                    return torch.nn.functional.normalize(data, dim=-1)
                elif sub_op == "square":
                    return torch.square(data)
                elif sub_op == "sqrt":
                    return torch.sqrt(torch.abs(data))

            elif operation_type == "scientific":
                sub_op = kwargs.get('sub_operation', 'fft')
                if sub_op == "fft":
                    return torch.fft.fft(data)
                elif sub_op == "ifft":
                    return torch.fft.ifft(data)
                elif sub_op == "gradient":
                    return torch.gradient(data, dim=0)[0]

            # Default: return data unchanged
            return data

        except Exception as e:
            logger.error(f"Error in GPU operation {operation_type}: {e}")
            raise

    def _update_metrics(self, operation: GPUOperation, success: bool):
        """Update performance metrics"""
        duration = time.time() - operation.start_time

        with self._lock:
            if success:
                self.metrics.operations_completed += 1
                self.metrics.total_compute_time += duration

            # Update memory utilization
            memory_stats = self.memory_manager.get_memory_stats()
            if memory_stats.total_mb > 0:
                utilization = memory_stats.reserved_mb / memory_stats.total_mb
                if self.metrics.operations_completed > 0:
                    self.metrics.average_memory_utilization = (
                        (self.metrics.average_memory_utilization * (self.metrics.operations_completed - 1) + utilization)
                        / self.metrics.operations_completed
                    )
                else:
                    self.metrics.average_memory_utilization = utilization

    def get_performance_stats(self) -> Dict:
        """Get comprehensive performance statistics"""
        memory_stats = self.memory_manager.get_memory_stats()

        return {
            "device": str(self.device),
            "memory_stats": {
                "allocated_mb": memory_stats.allocated_mb,
                "reserved_mb": memory_stats.reserved_mb,
                "total_mb": memory_stats.total_mb,
                "available_mb": memory_stats.available_mb,
                "fragmentation_ratio": memory_stats.fragmentation_ratio
            },
            "performance_metrics": {
                "operations_completed": self.metrics.operations_completed,
                "total_compute_time_sec": self.metrics.total_compute_time,
                "average_operation_time_sec": (
                    self.metrics.total_compute_time / max(self.metrics.operations_completed, 1)
                ),
                "memory_transfers": self.metrics.memory_transfers,
                "cache_hits": self.metrics.cache_hits,
                "cache_misses": self.metrics.cache_misses,
                "average_memory_utilization": self.metrics.average_memory_utilization
            },
            "memory_history": self.memory_manager.allocation_history[-10:]  # Last 10 operations
        }

    def optimize_for_workload(self, workload_type: str):
        """Optimize GPU settings for specific workload"""
        if workload_type == "scientific":
            if self.device.type == "cuda":
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
            self.memory_manager.memory_threshold = 0.90  # Allow higher memory usage

        elif workload_type == "training":
            if self.device.type == "cuda":
                torch.backends.cudnn.benchmark = False
                torch.backends.cudnn.deterministic = True
            self.memory_manager.memory_threshold = 0.80  # More conservative

        elif workload_type == "inference":
            if self.device.type == "cuda":
                torch.backends.cudnn.benchmark = True
                torch.backends.cudnn.deterministic = False
            self.memory_manager.memory_threshold = 0.85

        logger.info(f"GPU optimized for {workload_type} workload")

    def cleanup(self):
        """Clean up GPU resources"""
        self.memory_manager.optimize_memory()
        self.executor.shutdown(wait=True)
        logger.info("GPU Accelerator cleaned up")

# Global GPU accelerator instance
gpu_accelerator = GPUAccelerator()

def get_gpu_accelerator() -> GPUAccelerator:
    """Get the global GPU accelerator instance"""
    return gpu_accelerator

async def accelerate_scientific_operation(operation_type: str, data: Any, **kwargs) -> Any:
    """Convenience function for scientific GPU acceleration"""
    return await gpu_accelerator.accelerate_operation(operation_type, data, **kwargs)
