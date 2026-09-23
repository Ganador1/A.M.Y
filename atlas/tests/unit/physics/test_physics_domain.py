import pytest
from app.domains.service_locator import ServiceLocator, get_service
from app.domains.physics.quantum.particle_physics_service import ParticlePhysicsService
from app.domains.physics.quantum.quantum_computing_service import QuantumComputingService
from app.domains.physics.computational.solid_state_physics_service import SolidStatePhysicsService
from app.domains.physics.plasma.plasma_physics_service import PlasmaPhysicsService
from app.domains.physics.computational.physics_informed_nn_service import PhysicsInformedNNService

class TestPhysicsDomain:
    
    @pytest.fixture(autouse=True)
    def setup_locator(self):
        # Ensure locator is initialized
        ServiceLocator.get_instance()

    def test_services_registered(self):
        services = ServiceLocator.get_instance().list_services(domain="physics")
        assert "ParticlePhysicsService" in services
        assert "QuantumComputingService" in services
        assert "SolidStatePhysicsService" in services
        assert "PlasmaPhysicsService" in services
        assert "PhysicsInformedNNService" in services

    def test_get_particle_physics_service(self):
        service = get_service("ParticlePhysicsService")
        assert isinstance(service, ParticlePhysicsService)
        assert service.name == "ParticlePhysicsService"

    def test_get_quantum_computing_service(self):
        service = get_service("QuantumComputingService")
        assert isinstance(service, QuantumComputingService)
        
    def test_get_solid_state_physics_service(self):
        service = get_service("SolidStatePhysicsService")
        assert isinstance(service, SolidStatePhysicsService)
        assert service.name == "SolidStatePhysics"

    def test_get_plasma_physics_service(self):
        service = get_service("PlasmaPhysicsService")
        assert isinstance(service, PlasmaPhysicsService)
        assert service.name == "PlasmaPhysicsService"

    def test_get_pinn_service(self):
        service = get_service("PhysicsInformedNNService")
        assert isinstance(service, PhysicsInformedNNService)
        assert service.name == "PhysicsInformedNN"
