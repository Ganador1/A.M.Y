"""External Service Exceptions"""

from app.exceptions.base import AtlasExternalError


class ServiceUnavailableError(AtlasExternalError):
    """External service unavailable"""
    pass


class TimeoutError(ServiceUnavailableError):
    """External service timeout"""
    pass


class AuthenticationError(AtlasExternalError):
    """Authentication or authorization error when calling external services"""
    pass