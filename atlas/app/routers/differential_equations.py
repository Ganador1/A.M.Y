"""Compatibility wrapper for the differential equations router."""

from app.domains.mathematics.routers.differential_equations import (
    router as differential_equations_router,
)

router = differential_equations_router

__all__ = ["router"]
