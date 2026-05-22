"""
Router de Equipos de Laboratorio - AXIOM Meta 4.1
===============================================

Módulo especializado para interfaz con equipos de laboratorio en el ecosistema
AXIOM. Proporciona acceso programático a instrumentos de laboratorio para
ejecución automatizada de experimentos, incluyendo equipos reales y simulados
para investigación y desarrollo.

Capacidades Principales
----------------------
- **Gestión de Equipos**: Inventario y estado de instrumentos de laboratorio
- **Ejecución de Tareas**: Envío y monitoreo de tareas experimentales automatizadas
- **Procesamiento por Lotes**: Ejecución secuencial o paralela de múltiples tareas
- **Monitoreo en Tiempo Real**: Estado de equipos, colas y progreso de tareas
- **Análisis Rápido**: Endpoints simplificados para análisis comunes (NMR, MS, ELISA)
- **Control de Calidad**: Validación de parámetros y manejo de errores
- **Trazabilidad**: Logging completo de operaciones y resultados

Endpoints Disponibles
--------------------
**Equipos:**
- `GET /api/v1/lab-equipment/equipment` - Listar equipos disponibles con filtros
- `GET /api/v1/lab-equipment/equipment/{id}` - Detalles específicos de equipo

**Tareas:**
- `POST /api/v1/lab-equipment/submit-task` - Enviar tarea individual
- `POST /api/v1/lab-equipment/batch-submit` - Enviar lote de tareas
- `GET /api/v1/lab-equipment/task/{id}` - Estado de tarea específica
- `DELETE /api/v1/lab-equipment/task/{id}` - Cancelar/abortar tarea

**Sistema:**
- `GET /api/v1/lab-equipment/system-status` - Estado general del sistema
- `GET /api/v1/lab-equipment/health` - Verificación de salud del servicio

**Análisis Rápido:**
- `POST /api/v1/lab-equipment/quick/nmr-analysis` - Análisis NMR simplificado
- `POST /api/v1/lab-equipment/quick/mass-spec` - Espectrometría de masas rápida
- `POST /api/v1/lab-equipment/quick/plate-assay` - Ensayo en placa automatizado

Dependencias
-----------
- **LabEquipmentBridge**: Puente principal para comunicación con equipos
- **ExperimentTask**: Modelo de tareas experimentales
- **EquipmentType**: Enumeración de tipos de equipos soportados
- **TaskStatus**: Estados posibles de tareas
- **security.require_scopes**: Control de acceso por scopes de seguridad

Uso y Ejemplos
--------------
**Listar equipos disponibles:**
```python
response = await client.get("/api/v1/lab-equipment/equipment?equipment_type=nmr&status=available")
# Retorna lista filtrada de equipos NMR disponibles
```

**Enviar tarea NMR:**
```python
response = await client.post("/api/v1/lab-equipment/submit-task", json={
    "equipment_id": "nmr_001",
    "task_type": "1h_nmr",
    "parameters": {
        "nucleus": "1H",
        "pulse_sequence": "zg30",
        "scans": 16,
        "molecule": "aspirin"
    },
    "priority": 2,
    "estimated_duration": 900,
    "samples": [
        {
            "sample_id": "sample_001",
            "volume": "0.5 mL",
            "solvent": "CDCl3"
        }
    ]
})
# Retorna ID de tarea y confirmación de envío
```

**Análisis rápido de masas:**
```python
response = await client.post("/api/v1/lab-equipment/quick/mass-spec", json={
    "molecule": "caffeine",
    "ionization": "ESI+",
    "mass_range": [100, 500]
})
# Envía tarea MS con parámetros predeterminados optimizados
```

**Procesamiento por lotes:**
```python
response = await client.post("/api/v1/lab-equipment/batch-submit", json={
    "tasks": [
        {
            "equipment_id": "nmr_001",
            "task_type": "1h_nmr",
            "parameters": {"nucleus": "1H", "scans": 8},
            "priority": 3
        },
        {
            "equipment_id": "ms_001",
            "task_type": "esi_ms",
            "parameters": {"ionization": "ESI+", "mass_range": [50, 1000]},
            "priority": 3
        }
    ],
    "sequential": false
})
# Ejecuta tareas en paralelo según disponibilidad de equipos
```

**Monitoreo de tarea:**
```python
response = await client.get("/api/v1/lab-equipment/task/task_20250919_143022_123")
# Retorna estado actual, progreso y resultados si completada
```

Equipos Soportados
------------------
- **NMR (Nuclear Magnetic Resonance)**: Espectroscopía RMN 1H, 13C, multidimensional
- **MS (Mass Spectrometry)**: Espectrometría de masas ESI, MALDI, GC-MS
- **Plate Readers**: Lectores de placas para ELISA, fluorescencia, luminiscencia
- **Chromatography**: HPLC, GC con detectores múltiples
- **Thermal Cyclers**: PCR machines con detección en tiempo real
- **Robotic Systems**: Sistemas de automatización robótica para manejo de muestras

Características de Seguridad
---------------------------
- Control de acceso granular mediante scopes ("lab-equipment:read", "lab-equipment:execute")
- Validación estricta de parámetros de equipo y tareas
- Rate limiting para prevenir sobrecarga de instrumentos
- Logging detallado de todas las operaciones para trazabilidad
- Manejo seguro de excepciones sin exposición de configuración interna
- Validación de prioridades y duraciones estimadas

Consideraciones de Rendimiento
-----------------------------
- Procesamiento asíncrono para tareas de larga duración
- Colas inteligentes con priorización de tareas
- Monitoreo de utilización de equipos para optimización
- Caching de estados de equipos para consultas frecuentes
- Escalabilidad para laboratorios con múltiples instrumentos
- Optimización de lotes para maximizar throughput
"""

