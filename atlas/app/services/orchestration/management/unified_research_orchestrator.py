"""
Unified Research Orchestrator Service
Extracts the core orchestration interface to reduce duplication between:
- workflow_orchestration.py
- scientific_copilot.py  
- research_cycle_manager.py

This service acts as a single point of coordination for scientific research workflows,
consolidating orchestration responsibilities and providing a clean interface.

Author: AXIOM Development Team
Date: September 14, 2025
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger, log_decision_event
from app.middleware.trace_id_middleware import get_current_trace_id
from app.monitoring.metrics import inc, phase_activity
from app.exceptions.base import (
    AtlasDomainError,
    AtlasExternalError,
    AtlasValidationError,
    AtlasInfrastructureError,
)
from app.exceptions.domain.biology import BiologyError
from app.types.unified_research_orchestrator_types import (
    GetPerformanceMetricsResult,
    ProcessRequestResult,
)



class ResearchPhase(Enum):
    """Unified research phases across all orchestration services"""
    INITIALIZATION = "initialization"
    HYPOTHESIS_GENERATION = "hypothesis_generation"
    LITERATURE_REVIEW = "literature_review"
    EXPERIMENTAL_DESIGN = "experimental_design"
    EXECUTION = "execution"
    ANALYSIS = "analysis"
    VALIDATION = "validation" 
    REFINEMENT = "refinement"
    COMPLETION = "completion"


class OrchestrationStrategy(Enum):
    """Different orchestration strategies available"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    ADAPTIVE = "adaptive"
    AUTONOMOUS = "autonomous"


@dataclass
class OrchestrationTask:
    """Unified task representation for orchestration"""
    task_id: str
    task_type: str
    service_name: str
    operation: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    timeout_sec: int = 300
    retry_count: int = 0
    max_retries: int = 3
    phase: Optional[ResearchPhase] = None
    priority: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass  
class OrchestrationResult:
    """Unified result representation"""
    task_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time_sec: float = 0.0
    phase: Optional[ResearchPhase] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class OrchestrationEngine(ABC):
    """Abstract base class for orchestration engines"""
    
    @abstractmethod
    async def execute_task(self, task: OrchestrationTask) -> OrchestrationResult:
        """Execute a single task"""
        pass
    
    @abstractmethod
    async def execute_workflow(
        self, 
        tasks: List[OrchestrationTask],
        strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL
    ) -> List[OrchestrationResult]:
        """Execute a workflow composed of multiple tasks"""
        pass
    
    @abstractmethod
    def validate_task(self, task: OrchestrationTask) -> bool:
        """Validate task configuration"""
        pass


