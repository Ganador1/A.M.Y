"""Performance tests for autonomous research pipelines"""

import asyncio
import time
from typing import Dict, Optional
import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.master_orchestration_service import MasterOrchestrationService, PipelineStatus


class TestMasterOrchestrationService(MasterOrchestrationService):
    """Test version that doesn't start background tasks automatically"""
    
    def __init__(self):
        # Call parent constructor with empty config to prevent background task startup
        super().__init__({})
        # Don't start background tasks in tests
        self.background_tasks_started = False


class TestPipelinePerformance:
    """Performance testing for research pipelines"""
    
    @pytest.fixture
    def mock_services(self):
        """Mock services for performance testing"""
        services = {
            'literature': MagicMock(),
            'scientific_ai': MagicMock(),
            'ai_scientist': MagicMock(),
            'code_scientist': MagicMock(),
            'research_orchestrator': MagicMock(),
            'automl': MagicMock()
        }
        
        # Mock methods with realistic response times
        services['literature'].comprehensive_search = AsyncMock()
        services['literature'].comprehensive_search.return_value = {
            'results': [{'title': f'Paper {i}', 'abstract': f'Abstract {i}'} for i in range(50)],
            'total_count': 50
        }
        
        services['scientific_ai'].scientific_reasoning_workflow = AsyncMock()
        services['scientific_ai'].scientific_reasoning_workflow.return_value = {
            'reasoning_steps': ['step1', 'step2', 'step3'],
            'conclusions': ['conclusion1', 'conclusion2'],
            'confidence': 0.85
        }
        
        services['ai_scientist'].generate_research_hypothesis = AsyncMock()
        services['ai_scientist'].generate_research_hypothesis.return_value = {
            'hypothesis': 'Test hypothesis',
            'confidence': 0.9,
            'methodology': 'Experimental design'
        }
        
        services['code_scientist'].analyze_research_patterns = AsyncMock()
        services['code_scientist'].analyze_research_patterns.return_value = {
            'patterns': ['pattern1', 'pattern2'],
            'recommendations': ['recommendation1', 'recommendation2']
        }
        
        services['research_orchestrator'].orchestrate_research_cycle = AsyncMock()
        services['research_orchestrator'].orchestrate_research_cycle.return_value = {
            'research_plan': 'Complete plan',
            'timeline': '2 weeks',
            'resources': ['resource1', 'resource2']
        }
        
        services['automl'].optimize_research_pipeline = AsyncMock()
        services['automl'].optimize_research_pipeline.return_value = {
            'optimizations': ['opt1', 'opt2'],
            'performance_gain': 0.25
        }
        
        return services
    
    @pytest.fixture
    def orchestration_service(self, mock_services):
        """Orchestration service with mocked services"""
        service = TestMasterOrchestrationService()
        service.services = mock_services
        return service
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_comprehensive_research_pipeline_performance(self, orchestration_service):
        """Test performance of comprehensive research pipeline"""
        
        # Create and start pipeline using the proper method
        research_question = "Test research question"
        domain = "materials_science"
        
        # Start timing
        start_time = time.time()
        
        # Create and start pipeline (this automatically adds to active_pipelines and starts execution)
        pipeline_id = await orchestration_service.create_autonomous_pipeline(
            research_question, domain, "comprehensive_research", {}
        )
        
        # Wait for pipeline completion
        pipeline = orchestration_service.active_pipelines.get(pipeline_id)
        while pipeline and pipeline.status not in [PipelineStatus.COMPLETED, PipelineStatus.FAILED, PipelineStatus.CANCELLED]:
            await asyncio.sleep(0.1)
            pipeline = orchestration_service.active_pipelines.get(pipeline_id)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Assert performance metrics
        assert execution_time < 300  # Should complete within 5 minutes
        assert pipeline.status == PipelineStatus.COMPLETED
        assert pipeline.success_rate >= 0.8  # At least 80% success rate
        
        print(f"Comprehensive research pipeline completed in {execution_time:.2f} seconds")
        print(f"Success rate: {pipeline.success_rate:.2%}")
        print(f"Total tasks: {len(pipeline.tasks)}")
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_advanced_scientific_research_pipeline_performance(self, orchestration_service):
        """Test performance of advanced scientific research pipeline"""
        
        # Create and start pipeline using the proper method
        research_question = "Advanced test research question"
        domain = "biochemistry"
        
        # Start timing
        start_time = time.time()
        
        # Create and start pipeline (this automatically adds to active_pipelines and starts execution)
        pipeline_id = await orchestration_service.create_autonomous_pipeline(
            research_question, domain, "advanced_scientific_research", {}
        )
        
        # Wait for pipeline completion
        pipeline = orchestration_service.active_pipelines.get(pipeline_id)
        while pipeline and pipeline.status not in [PipelineStatus.COMPLETED, PipelineStatus.FAILED, PipelineStatus.CANCELLED]:
            await asyncio.sleep(0.1)
            pipeline = orchestration_service.active_pipelines.get(pipeline_id)
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Assert performance metrics
        assert execution_time < 600  # Should complete within 10 minutes
        assert pipeline.status == PipelineStatus.COMPLETED
        assert pipeline.success_rate >= 0.7  # At least 70% success rate
        
        print(f"Advanced scientific research pipeline completed in {execution_time:.2f} seconds")
        print(f"Success rate: {pipeline.success_rate:.2%}")
        print(f"Total tasks: {len(pipeline.tasks)}")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "-m", "performance"])