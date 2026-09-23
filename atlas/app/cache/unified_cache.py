"""
Unified Caching System - Sistema de caché unificado para AXIOM ATLAS
===================================================================

Este módulo implementa un sistema de caché unificado que proporciona múltiples
backends de almacenamiento (memoria, Redis, archivos) con una interfaz común.
Incluye funcionalidades avanzadas como invalidación automática, compresión,
serialización y monitoreo de rendimiento.

Funcionalidades:
- Múltiples backends: memoria, Redis, archivos
- Invalidación automática por TTL y patrones
- Compresión y serialización automática
- Monitoreo de hit/miss rates
- Estrategias de evicción configurables
- Cache warming y preloading
- Integración con sistemas de observabilidad

Author: AXIOM Team
Date: 2025-01-01
Version: 1.0.0
"""

import time
import json
import msgpack
import hashlib
import threading
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
import logging
import gzip
import zlib
from collections import OrderedDict
from enum import Enum
import aiofiles
import math

logger = logging.getLogger(__name__)


class CacheBackend(Enum):
    """Tipos de backend de caché disponibles."""
    MEMORY = "memory"
    REDIS = "redis"
    FILE = "file"


class CompressionType(Enum):
    """Tipos de compresión disponibles."""
    NONE = "none"
    GZIP = "gzip"
    ZLIB = "zlib"


class EvictionPolicy(Enum):
    """Políticas de evicción de caché."""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    RANDOM = "random"


@dataclass
class CacheConfig:
    """Configuración del sistema de caché."""
    
    # Backend principal
    backend: CacheBackend = CacheBackend.MEMORY
    
    # Configuración de memoria
    max_memory_size: int = 100 * 1024 * 1024  # 100MB
    max_memory_items: int = 10000
    
    # Configuración de Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # Configuración de archivos
    file_cache_dir: str = "cache/files"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Configuración general
    default_ttl: int = 3600  # 1 hora
    compression: CompressionType = CompressionType.GZIP
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    
    # Configuración de monitoreo
    enable_monitoring: bool = True
    monitoring_interval: int = 300  # 5 minutos
    
    # Configuración de serialización
    serialization_format: str = "pickle"  # pickle, json
    
    # Configuración de invalidación
    enable_auto_invalidation: bool = True
    invalidation_check_interval: int = 60  # 1 minuto


@dataclass
class CacheStats:
    """Estadísticas del sistema de caché."""
    
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    evictions: int = 0
    compression_savings: float = 0.0
    total_size: int = 0
    item_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    @property
    def hit_rate(self) -> float:
        """Tasa de aciertos del caché."""
        total = self.hits + self.misses
        if total <= 0:
            return 0.0
        return round(self.hits / total, 10)
    
    @property
    def miss_rate(self) -> float:
        """Tasa de fallos del caché."""
        return round(1.0 - self.hit_rate, 10)


@dataclass
class CacheItem:
    """Elemento del caché con metadatos."""
    
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    size: int = 0
    compressed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_expired(self) -> bool:
        """Verificar si el elemento ha expirado."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    @property
    def ttl_seconds(self) -> Optional[int]:
        """Obtener TTL en segundos."""
        if self.expires_at is None:
            return None
        delta = self.expires_at - datetime.now()
        # Use ceil to avoid off-by-one issues in tests (small deltas)
        return max(0, int(math.ceil(delta.total_seconds())))


class CacheBackendInterface(ABC):
    """Interfaz abstracta para backends de caché."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheItem]:
        """Obtener elemento del caché."""
        pass
    
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establecer elemento en el caché."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Eliminar elemento del caché."""
        pass
    
    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Verificar si existe un elemento."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Limpiar todo el caché."""
        pass
    
    @abstractmethod
    async def keys(self, pattern: str = "*") -> List[str]:
        """Obtener claves que coincidan con el patrón."""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Obtener tamaño del caché."""
        pass
    
    @abstractmethod
    async def stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del backend."""
        pass


