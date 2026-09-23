"""
AXIOM ATLAS - Base Exception Framework
Jerarquía base de excepciones para todo el sistema.
"""

from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AtlasException(Exception):
    """
    Excepción base para todo el sistema AXIOM ATLAS.

    Todas las excepciones custom deben heredar de esta clase.
    """

    def __init__(
        self,
        message: str,
        *,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.cause = cause

        # Log automático de la excepción
        logger.error(
            f"{self.error_code}: {message}",
            extra={"details": self.details, "cause": str(cause) if cause else None},
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializar excepción para APIs"""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }


class AtlasValidationError(AtlasException):
    """Errores de validación de datos de entrada"""
    pass


class AtlasInfrastructureError(AtlasException):
    """Errores de infraestructura (DB, cache, storage)"""
    pass


class AtlasDomainError(AtlasException):
    """Errores específicos de dominio científico"""
    pass


class MathematicsError(AtlasDomainError):
    """Errores específicos del dominio de Matemáticas"""
    pass


class AtlasExternalError(AtlasException):
    """Errores de servicios externos (APIs, LLMs)"""
    pass


class AtlasSecurityError(AtlasException):
    """Errores de seguridad y ética"""
    pass


def handle_atlas_errors(default_message: str = "Operation failed"):
    """
    Decorator para convertir excepciones genéricas en AtlasException

    Uso:
        @handle_atlas_errors("Failed to process data")
        def process_data(data):
            # ...
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AtlasException:
                # Re-raise Atlas exceptions
                raise
            except Exception as e:
                # Convert to Atlas exception
                raise AtlasException(
                    default_message,
                    details={"original_error": str(e), "function": func.__name__},
                    cause=e,
                ) from e
        return wrapper

    return decorator


def handle_atlas_errors_async(default_message: str = "Operation failed"):
    """Versión async de handle_atlas_errors"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except AtlasException:
                raise
            except Exception as e:
                raise AtlasException(
                    default_message,
                    details={"original_error": str(e), "function": func.__name__},
                    cause=e,
                ) from e
        return wrapper

    return decorator