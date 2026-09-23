"""Compatibility wrapper for the advanced genomics router."""

from app.domains.biology.routers.advanced_genomics import (
    router as advanced_genomics_router,
)

router = advanced_genomics_router

__all__ = ["router"]