class MemoryCacheBackend(CacheBackendInterface):
    """Backend de caché en memoria."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: OrderedDict[str, CacheItem] = OrderedDict()
        self._lock = threading.RLock()
        self._stats = CacheStats()
    
    async def get(self, key: str) -> Optional[CacheItem]:
        """Obtener elemento del caché."""
        with self._lock:
            if key not in self._cache:
                self._stats.misses += 1
                return None
            
            item = self._cache[key]
            
            # Verificar expiración
            if item.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                return None
            
            # Actualizar estadísticas de acceso
            item.access_count += 1
            item.last_accessed = datetime.now()
            
            # Mover al final (LRU)
            self._cache.move_to_end(key)
            
            self._stats.hits += 1
            return item
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establecer elemento en el caché."""
        with self._lock:
            # Calcular TTL
            expires_at = None
            if ttl is not None:
                expires_at = datetime.now() + timedelta(seconds=ttl)
            elif self.config.default_ttl > 0:
                expires_at = datetime.now() + timedelta(seconds=self.config.default_ttl)

            # Crear elemento
            item = CacheItem(
                key=key,
                value=value,
                created_at=datetime.now(),
                expires_at=expires_at,
                size=self._calculate_size(value)
            )

            # Rechazar si el elemento es demasiado grande
            if item.size > self.config.max_memory_size:
                return False

            # Evictar hasta que haya espacio (siempre que sea posible)
            while len(self._cache) >= self.config.max_memory_items:
                await self._evict_item()
                # Si no se liberó espacio (cache vacía), rompemos para evitar bucle infinito
                if len(self._cache) == 0:
                    break

            # Comprobar nuevamente límites y agregar
            if len(self._cache) >= self.config.max_memory_items:
                return False

            self._cache[key] = item

            self._stats.sets += 1
            self._stats.item_count = len(self._cache)
            return True

    async def delete(self, key: str) -> bool:
        """Eliminar elemento del caché."""
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._stats.deletes += 1
                self._stats.item_count = len(self._cache)
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Verificar si existe un elemento en memoria (y no expiró)."""
        with self._lock:
            if key not in self._cache:
                return False
            item = self._cache[key]
            if item.is_expired:
                del self._cache[key]
                self._stats.misses += 1
                self._stats.item_count = len(self._cache)
                return False
            return True
    
    async def clear(self) -> bool:
        """Limpiar todo el caché."""
        with self._lock:
            self._cache.clear()
            self._stats.item_count = 0
            return True
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Obtener claves que coincidan con el patrón."""
        with self._lock:
            keys = []
            for key in self._cache.keys():
                if self._match_pattern(key, pattern):
                    if not self._cache[key].is_expired:
                        keys.append(key)
            return keys
    
    async def size(self) -> int:
        """Obtener tamaño del caché."""
        with self._lock:
            return len(self._cache)
    
    async def stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del backend."""
        with self._lock:
            total_size = sum(item.size for item in self._cache.values())
            return {
                "backend": "memory",
                "item_count": len(self._cache),
                "total_size": total_size,
                "max_size": self.config.max_memory_size,
                "max_items": self.config.max_memory_items,
                "hits": self._stats.hits,
                "misses": self._stats.misses,
                "hit_rate": self._stats.hit_rate,
                "evictions": self._stats.evictions
            }
    
    def _calculate_size(self, value: Any) -> int:
        """Calcular tamaño aproximado del valor."""
        try:
            if self.config.serialization_format == "json":
                return len(json.dumps(value, default=str).encode('utf-8'))
            else:
                return len(msgpack.packb(value))
        except Exception:  # TODO: Change to JSONDecodeError or ValueError:
            return 0
    
    def _check_limits(self, item: CacheItem) -> bool:
        """Verificar si el elemento cumple con los límites.

        Nota: no evictamos aquí automáticamente; `set` debe intentar evicción
        si es necesario antes de rechazar la inserción.
        """
        # Verificar tamaño máximo del elemento (memoria)
        if item.size > self.config.max_memory_size:
            return False

        return True
    
    async def _evict_if_needed(self):
        """Evictar elementos si es necesario."""
        while len(self._cache) > self.config.max_memory_items:
            await self._evict_item()
    
    async def _evict_item(self):
        """Evictar un elemento según la política."""
        if not self._cache:
            return
        
        if self.config.eviction_policy == EvictionPolicy.LRU:
            # Eliminar el menos recientemente usado
            key, _ = self._cache.popitem(last=False)
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            # Eliminar el menos frecuentemente usado
            key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
            del self._cache[key]
        elif self.config.eviction_policy == EvictionPolicy.TTL:
            # Eliminar el que expire primero
            key = min(self._cache.keys(), 
                     key=lambda k: self._cache[k].expires_at or datetime.max)
            del self._cache[key]
        else:  # RANDOM
            # Eliminar aleatoriamente
            key = next(iter(self._cache.keys()))
            del self._cache[key]
        
        self._stats.evictions += 1
    
    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Verificar si la clave coincide con el patrón."""
        if pattern == "*":
            return True
        
        # Implementación simple de wildcards
        import fnmatch
        return fnmatch.fnmatch(key, pattern)


