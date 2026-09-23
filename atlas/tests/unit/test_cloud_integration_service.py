#!/usr/bin/env python3
"""
AXIOM Cloud Integration Service - Unit Tests
Comprehensive testing for multi-cloud deployment capabilities

Author: AXIOM Autonomous Laboratory System
Date: September 13, 2025
"""

import pytest
from unittest.mock import patch
from datetime import datetime

from app.services.cloud_integration_service import (
    CloudIntegrationService,
    CloudProvider,
    DeploymentStatus,
    ResourceType,
    CloudCredentials,
    DeploymentConfig,
    DeploymentInfo,
    CloudResource,
    AWSProvider,
    AzureProvider,
    GCPProvider
)

@pytest.fixture
def cloud_service():
    """Create a CloudIntegrationService instance for testing"""
    return CloudIntegrationService()

@pytest.fixture
def aws_credentials():
    """Create AWS credentials for testing"""
    return CloudCredentials(
        provider=CloudProvider.AWS,
        access_key="test_aws_access_key",
        secret_key="test_aws_secret_key",
        region="us-east-1"
    )

@pytest.fixture
def azure_credentials():
    """Create Azure credentials for testing"""
    return CloudCredentials(
        provider=CloudProvider.AZURE,
        access_key="test_azure_client_id",
        secret_key="test_azure_client_secret",
        region="East US",
        additional_params={"tenant_id": "test_tenant_id"}
    )

@pytest.fixture
def gcp_credentials():
    """Create GCP credentials for testing"""
    return CloudCredentials(
        provider=CloudProvider.GCP,
        access_key="test_gcp_project_id",
        secret_key="test_gcp_service_key",
        region="us-central1"
    )

@pytest.fixture
def deployment_config():
    """Create a deployment configuration for testing"""
    return DeploymentConfig(
        name="test-deployment",
        provider=CloudProvider.AWS,
        instance_type="t3.medium",
        min_instances=1,
        max_instances=5,
        auto_scaling=True,
        load_balancer=True,
        storage_gb=100,
        database_required=True,
        ssl_enabled=True,
        backup_enabled=True,
        monitoring_enabled=True,
        environment_vars={"ENV": "test"},
        tags={"project": "axiom", "environment": "test"}
    )

