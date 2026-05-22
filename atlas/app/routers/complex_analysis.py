"""Compatibility wrapper for the complex analysis router."""

from app.domains.mathematics.routers.complex_analysis import (
    router as complex_analysis_router,
)

router = complex_analysis_router

__all__ = ["router"]
