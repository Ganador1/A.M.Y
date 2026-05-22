"""Engineering Domain Exceptions"""

from app.exceptions.base import AtlasDomainError


class EngineeringError(AtlasDomainError):
    """Base exception for engineering domain"""
    pass


class MaterialsError(EngineeringError):
    """Errores en ciencia de materiales"""
    pass


class ManufacturingError(EngineeringError):
    """Errores en manufactura"""
    pass