"""
AXIOM Policy-Aware Scheduler
Multi-objective scheduling system with plausibility, ethics, cost, and impact optimization
"""

import heapq
import time
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math

from app.services.policy_engine_service import policy_engine_service
from app.core.bootstrap_logging import logger
from app.exceptions.external.llm import LLMError

class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ResourceRequirements:
    """Resource requirements for task execution"""
    cpu_cores: float = 1.0
    memory_gb: float = 2.0
    gpu_cores: float = 0.0
    gpu_memory_gb: float = 0.0
    storage_gb: float = 1.0
    network_bandwidth_mbps: float = 10.0
    execution_time_minutes: float = 30.0

@dataclass
class PolicyFactors:
    """Policy-aware factors for multi-objective optimization"""
    plausibility_score: float = 0.5  # 0.0 to 1.0
    ethics_score: float = 0.8  # 0.0 to 1.0 (higher = more ethical)
    risk_score: float = 0.3  # 0.0 to 1.0 (higher = more risky)
    scientific_impact: float = 0.6  # 0.0 to 1.0
    cost_efficiency: float = 0.7  # 0.0 to 1.0 (higher = more efficient)
    reproducibility_likelihood: float = 0.75  # 0.0 to 1.0
    innovation_potential: float = 0.4  # 0.0 to 1.0
    collaboration_value: float = 0.3  # 0.0 to 1.0

@dataclass
class ScheduledTask:
    """Task with scheduling metadata"""
    task_id: str
    name: str
    task_type: str
    priority: TaskPriority
    status: TaskStatus
    
    # Resource and policy factors
    resources: ResourceRequirements
    policy_factors: PolicyFactors
    
    # Scheduling metadata
    submitted_at: datetime
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Task execution
    executor: Optional[Callable] = field(default=None, repr=False)
    parameters: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    
    # Multi-objective scores
    composite_score: float = 0.0
    cost_score: float = 0.0
    feasibility_score: float = 1.0
    
    # Dependencies and constraints
    depends_on: List[str] = field(default_factory=list)
    max_retries: int = 3
    current_retries: int = 0