class FileCacheBackend(CacheBackendInterface):
    """Backend de caché en archivos."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache_dir = Path(config.file_cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._stats = CacheStats()
        self._lock = threading.RLock()
    
    async def get(self, key: str) -> Optional[CacheItem]:
        """Obtener elemento del caché."""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            self._stats.misses += 1
            return None
        
        try:
            with self._lock:
                # Intentar lectura asíncrona cuando haya loop; si no, fallback síncrono
                data = None
                try:
                    async with aiofiles.open(file_path, 'rb') as f:
                        data = await f.read()
                except Exception:
                    # Fallback sincrónico (sensible para entornos de test sin loop)
                    try:
                        data = file_path.read_bytes()
                    except Exception as e:
                        raise

                # Descomprimir si es necesario
                if self.config.compression != CompressionType.NONE:
                    data = self._decompress(data)

                # Deserializar
                item = self._deserialize(data)

                # Verificar expiración
                if item.is_expired:
                    try:
                        file_path.unlink()
                    except Exception:
                        pass
                    self._stats.misses += 1
                    return None

                # Actualizar estadísticas de acceso
                item.access_count += 1
                item.last_accessed = datetime.now()

                # Guardar estadísticas actualizadas (intentar actualizar TTL)
                try:
                    await self.set(key, item.value, item.ttl_seconds)
                except Exception:
                    # No crítico si falla aquí
                    pass

                self._stats.hits += 1
                return item

        except Exception as e:
            logger.error(f"Error reading cache file {file_path}: {e}")
            self._stats.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establecer elemento en el caché."""
        file_path = self._get_file_path(key)
        
        try:
            with self._lock:
                # Calcular TTL
                expires_at = None
                if ttl is not None:
                    expires_at = datetime.now() + timedelta(seconds=ttl)
                elif self.config.default_ttl > 0:
                    expires_at = datetime.now() + timedelta(seconds=self.config.default_ttl)

                # Crear elemento
                item = CacheItem(
                    key=key,
                    value=value,
                    created_at=datetime.now(),
                    expires_at=expires_at,
                    size=self._calculate_size(value)
                )

                # Serializar
                data = self._serialize(item)

                # Comprimir si es necesario
                if self.config.compression != CompressionType.NONE:
                    data = self._compress(data)

                # Verificar tamaño
                if len(data) > self.config.max_file_size:
                    return False

                # Escribir archivo: preferir escritura asíncrona cuando exista loop,
                # fallback a escritura síncrona por robustez en tests.
                try:
                    try:
                        async with aiofiles.open(file_path, 'wb') as f:
                            await f.write(data)
                    except Exception:
                        # Si no se puede usar aiofiles (o falla la escritura async), hacer write síncrono
                        file_path.write_bytes(data)
                except Exception as e:
                    # Fallback final
                    logger.error(f"Error writing cache file (fallback): {e}")
                    try:
                        file_path.write_bytes(data)
                    except Exception:
                        raise

                self._stats.sets += 1
                return True

        except Exception as e:
            logger.error(f"Error writing cache file {file_path}: {e}")
            return False

    
    async def delete(self, key: str) -> bool:
        """Eliminar elemento del caché."""
        file_path = self._get_file_path(key)
        
        try:
            with self._lock:
                if file_path.exists():
                    file_path.unlink()
                    self._stats.deletes += 1
                    return True
                return False
        except Exception as e:
            logger.error(f"Error deleting cache file {file_path}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verificar si existe un elemento."""
        file_path = self._get_file_path(key)
        
        if not file_path.exists():
            return False
        
        try:
            # Verificar expiración
            item = await self.get(key)
            return item is not None
        except Exception:  # TODO: Change to IOError or FileNotFoundError
            return False
    
    async def clear(self) -> bool:
        """Limpiar todo el caché."""
        try:
            with self._lock:
                for file_path in self.cache_dir.glob("*.cache"):
                    file_path.unlink()
                return True
        except Exception as e:
            logger.error(f"Error clearing cache directory: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Obtener claves que coincidan con el patrón.

        Devuelve las claves originales (no el hash de archivo) para que las
        pruebas y consumidores puedan trabajar con las claves lógicas.
        """
        keys: List[str] = []
        try:
            with self._lock:
                for file_path in self.cache_dir.glob("*.cache"):
                    try:
                        # Leer archivo (preferir async cuando sea posible)
                        try:
                            async with aiofiles.open(file_path, 'rb') as f:
                                data = await f.read()
                        except Exception:
                            data = file_path.read_bytes()

                        if self.config.compression != CompressionType.NONE:
                            data = self._decompress(data)

                        item = self._deserialize(data)
                        if item.is_expired:
                            try:
                                file_path.unlink()
                            except Exception:
                                pass
                            continue

                        # Filtrar por patrón usando la clave original
                        if self._match_pattern(item.key, pattern):
                            keys.append(item.key)
                    except Exception:
                        # Ignorar archivos corruptos y seguir
                        logger.debug("Ignoring cache file during keys scan: %s", file_path)
                        continue
        except Exception as e:
            logger.error(f"Error listing cache keys: {e}")

        return keys
    
    async def size(self) -> int:
        """Obtener tamaño del caché."""
        try:
            with self._lock:
                return len(list(self.cache_dir.glob("*.cache")))
        except Exception:  # TODO: Use specific exception type
            return 0
    
    async def stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del backend."""
        try:
            with self._lock:
                total_size = sum(f.stat().st_size for f in self.cache_dir.glob("*.cache"))
                return {
                    "backend": "file",
                    "item_count": await self.size(),
                    "total_size": total_size,
                    "max_file_size": self.config.max_file_size,
                    "cache_dir": str(self.cache_dir),
                    "hits": self._stats.hits,
                    "misses": self._stats.misses,
                    "hit_rate": self._stats.hit_rate
                }
        except Exception:  # TODO: Change to IOError or FileNotFoundError
            return {"backend": "file", "error": "Unable to get stats"}
    
    def _get_file_path(self, key: str) -> Path:
        """Obtener ruta del archivo para una clave."""
        # Usar hash para evitar caracteres problemáticos
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def _serialize(self, item: CacheItem) -> bytes:
        """Serializar elemento."""
        if self.config.serialization_format == "json":
            data = {
                "key": item.key,
                "value": item.value,
                "created_at": item.created_at.isoformat(),
                "expires_at": item.expires_at.isoformat() if item.expires_at else None,
                "access_count": item.access_count,
                "last_accessed": item.last_accessed.isoformat(),
                "size": item.size,
                "compressed": item.compressed,
                "metadata": item.metadata
            }
            return json.dumps(data, default=str).encode('utf-8')
        else:
            # Pack a dictionary to avoid serializing dataclass objects directly
            data = {
                "key": item.key,
                "value": item.value,
                "created_at": item.created_at.isoformat(),
                "expires_at": item.expires_at.isoformat() if item.expires_at else None,
                "access_count": item.access_count,
                "last_accessed": item.last_accessed.isoformat(),
                "size": item.size,
                "compressed": item.compressed,
                "metadata": item.metadata
            }
            return msgpack.packb(data, use_bin_type=True)
    
    def _deserialize(self, data: bytes) -> CacheItem:
        """Deserializar elemento."""
        if self.config.serialization_format == "json":
            data_dict = json.loads(data.decode('utf-8'))
            return CacheItem(
                key=data_dict["key"],
                value=data_dict["value"],
                created_at=datetime.fromisoformat(data_dict["created_at"]),
                expires_at=datetime.fromisoformat(data_dict["expires_at"]) if data_dict["expires_at"] else None,
                access_count=data_dict["access_count"],
                last_accessed=datetime.fromisoformat(data_dict["last_accessed"]),
                size=data_dict["size"],
                compressed=data_dict["compressed"],
                metadata=data_dict["metadata"]
            )
        else:
            data_dict = msgpack.unpackb(data, raw=False)
            return CacheItem(
                key=data_dict["key"],
                value=data_dict["value"],
                created_at=datetime.fromisoformat(data_dict["created_at"]),
                expires_at=datetime.fromisoformat(data_dict["expires_at"]) if data_dict["expires_at"] else None,
                access_count=data_dict.get("access_count", 0),
                last_accessed=datetime.fromisoformat(data_dict["last_accessed"]),
                size=data_dict.get("size", 0),
                compressed=data_dict.get("compressed", False),
                metadata=data_dict.get("metadata", {})
            )
    
    def _compress(self, data: bytes) -> bytes:
        """Comprimir datos."""
        if self.config.compression == CompressionType.GZIP:
            return gzip.compress(data)
        elif self.config.compression == CompressionType.ZLIB:
            return zlib.compress(data)
        else:
            return data
    
    def _decompress(self, data: bytes) -> bytes:
        """Descomprimir datos."""
        if self.config.compression == CompressionType.GZIP:
            return gzip.decompress(data)
        elif self.config.compression == CompressionType.ZLIB:
            return zlib.decompress(data)
        else:
            return data
    
    def _calculate_size(self, value: Any) -> int:
        """Calcular tamaño aproximado del valor."""
        try:
            if self.config.serialization_format == "json":
                return len(json.dumps(value, default=str).encode('utf-8'))
            else:
                # Use a safe pack with binary types enabled
                return len(msgpack.packb(value, use_bin_type=True))
        except Exception:
            return 0

    def _match_pattern(self, key: str, pattern: str) -> bool:
        """Verificar si la clave coincide con el patrón."""
        if pattern == "*":
            return True
        
        import fnmatch
        return fnmatch.fnmatch(key, pattern)


class UnifiedCache:
    """Sistema de caché unificado."""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.backend = self._create_backend()
        self.stats = CacheStats()
        self._lock = threading.RLock()
        self._monitoring_task = None
        self._invalidation_task = None
        
        # Iniciar tareas de monitoreo si están habilitadas
        if self.config.enable_monitoring:
            self._start_monitoring()
        
        if self.config.enable_auto_invalidation:
            self._start_invalidation()
    
    def _create_backend(self) -> CacheBackendInterface:
        """Crear backend según la configuración."""
        if self.config.backend == CacheBackend.MEMORY:
            return MemoryCacheBackend(self.config)
        elif self.config.backend == CacheBackend.FILE:
            return FileCacheBackend(self.config)
        elif self.config.backend == CacheBackend.REDIS:
            # TODO: Implementar Redis backend
            raise NotImplementedError("Redis backend not implemented yet")
        else:
            raise ValueError(f"Unsupported backend: {self.config.backend}")
    
    def _start_monitoring(self):
        """Iniciar tarea de monitoreo."""
        async def monitoring_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.monitoring_interval)
                    await self._update_stats()
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")

        # Evitar crear tasks en tiempo de importación si no existe un loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.debug("No running event loop; skipping monitoring task startup")
            return
        self._monitoring_task = loop.create_task(monitoring_loop())
    
    def _start_invalidation(self):
        """Iniciar tarea de invalidación automática."""
        async def invalidation_loop():
            while True:
                try:
                    await asyncio.sleep(self.config.invalidation_check_interval)
                    await self._cleanup_expired()
                except Exception as e:
                    logger.error(f"Error in invalidation loop: {e}")

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            logger.debug("No running event loop; skipping invalidation task startup")
            return
        self._invalidation_task = loop.create_task(invalidation_loop())
    
    async def _update_stats(self):
        """Actualizar estadísticas del caché."""
        try:
            backend_stats = await self.backend.stats()
            
            with self._lock:
                self.stats.total_size = backend_stats.get("total_size", 0)
                self.stats.item_count = backend_stats.get("item_count", 0)
                self.stats.last_updated = datetime.now()
                
                # Log de estadísticas
                logger.info(f"Cache stats - Items: {self.stats.item_count}, "
                           f"Size: {self.stats.total_size / 1024 / 1024:.2f}MB, "
                           f"Hit rate: {self.stats.hit_rate:.2%}")
        except Exception as e:
            logger.error(f"Error updating cache stats: {e}")
    
    async def _cleanup_expired(self):
        """Limpiar elementos expirados."""
        try:
            keys = await self.backend.keys()
            expired_count = 0
            
            for key in keys:
                if not await self.backend.exists(key):
                    expired_count += 1
            
            if expired_count > 0:
                logger.info(f"Cleaned up {expired_count} expired cache items")
        except Exception as e:
            logger.error(f"Error cleaning up expired items: {e}")
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del caché."""
        try:
            item = await self.backend.get(key)
            if item:
                with self._lock:
                    self.stats.hits += 1
                return item.value
            else:
                with self._lock:
                    self.stats.misses += 1
                return None
        except Exception as e:
            logger.error(f"Error getting cache item {key}: {e}")
            with self._lock:
                self.stats.misses += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Establecer valor en el caché."""
        try:
            success = await self.backend.set(key, value, ttl)
            if success:
                with self._lock:
                    self.stats.sets += 1
            return success
        except Exception as e:
            logger.error(f"Error setting cache item {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del caché."""
        try:
            success = await self.backend.delete(key)
            if success:
                with self._lock:
                    self.stats.deletes += 1
            return success
        except Exception as e:
            logger.error(f"Error deleting cache item {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Verificar si existe un valor en el caché."""
        try:
            return await self.backend.exists(key)
        except Exception as e:
            logger.error(f"Error checking cache item {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Limpiar todo el caché."""
        try:
            success = await self.backend.clear()
            if success:
                with self._lock:
                    self.stats = CacheStats()
            return success
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    async def keys(self, pattern: str = "*") -> List[str]:
        """Obtener claves que coincidan con el patrón."""
        try:
            return await self.backend.keys(pattern)
        except Exception as e:
            logger.error(f"Error listing cache keys: {e}")
            return []
    
    async def size(self) -> int:
        """Obtener número de elementos en el caché."""
        try:
            return await self.backend.size()
        except Exception as e:
            logger.error(f"Error getting cache size: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas completas del caché."""
        try:
            backend_stats = await self.backend.stats()
            
            with self._lock:
                return {
                    "unified_cache": {
                        "hits": self.stats.hits,
                        "misses": self.stats.misses,
                        "hit_rate": self.stats.hit_rate,
                        "miss_rate": self.stats.miss_rate,
                        "sets": self.stats.sets,
                        "deletes": self.stats.deletes,
                        "evictions": self.stats.evictions,
                        "total_size": self.stats.total_size,
                        "item_count": self.stats.item_count,
                        "last_updated": self.stats.last_updated.isoformat()
                    },
                    "backend": backend_stats
                }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    async def warm_cache(self, items: Dict[str, Any], ttl: Optional[int] = None):
        """Precalentar el caché con elementos específicos."""
        try:
            for key, value in items.items():
                await self.set(key, value, ttl)
            logger.info(f"Cache warmed with {len(items)} items")
        except Exception as e:
            logger.error(f"Error warming cache: {e}")
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidar elementos que coincidan con el patrón."""
        try:
            keys = await self.keys(pattern)
            invalidated = 0
            
            for key in keys:
                if await self.delete(key):
                    invalidated += 1
            
            logger.info(f"Invalidated {invalidated} items matching pattern: {pattern}")
            return invalidated
        except Exception as e:
            logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
    
    def close(self):
        """Cerrar el caché y limpiar recursos."""
        try:
            if self._monitoring_task:
                self._monitoring_task.cancel()
            if self._invalidation_task:
                self._invalidation_task.cancel()
            logger.info("Unified cache closed")
        except Exception as e:
            logger.error(f"Error closing cache: {e}")


# Instancia global del caché unificado
unified_cache = UnifiedCache()

# Funciones de conveniencia
async def cache_get(key: str) -> Optional[Any]:
    """Obtener valor del caché global."""
    return await unified_cache.get(key)

async def cache_set(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """Establecer valor en el caché global."""
    return await unified_cache.set(key, value, ttl)

async def cache_delete(key: str) -> bool:
    """Eliminar valor del caché global."""
    return await unified_cache.delete(key)

async def cache_exists(key: str) -> bool:
    """Verificar si existe un valor en el caché global."""
    return await unified_cache.exists(key)

async def cache_clear() -> bool:
    """Limpiar todo el caché global."""
    return await unified_cache.clear()

async def cache_stats() -> Dict[str, Any]:
    """Obtener estadísticas del caché global."""
    return await unified_cache.get_stats()
