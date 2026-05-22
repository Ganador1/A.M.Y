"""
Tests unitarios para Tool Adapters mejorados

Pruebas para:
- Circuit breaker pattern
- Retry logic con backoff exponencial
- Rate limiting
- Async/sync execution
- Configuration validation
- Error handling mejorado
- Caching integration
"""

import pytest
import time
import asyncio
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from app.adapters.tool_adapter import (
    ToolAdapter,
    ToolExecutionConfig,
    CircuitBreaker,
    RateLimiter,
    ToolExecutionResult,
    AdapterStatus,
    EchoAdapter
)


class TestToolExecutionConfig:
    """Tests para configuración de ejecución"""

    def test_config_validation_valid(self):
        """Test validación de configuración válida"""
        config = ToolExecutionConfig(
            max_retries=3,
            retry_delay=1.0,
            retry_backoff=2.0,
            timeout=30.0,
            rate_limit=10.0,
            circuit_breaker_threshold=5,
            circuit_breaker_timeout=60.0
        )

        # Should not raise exception
        config.validate()

    def test_config_validation_invalid_max_retries(self):
        """Test validación con max_retries inválido"""
        config = ToolExecutionConfig(max_retries=-1)

        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            config.validate()

    def test_config_validation_invalid_retry_delay(self):
        """Test validación con retry_delay inválido"""
        config = ToolExecutionConfig(retry_delay=-1.0)

        with pytest.raises(ValueError, match="retry_delay must be positive"):
            config.validate()

    def test_config_validation_invalid_retry_backoff(self):
        """Test validación con retry_backoff inválido"""
        config = ToolExecutionConfig(retry_backoff=0.5)

        with pytest.raises(ValueError, match="retry_backoff must be >= 1.0"):
            config.validate()

    def test_config_validation_invalid_timeout(self):
        """Test validación con timeout inválido"""
        config = ToolExecutionConfig(timeout=-1.0)

        with pytest.raises(ValueError, match="timeout must be positive"):
            config.validate()


class TestCircuitBreaker:
    """Tests para circuit breaker"""

    def test_circuit_breaker_initialization(self):
        """Test inicialización del circuit breaker"""
        cb = CircuitBreaker(failure_threshold=3, timeout=30.0)

        assert cb.failure_threshold == 3
        assert cb.timeout == 30.0
        assert cb._failures == 0
        assert cb._state == "closed"

    def test_circuit_breaker_can_execute_closed(self):
        """Test que permite ejecución cuando está cerrado"""
        cb = CircuitBreaker()

        assert cb.can_execute() is True

    def test_circuit_breaker_can_execute_open(self):
        """Test que no permite ejecución cuando está abierto"""
        cb = CircuitBreaker(failure_threshold=2, timeout=60.0)
        cb._state = "open"
        cb._last_failure_time = time.time()

        assert cb.can_execute() is False

    def test_circuit_breaker_can_execute_half_open(self):
        """Test que permite ejecución cuando está semi-abierto"""
        cb = CircuitBreaker(timeout=0.1)  # Very short timeout
        cb._state = "open"
        cb._last_failure_time = time.time() - 1.0  # Timeout expired

        assert cb.can_execute() is True
        assert cb._state == "half_open"

    def test_circuit_breaker_record_success(self):
        """Test registro de éxito"""
        cb = CircuitBreaker()
        cb._state = "half_open"
        cb._failures = 2

        cb.record_success()

        assert cb._state == "closed"
        assert cb._failures == 0

    def test_circuit_breaker_record_failure_below_threshold(self):
        """Test registro de fallo por debajo del umbral"""
        cb = CircuitBreaker(failure_threshold=3)

        cb.record_failure()

        assert cb._state == "closed"
        assert cb._failures == 1

    def test_circuit_breaker_record_failure_at_threshold(self):
        """Test registro de fallo en el umbral"""
        cb = CircuitBreaker(failure_threshold=2)
        cb._failures = 1

        cb.record_failure()

        assert cb._state == "open"
        assert cb._failures == 2


