"""
Tests unitarios para Service Registry & Discovery
===============================================

Validación completa del sistema de registro y descubrimiento de servicios
para ecosistema AXIOM con auto-discovery, health monitoring, intelligent routing.
"""

import pytest

from app.service_registry_discovery import (
    ServiceRegistry,
    ServiceDiscoveryClient,
    ServiceMetadata,
    ServiceCapability,
    ServiceDiscoveryQuery,
    RoutingDecision,
    ServiceStatus,
    CapabilityType,
    create_service_registry,
    auto_register_axiom_services
)


class TestServiceMetadata:
    """Tests para ServiceMetadata"""
    
    def test_service_metadata_creation(self):
        """Test creación de ServiceMetadata"""
        capability = ServiceCapability(
            name="test_capability",
            type=CapabilityType.COMPUTATIONAL,
            description="Test capability",
            input_schema={"input": "str"},
            output_schema={"output": "str"}
        )
        
        metadata = ServiceMetadata(
            service_id="test_service",
            name="Test Service",
            version="1.0.0",
            description="Test service description",
            endpoint="http://localhost:8080",
            capabilities=[capability],
            tags=["test", "example"]
        )
        
        assert metadata.service_id == "test_service"
        assert metadata.name == "Test Service"
        assert len(metadata.capabilities) == 1
        assert metadata.capabilities[0].name == "test_capability"
        assert metadata.health_status == ServiceStatus.UNKNOWN


class TestServiceCapability:
    """Tests para ServiceCapability"""
    
    def test_capability_creation(self):
        """Test creación de ServiceCapability"""
        capability = ServiceCapability(
            name="data_processing",
            type=CapabilityType.PROCESSING,
            description="Process data efficiently",
            input_schema={"data": "list"},
            output_schema={"processed_data": "list"},
            performance_metrics={"avg_time": 100.0}
        )
        
        assert capability.name == "data_processing"
        assert capability.type == CapabilityType.PROCESSING
        assert capability.performance_metrics["avg_time"] == 100.0
        assert capability.version == "1.0.0"


