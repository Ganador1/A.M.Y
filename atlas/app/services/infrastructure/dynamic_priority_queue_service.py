"""
Dynamic Priority Queue Service para Pipelines Científicos
========================================================

Servicio avanzado para gestión de colas de priorización dinámica basada en valor científico.
Optimiza automáticamente la ejecución de experimentos, análisis y tareas computacionales
según múltiples criterios de valor científico y recursos disponibles.

Características Principales:
- Scoring dinámico basado en valor científico
- Priorización adaptativa en tiempo real
- Balanceador de cargas inteligente
- Predicción de tiempo de ejecución
- Optimización de recursos computacionales
- Análisis de dependencias entre tareas
- Sistema de penalizaciones y recompensas

Algoritmos de Priorización:
- Scientific Value Scoring (SVS)
- Resource-Aware Priority Scheduling (RAPS)
- Dependency-Based Task Ordering (DBTO)
- Temporal Relevance Weighting (TRW)
- Impact Factor Prediction (IFP)

Métricas de Valor Científico:
- Novedad e innovación del experimento
- Impacto potencial en la comunidad científica
- Urgencia temporal y deadlines
- Disponibilidad de recursos computacionales
- Dependencias entre experimentos
- Historial de éxito del investigador/equipo
- Reproducibilidad y robustez
- Interdisciplinariedad y colaboración

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
import asyncio
import time
import uuid
import heapq
from typing import Dict, Any, List, Optional, Union, Tuple, Callable
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json
from pathlib import Path

from app.services.base_service import BaseService
from app.exceptions.domain.biology import BiologyError
from app.types.dynamic_priority_queue_service_types import (
    ProcessRequestResult,
    StartQueueManagerResult,
    StopQueueManagerResult,
    CancelTaskResult,
    GetTaskPredictionsResult,
    ValidateTaskResult,
    AssessQueueHealthResult,
    TaskSummaryResult,
    CheckDependenciesResult,
)

# Machine Learning para predicciones
try:
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_absolute_error, r2_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Optimización de recursos
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Estados de las tareas en la cola"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class PriorityLevel(Enum):
    """Niveles de prioridad"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class ScientificTask:
    """Tarea científica con metadatos para priorización"""
    task_id: str
    name: str
    description: str
    task_type: str  # experiment, analysis, simulation, etc.
    
    # Metadatos científicos
    domain: str
    research_area: str
    principal_investigator: str
    collaborators: List[str] = field(default_factory=list)
    
    # Configuración de ejecución
    estimated_duration_minutes: float = 60.0
    required_resources: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    # Scoring científico
    novelty_score: float = 0.5
    impact_potential: float = 0.5
    urgency_score: float = 0.5
    reproducibility_score: float = 0.5
    interdisciplinary_score: float = 0.5
    
    # Estado y timestamps
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Priorización dinámica
    dynamic_priority: float = 0.5
    last_priority_update: datetime = field(default_factory=datetime.now)
    execution_attempts: int = 0
    max_retries: int = 3
    
    # Resultados y feedback
    success_probability: float = 0.8
    actual_duration: Optional[float] = None
    quality_score: Optional[float] = None
    scientific_output: Optional[Dict[str, Any]] = None


@dataclass
class QueueConfiguration:
    """Configuración del sistema de colas"""
    max_concurrent_tasks: int = 10
    max_queue_size: int = 1000
    priority_update_interval_seconds: int = 300  # 5 minutos
    resource_check_interval_seconds: int = 60    # 1 minuto
    
    # Pesos para scoring científico
    scoring_weights: Dict[str, float] = field(default_factory=lambda: {
        'novelty': 0.25,
        'impact': 0.25,
        'urgency': 0.20,
        'reproducibility': 0.15,
        'interdisciplinary': 0.10,
        'researcher_track_record': 0.05
    })
    
    # Configuración de recursos
    resource_limits: Dict[str, Any] = field(default_factory=lambda: {
        'max_cpu_percent': 80,
        'max_memory_gb': 16,
        'max_gpu_utilization': 90,
        'max_disk_io_mb_s': 100
    })


@dataclass
class QueueMetrics:
    """Métricas del sistema de colas"""
    total_tasks: int = 0
    pending_tasks: int = 0
    running_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    
    average_wait_time_minutes: float = 0.0
    average_execution_time_minutes: float = 0.0
    throughput_tasks_per_hour: float = 0.0
    resource_utilization_percent: float = 0.0
    
    queue_efficiency_score: float = 0.0
    scientific_value_delivered: float = 0.0


