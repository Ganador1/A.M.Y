"""Compatibility wrapper for the number theory router."""

from app.domains.mathematics.routers.number_theory import (
    router as number_theory_router,
)

router = number_theory_router

__all__ = ["router"]
