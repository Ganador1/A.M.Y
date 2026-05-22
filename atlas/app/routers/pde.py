"""Compatibility wrapper for the partial differential equations router."""

from app.domains.mathematics.routers.pde import router as pde_router

router = pde_router

__all__ = ["router"]