class DynamicPriorityQueueService(BaseService):
    """
    Servicio de gestión de colas con priorización dinámica científica
    """
    
    def __init__(self, config: Optional[QueueConfiguration] = None):
        super().__init__("DynamicPriorityQueue")
        
        # Configuración
        self.config = config or QueueConfiguration()
        
        # Estado de las colas
        self.priority_queue = []  # Min-heap para prioridades
        self.task_registry = {}  # task_id -> ScientificTask
        self.running_tasks = {}  # task_id -> task info
        self.completed_tasks = {}  # task_id -> results
        
        # Métricas y estadísticas
        self.metrics = QueueMetrics()
        self.performance_history = []
        self.prediction_models = {}
        
        # Sistema de scoring
        self.scientific_scoring_engine = ScientificScoringEngine()
        self.resource_monitor = ResourceMonitor()
        self.dependency_resolver = DependencyResolver()
        
        # Estado del sistema
        self.is_running = False
        self.worker_tasks = []
        
        logger.info("🚦 DynamicPriorityQueueService inicializado")
    
    async def process_request(self, operation: str, data: ProcessRequestResult) -> ProcessRequestResult:
        """
        Implementación del método abstracto process_request para DynamicPriorityQueueService
        
        Args:
            operation: Tipo de operación ('submit_task', 'get_status', 'cancel_task', 'update_priority')
            data: Datos de entrada con información de la tarea
            
        Returns:
            Resultado de la operación
        """
        try:
            if operation == "submit_task":
                # Crear tarea científica desde los datos
                task_data = data.get("task", {})
                task = ScientificTask(
                    task_id=task_data.get("task_id", str(uuid.uuid4())),
                    name=task_data.get("name", "Unnamed Task"),
                    description=task_data.get("description", ""),
                    task_type=task_data.get("task_type", "experiment"),
                    domain=task_data.get("domain", "general"),
                    research_area=task_data.get("research_area", "general"),
                    principal_investigator=task_data.get("principal_investigator", "unknown"),
                    estimated_duration_minutes=task_data.get("estimated_duration_minutes", 60.0),
                    novelty_score=task_data.get("novelty_score", 0.5),
                    impact_potential=task_data.get("impact_potential", 0.5),
                    urgency_score=task_data.get("urgency_score", 0.5)
                )
                
                auto_start = data.get("auto_start", True)
                result = await self.submit_scientific_task(task, auto_start)
                
                return {
                    "success": True,
                    "operation": operation,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "get_status":
                include_detailed = data.get("include_detailed_tasks", False)
                result = await self.get_queue_status(include_detailed)
                
                return {
                    "success": True,
                    "operation": operation,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "cancel_task":
                task_id = data.get("task_id")
                reason = data.get("reason", "User requested cancellation")
                
                if not task_id:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": "task_id is required"
                    }
                
                result = await self.cancel_task(task_id, reason)
                
                return {
                    "success": True,
                    "operation": operation,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "update_priority":
                task_id = data.get("task_id")
                priority_adjustments = data.get("priority_adjustments", {})
                
                if not task_id:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": "task_id is required"
                    }
                
                result = await self.update_task_priority(task_id, priority_adjustments)
                
                return {
                    "success": True,
                    "operation": operation,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            elif operation == "get_predictions":
                task_id = data.get("task_id")
                
                if not task_id:
                    return {
                        "success": False,
                        "operation": operation,
                        "error": "task_id is required"
                    }
                
                result = await self.get_task_predictions(task_id)
                
                return {
                    "success": True,
                    "operation": operation,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            else:
                return {
                    "success": False,
                    "operation": operation,
                    "error": f"Unsupported operation: {operation}"
                }
                
        except BiologyError as e:
            logger.error(f"Error in DynamicPriorityQueueService.process_request: {str(e)}")
            return {
                "success": False,
                "operation": operation,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def start_queue_manager(self) -> StartQueueManagerResult:
        """
        Inicia el gestor de colas con todos los subsistemas
        """
        try:
            logger.info("🚀 Iniciando gestor de colas dinámicas")
            
            if self.is_running:
                return {"status": "already_running", "message": "Queue manager ya está activo"}
            
            self.is_running = True
            
            # Iniciar tareas de background
            self.worker_tasks = [
                asyncio.create_task(self._priority_updater()),
                asyncio.create_task(self._resource_monitor_loop()),
                asyncio.create_task(self._task_executor()),
                asyncio.create_task(self._metrics_collector()),
                asyncio.create_task(self._dependency_resolver_loop())
            ]
            
            # Inicializar modelos predictivos
            await self._initialize_prediction_models()
            
            logger.info("✅ Gestor de colas iniciado exitosamente")
            
            return {
                "status": "started",
                "message": "Queue manager iniciado",
                "config": {
                    "max_concurrent_tasks": self.config.max_concurrent_tasks,
                    "max_queue_size": self.config.max_queue_size,
                    "priority_update_interval": self.config.priority_update_interval_seconds
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except BiologyError as e:
            logger.error(f"❌ Error iniciando gestor de colas: {str(e)}")
            raise
    
    async def stop_queue_manager(self) -> StopQueueManagerResult:
        """
        Detiene el gestor de colas de forma ordenada
        """
        try:
            logger.info("🛑 Deteniendo gestor de colas")
            
            self.is_running = False
            
            # Cancelar tareas de background
            for task in self.worker_tasks:
                task.cancel()
            
            # Esperar a que las tareas terminen
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            
            # Guardar estado final
            final_metrics = await self._calculate_current_metrics()
            
            logger.info("✅ Gestor de colas detenido")
            
            return {
                "status": "stopped",
                "final_metrics": final_metrics,
                "tasks_in_queue": len(self.priority_queue),
                "running_tasks": len(self.running_tasks),
                "timestamp": datetime.now().isoformat()
            }
            
        except BiologyError as e:
            logger.error(f"❌ Error deteniendo gestor de colas: {str(e)}")
            raise
    
    async def submit_scientific_task(
        self,
        task: ScientificTask,
        auto_start: bool = True
    ) -> Dict[str, Any]:
        """
        Envía una nueva tarea científica a la cola
        
        Args:
            task: Tarea científica a enviar
            auto_start: Si iniciar automáticamente la ejecución
            
        Returns:
            Información de la tarea enviada
        """
        try:
            logger.info(f"📥 Enviando tarea científica: {task.name}")
            
            # Validar tarea
            validation_result = await self._validate_task(task)
            if not validation_result["valid"]:
                raise ValueError(f"Tarea inválida: {validation_result['reason']}")
            
            # Calcular prioridad científica inicial
            initial_priority = await self.scientific_scoring_engine.calculate_scientific_priority(task)
            task.dynamic_priority = initial_priority
            
            # Predecir tiempo de ejecución
            predicted_duration = await self._predict_execution_time(task)
            if predicted_duration:
                task.estimated_duration_minutes = predicted_duration
            
            # Verificar dependencias
            dependency_status = await self.dependency_resolver.check_dependencies(task)
            
            # Registrar tarea
            self.task_registry[task.task_id] = task
            
            # Agregar a cola de prioridad (usar negative priority para min-heap)
            priority_score = -task.dynamic_priority  # Negativo para max-heap comportamiento
            heapq.heappush(self.priority_queue, (priority_score, time.time(), task.task_id))
            
            # Actualizar métricas
            self.metrics.total_tasks += 1
            self.metrics.pending_tasks += 1
            
            logger.info(f"✅ Tarea {task.task_id} añadida con prioridad {initial_priority:.3f}")
            
            result = {
                "task_id": task.task_id,
                "status": "queued",
                "initial_priority": initial_priority,
                "estimated_duration_minutes": task.estimated_duration_minutes,
                "queue_position": len(self.priority_queue),
                "dependency_status": dependency_status,
                "auto_start": auto_start
            }
            
            if auto_start and self.is_running:
                # Trigger immediate evaluation
                await self._trigger_task_evaluation()
            
            return result
            
        except BiologyError as e:
            logger.error(f"❌ Error enviando tarea: {str(e)}")
            raise
    
    async def get_queue_status(
        self,
        include_detailed_tasks: bool = False
    ) -> Dict[str, Any]:
        """
        Obtiene estado completo de la cola
        
        Args:
            include_detailed_tasks: Incluir detalles de todas las tareas
            
        Returns:
            Estado completo del sistema de colas
        """
        try:
            current_metrics = await self._calculate_current_metrics()
            
            # Estado general
            queue_status = {
                "system_status": "running" if self.is_running else "stopped",
                "metrics": current_metrics,
                "resource_utilization": await self.resource_monitor.get_current_utilization(),
                "queue_health": await self._assess_queue_health(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Tareas detalladas si se solicita
            if include_detailed_tasks:
                queue_status.update({
                    "pending_tasks": [
                        self._task_summary(self.task_registry[task_id])
                        for _, _, task_id in self.priority_queue
                    ],
                    "running_tasks": [
                        self._task_summary(task_info["task"])
                        for task_info in self.running_tasks.values()
                    ],
                    "recent_completed": [
                        self._task_summary(task_info["task"])
                        for task_info in list(self.completed_tasks.values())[-10:]
                    ]
                })
            
            return queue_status
            
        except BiologyError as e:
            logger.error(f"❌ Error obteniendo estado de cola: {str(e)}")
            raise
    
    async def update_task_priority(
        self,
        task_id: str,
        priority_adjustments: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Actualiza manualmente la prioridad de una tarea
        
        Args:
            task_id: ID de la tarea
            priority_adjustments: Ajustes a aplicar
            
        Returns:
            Nueva información de prioridad
        """
        try:
            if task_id not in self.task_registry:
                raise ValueError(f"Tarea {task_id} no encontrada")
            
            task = self.task_registry[task_id]
            
            # Aplicar ajustes
            if 'urgency_boost' in priority_adjustments:
                task.urgency_score = min(1.0, task.urgency_score + priority_adjustments['urgency_boost'])
            
            if 'impact_adjustment' in priority_adjustments:
                task.impact_potential = max(0.0, min(1.0, 
                    task.impact_potential + priority_adjustments['impact_adjustment']))
            
            # Recalcular prioridad
            new_priority = await self.scientific_scoring_engine.calculate_scientific_priority(task)
            old_priority = task.dynamic_priority
            task.dynamic_priority = new_priority
            task.last_priority_update = datetime.now()
            
            # Reorganizar cola si está pendiente
            if task.status == TaskStatus.PENDING:
                await self._reorder_task_in_queue(task_id, new_priority)
            
            logger.info(f"🔄 Prioridad actualizada para {task_id}: {old_priority:.3f} → {new_priority:.3f}")
            
            return {
                "task_id": task_id,
                "old_priority": old_priority,
                "new_priority": new_priority,
                "adjustments_applied": priority_adjustments,
                "queue_position": await self._get_task_queue_position(task_id)
            }
            
        except BiologyError as e:
            logger.error(f"❌ Error actualizando prioridad: {str(e)}")
            raise
    
    async def cancel_task(self, task_id: str, reason: str = "") -> CancelTaskResult:
        """
        Cancela una tarea específica
        
        Args:
            task_id: ID de la tarea a cancelar
            reason: Razón de la cancelación
            
        Returns:
            Resultado de la cancelación
        """
        try:
            if task_id not in self.task_registry:
                raise ValueError(f"Tarea {task_id} no encontrada")
            
            task = self.task_registry[task_id]
            previous_status = task.status
            
            # Cancelar según estado actual
            if task.status == TaskStatus.PENDING:
                # Remover de la cola
                self._remove_from_queue(task_id)
                task.status = TaskStatus.CANCELLED
                self.metrics.pending_tasks -= 1
                
            elif task.status == TaskStatus.RUNNING:
                # Cancelar tarea en ejecución
                if task_id in self.running_tasks:
                    # En implementación real, enviar señal de cancelación
                    self.running_tasks[task_id]["cancelled"] = True
                    task.status = TaskStatus.CANCELLED
                    self.metrics.running_tasks -= 1
                
            elif task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                raise ValueError(f"No se puede cancelar tarea en estado {task.status.value}")
            
            # Registrar cancelación
            cancellation_info = {
                "task_id": task_id,
                "previous_status": previous_status.value,
                "reason": reason,
                "cancelled_at": datetime.now().isoformat()
            }
            
            logger.info(f"❌ Tarea {task_id} cancelada - Razón: {reason}")
            
            return cancellation_info
            
        except BiologyError as e:
            logger.error(f"❌ Error cancelando tarea: {str(e)}")
            raise
    
    async def get_task_predictions(self, task_id: str) -> GetTaskPredictionsResult:
        """
        Obtiene predicciones para una tarea específica
        
        Args:
            task_id: ID de la tarea
            
        Returns:
            Predicciones detalladas
        """
        try:
            if task_id not in self.task_registry:
                raise ValueError(f"Tarea {task_id} no encontrada")
            
            task = self.task_registry[task_id]
            
            # Predicciones múltiples
            predictions = {
                "execution_time_minutes": await self._predict_execution_time(task),
                "success_probability": await self._predict_success_probability(task),
                "resource_requirements": await self._predict_resource_usage(task),
                "optimal_start_time": await self._predict_optimal_start_time(task),
                "expected_wait_time_minutes": await self._predict_wait_time(task),
                "scientific_impact_score": await self._predict_scientific_impact(task)
            }
            
            # Confianza en las predicciones
            prediction_confidence = await self._calculate_prediction_confidence(task)
            predictions["prediction_confidence"] = prediction_confidence
            
            return predictions
            
        except BiologyError as e:
            logger.error(f"❌ Error obteniendo predicciones: {str(e)}")
            raise
    
    # ========== MÉTODOS DE BACKGROUND ==========
    
    async def _priority_updater(self):
        """Loop de actualización de prioridades dinámicas"""
        
        while self.is_running:
            try:
                await asyncio.sleep(self.config.priority_update_interval_seconds)
                
                if not self.priority_queue:
                    continue
                
                logger.debug("🔄 Actualizando prioridades dinámicas")
                
                # Actualizar prioridades de tareas pendientes
                tasks_updated = 0
                for _, _, task_id in self.priority_queue:
                    if task_id in self.task_registry:
                        task = self.task_registry[task_id]
                        
                        # Recalcular prioridad
                        new_priority = await self.scientific_scoring_engine.calculate_scientific_priority(task)
                        
                        if abs(new_priority - task.dynamic_priority) > 0.05:  # Umbral de cambio
                            task.dynamic_priority = new_priority
                            task.last_priority_update = datetime.now()
                            tasks_updated += 1
                
                # Reordenar cola si hubo cambios significativos
                if tasks_updated > 0:
                    await self._reorder_priority_queue()
                    logger.debug(f"📊 {tasks_updated} prioridades actualizadas")
                
            except BiologyError as e:
                logger.error(f"Error en priority_updater: {str(e)}")
                await asyncio.sleep(10)  # Breve pausa en caso de error
    
    async def _resource_monitor_loop(self):
        """Loop de monitoreo de recursos"""
        
        while self.is_running:
            try:
                await asyncio.sleep(self.config.resource_check_interval_seconds)
                
                # Actualizar utilización de recursos
                await self.resource_monitor.update_utilization()
                
                # Verificar si podemos ejecutar más tareas
                if self._can_start_new_task():
                    await self._trigger_task_evaluation()
                
            except BiologyError as e:
                logger.error(f"Error en resource_monitor_loop: {str(e)}")
                await asyncio.sleep(5)
    
    async def _task_executor(self):
        """Loop principal de ejecución de tareas"""
        
        while self.is_running:
            try:
                await asyncio.sleep(1)  # Check frecuente
                
                # Verificar si podemos ejecutar nuevas tareas
                if (len(self.running_tasks) < self.config.max_concurrent_tasks and 
                    self.priority_queue and 
                    self._can_start_new_task()):
                    
                    # Obtener tarea de mayor prioridad
                    while self.priority_queue:
                        priority_score, timestamp, task_id = heapq.heappop(self.priority_queue)
                        
                        if task_id in self.task_registry:
                            task = self.task_registry[task_id]
                            
                            # Verificar dependencias
                            if await self.dependency_resolver.are_dependencies_ready(task):
                                await self._start_task_execution(task)
                                break
                            else:
                                # Volver a encolar si dependencias no están listas
                                heapq.heappush(self.priority_queue, (priority_score, time.time(), task_id))
                                break
                
            except BiologyError as e:
                logger.error(f"Error en task_executor: {str(e)}")
                await asyncio.sleep(5)
    
    async def _metrics_collector(self):
        """Loop de recolección de métricas"""
        
        while self.is_running:
            try:
                await asyncio.sleep(60)  # Cada minuto
                
                # Calcular métricas actuales
                current_metrics = await self._calculate_current_metrics()
                
                # Guardar en historial
                self.performance_history.append({
                    'timestamp': datetime.now(),
                    'metrics': current_metrics
                })
                
                # Mantener solo últimas 24 horas
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.performance_history = [
                    entry for entry in self.performance_history
                    if entry['timestamp'] > cutoff_time
                ]
                
            except BiologyError as e:
                logger.error(f"Error en metrics_collector: {str(e)}")
                await asyncio.sleep(30)
    
    async def _dependency_resolver_loop(self):
        """Loop de resolución de dependencias"""
        
        while self.is_running:
            try:
                await asyncio.sleep(30)  # Cada 30 segundos
                
                # Verificar tareas bloqueadas por dependencias
                await self.dependency_resolver.check_blocked_tasks(self.task_registry)
                
            except BiologyError as e:
                logger.error(f"Error en dependency_resolver_loop: {str(e)}")
                await asyncio.sleep(10)
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def _validate_task(self, task: ScientificTask) -> ValidateTaskResult:
        """Valida una tarea científica"""
        
        if not task.task_id:
            return {"valid": False, "reason": "task_id es requerido"}
        
        if task.task_id in self.task_registry:
            return {"valid": False, "reason": f"task_id {task.task_id} ya existe"}
        
        if len(self.priority_queue) >= self.config.max_queue_size:
            return {"valid": False, "reason": "Cola llena"}
        
        return {"valid": True, "reason": "Tarea válida"}
    
    async def _predict_execution_time(self, task: ScientificTask) -> Optional[float]:
        """Predice tiempo de ejecución usando ML"""
        
        if 'duration' in self.prediction_models and SKLEARN_AVAILABLE:
            try:
                model = self.prediction_models['duration']
                features = self._extract_task_features(task)
                predicted_duration = model.predict([features])[0]
                return max(1.0, predicted_duration)  # Mínimo 1 minuto
            except BiologyError as e:
                logger.warning(f"Error prediciendo duración: {str(e)}")
        
        return task.estimated_duration_minutes
    
    async def _predict_success_probability(self, task: ScientificTask) -> float:
        """Predice probabilidad de éxito"""
        
        # Factores que influyen en éxito
        base_probability = 0.8
        
        # Ajustar por complejidad
        complexity_factor = 1.0 - (task.estimated_duration_minutes / 1440)  # Normalizar por día
        
        # Ajustar por historial del investigador
        researcher_factor = 0.9  # Placeholder
        
        # Ajustar por reproducibilidad
        reproducibility_factor = task.reproducibility_score
        
        success_prob = base_probability * complexity_factor * researcher_factor * reproducibility_factor
        
        return max(0.1, min(0.95, success_prob))
    
    async def _predict_resource_usage(self, task: ScientificTask) -> Dict[str, float]:
        """Predice uso de recursos"""
        
        # Predicción basada en tipo de tarea y duración
        base_resources = {
            'cpu_percent': 50.0,
            'memory_gb': 4.0,
            'disk_gb': 1.0,
            'gpu_percent': 0.0
        }
        
        # Ajustar por tipo de tarea
        if task.task_type in ['simulation', 'deep_learning']:
            base_resources['cpu_percent'] *= 1.5
            base_resources['memory_gb'] *= 2.0
            base_resources['gpu_percent'] = 70.0
        
        # Ajustar por duración estimada
        duration_factor = min(2.0, task.estimated_duration_minutes / 60)
        base_resources['memory_gb'] *= duration_factor
        
        return base_resources
    
    async def _predict_optimal_start_time(self, task: ScientificTask) -> datetime:
        """Predice momento óptimo para iniciar la tarea"""
        
        # Considerar recursos disponibles y carga del sistema
        now = datetime.now()
        
        # Si urgente, empezar ASAP
        if task.urgency_score > 0.8:
            return now
        
        # Considerar horarios de menor carga (implementación simplificada)
        hour = now.hour
        if 2 <= hour <= 6:  # Horario de menor carga
            return now
        else:
            # Programar para próxima ventana de menor carga
            next_optimal = now.replace(hour=2, minute=0, second=0, microsecond=0)
            if next_optimal <= now:
                next_optimal += timedelta(days=1)
            return next_optimal
    
    async def _predict_wait_time(self, task: ScientificTask) -> float:
        """Predice tiempo de espera en cola"""
        
        if not self.priority_queue:
            return 0.0
        
        # Contar tareas con mayor prioridad
        higher_priority_tasks = sum(
            1 for priority_score, _, _ in self.priority_queue
            if -priority_score > task.dynamic_priority
        )
        
        # Estimar tiempo basado en duración promedio
        avg_duration = 30.0  # Placeholder
        estimated_wait = higher_priority_tasks * avg_duration / self.config.max_concurrent_tasks
        
        return max(0.0, estimated_wait)
    
    async def _predict_scientific_impact(self, task: ScientificTask) -> float:
        """Predice impacto científico"""
        
        # Combinar múltiples factores
        impact_factors = [
            task.impact_potential,
            task.novelty_score,
            task.interdisciplinary_score,
            task.reproducibility_score
        ]
        
        # Score ponderado
        weights = [0.4, 0.3, 0.2, 0.1]
        impact_score = sum(f * w for f, w in zip(impact_factors, weights))
        
        return impact_score
    
    async def _calculate_prediction_confidence(self, task: ScientificTask) -> float:
        """Calcula confianza en las predicciones"""
        
        # Factores que afectan confianza
        historical_data_availability = 0.7  # Placeholder
        task_similarity_to_historical = 0.6  # Placeholder
        researcher_track_record_data = 0.8  # Placeholder
        
        confidence = (
            historical_data_availability * 0.4 +
            task_similarity_to_historical * 0.4 +
            researcher_track_record_data * 0.2
        )
        
        return confidence
    
    def _extract_task_features(self, task: ScientificTask) -> List[float]:
        """Extrae características numéricas de una tarea para ML"""
        
        features = [
            task.estimated_duration_minutes,
            task.novelty_score,
            task.impact_potential,
            task.urgency_score,
            task.reproducibility_score,
            task.interdisciplinary_score,
            len(task.dependencies),
            len(task.collaborators),
            task.execution_attempts,
            1.0 if task.task_type == 'experiment' else 0.0,
            1.0 if task.task_type == 'simulation' else 0.0,
            1.0 if task.task_type == 'analysis' else 0.0
        ]
        
        return features
    
    async def _initialize_prediction_models(self):
        """Inicializa modelos predictivos de ML"""
        
        if not SKLEARN_AVAILABLE:
            logger.warning("Scikit-learn no disponible, usando predicciones heurísticas")
            return
        
        # Placeholder - en implementación real, cargar datos históricos
        logger.info("🤖 Inicializando modelos predictivos")
        
        # Generar datos sintéticos para demostración
        synthetic_data = self._generate_synthetic_training_data()
        
        # Modelo de predicción de duración
        if len(synthetic_data) > 10:
            X = [self._extract_task_features_from_data(record) for record in synthetic_data]
            y_duration = [record['actual_duration'] for record in synthetic_data]
            
            model_duration = RandomForestRegressor(n_estimators=50, random_state=42)
            model_duration.fit(X, y_duration)
            self.prediction_models['duration'] = model_duration
            
            logger.info("✅ Modelo de predicción de duración entrenado")
    
    def _generate_synthetic_training_data(self) -> List[Dict[str, Any]]:
        """Genera datos sintéticos para entrenamiento"""
        
        # Simular datos históricos
        synthetic_data = []
        
        for i in range(100):
            task_data = {
                'estimated_duration': np.random.uniform(10, 300),
                'novelty_score': np.random.random(),
                'impact_potential': np.random.random(),
                'urgency_score': np.random.random(),
                'reproducibility_score': np.random.random(),
                'interdisciplinary_score': np.random.random(),
                'n_dependencies': np.random.randint(0, 5),
                'n_collaborators': np.random.randint(1, 10),
                'task_type': np.random.choice(['experiment', 'simulation', 'analysis'])
            }
            
            # Simular duración actual basada en estimación con ruido
            noise_factor = np.random.uniform(0.8, 1.3)
            task_data['actual_duration'] = task_data['estimated_duration'] * noise_factor
            
            synthetic_data.append(task_data)
        
        return synthetic_data
    
    def _extract_task_features_from_data(self, record: Dict[str, Any]) -> List[float]:
        """Extrae features de un registro de datos"""
        
        return [
            record['estimated_duration'],
            record['novelty_score'],
            record['impact_potential'],
            record['urgency_score'],
            record['reproducibility_score'],
            record['interdisciplinary_score'],
            record['n_dependencies'],
            record['n_collaborators'],
            0,  # execution_attempts
            1.0 if record['task_type'] == 'experiment' else 0.0,
            1.0 if record['task_type'] == 'simulation' else 0.0,
            1.0 if record['task_type'] == 'analysis' else 0.0
        ]
    
    async def _start_task_execution(self, task: ScientificTask):
        """Inicia la ejecución de una tarea"""
        
        try:
            logger.info(f"🚀 Iniciando ejecución de tarea: {task.name}")
            
            # Actualizar estado
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            task.execution_attempts += 1
            
            # Registrar como ejecutándose
            self.running_tasks[task.task_id] = {
                'task': task,
                'started_at': task.started_at,
                'cancelled': False
            }
            
            # Actualizar métricas
            self.metrics.pending_tasks -= 1
            self.metrics.running_tasks += 1
            
            # Simular ejecución asíncrona
            asyncio.create_task(self._simulate_task_execution(task))
            
        except BiologyError as e:
            logger.error(f"Error iniciando tarea {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
    
    async def _simulate_task_execution(self, task: ScientificTask):
        """Simula la ejecución de una tarea (placeholder)"""
        
        try:
            # Simular tiempo de ejecución
            execution_time = task.estimated_duration_minutes * 60  # Convertir a segundos
            await asyncio.sleep(min(execution_time, 10))  # Max 10 segundos para demo
            
            # Verificar si fue cancelada
            if (task.task_id in self.running_tasks and 
                self.running_tasks[task.task_id].get('cancelled', False)):
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.now()
                logger.info(f"❌ Tarea {task.task_id} cancelada durante ejecución")
            else:
                # Simular éxito/fallo
                success = np.random.random() < task.success_probability
                
                if success:
                    task.status = TaskStatus.COMPLETED
                    task.quality_score = np.random.uniform(0.7, 1.0)
                    task.scientific_output = {"result": "success", "data": "simulated_output"}
                    logger.info(f"✅ Tarea {task.task_id} completada exitosamente")
                else:
                    task.status = TaskStatus.FAILED
                    logger.info(f"❌ Tarea {task.task_id} falló")
                
                task.completed_at = datetime.now()
                task.actual_duration = (task.completed_at - task.started_at).total_seconds() / 60
            
            # Mover de running a completed
            if task.task_id in self.running_tasks:
                task_info = self.running_tasks.pop(task.task_id)
                self.completed_tasks[task.task_id] = task_info
            
            # Actualizar métricas
            self.metrics.running_tasks -= 1
            if task.status == TaskStatus.COMPLETED:
                self.metrics.completed_tasks += 1
            else:
                self.metrics.failed_tasks += 1
            
        except BiologyError as e:
            logger.error(f"Error ejecutando tarea {task.task_id}: {str(e)}")
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now()
    
    async def _calculate_current_metrics(self) -> QueueMetrics:
        """Calcula métricas actuales del sistema"""
        
        # Contar estados
        pending = len(self.priority_queue)
        running = len(self.running_tasks)
        completed = len([t for t in self.task_registry.values() if t.status == TaskStatus.COMPLETED])
        failed = len([t for t in self.task_registry.values() if t.status == TaskStatus.FAILED])
        
        # Calcular tiempos promedio
        completed_tasks = [t for t in self.task_registry.values() if t.status == TaskStatus.COMPLETED]
        
        if completed_tasks:
            wait_times = []
            execution_times = []
            
            for task in completed_tasks:
                if task.started_at and task.created_at:
                    wait_time = (task.started_at - task.created_at).total_seconds() / 60
                    wait_times.append(wait_time)
                
                if task.actual_duration:
                    execution_times.append(task.actual_duration)
            
            avg_wait_time = np.mean(wait_times) if wait_times else 0.0
            avg_execution_time = np.mean(execution_times) if execution_times else 0.0
        else:
            avg_wait_time = 0.0
            avg_execution_time = 0.0
        
        # Throughput (tareas por hora)
        hour_ago = datetime.now() - timedelta(hours=1)
        recent_completed = len([
            t for t in completed_tasks 
            if t.completed_at and t.completed_at > hour_ago
        ])
        
        # Utilización de recursos
        resource_util = await self.resource_monitor.get_current_utilization() if hasattr(self, 'resource_monitor') else 0.0
        
        # Score de eficiencia
        efficiency_score = self._calculate_efficiency_score(completed, failed, avg_wait_time)
        
        # Valor científico entregado
        scientific_value = sum(
            task.impact_potential * task.quality_score if task.quality_score else 0
            for task in completed_tasks
        )
        
        return QueueMetrics(
            total_tasks=len(self.task_registry),
            pending_tasks=pending,
            running_tasks=running,
            completed_tasks=completed,
            failed_tasks=failed,
            average_wait_time_minutes=avg_wait_time,
            average_execution_time_minutes=avg_execution_time,
            throughput_tasks_per_hour=recent_completed,
            resource_utilization_percent=resource_util,
            queue_efficiency_score=efficiency_score,
            scientific_value_delivered=scientific_value
        )
    
    def _calculate_efficiency_score(self, completed: int, failed: int, avg_wait_time: float) -> float:
        """Calcula score de eficiencia del sistema"""
        
        if completed + failed == 0:
            return 0.0
        
        # Factores de eficiencia
        success_rate = completed / (completed + failed)
        wait_time_penalty = max(0, 1 - avg_wait_time / 60)  # Penalizar esperas >1 hora
        
        efficiency = success_rate * 0.7 + wait_time_penalty * 0.3
        
        return efficiency
    
    async def _assess_queue_health(self) -> AssessQueueHealthResult:
        """Evalúa la salud general del sistema de colas"""
        
        metrics = await self._calculate_current_metrics()
        
        # Indicadores de salud
        health_indicators = {
            "overall_health": "good",
            "queue_load": "normal",
            "resource_pressure": "low",
            "performance_trend": "stable",
            "recommendations": []
        }
        
        # Evaluar carga de la cola
        queue_load_ratio = metrics.pending_tasks / self.config.max_queue_size
        if queue_load_ratio > 0.8:
            health_indicators["queue_load"] = "high"
            health_indicators["recommendations"].append("Considerar aumentar capacidad de procesamiento")
        
        # Evaluar presión de recursos
        if metrics.resource_utilization_percent > 85:
            health_indicators["resource_pressure"] = "high"
            health_indicators["recommendations"].append("Recursos computacionales bajo presión")
        
        # Evaluar eficiencia
        if metrics.queue_efficiency_score < 0.7:
            health_indicators["overall_health"] = "degraded"
            health_indicators["recommendations"].append("Eficiencia del sistema por debajo del óptimo")
        
        return health_indicators
    
    def _can_start_new_task(self) -> bool:
        """Verifica si se puede iniciar una nueva tarea"""
        
        # Verificar límites de concurrencia
        if len(self.running_tasks) >= self.config.max_concurrent_tasks:
            return False
        
        # Verificar recursos disponibles
        if hasattr(self, 'resource_monitor'):
            current_util = asyncio.create_task(self.resource_monitor.get_current_utilization())
            # En implementación real, verificar recursos específicos
        
        return True
    
    async def _trigger_task_evaluation(self):
        """Dispara evaluación inmediata de tareas"""
        # Este método sería usado para forzar una re-evaluación de la cola
        pass
    
    async def _reorder_task_in_queue(self, task_id: str, new_priority: float):
        """Reordena una tarea específica en la cola"""
        
        # Remover de la cola actual
        self._remove_from_queue(task_id)
        
        # Volver a agregar con nueva prioridad
        priority_score = -new_priority
        heapq.heappush(self.priority_queue, (priority_score, time.time(), task_id))
    
    def _remove_from_queue(self, task_id: str):
        """Remueve una tarea de la cola de prioridad"""
        
        # Marcar como removida (lazy deletion)
        # En implementación más eficiente, usar estructura de datos especializada
        self.priority_queue = [
            (p, t, tid) for p, t, tid in self.priority_queue 
            if tid != task_id
        ]
        heapq.heapify(self.priority_queue)
    
    async def _reorder_priority_queue(self):
        """Reordena completamente la cola de prioridad"""
        
        # Extraer todas las tareas
        tasks_to_requeue = []
        while self.priority_queue:
            _, _, task_id = heapq.heappop(self.priority_queue)
            if task_id in self.task_registry:
                task = self.task_registry[task_id]
                tasks_to_requeue.append(task)
        
        # Volver a agregar con prioridades actualizadas
        for task in tasks_to_requeue:
            priority_score = -task.dynamic_priority
            heapq.heappush(self.priority_queue, (priority_score, time.time(), task.task_id))
    
    async def _get_task_queue_position(self, task_id: str) -> int:
        """Obtiene la posición de una tarea en la cola"""
        
        for i, (_, _, tid) in enumerate(self.priority_queue):
            if tid == task_id:
                return i + 1
        
        return -1  # No encontrada
    
    def _task_summary(self, task: ScientificTask) -> TaskSummaryResult:
        """Crea resumen de una tarea"""
        
        return {
            "task_id": task.task_id,
            "name": task.name,
            "task_type": task.task_type,
            "status": task.status.value,
            "priority": task.dynamic_priority,
            "estimated_duration_minutes": task.estimated_duration_minutes,
            "domain": task.domain,
            "principal_investigator": task.principal_investigator,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }


# ========== CLASES AUXILIARES ==========

class ScientificScoringEngine:
    """Motor de scoring científico para priorización"""
    
    async def calculate_scientific_priority(self, task: ScientificTask) -> float:
        """Calcula prioridad científica basada en múltiples factores"""
        
        # Factores base
        base_score = (
            task.novelty_score * 0.25 +
            task.impact_potential * 0.25 +
            task.urgency_score * 0.20 +
            task.reproducibility_score * 0.15 +
            task.interdisciplinary_score * 0.10
        )
        
        # Ajustes temporales
        temporal_factor = await self._calculate_temporal_factor(task)
        
        # Factor de colaboración
        collaboration_factor = min(1.0, len(task.collaborators) / 5) * 0.05
        
        # Penalización por intentos fallidos
        retry_penalty = max(0, 1 - task.execution_attempts * 0.1)
        
        final_score = (base_score + collaboration_factor) * temporal_factor * retry_penalty
        
        return max(0.0, min(1.0, final_score))
    
    async def _calculate_temporal_factor(self, task: ScientificTask) -> float:
        """Calcula factor temporal para la priorización"""
        
        # Boost para tareas urgentes
        if task.urgency_score > 0.8:
            return 1.2
        
        # Penalización por tareas muy antiguas
        age_hours = (datetime.now() - task.created_at).total_seconds() / 3600
        if age_hours > 168:  # Una semana
            return 0.9
        
        return 1.0


class ResourceMonitor:
    """Monitor de recursos del sistema"""
    
    def __init__(self):
        self.current_utilization = 0.0
        self.history = []
    
    async def get_current_utilization(self) -> float:
        """Obtiene utilización actual de recursos"""
        
        if PSUTIL_AVAILABLE:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            # Promedio ponderado
            utilization = cpu_percent * 0.6 + memory_percent * 0.4
            self.current_utilization = utilization
            
            return utilization
        else:
            # Simulación
            return np.random.uniform(20, 70)
    
    async def update_utilization(self):
        """Actualiza métricas de utilización"""
        
        current = await self.get_current_utilization()
        
        self.history.append({
            'timestamp': datetime.now(),
            'utilization': current
        })
        
        # Mantener solo última hora
        cutoff = datetime.now() - timedelta(hours=1)
        self.history = [h for h in self.history if h['timestamp'] > cutoff]


class DependencyResolver:
    """Resolvedor de dependencias entre tareas"""
    
    async def check_dependencies(self, task: ScientificTask) -> CheckDependenciesResult:
        """Verifica estado de dependencias de una tarea"""
        
        if not task.dependencies:
            return {"ready": True, "blocking_dependencies": []}
        
        # En implementación real, verificar estado de tareas dependientes
        blocking_deps = []
        
        # Simulación
        for dep_id in task.dependencies:
            # Simular verificación de dependencia
            if np.random.random() < 0.8:  # 80% probabilidad de estar lista
                continue
            else:
                blocking_deps.append(dep_id)
        
        return {
            "ready": len(blocking_deps) == 0,
            "blocking_dependencies": blocking_deps,
            "total_dependencies": len(task.dependencies)
        }
    
    async def are_dependencies_ready(self, task: ScientificTask) -> bool:
        """Verifica si todas las dependencias están listas"""
        
        status = await self.check_dependencies(task)
        return status["ready"]
    
    async def check_blocked_tasks(self, task_registry: Dict[str, ScientificTask]):
        """Verifica tareas bloqueadas por dependencias"""
        
        # En implementación real, verificar y desbloquear tareas
        blocked_count = 0
        
        for task in task_registry.values():
            if task.status == TaskStatus.PENDING and task.dependencies:
                if not await self.are_dependencies_ready(task):
                    blocked_count += 1
        
        if blocked_count > 0:
            logger.debug(f"📊 {blocked_count} tareas bloqueadas por dependencias")


# Instancia global del servicio
dynamic_priority_queue_service = DynamicPriorityQueueService()
