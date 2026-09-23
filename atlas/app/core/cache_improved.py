"""
Fixed: Advanced Cache compatibility layer.
This file was causing an infinite import loop. Now it properly delegates to the working cache system.
"""
from __future__ import annotations

from typing import Any, Dict, Optional
from app.core.cache import DistributedCache as BaseDistributedCache, cache as base_cache, cached as base_cached

# Fix: Create working aliases instead of circular imports
class AdvancedDistributedCache(BaseDistributedCache):
    """Enhanced cache that delegates to the working base implementation"""
    pass

class CacheMetrics:
    """Cache metrics stub"""
    def __init__(self):
        pass

class CacheEntry:
    """Cache entry stub"""
    def __init__(self, value: Any, ttl: Optional[int] = None):
        self.value = value
        self.ttl = ttl

class CacheAnalytics:
    """Cache analytics stub"""
    def __init__(self):
        pass

# Working instances
advanced_cache = base_cache
intelligent_cache_decorator = base_cached

# Legacy compatibility
DistributedCache = AdvancedDistributedCache  
cache = advanced_cache
cached = intelligent_cache_decorator

__all__ = [
    "AdvancedDistributedCache",
    "DistributedCache",  # Legacy compatibility
    "advanced_cache",
    "cache",  # Legacy compatibility
    "intelligent_cache_decorator", 
    "cached",  # Legacy compatibility
    "CacheMetrics",
    "CacheEntry", 
    "CacheAnalytics"
]