class TestCloudIntegrationService:
    """Test suite for CloudIntegrationService"""
    
    def test_service_initialization(self, cloud_service):
        """Test service initializes correctly"""
        assert cloud_service.providers == {}
        assert cloud_service.deployments == {}
        
    def test_add_credentials(self, cloud_service, aws_credentials):
        """Test adding cloud credentials"""
        cloud_service.add_credentials(aws_credentials)
        
        assert CloudProvider.AWS in cloud_service.providers
        provider = cloud_service.providers[CloudProvider.AWS]
        assert isinstance(provider, AWSProvider)
        assert provider.credentials == aws_credentials
        
    def test_add_multiple_credentials(self, cloud_service, aws_credentials, azure_credentials, gcp_credentials):
        """Test adding credentials for multiple providers"""
        cloud_service.add_credentials(aws_credentials)
        cloud_service.add_credentials(azure_credentials)
        cloud_service.add_credentials(gcp_credentials)
        
        assert len(cloud_service.providers) == 3
        assert CloudProvider.AWS in cloud_service.providers
        assert CloudProvider.AZURE in cloud_service.providers
        assert CloudProvider.GCP in cloud_service.providers
        
    def test_get_supported_providers(self, cloud_service):
        """Test getting supported providers"""
        providers = cloud_service.get_supported_providers()
        
        assert len(providers) >= 3
        provider_names = {p["provider"] for p in providers}
        assert "aws" in provider_names
        assert "azure" in provider_names
        assert "gcp" in provider_names
        
    def test_get_recommended_configurations(self, cloud_service):
        """Test getting recommended configurations"""
        configs = cloud_service.get_recommended_configurations()
        
        assert len(configs) > 0
        assert any("development" in c["name"].lower() for c in configs)
        assert any("production" in c["name"].lower() for c in configs)
        
    @pytest.mark.asyncio
    async def test_get_cost_estimate(self, cloud_service, deployment_config, aws_credentials):
        """Test cost estimation"""
        cloud_service.add_credentials(aws_credentials)
        
        with patch.object(AWSProvider, 'estimate_cost', return_value=150.0) as mock_estimate:
            cost = await cloud_service.get_cost_estimate(deployment_config)
            
            assert cost == 150.0
            mock_estimate.assert_called_once_with(deployment_config)
            
    @pytest.mark.asyncio
    async def test_compare_providers(self, cloud_service, deployment_config, aws_credentials, azure_credentials, gcp_credentials):
        """Test provider cost comparison"""
        cloud_service.add_credentials(aws_credentials)
        cloud_service.add_credentials(azure_credentials)
        cloud_service.add_credentials(gcp_credentials)
        
        with patch.object(AWSProvider, 'estimate_cost', return_value=150.0), \
             patch.object(AzureProvider, 'estimate_cost', return_value=140.0), \
             patch.object(GCPProvider, 'estimate_cost', return_value=160.0):
            
            costs = await cloud_service.compare_providers(deployment_config)
            
            assert len(costs) == 3
            assert costs[CloudProvider.AWS] == 150.0
            assert costs[CloudProvider.AZURE] == 140.0
            assert costs[CloudProvider.GCP] == 160.0
            
    @pytest.mark.asyncio
    async def test_create_deployment(self, cloud_service, deployment_config, aws_credentials):
        """Test creating a deployment"""
        cloud_service.add_credentials(aws_credentials)
        
        mock_resources = [
            CloudResource(
                id="i-1234567890abcdef0",
                name="axiom-compute-1",
                provider=CloudProvider.AWS,
                resource_type=ResourceType.COMPUTE,
                status="running",
                region="us-east-1",
                cost_per_hour=0.05,
                created_at=datetime.now()
            )
        ]
        
        with patch.object(AWSProvider, 'create_deployment') as mock_create:
            mock_create.return_value = DeploymentInfo(
                id="deployment-123",
                name="test-deployment",
                provider=CloudProvider.AWS,
                status=DeploymentStatus.DEPLOYING,
                config=deployment_config,
                resources=mock_resources,
                endpoint_url="https://test-deployment.aws.com",
                cost_estimate=150.0,
                created_at=datetime.now()
            )
            
            deployment = await cloud_service.create_deployment(deployment_config)
            
            assert deployment.id == "deployment-123"
            assert deployment.name == "test-deployment"
            assert deployment.provider == CloudProvider.AWS
            assert deployment.status == DeploymentStatus.DEPLOYING
            assert len(deployment.resources) == 1
            assert deployment.cost_estimate == 150.0
            
            # Verify deployment is stored
            assert "deployment-123" in cloud_service.deployments
            
    @pytest.mark.asyncio
    async def test_list_deployments(self, cloud_service, deployment_config, aws_credentials):
        """Test listing deployments"""
        cloud_service.add_credentials(aws_credentials)
        
        # Create a mock deployment
        mock_deployment = DeploymentInfo(
            id="deployment-123",
            name="test-deployment",
            provider=CloudProvider.AWS,
            status=DeploymentStatus.RUNNING,
            config=deployment_config,
            resources=[],
            endpoint_url="https://test-deployment.aws.com",
            cost_estimate=150.0,
            created_at=datetime.now()
        )
        
        cloud_service.deployments["deployment-123"] = mock_deployment
        
        deployments = await cloud_service.list_deployments()
        
        assert len(deployments) == 1
        assert deployments[0].id == "deployment-123"
        assert deployments[0].name == "test-deployment"
        
    @pytest.mark.asyncio
    async def test_get_deployment(self, cloud_service, deployment_config):
        """Test getting a specific deployment"""
        # Create a mock deployment
        mock_deployment = DeploymentInfo(
            id="deployment-123",
            name="test-deployment",
            provider=CloudProvider.AWS,
            status=DeploymentStatus.RUNNING,
            config=deployment_config,
            resources=[],
            endpoint_url="https://test-deployment.aws.com",
            cost_estimate=150.0,
            created_at=datetime.now()
        )
        
        cloud_service.deployments["deployment-123"] = mock_deployment
        
        deployment = await cloud_service.get_deployment("deployment-123")
        
        assert deployment is not None
        assert deployment.id == "deployment-123"
        assert deployment.name == "test-deployment"
        
        # Test non-existent deployment
        non_existent = await cloud_service.get_deployment("non-existent")
        assert non_existent is None
        
    @pytest.mark.asyncio
    async def test_scale_deployment(self, cloud_service, deployment_config, aws_credentials):
        """Test scaling a deployment"""
        cloud_service.add_credentials(aws_credentials)
        
        # Create a mock deployment
        mock_deployment = DeploymentInfo(
            id="deployment-123",
            name="test-deployment",
            provider=CloudProvider.AWS,
            status=DeploymentStatus.RUNNING,
            config=deployment_config,
            resources=[],
            endpoint_url="https://test-deployment.aws.com",
            cost_estimate=150.0,
            created_at=datetime.now()
        )
        
        cloud_service.deployments["deployment-123"] = mock_deployment
        
        with patch.object(AWSProvider, 'scale_deployment', return_value=True) as mock_scale:
            success = await cloud_service.scale_deployment("deployment-123", 5)
            
            assert success is True
            mock_scale.assert_called_once_with("deployment-123", 5)
            
    @pytest.mark.asyncio
    async def test_delete_deployment(self, cloud_service, deployment_config, aws_credentials):
        """Test deleting a deployment"""
        cloud_service.add_credentials(aws_credentials)
        
        # Create a mock deployment
        mock_deployment = DeploymentInfo(
            id="deployment-123",
            name="test-deployment",
            provider=CloudProvider.AWS,
            status=DeploymentStatus.RUNNING,
            config=deployment_config,
            resources=[],
            endpoint_url="https://test-deployment.aws.com",
            cost_estimate=150.0,
            created_at=datetime.now()
        )
        
        cloud_service.deployments["deployment-123"] = mock_deployment
        
        with patch.object(AWSProvider, 'delete_deployment', return_value=True) as mock_delete:
            success = await cloud_service.delete_deployment("deployment-123")
            
            assert success is True
            mock_delete.assert_called_once_with("deployment-123")
            
            # Verify deployment is removed from storage
            assert "deployment-123" not in cloud_service.deployments
            
    @pytest.mark.asyncio
    async def test_get_deployment_metrics(self, cloud_service, deployment_config, aws_credentials):
        """Test getting deployment metrics"""
        cloud_service.add_credentials(aws_credentials)
        
        # Create a mock deployment
        mock_deployment = DeploymentInfo(
            id="deployment-123",
            name="test-deployment",
            provider=CloudProvider.AWS,
            status=DeploymentStatus.RUNNING,
            config=deployment_config,
            resources=[],
            endpoint_url="https://test-deployment.aws.com",
            cost_estimate=150.0,
            created_at=datetime.now()
        )
        
        cloud_service.deployments["deployment-123"] = mock_deployment
        
        mock_metrics = {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "network_io": 1024,
            "disk_io": 2048,
            "active_connections": 15
        }
        
        with patch.object(AWSProvider, 'get_metrics', return_value=mock_metrics) as mock_get_metrics:
            metrics = await cloud_service.get_deployment_metrics("deployment-123")
            
            assert metrics == mock_metrics
            mock_get_metrics.assert_called_once_with("deployment-123")

