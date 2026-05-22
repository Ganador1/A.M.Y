"""
Pipeline Execution Module for Master Orchestration Service
Lógica de ejecución de pipelines y tasks con manejo de errores robusto
"""

import asyncio
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
from app.services.orchestration.models import (
    ResearchPipeline, PipelineTask, PipelineStatus, OrchestrationMetrics
)
from app.exceptions import AtlasInfrastructureError

logger = logging.getLogger(__name__)


class PipelineExecutor:
    """Ejecutor de pipelines con manejo robusto de errores"""

    def __init__(self, service_registry: Dict[str, Any], metrics: OrchestrationMetrics):
        self.service_registry = service_registry
        self.metrics = metrics

    async def execute_pipeline(self, pipeline: ResearchPipeline) -> bool:
        """
        Execute pipeline tasks with robust error handling
        """
        try:
            pipeline.status = PipelineStatus.RUNNING
            pipeline.started_at = datetime.now()

            logger.info(f"Starting pipeline execution: {pipeline.id}")

            # Execute tasks in topological order
            executed_tasks = set()

            while len(executed_tasks) < len(pipeline.tasks):
                # Find tasks ready to execute
                ready_tasks = []
                for task in pipeline.tasks:
                    if (task.id not in executed_tasks and
                        all(dep in executed_tasks for dep in task.dependencies)):
                        ready_tasks.append(task)

                if not ready_tasks:
                    logger.error(f"Pipeline {pipeline.id} has circular dependencies or is stuck")
                    pipeline.status = PipelineStatus.FAILED
                    break

                # Execute ready tasks concurrently
                task_futures = []
                for task in ready_tasks:
                    future = asyncio.create_task(self._execute_task(task, pipeline))
                    task_futures.append((task, future))

                # Wait for tasks to complete
                for task, future in task_futures:
                    try:
                        await future
                        executed_tasks.add(task.id)
                    except Exception as e:
                        logger.error(f"Task {task.id} failed: {e}")
                        task.status = PipelineStatus.FAILED
                        task.error = str(e)
                        executed_tasks.add(task.id)  # Mark as processed even if failed

            # Calculate pipeline completion
            successful_tasks = sum(1 for task in pipeline.tasks if task.status == PipelineStatus.COMPLETED)
            pipeline.success_rate = successful_tasks / len(pipeline.tasks)

            if pipeline.success_rate > 0.5:  # At least 50% success
                pipeline.status = PipelineStatus.COMPLETED
            else:
                pipeline.status = PipelineStatus.FAILED

            pipeline.completed_at = datetime.now()
            pipeline.total_execution_time = (pipeline.completed_at - pipeline.started_at).total_seconds()

            # Update metrics
            self.metrics.pipelines_executed += 1
            self.metrics.total_execution_time += pipeline.total_execution_time
            self.metrics.success_rate = (
                (self.metrics.success_rate * (self.metrics.pipelines_executed - 1) + pipeline.success_rate) /
                self.metrics.pipelines_executed
            )

            logger.info(f"Pipeline {pipeline.id} completed with {pipeline.success_rate:.2%} success rate")
            return pipeline.status == PipelineStatus.COMPLETED

        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            pipeline.status = PipelineStatus.FAILED
            pipeline.completed_at = datetime.now()
            if pipeline.started_at:
                pipeline.total_execution_time = (pipeline.completed_at - pipeline.started_at).total_seconds()
            return False

    async def _execute_task(self, task: PipelineTask, pipeline: ResearchPipeline) -> bool:
        """
        Execute individual task with robust error handling and retry logic
        """
        task.status = PipelineStatus.RUNNING
        task.start_time = datetime.now()

        # Resolve parameter references
        resolved_params = self._resolve_parameter_references(task.parameters, pipeline)

        # Validate resolved parameters
        self._validate_task_parameters(resolved_params, task)

        for attempt in range(task.max_retries + 1):
            try:
                # Get service
                service = self.service_registry.get(task.service)
                if not service:
                    raise AtlasInfrastructureError(
                        f"Service {task.service} not available",
                        details={"service": task.service}
                    )

                # Execute method with timeout
                method = getattr(service, task.method)

                # Add exponential backoff for retries
                if attempt > 0:
                    backoff_time = min(2 ** attempt, 30)  # Exponential backoff with max 30s
                    logger.info(f"Retrying task {task.id}, attempt {attempt + 1}/{task.max_retries + 1}, waiting {backoff_time}s")
                    await asyncio.sleep(backoff_time)

                result = await asyncio.wait_for(
                    method(**resolved_params),
                    timeout=task.timeout
                )

                task.result = result
                task.status = PipelineStatus.COMPLETED
                task.retry_count = attempt

                # Update metrics
                # Track execution time (aggregate in metrics)
                self.metrics.tasks_completed += 1

                logger.info(f"Task {task.id} completed successfully on attempt {attempt + 1}")
                return True

            except asyncio.TimeoutError:
                task.error = f"Task timed out after {task.timeout} seconds (attempt {attempt + 1})"
                task.retry_count = attempt

                if attempt == task.max_retries:
                    task.status = PipelineStatus.FAILED
                    logger.error(f"Task {task.id} timed out after {task.max_retries + 1} attempts")
                else:
                    logger.warning(f"Task {task.id} timed out on attempt {attempt + 1}, will retry")
                continue

            except (AttributeError, KeyError, ValueError, RuntimeError, ImportError) as e:
                task.error = f"{type(e).__name__}: {str(e)} (attempt {attempt + 1})"
                task.retry_count = attempt

                if attempt == task.max_retries:
                    task.status = PipelineStatus.FAILED
                    logger.error(f"Task {task.id} failed after {task.max_retries + 1} attempts: {e}")
                else:
                    logger.warning(f"Task {task.id} failed on attempt {attempt + 1}: {e}, will retry")

                # Don't retry on certain errors
                if isinstance(e, (AttributeError, ImportError)):
                    task.status = PipelineStatus.FAILED
                    logger.error(f"Task {task.id} failed with non-retryable error: {e}")
                    break
                continue

            except Exception as e:
                task.error = f"Unexpected error: {str(e)} (attempt {attempt + 1})"
                task.retry_count = attempt

                if attempt == task.max_retries:
                    task.status = PipelineStatus.FAILED
                    logger.error(f"Task {task.id} failed with unexpected error after {task.max_retries + 1} attempts: {e}")
                else:
                    logger.warning(f"Task {task.id} failed with unexpected error on attempt {attempt + 1}: {e}, will retry")
                continue

        # Task failed all retries
        return False

    def _resolve_parameter_references(self, parameters: Dict[str, Any], pipeline: ResearchPipeline) -> Dict[str, Any]:
        """Resolve parameter references to previous task results with advanced path traversal"""
        resolved = {}

        def resolve_value(value):
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # This is a reference to another task's result
                ref_path = value[2:-1]  # Remove ${ and }

                if '.' in ref_path:
                    task_id, result_path = ref_path.split('.', 1)

                    # Find the referenced task
                    task_result = None
                    for task in pipeline.tasks:
                        if task.id == task_id and task.result:
                            task_result = task.result
                            break

                    if task_result:
                        # Advanced path traversal using dot notation
                        try:
                            current_value = task_result
                            for path_part in result_path.split('.'):
                                if isinstance(current_value, dict) and path_part in current_value:
                                    current_value = current_value[path_part]
                                elif isinstance(current_value, list):
                                    try:
                                        index = int(path_part)
                                        if 0 <= index < len(current_value):
                                            current_value = current_value[index]
                                        else:
                                            return None
                                    except (ValueError, IndexError):
                                        return None
                                else:
                                    return None
                            return current_value
                        except (KeyError, TypeError, IndexError):
                            logger.warning(f"Could not resolve reference path: {ref_path}")
                            return None
                    else:
                        return None
                else:
                    # Simple task reference without path
                    for task in pipeline.tasks:
                        if task.id == ref_path and task.result:
                            return task.result
                    return None
            elif isinstance(value, dict):
                # Recursively resolve nested dictionaries
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                # Recursively resolve lists
                return [resolve_value(item) for item in value]
            else:
                return value

        for key, value in parameters.items():
            resolved[key] = resolve_value(value)

        return resolved

    def _validate_task_parameters(self, parameters: Dict[str, Any], task: PipelineTask):
        """
        Validate task parameters before execution
        """
        if not parameters:
            return

        # Get service method signature
        service = self.service_registry.get(task.service)
        if not service:
            return

        try:
            method = getattr(service, task.method)
            import inspect
            sig = inspect.signature(method)

            # Check for required parameters
            for param_name, param in sig.parameters.items():
                if param.default == inspect.Parameter.empty and param_name not in parameters:
                    logger.warning(f"Task {task.id} missing required parameter '{param_name}' for {task.service}.{task.method}")

            # Check for extra parameters
            for param_name in parameters.keys():
                if param_name not in sig.parameters:
                    logger.warning(f"Task {task.id} has extra parameter '{param_name}' not in {task.service}.{task.method} signature")

        except (AttributeError, TypeError):
            # Method might not be inspectable (e.g., async methods, wrapped methods)
            pass

    def calculate_pipeline_progress(self, pipeline: ResearchPipeline) -> float:
        """Calculate pipeline completion progress"""
        if not pipeline.tasks:
            return 0.0

        completed_tasks = sum(1 for task in pipeline.tasks if task.status == PipelineStatus.COMPLETED)
        return completed_tasks / len(pipeline.tasks)

    def task_to_dict(self, task: PipelineTask) -> Dict[str, Any]:
        """Convert task to dictionary"""
        return {
            'id': task.id,
            'name': task.name,
            'service': task.service,
            'method': task.method,
            'status': task.status.value,
            'priority': task.priority.value,
            'execution_time': task.execution_time,
            'error': task.error,
            'dependencies': task.dependencies
        }
