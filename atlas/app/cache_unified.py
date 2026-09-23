"""Compatibility module exposing `unified_cache` implementations when
`app.cache.unified_cache` import path is not available (e.g., when
`app/cache.py` shadows the package layout).

This is a pragmatic compatibility shim for the test environment.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

_unified_path = Path(__file__).parent / "cache" / "unified_cache.py"
if _unified_path.exists():
    spec = importlib.util.spec_from_file_location("app.cache.unified_cache", str(_unified_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    # Re-export commonly-used symbols
    for name in [
        'UnifiedCache', 'CacheConfig', 'CacheStats', 'CacheItem',
        'CacheBackend', 'CompressionType', 'EvictionPolicy',
        'MemoryCacheBackend', 'FileCacheBackend',
        'unified_cache', 'cache_get', 'cache_set', 'cache_delete'
    ]:
        if hasattr(module, name):
            globals()[name] = getattr(module, name)
else:
    # Minimal fallbacks to avoid import errors in environments without the file
    class CacheBackend:  # pragma: no cover - fallback
        pass
    class CompressionType:  # pragma: no cover
        pass
    class EvictionPolicy:  # pragma: no cover
        pass
    class CacheConfig:  # pragma: no cover
        pass
    class CacheStats:  # pragma: no cover
        pass
    class CacheItem:  # pragma: no cover
        pass
    class MemoryCacheBackend:  # pragma: no cover
        pass
    class FileCacheBackend:  # pragma: no cover
        pass

    def cache_get(*_a, **_k):  # pragma: no cover
        return None

    def cache_set(*_a, **_k):  # pragma: no cover
        return False

    def cache_delete(*_a, **_k):  # pragma: no cover
        return False
