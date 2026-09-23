"""
Integration tests for Agent 2 Bridge functionality

Tests the complete integration of the bridge service and router with the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import json

from app.main import app
from app.services.agent2_bridge_service import (
    DataIngestionRequest,
    DataIngestionResponse,
    Agent2ServiceStatus,
    DatasetFormat
)


@pytest.fixture
def test_client():
    """Fixture to create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_bridge_service():
    """Fixture to mock the bridge service for integration tests"""
    with patch('app.routers.agent2_bridge_router.agent2_bridge_service') as mock_service:
        # Mock service methods
        mock_service.initialize = AsyncMock()
        mock_service.discover_services = AsyncMock(return_value={
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
        })
        mock_service.ingest_dataset = AsyncMock(return_value=DataIngestionResponse(
            success=True,
            dataset_id="test_dataset_001",
            message="Dataset ingested successfully",
            storage_location="storage_key_001",
            validation_errors=[],
            transformed_sample={"key": "value"}
        ))
        mock_service.check_service_health = AsyncMock(return_value=Agent2ServiceStatus(
            name="neuro-simulation",
            available=True,
            endpoint="/api/neuro-sim",
            health_status="healthy",
            last_checked="2025-01-20T00:00:00Z"
        ))
        mock_service.stream_data = AsyncMock(return_value={
            "data": [1, 2, 3, 4, 5],
            "timestamp": "2025-01-20T00:00:00Z"
        })
        mock_service.execute_cross_agent_workflow = AsyncMock(return_value={
            "workflow_id": "workflow_001",
            "overall_status": "completed",
            "steps": [
                {
                    "service": "neuro-simulation",
                    "status": "success",
                    "result": {"data": [1, 2, 3]}
                }
            ]
        })
        
        yield mock_service


