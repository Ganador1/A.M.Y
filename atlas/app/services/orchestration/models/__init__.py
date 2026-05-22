"""
Models for Master Orchestration Service
Data classes and enums for pipeline management
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


class PipelineStatus(Enum):
    """Estados de pipeline"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Prioridades de tareas"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PipelineTask:
    """Tarea individual en un pipeline"""
    id: str
    name: str
    service: str
    method: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    priority: TaskPriority
    timeout: int
    retry_count: int
    max_retries: int
    status: PipelineStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    execution_time: Optional[float] = None


@dataclass
class ResearchPipeline:
    """Pipeline de investigación completo"""
    id: str
    name: str
    description: str
    domain: str
    tasks: List[PipelineTask]
    status: PipelineStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_execution_time: Optional[float] = None
    success_rate: float = 0.0
    resource_usage: Dict[str, Any] = None
    metadata: Dict[str, Any] = None


@dataclass
class ServiceHealth:
    """Estado de salud de un servicio"""
    service_name: str
    status: str  # 'healthy', 'degraded', 'circuit_open'
    last_check: datetime
    failure_count: int
    response_time: float
    consecutive_failures: int = 0


@dataclass
class OrchestrationMetrics:
    """Métricas de orquestación"""
    pipelines_executed: int = 0
    tasks_completed: int = 0
    total_execution_time: float = 0.0
    success_rate: float = 0.0
    resource_usage_history: List[Dict[str, Any]] = None
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_pipelines: int = 0

    def __post_init__(self):
        if self.resource_usage_history is None:
            self.resource_usage_history = []