import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.security import require_scopes
from app.domains.engineering.services.lab_equipment_bridge import (
    get_lab_bridge,
    ExperimentTask,
    EquipmentType
)
from app.exceptions.domain.biology import BiologyError


# Configure logging
logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(
    prefix="/api/v1/lab-equipment",
    tags=["lab-equipment", "automation"],
    dependencies=[Depends(require_scopes(["lab-equipment"]))]
)


class TaskSubmissionRequest(BaseModel):
    """Request model for submitting a lab task"""
    equipment_id: str = Field(..., description="ID of the equipment to use")
    task_type: str = Field(..., description="Type of task to execute")
    parameters: Dict[str, Any] = Field(..., description="Task-specific parameters")
    priority: int = Field(default=3, ge=1, le=5, description="Task priority (1=highest, 5=lowest)")
    estimated_duration: int = Field(default=300, ge=1, description="Estimated duration in seconds")
    samples: Optional[List[Dict[str, Any]]] = Field(default=[], description="Sample information")
    protocols: Optional[List[str]] = Field(default=[], description="Protocol references")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "equipment_id": "nmr_001",
                "task_type": "1h_nmr",
                "parameters": {
                    "nucleus": "1H",
                    "pulse_sequence": "zg30",
                    "scans": 16,
                    "molecule": "aspirin"
                },
                "priority": 2,
                "estimated_duration": 900,
                "samples": [
                    {
                        "sample_id": "sample_001",
                        "volume": "0.5 mL",
                        "solvent": "CDCl3"
                    }
                ]
            }
        }
    )


class BatchTaskRequest(BaseModel):
    """Request for submitting multiple tasks"""
    tasks: List[TaskSubmissionRequest] = Field(..., description="List of tasks to submit")
    sequential: bool = Field(default=False, description="Execute tasks sequentially")


class EquipmentFilterRequest(BaseModel):
    """Request for filtering equipment"""
    equipment_type: Optional[str] = Field(default=None, description="Filter by equipment type")
    status: Optional[str] = Field(default=None, description="Filter by status")
    location: Optional[str] = Field(default=None, description="Filter by location")


@router.get("/equipment",
    dependencies=[Depends(require_scopes(["lab-equipment:read"]))],
    response_model=Dict[str, Any]
)
async def list_equipment(
    equipment_type: Optional[str] = None,
    status: Optional[str] = None,
    location: Optional[str] = None
) -> Dict[str, Any]:
    """
    List available laboratory equipment

    Returns information about all available equipment including their
    current status, capabilities, and specifications.
    """
    try:
        bridge = await get_lab_bridge()

        # Parse equipment type filter
        eq_type_filter = None
        if equipment_type:
            try:
                eq_type_filter = EquipmentType(equipment_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid equipment type: {equipment_type}"
                )

        equipment_list = bridge.list_equipment(eq_type_filter)

        # Apply additional filters
        if status:
            equipment_list = [eq for eq in equipment_list if eq["status"] == status]

        if location:
            equipment_list = [eq for eq in equipment_list if location.lower() in eq["location"].lower()]

        return {
            "status": "success",
            "equipment_count": len(equipment_list),
            "equipment": equipment_list,
            "available_types": {eq["type"] for eq in equipment_list},
            "available_locations": {eq["location"] for eq in equipment_list}
        }

    except BiologyError as e:
        logger.error(f"Error listing equipment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list equipment: {str(e)}"
        )


