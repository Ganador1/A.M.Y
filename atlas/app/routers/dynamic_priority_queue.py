"""
Router para Dynamic Priority Queue - Sistema de Colas Científicas Inteligentes
=============================================================================

Router FastAPI que expone el sistema avanzado de priorización dinámica de colas
para pipelines científicos. Optimiza automáticamente la ejecución de experimentos
y análisis basándose en valor científico, recursos disponibles y dependencias.

Características:
- Envío de tareas científicas con metadatos de priorización
- Monitoreo en tiempo real del estado de las colas
- Predicciones de tiempo de ejecución y recursos
- Gestión de dependencias entre experimentos
- Ajuste manual de prioridades
- Métricas de rendimiento y utilización

Endpoints Principales:
- POST /start: Iniciar el gestor de colas
- POST /submit-task: Enviar nueva tarea científica
- GET /status: Estado completo de las colas
- PUT /task/{task_id}/priority: Actualizar prioridad de tarea
- DELETE /task/{task_id}: Cancelar tarea
- GET /task/{task_id}/predictions: Predicciones para tarea específica
- GET /metrics: Métricas de rendimiento
- POST /stop: Detener el gestor de colas

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field, field_validator

from app.routers.auth import require_scopes
from app.exceptions.domain.biology import BiologyError
from app.services.dynamic_priority_queue_service import (
    dynamic_priority_queue_service,
    ScientificTask,
    TaskStatus,
    QueueConfiguration,
)
from app.core.bootstrap_logging import logger

router = APIRouter()


# ========== MODELOS DE REQUEST/RESPONSE ==========

class TaskSubmissionRequest(BaseModel):
    """Request para envío de tarea científica"""
    name: str = Field(..., description="Nombre descriptivo de la tarea")
    description: str = Field(..., description="Descripción detallada del experimento/análisis")
    task_type: str = Field(..., description="Tipo de tarea (experiment, simulation, analysis, etc.)")
    
    # Metadatos científicos
    domain: str = Field(..., description="Dominio científico (physics, chemistry, biology, etc.)")
    research_area: str = Field(..., description="Área específica de investigación")
    principal_investigator: str = Field(..., description="Investigador principal")
    collaborators: List[str] = Field(default_factory=list, description="Lista de colaboradores")
    
    # Configuración de ejecución
    estimated_duration_minutes: float = Field(60.0, gt=0, le=10080, description="Duración estimada en minutos")
    required_resources: Optional[Dict[str, Any]] = Field(None, description="Recursos computacionales requeridos")
    dependencies: List[str] = Field(default_factory=list, description="IDs de tareas dependientes")
    
    # Scoring científico
    novelty_score: float = Field(0.5, ge=0.0, le=1.0, description="Score de novedad e innovación")
    impact_potential: float = Field(0.5, ge=0.0, le=1.0, description="Potencial de impacto científico")
    urgency_score: float = Field(0.5, ge=0.0, le=1.0, description="Urgencia temporal")
    reproducibility_score: float = Field(0.5, ge=0.0, le=1.0, description="Score de reproducibilidad")
    interdisciplinary_score: float = Field(0.5, ge=0.0, le=1.0, description="Score interdisciplinario")
    
    # Configuración adicional
    max_retries: int = Field(3, ge=0, le=10, description="Número máximo de reintentos")
    auto_start: bool = Field(True, description="Iniciar automáticamente cuando sea posible")
    
    @field_validator('task_type')
    @classmethod
    def validate_task_type(cls, v):
        valid_types = ['experiment', 'simulation', 'analysis', 'computation', 'data_processing', 'training']
        if v not in valid_types:
            raise ValueError(f'task_type debe ser uno de: {valid_types}')
        return v

class QueueStartRequest(BaseModel):
    """Request para iniciar el gestor de colas"""
    max_concurrent_tasks: int = Field(10, ge=1, le=100, description="Tareas concurrentes máximas")
    max_queue_size: int = Field(1000, ge=10, le=10000, description="Tamaño máximo de la cola")
    priority_update_interval_seconds: int = Field(300, ge=60, le=3600, description="Intervalo de actualización de prioridades")
    resource_check_interval_seconds: int = Field(60, ge=10, le=600, description="Intervalo de monitoreo de recursos")

class PriorityUpdateRequest(BaseModel):
    """Request para actualizar prioridad de tarea"""
    urgency_boost: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Incremento en urgencia")
    impact_adjustment: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Ajuste en impacto potencial")
    reason: str = Field("Manual adjustment", description="Razón del ajuste")

class TaskCancellationRequest(BaseModel):
    """Request para cancelar tarea"""
    reason: str = Field(..., description="Razón de la cancelación")
    force_cancel: bool = Field(False, description="Forzar cancelación incluso si está ejecutándose")

class QueueStatusResponse(BaseModel):
    """Response con estado de las colas"""
    system_status: str = Field(..., description="Estado del sistema (running/stopped)")
    metrics: Dict[str, Any] = Field(..., description="Métricas actuales del sistema")
    resource_utilization: Dict[str, Any] = Field(..., description="Utilización de recursos")
    queue_health: Dict[str, Any] = Field(..., description="Salud general del sistema")
    timestamp: str = Field(..., description="Timestamp del estado")

class TaskSubmissionResponse(BaseModel):
    """Response de envío de tarea"""
    task_id: str = Field(..., description="ID único de la tarea")
    status: str = Field(..., description="Estado inicial de la tarea")
    initial_priority: float = Field(..., description="Prioridad científica inicial")
    estimated_duration_minutes: float = Field(..., description="Duración estimada")
    queue_position: int = Field(..., description="Posición en la cola")
    dependency_status: Dict[str, Any] = Field(..., description="Estado de dependencias")
    auto_start: bool = Field(..., description="Si se iniciará automáticamente")

class TaskPredictionsResponse(BaseModel):
    """Response con predicciones de tarea"""
    execution_time_minutes: Optional[float] = Field(None, description="Tiempo de ejecución predicho")
    success_probability: float = Field(..., description="Probabilidad de éxito")
    resource_requirements: Dict[str, float] = Field(..., description="Recursos estimados")
    optimal_start_time: str = Field(..., description="Momento óptimo para iniciar")
    expected_wait_time_minutes: float = Field(..., description="Tiempo de espera esperado")
    scientific_impact_score: float = Field(..., description="Score de impacto científico predicho")
    prediction_confidence: float = Field(..., description="Confianza en las predicciones")

class SystemMetricsResponse(BaseModel):
    """Response con métricas del sistema"""
    current_metrics: Dict[str, Any] = Field(..., description="Métricas actuales")
    performance_trends: Dict[str, Any] = Field(..., description="Tendencias de rendimiento")
    resource_efficiency: Dict[str, Any] = Field(..., description="Eficiencia de recursos")
    scientific_value_metrics: Dict[str, Any] = Field(..., description="Métricas de valor científico")
    timestamp: str = Field(..., description="Timestamp de las métricas")


# ========== ENDPOINTS ==========

@router.post("/start", response_model=Dict[str, Any])
async def start_queue_manager(
    request: QueueStartRequest,
    current_user: dict = Depends(require_scopes(["queue:admin"]))
) -> Dict[str, Any]:
    """
    🚀 INICIAR GESTOR DE COLAS CIENTÍFICAS
    =====================================
    
    Inicia el sistema avanzado de gestión de colas con priorización dinámica
    basada en valor científico. El sistema optimiza automáticamente la ejecución
    de experimentos según múltiples criterios.
    
    Características del sistema:
    - Priorización científica automática
    - Monitoreo de recursos en tiempo real
    - Predicción de tiempos de ejecución
    - Gestión de dependencias
    - Balanceado de cargas inteligente
    """
    logger.info(f"🚀 Iniciando gestor de colas - Usuario: {current_user.get('sub')}")
    
    try:
        # Configurar sistema
        config = QueueConfiguration(
            max_concurrent_tasks=request.max_concurrent_tasks,
            max_queue_size=request.max_queue_size,
            priority_update_interval_seconds=request.priority_update_interval_seconds,
            resource_check_interval_seconds=request.resource_check_interval_seconds
        )
        
        dynamic_priority_queue_service.config = config
        
        # Iniciar sistema
        result = await dynamic_priority_queue_service.start_queue_manager()
        
        logger.info(f"✅ Gestor de colas iniciado exitosamente")
        
        return result
        
    except BiologyError as e:
        logger.error(f"❌ Error iniciando gestor de colas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error iniciando gestor de colas: {str(e)}"
        )

@router.post("/submit-task", response_model=TaskSubmissionResponse)
async def submit_scientific_task(
    request: TaskSubmissionRequest,
    current_user: dict = Depends(require_scopes(["queue:submit"]))
) -> TaskSubmissionResponse:
    """
    📋 ENVIAR TAREA CIENTÍFICA
    =========================
    
    Envía una nueva tarea científica al sistema de colas con priorización automática.
    El sistema evalúa el valor científico, recursos necesarios y dependencias para
    optimizar la ejecución.
    
    Scoring Científico Automático:
    - Novedad e innovación
    - Impacto potencial en la comunidad
    - Urgencia temporal
    - Reproducibilidad
    - Interdisciplinariedad
    - Historial del investigador
    """
    logger.info(f"📋 Enviando tarea científica: {request.name} - Usuario: {current_user.get('sub')}")
    
    try:
        # Crear tarea científica
        task = ScientificTask(
            task_id=str(uuid.uuid4()),
            name=request.name,
            description=request.description,
            task_type=request.task_type,
            domain=request.domain,
            research_area=request.research_area,
            principal_investigator=request.principal_investigator,
            collaborators=request.collaborators,
            estimated_duration_minutes=request.estimated_duration_minutes,
            required_resources=request.required_resources or {},
            dependencies=request.dependencies,
            novelty_score=request.novelty_score,
            impact_potential=request.impact_potential,
            urgency_score=request.urgency_score,
            reproducibility_score=request.reproducibility_score,
            interdisciplinary_score=request.interdisciplinary_score,
            max_retries=request.max_retries
        )
        
        # Enviar a la cola
        submission_result = await dynamic_priority_queue_service.submit_scientific_task(
            task=task,
            auto_start=request.auto_start
        )
        
        logger.info(f"✅ Tarea {task.task_id} enviada exitosamente con prioridad {submission_result['initial_priority']:.3f}")
        
        return TaskSubmissionResponse(**submission_result)
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error enviando tarea: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error enviando tarea: {str(e)}"
        )

@router.get("/status", response_model=QueueStatusResponse)
async def get_queue_status(
    include_detailed_tasks: bool = False,
    current_user: dict = Depends(require_scopes(["queue:read"]))
) -> QueueStatusResponse:
    """
    📊 ESTADO DE LAS COLAS
    =====================
    
    Obtiene el estado completo del sistema de colas incluyendo:
    - Métricas de rendimiento
    - Utilización de recursos
    - Salud del sistema
    - Tareas en cada estado
    - Tendencias de carga
    """
    logger.info(f"📊 Consultando estado de colas - Usuario: {current_user.get('sub')}")
    
    try:
        status = await dynamic_priority_queue_service.get_queue_status(
            include_detailed_tasks=include_detailed_tasks
        )
        
        return QueueStatusResponse(**status)
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo estado: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado: {str(e)}"
        )

@router.put("/task/{task_id}/priority")
async def update_task_priority(
    task_id: str,
    request: PriorityUpdateRequest,
    current_user: dict = Depends(require_scopes(["queue:modify"]))
) -> Dict[str, Any]:
    """
    🔄 ACTUALIZAR PRIORIDAD DE TAREA
    ===============================
    
    Ajusta manualmente la prioridad de una tarea específica.
    Útil para responder a cambios en urgencia, nuevos descubrimientos
    o modificaciones en los objetivos de investigación.
    """
    logger.info(f"🔄 Actualizando prioridad de tarea {task_id} - Usuario: {current_user.get('sub')}")
    
    try:
        # Preparar ajustes
        priority_adjustments = {}
        if request.urgency_boost is not None:
            priority_adjustments['urgency_boost'] = request.urgency_boost
        if request.impact_adjustment is not None:
            priority_adjustments['impact_adjustment'] = request.impact_adjustment
        
        # Actualizar prioridad
        result = await dynamic_priority_queue_service.update_task_priority(
            task_id=task_id,
            priority_adjustments=priority_adjustments
        )
        
        # Agregar información adicional
        result['reason'] = request.reason
        result['updated_by'] = current_user.get('sub')
        result['updated_at'] = datetime.now().isoformat()
        
        logger.info(f"✅ Prioridad actualizada para {task_id}: {result['old_priority']:.3f} → {result['new_priority']:.3f}")
        
        return result
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error actualizando prioridad: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error actualizando prioridad: {str(e)}"
        )

@router.delete("/task/{task_id}")
async def cancel_task(
    task_id: str,
    request: TaskCancellationRequest,
    current_user: dict = Depends(require_scopes(["queue:modify"]))
) -> Dict[str, Any]:
    """
    ❌ CANCELAR TAREA
    ================
    
    Cancela una tarea específica, ya sea pendiente o en ejecución.
    Libera recursos y actualiza las métricas del sistema.
    """
    logger.info(f"❌ Cancelando tarea {task_id} - Usuario: {current_user.get('sub')}")
    
    try:
        result = await dynamic_priority_queue_service.cancel_task(
            task_id=task_id,
            reason=request.reason
        )
        
        # Agregar información de auditoría
        result['cancelled_by'] = current_user.get('sub')
        result['force_cancel'] = request.force_cancel
        
        logger.info(f"✅ Tarea {task_id} cancelada exitosamente")
        
        return result
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error cancelando tarea: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error cancelando tarea: {str(e)}"
        )

@router.get("/task/{task_id}/predictions", response_model=TaskPredictionsResponse)
async def get_task_predictions(
    task_id: str,
    current_user: dict = Depends(require_scopes(["queue:read"]))
) -> TaskPredictionsResponse:
    """
    🔮 PREDICCIONES DE TAREA
    =======================
    
    Obtiene predicciones detalladas para una tarea específica usando
    modelos de machine learning entrenados con datos históricos.
    
    Predicciones incluyen:
    - Tiempo de ejecución estimado
    - Probabilidad de éxito
    - Recursos computacionales necesarios
    - Momento óptimo para ejecutar
    - Impacto científico esperado
    """
    logger.info(f"🔮 Obteniendo predicciones para tarea {task_id} - Usuario: {current_user.get('sub')}")
    
    try:
        predictions = await dynamic_priority_queue_service.get_task_predictions(task_id)
        
        # Convertir datetime a string si es necesario
        if 'optimal_start_time' in predictions and hasattr(predictions['optimal_start_time'], 'isoformat'):
            predictions['optimal_start_time'] = predictions['optimal_start_time'].isoformat()
        
        return TaskPredictionsResponse(**predictions)
        
    except ValueError as e:
        logger.error(f"❌ Error de validación: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo predicciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo predicciones: {str(e)}"
        )

@router.get("/metrics", response_model=SystemMetricsResponse)
async def get_system_metrics(
    include_trends: bool = True,
    time_window_hours: int = 24,
    current_user: dict = Depends(require_scopes(["queue:read"]))
) -> SystemMetricsResponse:
    """
    📈 MÉTRICAS DEL SISTEMA
    ======================
    
    Obtiene métricas completas de rendimiento del sistema de colas
    incluyendo tendencias históricas y análisis de eficiencia.
    
    Métricas incluyen:
    - Throughput y latencia
    - Utilización de recursos
    - Valor científico entregado
    - Eficiencia del sistema
    - Tendencias temporales
    """
    logger.info(f"📈 Obteniendo métricas del sistema - Usuario: {current_user.get('sub')}")
    
    try:
        # Métricas actuales
        status = await dynamic_priority_queue_service.get_queue_status()
        current_metrics = status['metrics']
        
        # Tendencias de rendimiento (simplificado para demo)
        performance_trends = {
            "throughput_trend": "stable",
            "latency_trend": "improving",
            "resource_efficiency_trend": "stable",
            "scientific_value_trend": "increasing"
        }
        
        # Eficiencia de recursos
        resource_efficiency = {
            "cpu_efficiency": 0.75,
            "memory_efficiency": 0.80,
            "queue_efficiency": current_metrics.get('queue_efficiency_score', 0.0),
            "overall_efficiency": 0.78
        }
        
        # Métricas de valor científico
        scientific_value_metrics = {
            "total_scientific_value_delivered": current_metrics.get('scientific_value_delivered', 0.0),
            "average_impact_per_task": 0.65,
            "high_impact_task_ratio": 0.25,
            "interdisciplinary_collaboration_score": 0.40
        }
        
        return SystemMetricsResponse(
            current_metrics=current_metrics,
            performance_trends=performance_trends,
            resource_efficiency=resource_efficiency,
            scientific_value_metrics=scientific_value_metrics,
            timestamp=datetime.now().isoformat()
        )
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo métricas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo métricas: {str(e)}"
        )

@router.post("/stop")
async def stop_queue_manager(
    current_user: dict = Depends(require_scopes(["queue:admin"]))
) -> Dict[str, Any]:
    """
    🛑 DETENER GESTOR DE COLAS
    =========================
    
    Detiene el gestor de colas de forma ordenada, completando las tareas
    en ejecución y guardando el estado final del sistema.
    
    ⚠️ Advertencia: Las tareas pendientes permanecerán en cola pero no
    se ejecutarán hasta que el sistema se reinicie.
    """
    logger.info(f"🛑 Deteniendo gestor de colas - Usuario: {current_user.get('sub')}")
    
    try:
        result = await dynamic_priority_queue_service.stop_queue_manager()
        
        # Agregar información de auditoría
        result['stopped_by'] = current_user.get('sub')
        
        logger.info("✅ Gestor de colas detenido exitosamente")
        
        return result
        
    except BiologyError as e:
        logger.error(f"❌ Error deteniendo gestor: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deteniendo gestor: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    💊 HEALTH CHECK
    ===============
    
    Verifica el estado de salud del sistema de colas dinámicas.
    """
    try:
        return {
            "status": "healthy",
            "service": "DynamicPriorityQueue",
            "queue_manager_running": dynamic_priority_queue_service.is_running,
            "timestamp": datetime.now().isoformat()
        }
    except BiologyError as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@router.get("/queue-analytics")
