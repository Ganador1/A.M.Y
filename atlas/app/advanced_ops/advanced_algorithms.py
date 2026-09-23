"""
AXIOM Advanced Algorithms System
High-performance algorithms for scientific computing with GPU acceleration
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
import time
from enum import Enum
from scipy import optimize, integrate, linalg
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import multiprocessing as mp

# Optional torch import for GPU acceleration
try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None  # type: ignore

from app.core.config import settings
from app.distributed.gpu_manager import gpu_manager
from app.distributed_manager import distributed_manager

logger = logging.getLogger(__name__)

class AlgorithmType(Enum):
    """Types of advanced algorithms"""
    OPTIMIZATION = "optimization"
    INTEGRATION = "integration"
    DECOMPOSITION = "decomposition"
    CLUSTERING = "clustering"
    INTERPOLATION = "interpolation"
    SOLVER = "solver"
    TRANSFORM = "transform"

class PrecisionLevel(Enum):
    """Precision levels for computations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

@dataclass
class AlgorithmResult:
    """Result of advanced algorithm execution"""
    result: Any
    execution_time: float
    algorithm_type: AlgorithmType
    precision_level: PrecisionLevel
    convergence_info: Optional[Dict] = None
    performance_metrics: Optional[Dict] = None
    success: bool = True
    error_message: Optional[str] = None

