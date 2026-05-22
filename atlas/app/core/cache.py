"""
AXIOM Caching System
Advanced distributed caching system with Redis Cluster support and intelligent strategies
"""

import hashlib
import json
import time
from typing import Any, Dict, Optional
from functools import wraps
import redis
import asyncio
try:
    import aioredis  # Optional; used if available
except ImportError:
    aioredis = None  # type: ignore
from app.core.config import settings
from app.core.bootstrap_logging import logger


class DistributedCache:
    """Distributed cache with Redis Cluster support and intelligent caching strategies"""

    def __init__(self, max_size: int = 10000, default_ttl: int = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.redis_client = None
        self.cluster_mode = False
        self.fallback_cache: Dict[str, Dict[str, Any]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self._connect_redis()

    def _connect_redis(self):
        """Connect to Redis with cluster support and error handling"""
        if not settings.enable_redis_cache or not settings.redis_url:
            logger.info("Redis cache disabled or not configured")
            return

        try:
            # Try cluster connection first
            if "cluster" in settings.redis_url.lower():
                from redis.cluster import RedisCluster
                self.redis_client = RedisCluster.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                self.cluster_mode = True
                logger.info("Redis Cluster connected successfully")
            else:
                # Standard Redis connection
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    db=settings.redis_db,
                    password=settings.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True
                )
                self.cluster_mode = False
                logger.info("Redis cache connected successfully")

            # Test connection
            self.redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback")
            self.redis_client = None
        except Exception as e:
            logger.error(f"Unexpected Redis error: {e}. Using in-memory fallback")
            self.redis_client = None

    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from function arguments using SHA-256"""
        key_data = {
            "args": args,
            "kwargs": kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def _get_cache_strategy(self, operation_type: str) -> Dict[str, Any]:
        """Get caching strategy based on operation type"""
        strategies = {
            'arithmetic': {
                'ttl': 1800,  # 30 minutes
                'max_size': 5000,
                'strategy': 'LRU',
                'compression': False
            },
            'calculus': {
                'ttl': 3600,  # 1 hour
                'max_size': 3000,
                'strategy': 'LFU',
                'compression': True
            },
            'scientific': {
                'ttl': 7200,  # 2 hours
                'max_size': 2000,
                'strategy': 'TTL',
                'compression': True
            },
            'matrix': {
                'ttl': 1800,  # 30 minutes
                'max_size': 1000,
                'strategy': 'SIZE',
                'compression': True
            },
            'oeis_search': {
                'ttl': 21600,  # 6 hours default (will be overridden by intelligent TTL)
                'max_size': 10000,
                'strategy': 'LRU',
                'compression': True
            }
        }
        return strategies.get(operation_type, {
            'ttl': settings.cache_ttl,
            'max_size': 1000,
            'strategy': 'LRU',
            'compression': False
        })

    async def get(self, key: str, operation_type: str = 'default') -> Optional[Any]:
        """Get value from cache with hit/miss tracking (async)"""
        if self.redis_client:
            try:
                # Use async Redis client if available
                if hasattr(self.redis_client, 'get'):
                    data = await self.redis_client.get(key)
                else:
                    # Fallback to sync for now
                    data = self.redis_client.get(key)
                
                if data and isinstance(data, str):
                    self.cache_hits += 1
                    logger.debug(f"Redis cache hit for key: {key}")
                    return json.loads(data)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
                # Fall back to in-memory
                return self._get_fallback(key)
        else:
            return self._get_fallback(key)

        self.cache_misses += 1
        return None

    def _get_fallback(self, key: str) -> Optional[Any]:
        """Get from in-memory fallback cache"""
        if key in self.fallback_cache:
            entry = self.fallback_cache[key]
            if time.time() < entry["expires"]:
                logger.debug(f"Fallback cache hit for key: {key}")
                return entry["value"]
            else:
                del self.fallback_cache[key]
        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None, operation_type: str = 'default') -> None:
        """Set value in cache with intelligent strategy"""
        strategy = self._get_cache_strategy(operation_type)
        ttl_value = ttl or strategy['ttl']

        # Compress if needed
        if strategy['compression'] and isinstance(value, (dict, list)):
            try:
                import gzip
                compressed_value = gzip.compress(json.dumps(value).encode())
                value = {"__compressed__": True, "data": compressed_value.decode('latin1')}
            except ImportError:
                pass  # Compression not available

        if self.redis_client:
            try:
                # Support both sync and async Redis clients without using await in sync method
                if hasattr(self.redis_client, 'setex'):
                    res = self.redis_client.setex(key, ttl_value, json.dumps(value))
                    # If async client returns coroutine, run it appropriately
                    if asyncio.iscoroutine(res):
                        try:
                            loop = asyncio.get_event_loop()
                            if loop.is_running():
                                loop.create_task(res)
                            else:
                                loop.run_until_complete(res)
                        except RuntimeError:
                            asyncio.run(res)
                else:
                    # Fallback to sync for now
                    self.redis_client.setex(key, ttl_value, json.dumps(value))
                logger.debug(f"Redis cache set for key: {key} (TTL: {ttl_value}s)")
                return
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
                # Fall back to in-memory

        # Fallback to in-memory cache
        self._set_fallback(key, value, ttl_value)

    def _set_fallback(self, key: str, value: Any, ttl: int) -> None:
        """Set in fallback in-memory cache with eviction"""
        if len(self.fallback_cache) >= self.max_size:
            # Remove oldest entry based on access time
            oldest_key = min(self.fallback_cache.keys(),
                           key=lambda k: self.fallback_cache[k].get("last_access", 0))
            del self.fallback_cache[oldest_key]
            logger.debug(f"Fallback cache eviction: removed {oldest_key}")

        expires = time.time() + ttl
        self.fallback_cache[key] = {
            "value": value,
            "expires": expires,
            "created": time.time(),
            "last_access": time.time()
        }
        logger.debug(f"Fallback cache set for key: {key}")

    def clear(self, pattern: str = "*") -> None:
        """Clear cache entries with pattern support"""
        if self.redis_client:
            try:
                if self.cluster_mode:
                    # For cluster mode, we need to handle pattern deletion differently
                    keys = self.redis_client.keys(pattern)
                    if keys and isinstance(keys, list):
                        self.redis_client.delete(*keys)
                else:
                    self.redis_client.delete(pattern)
                logger.info(f"Redis cache cleared with pattern: {pattern}")
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")

        # Clear fallback cache
        keys_to_remove = [k for k in self.fallback_cache.keys() if pattern == "*" or pattern in k]
        for key in keys_to_remove:
            del self.fallback_cache[key]
        logger.info(f"Fallback cache cleared: {len(keys_to_remove)} entries removed")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        stats = {
            "redis_enabled": self.redis_client is not None,
            "cluster_mode": self.cluster_mode,
            "fallback_entries": len(self.fallback_cache),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_ratio": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }

        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                if isinstance(redis_info, dict):
                    stats.update({
                        "redis_connected": True,
                        "redis_keys": self.redis_client.dbsize() if not self.cluster_mode else "N/A (cluster)",
                        "redis_memory_used": redis_info.get("used_memory_human", "unknown"),
                        "redis_uptime": redis_info.get("uptime_in_seconds", 0),
                        "redis_version": redis_info.get("redis_version", "unknown")
                    })
                else:
                    stats.update({
                        "redis_connected": True,
                        "redis_keys": "N/A",
                        "redis_memory_used": "unknown",
                        "redis_uptime": 0,
                        "redis_version": "unknown"
                    })
            except Exception as e:
                logger.warning(f"Redis stats error: {e}")
                stats["redis_connected"] = False
        else:
            stats["redis_connected"] = False

        # Fallback stats
        now = time.time()
        valid_entries = sum(1 for entry in self.fallback_cache.values()
                          if now < entry["expires"])

        stats.update({
            "fallback_total_entries": len(self.fallback_cache),
            "fallback_valid_entries": valid_entries,
            "fallback_expired_entries": len(self.fallback_cache) - valid_entries,
            "fallback_max_size": self.max_size,
            "fallback_memory_usage_mb": len(json.dumps(self.fallback_cache)) / (1024 * 1024)
        })

        return stats

    def preload_common_operations(self) -> None:
        """Preload commonly used mathematical constants and functions"""
        common_values = {
            "pi": 3.141592653589793,
            "e": 2.718281828459045,
            "golden_ratio": 1.618033988749895,
            "euler_gamma": 0.5772156649015329
        }

        for key, value in common_values.items():
            cache_key = f"constant:{key}"
            self.set(cache_key, value, ttl=86400, operation_type='arithmetic')  # 24 hours

        logger.info("Preloaded common mathematical constants into cache")


# Global cache instance
cache = DistributedCache()


def cached(ttl: Optional[int] = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Skip caching for complex objects or when disabled
            if settings.debug or len(args) > 10:
                return func(*args, **kwargs)

            key = cache._generate_key(func.__name__, *args, **kwargs)

            # Try to get from cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result

            # Compute result
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            # Cache result if computation took significant time
            if duration > 0.1:  # More than 100ms
                cache.set(key, result, ttl)

            return result

        return wrapper
    return decorator


def cache_key(*args, **kwargs) -> str:
    """Generate cache key for manual caching"""
    return cache._generate_key(*args, **kwargs)


__all__ = [
    "DistributedCache",
    "cache",
    "cached",
    "cache_key",
]