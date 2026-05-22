"""
Compatibility shim for legacy imports of cache utilities.
Re-exports the DistributedCache and cache decorator from the new location.
"""
from app.core.cache import (
    DistributedCache,
    cache,
)

__all__ = [
    "DistributedCache",
    "cache",
]