class TestCloudProviders:
    """Test suite for individual cloud providers"""
    
    def test_aws_provider_initialization(self, aws_credentials):
        """Test AWS provider initialization"""
        provider = AWSProvider(aws_credentials)
        
        assert provider.credentials == aws_credentials
        assert provider.provider == CloudProvider.AWS
        
    def test_azure_provider_initialization(self, azure_credentials):
        """Test Azure provider initialization"""
        provider = AzureProvider(azure_credentials)
        
        assert provider.credentials == azure_credentials
        assert provider.provider == CloudProvider.AZURE
        
    def test_gcp_provider_initialization(self, gcp_credentials):
        """Test GCP provider initialization"""
        provider = GCPProvider(gcp_credentials)
        
        assert provider.credentials == gcp_credentials
        assert provider.provider == CloudProvider.GCP

class TestDataClasses:
    """Test suite for data classes and enums"""
    
    def test_cloud_provider_enum(self):
        """Test CloudProvider enum values"""
        assert CloudProvider.AWS.value == "aws"
        assert CloudProvider.AZURE.value == "azure"
        assert CloudProvider.GCP.value == "gcp"
        assert CloudProvider.DIGITAL_OCEAN.value == "digitalocean"
        assert CloudProvider.LINODE.value == "linode"
        
    def test_deployment_status_enum(self):
        """Test DeploymentStatus enum values"""
        assert DeploymentStatus.DEPLOYING.value == "deploying"
        assert DeploymentStatus.RUNNING.value == "running"
        assert DeploymentStatus.SCALING.value == "scaling"
        assert DeploymentStatus.ERROR.value == "error"
        assert DeploymentStatus.TERMINATED.value == "terminated"
        
    def test_resource_type_enum(self):
        """Test ResourceType enum values"""
        assert ResourceType.COMPUTE.value == "compute"
        assert ResourceType.STORAGE.value == "storage"
        assert ResourceType.DATABASE.value == "database"
        assert ResourceType.NETWORK.value == "network"
        assert ResourceType.LOAD_BALANCER.value == "load_balancer"
        
    def test_cloud_credentials_creation(self):
        """Test CloudCredentials data class"""
        creds = CloudCredentials(
            provider=CloudProvider.AWS,
            access_key="test_key",
            secret_key="test_secret",
            region="us-west-2",
            additional_params={"role_arn": "test_role"}
        )
        
        assert creds.provider == CloudProvider.AWS
        assert creds.access_key == "test_key"
        assert creds.secret_key == "test_secret"
        assert creds.region == "us-west-2"
        assert creds.additional_params is not None
        assert creds.additional_params.get("role_arn") == "test_role"
        
    def test_deployment_config_creation(self):
        """Test DeploymentConfig data class"""
        config = DeploymentConfig(
            name="test-deployment",
            provider=CloudProvider.AWS,
            instance_type="t3.large",
            min_instances=2,
            max_instances=10,
            auto_scaling=True,
            storage_gb=200,
            environment_vars={"DEBUG": "true"}
        )
        
        assert config.name == "test-deployment"
        assert config.provider == CloudProvider.AWS
        assert config.instance_type == "t3.large"
        assert config.min_instances == 2
        assert config.max_instances == 10
        assert config.auto_scaling is True
        assert config.storage_gb == 200
        assert config.environment_vars is not None
        assert config.environment_vars.get("DEBUG") == "true"

# Run tests with: pytest -xvs tests/unit/test_cloud_integration_service.py
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