@router.get("/equipment/{equipment_id}",
    dependencies=[Depends(require_scopes(["lab-equipment:read"]))],
    response_model=Dict[str, Any]
)
async def get_equipment_details(equipment_id: str) -> Dict[str, Any]:
    """
    Get detailed information about specific equipment

    Returns comprehensive information including current status,
    running tasks, and queue information.
    """
    try:
        bridge = await get_lab_bridge()

        equipment_status = bridge.get_equipment_status(equipment_id)
        if not equipment_status:
            raise HTTPException(
                status_code=404,
                detail=f"Equipment {equipment_id} not found"
            )

        # Get equipment details from list
        equipment_list = bridge.list_equipment()
        if not (equipment_details := next(
            (eq for eq in equipment_list if eq["equipment_id"] == equipment_id),
            None
        )):
            raise HTTPException(
                status_code=404,
                detail=f"Equipment {equipment_id} details not found"
            )

        return {
            "status": "success",
            "equipment": equipment_details,
            "current_status": equipment_status
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error getting equipment details: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get equipment details: {str(e)}"
        )


@router.post("/submit-task",
    dependencies=[Depends(require_scopes(["lab-equipment:execute"]))],
    response_model=Dict[str, Any]
)
async def submit_task(request: TaskSubmissionRequest) -> Dict[str, Any]:
    """
    Submit a task to laboratory equipment

    Submits a task to the specified equipment for execution.
    The task will be queued and executed based on priority and availability.
    """
    try:
        bridge = await get_lab_bridge()

        # Create task
        task = ExperimentTask(
            task_id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]}",
            equipment_id=request.equipment_id,
            task_type=request.task_type,
            parameters=request.parameters,
            priority=request.priority,
            estimated_duration=request.estimated_duration,
            samples=request.samples or [],
            protocols=request.protocols or []
        )

        # Submit task
        success = await bridge.submit_task(task)

        if not success:
            raise HTTPException(
                status_code=400,
                detail="Failed to submit task - check equipment ID and parameters"
            )

        return {
            "status": "success",
            "task_id": task.task_id,
            "equipment_id": task.equipment_id,
            "task_type": task.task_type,
            "priority": task.priority,
            "estimated_duration": task.estimated_duration,
            "submitted_at": task.created_at.isoformat(),
            "message": "Task submitted successfully"
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error submitting task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit task: {str(e)}"
        )


@router.post("/batch-submit",
    dependencies=[Depends(require_scopes(["lab-equipment:execute"]))],
    response_model=Dict[str, Any]
)
async def submit_batch_tasks(request: BatchTaskRequest) -> Dict[str, Any]:
    """
    Submit multiple tasks in batch

    Submits multiple tasks for execution. Can be configured to run
    sequentially or in parallel based on equipment availability.
    """
    try:
        bridge = await get_lab_bridge()

        submitted_tasks = []
        failed_tasks = []

        for i, task_req in enumerate(request.tasks):
            try:
                # Create task with sequential priority if needed
                priority = task_req.priority
                if request.sequential:
                    priority = i + 1  # Sequential priority

                task = ExperimentTask(
                    task_id=f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{i:03d}",
                    equipment_id=task_req.equipment_id,
                    task_type=task_req.task_type,
                    parameters=task_req.parameters,
                    priority=priority,
                    estimated_duration=task_req.estimated_duration,
                    samples=task_req.samples or [],
                    protocols=task_req.protocols or []
                )

                success = await bridge.submit_task(task)

                if success:
                    submitted_tasks.append({
                        "task_id": task.task_id,
                        "equipment_id": task.equipment_id,
                        "task_type": task.task_type,
                        "priority": task.priority
                    })
                else:
                    failed_tasks.append({
                        "index": i,
                        "equipment_id": task_req.equipment_id,
                        "error": "Submission failed"
                    })

            except BiologyError as e:
                failed_tasks.append({
                    "index": i,
                    "equipment_id": task_req.equipment_id,
                    "error": str(e)
                })

        return {
            "status": "partial_success" if failed_tasks else "success",
            "batch_id": f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_tasks": len(request.tasks),
            "submitted": len(submitted_tasks),
            "failed": len(failed_tasks),
            "submitted_tasks": submitted_tasks,
            "failed_tasks": failed_tasks,
            "sequential": request.sequential
        }

    except BiologyError as e:
        logger.error(f"Error submitting batch tasks: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit batch tasks: {str(e)}"
        )


