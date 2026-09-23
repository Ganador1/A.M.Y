"""
Unit tests for Agent2BridgeService

Tests the bridge service functionality for communication between Agent 2 and Agent 3.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
from fastapi import HTTPException

from app.services.agent2_bridge_service import (
    Agent2BridgeService,
    DataIngestionRequest,
    DataIngestionResponse,
    Agent2ServiceStatus,
    DatasetFormat,
    DataTransformationConfig
)


@pytest.fixture
def bridge_service():
    """Fixture to create a fresh bridge service instance for testing"""
    service = Agent2BridgeService()
    return service


@pytest.fixture
def mock_ingestion_request():
    """Fixture for a sample ingestion request"""
    return DataIngestionRequest(
        dataset_id="test_dataset_001",
        source_service="neuro-simulation",
        dataset_format=DatasetFormat.JSON,
        transformation_config=DataTransformationConfig(
            normalize_types=True,
            validate_schema=True,
            remove_duplicates=True
        ),
        metadata={
            "description": "Test dataset for unit testing",
            "domain": "neuroscience",
            "size": 1000
        }
    )


@pytest.mark.asyncio
async def test_initialize_service(bridge_service):
    """Test service initialization"""
    await bridge_service.initialize()
    
    # Service should be initialized
    assert bridge_service.initialized is True
    assert bridge_service.service_discovery is not None


@pytest.mark.asyncio
async def test_discover_services(bridge_service):
    """Test service discovery functionality"""
    await bridge_service.initialize()
    
    # Mock the service discovery
    with patch.object(bridge_service.service_discovery, 'discover_services', 
                     AsyncMock(return_value={
                         "neuro-simulation": Agent2ServiceStatus(
                             name="neuro-simulation",
                             available=True,
                             endpoint="/api/neuro-sim",
                             health_status="healthy",
                             last_checked="2025-01-20T00:00:00Z"
                         ),
                         "cloud-lab": Agent2ServiceStatus(
                             name="cloud-lab",
                             available=True,
                             endpoint="/api/cloud-lab",
                             health_status="healthy",
                             last_checked="2025-01-20T00:00:00Z"
                         )
                     })):
        
        services = await bridge_service.discover_services()
        
        assert len(services) == 2
        assert "neuro-simulation" in services
        assert "cloud-lab" in services
        assert services["neuro-simulation"].available is True


@pytest.mark.asyncio
async def test_ingest_dataset_success(bridge_service, mock_ingestion_request):
    """Test successful dataset ingestion"""
    await bridge_service.initialize()
    
    # Mock the data transformation and validation
    with patch.object(bridge_service, '_transform_dataset', AsyncMock(return_value={"transformed": "data"})), \
         patch.object(bridge_service, '_validate_dataset', AsyncMock(return_value=[])), \
         patch.object(bridge_service, '_store_dataset', AsyncMock(return_value="storage_key_001")):
        
        response = await bridge_service.ingest_dataset(mock_ingestion_request)
        
        assert response.success is True
        assert response.dataset_id == "test_dataset_001"
        assert response.storage_location == "storage_key_001"
        assert len(response.validation_errors) == 0


@pytest.mark.asyncio
async def test_ingest_dataset_validation_failure(bridge_service, mock_ingestion_request):
    """Test dataset ingestion with validation failures"""
    await bridge_service.initialize()
    
    # Mock validation to return errors
    validation_errors = [
        "Missing required field: timestamp",
        "Invalid data type for field: value (expected number, got string)"
    ]
    
    with patch.object(bridge_service, '_transform_dataset', AsyncMock(return_value={"invalid": "data"})), \
         patch.object(bridge_service, '_validate_dataset', AsyncMock(return_value=validation_errors)):
        
        response = await bridge_service.ingest_dataset(mock_ingestion_request)
        
        assert response.success is False
        assert response.dataset_id == "test_dataset_001"
        assert len(response.validation_errors) == 2
        assert "Missing required field" in response.validation_errors[0]


@pytest.mark.asyncio
async def test_check_service_health_success(bridge_service):
    """Test successful service health check"""
    await bridge_service.initialize()
    
    # Mock HTTP client to return successful response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy", "timestamp": "2025-01-20T00:00:00Z"}
    
    with patch('app.services.agent2_bridge_service.httpx.AsyncClient.get', 
              AsyncMock(return_value=mock_response)):
        
        status = await bridge_service.check_service_health("neuro-simulation", "/api/neuro-sim/health")
        
        assert status.available is True
        assert status.health_status == "healthy"


@pytest.mark.asyncio
async def test_check_service_health_failure(bridge_service):
    """Test service health check with failure"""
    await bridge_service.initialize()
    
    # Mock HTTP client to return error response
    with patch('app.services.agent2_bridge_service.httpx.AsyncClient.get', 
              AsyncMock(side_effect=Exception("Connection failed"))):
        
        status = await bridge_service.check_service_health("neuro-simulation", "/api/neuro-sim/health")
        
        assert status.available is False
        assert status.health_status == "unavailable"
        assert "Connection failed" in status.last_error


@pytest.mark.asyncio
async def test_stream_data_success(bridge_service):
    """Test successful data streaming"""
    await bridge_service.initialize()
    
    # Mock streaming endpoint
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [1, 2, 3, 4, 5],
        "timestamp": "2025-01-20T00:00:00Z"
    }
    
    with patch('app.services.agent2_bridge_service.httpx.AsyncClient.get', 
              AsyncMock(return_value=mock_response)):
        
        data = await bridge_service.stream_data("neuro-simulation", {"param": "value"})
        
        assert "data" in data
        assert "timestamp" in data
        assert len(data["data"]) == 5


@pytest.mark.asyncio
async def test_stream_data_service_not_found(bridge_service):
    """Test data streaming for unknown service"""
    await bridge_service.initialize()
    
    with pytest.raises(ValueError, match="Service not found"):
        await bridge_service.stream_data("unknown-service", {"param": "value"})


@pytest.mark.asyncio
async def test_execute_cross_agent_workflow(bridge_service):
    """Test cross-agent workflow execution"""
    await bridge_service.initialize()
    
    workflow_config = {
        "name": "test_workflow",
        "steps": [
            {
                "service": "neuro-simulation",
                "operation": "generate_data",
                "params": {"size": 100}
            },
            {
                "service": "ai-scientist",
                "operation": "analyze_data",
                "params": {"method": "statistical"}
            }
        ]
    }
    
    # Mock the individual service calls
    mock_neuro_response = {"data": [1, 2, 3], "status": "success"}
    mock_ai_response = {"analysis": "completed", "results": {"mean": 2.0}}
    
    with patch.object(bridge_service, 'stream_data', 
                     AsyncMock(side_effect=[mock_neuro_response, mock_ai_response])):
        
        results = await bridge_service.execute_cross_agent_workflow(workflow_config)
        
        assert len(results["steps"]) == 2
        assert results["steps"][0]["service"] == "neuro-simulation"
        assert results["steps"][1]["service"] == "ai-scientist"
        assert results["overall_status"] == "completed"


@pytest.mark.asyncio
async def test_execute_workflow_with_failure(bridge_service):
    """Test workflow execution with step failure"""
    await bridge_service.initialize()
    
    workflow_config = {
        "name": "test_workflow_failure",
        "steps": [
            {
                "service": "neuro-simulation",
                "operation": "generate_data",
                "params": {"size": 100}
            }
        ]
    }
    
    # Mock service failure
    with patch.object(bridge_service, 'stream_data', 
                     AsyncMock(side_effect=Exception("Service unavailable"))):
        
        results = await bridge_service.execute_cross_agent_workflow(workflow_config)
        
        assert results["overall_status"] == "failed"
        assert "Service unavailable" in results["error"]


def test_data_ingestion_request_validation():
    """Test DataIngestionRequest validation"""
    # Valid request
    valid_request = DataIngestionRequest(
        dataset_id="test_001",
        source_service="neuro-simulation",
        dataset_format=DatasetFormat.JSON
    )
    assert valid_request.dataset_id == "test_001"
    
    # Invalid request - missing required fields
    with pytest.raises(ValueError):
        DataIngestionRequest(
            dataset_id="",  # Empty string should raise validation error
            source_service="neuro-simulation",
            dataset_format=DatasetFormat.JSON
        )


def test_agent2_service_status_serialization():
    """Test Agent2ServiceStatus serialization"""
    status = Agent2ServiceStatus(
        name="test-service",
        available=True,
        endpoint="/api/test",
        health_status="healthy",
        last_checked="2025-01-20T00:00:00Z"
    )
    
    # Should serialize to dict correctly
    status_dict = status.dict()
    assert status_dict["name"] == "test-service"
    assert status_dict["available"] is True
    assert status_dict["health_status"] == "healthy"


@pytest.mark.asyncio
async def test_service_initialization_with_retry(bridge_service):
    """Test service initialization with retry mechanism"""
    # Mock service discovery to fail first time, then succeed
    mock_discovery = AsyncMock()
    mock_discovery.discover_services.side_effect = [
        Exception("First attempt failed"),
        {"test-service": Agent2ServiceStatus(
            name="test-service",
            available=True,
            endpoint="/api/test",
            health_status="healthy"
        )}
    ]
    
    bridge_service.service_discovery = mock_discovery
    
    # Should succeed on retry
    services = await bridge_service.discover_services()
    assert len(services) == 1
    assert "test-service" in services


if __name__ == "__main__":
    pytest.main([__file__, "-v"])