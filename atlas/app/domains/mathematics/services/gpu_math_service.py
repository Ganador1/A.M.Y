"""
GPU Mathematics Service
======================

Servicio de aceleración GPU para operaciones matemáticas intensivas.

Este servicio proporciona aceleración por GPU para operaciones matemáticas
que requieren alto rendimiento computacional, incluyendo:

- Multiplicación masiva de matrices
- Transformadas rápidas de Fourier (FFT)
- Operaciones vectoriales paralelas
- Álgebra lineal acelerada
- Simulaciones numéricas intensivas

Tecnologías Soportadas:
----------------------
- NVIDIA CUDA (CuPy, PyCUDA)
- OpenCL (PyOpenCL)
- Numba CUDA JIT
- Fallback automático a CPU

Ejemplos de Uso:
---------------
```python
from app.domains.mathematics.services.gpu_math_service import GPUMathService
from app.exceptions.domain.mathematics import MathematicsError

# Inicializar servicio
gpu_service = GPUMathService()

# Verificar disponibilidad de GPU
if gpu_service.is_gpu_available():
    # Multiplicación de matrices grandes
    result = await gpu_service.matrix_multiply_gpu(matrix_a, matrix_b)
    
    # FFT acelerada
    fft_result = await gpu_service.fft_gpu(signal_data)
    
    # Operaciones vectoriales
    vector_result = await gpu_service.vector_operations_gpu(vectors, operation="dot")
```

Requisitos:
----------
- NVIDIA GPU con CUDA 11.0+ (opcional)
- CuPy >= 10.0.0 (opcional)
- NumPy >= 1.20.0
- SciPy >= 1.7.0

Autor: AXIOM Mathematics Team
Fecha: Enero 2024
Versión: 1.0.0
"""

import asyncio
import logging
import time
import warnings
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from scipy import fft

# Configurar logging
logger = logging.getLogger(__name__)

# Intentar importar dependencias GPU (opcionales)
try:
    import cupy as cp
    CUPY_AVAILABLE = True
    logger.info("CuPy disponible - Aceleración CUDA habilitada")
except ImportError:
    CUPY_AVAILABLE = False
    logger.info("CuPy no disponible - Usando fallback CPU")

try:
    import numba
    from numba import cuda
    NUMBA_CUDA_AVAILABLE = cuda.is_available()
    logger.info(f"Numba CUDA disponible: {NUMBA_CUDA_AVAILABLE}")
except ImportError:
    NUMBA_CUDA_AVAILABLE = False
    logger.info("Numba CUDA no disponible")

try:
    import pyopencl as cl
    OPENCL_AVAILABLE = True
    logger.info("PyOpenCL disponible - Soporte OpenCL habilitado")
except ImportError:
    OPENCL_AVAILABLE = False
    logger.info("PyOpenCL no disponible")


