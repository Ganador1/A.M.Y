"""Compatibility wrapper for the relocated advanced algebra router.

This module preserves legacy imports from ``app.routers.advanced_algebra``
by delegating to the refactored router that now lives inside the
mathematics domain package.
"""

from app.domains.mathematics.routers.advanced_algebra import (
    router as advanced_algebra_router,
)

# Re-export for FastAPI router registry compatibility
router = advanced_algebra_router

__all__ = ["router"]
