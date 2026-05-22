"""Tool Adapter Cache (MVP)

LRU cache con TTL para resultados de tool adapters.
- Caching por hash de input cuando allow_cache=True
- Configuración via environment (tamaño, TTL)
- Thread-safe para acceso concurrente
"""
from __future__ import annotations
import time
import threading
from typing import Any, Dict, Optional
from collections import OrderedDict
import os
from app.config import settings

class CacheEntry:
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.expires_at = time.time() + ttl_seconds

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

class ToolAdapterCache:
    def __init__(self, max_size: int = 100, default_ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self._misses += 1
                return None
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None
            # Move to end (LRU)
            self._cache.move_to_end(key)
            self._hits += 1
            return entry.value

    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            ttl = ttl or self.default_ttl
            self._cache[key] = CacheEntry(value, ttl)
            self._cache.move_to_end(key)
            # Evict if over limit
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def stats(self) -> Dict[str, Any]:
        with self._lock:
            total = self._hits + self._misses
            hit_rate = (self._hits / total) if total > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
            }

# Configure from environment (safe fallbacks)
# Prefer settings lower-case attributes; fall back to environment; then defaults
_MAX_SIZE = int(os.getenv("TOOL_ADAPTER_CACHE_SIZE", getattr(settings, "tool_adapter_cache_size", "100")))
_DEFAULT_TTL = int(os.getenv("TOOL_ADAPTER_CACHE_TTL", getattr(settings, "tool_adapter_cache_ttl", "300")))

# Global cache instance
tool_adapter_cache = ToolAdapterCache(_MAX_SIZE, _DEFAULT_TTL)