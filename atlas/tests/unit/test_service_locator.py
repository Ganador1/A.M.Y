"""
Test suite for ServiceLocator and domain architecture improvements.

Validates:
1. BaseService shim works correctly in biology domain
2. GenomicsService properly inherits from BaseService
3. ServiceLocator can discover and instantiate services
4. Domain services are compatible with autonomous loops
"""

import pytest
from typing import Dict, Any


class TestBiologyBaseServiceShim:
    """Test that biology's base_service.py is now a proper shim."""
    
    def test_biology_base_service_reexports_core_base_service(self):
        """Verify biology's BaseService is the same as core BaseService."""
        from app.domains.biology.services.base_service import BaseService as BiologyBaseService
        from app.services.base_service import BaseService as CoreBaseService
        
        assert BiologyBaseService is CoreBaseService, (
            "Biology BaseService should be a re-export of core BaseService"
        )
    
    def test_biology_service_mixin_available(self):
        """Verify BiologyServiceMixin is available for backwards compatibility."""
        from app.domains.biology.services.base_service import BiologyServiceMixin
        
        assert hasattr(BiologyServiceMixin, "get_service_info")
        assert hasattr(BiologyServiceMixin, "validate_biology_request")
        assert hasattr(BiologyServiceMixin, "check_ethics_compliance")
        assert hasattr(BiologyServiceMixin, "log_biology_operation")


class TestGenomicsServiceRefactored:
    """Test GenomicsService with new inheritance."""
    
    def test_genomics_service_inherits_from_core_base_service(self):
        """Verify GenomicsService inherits from core BaseService."""
        from app.domains.biology.services.genomics_service import GenomicsService
        from app.services.base_service import BaseService
        
        assert issubclass(GenomicsService, BaseService), (
            "GenomicsService should inherit from core BaseService"
        )
    
    def test_genomics_service_has_process_request(self):
        """Verify GenomicsService implements process_request."""
        from app.domains.biology.services.genomics_service import GenomicsService
        import inspect
        
        service = GenomicsService()
        assert hasattr(service, "process_request")
        assert inspect.iscoroutinefunction(service.process_request)
    
    @pytest.mark.asyncio
    async def test_genomics_service_process_request_returns_dict(self):
        """Test process_request returns expected structure."""
        from app.domains.biology.services.genomics_service import GenomicsService
        
        service = GenomicsService()
        result = await service.process_request({
            "timestamp": "2024-01-01T00:00:00Z",
            "operation": "info"
        })
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "service_info" in result
    
    def test_genomics_service_has_name(self):
        """Verify GenomicsService has name from BaseService."""
        from app.domains.biology.services.genomics_service import GenomicsService
        
        service = GenomicsService()
        # BaseService sets name in __init__
        assert hasattr(service, "name")
        assert service.name == "GenomicsService"


class TestServiceLocator:
    """Test the new ServiceLocator functionality."""
    
    def test_service_locator_singleton(self):
        """Verify ServiceLocator is a singleton."""
        from app.domains.service_locator import ServiceLocator
        
        locator1 = ServiceLocator.get_instance()
        locator2 = ServiceLocator.get_instance()
        
        assert locator1 is locator2
    
    def test_service_locator_lists_domains(self):
        """Test listing available domains."""
        from app.domains.service_locator import ServiceLocator
        
        locator = ServiceLocator.get_instance()
        domains = locator.list_domains()
        
        assert "chemistry" in domains
        assert "biology" in domains
        assert "physics" in domains
    
    def test_service_locator_lists_services_by_domain(self):
        """Test listing services for a specific domain."""
        from app.domains.service_locator import ServiceLocator
        
        locator = ServiceLocator.get_instance()
        chemistry_services = locator.list_services("chemistry")
        
        assert "ComputationalChemistryService" in chemistry_services
        assert "GNOMEMaterialsService" in chemistry_services
    
    def test_service_locator_get_service_by_name(self):
        """Test getting a service by name."""
        from app.domains.service_locator import ServiceLocator
        from app.services.base_service import BaseService
        
        locator = ServiceLocator.get_instance()
        
        # GenomicsService should be instantiable
        service = locator.get_service("GenomicsService")
        
        assert service is not None
        assert isinstance(service, BaseService)
    
    def test_service_locator_singleton_caching(self):
        """Test that singleton services return same instance."""
        from app.domains.service_locator import ServiceLocator
        
        locator = ServiceLocator.get_instance()
        
        service1 = locator.get_service("GenomicsService")
        service2 = locator.get_service("GenomicsService")
        
        assert service1 is service2
    
    def test_service_locator_force_new_instance(self):
        """Test forcing a new instance bypasses cache."""
        from app.domains.service_locator import ServiceLocator
        
        locator = ServiceLocator.get_instance()
        
        service1 = locator.get_service("GenomicsService")
        service2 = locator.get_service("GenomicsService", force_new=True)
        
        assert service1 is not service2
    
    def test_service_locator_raises_on_unknown_service(self):
        """Test that unknown services raise KeyError."""
        from app.domains.service_locator import ServiceLocator
        
        locator = ServiceLocator.get_instance()
        
        with pytest.raises(KeyError) as exc_info:
            locator.get_service("NonExistentService")
        
        assert "NonExistentService" in str(exc_info.value)
    
    def test_convenience_functions(self):
        """Test module-level convenience functions."""
        from app.domains.service_locator import get_service, list_services
        
        # get_service should work
        service = get_service("GenomicsService")
        assert service is not None
        
        # list_services should work
        services = list_services("biology")
        assert "GenomicsService" in services


class TestDomainServiceCompatibility:
    """Test that domain services work with autonomous loops."""
    
    @pytest.mark.asyncio
    async def test_service_can_be_called_via_process_request(self):
        """Verify services can be invoked uniformly via process_request."""
        from app.domains.service_locator import get_service
        
        service = get_service("GenomicsService")
        
        # The autonomous loops call services via process_request
        result = await service.process_request({
            "timestamp": "2024-01-01T00:00:00Z",
            "operation": "validate_environment"
        })
        
        assert result["success"] is True
        assert "result" in result
        assert "docker_available" in result["result"]
    
    def test_service_definition_metadata(self):
        """Test that service definitions contain useful metadata."""
        from app.domains.service_locator import ServiceLocator
        
        locator = ServiceLocator.get_instance()
        definition = locator.get_definition("GenomicsService")
        
        assert definition is not None
        assert definition.domain == "biology"
        assert definition.class_name == "GenomicsService"
        assert "genomics" in definition.tags


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
