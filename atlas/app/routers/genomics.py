"""Compatibility wrapper for the genomics router."""

from app.domains.biology.routers.genomics import router as genomics_router

router = genomics_router

__all__ = ["router"]
