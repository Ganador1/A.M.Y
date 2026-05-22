"""
Compatibility wrapper for quantum_algorithms router.
Re-exports from app.domains.physics.routers.quantum_algorithms
"""

from app.domains.physics.routers.quantum_algorithms import router

__all__ = ["router"]