class TestServiceRegistry:
    """Tests para ServiceRegistry"""
    
    @pytest.fixture
    def registry(self):
        """Registry de prueba sin dependencias externas"""
        return ServiceRegistry(cache=None, cross_validation_matrix=None)
    
    @pytest.fixture
    def sample_service_metadata(self):
        """Metadata de servicio de ejemplo"""
        capability = ServiceCapability(
            name="computation",
            type=CapabilityType.COMPUTATIONAL,
            description="Mathematical computation",
            input_schema={"numbers": "list"},
            output_schema={"result": "float"}
        )
        
        return ServiceMetadata(
            service_id="math_service",
            name="Mathematics Service",
            version="1.0.0",
            description="Advanced mathematical computations",
            endpoint=None,
            capabilities=[capability],
            tags=["math", "computation"],
            performance_metrics={"avg_response_time": 200.0, "error_rate": 0.01}
        )
    
    @pytest.mark.asyncio
    async def test_register_service(self, registry, sample_service_metadata):
        """Test registro de servicio"""
        result = await registry.register_service(sample_service_metadata)
        
        assert result is True
        assert "math_service" in registry._services
        assert registry._services["math_service"].name == "Mathematics Service"
        
        # Verificar índices
        assert "math_service" in registry._capability_index[CapabilityType.COMPUTATIONAL.value]
        assert "math_service" in registry._tag_index["math"]
        assert "math_service" in registry._tag_index["computation"]
    
    @pytest.mark.asyncio
    async def test_unregister_service(self, registry, sample_service_metadata):
        """Test desregistro de servicio"""
        # Primero registrar
        await registry.register_service(sample_service_metadata)
        assert "math_service" in registry._services
        
        # Luego desregistrar
        result = await registry.unregister_service("math_service")
        
        assert result is True
        assert "math_service" not in registry._services
        
        # Verificar limpieza de índices
        assert "math_service" not in registry._capability_index[CapabilityType.COMPUTATIONAL.value]
        assert "math_service" not in registry._tag_index["math"]
    
    @pytest.mark.asyncio
    async def test_discover_services_by_capability(self, registry):
        """Test descubrimiento de servicios por capability"""
        # Registrar servicios de prueba
        math_capability = ServiceCapability(
            name="math_ops", type=CapabilityType.COMPUTATIONAL,
            description="Math", input_schema={}, output_schema={}
        )
        analysis_capability = ServiceCapability(
            name="analysis", type=CapabilityType.ANALYTICAL,
            description="Analysis", input_schema={}, output_schema={}
        )
        
        math_service = ServiceMetadata(
            service_id="math_svc", name="Math", version="1.0",
            description="Math service", endpoint=None,
            capabilities=[math_capability], health_status=ServiceStatus.HEALTHY
        )
        
        analysis_service = ServiceMetadata(
            service_id="analysis_svc", name="Analysis", version="1.0",
            description="Analysis service", endpoint=None,
            capabilities=[analysis_capability], health_status=ServiceStatus.HEALTHY
        )
        
        await registry.register_service(math_service)
        await registry.register_service(analysis_service)
        
        # Query por capability específica
        query = ServiceDiscoveryQuery(
            capability_types=[CapabilityType.COMPUTATIONAL],
            required_status=[ServiceStatus.HEALTHY]
        )
        
        results = await registry.discover_services(query)
        
        assert len(results) == 1
        assert results[0].service_id == "math_svc"
    
    @pytest.mark.asyncio
    async def test_discover_services_by_tags(self, registry):
        """Test descubrimiento por tags"""
        capability = ServiceCapability(
            name="test", type=CapabilityType.COMPUTATIONAL,
            description="Test", input_schema={}, output_schema={}
        )
        
        service1 = ServiceMetadata(
            service_id="svc1", name="Service 1", version="1.0",
            description="Service 1", endpoint=None, capabilities=[capability],
            tags=["tag1", "common"], health_status=ServiceStatus.HEALTHY
        )
        
        service2 = ServiceMetadata(
            service_id="svc2", name="Service 2", version="1.0",
            description="Service 2", endpoint=None, capabilities=[capability],
            tags=["tag2", "common"], health_status=ServiceStatus.HEALTHY
        )
        
        await registry.register_service(service1)
        await registry.register_service(service2)
        
        # Query por tag común
        query = ServiceDiscoveryQuery(tags=["common"])
        results = await registry.discover_services(query)
        
        assert len(results) == 2
        service_ids = [s.service_id for s in results]
        assert "svc1" in service_ids
        assert "svc2" in service_ids
    
    @pytest.mark.asyncio
    async def test_health_check(self, registry, sample_service_metadata):
        """Test health check del registry"""
        # Registry vacío
        health = await registry.health_check()
        assert health["total_services"] == 0
        assert health["status"] == "healthy"
        
        # Con servicios
        await registry.register_service(sample_service_metadata)
        health = await registry.health_check()
        
        assert health["total_services"] == 1
        assert "healthy_services" in health
        assert "capability_index_size" in health
        assert "tag_index_size" in health
    
    @pytest.mark.asyncio
    async def test_get_intelligent_routing(self, registry):
        """Test intelligent routing"""
        # Crear servicio con métricas de performance
        capability = ServiceCapability(
            name="optimization", type=CapabilityType.OPTIMIZATION,
            description="Optimization", input_schema={}, output_schema={}
        )
        
        service = ServiceMetadata(
            service_id="optimizer", name="Optimizer", version="1.0",
            description="Optimization service", endpoint=None,
            capabilities=[capability], health_status=ServiceStatus.HEALTHY,
            performance_metrics={
                "avg_response_time": 150.0,
                "error_rate": 0.02,
                "throughput": 50.0
            }
        )
        
        await registry.register_service(service)
        
        # Request routing
        payload = {"problem": "minimize", "variables": 5}
        routing = await registry.get_intelligent_routing(
            payload, CapabilityType.OPTIMIZATION
        )
        
        assert routing is not None
        assert isinstance(routing, RoutingDecision)
        assert routing.target_service == "optimizer"
        assert 0.0 <= routing.confidence <= 1.0
        assert routing.compatibility_score >= 0.0
    
    @pytest.mark.asyncio
    async def test_update_performance_metrics(self, registry, sample_service_metadata):
        """Test actualización de métricas de performance"""
        await registry.register_service(sample_service_metadata)
        
        new_metrics = {
            "avg_response_time": 180.0,
            "error_rate": 0.005,
            "throughput": 75.0
        }
        
        result = await registry.update_performance_metrics("math_service", new_metrics)
        
        assert result is True
        service = registry._services["math_service"]
        assert service.performance_metrics["avg_response_time"] == 180.0
        assert service.performance_metrics["error_rate"] == 0.005
    
    @pytest.mark.asyncio
    async def test_get_service_compatibility_matrix(self, registry):
        """Test matriz de compatibilidad de servicios"""
        # Registrar múltiples servicios
        services_data = []
        for i in range(3):
            capability = ServiceCapability(
                name=f"cap_{i}", type=CapabilityType.COMPUTATIONAL,
                description=f"Capability {i}", input_schema={}, output_schema={}
            )
            service = ServiceMetadata(
                service_id=f"service_{i}", name=f"Service {i}", version="1.0",
                description=f"Service {i}", endpoint=None, capabilities=[capability]
            )
            services_data.append(service)
            await registry.register_service(service)
        
        service_ids = [f"service_{i}" for i in range(3)]
        matrix = await registry.get_service_compatibility_matrix(service_ids)
        
        assert "matrix" in matrix
        assert "services" in matrix
        assert len(matrix["services"]) == 3
        
        # Verificar estructura de matriz
        for service_id in service_ids:
            assert service_id in matrix["matrix"]
            assert len(matrix["matrix"][service_id]) == 3


