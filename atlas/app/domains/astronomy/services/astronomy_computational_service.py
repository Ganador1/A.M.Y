"""Compatibility wrapper for the Astronomy computational service.

This module keeps backwards compatibility with legacy imports that expect
``app.services.astronomy_computational_service`` while the canonical implementation
lives under ``app.domains.astronomy``.  Importing from this module ensures the
advanced domain service is always used and that shared symbols such as
``ML_AVAILABLE`` remain accessible.
"""

from __future__ import annotations

from app.domains.astronomy.astronomy_computational_service import (  # noqa: F401
    AstronomyComputationalService as _DomainAstronomyComputationalService,
    ML_AVAILABLE,
    SCIPY_AVAILABLE,
)

__all__ = [
    "AstronomyComputationalService",
    "ML_AVAILABLE",
    "SCIPY_AVAILABLE",
]


class AstronomyComputationalService(_DomainAstronomyComputationalService):
    """Thin proxy subclass for backwards compatibility."""