class UnifiedResearchOrchestrator(BaseService, OrchestrationEngine):
    """
    Unified orchestration service that consolidates orchestration logic
    from workflow_orchestration, scientific_copilot, and research_cycle_manager.
    
    This service acts as the single source of truth for research workflow 
    orchestration patterns, reducing duplication and providing a clean interface.
    """
    
    def __init__(self):
        super().__init__("UnifiedResearchOrchestrator")
        
        # Service registry for delegation
        self._service_registry: Dict[str, Any] = {}
        self._active_workflows: Dict[str, Dict[str, Any]] = {}
        self._execution_history: List[OrchestrationResult] = []
        
        # Configuration
        self.max_concurrent_tasks = 10
        self.default_timeout = 300
        self.enable_metrics = True
        
        # Performance tracking
        self._task_execution_times: Dict[str, List[float]] = {}
        self._success_rates: Dict[str, List[bool]] = {}
        
        logger.info("✅ UnifiedResearchOrchestrator initialized")
    
    def register_service(self, service_name: str, service_instance: Any) -> None:
        """Register a service implementation for delegation"""
        self._service_registry[service_name] = service_instance
        logger.info(f"📋 Registered service: {service_name}")
    
    def validate_task(self, task: OrchestrationTask) -> bool:
        """Validate task configuration"""
        try:
            # Basic validation
            if not task.task_id or not task.service_name or not task.operation:
                return False
            
            # Check if required service is registered
            if task.service_name not in self._service_registry:
                logger.warning(f"Service not registered: {task.service_name}")
                return False
            
            # Validate parameters
            if not isinstance(task.parameters, dict):
                return False
            
            # Validate dependencies are strings
            if not all(isinstance(dep, str) for dep in task.dependencies):
                return False
            
            return True
        except (TypeError, AttributeError, ValueError) as e:
            logger.error(f"Task validation error: {e}")
            return False
    
    async def execute_task(self, task: OrchestrationTask) -> OrchestrationResult:
        """Execute a single orchestration task with full observability"""
        start_time = datetime.now()
        trace_id = get_current_trace_id()
        
        # Log decision event for task execution
        log_decision_event(
            event_type="task_execution_started",
            phase=task.phase.value if task.phase else "unknown",
            details={
                "task_id": task.task_id,
                "service_name": task.service_name,
                "operation": task.operation,
                "timeout_sec": task.timeout_sec
            },
            outcome="initiated",
            trace_id=trace_id
        )
        
        try:
            # Validate task before execution
            if not self.validate_task(task):
                raise ValueError(f"Task validation failed: {task.task_id}")
            
            # Get service instance
            service = self._service_registry.get(task.service_name)
            if not service:
                raise RuntimeError(f"Service not available: {task.service_name}")
            
            # Start phase activity tracking
            phase_name = task.phase.value if task.phase else task.operation
            with phase_activity(phase_name, task.metadata.get("domain", "unknown")):
                
                # Execute with timeout
                try:
                    if hasattr(service, 'process_request'):
                        # Standard service interface
                        request_data = {
                            "action": task.operation,
                            **task.parameters
                        }
                        result = await asyncio.wait_for(
                            service.process_request(request_data),
                            timeout=task.timeout_sec
                        )
                    else:
                        # Direct method call
                        method = getattr(service, task.operation, None)
                        if not method:
                            raise AttributeError(f"Method {task.operation} not found on {task.service_name}")
                        
                        result = await asyncio.wait_for(
                            method(**task.parameters),
                            timeout=task.timeout_sec
                        )
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    # Track performance metrics
                    if self.enable_metrics:
                        self._update_performance_metrics(task, execution_time, True)
                        inc("atlas_orchestrator_task_success_total")
                        inc("atlas_orchestrator_task_total")
                    
                    # Create success result
                    orchestration_result = OrchestrationResult(
                        task_id=task.task_id,
                        success=True,
                        result=result,
                        execution_time_sec=execution_time,
                        phase=task.phase,
                        metadata={
                            "service_name": task.service_name,
                            "operation": task.operation,
                            "trace_id": trace_id
                        }
                    )
                    
                    # Log successful completion
                    log_decision_event(
                        event_type="task_execution_completed",
                        phase=task.phase.value if task.phase else "unknown",
                        details={
                            "task_id": task.task_id,
                            "execution_time_sec": execution_time,
                            "success": True
                        },
                        outcome="success",
                        trace_id=trace_id
                    )
                    
                    return orchestration_result
                
                except asyncio.TimeoutError:
                    raise RuntimeError(f"Task {task.task_id} timed out after {task.timeout_sec}s")
        
        except AtlasDomainError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            if self.enable_metrics:
                self._update_performance_metrics(task, execution_time, False)
                inc("atlas_orchestrator_task_failure_total")
                inc("atlas_orchestrator_task_total")
            log_decision_event(
                event_type="task_execution_failed",
                phase=task.phase.value if task.phase else "unknown",
                details={
                    "task_id": task.task_id,
                    "error": str(e),
                    "execution_time_sec": execution_time
                },
                outcome="failed",
                trace_id=trace_id
            )
            logger.error(f"❌ Task execution failed {task.task_id}: {e}")
            return OrchestrationResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                execution_time_sec=execution_time,
                phase=task.phase,
                metadata={
                    "service_name": task.service_name,
                    "operation": task.operation,
                    "trace_id": trace_id
                }
            )
        except AtlasExternalError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            if self.enable_metrics:
                self._update_performance_metrics(task, execution_time, False)
                inc("atlas_orchestrator_task_failure_total")
                inc("atlas_orchestrator_task_total")
            log_decision_event(
                event_type="task_execution_failed",
                phase=task.phase.value if task.phase else "unknown",
                details={
                    "task_id": task.task_id,
                    "error": str(e),
                    "execution_time_sec": execution_time
                },
                outcome="failed",
                trace_id=trace_id
            )
            logger.error(f"❌ Task execution failed {task.task_id}: {e}")
            return OrchestrationResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                execution_time_sec=execution_time,
                phase=task.phase,
                metadata={
                    "service_name": task.service_name,
                    "operation": task.operation,
                    "trace_id": trace_id
                }
            )
        except AtlasValidationError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            if self.enable_metrics:
                self._update_performance_metrics(task, execution_time, False)
                inc("atlas_orchestrator_task_failure_total")
                inc("atlas_orchestrator_task_total")
            log_decision_event(
                event_type="task_execution_failed",
                phase=task.phase.value if task.phase else "unknown",
                details={
                    "task_id": task.task_id,
                    "error": str(e),
                    "execution_time_sec": execution_time
                },
                outcome="failed",
                trace_id=trace_id
            )
            logger.error(f"❌ Task execution failed {task.task_id}: {e}")
            return OrchestrationResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                execution_time_sec=execution_time,
                phase=task.phase,
                metadata={
                    "service_name": task.service_name,
                    "operation": task.operation,
                    "trace_id": trace_id
                }
            )
        except (ValueError, RuntimeError, AttributeError) as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            if self.enable_metrics:
                self._update_performance_metrics(task, execution_time, False)
                inc("atlas_orchestrator_task_failure_total")
                inc("atlas_orchestrator_task_total")
            log_decision_event(
                event_type="task_execution_failed",
                phase=task.phase.value if task.phase else "unknown",
                details={
                    "task_id": task.task_id,
                    "error": str(e),
                    "execution_time_sec": execution_time
                },
                outcome="failed",
                trace_id=trace_id
            )
            logger.error(f"❌ Task execution failed {task.task_id}: {e}")
            return OrchestrationResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                execution_time_sec=execution_time,
                phase=task.phase,
                metadata={
                    "service_name": task.service_name,
                    "operation": task.operation,
                    "trace_id": trace_id
                }
            )
        except BiologyError as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            # Track failure metrics
            if self.enable_metrics:
                self._update_performance_metrics(task, execution_time, False)
                inc("atlas_orchestrator_task_failure_total")
                inc("atlas_orchestrator_task_total")
            
            # Log failure
            log_decision_event(
                event_type="task_execution_failed",
                phase=task.phase.value if task.phase else "unknown",
                details={
                    "task_id": task.task_id,
                    "error": str(e),
                    "execution_time_sec": execution_time
                },
                outcome="failed",
                trace_id=trace_id
            )
            
            logger.error(f"❌ Task execution failed {task.task_id}: {e}")
            
            return OrchestrationResult(
                task_id=task.task_id,
                success=False,
                error=str(e),
                execution_time_sec=execution_time,
                phase=task.phase,
                metadata={
                    "service_name": task.service_name,
                    "operation": task.operation,
                    "trace_id": trace_id
                }
            )
    
    async def execute_workflow(
        self, 
        tasks: List[OrchestrationTask],
        strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL
    ) -> List[OrchestrationResult]:
        """Execute a complete workflow using specified strategy"""
        workflow_id = str(uuid.uuid4())
        start_time = datetime.now()
        trace_id = get_current_trace_id()
        
        # Register workflow
        self._active_workflows[workflow_id] = {
            "start_time": start_time,
            "strategy": strategy,
            "task_count": len(tasks),
            "trace_id": trace_id
        }
        
        logger.info(f"🚀 Starting workflow {workflow_id} with {len(tasks)} tasks using {strategy.value} strategy")
        
        try:
            if strategy == OrchestrationStrategy.SEQUENTIAL:
                return await self._execute_sequential(tasks)
            elif strategy == OrchestrationStrategy.PARALLEL:
                return await self._execute_parallel(tasks)
            elif strategy == OrchestrationStrategy.ADAPTIVE:
                return await self._execute_adaptive(tasks)
            else:
                raise ValueError(f"Unsupported orchestration strategy: {strategy}")
        
        except BiologyError as e:
            logger.error(f"❌ Workflow {workflow_id} failed: {e}")
            raise
        
        finally:
            # Clean up workflow registry
            self._active_workflows.pop(workflow_id, None)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Workflow {workflow_id} completed in {execution_time:.2f}s")
    
    async def _execute_sequential(self, tasks: List[OrchestrationTask]) -> List[OrchestrationResult]:
        """Execute tasks sequentially with dependency resolution"""
        results: Dict[str, OrchestrationResult] = {}
        task_map = {task.task_id: task for task in tasks}
        
        # Topological sort for dependency resolution
        execution_order = self._resolve_dependencies(tasks)
        
        for task_id in execution_order:
            task = task_map[task_id]
            
            # Check if dependencies succeeded
            failed_dependencies = []
            for dep_id in task.dependencies:
                if dep_id in results and not results[dep_id].success:
                    failed_dependencies.append(dep_id)
            
            if failed_dependencies:
                # Skip task due to failed dependencies
                results[task_id] = OrchestrationResult(
                    task_id=task_id,
                    success=False,
                    error=f"Dependencies failed: {failed_dependencies}",
                    phase=task.phase
                )
                continue
            
            # Execute task
            result = await self.execute_task(task)
            results[task_id] = result
            
            # Store result for history
            self._execution_history.append(result)
        
        return [results[task.task_id] for task in tasks]
    
    async def _execute_parallel(self, tasks: List[OrchestrationTask]) -> List[OrchestrationResult]:
        """Execute independent tasks in parallel"""
        # Group tasks by dependency levels
        dependency_groups = self._group_by_dependencies(tasks)
        all_results: Dict[str, OrchestrationResult] = {}
        
        for group in dependency_groups:
            # Execute current group in parallel
            group_tasks = [task for task in tasks if task.task_id in group]
            
            if len(group_tasks) == 1:
                # Single task
                result = await self.execute_task(group_tasks[0])
                all_results[group_tasks[0].task_id] = result
                self._execution_history.append(result)
            else:
                # Multiple tasks in parallel
                async_tasks = [self.execute_task(task) for task in group_tasks]
                group_results = await asyncio.gather(*async_tasks, return_exceptions=True)
                
                for task, task_result in zip(group_tasks, group_results):
                    if isinstance(task_result, Exception):
                        orchestration_result = OrchestrationResult(
                            task_id=task.task_id,
                            success=False,
                            error=str(task_result),
                            phase=task.phase
                        )
                    else:
                        orchestration_result = task_result
                    
                    all_results[task.task_id] = orchestration_result
                    self._execution_history.append(orchestration_result)
        
        return [all_results[task.task_id] for task in tasks]
    
    async def _execute_adaptive(self, tasks: List[OrchestrationTask]) -> List[OrchestrationResult]:
        """Execute tasks with adaptive strategy based on performance metrics"""
        # Start with parallel for independent tasks, fall back to sequential for complex dependencies
        if self._has_complex_dependencies(tasks):
            logger.info("🔄 Using sequential strategy due to complex dependencies")
            return await self._execute_sequential(tasks)
        else:
            logger.info("⚡ Using parallel strategy for independent tasks")
            return await self._execute_parallel(tasks)
    
    def _resolve_dependencies(self, tasks: List[OrchestrationTask]) -> List[str]:
        """Topological sort for dependency resolution"""
        in_degree = {task.task_id: 0 for task in tasks}
        
        # Calculate in-degrees
        for task in tasks:
            for dep in task.dependencies:
                if dep in in_degree:
                    in_degree[task.task_id] += 1
        
        # Kahn's algorithm for topological sorting
        queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Reduce in-degree for dependent tasks
            for other_task in tasks:
                if current in other_task.dependencies:
                    in_degree[other_task.task_id] -= 1
                    if in_degree[other_task.task_id] == 0:
                        queue.append(other_task.task_id)
        
        return result
    
    def _group_by_dependencies(self, tasks: List[OrchestrationTask]) -> List[List[str]]:
        """Group tasks by dependency levels for parallel execution"""
        levels: List[List[str]] = []
        processed = set()
        
        while len(processed) < len(tasks):
            current_level = []
            
            for task in tasks:
                if task.task_id in processed:
                    continue
                
                # Check if all dependencies are processed
                deps_satisfied = all(dep in processed for dep in task.dependencies)
                
                if deps_satisfied:
                    current_level.append(task.task_id)
            
            if not current_level:
                # Circular dependency or other issue
                remaining = [task.task_id for task in tasks if task.task_id not in processed]
                logger.warning(f"Unable to resolve dependencies for tasks: {remaining}")
                current_level = remaining
            
            levels.append(current_level)
            processed.update(current_level)
        
        return levels
    
    def _has_complex_dependencies(self, tasks: List[OrchestrationTask]) -> bool:
        """Check if tasks have complex dependency patterns"""
        total_deps = sum(len(task.dependencies) for task in tasks)
        return total_deps > len(tasks) * 0.5  # More than 50% dependency ratio
    
    def _update_performance_metrics(self, task: OrchestrationTask, execution_time: float, success: bool):
        """Update performance tracking metrics"""
        task_key = f"{task.service_name}.{task.operation}"
        
        if task_key not in self._task_execution_times:
            self._task_execution_times[task_key] = []
            self._success_rates[task_key] = []
        
        self._task_execution_times[task_key].append(execution_time)
        self._success_rates[task_key].append(success)
        
        # Keep only last 100 entries for each task type
        if len(self._task_execution_times[task_key]) > 100:
            self._task_execution_times[task_key] = self._task_execution_times[task_key][-100:]
            self._success_rates[task_key] = self._success_rates[task_key][-100:]
    
    def get_performance_metrics(self) -> GetPerformanceMetricsResult:
        """Get orchestration performance metrics"""
        metrics = {
            "total_tasks_executed": len(self._execution_history),
            "active_workflows": len(self._active_workflows),
            "registered_services": list(self._service_registry.keys()),
            "task_performance": {}
        }
        
        for task_key in self._task_execution_times:
            times = self._task_execution_times[task_key]
            successes = self._success_rates[task_key]
            
            metrics["task_performance"][task_key] = {
                "avg_execution_time": sum(times) / len(times) if times else 0,
                "success_rate": sum(successes) / len(successes) if successes else 0,
                "total_executions": len(times)
            }
        
        return metrics
    
    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process orchestration requests"""
        try:
            action = request_data.get("action", "")
            
            if action == "execute_task":
                task_data = request_data.get("task", {})
                task = OrchestrationTask(
                    task_id=task_data.get("task_id", str(uuid.uuid4())),
                    task_type=task_data.get("task_type", "general"),
                    service_name=task_data.get("service_name", ""),
                    operation=task_data.get("operation", ""),
                    parameters=task_data.get("parameters", {}),
                    dependencies=task_data.get("dependencies", []),
                    timeout_sec=task_data.get("timeout_sec", self.default_timeout),
                    phase=ResearchPhase(task_data["phase"]) if "phase" in task_data else None
                )
                
                result = await self.execute_task(task)
                return {"success": result.success, "result": result.result, "error": result.error}
            
            elif action == "execute_workflow":
                tasks_data = request_data.get("tasks", [])
                strategy = OrchestrationStrategy(request_data.get("strategy", "sequential"))
                
                tasks = []
                for task_data in tasks_data:
                    task = OrchestrationTask(
                        task_id=task_data.get("task_id", str(uuid.uuid4())),
                        task_type=task_data.get("task_type", "general"),
                        service_name=task_data.get("service_name", ""),
                        operation=task_data.get("operation", ""),
                        parameters=task_data.get("parameters", {}),
                        dependencies=task_data.get("dependencies", []),
                        timeout_sec=task_data.get("timeout_sec", self.default_timeout),
                        phase=ResearchPhase(task_data["phase"]) if "phase" in task_data else None
                    )
                    tasks.append(task)
                
                results = await self.execute_workflow(tasks, strategy)
                return {
                    "success": True,
                    "results": [{"task_id": r.task_id, "success": r.success, "result": r.result, "error": r.error} for r in results]
                }
            
            elif action == "get_performance_metrics":
                return {"success": True, "metrics": self.get_performance_metrics()}
            
            elif action == "register_service":
                service_name = request_data.get("service_name", "")
                # This would need actual service instance, for now just acknowledge
                return {"success": True, "message": f"Service registration acknowledged: {service_name}"}
            
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": ["execute_task", "execute_workflow", "get_performance_metrics", "register_service"]
                }
        
        except BiologyError as e:
            return self.handle_error(e, "process_request")


# Global singleton for easy access
_unified_orchestrator = None


def get_unified_orchestrator() -> UnifiedResearchOrchestrator:
    """Get the global unified orchestrator instance"""
    global _unified_orchestrator
    if _unified_orchestrator is None:
        _unified_orchestrator = UnifiedResearchOrchestrator()
    return _unified_orchestrator