class TestServiceDiscoveryClient:
    """Tests para ServiceDiscoveryClient"""
    
    @pytest.fixture
    def registry(self):
        return ServiceRegistry(cache=None, cross_validation_matrix=None)
    
    @pytest.fixture
    def client(self, registry):
        return ServiceDiscoveryClient(registry)
    
    @pytest.mark.asyncio
    async def test_find_service(self, client, registry):
        """Test búsqueda de servicio específico"""
        # Registrar servicio
        capability = ServiceCapability(
            name="prediction", type=CapabilityType.PREDICTIVE,
            description="ML Prediction", input_schema={}, output_schema={}
        )
        
        service = ServiceMetadata(
            service_id="ml_predictor", name="ML Predictor", version="1.0",
            description="ML service", endpoint=None, capabilities=[capability],
            health_status=ServiceStatus.HEALTHY
        )
        
        await registry.register_service(service)
        
        # Buscar servicio
        found_service = await client.find_service(
            capability=CapabilityType.PREDICTIVE,
            tags=[]
        )
        
        assert found_service == "ml_predictor"
    
    @pytest.mark.asyncio
    async def test_get_routing_recommendation(self, client, registry):
        """Test recomendación de routing"""
        # Registrar servicio
        capability = ServiceCapability(
            name="simulation", type=CapabilityType.SIMULATION,
            description="Physics Simulation", input_schema={}, output_schema={}
        )
        
        service = ServiceMetadata(
            service_id="physics_sim", name="Physics Simulator", version="1.0",
            description="Physics simulation", endpoint=None, capabilities=[capability],
            health_status=ServiceStatus.HEALTHY,
            performance_metrics={"avg_response_time": 300.0, "error_rate": 0.01}
        )
        
        await registry.register_service(service)
        
        # Obtener recomendación
        payload = {"simulation_type": "molecular_dynamics"}
        recommendation = await client.get_routing_recommendation(
            payload=payload,
            capability=CapabilityType.SIMULATION
        )
        
        assert recommendation is not None
        assert recommendation.target_service == "physics_sim"
        assert recommendation.confidence > 0.0
    
    @pytest.mark.asyncio
    async def test_bulk_compatibility_check(self, client, registry):
        """Test verificación masiva de compatibilidad"""
        # Registrar servicios
        services = []
        for i in range(2):
            capability = ServiceCapability(
                name=f"capability_{i}", type=CapabilityType.ANALYTICAL,
                description=f"Analysis {i}", input_schema={}, output_schema={}
            )
            service = ServiceMetadata(
                service_id=f"analyzer_{i}", name=f"Analyzer {i}", version="1.0",
                description=f"Analyzer {i}", endpoint=None, capabilities=[capability]
            )
            services.append(service)
            await registry.register_service(service)
        
        service_ids = ["analyzer_0", "analyzer_1"]
        compatibility = await client.bulk_compatibility_check(service_ids)
        
        assert "matrix" in compatibility
        assert "services" in compatibility
        assert len(compatibility["services"]) == 2


