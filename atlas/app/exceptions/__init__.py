"""
AXIOM ATLAS - Exceptions Package

Exporta las clases base y categorías principales de excepciones.
"""

from .base import (
    AtlasException,
    AtlasValidationError,
    AtlasInfrastructureError,
    AtlasDomainError,
    AtlasExternalError,
    AtlasSecurityError,
    handle_atlas_errors,
    handle_atlas_errors_async,
)