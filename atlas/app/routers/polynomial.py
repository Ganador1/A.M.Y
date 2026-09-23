"""Compatibility wrapper for the polynomial algebra router."""

from app.domains.mathematics.routers.polynomial import (
    router as polynomial_router,
)

router = polynomial_router

__all__ = ["router"]
