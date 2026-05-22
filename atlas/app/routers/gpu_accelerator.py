"""
Router del Acelerador GPU - Gestión y Optimización de Recursos GPU

Módulo FastAPI para gestión de aceleración GPU, monitoreo y optimización de rendimiento.
Proporciona endpoints integrales para gestión de recursos GPU, monitoreo de rendimiento,
optimización de memoria y aceleración de cargas de trabajo en tareas de computación científica.

Capacidades principales:
- Estadísticas y monitoreo de rendimiento GPU
- Aceleración de operaciones científicas usando computación GPU
- Optimización específica por carga de trabajo
- Gestión y optimización de memoria GPU
- Análisis de estadísticas de memoria y fragmentación
- Historial de operaciones y registros de auditoría
- Monitoreo de salud y diagnósticos GPU
- Limpieza de recursos y mantenimiento

Catálogo de Endpoints:
- GET /gpu/stats: Estadísticas integrales de dispositivo y rendimiento GPU
- POST /gpu/accelerate: Aceleración de operaciones científicas usando GPU
- POST /gpu/optimize: Optimización de configuraciones GPU para cargas específicas
- POST /gpu/memory/optimize: Optimización de uso de memoria GPU y fragmentación
- GET /gpu/memory/stats: Estadísticas detalladas de memoria GPU y métricas
- GET /gpu/operations/history: Historial de operaciones y asignaciones GPU
- GET /gpu/health: Estado de salud GPU e información diagnóstica
- POST /gpu/cleanup: Limpieza de recursos GPU y liberación de memoria

Dependencias:
- GPUAccelerator: Servicio central de aceleración y gestión de memoria GPU
- GPUManager: Servicio de gestión y monitoreo de dispositivos GPU
- pydantic: Validación de requests/responses
- CUDA/cuDNN: Bibliotecas de computación GPU (cuando disponibles)
- logging: Sistema de logging para trazabilidad

Uso del Servicio:
    Todos los endpoints proporcionan capacidades de monitoreo y control GPU en tiempo real.
    La optimización de memoria y monitoreo de salud ayudan a mantener el rendimiento óptimo
    GPU para cargas de trabajo de computación científica intensiva.
"""

from fastapi import APIRouter, HTTPException
from typing import Any
from pydantic import BaseModel
import logging

from app.distributed.gpu_accelerator import get_gpu_accelerator
from app.distributed.gpu_manager import get_gpu_manager
from app.exceptions.infrastructure.api import APIError

logger = logging.getLogger(__name__)

router = APIRouter()

class GPUOperationRequest(BaseModel):
    operation_type: str
    data: Any
    priority: int = 1
    return_cpu: bool = True
    sub_operation: str = ""

class GPUOptimizationRequest(BaseModel):
    workload_type: str

@router.get("/gpu/stats")
async def get_gpu_stats():
    """Get comprehensive GPU statistics"""
    try:
        accelerator = get_gpu_accelerator()
        gpu_manager = get_gpu_manager()

        stats = accelerator.get_performance_stats()
        device_info = gpu_manager.get_device_info()

        return {
            "device_info": device_info,
            "performance_stats": stats,
            "memory_info": gpu_manager.get_memory_info()
        }
    except APIError as e:
        logger.error(f"Error getting GPU stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get GPU stats: {str(e)}")

@router.post("/gpu/accelerate")
async def accelerate_operation(request: GPUOperationRequest):
    """Accelerate a scientific operation using GPU"""
    try:
        accelerator = get_gpu_accelerator()

        result = await accelerator.accelerate_operation(
            operation_type=request.operation_type,
            data=request.data,
            priority=request.priority,
            return_cpu=request.return_cpu,
            sub_operation=request.sub_operation
        )

        return {
            "success": True,
            "result": result,
            "operation_type": request.operation_type
        }
    except APIError as e:
        logger.error(f"Error accelerating operation: {e}")
        raise HTTPException(status_code=500, detail=f"GPU acceleration failed: {str(e)}")

