"""Compatibility wrapper for the variational calculus router."""

from app.domains.mathematics.routers.variational_calculus import (
    router as variational_calculus_router,
)

router = variational_calculus_router

__all__ = ["router"]