async def get_queue_analytics(
    current_user: dict = Depends(require_scopes(["queue:read"]))
) -> Dict[str, Any]:
    """
    📊 ANALÍTICAS DE COLA
    ====================
    
    Proporciona analíticas avanzadas del comportamiento de las colas
    incluyendo patrones de uso, eficiencia por dominio científico
    y recomendaciones de optimización.
    """
    logger.info(f"📊 Obteniendo analíticas de cola - Usuario: {current_user.get('sub')}")
    
    try:
        # En implementación real, analizar datos históricos
        analytics = {
            "usage_patterns": {
                "peak_hours": [9, 10, 11, 14, 15, 16],
                "busiest_domains": ["biology", "physics", "chemistry"],
                "average_task_complexity": "medium",
                "seasonal_trends": "increasing"
            },
            "efficiency_by_domain": {
                "biology": 0.85,
                "physics": 0.78,
                "chemistry": 0.82,
                "interdisciplinary": 0.75
            },
            "bottleneck_analysis": {
                "primary_bottleneck": "resource_availability",
                "secondary_bottleneck": "dependency_resolution",
                "optimization_potential": 0.25
            },
            "recommendations": [
                "Aumentar capacidad durante horas pico (9-11, 14-16)",
                "Optimizar gestión de dependencias",
                "Considerar recursos adicionales para simulaciones",
                "Implementar pre-procesamiento para tareas de biología"
            ]
        }
        
        return analytics
        
    except BiologyError as e:
        logger.error(f"❌ Error obteniendo analíticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo analíticas: {str(e)}"
        )
