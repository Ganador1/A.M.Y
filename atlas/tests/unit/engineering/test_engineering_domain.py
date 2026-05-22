import pytest
from app.domains.service_locator import ServiceLocator, get_service
from app.domains.engineering.services.additive_manufacturing_service import AdditiveManufacturingService

class TestEngineeringDomain:
    
    @pytest.fixture(autouse=True)
    def setup_locator(self):
        # Ensure locator is initialized
        ServiceLocator.get_instance()

    def test_services_registered(self):
        services = ServiceLocator.get_instance().list_services(domain="engineering")
        assert "AdditiveManufacturingService" in services

    def test_get_additive_manufacturing_service(self):
        service = get_service("AdditiveManufacturingService")
        assert isinstance(service, AdditiveManufacturingService)
        assert service.name == "AdditiveManufacturingService"