class GPUMathService:
    """
    Servicio de matemáticas aceleradas por GPU.
    
    Proporciona operaciones matemáticas de alto rendimiento utilizando
    aceleración GPU cuando está disponible, con fallback automático a CPU.
    """
    
    def __init__(self):
        """Inicializar el servicio GPU."""
        self.gpu_available = self._check_gpu_availability()
        self.cuda_available = CUPY_AVAILABLE
        self.opencl_available = OPENCL_AVAILABLE
        self.numba_cuda_available = NUMBA_CUDA_AVAILABLE
        
        # Configurar contexto GPU si está disponible
        if self.cuda_available:
            try:
                self.cuda_device = cp.cuda.Device(0)
                self.cuda_context = self.cuda_device.use()
                logger.info(f"GPU CUDA inicializada: {cp.cuda.runtime.getDeviceProperties(0)['name'].decode()}")
            except MathematicsError as e:
                logger.warning(f"Error inicializando CUDA: {e}")
                self.cuda_available = False
        
        # Estadísticas de rendimiento
        self.performance_stats = {
            "operations_count": 0,
            "gpu_operations": 0,
            "cpu_fallback": 0,
            "total_gpu_time": 0.0,
            "total_cpu_time": 0.0
        }
    
    def _check_gpu_availability(self) -> bool:
        """Verificar disponibilidad de GPU."""
        return CUPY_AVAILABLE or OPENCL_AVAILABLE or NUMBA_CUDA_AVAILABLE
    
    def is_gpu_available(self) -> bool:
        """Verificar si GPU está disponible."""
        return self.gpu_available
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Obtener información detallada de GPU."""
        info = {
            "gpu_available": self.gpu_available,
            "cuda_available": self.cuda_available,
            "opencl_available": self.opencl_available,
            "numba_cuda_available": self.numba_cuda_available,
            "devices": []
        }
        
        if self.cuda_available:
            try:
                device_count = cp.cuda.runtime.getDeviceCount()
                for i in range(device_count):
                    props = cp.cuda.runtime.getDeviceProperties(i)
                    info["devices"].append({
                        "id": i,
                        "name": props["name"].decode(),
                        "compute_capability": f"{props['major']}.{props['minor']}",
                        "total_memory": props["totalGlobalMem"],
                        "multiprocessor_count": props["multiProcessorCount"]
                    })
            except MathematicsError as e:
                logger.error(f"Error obteniendo información GPU: {e}")
        
        return info
    
    async def matrix_multiply_gpu(
        self, 
        matrix_a: np.ndarray, 
        matrix_b: np.ndarray,
        use_gpu: bool = True
    ) -> Dict[str, Any]:
        """
        Multiplicación de matrices acelerada por GPU.
        
        Args:
            matrix_a: Primera matriz
            matrix_b: Segunda matriz
            use_gpu: Usar GPU si está disponible
            
        Returns:
            Dict con resultado y metadatos de rendimiento
        """
        start_time = time.time()
        
        # Validar dimensiones
        if matrix_a.shape[1] != matrix_b.shape[0]:
            return {
                "success": False,
                "error": "Dimensiones de matrices incompatibles",
                "shape_a": matrix_a.shape,
                "shape_b": matrix_b.shape
            }
        
        try:
            if use_gpu and self.cuda_available:
                # Usar CuPy para multiplicación GPU
                gpu_a = cp.asarray(matrix_a)
                gpu_b = cp.asarray(matrix_b)
                
                gpu_result = cp.matmul(gpu_a, gpu_b)
                result = cp.asnumpy(gpu_result)
                
                # Limpiar memoria GPU
                del gpu_a, gpu_b, gpu_result
                cp.get_default_memory_pool().free_all_blocks()
                
                computation_time = time.time() - start_time
                self.performance_stats["gpu_operations"] += 1
                self.performance_stats["total_gpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "GPU_CUDA",
                    "result_shape": result.shape,
                    "memory_used": result.nbytes
                }
            else:
                # Fallback a CPU
                result = np.matmul(matrix_a, matrix_b)
                computation_time = time.time() - start_time
                self.performance_stats["cpu_fallback"] += 1
                self.performance_stats["total_cpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "CPU_NumPy",
                    "result_shape": result.shape,
                    "memory_used": result.nbytes
                }
                
        except MathematicsError as e:
            logger.error(f"Error en multiplicación de matrices: {e}")
            return {
                "success": False,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
        finally:
            self.performance_stats["operations_count"] += 1
    
    async def fft_gpu(
        self, 
        signal: np.ndarray,
        use_gpu: bool = True,
        axis: int = -1
    ) -> Dict[str, Any]:
        """
        Transformada rápida de Fourier acelerada por GPU.
        
        Args:
            signal: Señal de entrada
            use_gpu: Usar GPU si está disponible
            axis: Eje para la transformada
            
        Returns:
            Dict con resultado FFT y metadatos
        """
        start_time = time.time()
        
        try:
            if use_gpu and self.cuda_available:
                # Usar CuPy FFT
                gpu_signal = cp.asarray(signal)
                gpu_fft = cp.fft.fft(gpu_signal, axis=axis)
                result = cp.asnumpy(gpu_fft)
                
                # Limpiar memoria GPU
                del gpu_signal, gpu_fft
                cp.get_default_memory_pool().free_all_blocks()
                
                computation_time = time.time() - start_time
                self.performance_stats["gpu_operations"] += 1
                self.performance_stats["total_gpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "GPU_CuPy_FFT",
                    "signal_length": len(signal),
                    "result_shape": result.shape
                }
            else:
                # Fallback a SciPy FFT
                result = fft.fft(signal, axis=axis)
                computation_time = time.time() - start_time
                self.performance_stats["cpu_fallback"] += 1
                self.performance_stats["total_cpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "CPU_SciPy_FFT",
                    "signal_length": len(signal),
                    "result_shape": result.shape
                }
                
        except MathematicsError as e:
            logger.error(f"Error en FFT: {e}")
            return {
                "success": False,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
        finally:
            self.performance_stats["operations_count"] += 1
    
    async def vector_operations_gpu(
        self,
        vectors: List[np.ndarray],
        operation: str = "dot",
        use_gpu: bool = True
    ) -> Dict[str, Any]:
        """
        Operaciones vectoriales paralelas en GPU.
        
        Args:
            vectors: Lista de vectores
            operation: Tipo de operación ('dot', 'cross', 'norm', 'add', 'multiply')
            use_gpu: Usar GPU si está disponible
            
        Returns:
            Dict con resultados de operaciones vectoriales
        """
        start_time = time.time()
        
        if len(vectors) < 2 and operation in ['dot', 'cross', 'add', 'multiply']:
            return {
                "success": False,
                "error": f"Operación '{operation}' requiere al menos 2 vectores"
            }
        
        try:
            if use_gpu and self.cuda_available:
                # Convertir a GPU
                gpu_vectors = [cp.asarray(v) for v in vectors]
                
                if operation == "dot":
                    result = cp.dot(gpu_vectors[0], gpu_vectors[1])
                elif operation == "cross":
                    result = cp.cross(gpu_vectors[0], gpu_vectors[1])
                elif operation == "norm":
                    result = [cp.linalg.norm(v) for v in gpu_vectors]
                elif operation == "add":
                    result = sum(gpu_vectors)
                elif operation == "multiply":
                    result = gpu_vectors[0]
                    for v in gpu_vectors[1:]:
                        result = cp.multiply(result, v)
                else:
                    return {
                        "success": False,
                        "error": f"Operación no soportada: {operation}"
                    }
                
                # Convertir resultado a CPU
                if isinstance(result, list):
                    result = [cp.asnumpy(r) for r in result]
                else:
                    result = cp.asnumpy(result)
                
                # Limpiar memoria GPU
                for v in gpu_vectors:
                    del v
                cp.get_default_memory_pool().free_all_blocks()
                
                computation_time = time.time() - start_time
                self.performance_stats["gpu_operations"] += 1
                self.performance_stats["total_gpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "GPU_CuPy",
                    "operation": operation,
                    "vector_count": len(vectors)
                }
            else:
                # Fallback a NumPy
                if operation == "dot":
                    result = np.dot(vectors[0], vectors[1])
                elif operation == "cross":
                    result = np.cross(vectors[0], vectors[1])
                elif operation == "norm":
                    result = [np.linalg.norm(v) for v in vectors]
                elif operation == "add":
                    result = sum(vectors)
                elif operation == "multiply":
                    result = vectors[0]
                    for v in vectors[1:]:
                        result = np.multiply(result, v)
                else:
                    return {
                        "success": False,
                        "error": f"Operación no soportada: {operation}"
                    }
                
                computation_time = time.time() - start_time
                self.performance_stats["cpu_fallback"] += 1
                self.performance_stats["total_cpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "CPU_NumPy",
                    "operation": operation,
                    "vector_count": len(vectors)
                }
                
        except MathematicsError as e:
            logger.error(f"Error en operaciones vectoriales: {e}")
            return {
                "success": False,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
        finally:
            self.performance_stats["operations_count"] += 1
    
    async def linear_algebra_gpu(
        self,
        matrix: np.ndarray,
        operation: str = "eigenvalues",
        use_gpu: bool = True
    ) -> Dict[str, Any]:
        """
        Operaciones de álgebra lineal aceleradas por GPU.
        
        Args:
            matrix: Matriz de entrada
            operation: Operación ('eigenvalues', 'svd', 'inverse', 'determinant')
            use_gpu: Usar GPU si está disponible
            
        Returns:
            Dict con resultados de álgebra lineal
        """
        start_time = time.time()
        
        try:
            if use_gpu and self.cuda_available:
                gpu_matrix = cp.asarray(matrix)
                
                if operation == "eigenvalues":
                    result = cp.linalg.eigvals(gpu_matrix)
                elif operation == "svd":
                    u, s, vh = cp.linalg.svd(gpu_matrix)
                    result = {"U": cp.asnumpy(u), "S": cp.asnumpy(s), "Vh": cp.asnumpy(vh)}
                elif operation == "inverse":
                    result = cp.linalg.inv(gpu_matrix)
                elif operation == "determinant":
                    result = cp.linalg.det(gpu_matrix)
                else:
                    return {
                        "success": False,
                        "error": f"Operación no soportada: {operation}"
                    }
                
                # Convertir resultado a CPU si es necesario
                if not isinstance(result, dict) and hasattr(result, 'get'):
                    result = cp.asnumpy(result)
                
                # Limpiar memoria GPU
                del gpu_matrix
                cp.get_default_memory_pool().free_all_blocks()
                
                computation_time = time.time() - start_time
                self.performance_stats["gpu_operations"] += 1
                self.performance_stats["total_gpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "GPU_CuPy",
                    "operation": operation,
                    "matrix_shape": matrix.shape
                }
            else:
                # Fallback a NumPy
                if operation == "eigenvalues":
                    result = np.linalg.eigvals(matrix)
                elif operation == "svd":
                    u, s, vh = np.linalg.svd(matrix)
                    result = {"U": u, "S": s, "Vh": vh}
                elif operation == "inverse":
                    result = np.linalg.inv(matrix)
                elif operation == "determinant":
                    result = np.linalg.det(matrix)
                else:
                    return {
                        "success": False,
                        "error": f"Operación no soportada: {operation}"
                    }
                
                computation_time = time.time() - start_time
                self.performance_stats["cpu_fallback"] += 1
                self.performance_stats["total_cpu_time"] += computation_time
                
                return {
                    "success": True,
                    "result": result,
                    "computation_time": computation_time,
                    "method": "CPU_NumPy",
                    "operation": operation,
                    "matrix_shape": matrix.shape
                }
                
        except MathematicsError as e:
            logger.error(f"Error en álgebra lineal: {e}")
            return {
                "success": False,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
        finally:
            self.performance_stats["operations_count"] += 1
    
    async def benchmark_performance(
        self,
        matrix_sizes: List[int] = [100, 500, 1000, 2000],
        iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Benchmark de rendimiento GPU vs CPU.
        
        Args:
            matrix_sizes: Tamaños de matrices para probar
            iterations: Número de iteraciones por tamaño
            
        Returns:
            Dict con resultados de benchmark
        """
        results = {
            "gpu_available": self.gpu_available,
            "benchmarks": [],
            "summary": {}
        }
        
        for size in matrix_sizes:
            logger.info(f"Benchmarking matrices {size}x{size}")
            
            # Generar matrices de prueba
            matrix_a = np.random.rand(size, size).astype(np.float32)
            matrix_b = np.random.rand(size, size).astype(np.float32)
            
            gpu_times = []
            cpu_times = []
            
            for i in range(iterations):
                # Benchmark GPU
                if self.gpu_available:
                    gpu_result = await self.matrix_multiply_gpu(matrix_a, matrix_b, use_gpu=True)
                    if gpu_result["success"]:
                        gpu_times.append(gpu_result["computation_time"])
                
                # Benchmark CPU
                cpu_result = await self.matrix_multiply_gpu(matrix_a, matrix_b, use_gpu=False)
                if cpu_result["success"]:
                    cpu_times.append(cpu_result["computation_time"])
            
            benchmark_result = {
                "matrix_size": size,
                "iterations": iterations,
                "gpu_times": gpu_times,
                "cpu_times": cpu_times,
                "gpu_avg": np.mean(gpu_times) if gpu_times else None,
                "cpu_avg": np.mean(cpu_times) if cpu_times else None,
                "speedup": np.mean(cpu_times) / np.mean(gpu_times) if gpu_times and cpu_times else None
            }
            
            results["benchmarks"].append(benchmark_result)
        
        # Calcular resumen
        if results["benchmarks"]:
            speedups = [b["speedup"] for b in results["benchmarks"] if b["speedup"]]
            results["summary"] = {
                "avg_speedup": np.mean(speedups) if speedups else None,
                "max_speedup": np.max(speedups) if speedups else None,
                "min_speedup": np.min(speedups) if speedups else None
            }
        
        return results
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de rendimiento."""
        stats = self.performance_stats.copy()
        
        if stats["operations_count"] > 0:
            stats["gpu_usage_percentage"] = (stats["gpu_operations"] / stats["operations_count"]) * 100
            stats["avg_gpu_time"] = stats["total_gpu_time"] / max(stats["gpu_operations"], 1)
            stats["avg_cpu_time"] = stats["total_cpu_time"] / max(stats["cpu_fallback"], 1)
        
        return stats
    
    def reset_performance_stats(self):
        """Resetear estadísticas de rendimiento."""
        self.performance_stats = {
            "operations_count": 0,
            "gpu_operations": 0,
            "cpu_fallback": 0,
            "total_gpu_time": 0.0,
            "total_cpu_time": 0.0
        }
    
    def cleanup_gpu_memory(self):
        """Limpiar memoria GPU."""
        if self.cuda_available:
            try:
                cp.get_default_memory_pool().free_all_blocks()
                logger.info("Memoria GPU limpiada")
            except MathematicsError as e:
                logger.error(f"Error limpiando memoria GPU: {e}")


# Instancia global del servicio
gpu_math_service = GPUMathService()