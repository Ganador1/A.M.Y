"""
Workflow Orchestration Service for AXIOM
Connects scientific services to create interdisciplinary workflows
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
import asyncio
import uuid
from dataclasses import dataclass, field
from enum import Enum

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger
from app.core.cache import cache, cache_key
from app.core.config import settings
from app.models.workflow_persistence_models import WorkflowRecord, WorkflowStepRecord, StepExecutionRecord
from app.core.database import get_db_session
from app.services.experiment_tracking import ExperimentTrackingService
from app.exceptions import AtlasInfrastructureError
from app.exceptions.base import (
    AtlasDomainError,
    AtlasExternalError,
    AtlasValidationError,
)
from app.exceptions.domain.biology import BiologyError
from app.types.workflow_orchestration_types import (
    ArithAdapterResult,
    CalcAdapterResult,
    EquationsAdapterResult,
    StatsAdapterResult,
    GraphAdapterResult,
    GeometryAdapterResult,
    ProcessRequestResult,
    CreateWorkflowResult,
    ExecuteWorkflowResult,
    ExecuteStepResult,
    ResolveParametersResult,
    GetWorkflowStatusResult,
    ListWorkflowsResult,
    GetWorkflowTemplatesResult,
    GetWorkflowGraphResult,
    GetWorkflowProvenanceResult,
)



class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ServiceType(Enum):
    """Available scientific service types"""
    COMPUTATIONAL_CHEMISTRY = "computational_chemistry"
    QUANTUM_PHYSICS = "quantum_physics"
    QUANTUM_COMPUTING = "quantum_computing"
    PDE = "pde"
    OPTIMIZATION = "optimization"
    SCIENTIFIC_AI = "scientific_ai"
    ARITHMETIC = "arithmetic"
    CALCULUS = "calculus"
    EQUATIONS = "equations"
    STATISTICS = "statistics"
    GRAPHING = "graphing"
    GEOMETRY = "geometry"


@dataclass
class WorkflowStep:
    """Individual step in a workflow"""
    step_id: str
    service_type: ServiceType
    operation: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_sec: Optional[int] = None
    max_retries: int = 0


@dataclass
class Workflow:
    """Complete workflow definition"""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowOrchestratorService(BaseService):
    """
    Service for orchestrating complex scientific workflows
    Connects multiple scientific services to solve interdisciplinary problems
    """

    def __init__(self):
        super().__init__("WorkflowOrchestrator")
        self.active_workflows: Dict[str, Workflow] = {}
        self.service_registry: Dict[ServiceType, Callable] = {}
        self.workflow_templates: Dict[str, Dict[str, Any]] = {}
        self.experiment_tracking = ExperimentTrackingService()

        # Initialize service registry
        self._initialize_service_registry()

        # Initialize workflow templates
        self._initialize_workflow_templates()

        logger.info("✅ WorkflowOrchestratorService initialized")

    def _initialize_service_registry(self):
        """Initialize the service registry with available scientific services"""
        # Import services dynamically to avoid circular imports
        try:
            from app.services.computational_chemistry import ComputationalChemistryService
            self.service_registry[ServiceType.COMPUTATIONAL_CHEMISTRY] = ComputationalChemistryService().process_request
        except ImportError:
            logger.warning("⚠️ ComputationalChemistryService not available")

        try:
            from app.domains.physics.services.quantum_physics import QuantumPhysicsService
            self.service_registry[ServiceType.QUANTUM_PHYSICS] = QuantumPhysicsService().process_request
        except ImportError:
            logger.warning("⚠️ QuantumPhysicsService not available")

        try:
            from app.domains.physics.services.quantum_computing import QuantumComputingService
            self.service_registry[ServiceType.QUANTUM_COMPUTING] = QuantumComputingService().process_request
        except ImportError:
            logger.warning("⚠️ QuantumComputingService not available")

        try:
            from app.services.pde_service import PDEService
            self.service_registry[ServiceType.PDE] = PDEService().process_request
        except ImportError:
            logger.warning("⚠️ PDEService not available")

        try:
            from app.domains.mathematics.services.optimization_service import OptimizationService
            self.service_registry[ServiceType.OPTIMIZATION] = OptimizationService().process_request
        except ImportError:
            logger.warning("⚠️ OptimizationService not available")

        try:
            from app.services.scientific_ai import ScientificAIService
            self.service_registry[ServiceType.SCIENTIFIC_AI] = ScientificAIService().process_request
        except ImportError:
            logger.warning("⚠️ ScientificAIService not available")

        # Core math services (guarded) via lightweight async adapters
        try:
            from app.domains.mathematics.services.arithmetic_service import ArithmeticService
            from app.models import ArithmeticRequest

            async def _arith_adapter(req: ArithAdapterResult) -> ArithAdapterResult:
                def _call_sync():
                    res = ArithmeticService.calculate(ArithmeticRequest(
                        operation=req.get("operation") or "add",
                        operands=req.get("operands", []) or [0.0, 0.0],
                    ))
                    return {"success": True, "result": res.model_dump()}

                return await asyncio.to_thread(_call_sync)

            self.service_registry[ServiceType.ARITHMETIC] = _arith_adapter
        except BiologyError:
            logger.warning("⚠️ ArithmeticService not available")

        try:
            from app.domains.mathematics.services.calculus_service import CalculusService
            from app.models.advanced_models import CalculusRequest as AdvCalculusRequest

            async def _calc_adapter(req: CalcAdapterResult) -> CalcAdapterResult:
                def _call_sync():
                    payload = AdvCalculusRequest(
                        expression=req.get("expression") or "x",
                        operation=req.get("operation") or "derivative",
                        variable=req.get("variable", "x"),
                        order=req.get("order"),
                        limits=req.get("limits"),
                    )
                    res = CalculusService.calculate(payload)
                    return {"success": True, "result": res.model_dump()}

                return await asyncio.to_thread(_call_sync)

            self.service_registry[ServiceType.CALCULUS] = _calc_adapter
        except BiologyError:
            logger.warning("⚠️ CalculusService not available")

        try:
            from app.domains.mathematics.services.equation_service import EquationService
            from app.models import EquationRequest

            async def _equations_adapter(req: EquationsAdapterResult) -> EquationsAdapterResult:
                def _call_sync():
                    # System of equations path
                    if "equations" in req and "variables" in req:
                        result = EquationService.solve_system(req.get("equations", []), req.get("variables", []))
                        return {"success": True, "result": result}
                    # Single equation
                    payload = EquationRequest(equation=req.get("equation", ""), variable=req.get("variable", "x"))
                    res = EquationService.solve_equation(payload)
                    return {"success": True, "result": res.model_dump()}

                return await asyncio.to_thread(_call_sync)

            self.service_registry[ServiceType.EQUATIONS] = _equations_adapter
        except BiologyError:
            logger.warning("⚠️ EquationService not available")

        try:
            from app.domains.mathematics.services.statistics_service import StatisticsService
            from app.models import StatisticsRequest

            async def _stats_adapter(req: StatsAdapterResult) -> StatsAdapterResult:
                def _call_sync():
                    payload = StatisticsRequest(data=req.get("data", []), operations=req.get("operations"))
                    res = StatisticsService.calculate(payload)
                    # StatisticsResponse is a Pydantic model; convert to dict
                    return {"success": True, "result": res.model_dump()}

                return await asyncio.to_thread(_call_sync)

            self.service_registry[ServiceType.STATISTICS] = _stats_adapter
        except BiologyError:
            logger.warning("⚠️ StatisticsService not available")

        try:
            from app.domains.mathematics.services.graphing_service import GraphingService
            from app.models.models import GraphingRequest as ModelsGraphingRequest

            async def _graph_adapter(req: GraphAdapterResult) -> GraphAdapterResult:
                def _call_sync():
                    # Default to single-graph generation
                    if req.get("operation") == "generate_multiple_graphs":
                        result = GraphingService.generate_multiple_graphs(
                            expressions=req.get("expressions", []),
                            x_min=req.get("x_min", -10),
                            x_max=req.get("x_max", 10),
                            points=req.get("points", 1000),
                            variable=req.get("variable", "x"),
                        )
                        return {"success": True, "result": result}

                    payload = ModelsGraphingRequest(
                        expression=req.get("expression", "x**2"),
                        x_min=req.get("x_min", -10),
                        x_max=req.get("x_max", 10),
                        points=req.get("points", 500),
                        variable=req.get("variable", "x"),
                        title=req.get("title"),
                    )
                    res = GraphingService.generate_graph(payload)
                    return {"success": True, "result": res.model_dump()}

                return await asyncio.to_thread(_call_sync)

            self.service_registry[ServiceType.GRAPHING] = _graph_adapter
        except BiologyError:
            logger.warning("⚠️ GraphingService not available")

        try:
            from app.services.analytical_geometry import AnalyticalGeometryService
            from app.models import GeometryRequest

            async def _geometry_adapter(req: GeometryAdapterResult) -> GeometryAdapterResult:
                def _call_sync():
                    payload = GeometryRequest(
                        shape=req.get("shape", "circle"),
                        parameters=req.get("parameters", {}),
                        operation=req.get("operation", "area"),
                    )
                    res = AnalyticalGeometryService.process_geometry(payload)
                    return {"success": True, "result": res.model_dump()}

                return await asyncio.to_thread(_call_sync)

            self.service_registry[ServiceType.GEOMETRY] = _geometry_adapter
        except BiologyError:
            logger.warning("⚠️ AnalyticalGeometryService not available")

    def _initialize_workflow_templates(self):
        """Initialize predefined workflow templates"""
        self.workflow_templates = {
            "heat_sink_design": {
                "name": "Heat Sink Design Optimization",
                "description": "Multi-scale workflow for optimizing heat sink design",
                "steps": [
                    {
                        "service_type": ServiceType.COMPUTATIONAL_CHEMISTRY,
                        "operation": "analyze_molecule",
                        "parameters": {"smiles": "{{material}}"},
                        "description": "Analyze thermal properties at molecular level"
                    },
                    {
                        "service_type": ServiceType.PDE,
                        "operation": "solve_heat_equation",
                        "parameters": {
                            "geometry": "{{geometry}}",
                            "boundary_conditions": "{{thermal_bc}}"
                        },
                        "description": "Solve heat transfer PDE for macroscale behavior",
                        "dependencies": ["step_0"]
                    },
                    {
                        "service_type": ServiceType.OPTIMIZATION,
                        "operation": "optimize_design",
                        "parameters": {
                            "objective": "minimize_temperature",
                            "constraints": "{{design_constraints}}",
                            "variables": "{{design_variables}}"
                        },
                        "description": "Optimize final design parameters",
                        "dependencies": ["step_1"]
                    }
                ]
            },
            "drug_discovery": {
                "name": "Drug Discovery Pipeline",
                "description": "Integrated workflow for drug candidate identification",
                "steps": [
                    {
                        "service_type": ServiceType.COMPUTATIONAL_CHEMISTRY,
                        "operation": "molecular_docking",
                        "parameters": {"ligand": "{{ligand}}", "receptor": "{{receptor}}"},
                        "description": "Perform molecular docking simulation"
                    },
                    {
                        "service_type": ServiceType.QUANTUM_COMPUTING,
                        "operation": "quantum_chemistry",
                        "parameters": {"molecule": "{{ligand}}", "method": "vqe"},
                        "description": "Quantum chemistry analysis for binding energies",
                        "dependencies": ["step_0"]
                    },
                    {
                        "service_type": ServiceType.SCIENTIFIC_AI,
                        "operation": "predict_properties",
                        "parameters": {"molecule": "{{ligand}}", "properties": ["solubility", "toxicity"]},
                        "description": "AI prediction of pharmacological properties",
                        "dependencies": ["step_1"]
                    }
                ]
            }
        }

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Process workflow orchestration requests"""
        try:
            action = request_data.get("action", "")

            if action == "create_workflow":
                return await self.create_workflow(request_data)
            elif action == "execute_workflow":
                return await self.execute_workflow(request_data)
            elif action == "get_workflow_status":
                return self.get_workflow_status(request_data)
            elif action == "list_workflows":
                return self.list_workflows()
            elif action == "get_workflow_templates":
                return self.get_workflow_templates()
            elif action == "get_workflow_graph":
                wf_id = request_data.get("workflow_id")
                if not isinstance(wf_id, str) or not wf_id:
                    return {"success": False, "error": "workflow_id is required"}
                return self.get_workflow_graph(wf_id)
            elif action == "get_workflow_provenance":
                wf_id = request_data.get("workflow_id")
                if not isinstance(wf_id, str) or not wf_id:
                    return {"success": False, "error": "workflow_id is required"}
                return self.get_workflow_provenance(wf_id)
            else:
                return {
                    "success": False,
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "create_workflow", "execute_workflow", "get_workflow_status",
                        "list_workflows", "get_workflow_templates", "get_workflow_graph",
                        "get_workflow_provenance"
                    ]
                }

        except AtlasDomainError as e:
            return self.handle_error(e, "process_request")
        except AtlasExternalError as e:
            return self.handle_error(e, "process_request")
        except AtlasValidationError as e:
            return self.handle_error(e, "process_request")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "process_request")

    async def create_workflow(self, request_data: CreateWorkflowResult) -> CreateWorkflowResult:
        """Create a new workflow from template or custom definition"""
        try:
            workflow_id = str(uuid.uuid4())
            name = request_data.get("name", f"Workflow_{workflow_id[:8]}")
            description = request_data.get("description", "")

            # Check if using template
            template_name = request_data.get("template")
            if template_name and template_name in self.workflow_templates:
                template = self.workflow_templates[template_name]
                steps_data = template["steps"]
                if not description:
                    description = template["description"]
            else:
                steps_data = request_data.get("steps", [])

            # Create workflow steps
            steps = []
            for i, step_data in enumerate(steps_data):
                step = WorkflowStep(
                    step_id=f"step_{i}",
                    service_type=ServiceType(step_data["service_type"]),
                    operation=step_data["operation"],
                    parameters=step_data["parameters"],
                    dependencies=step_data.get("dependencies", []),
                    timeout_sec=step_data.get("timeout", step_data.get("timeout_sec")),
                    max_retries=int(step_data.get("max_retries", 0) or 0),
                )
                steps.append(step)

            workflow = Workflow(
                workflow_id=workflow_id,
                name=name,
                description=description,
                steps=steps,
                metadata=request_data.get("metadata", {})
            )

            self.active_workflows[workflow_id] = workflow

            # Persist to DB (best-effort)
            self._persist_workflow(workflow)

            logger.info(f"✅ Created workflow: {workflow_id} - {name}")

            return {
                "success": True,
                "message": f"Workflow '{name}' created successfully",
                "workflow_id": workflow_id,
                "steps_count": len(steps)
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "create_workflow")
        except AtlasExternalError as e:
            return self.handle_error(e, "create_workflow")
        except AtlasValidationError as e:
            return self.handle_error(e, "create_workflow")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "create_workflow")

    async def execute_workflow(self, request_data: ExecuteWorkflowResult) -> ExecuteWorkflowResult:
        """Execute a workflow asynchronously"""
        try:
            workflow_id = request_data.get("workflow_id")
            if not workflow_id or workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }

            workflow = self.active_workflows[workflow_id]

            # Start execution in background
            asyncio.create_task(self._execute_workflow_async(workflow))

            logger.info(f"🚀 Started execution of workflow: {workflow_id}")

            return {
                "success": True,
                "message": "Workflow execution started",
                "workflow_id": workflow_id
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "execute_workflow")
        except AtlasExternalError as e:
            return self.handle_error(e, "execute_workflow")
        except AtlasValidationError as e:
            return self.handle_error(e, "execute_workflow")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "execute_workflow")

    async def _execute_workflow_async(self, workflow: Workflow):
        """Execute workflow steps asynchronously"""
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()

            # Persist status
            self._update_workflow_status(workflow)

            logger.info(f"🔄 Executing workflow: {workflow.workflow_id}")

            # Start an MLflow experiment/run to track workflow-level provenance (best-effort)
            # Enriquecer parámetros con una vista compacta del DAG para Provenance
            wf_params = {"workflow_id": workflow.workflow_id, "steps": len(workflow.steps)}
            try:
                wf_params["workflow_steps"] = [
                    {"id": s.step_id, "name": s.operation, "after": (s.dependencies[0] if s.dependencies else None)}
                    for s in workflow.steps
                ]
            except BiologyError:
                pass

            exp_resp = await self.experiment_tracking.process_request({
                "action": "start_experiment",
                "name": f"workflow_{workflow.name}",
                "description": workflow.description,
                "parameters": wf_params,
                "tags": {"type": "workflow", "orchestrator": "v1.1"}
            })
            if exp_resp.get("success"):
                workflow.metadata["mlflow_run_id"] = exp_resp.get("run_id")
                workflow.metadata["mlflow_experiment_id"] = exp_resp.get("mlflow_experiment_id")
                self._update_workflow_metadata(workflow)

            # Execute steps in dependency order
            completed_steps = set()
            step_results = {}

            while len(completed_steps) < len(workflow.steps):
                # Find steps ready to execute
                ready_steps = []
                for step in workflow.steps:
                    if step.step_id not in completed_steps:
                        deps_satisfied = all(dep in completed_steps for dep in step.dependencies)
                        if deps_satisfied:
                            ready_steps.append(step)

                if not ready_steps:
                    workflow.status = WorkflowStatus.FAILED
                    workflow.completed_at = datetime.now()
                    self._update_workflow_status(workflow)
                    logger.error(f"❌ Workflow {workflow.workflow_id} failed: No steps ready to execute")
                    break

                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(self._execute_step(workflow.workflow_id, step, step_results))
                    tasks.append((step.step_id, task))

                # Wait for all steps to complete
                for step_id, task in tasks:
                    try:
                        result = await task
                        step_results[step_id] = result
                        completed_steps.add(step_id)
                        self._update_step_status(workflow.workflow_id, step_id, WorkflowStatus.COMPLETED, step=next(s for s in workflow.steps if s.step_id==step_id))
                        logger.info(f"✅ Completed step: {step_id}")
                    except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
                        logger.error(f"❌ Step {step_id} failed: {e}")
                        workflow.status = WorkflowStatus.FAILED
                        workflow.completed_at = datetime.now()
                        self._update_step_status(workflow.workflow_id, step_id, WorkflowStatus.FAILED)
                        self._update_workflow_status(workflow)
                        break

            if workflow.status != WorkflowStatus.FAILED:
                # All steps completed successfully
                workflow.status = WorkflowStatus.COMPLETED
                workflow.completed_at = datetime.now()
                workflow.results = step_results
                self._update_workflow_status(workflow)
                logger.info(f"✅ Workflow {workflow.workflow_id} completed successfully")

            # End experiment tracking (best-effort)
            if workflow.metadata.get("mlflow_run_id"):
                await self.experiment_tracking.process_request({
                    "action": "end_experiment",
                    "experiment_id": next((eid for eid, e in self.experiment_tracking.active_experiments.items() if e.run_id == workflow.metadata.get("mlflow_run_id")), None) or "",
                    "status": "completed" if workflow.status == WorkflowStatus.COMPLETED else "failed"
                })

        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
            self._update_workflow_status(workflow)
            logger.error(f"❌ Workflow {workflow.workflow_id} execution failed: {e}")
            if workflow.metadata.get("mlflow_run_id"):
                try:
                    await self.experiment_tracking.process_request({
                        "action": "end_experiment",
                        "experiment_id": next((eid for eid, e in self.experiment_tracking.active_experiments.items() if e.run_id == workflow.metadata.get("mlflow_run_id")), None) or "",
                        "status": "failed"
                    })
                except BiologyError:
                    pass

    async def _execute_step(self, workflow_id: str, step: WorkflowStep, previous_results: ExecuteStepResult) -> ExecuteStepResult:
        """Execute a single workflow step"""
        try:
            step.status = WorkflowStatus.RUNNING
            step.started_at = datetime.now()

            # Get service function
            service_func = self.service_registry.get(step.service_type)
            if not service_func:
                raise AtlasInfrastructureError(
                    "Service unavailable",
                    context={
                        "service_type": step.service_type.value,
                        "operation": step.operation,
                        "workflow_id": workflow_id,
                    },
                )

            # Prepare parameters (resolve template variables)
            parameters = self._resolve_parameters(step.parameters, previous_results)

            # Cache key based on service + operation + parameters
            key = cache_key(
                "wf_step",
                service=step.service_type.value,
                operation=step.operation,
                params=parameters,
            )

            cached_result = cache.get(key)
            if cached_result is not None:
                step.result = cached_result
                step.status = WorkflowStatus.COMPLETED
                step.execution_time = 0.0
                step.completed_at = datetime.now()
                # Record execution as cache hit
                self._record_step_execution(workflow_id=workflow_id, step_id=step.step_id, attempt=1, status="completed", cache_hit=True, timeout=step.timeout_sec)
                logger.info(f"🟩 Cache hit for step {step.step_id} ({step.operation})")
                return cached_result

            # Execute service with retries/timeouts
            start_time = datetime.now()
            attempt = 0
            last_exc: Optional[Exception] = None
            timeout = step.timeout_sec or settings.max_computation_time
            max_retries = max(0, step.max_retries)

            while attempt <= max_retries:
                attempt += 1
                try:
                    # Run with timeout
                    result = await asyncio.wait_for(
                        service_func({"operation": step.operation, **parameters}),
                        timeout=timeout
                    )
                    end_time = datetime.now()
                    step.status = WorkflowStatus.COMPLETED
                    step.result = result
                    step.execution_time = (end_time - start_time).total_seconds()
                    step.completed_at = end_time

                    # Cache only successful results
                    cache.set(key, result, ttl=settings.cache_ttl)
                    self._record_step_execution(workflow_id=workflow_id, step_id=step.step_id, attempt=attempt, status="completed", cache_hit=False, timeout=timeout, duration=step.execution_time)
                    return result
                except asyncio.TimeoutError as te:
                    last_exc = te
                    logger.warning(f"⏱️ Step {step.step_id} timed out at {timeout}s (attempt {attempt}/{max_retries+1})")
                    self._record_step_execution(workflow_id=workflow_id, step_id=step.step_id, attempt=attempt, status="timeout", cache_hit=False, timeout=timeout)
                except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
                    last_exc = e
                    logger.warning(f"🔁 Step {step.step_id} failed attempt {attempt}/{max_retries+1}: {e}")
                    self._record_step_execution(workflow_id=workflow_id, step_id=step.step_id, attempt=attempt, status="failed", cache_hit=False, timeout=timeout)

            # If we get here, all attempts failed
            step.status = WorkflowStatus.FAILED
            step.error = str(last_exc) if last_exc else "Unknown error"
            step.completed_at = datetime.now()
            raise last_exc or AtlasInfrastructureError("Step failed without exception")

        except (AtlasDomainError, AtlasExternalError, AtlasValidationError, AtlasInfrastructureError) as e:
            step.status = WorkflowStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.now()
            raise e

    def _resolve_parameters(self, parameters: ResolveParametersResult, previous_results: ResolveParametersResult) -> ResolveParametersResult:
        """Resolve template variables in parameters using previous step results"""
        resolved = {}

        for key, value in parameters.items():
            if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
                # Template variable
                var_path = value[2:-2].strip()
                resolved_value = self._get_nested_value(previous_results, var_path)
                resolved[key] = resolved_value
            else:
                resolved[key] = value

        return resolved

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get nested value from dictionary using dot notation"""
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None

        return current

    def get_workflow_status(self, request_data: GetWorkflowStatusResult) -> GetWorkflowStatusResult:
        """Get status of a workflow"""
        try:
            workflow_id = request_data.get("workflow_id")
            if not workflow_id or workflow_id not in self.active_workflows:
                return {
                    "success": False,
                    "error": f"Workflow {workflow_id} not found"
                }

            workflow = self.active_workflows[workflow_id]

            steps_status = []
            for step in workflow.steps:
                steps_status.append({
                    "step_id": step.step_id,
                    "service_type": step.service_type.value,
                    "operation": step.operation,
                    "status": step.status.value,
                    "execution_time": step.execution_time,
                    "error": step.error
                })

            return {
                "success": True,
                "workflow_id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "steps": steps_status,
                "results": workflow.results,
                "cache_stats": cache.get_stats(),
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "get_workflow_status")
        except AtlasExternalError as e:
            return self.handle_error(e, "get_workflow_status")
        except AtlasValidationError as e:
            return self.handle_error(e, "get_workflow_status")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "get_workflow_status")

    def list_workflows(self) -> ListWorkflowsResult:
        """List all active workflows"""
        try:
            workflows = []
            for workflow_id, workflow in self.active_workflows.items():
                workflows.append({
                    "workflow_id": workflow_id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "status": workflow.status.value,
                    "created_at": workflow.created_at.isoformat(),
                    "steps_count": len(workflow.steps)
                })

            return {
                "success": True,
                "workflows": workflows,
                "total_count": len(workflows)
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "list_workflows")
        except AtlasExternalError as e:
            return self.handle_error(e, "list_workflows")
        except AtlasValidationError as e:
            return self.handle_error(e, "list_workflows")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "list_workflows")

    def get_workflow_templates(self) -> GetWorkflowTemplatesResult:
        """Get available workflow templates"""
        try:
            templates = []
            for template_name, template in self.workflow_templates.items():
                templates.append({
                    "template_name": template_name,
                    "name": template["name"],
                    "description": template["description"],
                    "steps_count": len(template["steps"])
                })

            return {
                "success": True,
                "templates": templates,
                "total_count": len(templates)
            }

        except AtlasDomainError as e:
            return self.handle_error(e, "get_workflow_templates")
        except AtlasExternalError as e:
            return self.handle_error(e, "get_workflow_templates")
        except AtlasValidationError as e:
            return self.handle_error(e, "get_workflow_templates")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "get_workflow_templates")

    # --- New: Workflow graph view ---
    def get_workflow_graph(self, workflow_id: Optional[str]) -> GetWorkflowGraphResult:
        try:
            if not workflow_id or workflow_id not in self.active_workflows:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}

            wf = self.active_workflows[workflow_id]
            nodes = []
            edges = []
            for s in wf.steps:
                nodes.append({
                    "id": s.step_id,
                    "label": f"{s.operation}",
                    "status": s.status.value,
                    "service_type": s.service_type.value,
                })
                for dep in s.dependencies:
                    edges.append({"source": dep, "target": s.step_id})

            return {"success": True, "workflow_id": wf.workflow_id, "name": wf.name, "nodes": nodes, "edges": edges}
        except AtlasDomainError as e:
            return self.handle_error(e, "get_workflow_graph")
        except AtlasExternalError as e:
            return self.handle_error(e, "get_workflow_graph")
        except AtlasValidationError as e:
            return self.handle_error(e, "get_workflow_graph")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "get_workflow_graph")

    def get_workflow_provenance(self, workflow_id: str) -> GetWorkflowProvenanceResult:
        try:
            if not workflow_id or workflow_id not in self.active_workflows:
                return {"success": False, "error": f"Workflow {workflow_id} not found"}
            wf = self.active_workflows[workflow_id]
            provenance = {
                "workflow_id": wf.workflow_id,
                "name": wf.name,
                "mlflow_run_id": wf.metadata.get("mlflow_run_id"),
                "mlflow_experiment_id": wf.metadata.get("mlflow_experiment_id"),
                "steps": [
                    {
                        "step_id": s.step_id,
                        "service_type": s.service_type.value,
                        "operation": s.operation,
                        "status": s.status.value,
                    }
                    for s in wf.steps
                ]
            }
            return {"success": True, "provenance": provenance}
        except AtlasDomainError as e:
            return self.handle_error(e, "get_workflow_provenance")
        except AtlasExternalError as e:
            return self.handle_error(e, "get_workflow_provenance")
        except AtlasValidationError as e:
            return self.handle_error(e, "get_workflow_provenance")
        except AtlasInfrastructureError as e:
            return self.handle_error(e, "get_workflow_provenance")

    # --- Persistence helpers (best-effort, guarded) ---
    def _persist_workflow(self, workflow: Workflow) -> None:
        db = None
        try:
            if not settings.enable_database:
                return
            db = get_db_session()
            rec = WorkflowRecord(
                workflow_id=workflow.workflow_id,
                name=workflow.name,
                description=workflow.description,
                status=workflow.status.value,
                metadata_json=workflow.metadata,
                created_at=workflow.created_at,
            )
            db.add(rec)
            db.flush()
            # Steps
            for s in workflow.steps:
                db.add(WorkflowStepRecord(
                    workflow_id=rec.id,
                    step_id=s.step_id,
                    service_type=s.service_type.value,
                    operation=s.operation,
                    parameters=s.parameters,
                    dependencies=s.dependencies,
                    status=s.status.value,
                ))
            db.commit()
        except AtlasExternalError as e:
            try:
                if db is not None:
                    db.rollback()
            except BiologyError:
                pass
            logger.warning(f"Workflow persistence skipped: {e}")
        finally:
            try:
                if db is not None:
                    db.close()
            except BiologyError:
                pass

    def _update_workflow_status(self, workflow: Workflow) -> None:
        db = None
        try:
            if not settings.enable_database:
                return
            db = get_db_session()
            rec = db.query(WorkflowRecord).filter(WorkflowRecord.workflow_id == workflow.workflow_id).first()
            if not rec:
                return
            setattr(rec, 'status', workflow.status.value)
            setattr(rec, 'started_at', workflow.started_at)
            setattr(rec, 'completed_at', workflow.completed_at)
            if workflow.metadata:
                try:
                    setattr(rec, 'metadata_json', workflow.metadata)
                except BiologyError:
                    pass
            db.commit()
        except BiologyError as e:
            try:
                if db is not None:
                    db.rollback()
            except BiologyError:
                pass
            logger.debug(f"Workflow status update skipped: {e}")
        finally:
            try:
                if db is not None:
                    db.close()
            except BiologyError:
                pass

    def _update_workflow_metadata(self, workflow: Workflow) -> None:
        db = None
        try:
            if not settings.enable_database:
                return
            db = get_db_session()
            rec = db.query(WorkflowRecord).filter(WorkflowRecord.workflow_id == workflow.workflow_id).first()
            if not rec:
                return
            setattr(rec, 'metadata_json', workflow.metadata)
            db.commit()
        except BiologyError:
            try:
                if db is not None:
                    db.rollback()
            except BiologyError:
                pass
        finally:
            try:
                if db is not None:
                    db.close()
            except BiologyError:
                pass

    def _update_step_status(self, workflow_id: str, step_id: str, status: WorkflowStatus, step: Optional[WorkflowStep] = None) -> None:
        db = None
        try:
            if not settings.enable_database:
                return
            db = get_db_session()
            wf = db.query(WorkflowRecord).filter(WorkflowRecord.workflow_id == workflow_id).first()
            if not wf:
                return
            rec = db.query(WorkflowStepRecord).filter(
                WorkflowStepRecord.workflow_id == wf.id,
                WorkflowStepRecord.step_id == step_id
            ).first()
            if not rec:
                return
            setattr(rec, 'status', status.value)
            if step:
                setattr(rec, 'result', step.result)
                setattr(rec, 'error', step.error)
                setattr(rec, 'execution_time', step.execution_time)
                setattr(rec, 'started_at', step.started_at)
                setattr(rec, 'completed_at', step.completed_at)
            db.commit()
        except BiologyError as e:
            try:
                if db is not None:
                    db.rollback()
            except BiologyError:
                pass
            logger.debug(f"Step status update skipped: {e}")
        finally:
            try:
                if db is not None:
                    db.close()
            except BiologyError:
                pass

    def _record_step_execution(self, workflow_id: Optional[str], step_id: str, attempt: int, status: str, cache_hit: bool, timeout: Optional[int], duration: Optional[float] = None) -> None:
        db = None
        try:
            if not settings.enable_database or not workflow_id:
                return
            db = get_db_session()
            wf = db.query(WorkflowRecord).filter(WorkflowRecord.workflow_id == workflow_id).first()
            if not wf:
                return
            step_rec = db.query(WorkflowStepRecord).filter(
                WorkflowStepRecord.workflow_id == wf.id,
                WorkflowStepRecord.step_id == step_id
            ).first()
            if not step_rec:
                return
            db.add(StepExecutionRecord(
                workflow_step_id=step_rec.id,
                attempt=attempt,
                status=status,
                cache_hit=cache_hit,
                timeout_sec=timeout,
                duration_sec=duration,
            ))
            db.commit()
        except AtlasExternalError as e:
            try:
                if db is not None:
                    db.rollback()
            except BiologyError:
                pass
            logger.debug(f"Step execution record skipped: {e}")
        finally:
            try:
                if db is not None:
                    db.close()
            except BiologyError:
                pass

    def _current_workflow_id(self) -> Optional[str]:
        """Best-effort current workflow id; when called from execution loop, last running workflow."""
        # Note: For simplicity, we can't reliably infer here without passing the workflow context.
        # Persist helpers accept explicit workflow_id in update paths elsewhere.
        return None
