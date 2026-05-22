"""
AXIOM GPU Manager
Advanced GPU detection and management system for CUDA, MPS, and CPU
"""

import logging
import warnings
import os
from typing import Dict, Optional, List
from dataclasses import dataclass
import psutil
import platform

# Optional torch import for GPU support
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore

from app.config import settings

logger = logging.getLogger(__name__)

@dataclass
class GPUInfo:
    """GPU device information"""
    available: bool
    device_type: str  # 'cuda', 'mps', 'cpu'
    device_count: int
    device_names: List[str]
    memory_gb: Optional[float]
    compute_capability: Optional[str]
    driver_version: Optional[str]

@dataclass
class SystemInfo:
    """System hardware information"""
    platform: str
    cpu_count: int
    total_memory_gb: float
    available_memory_gb: float
    gpu_info: GPUInfo

class GPUManager:
    """Advanced GPU detection and management system"""

    def __init__(self):
        self.system_info = self._detect_system()
        self._configure_gpu_settings()

    def _detect_system(self) -> SystemInfo:
        """Detect complete system information"""
        platform_name = platform.system()

        # CPU information with tolerancia a entornos restringidos
        try:
            cpu_count = psutil.cpu_count(logical=True)
            if cpu_count is None:
                raise ValueError("psutil.cpu_count returned None")
        except Exception as exc:  # pragma: no cover - fallback defensivo
            logger.warning("psutil.cpu_count falló (%s); usando os.cpu_count()", exc)
            cpu_count = os.cpu_count() or 1

        try:
            memory = psutil.virtual_memory()
            total_memory_gb = memory.total / (1024**3)
            available_memory_gb = memory.available / (1024**3)
        except Exception as exc:  # pragma: no cover
            logger.warning("psutil.virtual_memory falló (%s); usando valores por defecto", exc)
            total_memory_gb = float(os.getenv("AXIOM_SYSTEM_MEMORY_GB", "0") or 0)
            available_memory_gb = total_memory_gb

        # GPU detection
        gpu_info = self._detect_gpu()

        return SystemInfo(
            platform=platform_name,
            cpu_count=cpu_count,
            total_memory_gb=total_memory_gb,
            available_memory_gb=available_memory_gb,
            gpu_info=gpu_info
        )

    def _detect_gpu(self) -> GPUInfo:
        """Advanced GPU detection for CUDA, MPS, and fallback to CPU"""
        device_names = []
        memory_gb = None
        compute_capability = None
        driver_version = None

        # Check if torch is available
        if not HAS_TORCH or torch is None:
            logger.warning("PyTorch not available - GPU detection disabled")
            return GPUInfo(
                available=False,
                device_type="cpu",
                device_count=0,
                device_names=["CPU (torch not available)"],
                memory_gb=None,
                compute_capability=None,
                driver_version=None
            )

        # 1. Try CUDA first (NVIDIA GPUs)
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            device_names = [torch.cuda.get_device_name(i) for i in range(device_count)]

            # Get memory info for first GPU
            if device_count > 0:
                memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                major = torch.cuda.get_device_properties(0).major
                minor = torch.cuda.get_device_properties(0).minor
                compute_capability = f"{major}.{minor}"

            try:
                driver_version = torch.version.cuda
            except Exception:
                driver_version = "Unknown"

            logger.info(f"✅ CUDA GPU detected: {device_count} device(s), {memory_gb:.1f}GB memory")
            return GPUInfo(
                available=True,
                device_type="cuda",
                device_count=device_count,
                device_names=device_names,
                memory_gb=memory_gb,
                compute_capability=compute_capability,
                driver_version=driver_version
            )

        # 2. Try MPS (Apple Silicon)
        try:
            if torch.backends.mps.is_available():
                # Test MPS functionality
                test_tensor = torch.tensor([1.0, 2.0], device='mps')
                test_result = test_tensor * 2
                del test_tensor, test_result

                # MPS doesn't provide detailed device info like CUDA
                device_names = ["Apple Silicon GPU (MPS)"]
                memory_gb = self._estimate_mps_memory()

                logger.info(f"✅ MPS GPU detected: Apple Silicon, ~{memory_gb:.1f}GB estimated memory")
                return GPUInfo(
                    available=True,
                    device_type="mps",
                    device_count=1,
                    device_names=device_names,
                    memory_gb=memory_gb,
                    compute_capability="MPS",
                    driver_version="Apple Silicon"
                )
        except Exception as e:
            logger.warning(f"MPS detected but not functional: {e}")
            # Continue to CPU fallback

        # 3. CPU fallback
        logger.info("⚠️  No GPU detected, using CPU")
        return GPUInfo(
            available=False,
            device_type="cpu",
            device_count=1,
            device_names=["CPU"],
            memory_gb=self.system_info.total_memory_gb if hasattr(self, 'system_info') else None,
            compute_capability=None,
            driver_version=None
        )

    def _estimate_mps_memory(self) -> float:
        """Estimate MPS memory based on system RAM"""
        # MPS typically uses unified memory, estimate based on system RAM
        system_memory = psutil.virtual_memory().total / (1024**3)

        # Conservative estimate: MPS can use up to ~75% of system memory
        estimated_mps_memory = system_memory * 0.75

        # Cap at reasonable maximum (Apple Silicon GPUs typically have 16-32GB effective)
        return min(estimated_mps_memory, 32.0)

    def _configure_gpu_settings(self):
        """Configure optimal GPU settings"""
        if self.system_info.gpu_info.device_type == "cuda":
            # CUDA optimizations
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.deterministic = False

            # Set memory fraction if needed
            if self.system_info.gpu_info.memory_gb and self.system_info.gpu_info.memory_gb < 8:
                # For GPUs with less than 8GB, reserve some memory
                torch.cuda.set_per_process_memory_fraction(0.8)

        elif self.system_info.gpu_info.device_type == "mps":
            # MPS specific settings
            os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = str(settings.pytorch_mps_high_watermark_ratio)

        # Suppress common GPU warnings
        self._suppress_gpu_warnings()

    def _suppress_gpu_warnings(self):
        """Suppress common GPU-related warnings"""
        warnings.filterwarnings("ignore", message=".*MPS.*cannot be used.*")
        warnings.filterwarnings("ignore", message=".*CUDA.*not available.*")
        warnings.filterwarnings("ignore", message=".*cuDNN.*")
        warnings.filterwarnings("ignore", message=".*CUDNN.*")

    def get_optimal_device(self) -> "torch.device":  # type: ignore
        """Get the optimal device for computations"""
        if not HAS_TORCH or torch is None:
            # Return a mock device string when torch not available
            logger.warning("PyTorch not available - returning CPU mock device")
            return "cpu"  # type: ignore

        gpu_info = self.system_info.gpu_info

        if gpu_info.device_type == "cuda":
            return torch.device("cuda:0")
        elif gpu_info.device_type == "mps":
            return torch.device("mps")
        else:
            return torch.device("cpu")

    def get_device_info(self) -> Dict:
        """Get comprehensive device information"""
        gpu_info = self.system_info.gpu_info

        return {
            "device_type": gpu_info.device_type,
            "device_available": gpu_info.available,
            "device_count": gpu_info.device_count,
            "device_names": gpu_info.device_names,
            "memory_gb": gpu_info.memory_gb,
            "compute_capability": gpu_info.compute_capability,
            "driver_version": gpu_info.driver_version,
            "platform": self.system_info.platform,
            "cpu_count": self.system_info.cpu_count,
            "system_memory_gb": self.system_info.total_memory_gb,
            "available_memory_gb": self.system_info.available_memory_gb
        }

    def is_gpu_available(self) -> bool:
        """Check if any GPU is available"""
        return self.system_info.gpu_info.available

    def get_memory_info(self) -> Dict:
        """Get memory information for current device"""
        device = self.get_optimal_device()

        if device.type == "cuda":
            memory_allocated = torch.cuda.memory_allocated(device) / (1024**3)
            memory_reserved = torch.cuda.memory_reserved(device) / (1024**3)
            return {
                "allocated_gb": memory_allocated,
                "reserved_gb": memory_reserved,
                "total_gb": self.system_info.gpu_info.memory_gb
            }
        elif device.type == "mps":
            # MPS memory info is limited
            return {
                "allocated_gb": None,
                "reserved_gb": None,
                "total_gb": self.system_info.gpu_info.memory_gb
            }
        else:
            return {
                "allocated_gb": None,
                "reserved_gb": None,
                "total_gb": self.system_info.total_memory_gb
            }

# Global GPU manager instance
gpu_manager = GPUManager()

def get_gpu_manager() -> GPUManager:
    """Get the global GPU manager instance"""
    return gpu_manager

def get_optimal_device() -> "torch.device":  # type: ignore
    """Convenience function to get optimal device"""
    if not HAS_TORCH:
        logger.warning("PyTorch not available - returning CPU mock device")
        return "cpu"  # type: ignore
    return gpu_manager.get_optimal_device()

def is_gpu_available() -> bool:
    """Convenience function to check GPU availability"""
    return gpu_manager.is_gpu_available()
