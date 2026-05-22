"""
Tests for Unified Research Orchestrator Service
Tests the consolidated orchestration logic and service integration
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.services.unified_research_orchestrator import (
    UnifiedResearchOrchestrator,
    OrchestrationTask,
    OrchestrationResult,
    ResearchPhase,
    OrchestrationStrategy,
    get_unified_orchestrator
)


class MockService:
    """Mock service for testing orchestration"""
    
    def __init__(self, name: str, fail: bool = False, delay: float = 0.1):
        self.name = name
        self.fail = fail
        self.delay = delay
        
    async def process_request(self, request_data: dict):
        """Mock process_request method"""
        await asyncio.sleep(self.delay)
        
        if self.fail:
            raise RuntimeError(f"Mock service {self.name} failed")
        
        return {
            "success": True,
            "service": self.name,
            "action": request_data.get("action"),
            "data": request_data
        }


@pytest.fixture
def orchestrator():
    """Create orchestrator instance for testing"""
    return UnifiedResearchOrchestrator()


@pytest.fixture
def mock_services(orchestrator):
    """Setup mock services for testing"""
    services = {
        "test_service": MockService("test_service"),
        "slow_service": MockService("slow_service", delay=0.2),
        "failing_service": MockService("failing_service", fail=True)
    }
    
    for name, service in services.items():
        orchestrator.register_service(name, service)
    
    return services


@pytest.mark.asyncio
class TestUnifiedResearchOrchestrator:
    """Test suite for unified research orchestrator"""
    
    def test_service_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator.name == "UnifiedResearchOrchestrator"
        assert orchestrator.max_concurrent_tasks == 10
        assert orchestrator.default_timeout == 300
        assert orchestrator.enable_metrics is True
        assert len(orchestrator._service_registry) == 0
    
    def test_service_registration(self, orchestrator):
        """Test service registration"""
        mock_service = MockService("test")
        orchestrator.register_service("test", mock_service)
        
        assert "test" in orchestrator._service_registry
        assert orchestrator._service_registry["test"] == mock_service
    
    def test_task_validation(self, orchestrator, mock_services):
        """Test task validation logic"""
        # Valid task
        valid_task = OrchestrationTask(
            task_id="task1",
            task_type="test",
            service_name="test_service",
            operation="test_op",
            parameters={"key": "value"}
        )
        assert orchestrator.validate_task(valid_task) is True
        
        # Invalid task - missing service name
        invalid_task = OrchestrationTask(
            task_id="task2",
            task_type="test",
            service_name="",
            operation="test_op",
            parameters={}
        )
        assert orchestrator.validate_task(invalid_task) is False
        
        # Invalid task - unregistered service
        unregistered_task = OrchestrationTask(
            task_id="task3",
            task_type="test",
            service_name="nonexistent_service",
            operation="test_op",
            parameters={}
        )
        assert orchestrator.validate_task(unregistered_task) is False
    
    async def test_single_task_execution_success(self, orchestrator, mock_services):
        """Test successful single task execution"""
        task = OrchestrationTask(
            task_id="success_task",
            task_type="test",
            service_name="test_service",
            operation="test_action",
            parameters={"param": "value"},
            phase=ResearchPhase.HYPOTHESIS_GENERATION
        )
        
        result = await orchestrator.execute_task(task)
        
        assert result.success is True
        assert result.task_id == "success_task"
        assert result.result is not None
        assert result.result["success"] is True
        assert result.result["service"] == "test_service"
        assert result.error is None
        assert result.execution_time_sec > 0
        assert result.phase == ResearchPhase.HYPOTHESIS_GENERATION
    
    async def test_single_task_execution_failure(self, orchestrator, mock_services):
        """Test failed single task execution"""
        task = OrchestrationTask(
            task_id="fail_task",
            task_type="test",
            service_name="failing_service",
            operation="test_action",
            parameters={},
            phase=ResearchPhase.ANALYSIS
        )
        
        result = await orchestrator.execute_task(task)
        
        assert result.success is False
        assert result.task_id == "fail_task"
        assert result.result is None
        assert "Mock service failing_service failed" in result.error
        assert result.execution_time_sec > 0
        assert result.phase == ResearchPhase.ANALYSIS
    
    async def test_single_task_execution_timeout(self, orchestrator):
        """Test task execution timeout"""
        # Register a service that takes too long
        very_slow_service = MockService("very_slow_service", delay=2.0)
        orchestrator.register_service("very_slow_service", very_slow_service)
        
        task = OrchestrationTask(
            task_id="timeout_task",
            task_type="test",
            service_name="very_slow_service",
            operation="test_action",
            parameters={},
            timeout_sec=0.5  # Short timeout
        )
        
        result = await orchestrator.execute_task(task)
        
        assert result.success is False
        assert "timed out" in result.error
    
    async def test_sequential_workflow_execution(self, orchestrator, mock_services):
        """Test sequential workflow execution"""
        tasks = [
            OrchestrationTask(
                task_id="task1",
                task_type="test",
                service_name="test_service",
                operation="action1",
                parameters={"step": 1}
            ),
            OrchestrationTask(
                task_id="task2",
                task_type="test",
                service_name="slow_service",
                operation="action2",
                parameters={"step": 2},
                dependencies=["task1"]
            ),
            OrchestrationTask(
                task_id="task3",
                task_type="test",
                service_name="test_service",
                operation="action3",
                parameters={"step": 3},
                dependencies=["task2"]
            )
        ]
        
        results = await orchestrator.execute_workflow(tasks, OrchestrationStrategy.SEQUENTIAL)
        
        assert len(results) == 3
        assert all(result.success for result in results)
        assert results[0].task_id == "task1"
        assert results[1].task_id == "task2"
        assert results[2].task_id == "task3"
    
    async def test_sequential_workflow_with_failure(self, orchestrator, mock_services):
        """Test sequential workflow with failure propagation"""
        tasks = [
            OrchestrationTask(
                task_id="task1",
                task_type="test",
                service_name="test_service",
                operation="action1",
                parameters={}
            ),
            OrchestrationTask(
                task_id="task2_fail",
                task_type="test",
                service_name="failing_service",
                operation="action2",
                parameters={},
                dependencies=["task1"]
            ),
            OrchestrationTask(
                task_id="task3",
                task_type="test",
                service_name="test_service",
                operation="action3",
                parameters={},
                dependencies=["task2_fail"]
            )
        ]
        
        results = await orchestrator.execute_workflow(tasks, OrchestrationStrategy.SEQUENTIAL)
        
        assert len(results) == 3
        assert results[0].success is True  # task1 succeeds
        assert results[1].success is False  # task2_fail fails
        assert results[2].success is False  # task3 fails due to dependency
        assert "Dependencies failed" in results[2].error
    
    async def test_parallel_workflow_execution(self, orchestrator, mock_services):
        """Test parallel workflow execution"""
        tasks = [
            OrchestrationTask(
                task_id="parallel1",
                task_type="test",
                service_name="test_service",
                operation="action1",
                parameters={}
            ),
            OrchestrationTask(
                task_id="parallel2",
                task_type="test",
                service_name="slow_service",
                operation="action2",
                parameters={}
            ),
            OrchestrationTask(
                task_id="parallel3",
                task_type="test",
                service_name="test_service",
                operation="action3",
                parameters={}
            )
        ]
        
        start_time = datetime.now()
        results = await orchestrator.execute_workflow(tasks, OrchestrationStrategy.PARALLEL)
        end_time = datetime.now()
        
        # Should complete faster than sequential execution
        execution_time = (end_time - start_time).total_seconds()
        assert execution_time < 0.5  # Should be much faster than 0.6s (3 * 0.2s)
        
        assert len(results) == 3
        assert all(result.success for result in results)
    
    async def test_dependency_resolution(self, orchestrator):
        """Test dependency resolution algorithm"""
        tasks = [
            OrchestrationTask(
                task_id="C",
                task_type="test",
                service_name="test_service",
                operation="actionC",
                parameters={},
                dependencies=["A", "B"]
            ),
            OrchestrationTask(
                task_id="A",
                task_type="test",
                service_name="test_service",
                operation="actionA",
                parameters={}
            ),
            OrchestrationTask(
                task_id="B",
                task_type="test",
                service_name="test_service",
                operation="actionB",
                parameters={},
                dependencies=["A"]
            )
        ]
        
        execution_order = orchestrator._resolve_dependencies(tasks)
        
        # Should be: A first, then B, then C
        assert execution_order[0] == "A"
        assert execution_order[1] == "B"
        assert execution_order[2] == "C"
    
    async def test_adaptive_strategy_simple_dependencies(self, orchestrator, mock_services):
        """Test adaptive strategy with simple dependencies"""
        tasks = [
            OrchestrationTask(
                task_id="independent1",
                task_type="test",
                service_name="test_service",
                operation="action1",
                parameters={}
            ),
            OrchestrationTask(
                task_id="independent2",
                task_type="test",
                service_name="test_service",
                operation="action2",
                parameters={}
            )
        ]
        
        with patch.object(orchestrator, '_execute_parallel', new_callable=AsyncMock) as mock_parallel:
            mock_parallel.return_value = []
            
            await orchestrator.execute_workflow(tasks, OrchestrationStrategy.ADAPTIVE)
            
            # Should choose parallel strategy for independent tasks
            mock_parallel.assert_called_once()
    
    async def test_adaptive_strategy_complex_dependencies(self, orchestrator, mock_services):
        """Test adaptive strategy with complex dependencies"""
        tasks = [
            OrchestrationTask(
                task_id="task1",
                task_type="test",
                service_name="test_service",
                operation="action1",
                parameters={},
                dependencies=["task2", "task3"]
            ),
            OrchestrationTask(
                task_id="task2",
                task_type="test",
                service_name="test_service",
                operation="action2",
                parameters={},
                dependencies=["task3"]
            ),
            OrchestrationTask(
                task_id="task3",
                task_type="test",
                service_name="test_service",
                operation="action3",
                parameters={}
            )
        ]
        
        with patch.object(orchestrator, '_execute_sequential', new_callable=AsyncMock) as mock_sequential:
            mock_sequential.return_value = []
            
            await orchestrator.execute_workflow(tasks, OrchestrationStrategy.ADAPTIVE)
            
            # Should choose sequential strategy for complex dependencies
            mock_sequential.assert_called_once()
    
    def test_performance_metrics_tracking(self, orchestrator, mock_services):
        """Test performance metrics tracking"""
        # Simulate some task executions
        task1 = OrchestrationTask(
            task_id="perf1",
            task_type="test",
            service_name="test_service",
            operation="test_op",
            parameters={}
        )
        
        # Simulate performance updates
        orchestrator._update_performance_metrics(task1, 0.5, True)
        orchestrator._update_performance_metrics(task1, 0.3, True)
        orchestrator._update_performance_metrics(task1, 0.7, False)
        
        metrics = orchestrator.get_performance_metrics()
        
        assert "task_performance" in metrics
        assert "test_service.test_op" in metrics["task_performance"]
        
        task_metrics = metrics["task_performance"]["test_service.test_op"]
        assert task_metrics["avg_execution_time"] == 0.5  # (0.5 + 0.3 + 0.7) / 3
        assert task_metrics["success_rate"] == 2/3  # 2 successes out of 3
        assert task_metrics["total_executions"] == 3
    
    async def test_process_request_execute_task(self, orchestrator, mock_services):
        """Test process_request for single task execution"""
        request_data = {
            "action": "execute_task",
            "task": {
                "task_id": "req_task1",
                "service_name": "test_service",
                "operation": "test_action",
                "parameters": {"key": "value"},
                "phase": "hypothesis_generation"
            }
        }
        
        result = await orchestrator.process_request(request_data)
        
        assert result["success"] is True
        assert result["result"]["success"] is True
        assert result["result"]["service"] == "test_service"
    
    async def test_process_request_execute_workflow(self, orchestrator, mock_services):
        """Test process_request for workflow execution"""
        request_data = {
            "action": "execute_workflow",
            "strategy": "sequential",
            "tasks": [
                {
                    "task_id": "wf_task1",
                    "service_name": "test_service",
                    "operation": "action1",
                    "parameters": {}
                },
                {
                    "task_id": "wf_task2",
                    "service_name": "test_service",
                    "operation": "action2",
                    "parameters": {},
                    "dependencies": ["wf_task1"]
                }
            ]
        }
        
        result = await orchestrator.process_request(request_data)
        
        assert result["success"] is True
        assert len(result["results"]) == 2
        assert all(res["success"] for res in result["results"])
    
    async def test_process_request_get_metrics(self, orchestrator):
        """Test process_request for getting metrics"""
        request_data = {"action": "get_performance_metrics"}
        
        result = await orchestrator.process_request(request_data)
        
        assert result["success"] is True
        assert "metrics" in result
        assert "total_tasks_executed" in result["metrics"]
        assert "registered_services" in result["metrics"]
    
    async def test_process_request_unknown_action(self, orchestrator):
        """Test process_request with unknown action"""
        request_data = {"action": "unknown_action"}
        
        result = await orchestrator.process_request(request_data)
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
        assert "available_actions" in result
    
    def test_global_singleton(self):
        """Test global singleton functionality"""
        orchestrator1 = get_unified_orchestrator()
        orchestrator2 = get_unified_orchestrator()
        
        # Should be the same instance
        assert orchestrator1 is orchestrator2
        assert isinstance(orchestrator1, UnifiedResearchOrchestrator)
    
    @patch('app.services.unified_research_orchestrator.get_current_trace_id')
    @patch('app.services.unified_research_orchestrator.log_decision_event')
    async def test_tracing_integration(self, mock_log, mock_trace, orchestrator, mock_services):
        """Test trace ID propagation and decision logging"""
        mock_trace.return_value = "test-trace-123"
        
        task = OrchestrationTask(
            task_id="trace_task",
            task_type="test",
            service_name="test_service",
            operation="test_action",
            parameters={},
            phase=ResearchPhase.EXECUTION
        )
        
        result = await orchestrator.execute_task(task)
        
        # Should call log_decision_event twice (start and completion)
        assert mock_log.call_count == 2
        
        # Check start event
        start_call = mock_log.call_args_list[0]
        assert start_call[1]["event_type"] == "task_execution_started"
        assert start_call[1]["trace_id"] == "test-trace-123"
        
        # Check completion event
        completion_call = mock_log.call_args_list[1]
        assert completion_call[1]["event_type"] == "task_execution_completed"
        assert completion_call[1]["trace_id"] == "test-trace-123"