@pytest.mark.asyncio
async def test_bridge_health_endpoint(test_client):
    """Test the bridge health endpoint"""
    response = test_client.get("/api/agent2-bridge/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agent2_bridge"


@pytest.mark.asyncio
async def test_get_available_services(test_client, mock_bridge_service):
    """Test the services discovery endpoint"""
    response = test_client.get("/api/agent2-bridge/services")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "neuro-simulation" in data
    assert "cloud-lab" in data
    assert data["neuro-simulation"]["available"] is True
    assert data["neuro-simulation"]["health_status"] == "healthy"


@pytest.mark.asyncio
async def test_ingest_dataset_endpoint(test_client, mock_bridge_service):
    """Test the dataset ingestion endpoint"""
    ingestion_request = {
        "dataset_id": "test_dataset_001",
        "source_service": "neuro-simulation",
        "dataset_format": "JSON",
        "transformation_config": {
            "normalize_types": True,
            "validate_schema": True,
            "remove_duplicates": True
        },
        "metadata": {
            "description": "Test dataset",
            "domain": "neuroscience"
        }
    }
    
    response = test_client.post("/api/agent2-bridge/ingest", json=ingestion_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["success"] is True
    assert data["dataset_id"] == "test_dataset_001"
    assert data["storage_location"] == "storage_key_001"
    assert len(data["validation_errors"]) == 0


@pytest.mark.asyncio
async def test_ingest_dataset_async_endpoint(test_client, mock_bridge_service):
    """Test the async dataset ingestion endpoint"""
    ingestion_request = {
        "dataset_id": "test_dataset_001",
        "source_service": "neuro-simulation",
        "dataset_format": "JSON"
    }
    
    response = test_client.post("/api/agent2-bridge/ingest/async", json=ingestion_request)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "task_id" in data
    assert data["status"] == "completed"


@pytest.mark.asyncio
async def test_ingest_dataset_validation_failure(test_client, mock_bridge_service):
    """Test ingestion endpoint with validation failure"""
    # Mock service to return validation failure
    mock_bridge_service.ingest_dataset.return_value = DataIngestionResponse(
        success=False,
        dataset_id="test_dataset_001",
        message="Validation failed",
        storage_location=None,
        validation_errors=[
            "Missing required field: timestamp",
            "Invalid data type for field: value"
        ],
        transformed_sample={"key": "value"}
    )
    
    ingestion_request = {
        "dataset_id": "test_dataset_001",
        "source_service": "neuro-simulation",
        "dataset_format": "JSON"
    }
    
    response = test_client.post("/api/agent2-bridge/ingest", json=ingestion_request)
    
    assert response.status_code == 400
    data = response.json()
    
    assert "detail" in data
    assert "message" in data["detail"]
    assert "validation_errors" in data["detail"]
    assert len(data["detail"]["validation_errors"]) == 2


@pytest.mark.asyncio
async def test_stream_data_endpoint(test_client, mock_bridge_service):
    """Test the data streaming endpoint"""
    stream_params = {
        "param": "value",
        "limit": 10
    }
    
    response = test_client.post("/api/agent2-bridge/stream/neuro-simulation", json=stream_params)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "service" in data
    assert "data" in data
    assert "timestamp" in data
    assert data["service"] == "neuro-simulation"
    assert len(data["data"]) == 5


@pytest.mark.asyncio
async def test_stream_data_service_not_found(test_client, mock_bridge_service):
    """Test streaming endpoint for unknown service"""
    # Mock service to raise ValueError for unknown service
    mock_bridge_service.stream_data.side_effect = ValueError("Service not found: unknown-service")
    
    stream_params = {"param": "value"}
    
    response = test_client.post("/api/agent2-bridge/stream/unknown-service", json=stream_params)
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert "Service not found" in data["detail"]


@pytest.mark.asyncio
async def test_execute_workflow_endpoint(test_client, mock_bridge_service):
    """Test the workflow execution endpoint"""
    workflow_config = {
        "name": "test_workflow",
        "steps": [
            {
                "service": "neuro-simulation",
                "operation": "generate_data",
                "params": {"size": 100}
            }
        ]
    }
    
    response = test_client.post("/api/agent2-bridge/workflow/execute", json=workflow_config)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "workflow_id" in data
    assert "overall_status" in data
    assert "steps" in data
    assert data["overall_status"] == "completed"
    assert len(data["steps"]) == 1


@pytest.mark.asyncio
async def test_check_service_health_endpoint(test_client, mock_bridge_service):
    """Test the service health check endpoint"""
    response = test_client.get("/api/agent2-bridge/services/neuro-simulation/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "neuro-simulation"
    assert data["available"] is True
    assert data["health_status"] == "healthy"
    assert data["endpoint"] == "/api/neuro-sim"


@pytest.mark.asyncio
async def test_check_service_health_not_found(test_client, mock_bridge_service):
    """Test health check for unknown service"""
    response = test_client.get("/api/agent2-bridge/services/unknown-service/health")
    
    assert response.status_code == 404
    data = response.json()
    
    assert "detail" in data
    assert "Service not found" in data["detail"]


@pytest.mark.asyncio
async def test_ingest_dataset_invalid_request(test_client):
    """Test ingestion endpoint with invalid request data"""
    # Missing required fields
    invalid_request = {
        "source_service": "neuro-simulation"
        # Missing dataset_id and dataset_format
    }
    
    response = test_client.post("/api/agent2-bridge/ingest", json=invalid_request)
    
    # Should return 422 Unprocessable Entity for validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_cors_headers(test_client):
    """Test that CORS headers are properly set for bridge endpoints"""
    response = test_client.options("/api/agent2-bridge/health")
    
    # Should include CORS headers
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers


@pytest.mark.asyncio
async def test_bridge_endpoints_documentation(test_client):
    """Test that bridge endpoints are properly documented in OpenAPI"""
    # Get OpenAPI schema
    response = test_client.get("/openapi.json")
    
    assert response.status_code == 200
    openapi_schema = response.json()
    
    # Check that bridge endpoints are documented
    paths = openapi_schema["paths"]
    
    assert "/api/agent2-bridge/health" in paths
    assert "/api/agent2-bridge/services" in paths
    assert "/api/agent2-bridge/ingest" in paths
    assert "/api/agent2-bridge/stream/{service_name}" in paths
    assert "/api/agent2-bridge/workflow/execute" in paths
    
    # Check tags
    assert any(tag["name"] == "Agent 2 Bridge" for tag in openapi_schema["tags"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])