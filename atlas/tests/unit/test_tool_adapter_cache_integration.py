"""Tests para integración de cache en ToolAdapter"""
import pytest
from app.tool_adapter import ToolAdapter, get_tool_registry
from app.adapters.tool_adapter_cache import tool_adapter_cache


class TestAdapter(ToolAdapter):
    name = "test"
    version = "1.0.0"
    description = "Test adapter for cache testing"
    allow_cache = True
    
    def __init__(self, should_fail=False):
        super().__init__()
        self.should_fail = should_fail
        self.call_count = 0
    
    def _run(self, params):
        self.call_count += 1
        if self.should_fail:
            raise ValueError("Test error")
        return {"result": f"processed_{self.call_count}", "input": params}


def test_cache_hit_reduces_calls():
    """Test que el cache evita múltiples ejecuciones"""
    tool_adapter_cache.clear()
    
    adapter = TestAdapter()
    params = {"test": "value"}
    
    # Primera ejecución
    result1 = adapter.execute(params)
    assert result1.success
    assert adapter.call_count == 1
    
    # Segunda ejecución - debería usar cache
    result2 = adapter.execute(params)
    assert result2.success
    assert adapter.call_count == 1  # No se incrementa por el cache
    assert result1.output == result2.output


def test_cache_miss_on_different_params():
    """Test que parámetros diferentes causan cache miss"""
    tool_adapter_cache.clear()
    
    adapter = TestAdapter()
    
    result1 = adapter.execute({"test": "value1"})
    result2 = adapter.execute({"test": "value2"})
    
    assert result1.success and result2.success
    assert adapter.call_count == 2  # Dos ejecuciones diferentes
    assert result1.output != result2.output


def test_cache_disabled_adapter():
    """Test que adapter sin cache siempre ejecuta"""
    tool_adapter_cache.clear()
    
    class NoCacheAdapter(TestAdapter):
        allow_cache = False
    
    adapter = NoCacheAdapter()
    params = {"test": "value"}
    
    result1 = adapter.execute(params)
    result2 = adapter.execute(params)
    
    assert adapter.call_count == 2  # Ambas ejecutadas
    assert result1.input_hash is None  # Sin hash
    assert result2.input_hash is None


def test_failed_execution_not_cached():
    """Test que ejecuciones fallidas no se cachean"""
    tool_adapter_cache.clear()
    
    adapter = TestAdapter(should_fail=True)
    params = {"test": "value"}
    
    result1 = adapter.execute(params)
    result2 = adapter.execute(params)
    
    assert not result1.success
    assert not result2.success
    assert adapter.call_count == 2  # Ambas ejecutadas por fallos


def test_cache_stats():
    """Test estadísticas de cache"""
    tool_adapter_cache.clear()
    
    adapter = TestAdapter()
    
    # Cache vacío
    stats = adapter.cache_stats()
    assert stats["cache_enabled"]
    assert stats["size"] == 0
    assert stats["hits"] == 0
    assert stats["misses"] == 0
    
    # Ejecutar para generar stats
    adapter.execute({"test": "1"})  # miss
    adapter.execute({"test": "1"})  # hit
    adapter.execute({"test": "2"})  # miss
    
    stats = adapter.cache_stats()
    assert stats["size"] == 2  # Dos entradas únicas
    assert stats["hits"] == 1
    assert stats["misses"] == 2
    assert stats["hit_rate"] == 1/3


def test_registry_integration():
    """Test integración con registry"""
    registry = get_tool_registry()
    adapter = TestAdapter()
    registry.register(adapter)
    
    retrieved = registry.get("test")
    assert retrieved is not None
    assert retrieved.name == "test"
    
    # Verificar que cache funciona a través del registry
    result = retrieved.execute({"registry": "test"})
    assert result.success


if __name__ == "__main__":
    pytest.main([__file__])
