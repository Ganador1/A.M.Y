"""
AXIOM Scheduler Router  
REST API endpoints for policy-aware scheduling system
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from pydantic import BaseModel, Field

from app.services.policy_aware_scheduler import (
from app.exceptions.domain.biology import BiologyError
    scheduler, ScheduledTask, ResourceRequirements, PolicyFactors,
    TaskPriority, TaskStatus, get_scheduler
)
from app.routers.auth import require_scheduler_access, require_scopes
from app.core.bootstrap_logging import logger

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])

# Request/Response models
class TaskSubmissionRequest(BaseModel):
    name: str = Field(..., description="Human-readable task name")
    task_type: str = Field(..., description="Type of task (e.g., 'research', 'experimental', 'analysis')")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority level")
    
    # Resource requirements
    cpu_cores: float = Field(default=1.0, ge=0.1, le=32.0, description="Required CPU cores")
    memory_gb: float = Field(default=2.0, ge=0.5, le=128.0, description="Required memory in GB")  
    gpu_cores: float = Field(default=0.0, ge=0.0, le=16.0, description="Required GPU cores")
    gpu_memory_gb: float = Field(default=0.0, ge=0.0, le=64.0, description="Required GPU memory in GB")
    storage_gb: float = Field(default=1.0, ge=0.1, le=1000.0, description="Required storage in GB")
    network_bandwidth_mbps: float = Field(default=10.0, ge=1.0, le=10000.0, description="Required network bandwidth")
    execution_time_minutes: float = Field(default=30.0, ge=1.0, le=1440.0, description="Estimated execution time")
    
    # Policy factors
    plausibility_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Scientific plausibility score")
    ethics_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Ethics compliance score") 
    risk_score: float = Field(default=0.3, ge=0.0, le=1.0, description="Risk assessment score")
    scientific_impact: float = Field(default=0.6, ge=0.0, le=1.0, description="Expected scientific impact")
    cost_efficiency: float = Field(default=0.7, ge=0.0, le=1.0, description="Cost efficiency score")
    reproducibility_likelihood: float = Field(default=0.75, ge=0.0, le=1.0, description="Reproducibility likelihood")
    innovation_potential: float = Field(default=0.4, ge=0.0, le=1.0, description="Innovation potential score")
    collaboration_value: float = Field(default=0.3, ge=0.0, le=1.0, description="Collaboration value score")
    
    # Task parameters and dependencies
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Task execution parameters")
    depends_on: List[str] = Field(default_factory=list, description="List of task IDs this task depends on")
    max_retries: int = Field(default=3, ge=0, le=10, description="Maximum retry attempts")

class TaskSubmissionResponse(BaseModel):
    task_id: str
    status: str
    composite_score: float
    cost_score: float
    feasibility_score: float
    estimated_cost: float
    queue_position: int
    submitted_at: str

class TaskStatusResponse(BaseModel):
    task_id: str
    name: str
    status: TaskStatus
    priority: TaskPriority
    composite_score: float
    cost_score: float
    feasibility_score: float
    submitted_at: Optional[str]
    scheduled_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]
    resources: Dict[str, float]
    policy_factors: Dict[str, float]
    results: Dict[str, Any]

class SchedulerStatusResponse(BaseModel):
    status: str
    queue_length: int
    running_tasks: int
    completed_tasks: int
    resource_utilization: Dict[str, float]
    statistics: Dict[str, Any]
    optimizer_weights: Dict[str, float]

class OptimizationWeightsRequest(BaseModel):
    plausibility: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    ethics: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    risk: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    scientific_impact: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    cost_efficiency: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    reproducibility: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    innovation: Optional[float] = Field(default=None, ge=-1.0, le=1.0)
    collaboration: Optional[float] = Field(default=None, ge=-1.0, le=1.0)

@router.post("/submit", summary="Submit task for scheduling")
async def submit_task(
    request: TaskSubmissionRequest,
    current_user: Dict[str, Any] = Depends(require_scheduler_access())
) -> TaskSubmissionResponse:
    """Submit a new task to the policy-aware scheduler."""
    
    try:
        # Create task ID
        task_id = f"task_{uuid.uuid4().hex[:8]}_{int(datetime.utcnow().timestamp())}"
        
        # Build resource requirements
        resources = ResourceRequirements(
            cpu_cores=request.cpu_cores,
            memory_gb=request.memory_gb,
            gpu_cores=request.gpu_cores,
            gpu_memory_gb=request.gpu_memory_gb,
            storage_gb=request.storage_gb,
            network_bandwidth_mbps=request.network_bandwidth_mbps,
            execution_time_minutes=request.execution_time_minutes
        )
        
        # Build policy factors
        policy_factors = PolicyFactors(
            plausibility_score=request.plausibility_score,
            ethics_score=request.ethics_score,
            risk_score=request.risk_score,
            scientific_impact=request.scientific_impact,
            cost_efficiency=request.cost_efficiency,
            reproducibility_likelihood=request.reproducibility_likelihood,
            innovation_potential=request.innovation_potential,
            collaboration_value=request.collaboration_value
        )
        
        # Create scheduled task
        task = ScheduledTask(
            task_id=task_id,
            name=request.name,
            task_type=request.task_type,
            priority=request.priority,
            status=TaskStatus.PENDING,
            resources=resources,
            policy_factors=policy_factors,
            submitted_at=datetime.utcnow(),
            parameters=request.parameters,
            depends_on=request.depends_on,
            max_retries=request.max_retries
        )
        
        # Submit to scheduler
        submitted_task_id = await scheduler.submit_task(task)
        
        # Calculate estimated cost
        estimated_cost = (1.0 - task.cost_score) * 100  # Mock calculation
        
        # Get queue position (approximate)
        queue_position = len(scheduler.task_queue) + len(scheduler.running_tasks)
        
        logger.info(f"Task {task_id} submitted by {current_user.get('sub')}")
        
        return TaskSubmissionResponse(
            task_id=submitted_task_id,
            status=task.status.value,
            composite_score=task.composite_score,
            cost_score=task.cost_score,
            feasibility_score=task.feasibility_score,
            estimated_cost=estimated_cost,
            queue_position=queue_position,
            submitted_at=task.submitted_at.isoformat()
        )
        
    except BiologyError as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit task: {str(e)}"
        )

@router.get("/tasks/{task_id}", summary="Get task status")
async def get_task_status(
    task_id: str,
    current_user: Dict[str, Any] = Depends(require_scopes(["scheduler:policy"]))
) -> TaskStatusResponse:
    """Get the status and details of a specific task."""
    
    task_info = scheduler.get_task_status(task_id)
    
    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found"
        )
    
    return TaskStatusResponse(**task_info)

@router.get("/status", summary="Get scheduler status")
async def get_scheduler_status(
    current_user: Dict[str, Any] = Depends(require_scopes(["scheduler:policy"]))
) -> SchedulerStatusResponse:
    """Get the current status of the policy-aware scheduler."""
    
    status_info = scheduler.get_scheduler_status()
    
    return SchedulerStatusResponse(**status_info)

@router.get("/tasks", summary="List all tasks")
async def list_tasks(
    status_filter: Optional[TaskStatus] = Query(default=None, description="Filter tasks by status"),
    priority_filter: Optional[TaskPriority] = Query(default=None, description="Filter tasks by priority"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum number of tasks to return"),
    offset: int = Query(default=0, ge=0, description="Number of tasks to skip"),
    current_user: Dict[str, Any] = Depends(require_scopes(["scheduler:policy"]))
) -> Dict[str, Any]:
    """List tasks with optional filtering."""
    
    all_tasks = []
    
    # Collect tasks from all categories
    all_tasks.extend(scheduler.tasks.values())
    all_tasks.extend(scheduler.running_tasks.values())
    all_tasks.extend(scheduler.completed_tasks.values())
    
    # Apply filters
    filtered_tasks = all_tasks
    
    if status_filter:
        filtered_tasks = [t for t in filtered_tasks if t.status == status_filter]
    
    if priority_filter:
        filtered_tasks = [t for t in filtered_tasks if t.priority == priority_filter]
    
    # Sort by submission time (most recent first)
    filtered_tasks.sort(key=lambda t: t.submitted_at, reverse=True)
    
    # Apply pagination
    paginated_tasks = filtered_tasks[offset:offset + limit]
    
    # Convert to response format
    task_list = []
    for task in paginated_tasks:
        task_dict = scheduler.get_task_status(task.task_id)
        if task_dict:
            task_list.append(task_dict)
    
    return {
        "tasks": task_list,
        "total_count": len(filtered_tasks),
        "offset": offset,
        "limit": limit,
        "has_more": len(filtered_tasks) > offset + limit
    }

@router.delete("/tasks/{task_id}", summary="Cancel task")
async def cancel_task(
    task_id: str,
    current_user: Dict[str, Any] = Depends(require_scheduler_access())
) -> Dict[str, str]:
    """Cancel a pending or running task."""
    
    # Check if task exists and is cancellable
    if task_id in scheduler.running_tasks:
        task = scheduler.running_tasks[task_id]
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        task.results['cancellation_reason'] = f"Cancelled by {current_user.get('sub')}"
        
        # Deallocate resources
        scheduler.deallocate_resources(task)
        
        # Move to completed tasks
        del scheduler.running_tasks[task_id]
        scheduler.completed_tasks[task_id] = task
        
        logger.info(f"Running task {task_id} cancelled by {current_user.get('sub')}")
        
    elif task_id in scheduler.tasks:
        task = scheduler.tasks[task_id]
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.utcnow()
        task.results['cancellation_reason'] = f"Cancelled by {current_user.get('sub')}"
        
        # Remove from pending queue (this is simplified - in practice would need to rebuild queue)
        scheduler.completed_tasks[task_id] = task
        del scheduler.tasks[task_id]
        
        logger.info(f"Pending task {task_id} cancelled by {current_user.get('sub')}")
        
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found or not cancellable"
        )
    
    return {
        "message": f"Task {task_id} cancelled successfully",
        "cancelled_by": current_user.get('sub'),
        "cancelled_at": datetime.utcnow().isoformat()
    }

@router.put("/optimization/weights", summary="Update optimization weights")
async def update_optimization_weights(
    weights: OptimizationWeightsRequest,
    current_user: Dict[str, Any] = Depends(require_scheduler_access())
) -> Dict[str, Any]:
    """Update the multi-objective optimization weights."""
    
    updated_weights = {}
    
    # Update only provided weights
    weight_mapping = {
        'plausibility': weights.plausibility,
        'ethics': weights.ethics,
        'risk': weights.risk,
        'scientific_impact': weights.scientific_impact,
        'cost_efficiency': weights.cost_efficiency,
        'reproducibility': weights.reproducibility,
        'innovation': weights.innovation,
        'collaboration': weights.collaboration
    }
    
    for weight_name, weight_value in weight_mapping.items():
        if weight_value is not None:
            scheduler.optimizer.weights[weight_name] = weight_value
            updated_weights[weight_name] = weight_value
    
    logger.info(f"Optimization weights updated by {current_user.get('sub')}: {updated_weights}")
    
    return {
        "message": "Optimization weights updated successfully",
        "updated_weights": updated_weights,
        "current_weights": scheduler.optimizer.weights,
        "updated_by": current_user.get('sub'),
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/optimization/weights", summary="Get current optimization weights")
async def get_optimization_weights(
    current_user: Dict[str, Any] = Depends(require_scopes(["scheduler:policy"]))
) -> Dict[str, float]:
    """Get the current multi-objective optimization weights."""
    
    return scheduler.optimizer.weights

@router.post("/priority/boost", summary="Boost task priority")
async def boost_task_priority(
    task_id: str = Body(..., embed=True),
    new_priority: TaskPriority = Body(..., embed=True),
    current_user: Dict[str, Any] = Depends(require_scheduler_access())
) -> Dict[str, Any]:
    """Boost the priority of a pending task."""
    
    if task_id not in scheduler.tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pending task {task_id} not found"
        )
    
    task = scheduler.tasks[task_id]
    old_priority = task.priority
    task.priority = new_priority
    
    # Recalculate composite score with new priority
    task.composite_score = scheduler.optimizer.calculate_composite_score(task)
    
    # Re-queue with new priority (simplified approach)
    # In practice, would need to rebuild the priority queue
    
    logger.info(f"Task {task_id} priority boosted from {old_priority.value} to {new_priority.value} by {current_user.get('sub')}")
    
    return {
        "message": f"Task {task_id} priority boosted successfully",
        "old_priority": old_priority.value,
        "new_priority": new_priority.value,
        "new_composite_score": task.composite_score,
        "updated_by": current_user.get('sub'),
        "updated_at": datetime.utcnow().isoformat()
    }

@router.get("/resources", summary="Get resource utilization")
async def get_resource_utilization(
    current_user: Dict[str, Any] = Depends(require_scopes(["scheduler:policy"]))
) -> Dict[str, Any]:
    """Get current resource utilization and availability."""
    
    available = scheduler.available_resources
    used = scheduler.used_resources
    
    utilization = {
        'cpu_cores': {
            'total': available.cpu_cores,
            'used': used.cpu_cores,
            'available': available.cpu_cores - used.cpu_cores,
            'utilization_percent': (used.cpu_cores / available.cpu_cores) * 100 if available.cpu_cores > 0 else 0
        },
        'memory_gb': {
            'total': available.memory_gb,
            'used': used.memory_gb,
            'available': available.memory_gb - used.memory_gb,
            'utilization_percent': (used.memory_gb / available.memory_gb) * 100 if available.memory_gb > 0 else 0
        },
        'gpu_cores': {
            'total': available.gpu_cores,
            'used': used.gpu_cores,
            'available': available.gpu_cores - used.gpu_cores,
            'utilization_percent': (used.gpu_cores / available.gpu_cores) * 100 if available.gpu_cores > 0 else 0
        },
        'gpu_memory_gb': {
            'total': available.gpu_memory_gb,
            'used': used.gpu_memory_gb,
            'available': available.gpu_memory_gb - used.gpu_memory_gb,
            'utilization_percent': (used.gpu_memory_gb / available.gpu_memory_gb) * 100 if available.gpu_memory_gb > 0 else 0
        },
        'storage_gb': {
            'total': available.storage_gb,
            'used': used.storage_gb,
            'available': available.storage_gb - used.storage_gb,
            'utilization_percent': (used.storage_gb / available.storage_gb) * 100 if available.storage_gb > 0 else 0
        }
    }
    
    return {
        'resource_utilization': utilization,
        'running_tasks': len(scheduler.running_tasks),
        'queued_tasks': len(scheduler.task_queue),
        'timestamp': datetime.utcnow().isoformat()
    }
