"""Medicine Domain Exceptions"""

from app.exceptions.base import AtlasDomainError


class MedicalError(AtlasDomainError):
    """Base exception for medicine domain"""
    pass


class DiagnosticError(MedicalError):
    """Errores en diagnóstico"""
    pass


class ImagingError(MedicalError):
    """Errores en imagen médica"""
    pass