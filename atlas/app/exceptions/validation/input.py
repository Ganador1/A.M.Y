"""Input Validation Exceptions"""

from app.exceptions.base import AtlasValidationError


class InputValidationError(AtlasValidationError):
    """Error de validación de input"""
    pass


class SchemaError(InputValidationError):
    """Error en esquema de datos"""
    pass


class SchemaValidationError(SchemaError):
    """Compatibility alias for schema validation failures."""


class ParameterValidationError(InputValidationError):
    """Validation error for an individual parameter."""
