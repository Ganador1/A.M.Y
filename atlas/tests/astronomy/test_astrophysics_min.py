import asyncio
import pytest

from app.services.astronomy_computational_service import AstronomyComputationalService
from app.services.particle_physics_service import ParticlePhysicsService


@pytest.mark.asyncio
async def test_astronomy_transit_detection_min():
    svc = AstronomyComputationalService()
    # Curva de luz simple con tránsito en el centro
    light_curve = []
    for i in range(60):
        flux = 1.0
        if 25 <= i <= 30:
            flux = 0.98  # caída de 2%
        light_curve.append({"time": float(i), "flux": flux})
    res = await svc.process_request({"operation": "exoplanet_transit", "light_curve": light_curve})
    assert res.get("success") is True
    assert res.get("estimated_depth") is not None


@pytest.mark.asyncio
async def test_particle_physics_stub():
    svc = ParticlePhysicsService()
    particles = [
        {"pt": 10.0, "px": 1.0},
        {"pt": 45.0, "px": -1.0},
        {"pt": 60.0, "px": 0.5},
    ]
    summary = await svc.process_request({"operation": "event_summary", "particles": particles})
    assert summary.get("success") is True
    jets = await svc.process_request({"operation": "jet_counting", "particles": particles})
    assert jets.get("n_jets") == 2
