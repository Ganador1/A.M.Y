import pytest
import asyncio
from app.domains.physics.quantum.particle_physics_service import ParticlePhysicsService
from app.exceptions.domain.physics import ParticlePhysicsError

class TestParticlePhysicsService:
    
    @pytest.fixture
    def service(self):
        return ParticlePhysicsService()

    @pytest.mark.asyncio
    async def test_initialization(self, service):
        assert service.name == "ParticlePhysicsService"
        assert hasattr(service, "root_available")
        assert hasattr(service, "jet_algorithms")

    @pytest.mark.asyncio
    async def test_process_request_info(self, service):
        result = await service.process_request({"operation": "info"})
        assert "capabilities" in result
        assert "advanced_event_analysis" in result["capabilities"]
        assert "root_available" in result

    @pytest.mark.asyncio
    async def test_process_request_unknown_operation(self, service):
        result = await service.process_request({"operation": "unknown"})
        assert "error" in result
        assert "Unknown operation" in result["error"]

    @pytest.mark.asyncio
    async def test_analyze_events_empty(self, service):
        result = await service.process_request({
            "operation": "event_analysis",
            "events": []
        })
        assert "error" in result
        assert "No events provided" in result["error"]