@router.get("/task/{task_id}",
    dependencies=[Depends(require_scopes(["lab-equipment:read"]))],
    response_model=Dict[str, Any]
)
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Get status of a specific task

    Returns current status, progress, and results (if completed) for a task.
    """
    try:
        bridge = await get_lab_bridge()

        task_status = bridge.get_task_status(task_id)

        if not task_status:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found"
            )

        # Get results if completed
        results = None
        if task_id in bridge.completed_tasks:
            result = bridge.completed_tasks[task_id]
            results = {
                "success": result.success,
                "data": result.data,
                "metadata": result.metadata,
                "warnings": result.warnings,
                "errors": result.errors,
                "execution_time": result.execution_time
            }

        return {
            "status": "success",
            "task": task_status,
            "results": results
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error getting task status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.delete("/task/{task_id}",
    dependencies=[Depends(require_scopes(["lab-equipment:execute"]))],
    response_model=Dict[str, str]
)
async def abort_task(task_id: str) -> Dict[str, str]:
    """
    Abort a running or queued task

    Cancels task execution if running or removes from queue if waiting.
    """
    try:
        bridge = await get_lab_bridge()

        success = await bridge.abort_task(task_id)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Task {task_id} not found or cannot be aborted"
            )

        return {
            "status": "success",
            "message": f"Task {task_id} aborted successfully"
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error aborting task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to abort task: {str(e)}"
        )


@router.get("/system-status",
    dependencies=[Depends(require_scopes(["lab-equipment:read"]))],
    response_model=Dict[str, Any]
)
async def get_system_status() -> Dict[str, Any]:
    """
    Get overall laboratory system status

    Returns system-wide status including equipment availability,
    queue status, and throughput metrics.
    """
    try:
        bridge = await get_lab_bridge()

        system_status = bridge.get_system_status()

        return {
            "status": "success",
            "system": system_status,
            "utilization": {
                "equipment_utilization": (system_status["busy"] / system_status["total_equipment"] * 100)
                    if system_status["total_equipment"] > 0 else 0,
                "avg_queue_per_equipment": (system_status["queue_length"] / system_status["total_equipment"])
                    if system_status["total_equipment"] > 0 else 0
            }
        }

    except BiologyError as e:
        logger.error(f"Error getting system status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system status: {str(e)}"
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for lab equipment system
    """
    try:
        bridge = await get_lab_bridge()
        system_status = bridge.get_system_status()

        health_status = "healthy"
        if system_status["error"] > 0:
            health_status = "degraded"
        if system_status["available"] == 0:
            health_status = "unhealthy"

        return {
            "status": health_status,
            "service": "lab_equipment_bridge",
            "equipment_count": system_status["total_equipment"],
            "available_equipment": system_status["available"],
            "message": f"Lab equipment system {health_status}"
        }
    except BiologyError as e:
        return {
            "status": "unhealthy",
            "service": "lab_equipment_bridge",
            "error": str(e)
        }


# Quick task endpoints for common operations

@router.post("/quick/nmr-analysis",
    dependencies=[Depends(require_scopes(["lab-equipment:execute"]))],
    response_model=Dict[str, Any]
)
async def quick_nmr_analysis(
    nucleus: str = "1H",
    molecule: str = "unknown",
    scans: int = 16
) -> Dict[str, Any]:
    """
    Quick endpoint for NMR analysis
    """
    request = TaskSubmissionRequest(
        equipment_id="nmr_001",
        task_type="1h_nmr" if nucleus == "1H" else "13c_nmr",
        parameters={
            "nucleus": nucleus,
            "pulse_sequence": "zg30",
            "scans": scans,
            "molecule": molecule
        },
        priority=2,
        estimated_duration=900 if nucleus == "1H" else 3600
    )

    return await submit_task(request)


@router.post("/quick/mass-spec",
    dependencies=[Depends(require_scopes(["lab-equipment:execute"]))],
    response_model=Dict[str, Any]
)
async def quick_mass_spec(
    molecule: str = "unknown",
    ionization: str = "ESI+",
    mass_range: Optional[List[int]] = None
) -> Dict[str, Any]:
    """
    Quick endpoint for mass spectrometry
    """
    request = TaskSubmissionRequest(
        equipment_id="ms_001",
        task_type="esi_ms",
        parameters={
            "molecule": molecule,
            "ionization": ionization,
            "mass_range": mass_range or [50, 1000],
            "resolution": 30000
        },
        priority=2,
        estimated_duration=600
    )

    return await submit_task(request)


@router.post("/quick/plate-assay",
    dependencies=[Depends(require_scopes(["lab-equipment:execute"]))],
    response_model=Dict[str, Any]
)
async def quick_plate_assay(
    assay_type: str = "viability",
    plate_format: int = 96,
    read_mode: str = "absorbance",
    wavelength: int = 450
) -> Dict[str, Any]:
    """
    Quick endpoint for plate reader assays
    """
    request = TaskSubmissionRequest(
        equipment_id="reader_001",
        task_type=read_mode,
        parameters={
            "assay_type": assay_type,
            "plate_format": plate_format,
            "read_mode": read_mode,
            "wavelength": wavelength,
            "temperature": 37
        },
        priority=3,
        estimated_duration=300
    )

    return await submit_task(request)