class TestServiceRegistryIntegration:
    """Tests de integración para Service Registry"""
    
    @pytest.mark.asyncio
    async def test_create_service_registry_factory(self):
        """Test factory de creación de registry"""
        registry = await create_service_registry(auto_discovery=True)
        
        assert isinstance(registry, ServiceRegistry)
        assert registry._auto_discovery_enabled is True
        
        health = await registry.health_check()
        assert health["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_auto_register_axiom_services(self):
        """Test auto-registro de servicios AXIOM"""
        registry = await create_service_registry()
        
        # Auto-registrar servicios
        count = await auto_register_axiom_services(registry)
        
        assert count >= 3  # Al menos 3 servicios base
        
        # Verificar que se registraron servicios conocidos
        services = registry._services
        service_ids = list(services.keys())
        
        expected_services = ["unified_tool_adapter", "cross_validation_matrix", "uncertainty_quantification"]
        for expected in expected_services:
            assert expected in service_ids
    
    @pytest.mark.asyncio
    async def test_end_to_end_service_discovery(self):
        """Test end-to-end de discovery de servicios"""
        # Crear registry y auto-registrar servicios
        registry = await create_service_registry()
        await auto_register_axiom_services(registry)
        
        client = ServiceDiscoveryClient(registry)
        
        # Buscar servicio de validación (acepta cualquier status incluyendo UNKNOWN)
        validation_service = await client.find_service(
            capability=CapabilityType.VALIDATION
        )
        
        assert validation_service is not None
        assert validation_service == "cross_validation_matrix"
        
        # Health check completo
        health = await registry.health_check()
        assert health["total_services"] >= 3
        assert health["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_performance_and_health_monitoring(self):
        """Test monitoring de performance y health"""
        registry = await create_service_registry()
        
        # Registrar servicio
        capability = ServiceCapability(
            name="monitoring_test", type=CapabilityType.COMPUTATIONAL,
            description="Test monitoring", input_schema={}, output_schema={}
        )
        
        service = ServiceMetadata(
            service_id="monitored_service", name="Monitored Service", version="1.0",
            description="Service for monitoring test", endpoint=None,
            capabilities=[capability], health_status=ServiceStatus.HEALTHY
        )
        
        await registry.register_service(service)
        
        # Actualizar métricas múltiples veces
        for i in range(3):
            metrics = {
                "avg_response_time": 100.0 + i * 10,
                "error_rate": 0.01 + i * 0.005,
                "throughput": 100.0 - i * 5
            }
            await registry.update_performance_metrics("monitored_service", metrics)
            
            # Verificar que las métricas se actualizaron
            service_data = registry._services["monitored_service"]
            assert service_data.performance_metrics["avg_response_time"] == 100.0 + i * 10
        
        # Health check final
        health = await registry.health_check()
        assert health["total_services"] == 1
        assert health["healthy_services"] >= 0


if __name__ == "__main__":
    # Ejecutar tests específicos para debugging
    pytest.main([__file__, "-v", "--tb=short"])