class MultiObjectiveOptimizer:
    """Multi-objective optimization for policy-aware scheduling"""
    
    def __init__(self):
        # Configurable weights for different objectives
        self.weights = {
            'plausibility': 0.20,
            'ethics': 0.15,
            'risk': -0.10,  # Negative weight (minimize risk)
            'scientific_impact': 0.25,
            'cost_efficiency': 0.15,
            'reproducibility': 0.10,
            'innovation': 0.10,
            'collaboration': 0.05
        }
        
        # Resource cost models (cost per unit per hour)
        self.resource_costs = {
            'cpu_core_hour': 0.10,
            'memory_gb_hour': 0.02,
            'gpu_core_hour': 2.50,
            'gpu_memory_gb_hour': 0.50,
            'storage_gb_hour': 0.001,
            'network_mbps_hour': 0.01
        }
    
    def calculate_composite_score(self, task: ScheduledTask) -> float:
        """Calculate multi-objective composite score for task prioritization"""
        pf = task.policy_factors
        
        # Individual objective scores
        objectives = {
            'plausibility': pf.plausibility_score,
            'ethics': pf.ethics_score,
            'risk': pf.risk_score,  # Will be minimized due to negative weight
            'scientific_impact': pf.scientific_impact,
            'cost_efficiency': pf.cost_efficiency,
            'reproducibility': pf.reproducibility_likelihood,
            'innovation': pf.innovation_potential,
            'collaboration': pf.collaboration_value
        }
        
        # Weighted sum with normalization
        composite = sum(self.weights[obj] * score for obj, score in objectives.items())
        
        # Apply priority boost
        priority_boost = {
            TaskPriority.CRITICAL: 0.3,
            TaskPriority.HIGH: 0.2,
            TaskPriority.NORMAL: 0.0,
            TaskPriority.LOW: -0.1
        }
        
        composite += priority_boost.get(task.priority, 0.0)
        
        # Normalize to [0, 1] range
        return max(0.0, min(1.0, (composite + 1.0) / 2.0))
    
    def calculate_cost_score(self, task: ScheduledTask) -> float:
        """Calculate estimated cost score for resource usage"""
        res = task.resources
        execution_hours = res.execution_time_minutes / 60.0
        
        cost_components = {
            'cpu': res.cpu_cores * execution_hours * self.resource_costs['cpu_core_hour'],
            'memory': res.memory_gb * execution_hours * self.resource_costs['memory_gb_hour'],
            'gpu': res.gpu_cores * execution_hours * self.resource_costs['gpu_core_hour'],
            'gpu_memory': res.gpu_memory_gb * execution_hours * self.resource_costs['gpu_memory_gb_hour'],
            'storage': res.storage_gb * execution_hours * self.resource_costs['storage_gb_hour'],
            'network': res.network_bandwidth_mbps * execution_hours * self.resource_costs['network_mbps_hour']
        }
        
        total_cost = sum(cost_components.values())
        
        # Convert to score (lower cost = higher score)
        # Using logarithmic scale to handle wide cost ranges
        cost_score = 1.0 / (1.0 + math.log10(max(0.01, total_cost)))
        
        return max(0.0, min(1.0, cost_score))
    
    def calculate_feasibility_score(self, task: ScheduledTask) -> float:
        """Calculate feasibility score based on resource availability and constraints"""
        # Mock resource availability check
        # In production, would check actual cluster resources
        
        res = task.resources
        feasibility_factors = []
        
        # CPU feasibility
        if res.cpu_cores <= 16:  # Max available CPU cores
            feasibility_factors.append(1.0)
        else:
            feasibility_factors.append(0.5)
        
        # Memory feasibility
        if res.memory_gb <= 64:  # Max available memory
            feasibility_factors.append(1.0)
        else:
            feasibility_factors.append(0.6)
        
        # GPU feasibility
        if res.gpu_cores == 0:
            feasibility_factors.append(1.0)  # No GPU needed
        elif res.gpu_cores <= 8:  # Max available GPU cores
            feasibility_factors.append(0.9)
        else:
            feasibility_factors.append(0.3)
        
        # Execution time feasibility
        if res.execution_time_minutes <= 60:
            feasibility_factors.append(1.0)
        elif res.execution_time_minutes <= 240:
            feasibility_factors.append(0.8)
        else:
            feasibility_factors.append(0.6)
        
        # Policy feasibility check
        policy_scores = {
            'plausibility': task.policy_factors.plausibility_score,
            'ethics': task.policy_factors.ethics_score,
            'reproducibility': task.policy_factors.reproducibility_likelihood
        }
        
        # Check against policy engine thresholds
        policy_decision = policy_engine_service.decide(policy_scores)
        if policy_decision['decision']['status'] == 'halt':
            feasibility_factors.append(0.0)  # Not feasible
        elif policy_decision['decision']['status'] == 'reject':
            feasibility_factors.append(0.2)  # Low feasibility
        else:
            feasibility_factors.append(1.0)  # Feasible
        
        return min(feasibility_factors) if feasibility_factors else 0.0

