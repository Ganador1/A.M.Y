"""AXIOM Multi-Agent Orchestrator
Coordinates multiple autonomous agents for laboratory operations.

Guarded global instantiation respects environment variable AXIOM_SKIP_AUTOINIT
to suppress heavy side-effects during bulk import verification.
"""

import os
import asyncio
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.services.policy_aware_scheduler import (
    scheduler, ScheduledTask, ResourceRequirements, PolicyFactors,
    TaskPriority, TaskStatus
)
from app.exceptions.domain.biology import BiologyError

from app.routers.system import track_lineage_node
from app.core.bootstrap_logging import logger
from app.config import settings
from app.types.multi_agent_orchestrator_types import (
    ResearchAgentExecutorResult,
    ExperimentalAgentExecutorResult,
    AnalysisAgentExecutorResult,
    ValidationAgentExecutorResult,
    ExecuteWorkflowResult,
    GetOrchestratorStatusResult,
)

class AgentType(Enum):
    """Types of autonomous agents"""
    RESEARCH = "research"
    EXPERIMENTAL = "experimental"
    ANALYSIS = "analysis"
    VALIDATION = "validation"
    PUBLICATION = "publication"
    ETHICS = "ethics"
    QUALITY_CONTROL = "quality_control"

class AgentStatus(Enum):
    """Agent operational status"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"

@dataclass
class AgentCapability:
    """Capability description for an agent"""
    name: str
    description: str
    resource_requirements: ResourceRequirements
    execution_time_estimate: float  # minutes
    success_probability: float
    prerequisites: List[str] = field(default_factory=list)

@dataclass
class AutonomousAgent:
    """Autonomous agent with capabilities and state"""
    agent_id: str
    name: str
    agent_type: AgentType
    status: AgentStatus
    capabilities: List[AgentCapability]
    
    # Agent metadata
    created_at: datetime
    last_active: datetime
    total_tasks_completed: int = 0
    success_rate: float = 1.0
    
    # Current execution
    current_task_id: Optional[str] = None
    current_capability: Optional[str] = None
    
    # Agent-specific configuration
    config: Dict[str, Any] = field(default_factory=dict)
    
    # Execution function (injected)
    executor: Optional[Callable] = field(default=None, repr=False)

@dataclass
class WorkflowStep:
    """Single step in a multi-agent workflow"""
    step_id: str
    agent_type: AgentType
    capability_name: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    
    # Execution tracking
    assigned_agent_id: Optional[str] = None
    scheduled_task_id: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    results: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

@dataclass
class AutonomousWorkflow:
    """Multi-agent autonomous workflow"""
    workflow_id: str
    name: str
    description: str
    domain: str
    
    # Workflow structure
    steps: List[WorkflowStep]
    
    # Overall workflow state
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results and provenance
    final_results: Dict[str, Any] = field(default_factory=dict)
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    
    # Policy and quality constraints
    quality_threshold: float = 0.8
    ethics_threshold: float = 0.7
    reproducibility_threshold: float = 0.75

class MultiAgentOrchestrator:
    """Orchestrates multiple autonomous agents for complex workflows"""
    
    def __init__(self):
        self.agents: Dict[str, AutonomousAgent] = {}
        self.workflows: Dict[str, AutonomousWorkflow] = {}
        self.active_workflows = set()
        self.knowledge_graph: Dict[str, Dict[str, Any]] = {}
        
        # Statistics tracking
        self.stats = {
            'workflows_executed': 0,
            'workflows_completed': 0,
            'workflows_failed': 0,
            'total_agents': 0,
            'total_execution_time': 0.0
        }
        
        # Initialize default agents
        self._initialize_default_agents()
        
        logger.info("Multi-Agent Orchestrator initialized")
    
    async def initialize(self):
        """Initialize the multi-agent orchestrator"""
        logger.info("🚀 Initializing Multi-Agent Orchestrator...")
        
        # Start agent monitoring
        self.stats['orchestrator_start_time'] = datetime.now().isoformat()
        self.stats['total_agents'] = len(self.agents)
        
        # Initialize knowledge graph integration
        self.stats['knowledge_graph_initialized'] = True
        
        logger.info(f"✅ Multi-Agent Orchestrator initialized with {len(self.agents)} agents")
    
    async def shutdown(self):
        """Shutdown the multi-agent orchestrator"""
        logger.info("🛑 Shutting down Multi-Agent Orchestrator...")
        
        # Stop all running workflows
        for workflow_id, workflow in self.workflows.items():
            if workflow.status == TaskStatus.RUNNING:
                workflow.status = TaskStatus.CANCELLED
                logger.info(f"Cancelled workflow: {workflow_id}")
        
        # Update stats
        self.stats['orchestrator_stop_time'] = datetime.now().isoformat()
        
        logger.info("✅ Multi-Agent Orchestrator shutdown complete")
    
    def _initialize_default_agents(self):
        """Initialize default autonomous agents"""
        
        # Research Agent
        research_agent = AutonomousAgent(
            agent_id="research_001",
            name="Research Agent Alpha",
            agent_type=AgentType.RESEARCH,
            status=AgentStatus.IDLE,
            capabilities=[
                AgentCapability(
                    name="hypothesis_generation",
                    description="Generate scientific hypotheses from literature",
                    resource_requirements=ResourceRequirements(cpu_cores=2.0, memory_gb=4.0, execution_time_minutes=15.0),
                    execution_time_estimate=15.0,
                    success_probability=0.85
                ),
                AgentCapability(
                    name="literature_analysis",
                    description="Analyze scientific literature for patterns",
                    resource_requirements=ResourceRequirements(cpu_cores=1.0, memory_gb=2.0, execution_time_minutes=30.0),
                    execution_time_estimate=30.0,
                    success_probability=0.90
                )
            ],
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            executor=self._research_agent_executor
        )
        
        # Experimental Agent
        experimental_agent = AutonomousAgent(
            agent_id="experiment_001",
            name="Experimental Agent Beta",
            agent_type=AgentType.EXPERIMENTAL,
            status=AgentStatus.IDLE,
            capabilities=[
                AgentCapability(
                    name="molecular_simulation",
                    description="Run molecular dynamics simulations",
                    resource_requirements=ResourceRequirements(cpu_cores=4.0, memory_gb=8.0, gpu_cores=1.0, execution_time_minutes=60.0),
                    execution_time_estimate=60.0,
                    success_probability=0.80
                ),
                AgentCapability(
                    name="chemical_property_prediction",
                    description="Predict chemical properties using ML",
                    resource_requirements=ResourceRequirements(cpu_cores=2.0, memory_gb=4.0, execution_time_minutes=20.0),
                    execution_time_estimate=20.0,
                    success_probability=0.88
                )
            ],
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            executor=self._experimental_agent_executor
        )
        
        # Analysis Agent
        analysis_agent = AutonomousAgent(
            agent_id="analysis_001",
            name="Analysis Agent Gamma",
            agent_type=AgentType.ANALYSIS,
            status=AgentStatus.IDLE,
            capabilities=[
                AgentCapability(
                    name="statistical_analysis",
                    description="Perform statistical analysis of experimental data",
                    resource_requirements=ResourceRequirements(cpu_cores=2.0, memory_gb=4.0, execution_time_minutes=25.0),
                    execution_time_estimate=25.0,
                    success_probability=0.92
                ),
                AgentCapability(
                    name="pattern_recognition",
                    description="Identify patterns in complex datasets",
                    resource_requirements=ResourceRequirements(cpu_cores=3.0, memory_gb=6.0, execution_time_minutes=45.0),
                    execution_time_estimate=45.0,
                    success_probability=0.78
                )
            ],
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            executor=self._analysis_agent_executor
        )
        
        # Validation Agent
        validation_agent = AutonomousAgent(
            agent_id="validation_001",
            name="Validation Agent Delta",
            agent_type=AgentType.VALIDATION,
            status=AgentStatus.IDLE,
            capabilities=[
                AgentCapability(
                    name="reproducibility_check",
                    description="Verify reproducibility of experimental results",
                    resource_requirements=ResourceRequirements(cpu_cores=1.0, memory_gb=2.0, execution_time_minutes=20.0),
                    execution_time_estimate=20.0,
                    success_probability=0.95
                ),
                AgentCapability(
                    name="quality_assessment",
                    description="Assess quality and validity of results",
                    resource_requirements=ResourceRequirements(cpu_cores=1.0, memory_gb=2.0, execution_time_minutes=15.0),
                    execution_time_estimate=15.0,
                    success_probability=0.90
                )
            ],
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            executor=self._validation_agent_executor
        )
        
        # Register agents
        self.agents[research_agent.agent_id] = research_agent
        self.agents[experimental_agent.agent_id] = experimental_agent
        self.agents[analysis_agent.agent_id] = analysis_agent
        self.agents[validation_agent.agent_id] = validation_agent
        
        # Track in lineage
        for agent in self.agents.values():
            track_lineage_node(
                agent.agent_id,
                "agent",
                agent.name,
                parent_ids=["axiom_core"],
                metadata={
                    "type": agent.agent_type.value,
                    "capabilities": [cap.name for cap in agent.capabilities],
                    "status": agent.status.value
                }
            )
    
    async def _research_agent_executor(self, parameters: ResearchAgentExecutorResult) -> ResearchAgentExecutorResult:
        """Mock research agent execution"""
        capability = parameters.get('capability')
        
        # Simulate research work
        await asyncio.sleep(2)  # Simulated processing time
        
        if capability == "hypothesis_generation":
            return {
                "hypothesis": "Novel compound X shows promising properties for Y application",
                "confidence": 0.78,
                "literature_refs": ["doi:10.1000/example1", "doi:10.1000/example2"],
                "research_areas": ["chemistry", "materials_science"]
            }
        elif capability == "literature_analysis":
            return {
                "patterns_found": 3,
                "key_insights": ["Trend A in domain X", "Gap B in research Y"],
                "recommendation": "Focus on unexplored area Z",
                "confidence": 0.82
            }
        
        return {"status": "completed", "capability": capability}
    
    async def _experimental_agent_executor(self, parameters: ExperimentalAgentExecutorResult) -> ExperimentalAgentExecutorResult:
        """Mock experimental agent execution"""
        capability = parameters.get('capability')
        
        # Simulate experimental work
        await asyncio.sleep(3)  # Simulated processing time
        
        if capability == "molecular_simulation":
            return {
                "simulation_results": {
                    "binding_affinity": -8.5,
                    "stability": 0.89,
                    "interaction_sites": 4
                },
                "trajectory_file": "/tmp/simulation_001.xtc",
                "confidence": 0.85
            }
        elif capability == "chemical_property_prediction":
            return {
                "predicted_properties": {
                    "solubility": 3.2,
                    "toxicity": 0.15,
                    "bioavailability": 0.68
                },
                "model_accuracy": 0.91,
                "confidence": 0.87
            }
        
        return {"status": "completed", "capability": capability}
    
    async def _analysis_agent_executor(self, parameters: AnalysisAgentExecutorResult) -> AnalysisAgentExecutorResult:
        """Mock analysis agent execution"""
        capability = parameters.get('capability')
        
        # Simulate analysis work
        await asyncio.sleep(2.5)  # Simulated processing time
        
        if capability == "statistical_analysis":
            return {
                "statistical_summary": {
                    "mean": 4.2,
                    "std": 1.1,
                    "p_value": 0.003,
                    "effect_size": 0.8
                },
                "significance": True,
                "confidence_interval": [3.1, 5.3]
            }
        elif capability == "pattern_recognition":
            return {
                "patterns_identified": [
                    {"pattern": "cyclical_behavior", "strength": 0.89},
                    {"pattern": "correlation_xy", "strength": 0.76}
                ],
                "anomalies_detected": 2,
                "model_performance": 0.84
            }
        
        return {"status": "completed", "capability": capability}
    
    async def _validation_agent_executor(self, parameters: ValidationAgentExecutorResult) -> ValidationAgentExecutorResult:
        """Mock validation agent execution"""
        capability = parameters.get('capability')
        
        # Simulate validation work
        await asyncio.sleep(1.5)  # Simulated processing time
        
        if capability == "reproducibility_check":
            return {
                "reproducibility_score": 0.87,
                "issues_found": ["minor_parameter_variation"],
                "recommendations": ["standardize_temperature_control"],
                "validation_status": "passed"
            }
        elif capability == "quality_assessment":
            return {
                "quality_score": 0.91,
                "quality_dimensions": {
                    "accuracy": 0.94,
                    "precision": 0.88,
                    "completeness": 0.92
                },
                "overall_assessment": "high_quality"
            }
        
        return {"status": "completed", "capability": capability}
    
    def register_agent(self, agent: AutonomousAgent):
        """Register a new autonomous agent"""
        self.agents[agent.agent_id] = agent
        
        # Track in lineage
        track_lineage_node(
            agent.agent_id,
            "agent",
            agent.name,
            parent_ids=["axiom_core"],
            metadata={
                "type": agent.agent_type.value,
                "capabilities": [cap.name for cap in agent.capabilities],
                "status": agent.status.value
            }
        )
        
        logger.info(f"Agent {agent.agent_id} registered: {agent.name}")
    
    def find_available_agent(self, agent_type: AgentType, capability_name: str) -> Optional[AutonomousAgent]:
        """Find an available agent with specific capability"""
        for agent in self.agents.values():
            if (agent.agent_type == agent_type and 
                agent.status == AgentStatus.IDLE and
                any(cap.name == capability_name for cap in agent.capabilities)):
                return agent
        return None
    
    async def create_autonomous_workflow(self, workflow_spec: Dict[str, Any]) -> AutonomousWorkflow:
        """Create a new autonomous workflow from specification"""
        
        workflow_id = f"workflow_{uuid.uuid4().hex[:8]}_{int(datetime.utcnow().timestamp())}"
        
        # Parse workflow steps
        steps = []
        for step_spec in workflow_spec.get('steps', []):
            step = WorkflowStep(
                step_id=step_spec['step_id'],
                agent_type=AgentType(step_spec['agent_type']),
                capability_name=step_spec['capability'],
                parameters=step_spec.get('parameters', {}),
                dependencies=step_spec.get('dependencies', [])
            )
            steps.append(step)
        
        workflow = AutonomousWorkflow(
            workflow_id=workflow_id,
            name=workflow_spec['name'],
            description=workflow_spec.get('description', ''),
            domain=workflow_spec.get('domain', 'general'),
            steps=steps,
            quality_threshold=workflow_spec.get('quality_threshold', 0.8),
            ethics_threshold=workflow_spec.get('ethics_threshold', 0.7),
            reproducibility_threshold=workflow_spec.get('reproducibility_threshold', 0.75)
        )
        
        self.workflows[workflow_id] = workflow
        
        # Track in lineage
        track_lineage_node(
            workflow_id,
            "workflow",
            workflow.name,
            parent_ids=["axiom_core"],
            metadata={
                "domain": workflow.domain,
                "steps_count": len(workflow.steps),
                "status": workflow.status.value
            }
        )
        
        logger.info(f"Autonomous workflow created: {workflow_id}")
        
        return workflow
    
    async def execute_workflow(self, workflow_id: str) -> ExecuteWorkflowResult:
        """Execute an autonomous workflow with multi-agent coordination"""
        
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        workflow = self.workflows[workflow_id]
        workflow.status = TaskStatus.RUNNING
        workflow.started_at = datetime.utcnow()
        self.active_workflows.add(workflow_id)
        
        try:
            # Execute steps in dependency order
            completed_steps = set()
            
            while len(completed_steps) < len(workflow.steps):
                # Find steps ready to execute
                ready_steps = [
                    step for step in workflow.steps
                    if (step.step_id not in completed_steps and
                        all(dep in completed_steps for dep in step.dependencies))
                ]
                
                if not ready_steps:
                    break  # No more steps can be executed
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(self._execute_workflow_step(workflow, step))
                    tasks.append((step.step_id, task))
                
                # Wait for step completion
                for step_id, task in tasks:
                    try:
                        await task
                        completed_steps.add(step_id)
                        
                        # Log step completion
                        workflow.execution_log.append({
                            "timestamp": datetime.utcnow().isoformat(),
                            "step_id": step_id,
                            "status": "completed"
                        })
                        
                    except BiologyError as e:
                        logger.error(f"Step {step_id} failed: {e}")
                        workflow.execution_log.append({
                            "timestamp": datetime.utcnow().isoformat(),
                            "step_id": step_id,
                            "status": "failed",
                            "error": str(e)
                        })
            
            # Collect final results
            workflow.final_results = {}
            for step in workflow.steps:
                if step.results:
                    workflow.final_results[step.step_id] = step.results
            
            # Update knowledge graph with results
            await self._update_knowledge_graph(workflow)
            
            workflow.status = TaskStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()
            
            logger.info(f"Autonomous workflow {workflow_id} completed successfully")
            
            return {
                "workflow_id": workflow_id,
                "status": "completed",
                "results": workflow.final_results,
                "execution_time_minutes": (workflow.completed_at - workflow.started_at).total_seconds() / 60,
                "steps_completed": len(completed_steps),
                "knowledge_graph_updated": True
            }
            
        except BiologyError as e:
            workflow.status = TaskStatus.FAILED
            workflow.completed_at = datetime.utcnow()
            
            logger.error(f"Workflow {workflow_id} failed: {e}")
            
            return {
                "workflow_id": workflow_id,
                "status": "failed",
                "error": str(e),
                "partial_results": workflow.final_results
            }
        
        finally:
            self.active_workflows.discard(workflow_id)
    
    async def _execute_workflow_step(self, workflow: AutonomousWorkflow, step: WorkflowStep):
        """Execute a single workflow step"""
        
        # Find available agent
        agent = self.find_available_agent(step.agent_type, step.capability_name)
        if not agent:
            raise RuntimeError(f"No available agent for {step.agent_type.value} with capability {step.capability_name}")
        
        # Assign agent and update status
        step.assigned_agent_id = agent.agent_id
        agent.status = AgentStatus.BUSY
        agent.current_task_id = step.step_id
        agent.current_capability = step.capability_name
        step.started_at = datetime.utcnow()
        
        try:
            # Find capability details
            capability = next((cap for cap in agent.capabilities if cap.name == step.capability_name), None)
            if not capability:
                raise ValueError(f"Capability {step.capability_name} not found in agent {agent.agent_id}")
            
            # Create policy factors for scheduling
            policy_factors = PolicyFactors(
                plausibility_score=0.8,
                ethics_score=workflow.ethics_threshold,
                scientific_impact=0.7,
                reproducibility_likelihood=workflow.reproducibility_threshold
            )
            
            # Create scheduled task
            scheduled_task = ScheduledTask(
                task_id=f"step_{step.step_id}_{uuid.uuid4().hex[:6]}",
                name=f"{workflow.name} - {step.step_id}",
                task_type="workflow_step",
                priority=TaskPriority.NORMAL,
                status=TaskStatus.PENDING,
                resources=capability.resource_requirements,
                policy_factors=policy_factors,
                submitted_at=datetime.utcnow(),
                executor=agent.executor,
                parameters=step.parameters | {"capability": step.capability_name}
            )
            
            # Submit to scheduler
            step.scheduled_task_id = await scheduler.submit_task(scheduled_task)
            
            # Wait for task completion (simplified - in practice would check scheduler status)
            await asyncio.sleep(capability.execution_time_estimate * 60 / 10)  # Accelerated for demo
            
            # Get results from scheduler
            task_status = scheduler.get_task_status(step.scheduled_task_id)
            if task_status and task_status['status'] == 'completed':
                step.results = task_status['results']
                step.status = TaskStatus.COMPLETED
            else:
                step.status = TaskStatus.FAILED
                step.results = {"error": "Task execution failed"}
            
            step.completed_at = datetime.utcnow()
            
            # Update agent statistics
            agent.total_tasks_completed += 1
            if step.status == TaskStatus.COMPLETED:
                agent.success_rate = (agent.success_rate * (agent.total_tasks_completed - 1) + 1) / agent.total_tasks_completed
            else:
                agent.success_rate = (agent.success_rate * (agent.total_tasks_completed - 1)) / agent.total_tasks_completed
            
        finally:
            # Release agent
            agent.status = AgentStatus.IDLE
            agent.current_task_id = None
            agent.current_capability = None
            agent.last_active = datetime.utcnow()
    
    async def _update_knowledge_graph(self, workflow: AutonomousWorkflow):
        """Update knowledge graph with workflow results"""
        
        # Simplified knowledge graph update
        kg_entry = {
            "workflow_id": workflow.workflow_id,
            "domain": workflow.domain,
            "timestamp": workflow.completed_at.isoformat() if workflow.completed_at else datetime.now().isoformat(),
            "results": workflow.final_results,
            "entities": [],
            "relationships": []
        }
        
        # Extract entities and relationships from results
        for step_id, results in workflow.final_results.items():
            if isinstance(results, dict):
                # Extract key findings as entities
                for key, value in results.items():
                    if isinstance(value, (str, int, float)) and key in ['hypothesis', 'binding_affinity', 'pattern', 'quality_score']:
                        kg_entry["entities"].append({
                            "entity": f"{workflow.domain}_{key}_{step_id}",
                            "type": key,
                            "value": value,
                            "source_step": step_id
                        })
                
                # Create relationships between steps
                step = next((s for s in workflow.steps if s.step_id == step_id), None)
                if step and step.dependencies:
                    for dep in step.dependencies:
                        kg_entry["relationships"].append({
                            "from": dep,
                            "to": step_id,
                            "relationship": "precedes",
                            "workflow": workflow.workflow_id
                        })
        
        # Store in simplified knowledge graph
        self.knowledge_graph[workflow.workflow_id] = kg_entry
        
        logger.info(f"Knowledge graph updated with workflow {workflow.workflow_id} results")
    
    def get_orchestrator_status(self) -> GetOrchestratorStatusResult:
        """Get current orchestrator status"""
        
        agents_by_status = {}
        for status in AgentStatus:
            agents_by_status[status.value] = len([a for a in self.agents.values() if a.status == status])
        
        workflows_by_status = {}
        for status in TaskStatus:
            workflows_by_status[status.value] = len([w for w in self.workflows.values() if w.status == status])
        
        return {
            "total_agents": len(self.agents),
            "agents_by_status": agents_by_status,
            "total_workflows": len(self.workflows),
            "workflows_by_status": workflows_by_status,
            "active_workflows": len(self.active_workflows),
            "knowledge_graph_entries": len(self.knowledge_graph),
            "agent_success_rates": {
                agent_id: agent.success_rate 
                for agent_id, agent in self.agents.items()
            }
        }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific workflow"""
        
        if workflow_id not in self.workflows:
            return None
        
        workflow = self.workflows[workflow_id]
        
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "domain": workflow.domain,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": [
                {
                    "step_id": step.step_id,
                    "agent_type": step.agent_type.value,
                    "capability": step.capability_name,
                    "status": step.status.value,
                    "assigned_agent": step.assigned_agent_id,
                    "results_available": bool(step.results)
                }
                for step in workflow.steps
            ],
            "final_results": workflow.final_results,
            "execution_log": workflow.execution_log[-10:]  # Last 10 entries
        }


def _should_skip_autoinit() -> bool:
    env_flag = str(os.getenv("AXIOM_SKIP_AUTOINIT", "0")).lower()
    settings_flag = str(getattr(settings, "AXIOM_SKIP_AUTOINIT", env_flag)).lower()
    return settings_flag in {"1", "true", "yes"}


# Global orchestrator instance (guarded)
if not _should_skip_autoinit():
    orchestrator = MultiAgentOrchestrator()
else:  # pragma: no cover
    orchestrator = None  # type: ignore

def get_orchestrator() -> MultiAgentOrchestrator:
    """Get the global orchestrator instance"""
    return orchestrator