class TestRateLimiter:
    """Tests para rate limiter"""

    def test_rate_limiter_initialization(self):
        """Test inicialización del rate limiter"""
        rl = RateLimiter(requests_per_second=10.0)

        assert rl.requests_per_second == 10.0
        assert rl._request_count == 0
        assert rl._window_start == 0.0

    def test_rate_limiter_can_make_request_empty(self):
        """Test que permite requests cuando está vacío"""
        rl = RateLimiter(requests_per_second=10.0)

        assert rl.can_make_request() is True

    def test_rate_limiter_can_make_request_within_limit(self):
        """Test que permite requests dentro del límite"""
        rl = RateLimiter(requests_per_second=2.0)
        rl._request_count = 1
        rl._window_start = time.time()

        assert rl.can_make_request() is True

    def test_rate_limiter_can_make_request_at_limit(self):
        """Test que no permite requests en el límite"""
        rl = RateLimiter(requests_per_second=2.0)
        rl._request_count = 2
        rl._window_start = time.time()

        assert rl.can_make_request() is False

    def test_rate_limiter_window_reset(self):
        """Test reset de ventana de tiempo"""
        rl = RateLimiter(requests_per_second=5.0)
        rl._request_count = 5
        rl._window_start = time.time() - 2.0  # 2 seconds ago

        assert rl.can_make_request() is True  # Should reset window
        assert rl._request_count == 0

    def test_rate_limiter_record_request(self):
        """Test registro de request"""
        rl = RateLimiter(requests_per_second=10.0)

        rl.record_request()

        assert rl._request_count == 1
        assert rl._last_request_time > 0


class TestToolAdapterInitialization:
    """Tests para inicialización de ToolAdapter"""

    def test_adapter_initialization_default_config(self):
        """Test inicialización con configuración por defecto"""
        adapter = ToolAdapter()

        assert adapter.name == "base"
        assert adapter.version == "0.1.0"
        assert adapter.description == "Generic tool adapter"
        assert adapter.allow_cache is True
        assert adapter.supports_async is False
        assert adapter.status == AdapterStatus.HEALTHY
        assert isinstance(adapter.config, ToolExecutionConfig)
        assert isinstance(adapter.circuit_breaker, CircuitBreaker)
        assert adapter.rate_limiter is None

    def test_adapter_initialization_custom_config(self):
        """Test inicialización con configuración personalizada"""
        config = ToolExecutionConfig(
            max_retries=5,
            rate_limit=20.0,
            timeout=10.0
        )
        adapter = ToolAdapter(config=config)

        assert adapter.config.max_retries == 5
        assert adapter.config.rate_limit == 20.0
        assert adapter.config.timeout == 10.0
        assert adapter.rate_limiter is not None

    def test_adapter_initialization_with_rate_limit(self):
        """Test inicialización con rate limiting"""
        config = ToolExecutionConfig(rate_limit=15.0)
        adapter = ToolAdapter(config=config)

        assert adapter.rate_limiter is not None
        assert adapter.rate_limiter.requests_per_second == 15.0


class TestToolAdapterExecution:
    """Tests para ejecución de ToolAdapter"""

    def test_execute_sync_success(self):
        """Test ejecución exitosa síncrona"""
        adapter = ToolAdapter()

        # Mock the internal methods
        adapter._execute_once = Mock(return_value=ToolExecutionResult(
            success=True,
            output={"test": "result"}
        ))

        result = adapter.execute({"param": "value"})

        assert result.success is True
        assert result.output == {"test": "result"}
        assert adapter.status == AdapterStatus.HEALTHY

    def test_execute_sync_failure_circuit_breaker(self):
        """Test ejecución con circuit breaker abierto"""
        adapter = ToolAdapter()
        adapter.circuit_breaker._state = "open"

        result = adapter.execute({"param": "value"})

        assert result.success is False
        assert "Circuit breaker is open" in result.error
        assert adapter.status == AdapterStatus.UNHEALTHY

    def test_execute_sync_failure_rate_limit(self):
        """Test ejecución con rate limit excedido"""
        config = ToolExecutionConfig(rate_limit=1.0)
        adapter = ToolAdapter(config=config)

        # Exceed rate limit
        adapter.rate_limiter._request_count = 1
        adapter.rate_limiter._window_start = time.time()

        result = adapter.execute({"param": "value"})

        assert result.success is False
        assert "Rate limit exceeded" in result.error

    def test_execute_retry_logic(self):
        """Test lógica de reintento"""
        adapter = ToolAdapter()

        # Mock _execute_once to fail twice then succeed
        call_count = 0
        def mock_execute_once(params):
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return ToolExecutionResult(success=True, output="success")

        adapter._execute_once = mock_execute_once

        result = adapter.execute({"param": "value"})

        assert result.success is True
        assert call_count == 3
        assert adapter.status == AdapterStatus.HEALTHY

    def test_execute_no_retry_on_validation_error(self):
        """Test que no reintenta en errores de validación"""
        adapter = ToolAdapter()

        # Mock _execute_once to raise validation error
        def mock_execute_once(params):
            raise ValueError("Validation error")

        adapter._execute_once = mock_execute_once

        result = adapter.execute({"param": "value"})

        assert result.success is False
        assert "Validation error" in result.error
        assert adapter.status == AdapterStatus.HEALTHY  # Should not affect status

    def test_execute_all_retries_failed(self):
        """Test cuando todos los reintentos fallan"""
        adapter = ToolAdapter()

        # Mock _execute_once to always fail
        def mock_execute_once(params):
            raise Exception("Always fails")

        adapter._execute_once = mock_execute_once

        result = adapter.execute({"param": "value"})

        assert result.success is False
        assert "All 4 attempts failed" in result.error
        assert adapter.status == AdapterStatus.UNHEALTHY