class PolicyAwareScheduler:
    """Policy-aware task scheduler with multi-objective optimization"""
    
    def __init__(self):
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue: List[tuple] = []  # Priority queue (negative_score, timestamp, task_id)
        self.running_tasks: Dict[str, ScheduledTask] = {}
        self.completed_tasks: Dict[str, ScheduledTask] = {}
        self.optimizer = MultiObjectiveOptimizer()
        
        # Resource tracking
        self.available_resources = ResourceRequirements(
            cpu_cores=16.0,
            memory_gb=64.0,
            gpu_cores=8.0,
            gpu_memory_gb=32.0,
            storage_gb=1000.0,
            network_bandwidth_mbps=1000.0
        )
        
        self.used_resources = ResourceRequirements()
        
        # Statistics
        self.stats = {
            'tasks_scheduled': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_cpu_hours': 0.0,
            'total_cost': 0.0,
            'avg_wait_time_minutes': 0.0
        }
        
        logger.info("Policy-aware scheduler initialized")
    
    async def start(self):
        """Start the policy-aware scheduler"""
        logger.info("🚀 Starting Policy-Aware Scheduler...")
        # Initialize background tasks, resource monitoring, etc.
        self.stats['scheduler_start_time'] = datetime.now().isoformat()
        logger.info("✅ Policy-Aware Scheduler started successfully")
    
    async def stop(self):
        """Stop the policy-aware scheduler"""
        logger.info("🛑 Stopping Policy-Aware Scheduler...")
        # Stop background tasks, save state, etc.
        self.stats['scheduler_stop_time'] = datetime.now().isoformat()
        logger.info("✅ Policy-Aware Scheduler stopped successfully")
    
    async def submit_task(self, task: ScheduledTask) -> str:
        """Submit a new task for scheduling"""
        
        # Calculate scores
        task.composite_score = self.optimizer.calculate_composite_score(task)
        task.cost_score = self.optimizer.calculate_cost_score(task)
        task.feasibility_score = self.optimizer.calculate_feasibility_score(task)
        
        # Check if task is feasible
        if task.feasibility_score < 0.1:
            task.status = TaskStatus.FAILED
            task.results['error'] = 'Task not feasible according to policy constraints'
            self.completed_tasks[task.task_id] = task
            logger.warning(f"Task {task.task_id} rejected as not feasible")
            return task.task_id
        
        # Add to queue with priority based on composite score
        task.status = TaskStatus.PENDING
        self.tasks[task.task_id] = task
        
        # Priority queue uses negative score for max-heap behavior
        priority = (-task.composite_score, time.time(), task.task_id)
        heapq.heappush(self.task_queue, priority)
        
        self.stats['tasks_scheduled'] += 1
        
        logger.info(f"Task {task.task_id} submitted with composite score {task.composite_score:.3f}")
        
        return task.task_id
    
    def can_allocate_resources(self, required: ResourceRequirements) -> bool:
        """Check if required resources are available"""
        return (
            self.used_resources.cpu_cores + required.cpu_cores <= self.available_resources.cpu_cores and
            self.used_resources.memory_gb + required.memory_gb <= self.available_resources.memory_gb and
            self.used_resources.gpu_cores + required.gpu_cores <= self.available_resources.gpu_cores and
            self.used_resources.gpu_memory_gb + required.gpu_memory_gb <= self.available_resources.gpu_memory_gb and
            self.used_resources.storage_gb + required.storage_gb <= self.available_resources.storage_gb
        )
    
    def allocate_resources(self, task: ScheduledTask):
        """Allocate resources for task execution"""
        res = task.resources
        self.used_resources.cpu_cores += res.cpu_cores
        self.used_resources.memory_gb += res.memory_gb
        self.used_resources.gpu_cores += res.gpu_cores
        self.used_resources.gpu_memory_gb += res.gpu_memory_gb
        self.used_resources.storage_gb += res.storage_gb
    
    def deallocate_resources(self, task: ScheduledTask):
        """Deallocate resources after task completion"""
        res = task.resources
        self.used_resources.cpu_cores -= res.cpu_cores
        self.used_resources.memory_gb -= res.memory_gb
        self.used_resources.gpu_cores -= res.gpu_cores
        self.used_resources.gpu_memory_gb -= res.gpu_memory_gb
        self.used_resources.storage_gb -= res.storage_gb
        
        # Ensure non-negative values
        self.used_resources.cpu_cores = max(0, self.used_resources.cpu_cores)
        self.used_resources.memory_gb = max(0, self.used_resources.memory_gb)
        self.used_resources.gpu_cores = max(0, self.used_resources.gpu_cores)
        self.used_resources.gpu_memory_gb = max(0, self.used_resources.gpu_memory_gb)
        self.used_resources.storage_gb = max(0, self.used_resources.storage_gb)
    
    async def schedule_next_task(self) -> Optional[ScheduledTask]:
        """Schedule the next highest-priority feasible task"""
        
        while self.task_queue:
            _, _, task_id = heapq.heappop(self.task_queue)
            
            if task_id not in self.tasks:
                continue  # Task was cancelled
            
            task = self.tasks[task_id]
            
            if task.status != TaskStatus.PENDING:
                continue  # Task already processed
            
            # Check dependencies
            if task.depends_on:
                deps_completed = all(
                    dep_id in self.completed_tasks and 
                    self.completed_tasks[dep_id].status == TaskStatus.COMPLETED
                    for dep_id in task.depends_on
                )
                if not deps_completed:
                    # Re-queue the task for later
                    priority = (-task.composite_score, time.time(), task_id)
                    heapq.heappush(self.task_queue, priority)
                    continue
            
            # Check resource availability
            if not self.can_allocate_resources(task.resources):
                # Re-queue the task for later
                priority = (-task.composite_score, time.time(), task_id)
                heapq.heappush(self.task_queue, priority)
                continue
            
            # Allocate resources and start task
            self.allocate_resources(task)
            task.status = TaskStatus.RUNNING
            task.scheduled_at = datetime.utcnow()
            task.started_at = datetime.utcnow()
            
            self.running_tasks[task_id] = task
            
            logger.info(f"Task {task_id} scheduled and started")
            
            return task
        
        return None
    
    async def execute_task(self, task: ScheduledTask) -> Dict[str, Any]:
        """Execute a scheduled task"""
        try:
            if task.executor:
                # Execute the actual task
                results = await task.executor(task.parameters)
                task.results.update(results)
                task.status = TaskStatus.COMPLETED
            else:
                # Mock execution
                await asyncio.sleep(min(5, task.resources.execution_time_minutes * 60 / 10))  # Accelerated for demo
                task.results = {
                    'status': 'completed',
                    'execution_time': task.resources.execution_time_minutes,
                    'resource_usage': task.resources.__dict__,
                    'mock_output': f'Executed {task.name} successfully'
                }
                task.status = TaskStatus.COMPLETED
            
            task.completed_at = datetime.utcnow()
            
            # Update statistics
            self.stats['tasks_completed'] += 1
            self.stats['total_cpu_hours'] += task.resources.cpu_cores * (task.resources.execution_time_minutes / 60.0)
            self.stats['total_cost'] += (1.0 - task.cost_score) * 100  # Mock cost calculation
            
            logger.info(f"Task {task.task_id} completed successfully")
            
        except LLMError as e:
            task.status = TaskStatus.FAILED
            task.results['error'] = str(e)
            task.completed_at = datetime.utcnow()
            
            self.stats['tasks_failed'] += 1
            
            logger.error(f"Task {task.task_id} failed: {e}")
        
        finally:
            # Deallocate resources
            self.deallocate_resources(task)
            
            # Move to completed tasks
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            
            self.completed_tasks[task.task_id] = task
        
        return task.results
    
    async def run_scheduler(self):
        """Main scheduler loop"""
        logger.info("Policy-aware scheduler started")
        
        while True:
            try:
                # Schedule next task if resources available
                task = await self.schedule_next_task()
                
                if task:
                    # Execute task asynchronously
                    asyncio.create_task(self.execute_task(task))
                
                # Small delay to prevent busy waiting
                await asyncio.sleep(1)
                
            except LLMError as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(5)  # Longer delay on error
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status and metrics"""
        return {
            'status': 'running',
            'queue_length': len(self.task_queue),
            'running_tasks': len(self.running_tasks),
            'completed_tasks': len(self.completed_tasks),
            'resource_utilization': {
                'cpu_percent': (self.used_resources.cpu_cores / self.available_resources.cpu_cores) * 100 if self.available_resources.cpu_cores > 0 else 0,
                'memory_percent': (self.used_resources.memory_gb / self.available_resources.memory_gb) * 100 if self.available_resources.memory_gb > 0 else 0,
                'gpu_percent': (self.used_resources.gpu_cores / self.available_resources.gpu_cores) * 100 if self.available_resources.gpu_cores > 0 else 0,
            },
            'statistics': self.stats,
            'optimizer_weights': self.optimizer.weights
        }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        if task_id in self.running_tasks:
            task = self.running_tasks[task_id]
        elif task_id in self.completed_tasks:
            task = self.completed_tasks[task_id]
        elif task_id in self.tasks:
            task = self.tasks[task_id]
        else:
            return None
        
        return {
            'task_id': task.task_id,
            'name': task.name,
            'status': task.status.value,
            'priority': task.priority.value,
            'composite_score': task.composite_score,
            'cost_score': task.cost_score,
            'feasibility_score': task.feasibility_score,
            'submitted_at': task.submitted_at.isoformat() if task.submitted_at else None,
            'scheduled_at': task.scheduled_at.isoformat() if task.scheduled_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'resources': task.resources.__dict__,
            'policy_factors': task.policy_factors.__dict__,
            'results': task.results
        }

# Global scheduler instance
scheduler = PolicyAwareScheduler()

def get_scheduler() -> PolicyAwareScheduler:
    """Get the global scheduler instance"""
    return scheduler
