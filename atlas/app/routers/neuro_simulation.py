"""
Compatibility wrapper for neuro_simulation router.
Re-exports the router from the domains structure.
"""

from app.domains.neuroscience.routers.simulation.neuro_simulation import router

__all__ = ["router"]