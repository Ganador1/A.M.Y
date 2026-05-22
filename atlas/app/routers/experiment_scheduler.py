"""
Router del Programador de Experimentos - Gestión de Trabajos Experimentales

Módulo FastAPI para programación y gestión de trabajos experimentales automatizados.
Proporciona endpoints REST API para crear, programar, monitorear y controlar la ejecución
de experimentos científicos con prioridades, reintentos y ejecución programada.

Capacidades principales:
- Programación de trabajos: creación de trabajos con ejecución inmediata o programada
- Gestión de prioridades: sistema de prioridades con mapeo automático por plausibilidad
- Reintentos inteligentes: reejecución automática de trabajos fallidos
- Trabajos recurrentes: ejecución periódica con intervalos configurables
- Monitoreo completo: estadísticas detalladas y estado de trabajos
- Control administrativo: inicio/parada manual del scheduler
- Filtrado y paginación: consultas eficientes de listas de trabajos

Catálogo de Endpoints:
- POST /scheduler/jobs: Creación de nuevos trabajos experimentales
- GET /scheduler/jobs: Listado de trabajos con filtros y paginación
- GET /scheduler/jobs/{job_uuid}: Información detallada de trabajo específico
- POST /scheduler/jobs/{job_uuid}/cancel: Cancelación de trabajos pendientes
- POST /scheduler/jobs/{job_uuid}/retry: Reintento manual de trabajos fallidos
- GET /scheduler/stats: Estadísticas generales del scheduler
- POST /scheduler/start: Inicio del procesamiento automático
- POST /scheduler/stop: Detención del procesamiento automático
- POST /scheduler/tick: Ejecución manual de un ciclo de procesamiento
- POST /scheduler/demo/create-sample-jobs: Creación de trabajos de ejemplo

Dependencias:
- ExperimentSchedulerService: Servicio central de programación de experimentos
- ExperimentJobState: Estados posibles de los trabajos experimentales
- require_scopes: Sistema de autenticación y autorización por scopes
- Pydantic BaseModel: Modelos de validación para requests/responses
- FastAPI Depends: Sistema de inyección de dependencias

Uso del Servicio:
    El router permite programar experimentos con diferentes niveles de prioridad
    y ejecución automática. Soporta trabajos únicos y recurrentes, con sistema
    de reintentos para mayor fiabilidad. Incluye mapeo automático de scores de
    plausibilidad a prioridades, facilitando la integración con sistemas de
    evaluación automática de hipótesis.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Depends, Query
from app.security import require_scopes
from pydantic import BaseModel, Field

from app.services.experiment_scheduler_service import ExperimentSchedulerService
from app.models.experiment_scheduler_models import ExperimentJobState
from app.exceptions.domain.biology import BiologyError

router = APIRouter(prefix="/scheduler", tags=["experiment-scheduler"])

# Dependency para obtener el servicio scheduler
def get_scheduler_service() -> ExperimentSchedulerService:
    """Dependency que proporciona una instancia del ExperimentSchedulerService."""
    return ExperimentSchedulerService()


class JobCreateRequest(BaseModel):
    """Request model para crear un nuevo trabajo experimental."""
    name: str = Field(..., description="Nombre descriptivo del trabajo")
    payload: Dict[str, Any] = Field(..., description="Datos JSON para el trabajo")
    run_at: Optional[datetime] = Field(None, description="Cuándo ejecutar (None = inmediato)")
    interval: Optional[int] = Field(None, description="Intervalo en segundos para repetición")
    priority: int = Field(1, ge=1, le=5, description="Prioridad del trabajo (1=alta, 5=baja)")
    max_retries: int = Field(3, ge=0, le=10, description="Máximo número de reintentos")
    plausibility_score: Optional[float] = Field(None, ge=0.0, le=1.0, 
                                                description="Score de plausibilidad para mapeo automático a prioridad")


class JobCreateResponse(BaseModel):
    """Response model para creación de trabajos."""
    job_uuid: str
    message: str


class JobInfo(BaseModel):
    """Model para información completa de un trabajo."""
    job_uuid: str
    name: str
    payload: Dict[str, Any]
    state: str
    run_at: Optional[str] = None
    interval_seconds: Optional[int] = None
    priority: int
    max_retries: int
    retry_count: int
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class JobListItem(BaseModel):
    """Model para elementos en lista de trabajos."""
    job_uuid: str
    name: str
    state: str
    run_at: Optional[str] = None
    priority: int
    retry_count: int
    created_at: Optional[str] = None


class SchedulerStats(BaseModel):
    """Model para estadísticas del scheduler."""
    pending: int
    running: int
    completed: int
    failed: int
    cancelled: int
    priority_breakdown: Dict[str, int]
    scheduler_running: bool


@router.post("/jobs", response_model=JobCreateResponse, dependencies=[Depends(require_scopes(["scheduler"]))])
async def create_job(
    request: JobCreateRequest,
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> JobCreateResponse:
    """
    Crea un nuevo trabajo experimental programado.
    
    - **name**: Nombre descriptivo del trabajo
    - **payload**: Datos JSON que se pasarán al trabajo
    - **run_at**: Fecha/hora de ejecución (opcional, None = inmediato)
    - **interval**: Intervalo en segundos para trabajos recurrentes (opcional)
    - **priority**: Prioridad manual (1-5, donde 1 es más alta)
    - **max_retries**: Número máximo de reintentos en caso de fallo
    - **plausibility_score**: Score de plausibilidad (0.0-1.0) para mapeo automático a prioridad
    
    Si se proporciona `plausibility_score`, se mapea automáticamente a prioridad:
    - 0.8-1.0 → prioridad 1 (alta)
    - 0.6-0.8 → prioridad 2 
    - 0.4-0.6 → prioridad 3
    - 0.0-0.4 → prioridad 4 (baja)
    """
    try:
        job_uuid = scheduler.submit(
            name=request.name,
            payload=request.payload,
            run_at=request.run_at,
            interval=request.interval,
            priority=request.priority,
            max_retries=request.max_retries,
            plausibility_score=request.plausibility_score
        )
        
        return JobCreateResponse(
            job_uuid=job_uuid,
            message=f"Trabajo '{request.name}' creado exitosamente"
        )
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error creando trabajo: {str(e)}")


@router.get("/jobs", response_model=List[JobListItem], dependencies=[Depends(require_scopes(["scheduler"]))])
async def list_jobs(
    state: Optional[str] = Query(None, description="Filtrar por estado (pending, running, completed, failed, cancelled)"),
    limit: int = Query(50, ge=1, le=500, description="Máximo número de resultados"),
    offset: int = Query(0, ge=0, description="Número de resultados a saltar"),
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> List[JobListItem]:
    """
    Lista trabajos experimentales con filtros opcionales.
    
    - **state**: Filtrar por estado específico
    - **limit**: Máximo número de trabajos a retornar (1-500)
    - **offset**: Número de trabajos a omitir (para paginación)
    
    Los resultados se ordenan por prioridad (alta primero) y luego por fecha de creación.
    """
    try:
        # Mapear string a enum si se proporciona
        state_filter = None
        if state:
            try:
                state_filter = ExperimentJobState(state.lower())
            except ValueError:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Estado inválido: {state}. Valores válidos: {[s.value for s in ExperimentJobState]}"
                )
        
        jobs_data = scheduler.list_jobs(state=state_filter, limit=limit, offset=offset)
        
        return [JobListItem(**job) for job in jobs_data]
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error listando trabajos: {str(e)}")


@router.get("/jobs/{job_uuid}", response_model=JobInfo, dependencies=[Depends(require_scopes(["scheduler"]))])
async def get_job(
    job_uuid: str,
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> JobInfo:
    """
    Obtiene información detallada de un trabajo específico.
    
    - **job_uuid**: UUID único del trabajo
    """
    try:
        job_data = scheduler.get_job(job_uuid)
        
        if job_data is None:
            raise HTTPException(status_code=404, detail=f"Trabajo no encontrado: {job_uuid}")
        
        return JobInfo(**job_data)
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo trabajo: {str(e)}")


@router.post("/jobs/{job_uuid}/cancel", dependencies=[Depends(require_scopes(["scheduler"]))])
async def cancel_job(
    job_uuid: str,
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Cancela un trabajo pendiente o en ejecución.
    
    - **job_uuid**: UUID único del trabajo a cancelar
    """
    try:
        success = scheduler.cancel_job(job_uuid)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail=f"No se pudo cancelar el trabajo: {job_uuid}. Puede que no exista o ya esté completado/cancelado."
            )
        
        return {
            "job_uuid": job_uuid,
            "message": "Trabajo cancelado exitosamente",
            "cancelled": True
        }
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error cancelando trabajo: {str(e)}")


