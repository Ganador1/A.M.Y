"""
Tests para Unified Cache - Sistema de caché unificado
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
from pathlib import Path
import json
import pickle

try:
    from app.cache.unified_cache import (
        UnifiedCache, CacheConfig, CacheStats, CacheItem,
        CacheBackend, CompressionType, EvictionPolicy,
        MemoryCacheBackend, FileCacheBackend,
        unified_cache, cache_get, cache_set, cache_delete
    )
except Exception:  # pragma: no cover - compatibility fallback
    from app.cache_unified import (
        UnifiedCache, CacheConfig, CacheStats, CacheItem,
        CacheBackend, CompressionType, EvictionPolicy,
        MemoryCacheBackend, FileCacheBackend,
        unified_cache, cache_get, cache_set, cache_delete
    )


class TestCacheConfig:
    """Tests para CacheConfig"""

    def test_default_config(self):
        """Test: Configuración por defecto"""
        config = CacheConfig()
        
        assert config.backend == CacheBackend.MEMORY
        assert config.max_memory_size == 100 * 1024 * 1024
        assert config.max_memory_items == 10000
        assert config.default_ttl == 3600
        assert config.compression == CompressionType.GZIP
        assert config.eviction_policy == EvictionPolicy.LRU
        assert config.enable_monitoring is True
        assert config.serialization_format == "pickle"

    def test_custom_config(self):
        """Test: Configuración personalizada"""
        config = CacheConfig(
            backend=CacheBackend.FILE,
            max_memory_size=50 * 1024 * 1024,
            default_ttl=1800,
            compression=CompressionType.NONE,
            eviction_policy=EvictionPolicy.LFU
        )
        
        assert config.backend == CacheBackend.FILE
        assert config.max_memory_size == 50 * 1024 * 1024
        assert config.default_ttl == 1800
        assert config.compression == CompressionType.NONE
        assert config.eviction_policy == EvictionPolicy.LFU


class TestCacheStats:
    """Tests para CacheStats"""

    def test_initialization(self):
        """Test: Inicialización de CacheStats"""
        stats = CacheStats()
        
        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.sets == 0
        assert stats.deletes == 0
        assert stats.evictions == 0
        assert stats.compression_savings == 0.0
        assert stats.total_size == 0
        assert stats.item_count == 0

    def test_hit_rate_calculation(self):
        """Test: Cálculo de tasa de aciertos"""
        stats = CacheStats(hits=80, misses=20)
        
        assert stats.hit_rate == 0.8
        assert stats.miss_rate == 0.2

    def test_hit_rate_zero_total(self):
        """Test: Tasa de aciertos con total cero"""
        stats = CacheStats()
        
        assert stats.hit_rate == 0.0
        assert stats.miss_rate == 1.0


class TestCacheItem:
    """Tests para CacheItem"""

    def test_initialization(self):
        """Test: Inicialización de CacheItem"""
        now = datetime.now()
        item = CacheItem(
            key="test_key",
            value="test_value",
            created_at=now,
            expires_at=now + timedelta(seconds=3600)
        )
        
        assert item.key == "test_key"
        assert item.value == "test_value"
        assert item.created_at == now
        assert item.expires_at == now + timedelta(seconds=3600)
        assert item.access_count == 0
        assert item.size == 0
        assert item.compressed is False
        assert item.metadata == {}

    def test_is_expired(self):
        """Test: Verificación de expiración"""
        now = datetime.now()
        
        # Item no expirado
        item1 = CacheItem(
            key="test1",
            value="value1",
            created_at=now,
            expires_at=now + timedelta(seconds=3600)
        )
        assert not item1.is_expired
        
        # Item expirado
        item2 = CacheItem(
            key="test2",
            value="value2",
            created_at=now,
            expires_at=now - timedelta(seconds=3600)
        )
        assert item2.is_expired
        
        # Item sin expiración
        item3 = CacheItem(
            key="test3",
            value="value3",
            created_at=now,
            expires_at=None
        )
        assert not item3.is_expired

    def test_ttl_seconds(self):
        """Test: Cálculo de TTL en segundos"""
        now = datetime.now()
        
        # Item con TTL
        item1 = CacheItem(
            key="test1",
            value="value1",
            created_at=now,
            expires_at=now + timedelta(seconds=3600)
        )
        assert item1.ttl_seconds == 3600
        
        # Item sin TTL
        item2 = CacheItem(
            key="test2",
            value="value2",
            created_at=now,
            expires_at=None
        )
        assert item2.ttl_seconds is None
        
        # Item expirado
        item3 = CacheItem(
            key="test3",
            value="value3",
            created_at=now,
            expires_at=now - timedelta(seconds=3600)
        )
        assert item3.ttl_seconds == 0


class TestMemoryCacheBackend:
    """Tests para MemoryCacheBackend"""

    def setup_method(self):
        """Setup para cada test"""
        self.config = CacheConfig(
            backend=CacheBackend.MEMORY,
            max_memory_items=100,
            default_ttl=3600
        )
        self.backend = MemoryCacheBackend(self.config)

    @pytest.mark.asyncio
    async def test_get_missing_key(self):
        """Test: Obtener clave inexistente"""
        result = await self.backend.get("nonexistent_key")
        assert result is None
        assert self.backend._stats.misses == 1

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test: Establecer y obtener valor"""
        # Establecer valor
        success = await self.backend.set("test_key", "test_value", ttl=3600)
        assert success is True
        assert self.backend._stats.sets == 1
        
        # Obtener valor
        item = await self.backend.get("test_key")
        assert item is not None
        assert item.key == "test_key"
        assert item.value == "test_value"
        assert item.access_count == 1
        assert self.backend._stats.hits == 1

    @pytest.mark.asyncio
    async def test_set_and_get_expired(self):
        """Test: Obtener valor expirado"""
        # Establecer valor con TTL muy corto
        await self.backend.set("test_key", "test_value", ttl=0)
        
        # Esperar un poco y obtener
        await asyncio.sleep(0.01)
        result = await self.backend.get("test_key")
        assert result is None
        assert self.backend._stats.misses == 1

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test: Eliminar valor"""
        # Establecer valor
        await self.backend.set("test_key", "test_value")
        
        # Eliminar valor
        success = await self.backend.delete("test_key")
        assert success is True
        assert self.backend._stats.deletes == 1
        
        # Verificar que no existe
        result = await self.backend.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self):
        """Test: Eliminar valor inexistente"""
        success = await self.backend.delete("nonexistent_key")
        assert success is False
        assert self.backend._stats.deletes == 0

    @pytest.mark.asyncio
    async def test_exists(self):
        """Test: Verificar existencia de valor"""
        # Valor inexistente
        exists = await self.backend.exists("nonexistent_key")
        assert exists is False
        
        # Establecer valor
        await self.backend.set("test_key", "test_value")
        
        # Verificar existencia
        exists = await self.backend.exists("test_key")
        assert exists is True

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test: Limpiar caché"""
        # Establecer algunos valores
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        
        # Limpiar
        success = await self.backend.clear()
        assert success is True
        
        # Verificar que está vacío
        assert await self.backend.size() == 0

    @pytest.mark.asyncio
    async def test_keys(self):
        """Test: Obtener claves"""
        # Establecer algunos valores
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        await self.backend.set("other_key", "value3")
        
        # Obtener todas las claves
        keys = await self.backend.keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "other_key" in keys
        
        # Obtener claves con patrón
        keys = await self.backend.keys("key*")
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

    @pytest.mark.asyncio
    async def test_size(self):
        """Test: Obtener tamaño del caché"""
        # Caché vacío
        assert await self.backend.size() == 0
        
        # Agregar elementos
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        
        # Verificar tamaño
        assert await self.backend.size() == 2

    @pytest.mark.asyncio
    async def test_stats(self):
        """Test: Obtener estadísticas"""
        # Realizar algunas operaciones
        await self.backend.set("key1", "value1")
        await self.backend.get("key1")
        await self.backend.get("nonexistent")
        await self.backend.delete("key1")
        
        # Obtener estadísticas
        stats = await self.backend.stats()
        
        assert stats["backend"] == "memory"
        assert stats["item_count"] == 0
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_eviction_lru(self):
        """Test: Evicción LRU"""
        # Configurar límite pequeño
        self.config.max_memory_items = 2
        self.config.eviction_policy = EvictionPolicy.LRU
        
        # Agregar más elementos que el límite
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        await self.backend.set("key3", "value3")  # Debe evictar key1
        
        # Verificar que key1 fue evictado
        assert await self.backend.size() == 2
        assert not await self.backend.exists("key1")
        assert await self.backend.exists("key2")
        assert await self.backend.exists("key3")

    @pytest.mark.asyncio
    async def test_eviction_lfu(self):
        """Test: Evicción LFU"""
        # Configurar límite pequeño
        self.config.max_memory_items = 2
        self.config.eviction_policy = EvictionPolicy.LFU
        
        # Agregar elementos
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        
        # Acceder a key1 más veces
        await self.backend.get("key1")
        await self.backend.get("key1")
        await self.backend.get("key2")  # Solo una vez
        
        # Agregar tercer elemento (debe evictar key2)
        await self.backend.set("key3", "value3")
        
        # Verificar que key2 fue evictado
        assert await self.backend.size() == 2
        assert await self.backend.exists("key1")
        assert not await self.backend.exists("key2")
        assert await self.backend.exists("key3")