class TestToolAdapterAsyncExecution:
    """Tests para ejecución asíncrona"""

    @pytest.mark.asyncio
    async def test_execute_async_sync_adapter(self):
        """Test ejecución asíncrona con adaptador síncrono"""
        adapter = ToolAdapter()

        # Mock _execute_sync to return success
        adapter._execute_sync = Mock(return_value=ToolExecutionResult(
            success=True,
            output="async_result"
        ))

        result = await adapter.execute_async({"param": "value"})

        assert result.success is True
        assert result.output == "async_result"

    @pytest.mark.asyncio
    async def test_execute_async_async_adapter(self):
        """Test ejecución asíncrona con adaptador asíncrono"""
        adapter = ToolAdapter()
        adapter.supports_async = True

        # Mock _execute_sync for async adapter
        adapter._execute_sync = Mock(return_value=ToolExecutionResult(
            success=True,
            output="async_adapter_result"
        ))

        result = await adapter.execute_async({"param": "value"})

        assert result.success is True
        assert result.output == "async_adapter_result"

    def test_execute_async_not_supported(self):
        """Test error cuando adaptador no soporta async"""
        adapter = ToolAdapter()
        adapter.supports_async = False

        with pytest.raises(RuntimeError, match="does not support async execution"):
            asyncio.run(adapter.execute_async({"param": "value"}))


class TestToolAdapterTimeout:
    """Tests para timeout de ejecución"""

    def test_execute_with_timeout_success(self):
        """Test ejecución con timeout exitosa"""
        adapter = ToolAdapter()

        # Mock _execute_once to succeed quickly
        def mock_execute_once(params):
            return ToolExecutionResult(success=True, output="success")

        adapter._execute_once = mock_execute_once

        with patch('signal.signal'), patch('signal.alarm'):
            result = adapter._execute_with_timeout({"param": "value"}, timeout=5.0)

            assert result.success is True

    def test_execute_with_timeout_timeout_error(self):
        """Test ejecución que excede timeout"""
        adapter = ToolAdapter()

        # Mock _execute_once to take too long
        def mock_execute_once(params):
            time.sleep(2.0)  # Longer than timeout
            return ToolExecutionResult(success=True, output="success")

        adapter._execute_once = mock_execute_once

        with patch('signal.signal'), patch('signal.alarm'):
            result = adapter._execute_with_timeout({"param": "value"}, timeout=1.0)

            assert result.success is False
            assert "timed out" in result.error


class TestToolAdapterCaching:
    """Tests para caching de ToolAdapter"""

    def test_hash_input_generation(self):
        """Test generación de hash de input"""
        adapter = ToolAdapter()

        params1 = {"key": "value", "number": 42}
        params2 = {"number": 42, "key": "value"}  # Same content, different order

        hash1 = adapter._hash_input(params1)
        hash2 = adapter._hash_input(params2)

        assert hash1 == hash2  # Should be the same
        assert len(hash1) == 64  # SHA256 hex length

    def test_cache_miss(self):
        """Test cache miss"""
        adapter = ToolAdapter()

        with patch('app.adapters.tool_adapter.tool_adapter_cache') as mock_cache:
            mock_cache.get.return_value = None

            # Mock _execute_once
            def mock_execute_once(params):
                return ToolExecutionResult(success=True, output="cached_result")

            adapter._execute_once = mock_execute_once

            result = adapter._execute_once({"param": "value"})

            assert result.success is True
            mock_cache.get.assert_called_once()

    def test_cache_hit(self):
        """Test cache hit"""
        adapter = ToolAdapter()

        cached_result = ToolExecutionResult(success=True, output="cached_result")

        with patch('app.adapters.tool_adapter.tool_adapter_cache') as mock_cache:
            mock_cache.get.return_value = cached_result

            result = adapter._execute_once({"param": "value"})

            assert result.success is True
            assert result.output == "cached_result"
            assert result == cached_result

    def test_cache_store_on_success(self):
        """Test almacenamiento en cache en éxito"""
        adapter = ToolAdapter()

        with patch('app.adapters.tool_adapter.tool_adapter_cache') as mock_cache:
            mock_cache.get.return_value = None

            # Mock _execute_once to succeed
            def mock_execute_once(params):
                return ToolExecutionResult(success=True, output="new_result")

            adapter._execute_once = mock_execute_once

            result = adapter._execute_once({"param": "value"})

            assert result.success is True
            mock_cache.put.assert_called_once()


