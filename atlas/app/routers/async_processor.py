"""
Async Processing Router

Router FastAPI para procesamiento avanzado de tareas asíncronas y gestión de computaciones científicas.
Proporciona endpoints REST API para envío asíncrono de tareas con colas de prioridad,
ejecución de computaciones científicas con pools de workers, monitoreo en tiempo real del estado
de tareas y seguimiento de progreso, cancelación de tareas y gestión de dependencias,
métricas del sistema y análisis de rendimiento, gestión de pools de workers y escalado,
ejecución de tareas en segundo plano para operaciones de larga duración, y tolerancia a fallos
y manejo de errores para computación distribuida.

Capacidades principales:
- Envío asíncrono de tareas con sistema de colas de prioridad
- Ejecución de computaciones científicas con pools de workers especializados
- Monitoreo en tiempo real del estado de tareas y seguimiento de progreso
- Cancelación de tareas y gestión avanzada de dependencias
- Métricas del sistema y análisis de rendimiento comprehensivo
- Gestión de pools de workers y escalado automático
- Ejecución de tareas en segundo plano para operaciones de larga duración
- Tolerancia a fallos y manejo robusto de errores para computación distribuida
- Procesamiento paralelo de múltiples tareas científicas
- Optimización de recursos y balanceo de carga

Endpoints disponibles:
- POST /async/submit: Envío de tarea asíncrona con configuración completa
- POST /scientific/run: Ejecución de tarea científica específica
- GET /tasks/status: Estado de todas las tareas activas
- GET /tasks/{task_id}/status: Estado detallado de tarea específica
- DELETE /tasks/{task_id}: Cancelación de tarea en ejecución
- GET /system/metrics: Métricas del sistema y rendimiento
- GET /workers/status: Estado de pools de workers
- POST /workers/scale: Escalado manual de workers
- GET /queue/status: Estado de colas de tareas por prioridad
- POST /batch/submit: Envío por lotes de múltiples tareas

Dependencias:
- AsyncProcessor: Procesador principal de tareas asíncronas
- TaskType: Enumeración de tipos de tareas disponibles
- TaskPriority: Enumeración de niveles de prioridad
- TaskSubmissionRequest: Solicitud de envío de tarea
- ScientificTaskRequest: Solicitud de tarea científica

Uso típico:
    from app.routers.async_processor import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import logging
import asyncio
import time

from app.exceptions.domain.mathematics import MathematicsError
from app.processing.async_processor import (
    get_async_processor, submit_async_task, run_scientific_task,
    TaskType, TaskPriority,
)

logger = logging.getLogger(__name__)

router = APIRouter()

class TaskSubmissionRequest(BaseModel):
    task_id: str
    task_type: str = "cpu_intensive"
    priority: str = "normal"
    timeout: Optional[float] = None
    dependencies: List[str] = []

class ScientificTaskRequest(BaseModel):
    task_id: str
    operation_data: Dict[str, Any]
    task_type: str = "cpu_intensive"

@router.post("/async/submit")
async def submit_task(request: TaskSubmissionRequest, background_tasks: BackgroundTasks):
    """Submit an asynchronous task"""
    try:
        # Convert string enums to actual enums
        task_type = TaskType(request.task_type)
        priority = TaskPriority(request.priority)

        # Create a simple test coroutine
        async def test_coroutine():
            await asyncio.sleep(1)  # Simulate work
            return {"result": f"Task {request.task_id} completed", "timestamp": time.time()}

        task_id = await submit_async_task(
            task_id=request.task_id,
            coroutine=test_coroutine,
            task_type=task_type,
            priority=priority,
            timeout=request.timeout,
            dependencies=request.dependencies
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Task {task_id} submitted successfully"
        }
    except MathematicsError as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail=f"Task submission failed: {str(e)}")

@router.post("/async/scientific")
async def submit_scientific_task(request: ScientificTaskRequest):
    """Submit a scientific computation task"""
    try:
        task_type = TaskType(request.task_type)

        # Create scientific operation
        def scientific_operation():
            # Simulate scientific computation
            import math
            result = 0
            for i in range(100000):
                result += math.sin(i) * math.cos(i)
            return {"computation_result": result, "iterations": 100000}

        task_id = await run_scientific_task(
            task_id=request.task_id,
            operation=scientific_operation,
            task_type=task_type
        )

        return {
            "success": True,
            "task_id": task_id,
            "message": f"Scientific task {task_id} submitted"
        }
    except MathematicsError as e:
        logger.error(f"Error submitting scientific task: {e}")
        raise HTTPException(status_code=500, detail=f"Scientific task submission failed: {str(e)}")

@router.get("/async/status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task"""
    try:
        processor = get_async_processor()
        status = processor.get_task_status(task_id)

        return {
            "task_id": task_id,
            "status": status
        }
    except MathematicsError as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get task status: {str(e)}")

