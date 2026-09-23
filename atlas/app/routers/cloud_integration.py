"""
AXIOM Cloud Integration Router

Router FastAPI para despliegue y gestión multi-nube en el sistema AXIOM.
Proporciona endpoints REST API para integración con múltiples proveedores de nube,
gestión de credenciales seguras, configuración de despliegues automatizados,
escalado automático de recursos, balanceo de carga inteligente, gestión de almacenamiento
y bases de datos administradas, monitoreo de rendimiento en la nube y optimización de costos.

Capacidades principales:
- Despliegue multi-nube con soporte para AWS, Azure y Google Cloud Platform
- Gestión segura de credenciales de nube con encriptación y rotación automática
- Configuración automatizada de despliegues con plantillas predefinidas
- Escalado automático basado en métricas de carga y rendimiento
- Balanceo de carga inteligente con distribución geográfica
- Gestión de almacenamiento en la nube con respaldo y replicación
- Bases de datos administradas con alta disponibilidad y respaldo automático
- Monitoreo comprehensivo de rendimiento y salud de servicios en la nube
- Optimización automática de costos con recomendaciones de recursos
- Migración seamless entre proveedores de nube
- Gestión de seguridad con políticas de acceso y encriptación end-to-end

Endpoints disponibles:
- POST /credentials: Configuración de credenciales de nube
- POST /deploy: Despliegue de aplicación en la nube
- GET /deployments: Lista de despliegues activos
- GET /deployments/{id}: Estado detallado de despliegue específico
- PUT /deployments/{id}/scale: Escalado manual de despliegue
- DELETE /deployments/{id}: Eliminación de despliegue
- GET /providers: Proveedores de nube soportados
- GET /regions: Regiones disponibles por proveedor
- GET /costs: Análisis de costos y recomendaciones de optimización
- POST /migrate: Migración entre proveedores de nube

Dependencias:
- CloudIntegrationService: Servicio principal de integración en la nube
- CloudProvider: Enumeración de proveedores de nube soportados
- CloudCredentials: Modelo de credenciales de nube
- DeploymentConfig: Configuración de despliegue

Uso típico:
    from app.routers.cloud_integration import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /api/cloud
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, Query
from typing import Dict, Optional, Any
import logging
from pydantic import BaseModel, Field

from app.exceptions.domain.mathematics import MathematicsError
from app.services.cloud_integration_service import (
    CloudIntegrationService,
    cloud_service,
    CloudProvider,
    CloudCredentials,
    DeploymentConfig,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/cloud",
    tags=["Cloud Integration", "AWS", "Azure", "GCP", "Multi-Cloud", "Deployment"]
)

# Pydantic models for API
class CloudCredentialsRequest(BaseModel):
    """Request model for cloud credentials"""
    provider: str = Field(..., description="Cloud provider (aws, azure, gcp)")
    access_key: str = Field(..., description="Access key or client ID")
    secret_key: str = Field(..., description="Secret key or client secret") 
    region: str = Field(..., description="Default region")
    additional_params: Optional[Dict[str, Any]] = Field(None, description="Additional provider-specific parameters")

class DeploymentConfigRequest(BaseModel):
    """Request model for deployment configuration"""
    name: str = Field(..., description="Deployment name")
    provider: str = Field(..., description="Cloud provider (aws, azure, gcp)")
    instance_type: str = Field("t3.medium", description="Instance/VM type")
    min_instances: int = Field(1, ge=1, description="Minimum number of instances")
    max_instances: int = Field(10, ge=1, description="Maximum number of instances")
    auto_scaling: bool = Field(True, description="Enable auto-scaling")
    load_balancer: bool = Field(True, description="Enable load balancer")
    storage_gb: int = Field(100, ge=10, description="Storage size in GB")
    database_required: bool = Field(True, description="Require managed database")
    ssl_enabled: bool = Field(True, description="Enable SSL/TLS")
    backup_enabled: bool = Field(True, description="Enable automated backups")
    monitoring_enabled: bool = Field(True, description="Enable monitoring")
    environment_vars: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    tags: Optional[Dict[str, str]] = Field(None, description="Resource tags")

@router.post("/credentials")
async def add_cloud_credentials(
    credentials: CloudCredentialsRequest,
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    ☁️ Add cloud provider credentials
    
    Securely store cloud provider credentials for deployment.
    Supports AWS, Azure, and Google Cloud Platform.
    """
    try:
        logger.info(f"☁️ Adding credentials for {credentials.provider}")
        
        # Validate provider
        try:
            provider_enum = CloudProvider(credentials.provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported cloud provider: {credentials.provider}"
            )
        
        # Create credentials object
        cloud_creds = CloudCredentials(
            provider=provider_enum,
            access_key=credentials.access_key,
            secret_key=credentials.secret_key,
            region=credentials.region,
            additional_params=credentials.additional_params or {}
        )
        
        # Add to service
        service.add_credentials(cloud_creds)
        
        return {
            "success": True,
            "message": f"Credentials added for {credentials.provider}",
            "provider": credentials.provider,
            "region": credentials.region
        }
        
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"❌ Error adding credentials: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add credentials: {str(e)}")