class TestToolAdapterStatus:
    """Tests para estado del adaptador"""

    def test_adapter_status_transitions(self):
        """Test transiciones de estado del adaptador"""
        adapter = ToolAdapter()

        # Initially healthy
        assert adapter.get_status() == AdapterStatus.HEALTHY

        # Simulate some failures
        adapter.circuit_breaker._failures = 2
        adapter.status = AdapterStatus.DEGRADED

        assert adapter.get_status() == AdapterStatus.DEGRADED

        # Simulate circuit breaker open
        adapter.circuit_breaker._state = "open"
        adapter.status = AdapterStatus.UNHEALTHY

        assert adapter.get_status() == AdapterStatus.UNHEALTHY

    def test_reset_circuit_breaker(self):
        """Test reset del circuit breaker"""
        adapter = ToolAdapter()
        adapter.circuit_breaker._state = "open"
        adapter.circuit_breaker._failures = 5

        adapter.reset_circuit_breaker()

        assert adapter.circuit_breaker._state == "closed"
        assert adapter.circuit_breaker._failures == 0


class TestEchoAdapter:
    """Tests para el adaptador de ejemplo EchoAdapter"""

    def test_echo_adapter_execution(self):
        """Test ejecución del adaptador Echo"""
        adapter = EchoAdapter()

        result = adapter.execute({"message": "hello", "count": 5})

        assert result.success is True
        assert result.output["echo"] == {"message": "hello", "count": 5}
        assert result.output["length"] == 2

    def test_echo_adapter_async_execution(self):
        """Test ejecución asíncrona del adaptador Echo"""
        adapter = EchoAdapter()

        result = asyncio.run(adapter.execute_async({"message": "async_hello"}))

        assert result.success is True
        assert result.output["echo"] == {"message": "async_hello"}
        assert result.output["length"] == 1


class TestToolAdapterValidation:
    """Tests para validación de ToolAdapter"""

    def test_validate_basic_valid_params(self):
        """Test validación básica de parámetros válidos"""
        adapter = ToolAdapter()

        # Should not raise exception
        adapter._validate({"param": "value", "number": 42})

    def test_validate_invalid_params_type(self):
        """Test validación con tipo de parámetros inválido"""
        adapter = ToolAdapter()

        with pytest.raises(ValueError, match="params must be a dict"):
            adapter._validate("not_a_dict")

    def test_validate_params_too_large(self):
        """Test validación con parámetros demasiado grandes"""
        adapter = ToolAdapter()

        # Create large params
        large_params = {"data": "x" * 60000}  # Over 50KB limit

        with pytest.raises(ValueError, match="params too large for adapter"):
            adapter._validate(large_params)


class TestToolAdapterHooks:
    """Tests para hooks de ToolAdapter"""

    def test_pre_and_post_hooks(self):
        """Test hooks de pre y post ejecución"""
        adapter = ToolAdapter()

        # Track calls
        pre_hook_called = False
        post_hook_called = False

        def mock_pre_hook(params):
            nonlocal pre_hook_called
            pre_hook_called = True

        def mock_post_hook(params, output):
            nonlocal post_hook_called
            post_hook_called = True

        adapter._pre_hook = mock_pre_hook
        adapter._post_hook = mock_post_hook

        # Mock _run and _validate
        adapter._validate = Mock()
        adapter._run = Mock(return_value="test_output")

        result = adapter._execute_once({"param": "value"})

        assert pre_hook_called is True
        assert post_hook_called is True
        assert result.success is True
