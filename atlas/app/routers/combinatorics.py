"""Compatibility wrapper for the combinatorics router."""

from app.domains.mathematics.routers.combinatorics import (
    router as combinatorics_router,
)

router = combinatorics_router

__all__ = ["router"]
