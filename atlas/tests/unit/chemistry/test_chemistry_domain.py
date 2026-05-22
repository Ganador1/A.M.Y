import pytest
from app.domains.service_locator import ServiceLocator, get_service
from app.domains.chemistry.services.chemml_service import ChemMLService
from app.domains.chemistry.services.materials_discovery_service import MaterialsDiscoveryService
from app.domains.chemistry.services.xray_crystallography_service import XRayCrystallographyService

class TestChemistryDomain:
    
    @pytest.fixture(autouse=True)
    def setup_locator(self):
        # Ensure locator is initialized
        ServiceLocator.get_instance()

    def test_services_registered(self):
        services = ServiceLocator.get_instance().list_services(domain="chemistry")
        assert "ChemMLService" in services
        assert "MaterialsDiscoveryService" in services
        assert "XRayCrystallographyService" in services

    def test_get_chemml_service(self):
        service = get_service("ChemMLService")
        assert isinstance(service, ChemMLService)
        assert service.name == "ChemMLService"

    def test_get_materials_discovery_service(self):
        service = get_service("MaterialsDiscoveryService")
        assert isinstance(service, MaterialsDiscoveryService)
        assert service.name == "MaterialsDiscoveryService"

    def test_get_xray_crystallography_service(self):
        service = get_service("XRayCrystallographyService")
        assert isinstance(service, XRayCrystallographyService)
        assert service.name == "xray_crystallography"
