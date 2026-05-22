"""Output Validation Exceptions"""

from app.exceptions.base import AtlasValidationError


class OutputValidationError(AtlasValidationError):
    """Error de validación de output"""
    pass


class ResultValidationError(OutputValidationError):
    """Validation error for a computed result payload."""