@router.post("/gpu/optimize")
async def optimize_gpu_workload(request: GPUOptimizationRequest):
    """Optimize GPU settings for specific workload"""
    try:
        accelerator = get_gpu_accelerator()
        accelerator.optimize_for_workload(request.workload_type)

        return {
            "success": True,
            "message": f"GPU optimized for {request.workload_type} workload",
            "workload_type": request.workload_type
        }
    except APIError as e:
        logger.error(f"Error optimizing GPU: {e}")
        raise HTTPException(status_code=500, detail=f"GPU optimization failed: {str(e)}")

@router.post("/gpu/memory/optimize")
async def optimize_gpu_memory():
    """Optimize GPU memory usage"""
    try:
        accelerator = get_gpu_accelerator()
        accelerator.memory_manager.optimize_memory()

        stats = accelerator.memory_manager.get_memory_stats()

        return {
            "success": True,
            "message": "GPU memory optimized",
            "memory_stats": {
                "allocated_mb": stats.allocated_mb,
                "reserved_mb": stats.reserved_mb,
                "available_mb": stats.available_mb
            }
        }
    except APIError as e:
        logger.error(f"Error optimizing GPU memory: {e}")
        raise HTTPException(status_code=500, detail=f"GPU memory optimization failed: {str(e)}")

@router.get("/gpu/memory/stats")
async def get_gpu_memory_stats():
    """Get detailed GPU memory statistics"""
    try:
        accelerator = get_gpu_accelerator()
        stats = accelerator.memory_manager.get_memory_stats()

        return {
            "allocated_mb": stats.allocated_mb,
            "reserved_mb": stats.reserved_mb,
            "total_mb": stats.total_mb,
            "available_mb": stats.available_mb,
            "fragmentation_ratio": stats.fragmentation_ratio,
            "should_gc": accelerator.memory_manager.should_gc()
        }
    except APIError as e:
        logger.error(f"Error getting GPU memory stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get GPU memory stats: {str(e)}")

@router.get("/gpu/operations/history")
async def get_gpu_operations_history():
    """Get GPU operations history"""
    try:
        accelerator = get_gpu_accelerator()
        history = accelerator.memory_manager.allocation_history[-50:]  # Last 50 operations

        return {
            "operations": history,
            "total_operations": len(accelerator.memory_manager.allocation_history)
        }
    except APIError as e:
        logger.error(f"Error getting operations history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get operations history: {str(e)}")

@router.get("/gpu/health")
async def get_gpu_health():
    """Get GPU health status"""
    try:
        gpu_manager = get_gpu_manager()
        accelerator = get_gpu_accelerator()

        device_info = gpu_manager.get_device_info()
        memory_stats = accelerator.memory_manager.get_memory_stats()

        health_status = "healthy"
        issues = []

        # Check memory usage
        if memory_stats.total_mb > 0:
            usage_ratio = memory_stats.reserved_mb / memory_stats.total_mb
            if usage_ratio > 0.95:
                health_status = "critical"
                issues.append("Memory usage above 95%")
            elif usage_ratio > 0.85:
                health_status = "warning"
                issues.append("Memory usage above 85%")

        # Check fragmentation
        if memory_stats.fragmentation_ratio > 0.8:
            issues.append("High memory fragmentation detected")

        return {
            "status": health_status,
            "device_available": device_info["device_available"],
            "device_type": device_info["device_type"],
            "memory_usage_percent": (memory_stats.reserved_mb / memory_stats.total_mb * 100) if memory_stats.total_mb > 0 else 0,
            "issues": issues,
            "recommendations": [
                "Optimize memory usage" if issues else "System operating normally"
            ]
        }
    except APIError as e:
        logger.error(f"Error getting GPU health: {e}")
        return {
            "status": "error",
            "device_available": False,
            "issues": [f"Health check failed: {str(e)}"],
            "recommendations": ["Check GPU configuration"]
        }

@router.post("/gpu/cleanup")
async def cleanup_gpu_resources():
    """Clean up GPU resources"""
    try:
        accelerator = get_gpu_accelerator()
        accelerator.cleanup()

        return {
            "success": True,
            "message": "GPU resources cleaned up successfully"
        }
    except APIError as e:
        logger.error(f"Error cleaning up GPU resources: {e}")
        raise HTTPException(status_code=500, detail=f"GPU cleanup failed: {str(e)}")
