import pytest
from app.domains.service_locator import ServiceLocator, get_service

class TestServiceLocatorComprehensive:
    
    @pytest.fixture(autouse=True)
    def setup_locator(self):
        ServiceLocator.get_instance()

    def test_all_domains_registered(self):
        locator = ServiceLocator.get_instance()
        
        # Physics
        physics_services = locator.list_services(domain="physics")
        assert "ParticlePhysicsService" in physics_services
        assert "QuantumComputingService" in physics_services
        assert "SolidStatePhysicsService" in physics_services
        assert "PlasmaPhysicsService" in physics_services
        assert "PhysicsInformedNNService" in physics_services
        assert "GravitationalLensingService" in physics_services
        assert "QuantumPhysicsService" in physics_services
        
        # Chemistry
        chemistry_services = locator.list_services(domain="chemistry")
        assert "ChemMLService" in chemistry_services
        assert "MaterialsDiscoveryService" in chemistry_services
        assert "XRayCrystallographyService" in chemistry_services
        
        # Engineering
        engineering_services = locator.list_services(domain="engineering")
        assert "AdditiveManufacturingService" in engineering_services
        
        # Medicine
        medicine_services = locator.list_services(domain="medicine")
        assert "AdvancedMedicalImagingService" in medicine_services
        assert "ClinicalBERTService" in medicine_services
        assert "AlphaFold3ProteinStructureService" in medicine_services
        
        # Astronomy
        astronomy_services = locator.list_services(domain="astronomy")
        assert "AstronomicalMLService" in astronomy_services
        
        # Neuroscience
        neuroscience_services = locator.list_services(domain="neuroscience")
        assert "NeuroscienceLightService" in neuroscience_services

    def test_get_service_instantiation(self):
        # Test instantiation of one service from each domain to ensure paths are correct
        
        # Physics
        assert get_service("ParticlePhysicsService") is not None
        
        # Chemistry
        assert get_service("ChemMLService") is not None
        
        # Engineering
        assert get_service("AdditiveManufacturingService") is not None
        
        # Medicine
        assert get_service("AdvancedMedicalImagingService") is not None
        
        # Astronomy
        assert get_service("AstronomicalMLService") is not None
        
        # Neuroscience
        assert get_service("NeuroscienceLightService") is not None
