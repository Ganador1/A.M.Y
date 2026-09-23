"""
Advanced Algorithms Router

Este módulo proporciona endpoints para algoritmos matemáticos avanzados y computación distribuida,
incluyendo optimización de funciones, integración numérica, descomposición de matrices,
clustering paralelo y interpolación avanzada. Soporta ejecución en GPU y sistemas distribuidos
para procesamiento de alto rendimiento de datos científicos.

Capacidades principales:
- Optimización de funciones con múltiples métodos y restricciones
- Integración numérica adaptativa y de punto fijo
- Descomposición de matrices (SVD, QR, LU, Cholesky)
- Algoritmos de clustering paralelos (K-means, jerárquico)
- Métodos de interpolación avanzados (cúbica, spline)
- Computación científica distribuida en múltiples nodos
- Ejecución acelerada por GPU de algoritmos
- Perfilado de rendimiento y monitoreo del sistema
- Monitoreo de estado y salud de algoritmos

Endpoints disponibles:
- GET /gpu/status: Estado del sistema GPU
- GET /distributed/status: Estado de computación distribuida
- GET /algorithms/status: Estado de algoritmos avanzados
- POST /optimize: Optimización avanzada de funciones
- POST /integrate: Integración numérica avanzada
- POST /decompose: Descomposición de matrices
- POST /cluster: Clustering paralelo
- POST /interpolate: Interpolación avanzada
- POST /distributed/compute: Computación distribuida
- GET /performance/summary: Resumen de rendimiento del sistema

Dependencias:
- get_advanced_algorithms(): Servicio de algoritmos avanzados
- get_distributed_manager(): Gestor de computación distribuida
- gpu_manager: Gestor de GPU para aceleración
- performance_profiler: Perfilador de rendimiento del sistema
- OptimizationRequest, IntegrationRequest, MatrixDecompositionRequest: Modelos de solicitud
- ClusteringRequest, InterpolationRequest: Modelos especializados

Uso típico:
    from app.routers.advanced_algorithms import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

from app.advanced_ops.advanced_algorithms import get_advanced_algorithms
from app.distributed_manager import get_distributed_manager
from app.distributed.gpu_manager import gpu_manager
from app.performance_profiler import profiler as performance_profiler
from app.exceptions.domain.mathematics import MathematicsError
from sympy import sympify, lambdify, symbols, IndexedBase

router = APIRouter()

# Get algorithm instances
algorithms = get_advanced_algorithms()
distributed_mgr = get_distributed_manager()

# Pydantic models for API
class OptimizationRequest(BaseModel):
    function: str = Field(..., description="Mathematical function to optimize (as string)")
    bounds: List[List[float]] = Field(..., description="Bounds for each variable [[min1, max1], [min2, max2], ...]")
    method: str = Field("L-BFGS-B", description="Optimization method")
    constraints: Optional[List[Dict]] = Field(None, description="Optimization constraints")

class IntegrationRequest(BaseModel):
    function: str = Field(..., description="Function to integrate (as string)")
    lower_limit: float = Field(..., description="Lower integration limit")
    upper_limit: float = Field(..., description="Upper integration limit")
    method: str = Field("adaptive", description="Integration method: adaptive, fixed_quad, romberg")

class MatrixDecompositionRequest(BaseModel):
    matrix: List[List[float]] = Field(..., description="Matrix to decompose")
    method: str = Field("svd", description="Decomposition method: svd, qr, lu, cholesky")

class ClusteringRequest(BaseModel):
    data: List[List[float]] = Field(..., description="Data points for clustering")
    n_clusters: int = Field(3, description="Number of clusters")
    method: str = Field("kmeans", description="Clustering method")

class InterpolationRequest(BaseModel):
    x_values: List[float] = Field(..., description="X values")
    y_values: List[float] = Field(..., description="Y values")
    x_new: List[float] = Field(..., description="New X values for interpolation")
    method: str = Field("cubic", description="Interpolation method")

@router.get("/gpu/status")
async def get_gpu_status():
    """Get GPU system status"""
    try:
        gpu_info = gpu_manager.get_device_info()
        memory_info = gpu_manager.get_memory_info()

        return {
            "status": "success",
            "gpu_info": gpu_info,
            "memory_info": memory_info,
            "timestamp": datetime.now().isoformat()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"GPU status error: {str(e)}")

@router.get("/distributed/status")
async def get_distributed_status():
    """Get distributed computing status"""
    try:
        status = distributed_mgr.get_system_status()

        return {
            "status": "success",
            "distributed_info": status,
            "timestamp": datetime.now().isoformat()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Distributed status error: {str(e)}")

@router.get("/algorithms/status")
async def get_algorithms_status():
    """Get advanced algorithms system status"""
    try:
        status = algorithms.get_system_status()

        return {
            "status": "success",
            "algorithms_info": status,
            "timestamp": datetime.now().isoformat()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Algorithms status error: {str(e)}")

@router.post("/optimize")
async def optimize_function(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """Advanced function optimization"""
    try:
        # Parse function safely using sympy
        try:
            from sympy import symbols, sympify, lambdify
            # Define symbols. Support both scalar 'x' and indexed 'x[i]'
            x_sym = IndexedBase('x')
            expr = sympify(request.function)
            
            # Create a lambda function that uses numpy for evaluation
            # This is significantly safer than eval()
            func_lambda = lambdify(x_sym, expr, modules=['numpy'])
            
            def func(x):
                """Safely evaluate function using sympy/numpy."""
                if isinstance(x, (list, np.ndarray)):
                    # Ensure it's a numpy array for IndexedBase access
                    return func_lambda(np.array(x))
                return func_lambda(x)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid mathematical expression: {str(e)}")

        # Convert bounds to tuples
        bounds = [(b[0], b[1]) for b in request.bounds]

        # Profile the optimization
        with performance_profiler.profile_operation("advanced_optimization"):
            result = algorithms.optimize_function(
                func=func,
                bounds=bounds,
                method=request.method,
                constraints=request.constraints
            )

        return {
            "status": "success",
            "result": {
                "optimal_point": result.result.tolist() if hasattr(result.result, 'tolist') else result.result,
                "execution_time": result.execution_time,
                "precision_level": result.precision_level.value,
                "convergence_info": result.convergence_info,
                "performance_metrics": result.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")

@router.post("/integrate")
async def numerical_integration(request: IntegrationRequest, background_tasks: BackgroundTasks):
    """Advanced numerical integration"""
    try:
        # Parse function safely using sympy
        try:
            from sympy import symbols, sympify, lambdify
            x_sym = symbols('x')
            expr = sympify(request.function)
            func_lambda = lambdify(x_sym, expr, modules=['numpy'])
            
            def func(x):
                """Safely evaluate integration function."""
                return func_lambda(x)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid mathematical expression: {str(e)}")

        # Profile the integration
        with performance_profiler.profile_operation("advanced_integration"):
            result = algorithms.numerical_integration(
                func=func,
                a=request.lower_limit,
                b=request.upper_limit,
                method=request.method
            )

        return {
            "status": "success",
            "result": {
                "integral_value": float(result.result),
                "execution_time": result.execution_time,
                "precision_level": result.precision_level.value,
                "method": request.method,
                "convergence_info": result.convergence_info,
                "performance_metrics": result.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Integration error: {str(e)}")

@router.post("/decompose")
async def matrix_decomposition(request: MatrixDecompositionRequest, background_tasks: BackgroundTasks):
    """Advanced matrix decomposition"""
    try:
        matrix = np.array(request.matrix)

        # Profile the decomposition
        with performance_profiler.profile_operation("matrix_decomposition"):
            result = algorithms.matrix_decomposition(
                matrix=matrix,
                method=request.method
            )

        # Convert numpy arrays to lists for JSON serialization
        result_data = {
            key: value.tolist() if hasattr(value, 'tolist') else value
            for key, value in result.result.items()
        }

        return {
            "status": "success",
            "result": {
                "decomposition": result_data,
                "execution_time": result.execution_time,
                "precision_level": result.precision_level.value,
                "method": request.method,
                "performance_metrics": result.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Decomposition error: {str(e)}")

@router.post("/cluster")
async def parallel_clustering(request: ClusteringRequest, background_tasks: BackgroundTasks):
    """Parallel clustering algorithms"""
    try:
        data = np.array(request.data)

        # Profile the clustering
        with performance_profiler.profile_operation("parallel_clustering"):
            result = algorithms.parallel_clustering(
                data=data,
                n_clusters=request.n_clusters,
                method=request.method
            )

        return {
            "status": "success",
            "result": {
                "labels": result.result['labels'].tolist(),
                "n_clusters": result.result['n_clusters'],
                "centroids": result.result['centroids'].tolist() if result.result['centroids'] is not None else None,
                "inertia": result.result['inertia'],
                "execution_time": result.execution_time,
                "precision_level": result.precision_level.value,
                "performance_metrics": result.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Clustering error: {str(e)}")

@router.post("/interpolate")
async def advanced_interpolation(request: InterpolationRequest, background_tasks: BackgroundTasks):
    """Advanced interpolation methods"""
    try:
        x = np.array(request.x_values)
        y = np.array(request.y_values)
        x_new = np.array(request.x_new)

        # Profile the interpolation
        with performance_profiler.profile_operation("advanced_interpolation"):
            result = algorithms.advanced_interpolation(
                x=x,
                y=y,
                x_new=x_new,
                method=request.method
            )

        return {
            "status": "success",
            "result": {
                "interpolated_values": result.result.tolist(),
                "execution_time": result.execution_time,
                "precision_level": result.precision_level.value,
                "method": request.method,
                "performance_metrics": result.performance_metrics
            },
            "timestamp": datetime.now().isoformat()
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Interpolation error: {str(e)}")

@router.post("/distributed/compute")
async def distributed_computation(data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Execute computation using distributed system"""
    try:
        if not isinstance(data.get('data_sets'), list):
            raise ValueError("data_sets must be a list")

        data_sets = data['data_sets']

        # Define computation function (simple example - sum of squares)
        def computation_func(data_set):
            """
            Compute sum of squares for distributed processing.
            
            Simple computation function that calculates the sum of squares
            of input data for demonstration of distributed computing.
            
            Args:
                data_set: List of numbers or single number to process
                
            Returns:
                Sum of squares as float
            """
            if isinstance(data_set, list):
                return sum(x**2 for x in data_set)
            return data_set ** 2

        # Profile the distributed computation
        with performance_profiler.profile_operation("distributed_computation"):
            results = distributed_mgr.distributed_scientific_computation(
                computation_func=computation_func,
                data_sets=data_sets
            )

        return {
            "status": "success",
            "result": {
                "computation_results": results,
                "data_sets_count": len(data_sets),
                "distributed_enabled": distributed_mgr.is_initialized,
                "timestamp": datetime.now().isoformat()
            }
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Distributed computation error: {str(e)}")

@router.get("/performance/summary")
async def get_performance_summary():
    """Get performance summary of advanced algorithms"""
    try:
        gpu_info = gpu_manager.get_device_info()
        distributed_status = distributed_mgr.get_system_status()
        algorithms_status = algorithms.get_system_status()

        # Get profiling data
        profiling_data = performance_profiler.get_all_stats()

        return {
            "status": "success",
            "summary": {
                "gpu_acceleration": gpu_info,
                "distributed_computing": distributed_status,
                "advanced_algorithms": algorithms_status,
                "performance_profiling": profiling_data,
                "system_health": "optimal" if gpu_info['device_available'] else "cpu_only"
            },
            "timestamp": datetime.now().isoformat()
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Performance summary error: {str(e)}")
