"""Cache Exceptions"""

from app.exceptions.base import AtlasInfrastructureError


class CacheError(AtlasInfrastructureError):
    """Base cache error"""
    pass


class RedisError(CacheError):
    """Redis operation failed"""
    pass


class CacheMissError(CacheError):
    """Requested key not found in cache"""
    pass