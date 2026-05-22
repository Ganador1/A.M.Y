"""
Compatibility wrapper for math_physics router.
Re-exports the router from the domains structure.
"""

from app.domains.mathematics.routers.math_physics import router

__all__ = ["router"]