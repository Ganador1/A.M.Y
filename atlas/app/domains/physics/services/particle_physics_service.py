"""
Compatibility wrapper for particle_physics_service.
Re-exports the service from the domains structure.
"""

from app.domains.physics.quantum.particle_physics_service import (
    ParticlePhysicsService,
    ParticleEvent,
    JetAnalysisResult,
    ResonanceSearch,
    _check_root_stack,
)

__all__ = [
    "ParticlePhysicsService",
    "ParticleEvent",
    "JetAnalysisResult",
    "ResonanceSearch",
    "_check_root_stack",
]