"""API Exceptions"""

from app.exceptions.base import AtlasInfrastructureError


class APIError(AtlasInfrastructureError):
    """Base API error"""
    pass


class RateLimitError(APIError):
    """Exceeded API rate limits"""
    pass


class BadGatewayError(APIError):
    """Upstream service returned bad gateway"""
    pass