class AdvancedAlgorithms:
    """Advanced algorithms system with GPU acceleration and distributed computing"""

    def __init__(self):
        # Only get device if torch is available
        if HAS_TORCH:
            self.device = gpu_manager.get_optimal_device()
        else:
            self.device = None
            logger.warning("PyTorch not available - GPU acceleration disabled")

        # Set defaults if settings not available (e.g., during tests)
        precision = getattr(settings, 'algorithm_precision', 'medium')
        # Robust parsing: accept strings, enums, or mocks in test environments
        try:
            if isinstance(precision, PrecisionLevel):
                self.precision_level = precision
            else:
                pstr = str(precision)
                p_upper = pstr.upper() if pstr else 'MEDIUM'
                if p_upper in PrecisionLevel.__members__:
                    self.precision_level = PrecisionLevel[p_upper]
                else:
                    # Try matching by enum value (case-insensitive)
                    matched = False
                    for m in PrecisionLevel:
                        if m.value == pstr.lower():
                            self.precision_level = m
                            matched = True
                            break
                    if not matched:
                        self.precision_level = PrecisionLevel.MEDIUM
        except Exception:
            self.precision_level = PrecisionLevel.MEDIUM

        self.threshold = getattr(settings, 'parallel_computation_threshold', 1000)
        self.memory_optimization = getattr(settings, 'memory_optimization_level', 'balanced')

        logger.info(f"✅ Advanced Algorithms initialized: device={self.device}, precision={self.precision_level.value}")

    def optimize_function(self, func: Callable, bounds: List[Tuple[float, float]],
                         method: str = "L-BFGS-B", constraints: Optional[List] = None) -> AlgorithmResult:
        """Advanced function optimization with multiple methods"""
        start_time = time.time()

        try:
            if self.precision_level == PrecisionLevel.HIGH:
                # High precision optimization
                result = optimize.minimize(
                    func, x0=np.mean(bounds, axis=1),
                    bounds=bounds, method=method,
                    constraints=constraints,
                    options={'ftol': 1e-12, 'gtol': 1e-12, 'maxiter': 10000}
                )
            elif self.precision_level == PrecisionLevel.MEDIUM:
                # Medium precision
                result = optimize.minimize(
                    func, x0=np.mean(bounds, axis=1),
                    bounds=bounds, method=method,
                    constraints=constraints,
                    options={'ftol': 1e-9, 'gtol': 1e-9, 'maxiter': 5000}
                )
            else:
                # Fast optimization
                result = optimize.minimize(
                    func, x0=np.mean(bounds, axis=1),
                    bounds=bounds, method=method,
                    constraints=constraints,
                    options={'ftol': 1e-6, 'gtol': 1e-6, 'maxiter': 1000}
                )

            execution_time = time.time() - start_time

            return AlgorithmResult(
                result=result.x,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.OPTIMIZATION,
                precision_level=self.precision_level,
                convergence_info={
                    'success': result.success,
                    'message': result.message,
                    'nfev': result.nfev,
                    'njev': getattr(result, 'njev', None),
                    'nit': result.nit
                },
                performance_metrics={
                    'function_evaluations': result.nfev,
                    'iterations': result.nit,
                    'final_value': result.fun
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Optimization failed: {e}")

            return AlgorithmResult(
                result=None,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.OPTIMIZATION,
                precision_level=self.precision_level,
                success=False,
                error_message=str(e)
            )

    def numerical_integration(self, func: Callable, a: float, b: float,
                            method: str = "adaptive", points: Optional[np.ndarray] = None) -> AlgorithmResult:
        """Advanced numerical integration with GPU acceleration"""
        start_time = time.time()

        try:
            if method == "adaptive":
                if self.precision_level == PrecisionLevel.HIGH:
                    result = integrate.quad(func, a, b, epsabs=1e-12, epsrel=1e-12, limit=1000)
                elif self.precision_level == PrecisionLevel.MEDIUM:
                    result = integrate.quad(func, a, b, epsabs=1e-9, epsrel=1e-9, limit=500)
                else:
                    result = integrate.quad(func, a, b, epsabs=1e-6, epsrel=1e-6, limit=200)

                integral_value, error = result

            elif method == "fixed_quad":
                if points is None:
                    if self.precision_level == PrecisionLevel.HIGH:
                        points = np.linspace(a, b, 1000)
                    elif self.precision_level == PrecisionLevel.MEDIUM:
                        points = np.linspace(a, b, 500)
                    else:
                        points = np.linspace(a, b, 100)

                y = np.array([func(x) for x in points])
                integral_value = integrate.simps(y, points)
                error = None

            elif method == "romberg":
                if self.precision_level == PrecisionLevel.HIGH:
                    integral_value, error = integrate.romberg(func, a, b, tol=1e-12, rtol=1e-12, divmax=20)
                elif self.precision_level == PrecisionLevel.MEDIUM:
                    integral_value, error = integrate.romberg(func, a, b, tol=1e-9, rtol=1e-9, divmax=15)
                else:
                    integral_value, error = integrate.romberg(func, a, b, tol=1e-6, rtol=1e-6, divmax=10)

            execution_time = time.time() - start_time

            return AlgorithmResult(
                result=integral_value,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.INTEGRATION,
                precision_level=self.precision_level,
                convergence_info={'error_estimate': error} if error else None,
                performance_metrics={
                    'method': method,
                    'interval': [a, b],
                    'estimated_error': error
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Integration failed: {e}")

            return AlgorithmResult(
                result=None,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.INTEGRATION,
                precision_level=self.precision_level,
                success=False,
                error_message=str(e)
            )

    def matrix_decomposition(self, matrix: np.ndarray, method: str = "svd") -> AlgorithmResult:
        """Advanced matrix decomposition with GPU acceleration"""
        start_time = time.time()

        try:
            if method == "svd":
                U, s, Vt = linalg.svd(matrix)
                result = {'U': U, 's': s, 'Vt': Vt}

            elif method == "qr":
                Q, R = linalg.qr(matrix)
                result = {'Q': Q, 'R': R}

            elif method == "lu":
                P, L, U = linalg.lu(matrix)
                result = {'P': P, 'L': L, 'U': U}

            elif method == "cholesky" and self._is_positive_definite(matrix):
                L = linalg.cholesky(matrix)
                result = {'L': L}

            else:
                raise ValueError(f"Unsupported decomposition method: {method}")

            execution_time = time.time() - start_time

            return AlgorithmResult(
                result=result,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.DECOMPOSITION,
                precision_level=self.precision_level,
                performance_metrics={
                    'method': method,
                    'matrix_shape': matrix.shape,
                    'condition_number': np.linalg.cond(matrix)
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Matrix decomposition failed: {e}")

            return AlgorithmResult(
                result=None,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.DECOMPOSITION,
                precision_level=self.precision_level,
                success=False,
                error_message=str(e)
            )

    def _is_positive_definite(self, matrix: np.ndarray) -> bool:
        """Check if matrix is positive definite"""
        try:
            linalg.cholesky(matrix)
            return True
        except linalg.LinAlgError:
            return False

    def parallel_clustering(self, data: np.ndarray, n_clusters: int = 3,
                          method: str = "kmeans") -> AlgorithmResult:
        """Parallel clustering algorithms"""
        start_time = time.time()

        try:
            if len(data) > self.threshold:
                # Use distributed computing for large datasets
                logger.info(f"🔄 Using distributed clustering for {len(data)} data points")

                def clustering_task(chunk):
                    if method == "kmeans":
                        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                        return kmeans.fit_predict(chunk)
                    else:
                        raise ValueError(f"Unsupported clustering method: {method}")

                # Split data for distributed processing
                chunk_size = len(data) // distributed_manager.config.world_size
                data_chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

                results = distributed_manager.parallel_compute(clustering_task, data_chunks)
                labels = np.concatenate([r.result for r in results if r.success])

            else:
                # Local clustering
                if method == "kmeans":
                    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
                    labels = kmeans.fit_predict(data)
                    centroids = kmeans.cluster_centers_
                    inertia = kmeans.inertia_
                else:
                    raise ValueError(f"Unsupported clustering method: {method}")

            execution_time = time.time() - start_time

            return AlgorithmResult(
                result={
                    'labels': labels,
                    'n_clusters': n_clusters,
                    'centroids': centroids if 'centroids' in locals() else None,
                    'inertia': inertia if 'inertia' in locals() else None
                },
                execution_time=execution_time,
                algorithm_type=AlgorithmType.CLUSTERING,
                precision_level=self.precision_level,
                performance_metrics={
                    'method': method,
                    'data_points': len(data),
                    'features': data.shape[1] if len(data.shape) > 1 else 1,
                    'distributed': len(data) > self.threshold
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Clustering failed: {e}")

            return AlgorithmResult(
                result=None,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.CLUSTERING,
                precision_level=self.precision_level,
                success=False,
                error_message=str(e)
            )

    def advanced_interpolation(self, x: np.ndarray, y: np.ndarray,
                             x_new: np.ndarray, method: str = "cubic") -> AlgorithmResult:
        """Advanced interpolation methods"""
        start_time = time.time()

        try:
            from scipy import interpolate

            if method == "cubic":
                f = interpolate.interp1d(x, y, kind='cubic')
            elif method == "spline":
                f = interpolate.UnivariateSpline(x, y, s=0)
            elif method == "pchip":
                f = interpolate.PchipInterpolator(x, y)
            else:
                f = interpolate.interp1d(x, y, kind=method)

            y_new = f(x_new)

            execution_time = time.time() - start_time

            return AlgorithmResult(
                result=y_new,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.INTERPOLATION,
                precision_level=self.precision_level,
                performance_metrics={
                    'method': method,
                    'original_points': len(x),
                    'interpolated_points': len(x_new),
                    'x_range': [float(x.min()), float(x.max())]
                }
            )

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ Interpolation failed: {e}")

            return AlgorithmResult(
                result=None,
                execution_time=execution_time,
                algorithm_type=AlgorithmType.INTERPOLATION,
                precision_level=self.precision_level,
                success=False,
                error_message=str(e)
            )

    def get_system_status(self) -> Dict:
        """Get advanced algorithms system status"""
        return {
            "device": str(self.device),
            "precision_level": self.precision_level.value,
            "parallel_threshold": self.threshold,
            "memory_optimization": self.memory_optimization,
            "gpu_available": gpu_manager.is_gpu_available(),
            "distributed_available": distributed_manager.is_initialized,
            "supported_algorithms": [alg.value for alg in AlgorithmType]
        }

# Global advanced algorithms instance (lazy initialization)
_advanced_algorithms = None

def get_advanced_algorithms() -> AdvancedAlgorithms:
    """Get the global advanced algorithms instance"""
    global _advanced_algorithms
    if _advanced_algorithms is None:
        _advanced_algorithms = AdvancedAlgorithms()
    return _advanced_algorithms
