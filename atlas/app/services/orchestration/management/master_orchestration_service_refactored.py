"""
Refactored Master Orchestration Service for AXIOM
Usando arquitectura modular para mejor mantenibilidad
"""

import logging
import os as _os
import asyncio
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from app.exceptions import AtlasInfrastructureError

from app.services.base_service import BaseService
from app.services.orchestration.models import (
    ResearchPipeline, PipelineStatus, OrchestrationMetrics
)
from app.exceptions.domain.biology import BiologyError

from app.services.orchestration.templates import TEMPLATE_REGISTRY
from app.services.orchestration.execution import PipelineExecutor
from app.services.orchestration.monitoring import ServiceHealthMonitor, ResourceMonitor
from app.services.orchestration.management import ServiceManager, CircuitBreakerManager
from app.config import settings


def _should_skip_autoinit() -> bool:
    """Return True when auto initialization must be skipped."""
    env_flag = str(_os.getenv("AXIOM_SKIP_AUTOINIT", "0")).lower()
    settings_flag = str(getattr(settings, "AXIOM_SKIP_AUTOINIT", env_flag)).lower()
    return settings_flag in {"1", "true", "yes"}


_AUTO_INIT_DISABLED = _should_skip_autoinit()

logger = logging.getLogger(__name__)


class MasterOrchestrationService(BaseService):
    """
    Servicio maestro de orquestación refactorizado
    Ahora usa arquitectura modular para mejor mantenibilidad y escalabilidad
    """

    def __init__(self, config: Optional[Dict] = None):
        super().__init__("MasterOrchestration")

        # Configuration
        self.config = config or {}
        self.max_concurrent_pipelines = self.config.get('max_concurrent_pipelines', 5)
        self.max_concurrent_tasks = self.config.get('max_concurrent_tasks', 10)

        # Resource limits
        self.resource_limits = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'api_calls_per_minute': 1000
        }

        # Circuit breaker configuration
        self.failure_thresholds = {
            'service_failures': 5,
            'timeout_failures': 3,
            'resource_failures': 2
        }

        # Initialize modular components
        self.metrics = OrchestrationMetrics()

        # Service management
        self.service_manager = ServiceManager()
        self.circuit_breaker_manager = CircuitBreakerManager(self.failure_thresholds)

        # Pipeline management
        self.active_pipelines: Dict[str, ResearchPipeline] = {}
        # Historia debe ser lista, previo uso como dict causaba SyntaxError al intentar tratarlo como iterable de objetos
        self.pipeline_history: List[ResearchPipeline] = []
        self.task_queue = asyncio.Queue()

        # Background tasks
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_tasks)
        self.background_tasks_started = False

        # Initialize services
        self._initialize_services()

    def _initialize_services(self):
        """Initialize and register available services"""
        services_available = self.service_manager.initialize_services(self.config)

        if not services_available:
            logger.warning("Running in mock mode - no services initialized")

    async def start_background_tasks(self):
        """Start background tasks manually (for testing)"""
        if not self.background_tasks_started:
            self._start_background_tasks()
            self.background_tasks_started = True

    def _start_background_tasks(self):
        """Start background monitoring and execution tasks"""
        # Start health monitoring
        health_monitor = ServiceHealthMonitor(self.failure_thresholds)
        asyncio.create_task(health_monitor.monitor_service_health(
            self.service_manager.get_all_services()
        ))

        # Start resource monitoring
        resource_monitor = ResourceMonitor(self.metrics)
        asyncio.create_task(resource_monitor.monitor_resources())

        # Start task processor
        asyncio.create_task(self._process_task_queue())

    async def _process_task_queue(self):
        """Process background task queue."""
        while True:
            try:
                await asyncio.sleep(1)
            except (asyncio.CancelledError, RuntimeError) as exc:
                logger.error("Task queue processing error: %s", exc)
                break

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process orchestration requests - required by BaseService abstract method
        """
        try:
            request_type = request_data.get('type', '')

            if request_type == 'create_pipeline':
                # Create autonomous pipeline
                research_question = request_data.get('research_question', '')
                domain = request_data.get('domain', 'general')
                template = request_data.get('template', 'comprehensive_research')
                custom_parameters = request_data.get('custom_parameters', {})

                pipeline_id = await self.create_autonomous_pipeline(
                    research_question, domain, template, custom_parameters
                )

                return {
                    'success': True,
                    'pipeline_id': pipeline_id,
                    'message': f'Pipeline {pipeline_id} created successfully'
                }

            elif request_type == 'get_status':
                # Get pipeline status
                pipeline_id = request_data.get('pipeline_id')
                if not pipeline_id:
                    raise ValueError("Pipeline ID required for status request")

                status = await self.get_pipeline_status(pipeline_id)
                return {
                    'success': True,
                    'status': status
                }

            elif request_type == 'get_service_info':
                # Get service information
                info = self.get_service_info()
                return {
                    'success': True,
                    'service_info': info
                }

            elif request_type == 'control_pipeline':
                # Control pipeline operations
                pipeline_id = request_data.get('pipeline_id')
                action = request_data.get('action')

                if not pipeline_id or not action:
                    raise ValueError("Pipeline ID and action required")

                if action == 'pause':
                    result = await self.pause_pipeline(pipeline_id)
                    return {
                        'success': result,
                        'message': f'Pipeline {pipeline_id} paused' if result else f'Cannot pause pipeline {pipeline_id}'
                    }
                elif action == 'resume':
                    result = await self.resume_pipeline(pipeline_id)
                    return {
                        'success': result,
                        'message': f'Pipeline {pipeline_id} resumed' if result else f'Cannot resume pipeline {pipeline_id}'
                    }
                elif action == 'cancel':
                    result = await self.cancel_pipeline(pipeline_id)
                    return {
                        'success': result,
                        'message': f'Pipeline {pipeline_id} cancelled' if result else f'Cannot cancel pipeline {pipeline_id}'
                    }
                else:
                    raise ValueError(f"Unknown action: {action}")

            else:
                raise ValueError(f"Unknown request type: {request_type}")

        except BiologyError as e:
            logger.error(f"Process request failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Request processing failed: {e}'
            }

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about orchestration capabilities"""
        return {
            "registered_services": list(self.service_manager.services.keys()),
            "workflow_templates": list(TEMPLATE_REGISTRY.keys()),
            "active_pipelines": len(self.active_pipelines),
            "max_concurrent_pipelines": self.max_concurrent_pipelines,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "features": [
                "Modular architecture",
                "Autonomous pipeline execution",
                "Multi-service orchestration",
                "Circuit breaker pattern",
                "Resource monitoring",
                "Workflow templates",
                "Real-time health monitoring"
            ],
            "metrics": {
                'pipelines_executed': self.metrics.pipelines_executed,
                'tasks_completed': self.metrics.tasks_completed,
                'total_execution_time': self.metrics.total_execution_time,
                'success_rate': self.metrics.success_rate,
                'cpu_usage': self.metrics.cpu_usage,
                'memory_usage': self.metrics.memory_usage,
                'active_pipelines': self.metrics.active_pipelines
            },
            "service_health": self.service_manager.service_health,
            "circuit_breakers": self.circuit_breaker_manager.get_circuit_status()
        }

    async def create_autonomous_pipeline(self,
                                       research_question: str,
                                       domain: str = 'general',
                                       template: str = 'comprehensive_research',
                                       custom_parameters: Optional[Dict] = None) -> str:
        """
        Crear un pipeline autónomo de investigación
        """

        # Validate inputs
        if not research_question.strip():
            raise ValueError("Research question cannot be empty")

        if template not in TEMPLATE_REGISTRY:
            raise ValueError(f"Template {template} not available")

        # Check resource limits
        if len(self.active_pipelines) >= self.max_concurrent_pipelines:
            raise AtlasInfrastructureError(
                "Maximum concurrent pipelines reached",
                details={"max_concurrent": self.max_concurrent_pipelines}
            )

        # Generate pipeline ID
        pipeline_id = str(uuid.uuid4())

        # Create pipeline from template
        pipeline = await self._create_pipeline_from_template(
            pipeline_id, research_question, domain, template, custom_parameters
        )

        # Register pipeline
        self.active_pipelines[pipeline_id] = pipeline

        # Start execution using the modular executor
        executor = PipelineExecutor(
            self.service_manager.services,
            self.metrics
        )
        asyncio.create_task(executor.execute_pipeline(pipeline))

        logger.info(f"Created autonomous pipeline {pipeline_id} for: {research_question}")

        return pipeline_id

    async def _create_pipeline_from_template(self,
                                           pipeline_id: str,
                                           research_question: str,
                                           domain: str,
                                           template: str,
                                           custom_parameters: Optional[Dict]) -> ResearchPipeline:
        """Create pipeline from workflow template"""

        template_func = TEMPLATE_REGISTRY[template]
        tasks = template_func(research_question, domain, custom_parameters or {})

        pipeline = ResearchPipeline(
            id=pipeline_id,
            name=f"{template}_{domain}",
            description=f"Autonomous research pipeline for: {research_question}",
            domain=domain,
            tasks=tasks,
            status=PipelineStatus.PENDING,
            created_at=datetime.now(),
            metadata={
                'research_question': research_question,
                'template': template,
                'custom_parameters': custom_parameters
            }
        )

        return pipeline

    async def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get status of a specific pipeline"""

        # Check active pipelines
        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
        else:
            # Check history
            pipeline = None
            for p in self.pipeline_history:
                if p.id == pipeline_id:
                    pipeline = p
                    break

        if not pipeline:
            raise ValueError(f"Pipeline {pipeline_id} not found")

        executor = PipelineExecutor(self.service_manager.services, self.metrics)
        return {
            'id': pipeline.id,
            'name': pipeline.name,
            'status': pipeline.status.value,
            'progress': executor.calculate_pipeline_progress(pipeline),
            'tasks': [executor.task_to_dict(task) for task in pipeline.tasks],
            'execution_time': pipeline.total_execution_time,
            'success_rate': pipeline.success_rate,
            'created_at': pipeline.created_at.isoformat(),
            'started_at': pipeline.started_at.isoformat() if pipeline.started_at else None,
            'completed_at': pipeline.completed_at.isoformat() if pipeline.completed_at else None
        }

    async def pause_pipeline(self, pipeline_id: str) -> bool:
        """Pause a running pipeline"""
        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
            if pipeline.status == PipelineStatus.RUNNING:
                pipeline.status = PipelineStatus.PAUSED
                logger.info(f"Pipeline {pipeline_id} paused")
                return True
        return False

    async def resume_pipeline(self, pipeline_id: str) -> bool:
        """Resume a paused pipeline"""
        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
            if pipeline.status == PipelineStatus.PAUSED:
                pipeline.status = PipelineStatus.RUNNING
                # Restart execution
                executor = PipelineExecutor(self.service_manager.services, self.metrics)
                asyncio.create_task(executor.execute_pipeline(pipeline))
                logger.info(f"Pipeline {pipeline_id} resumed")
                return True
        return False

    async def cancel_pipeline(self, pipeline_id: str) -> bool:
        """Cancel a pipeline"""
        if pipeline_id in self.active_pipelines:
            pipeline = self.active_pipelines[pipeline_id]
            pipeline.status = PipelineStatus.CANCELLED
            pipeline.completed_at = datetime.now()
            if pipeline.started_at:
                pipeline.total_execution_time = (pipeline.completed_at - pipeline.started_at).total_seconds()

            # Move to history
            # Guardar en historial (lista simple)
            self.pipeline_history.append(pipeline)
            del self.active_pipelines[pipeline_id]

            logger.info(f"Pipeline {pipeline_id} cancelled")
            return True
        return False

# --- Module level guarded singleton pattern ---
_refactored_master_orchestration_service: Optional[MasterOrchestrationService] = None

def get_refactored_master_orchestration_service() -> Optional[MasterOrchestrationService]:
    """Lazy accessor to avoid heavy initialization during guarded imports."""
    global _refactored_master_orchestration_service
    if _refactored_master_orchestration_service is None and not _AUTO_INIT_DISABLED:
        try:
            _refactored_master_orchestration_service = MasterOrchestrationService()
        except BiologyError as e:  # pragma: no cover - defensive
            logger.error(f"Failed to auto-instantiate MasterOrchestrationService: {e}")
            _refactored_master_orchestration_service = None
    return _refactored_master_orchestration_service

# Perform auto init only if guard not set
if not _AUTO_INIT_DISABLED:
    get_refactored_master_orchestration_service()