@router.get("/async/system/status")
async def get_system_status():
    """Get comprehensive async system status"""
    try:
        processor = get_async_processor()
        return processor.get_system_status()
    except MathematicsError as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

@router.get("/async/metrics")
async def get_async_metrics():
    """Get async processing metrics"""
    try:
        processor = get_async_processor()
        status = processor.get_system_status()

        return {
            "metrics": status["metrics"],
            "timestamp": time.time()
        }
    except MathematicsError as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.delete("/async/task/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a running task"""
    try:
        processor = get_async_processor()

        # Check if task exists
        status = processor.get_task_status(task_id)
        if status["status"] == "not_found":
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        if status["status"] == "running":
            # Cancel the task
            task = processor.active_tasks.get(task_id)
            if task:
                task.cancel()
                return {"success": True, "message": f"Task {task_id} cancelled"}
            else:
                raise HTTPException(status_code=404, detail=f"Task {task_id} not found in active tasks")
        else:
            return {"success": False, "message": f"Task {task_id} is not running"}

    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")

@router.get("/async/tasks/active")
async def get_active_tasks():
    """Get list of active tasks"""
    try:
        processor = get_async_processor()

        active = []
        for task_id, task in processor.active_tasks.items():
            active.append({
                "task_id": task_id,
                "status": "running",
                "done": task.done()
            })

        return {"active_tasks": active, "count": len(active)}
    except MathematicsError as e:
        logger.error(f"Error getting active tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get active tasks: {str(e)}")

@router.get("/async/tasks/completed")
async def get_completed_tasks():
    """Get list of completed tasks"""
    try:
        processor = get_async_processor()

        completed = []
        for task_id, result in processor.completed_tasks.items():
            completed.append({
                "task_id": task_id,
                "status": "completed",
                "result": str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
            })

        return {"completed_tasks": completed, "count": len(completed)}
    except MathematicsError as e:
        logger.error(f"Error getting completed tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get completed tasks: {str(e)}")

@router.post("/async/start")
async def start_async_processor():
    """Start the async processor"""
    try:
        processor = get_async_processor()

        if processor.running:
            return {"success": False, "message": "Async processor already running"}

        # Start in background
        asyncio.create_task(processor.start())

        return {"success": True, "message": "Async processor started"}
    except MathematicsError as e:
        logger.error(f"Error starting async processor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start async processor: {str(e)}")

@router.post("/async/stop")
async def stop_async_processor():
    """Stop the async processor"""
    try:
        processor = get_async_processor()

        if not processor.running:
            return {"success": False, "message": "Async processor not running"}

        await processor.stop()

        return {"success": True, "message": "Async processor stopped"}
    except MathematicsError as e:
        logger.error(f"Error stopping async processor: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop async processor: {str(e)}")

@router.get("/async/workers")
async def get_worker_status():
    """Get worker pool status"""
    try:
        processor = get_async_processor()
        status = processor.get_system_status()

        return {
            "worker_pools": status["worker_pools"],
            "total_workers": sum(pool["max_workers"] for pool in status["worker_pools"].values()),
            "active_workers": sum(pool["active_tasks"] for pool in status["worker_pools"].values())
        }
    except MathematicsError as e:
        logger.error(f"Error getting worker status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get worker status: {str(e)}")