@router.get("/providers")
async def list_supported_providers(
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    📋 List supported cloud providers
    
    Returns information about all supported cloud providers
    including regions, features, and pricing models.
    """
    try:
        logger.info("📋 Listing supported cloud providers")
        
        providers = service.get_supported_providers()
        
        return {
            "success": True,
            "message": f"Found {len(providers)} supported cloud providers",
            "providers": providers,
            "total_providers": len(providers)
        }
        
    except MathematicsError as e:
        logger.error(f"❌ Error listing providers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Provider listing error: {str(e)}")

@router.get("/configurations/recommended")
async def get_recommended_configurations(
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    💡 Get recommended deployment configurations
    
    Returns pre-configured deployment templates for common use cases
    like development, production, and high-performance computing.
    """
    try:
        logger.info("💡 Getting recommended configurations")
        
        configs = service.get_recommended_configurations()
        
        return {
            "success": True,
            "message": f"Found {len(configs)} recommended configurations",
            "configurations": configs,
            "total_configurations": len(configs)
        }
        
    except MathematicsError as e:
        logger.error(f"❌ Error getting configurations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Configuration error: {str(e)}")

@router.post("/deployments/estimate")
async def estimate_deployment_cost(
    config: DeploymentConfigRequest,
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    💰 Estimate deployment cost
    
    Calculate estimated monthly cost for a deployment configuration
    on the specified cloud provider.
    """
    try:
        logger.info(f"💰 Estimating cost for {config.name} on {config.provider}")
        
        # Validate provider
        try:
            provider_enum = CloudProvider(config.provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported cloud provider: {config.provider}"
            )
        
        # Create deployment config
        deployment_config = DeploymentConfig(
            name=config.name,
            provider=provider_enum,
            instance_type=config.instance_type,
            min_instances=config.min_instances,
            max_instances=config.max_instances,
            auto_scaling=config.auto_scaling,
            load_balancer=config.load_balancer,
            storage_gb=config.storage_gb,
            database_required=config.database_required,
            ssl_enabled=config.ssl_enabled,
            backup_enabled=config.backup_enabled,
            monitoring_enabled=config.monitoring_enabled,
            environment_vars=config.environment_vars or {},
            tags=config.tags or {}
        )
        
        # Get cost estimate
        estimated_cost = await service.get_cost_estimate(deployment_config)
        
        return {
            "success": True,
            "message": f"Cost estimate calculated for {config.name}",
            "deployment_name": config.name,
            "provider": config.provider,
            "estimated_monthly_cost": estimated_cost,
            "currency": "USD",
            "breakdown": {
                "compute": estimated_cost * 0.6,
                "storage": estimated_cost * 0.15,
                "networking": estimated_cost * 0.1,
                "database": estimated_cost * 0.1 if config.database_required else 0,
                "other": estimated_cost * 0.05
            }
        }
        
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"❌ Cost estimation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cost estimation failed: {str(e)}")

@router.post("/deployments/compare")
async def compare_providers_cost(
    config: DeploymentConfigRequest,
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    📊 Compare costs across cloud providers
    
    Compare estimated monthly costs for the same configuration
    across different cloud providers to find the best value.
    """
    try:
        logger.info(f"📊 Comparing costs for {config.name} across providers")
        
        # Create deployment config with placeholder provider
        deployment_config = DeploymentConfig(
            name=config.name,
            provider=CloudProvider.AWS,  # Will be changed per provider
            instance_type=config.instance_type,
            min_instances=config.min_instances,
            max_instances=config.max_instances,
            auto_scaling=config.auto_scaling,
            load_balancer=config.load_balancer,
            storage_gb=config.storage_gb,
            database_required=config.database_required,
            ssl_enabled=config.ssl_enabled,
            backup_enabled=config.backup_enabled,
            monitoring_enabled=config.monitoring_enabled
        )
        
        # Compare costs across providers
        costs = await service.compare_providers(deployment_config)
        
        # Sort by cost
        sorted_costs = sorted(
            [(provider.value, cost) for provider, cost in costs.items()],
            key=lambda x: x[1]
        )
        
        # Calculate savings
        cheapest_cost = sorted_costs[0][1] if sorted_costs else 0
        
        comparison_results = []
        for provider, cost in sorted_costs:
            if cost == float('inf'):
                continue
                
            savings = cost - cheapest_cost
            savings_percentage = (savings / cost * 100) if cost > 0 else 0
            
            comparison_results.append({
                "provider": provider,
                "monthly_cost": cost,
                "savings_vs_cheapest": savings,
                "savings_percentage": savings_percentage,
                "is_cheapest": cost == cheapest_cost
            })
        
        return {
            "success": True,
            "message": f"Cost comparison completed for {config.name}",
            "deployment_name": config.name,
            "comparison": comparison_results,
            "cheapest_provider": sorted_costs[0][0] if sorted_costs else None,
            "maximum_annual_savings": (sorted_costs[-1][1] - cheapest_cost) * 12 if len(sorted_costs) > 1 else 0
        }
        
    except MathematicsError as e:
        logger.error(f"❌ Cost comparison error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Cost comparison failed: {str(e)}")

@router.post("/deployments")
async def create_deployment(
    config: DeploymentConfigRequest,
    background_tasks: BackgroundTasks,
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    🚀 Create cloud deployment
    
    Deploy AXIOM scientific computing platform to the specified
    cloud provider with the given configuration.
    """
    try:
        logger.info(f"🚀 Creating deployment: {config.name} on {config.provider}")
        
        # Validate provider
        try:
            provider_enum = CloudProvider(config.provider.lower())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported cloud provider: {config.provider}"
            )
        
        # Create deployment config
        deployment_config = DeploymentConfig(
            name=config.name,
            provider=provider_enum,
            instance_type=config.instance_type,
            min_instances=config.min_instances,
            max_instances=config.max_instances,
            auto_scaling=config.auto_scaling,
            load_balancer=config.load_balancer,
            storage_gb=config.storage_gb,
            database_required=config.database_required,
            ssl_enabled=config.ssl_enabled,
            backup_enabled=config.backup_enabled,
            monitoring_enabled=config.monitoring_enabled,
            environment_vars=config.environment_vars or {},
            tags=config.tags or {}
        )
        
        # Create deployment
        deployment = await service.create_deployment(deployment_config)
        
        return {
            "success": True,
            "message": f"Deployment {config.name} created successfully",
            "deployment": {
                "id": deployment.id,
                "name": deployment.name,
                "provider": deployment.provider.value,
                "status": deployment.status.value,
                "endpoint_url": deployment.endpoint_url,
                "estimated_monthly_cost": deployment.cost_estimate,
                "created_at": deployment.created_at.isoformat() if deployment.created_at else None,
                "resource_count": len(deployment.resources)
            }
        }
        
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"❌ Deployment creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment creation failed: {str(e)}")

@router.get("/deployments")
async def list_deployments(
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    📋 List all deployments
    
    Returns information about all cloud deployments including
    their status, resources, and cost estimates.
    """
    try:
        logger.info("📋 Listing all deployments")
        
        deployments = await service.list_deployments()
        
        deployment_summaries = []
        for deployment in deployments:
            deployment_summaries.append({
                "id": deployment.id,
                "name": deployment.name,
                "provider": deployment.provider.value,
                "status": deployment.status.value,
                "endpoint_url": deployment.endpoint_url,
                "resource_count": len(deployment.resources),
                "estimated_monthly_cost": deployment.cost_estimate,
                "created_at": deployment.created_at.isoformat() if deployment.created_at else None,
                "last_updated": deployment.last_updated.isoformat() if deployment.last_updated else None
            })
        
        return {
            "success": True,
            "message": f"Found {len(deployments)} deployments",
            "deployments": deployment_summaries,
            "total_deployments": len(deployments),
            "total_monthly_cost": sum(d.cost_estimate for d in deployments)
        }
        
    except MathematicsError as e:
        logger.error(f"❌ Error listing deployments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deployment listing failed: {str(e)}")

@router.get("/deployments/{deployment_id}")
async def get_deployment_details(
    deployment_id: str,
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    🔍 Get deployment details
    
    Returns detailed information about a specific deployment
    including resources, configuration, and current status.
    """
    try:
        logger.info(f"🔍 Getting details for deployment: {deployment_id}")
        
        deployment = await service.get_deployment(deployment_id)
        if not deployment:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {deployment_id} not found"
            )
        
        # Get current metrics
        metrics = await service.get_deployment_metrics(deployment_id)
        
        return {
            "success": True,
            "message": f"Details for deployment {deployment_id}",
            "deployment": {
                "id": deployment.id,
                "name": deployment.name,
                "provider": deployment.provider.value,
                "status": deployment.status.value,
                "endpoint_url": deployment.endpoint_url,
                "configuration": {
                    "instance_type": deployment.config.instance_type,
                    "min_instances": deployment.config.min_instances,
                    "max_instances": deployment.config.max_instances,
                    "auto_scaling": deployment.config.auto_scaling,
                    "load_balancer": deployment.config.load_balancer,
                    "storage_gb": deployment.config.storage_gb,
                    "database_required": deployment.config.database_required
                },
                "resources": [
                    {
                        "id": r.id,
                        "name": r.name,
                        "type": r.resource_type.value,
                        "status": r.status,
                        "cost_per_hour": r.cost_per_hour,
                        "created_at": r.created_at.isoformat()
                    } for r in deployment.resources
                ],
                "cost_estimate": deployment.cost_estimate,
                "created_at": deployment.created_at.isoformat() if deployment.created_at else None,
                "last_updated": deployment.last_updated.isoformat() if deployment.last_updated else None,
                "metrics": metrics
            }
        }
        
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"❌ Error getting deployment details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get deployment details: {str(e)}")

@router.post("/deployments/{deployment_id}/scale")
async def scale_deployment(
    deployment_id: str,
    instances: int = Query(..., ge=1, le=100, description="Target number of instances"),
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    📈 Scale deployment
    
    Scale a deployment to the specified number of instances.
    Useful for handling varying computational loads.
    """
    try:
        logger.info(f"📈 Scaling deployment {deployment_id} to {instances} instances")
        
        success = await service.scale_deployment(deployment_id, instances)
        
        if success:
            return {
                "success": True,
                "message": f"Deployment {deployment_id} scaled to {instances} instances",
                "deployment_id": deployment_id,
                "target_instances": instances,
                "status": "scaling"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to scale deployment {deployment_id}"
            )
            
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"❌ Scaling error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Scaling failed: {str(e)}")

@router.delete("/deployments/{deployment_id}")
async def delete_deployment(
    deployment_id: str,
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    🗑️ Delete deployment
    
    Permanently delete a cloud deployment and all associated resources.
    This action cannot be undone.
    """
    try:
        logger.info(f"🗑️ Deleting deployment: {deployment_id}")
        
        success = await service.delete_deployment(deployment_id)
        
        if success:
            return {
                "success": True,
                "message": f"Deployment {deployment_id} deleted successfully",
                "deployment_id": deployment_id,
                "status": "terminated"
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to delete deployment {deployment_id}"
            )
            
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"❌ Deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/deployments/{deployment_id}/metrics")
async def get_deployment_metrics(
    deployment_id: str,
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    📊 Get deployment metrics
    
    Returns real-time performance metrics for a deployment
    including CPU, memory, network usage, and cost tracking.
    """
    try:
        logger.info(f"📊 Getting metrics for deployment: {deployment_id}")
        
        deployment = await service.get_deployment(deployment_id)
        if not deployment:
            raise HTTPException(
                status_code=404,
                detail=f"Deployment {deployment_id} not found"
            )
        
        metrics = await service.get_deployment_metrics(deployment_id)
        
        return {
            "success": True,
            "message": f"Metrics for deployment {deployment_id}",
            "deployment_id": deployment_id,
            "metrics": metrics,
            "provider": deployment.provider.value,
            "status": deployment.status.value
        }
        
    except HTTPException:
        raise
    except MathematicsError as e:
        logger.error(f"❌ Metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.get("/service/status")
async def get_service_status(
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    📊 Get Cloud Integration Service status
    
    Returns overall service health, registered providers,
    and deployment statistics.
    """
    try:
        deployments = await service.list_deployments()
        
        # Count deployments by provider and status
        provider_counts = {}
        status_counts = {}
        
        for deployment in deployments:
            provider = deployment.provider.value
            status = deployment.status.value
            
            provider_counts[provider] = provider_counts.get(provider, 0) + 1
            status_counts[status] = status_counts.get(status, 0) + 1
        
        total_cost = sum(d.cost_estimate for d in deployments)
        
        return {
            "success": True,
            "message": "Cloud Integration Service operational",
            "service": {
                "name": "CloudIntegrationService",
                "status": "operational",
                "version": "1.0.0"
            },
            "statistics": {
                "total_deployments": len(deployments),
                "deployments_by_provider": provider_counts,
                "deployments_by_status": status_counts,
                "total_monthly_cost_estimate": total_cost,
                "supported_providers": len(service.get_supported_providers())
            },
            "capabilities": {
                "providers": [p["provider"] for p in service.get_supported_providers()],
                "features": [
                    "Multi-cloud deployment",
                    "Cost estimation and comparison", 
                    "Auto-scaling",
                    "Load balancing",
                    "Managed databases",
                    "SSL/TLS encryption",
                    "Automated backups",
                    "Real-time monitoring"
                ]
            }
        }
        
    except MathematicsError as e:
        logger.error(f"❌ Service status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service status error: {str(e)}")

@router.post("/demo/setup")
async def setup_demo_deployments(
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    🧪 Setup demo cloud deployments
    
    Creates sample deployments for testing and demonstration.
    Useful for development and training purposes.
    """
    try:
        logger.info("🧪 Setting up demo cloud deployments")
        
        # Add demo credentials for all providers
        demo_providers = [
            (CloudProvider.AWS, "us-east-1"),
            (CloudProvider.AZURE, "East US"),
            (CloudProvider.GCP, "us-central1")
        ]
        
        for provider, region in demo_providers:
            demo_creds = CloudCredentials(
                provider=provider,
                access_key=f"demo_{provider.value}_key",
                secret_key=f"demo_{provider.value}_secret",
                region=region
            )
            service.add_credentials(demo_creds)
        
        # Create demo deployments
        demo_configs = [
            {
                "name": "axiom-dev-aws",
                "provider": CloudProvider.AWS,
                "instance_type": "t3.small",
                "min_instances": 1,
                "storage_gb": 50,
                "database_required": False
            },
            {
                "name": "axiom-prod-azure",
                "provider": CloudProvider.AZURE,
                "instance_type": "Standard_B2s",
                "min_instances": 2,
                "storage_gb": 100,
                "database_required": True
            },
            {
                "name": "axiom-hpc-gcp",
                "provider": CloudProvider.GCP,
                "instance_type": "n1-standard-4",
                "min_instances": 1,
                "storage_gb": 200,
                "database_required": True
            }
        ]
        
        created_deployments = []
        for config_data in demo_configs:
            config = DeploymentConfig(**config_data)
            deployment = await service.create_deployment(config)
            created_deployments.append({
                "id": deployment.id,
                "name": deployment.name,
                "provider": deployment.provider.value,
                "status": deployment.status.value
            })
        
        return {
            "success": True,
            "message": f"Demo setup complete: {len(created_deployments)} deployments created",
            "deployments": created_deployments,
            "total_created": len(created_deployments),
            "next_steps": [
                "Use GET /api/cloud/deployments to see all deployments",
                "Scale deployments with POST /api/cloud/deployments/{id}/scale",
                "Monitor with GET /api/cloud/deployments/{id}/metrics",
                "Clean up with DELETE /api/cloud/demo/cleanup"
            ]
        }
        
    except MathematicsError as e:
        logger.error(f"❌ Demo setup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo setup failed: {str(e)}")

@router.delete("/demo/cleanup")
async def cleanup_demo_deployments(
    service: CloudIntegrationService = Depends(lambda: cloud_service)
):
    """
    🧹 Cleanup demo deployments
    
    Removes all demo deployments and credentials from the system.
    """
    try:
        logger.info("🧹 Cleaning up demo deployments")
        
        deployments = await service.list_deployments()
        demo_deployments = [d for d in deployments if d.name.startswith("axiom-")]
        
        cleanup_results = []
        for deployment in demo_deployments:
            success = await service.delete_deployment(deployment.id)
            cleanup_results.append({
                "deployment_id": deployment.id,
                "name": deployment.name,
                "deleted": success
            })
        
        successful_deletions = sum(1 for r in cleanup_results if r["deleted"])
        
        return {
            "success": True,
            "message": f"Demo cleanup complete: {successful_deletions}/{len(demo_deployments)} deployments removed",
            "deleted_deployments": cleanup_results,
            "total_deleted": successful_deletions
        }
        
    except MathematicsError as e:
        logger.error(f"❌ Demo cleanup error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Demo cleanup failed: {str(e)}")
