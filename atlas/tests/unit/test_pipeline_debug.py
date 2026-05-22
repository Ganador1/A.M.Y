#!/usr/bin/env python3
"""Debug script for pipeline testing"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.master_orchestration_service import MasterOrchestrationService, PipelineStatus
from unittest.mock import AsyncMock, MagicMock


class TestMasterOrchestrationService(MasterOrchestrationService):
    """Test version that doesn't start background tasks automatically"""
    
    def __init__(self, config=None):
        # Call parent constructor but prevent background task startup
        config = config or {}
        super().__init__(config)
        # Don't start background tasks in tests
        self.background_tasks_started = False


def create_mock_services():
    """Create mock services for testing"""
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


async def test_pipeline_creation():
    """Test pipeline creation and execution"""
    print("Testing pipeline creation...")
    
    # Create service instance
    service = TestMasterOrchestrationService()
    
    # Add mock services
    mock_services = create_mock_services()
    service.services = mock_services
    
    try:
        # Test create_autonomous_pipeline
        print("Creating autonomous pipeline...")
        pipeline_id = await service.create_autonomous_pipeline(
            'Test research question', 'materials_science', 'comprehensive_research', {}
        )
        
        print(f"Pipeline created with ID: {pipeline_id}")
        print(f"Active pipelines count: {len(service.active_pipelines)}")
        
        # Check if pipeline is in active_pipelines
        pipeline = service.active_pipelines.get(pipeline_id)
        if pipeline:
            print(f"✓ Pipeline found in active_pipelines: {pipeline.id}")
            print(f"  Pipeline name: {pipeline.name}")
            print(f"  Pipeline status: {pipeline.status}")
            print(f"  Number of tasks: {len(pipeline.tasks)}")
        else:
            print("✗ Pipeline NOT found in active_pipelines")
            print("Available pipeline IDs:", list(service.active_pipelines.keys()))
            return False
        
        # Wait a bit for execution to start
        print("Waiting for pipeline execution...")
        await asyncio.sleep(0.5)
        
        # Check pipeline status
        pipeline = service.active_pipelines.get(pipeline_id)
        if pipeline:
            print(f"Pipeline status after execution: {pipeline.status}")
            print(f"Success rate: {pipeline.success_rate}")
        else:
            print("Pipeline moved to history")
            # Check if it's in history
            if service.pipeline_history:
                last_pipeline = service.pipeline_history[-1]
                print(f"Last pipeline in history: {last_pipeline.id} - {last_pipeline.status}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function"""
    print("=== Pipeline Debug Test ===")
    
    success = await test_pipeline_creation()
    
    if success:
        print("\n✓ Test completed successfully!")
    else:
        print("\n✗ Test failed!")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)