class TestFileCacheBackend:
    """Tests para FileCacheBackend"""

    def setup_method(self):
        """Setup para cada test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = CacheConfig(
            backend=CacheBackend.FILE,
            file_cache_dir=self.temp_dir,
            default_ttl=3600
        )
        self.backend = FileCacheBackend(self.config)

    def teardown_method(self):
        """Cleanup después de cada test"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @pytest.mark.asyncio
    async def test_get_missing_key(self):
        """Test: Obtener clave inexistente"""
        result = await self.backend.get("nonexistent_key")
        assert result is None
        assert self.backend._stats.misses == 1

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test: Establecer y obtener valor"""
        # Establecer valor
        success = await self.backend.set("test_key", "test_value", ttl=3600)
        assert success is True
        assert self.backend._stats.sets == 1
        
        # Obtener valor
        item = await self.backend.get("test_key")
        assert item is not None
        assert item.key == "test_key"
        assert item.value == "test_value"
        assert item.access_count == 1
        assert self.backend._stats.hits == 1

    @pytest.mark.asyncio
    async def test_set_and_get_expired(self):
        """Test: Obtener valor expirado"""
        # Establecer valor con TTL muy corto
        await self.backend.set("test_key", "test_value", ttl=0)
        
        # Esperar un poco y obtener
        await asyncio.sleep(0.01)
        result = await self.backend.get("test_key")
        assert result is None
        assert self.backend._stats.misses == 1

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test: Eliminar valor"""
        # Establecer valor
        await self.backend.set("test_key", "test_value")
        
        # Eliminar valor
        success = await self.backend.delete("test_key")
        assert success is True
        assert self.backend._stats.deletes == 1
        
        # Verificar que no existe
        result = await self.backend.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_exists(self):
        """Test: Verificar existencia de valor"""
        # Valor inexistente
        exists = await self.backend.exists("nonexistent_key")
        assert exists is False
        
        # Establecer valor
        await self.backend.set("test_key", "test_value")
        
        # Verificar existencia
        exists = await self.backend.exists("test_key")
        assert exists is True

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test: Limpiar caché"""
        # Establecer algunos valores
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        
        # Limpiar
        success = await self.backend.clear()
        assert success is True
        
        # Verificar que está vacío
        assert await self.backend.size() == 0

    @pytest.mark.asyncio
    async def test_keys(self):
        """Test: Obtener claves"""
        # Establecer algunos valores
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        await self.backend.set("other_key", "value3")
        
        # Obtener todas las claves
        keys = await self.backend.keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "other_key" in keys

    @pytest.mark.asyncio
    async def test_size(self):
        """Test: Obtener tamaño del caché"""
        # Caché vacío
        assert await self.backend.size() == 0
        
        # Agregar elementos
        await self.backend.set("key1", "value1")
        await self.backend.set("key2", "value2")
        
        # Verificar tamaño
        assert await self.backend.size() == 2

    @pytest.mark.asyncio
    async def test_stats(self):
        """Test: Obtener estadísticas"""
        # Realizar algunas operaciones
        await self.backend.set("key1", "value1")
        await self.backend.get("key1")
        await self.backend.get("nonexistent")
        await self.backend.delete("key1")
        
        # Obtener estadísticas
        stats = await self.backend.stats()
        
        assert stats["backend"] == "file"
        assert stats["item_count"] == 0
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_compression(self):
        """Test: Compresión de datos"""
        # Configurar compresión
        self.config.compression = CompressionType.GZIP
        
        # Establecer valor grande
        large_value = "x" * 1000
        await self.backend.set("large_key", large_value)
        
        # Obtener valor
        item = await self.backend.get("large_key")
        assert item is not None
        assert item.value == large_value

    @pytest.mark.asyncio
    async def test_serialization_formats(self):
        """Test: Diferentes formatos de serialización"""
        # Test con JSON
        self.config.serialization_format = "json"
        await self.backend.set("json_key", {"test": "value"})
        item = await self.backend.get("json_key")
        assert item is not None
        assert item.value == {"test": "value"}
        
        # Test con Pickle
        self.config.serialization_format = "pickle"
        await self.backend.set("pickle_key", {"test": "value"})
        item = await self.backend.get("pickle_key")
        assert item is not None
        assert item.value == {"test": "value"}


class TestUnifiedCache:
    """Tests para UnifiedCache"""

    def setup_method(self):
        """Setup para cada test"""
        self.config = CacheConfig(
            backend=CacheBackend.MEMORY,
            max_memory_items=100,
            default_ttl=3600,
            enable_monitoring=False,
            enable_auto_invalidation=False
        )
        self.cache = UnifiedCache(self.config)

    def teardown_method(self):
        """Cleanup después de cada test"""
        self.cache.close()

    @pytest.mark.asyncio
    async def test_get_missing_key(self):
        """Test: Obtener clave inexistente"""
        result = await self.cache.get("nonexistent_key")
        assert result is None
        assert self.cache.stats.misses == 1

    @pytest.mark.asyncio
    async def test_set_and_get(self):
        """Test: Establecer y obtener valor"""
        # Establecer valor
        success = await self.cache.set("test_key", "test_value", ttl=3600)
        assert success is True
        assert self.cache.stats.sets == 1
        
        # Obtener valor
        value = await self.cache.get("test_key")
        assert value == "test_value"
        assert self.cache.stats.hits == 1

    @pytest.mark.asyncio
    async def test_delete(self):
        """Test: Eliminar valor"""
        # Establecer valor
        await self.cache.set("test_key", "test_value")
        
        # Eliminar valor
        success = await self.cache.delete("test_key")
        assert success is True
        assert self.cache.stats.deletes == 1
        
        # Verificar que no existe
        result = await self.cache.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_exists(self):
        """Test: Verificar existencia de valor"""
        # Valor inexistente
        exists = await self.cache.exists("nonexistent_key")
        assert exists is False
        
        # Establecer valor
        await self.cache.set("test_key", "test_value")
        
        # Verificar existencia
        exists = await self.cache.exists("test_key")
        assert exists is True

    @pytest.mark.asyncio
    async def test_clear(self):
        """Test: Limpiar caché"""
        # Establecer algunos valores
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")
        
        # Limpiar
        success = await self.cache.clear()
        assert success is True
        
        # Verificar que está vacío
        assert await self.cache.size() == 0
        assert self.cache.stats.hits == 0
        assert self.cache.stats.misses == 0

    @pytest.mark.asyncio
    async def test_keys(self):
        """Test: Obtener claves"""
        # Establecer algunos valores
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")
        await self.cache.set("other_key", "value3")
        
        # Obtener todas las claves
        keys = await self.cache.keys()
        assert len(keys) == 3
        assert "key1" in keys
        assert "key2" in keys
        assert "other_key" in keys

    @pytest.mark.asyncio
    async def test_size(self):
        """Test: Obtener tamaño del caché"""
        # Caché vacío
        assert await self.cache.size() == 0
        
        # Agregar elementos
        await self.cache.set("key1", "value1")
        await self.cache.set("key2", "value2")
        
        # Verificar tamaño
        assert await self.cache.size() == 2

    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test: Obtener estadísticas"""
        # Realizar algunas operaciones
        await self.cache.set("key1", "value1")
        await self.cache.get("key1")
        await self.cache.get("nonexistent")
        await self.cache.delete("key1")
        
        # Obtener estadísticas
        stats = await self.cache.get_stats()
        
        assert "unified_cache" in stats
        assert "backend" in stats
        assert stats["unified_cache"]["hits"] == 1
        assert stats["unified_cache"]["misses"] == 1
        assert stats["unified_cache"]["hit_rate"] == 0.5

    @pytest.mark.asyncio
    async def test_warm_cache(self):
        """Test: Precalentar caché"""
        items = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }
        
        await self.cache.warm_cache(items, ttl=3600)
        
        # Verificar que se establecieron
        assert await self.cache.size() == 3
        assert await self.cache.get("key1") == "value1"
        assert await self.cache.get("key2") == "value2"
        assert await self.cache.get("key3") == "value3"

    @pytest.mark.asyncio
    async def test_invalidate_pattern(self):
        """Test: Invalidar por patrón"""
        # Establecer algunos valores
        await self.cache.set("user:1", "data1")
        await self.cache.set("user:2", "data2")
        await self.cache.set("session:1", "data3")
        
        # Invalidar solo usuarios
        invalidated = await self.cache.invalidate_pattern("user:*")
        assert invalidated == 2
        
        # Verificar que solo quedan sesiones
        assert await self.cache.size() == 1
        assert await self.cache.exists("session:1")
        assert not await self.cache.exists("user:1")
        assert not await self.cache.exists("user:2")

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test: Manejo de errores"""
        # Simular error en el backend
        with patch.object(self.cache.backend, 'get', side_effect=Exception("Backend error")):
            result = await self.cache.get("test_key")
            assert result is None
            assert self.cache.stats.misses == 1

    @pytest.mark.asyncio
    async def test_backend_creation(self):
        """Test: Creación de backend"""
        # Test con backend de memoria
        memory_config = CacheConfig(backend=CacheBackend.MEMORY)
        memory_cache = UnifiedCache(memory_config)
        assert isinstance(memory_cache.backend, MemoryCacheBackend)
        memory_cache.close()
        
        # Test con backend de archivos
        file_config = CacheConfig(backend=CacheBackend.FILE)
        file_cache = UnifiedCache(file_config)
        assert isinstance(file_cache.backend, FileCacheBackend)
        file_cache.close()

    @pytest.mark.asyncio
    async def test_unsupported_backend(self):
        """Test: Backend no soportado"""
        config = CacheConfig(backend=CacheBackend.REDIS)
        
        with pytest.raises(NotImplementedError):
            UnifiedCache(config)


class TestGlobalCacheFunctions:
    """Tests para funciones globales de caché"""

    @pytest.mark.asyncio
    async def test_cache_get(self):
        """Test: Función global cache_get"""
        # Establecer valor
        await unified_cache.set("global_key", "global_value")
        
        # Obtener valor
        value = await cache_get("global_key")
        assert value == "global_value"

    @pytest.mark.asyncio
    async def test_cache_set(self):
        """Test: Función global cache_set"""
        # Establecer valor
        success = await cache_set("global_key", "global_value", ttl=3600)
        assert success is True
        
        # Verificar que se estableció
        value = await unified_cache.get("global_key")
        assert value == "global_value"

    @pytest.mark.asyncio
    async def test_cache_delete(self):
        """Test: Función global cache_delete"""
        # Establecer valor
        await unified_cache.set("global_key", "global_value")
        
        # Eliminar valor
        success = await cache_delete("global_key")
        assert success is True
        
        # Verificar que se eliminó
        value = await unified_cache.get("global_key")
        assert value is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