@router.post("/jobs/{job_uuid}/retry", dependencies=[Depends(require_scopes(["scheduler"]))])
async def retry_job(
    job_uuid: str,
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Reintenta manualmente un trabajo fallido.
    
    - **job_uuid**: UUID único del trabajo a reintentar
    """
    try:
        success = scheduler.retry_failed_job(job_uuid)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail=f"No se pudo reintentar el trabajo: {job_uuid}. Puede que no exista o no esté en estado 'failed'."
            )
        
        return {
            "job_uuid": job_uuid,
            "message": "Trabajo reintentado exitosamente",
            "retried": True
        }
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error reintentando trabajo: {str(e)}")


@router.get("/stats", response_model=SchedulerStats, dependencies=[Depends(require_scopes(["scheduler"]))])
async def get_scheduler_stats(
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> SchedulerStats:
    """
    Obtiene estadísticas generales del scheduler.
    
    Incluye:
    - Conteos de trabajos por estado
    - Distribución de trabajos pendientes por prioridad
    - Estado del scheduler (corriendo/detenido)
    """
    try:
        stats_data = scheduler.get_scheduler_stats()
        return SchedulerStats(**stats_data)
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error obteniendo estadísticas: {str(e)}")


@router.post("/start", dependencies=[Depends(require_scopes(["scheduler:admin"]))])
async def start_scheduler(
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Inicia el bucle de procesamiento del scheduler.
    
    Una vez iniciado, el scheduler procesará automáticamente trabajos pendientes cada 5 segundos.
    """
    try:
        scheduler.start_scheduler()
        return {
            "message": "Scheduler iniciado exitosamente",
            "running": True
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error iniciando scheduler: {str(e)}")


@router.post("/stop", dependencies=[Depends(require_scopes(["scheduler:admin"]))])
async def stop_scheduler(
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Detiene el bucle de procesamiento del scheduler.
    
    Los trabajos pendientes no se procesarán hasta que se reinicie el scheduler.
    """
    try:
        scheduler.stop_scheduler()
        return {
            "message": "Scheduler detenido exitosamente",
            "running": False
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error deteniendo scheduler: {str(e)}")


@router.post("/tick", dependencies=[Depends(require_scopes(["scheduler:admin"]))])
async def manual_tick(
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Ejecuta manualmente un tick del scheduler.
    
    Procesa trabajos pendientes que estén listos para ejecutarse sin esperar al bucle automático.
    """
    try:
        await scheduler.tick()
        return {
            "message": "Tick ejecutado exitosamente",
            "timestamp": datetime.utcnow().isoformat()
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error ejecutando tick: {str(e)}")


# Endpoint de utilidad para pruebas y demos
@router.post("/demo/create-sample-jobs", dependencies=[Depends(require_scopes(["scheduler"]))])
async def create_sample_jobs(
    count: int = Query(3, ge=1, le=10, description="Número de trabajos de ejemplo a crear"),
    scheduler: ExperimentSchedulerService = Depends(get_scheduler_service)
) -> Dict[str, Any]:
    """
    Crea trabajos de ejemplo para demostraciones y pruebas.
    
    - **count**: Número de trabajos de ejemplo a crear (1-10)
    """
    try:
        created_jobs = []
        
        for i in range(count):
            job_uuid = scheduler.submit(
                name=f"demo-job-{i+1}",
                payload={
                    "demo": True,
                    "iteration": i+1,
                    "message": f"Este es un trabajo de demostración #{i+1}"
                },
                priority=((i % 3) + 1),  # Prioridades variadas 1-3
                plausibility_score=0.7 + (i * 0.1) % 0.3  # Scores variados
            )
            created_jobs.append(job_uuid)
        
        return {
            "message": f"{count} trabajos de ejemplo creados exitosamente",
            "job_uuids": created_jobs,
            "count": len(created_jobs)
        }
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Error creando trabajos de ejemplo: {str(e)}")
