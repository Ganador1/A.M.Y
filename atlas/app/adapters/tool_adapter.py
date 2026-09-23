"""Tool Adapter Base - Enhanced Version

Objetivo: proporcionar una interfaz uniforme para integrar herramientas/servicios
heterogéneos (internos o externos) en flujos orquestados (workflows, research cycle,
validaciones cruzadas). Inspirado en patrones de *Driver/Adapter*.

Principios:
- Contrato claro: describe capacidades (sync/async, tipos de I/O, coste, riesgo)
- Observabilidad: métricas simples (tiempo, éxito, errores)
- Seguridad: validación básica de parámetros declarativos
- Extensibilidad: hooks para pre/post ejecución
- Idempotencia lógica: hash de input para caching opcional

Mejoras implementadas:
- Async/await support
- Circuit breaker pattern
- Retry logic with exponential backoff
- Rate limiting
- Enhanced logging
- Configuration validation
- Better error handling
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Callable, List, Union
import time
import hashlib
import json
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
import warnings

# Import metrics if available
try:
    from app.monitoring.metrics import metrics
except ImportError:  # pragma: no cover
    metrics = None  # type: ignore

try:
    from .tool_adapter_cache import tool_adapter_cache
except ImportError:  # pragma: no cover
    tool_adapter_cache = None  # type: ignore

# Set up logger
logger = logging.getLogger(__name__)

class AdapterStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class ToolExecutionConfig:
    """Configuration for tool execution"""
    max_retries: int = 3
    retry_delay: float = 1.0
    retry_backoff: float = 2.0
    timeout: Optional[float] = None
    rate_limit: Optional[float] = None  # requests per second
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0

    def validate(self) -> None:
        """Validate configuration parameters"""
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_delay <= 0:
            raise ValueError("retry_delay must be positive")
        if self.retry_backoff < 1.0:
            raise ValueError("retry_backoff must be >= 1.0")
        if self.timeout is not None and self.timeout <= 0:
            raise ValueError("timeout must be positive")


@dataclass
class CircuitBreaker:
    """Circuit breaker implementation"""
    failure_threshold: int = 5
    timeout: float = 60.0
    _failures: int = 0
    _last_failure_time: float = 0.0
    _state: str = "closed"

    def can_execute(self) -> bool:
        """Check if circuit breaker allows execution"""
        if self._state == "open":
            if time.time() - self._last_failure_time > self.timeout:
                self._state = "half_open"
                return True
            return False
        return True

    def record_success(self) -> None:
        """Record successful execution"""
        if self._state == "half_open":
            self._state = "closed"
        self._failures = 0

    def record_failure(self) -> None:
        """Record failed execution"""
        self._failures += 1
        self._last_failure_time = time.time()

        if self._failures >= self.failure_threshold:
            self._state = "open"


@dataclass
class RateLimiter:
    """Rate limiter implementation"""
    requests_per_second: float
    _last_request_time: float = 0.0
    _request_count: int = 0
    _window_start: float = 0.0

    def can_make_request(self) -> bool:
        """Check if request can be made without exceeding rate limit"""
        current_time = time.time()

        # Reset window if needed
        if current_time - self._window_start >= 1.0:
            self._request_count = 0
            self._window_start = current_time

        if self._request_count >= self.requests_per_second:
            return False

        return True

    def record_request(self) -> None:
        """Record that a request was made"""
        self._request_count += 1
        self._last_request_time = time.time()

@dataclass
class ToolExecutionResult:
    """Result of tool execution"""
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    input_hash: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
class ToolAdapter:
    """Base class for tool adapters with enhanced features"""

    # Class attributes (to be overridden by subclasses)
    name: str = "base_adapter"
    version: str = "0.1.0"
    description: str = "Base tool adapter"

    # Instance attributes
    supports_async: bool = False
    allow_cache: bool = True
    config: ToolExecutionConfig
    circuit_breaker: CircuitBreaker
    rate_limiter: Optional[RateLimiter]
    status: AdapterStatus
    _last_result: Optional[ToolExecutionResult]

    def __init__(self, config: Optional[ToolExecutionConfig] = None):
        """Initialize the adapter"""
        self.config = config or ToolExecutionConfig()
        self.config.validate()

        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.circuit_breaker_threshold,
            timeout=self.config.circuit_breaker_timeout
        )

        self.rate_limiter = RateLimiter(self.config.rate_limit) if self.config.rate_limit else None
        self.status = AdapterStatus.HEALTHY
        self._last_result = None

    # ---- Public API ----
    def execute(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Execute the tool synchronously"""
        if self.supports_async:
            # For async adapters, run in event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If loop is running, we can't use asyncio.run()
                    # This is a limitation - async adapters should be called with execute_async
                    raise RuntimeError("Async adapter called in sync context with running event loop")
                else:
                    return loop.run_until_complete(self.execute_async(params))
            except RuntimeError:
                # Fallback: run in thread pool if no event loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self.execute_async(params))
                    return future.result()
        else:
            return self._execute_sync(params)

    async def execute_async(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Execute the tool asynchronously"""
        if not self.supports_async:
            raise RuntimeError(f"Adapter {self.name} does not support async execution")

        # For sync adapters called async, we still run them in a thread
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._execute_sync, params)

    def _execute_sync(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Internal sync execution with retry logic"""
        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            return ToolExecutionResult(
                success=False,
                error="Circuit breaker is open",
                metadata={"adapter": self.name, "version": self.version}
            )

        # Check rate limiter
        if self.rate_limiter and not self.rate_limiter.can_make_request():
            return ToolExecutionResult(
                success=False,
                error="Rate limit exceeded",
                metadata={"adapter": self.name, "version": self.version}
            )

        last_exception = None
        for attempt in range(self.config.max_retries + 1):
            try:
                # Record rate limit
                if self.rate_limiter:
                    self.rate_limiter.record_request()

                # Execute with timeout if specified
                if self.config.timeout:
                    result = self._execute_with_timeout(params, self.config.timeout)
                else:
                    result = self._execute_once(params)

                # Record success
                self.circuit_breaker.record_success()
                self.status = AdapterStatus.HEALTHY
                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"ToolAdapter {self.name} attempt {attempt + 1} failed: {e}")

                # Record failure
                self.circuit_breaker.record_failure()
                if self.circuit_breaker._state == "open":
                    self.status = AdapterStatus.UNHEALTHY
                elif self.circuit_breaker._failures > 0:
                    self.status = AdapterStatus.DEGRADED

                # Don't retry on validation errors
                if isinstance(e, (ValueError, TypeError)):
                    break

                # Wait before retry (sync context)
                if attempt < self.config.max_retries:
                    delay = self.config.retry_delay * (self.config.retry_backoff ** attempt)
                    time.sleep(delay)

        # All retries failed
        return ToolExecutionResult(
            success=False,
            error=f"All {self.config.max_retries + 1} attempts failed. Last error: {last_exception}",
            metadata={"adapter": self.name, "version": self.version, "attempts": self.config.max_retries + 1}
        )

    def _execute_with_timeout(self, params: Dict[str, Any], timeout: float) -> ToolExecutionResult:
        """Execute with timeout"""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Execution timed out after {timeout} seconds")

        # Set timeout signal
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout))

        try:
            result = self._execute_once(params)
            return result
        finally:
            # Restore signal handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    def _execute_once(self, params: Dict[str, Any]) -> ToolExecutionResult:
        """Execute a single attempt"""
        start = time.perf_counter()
        ih = self._hash_input(params) if self.allow_cache else None

        # Check cache first
        if ih and tool_adapter_cache:
            cached = tool_adapter_cache.get(f"{self.name}:{ih}")
            if cached:
                logger.debug(f"Cache hit for {self.name}:{ih}")
                return cached

        try:
            # Validation
            self._validate(params)

            # Pre-hook
            self._pre_hook(params)

            # Main execution
            output = self._run(params)

            # Post-hook
            self._post_hook(params, output)

            # Create result
            result = ToolExecutionResult(
                success=True,
                output=output,
                duration_ms=(time.perf_counter() - start) * 1000.0,
                input_hash=ih,
                metadata={
                    "adapter": self.name,
                    "version": self.version,
                    "attempt": 1
                },
            )

        except Exception as e:
            result = ToolExecutionResult(
                success=False,
                error=str(e),
                duration_ms=(time.perf_counter() - start) * 1000.0,
                input_hash=ih,
                metadata={
                    "adapter": self.name,
                    "version": self.version,
                    "attempt": 1
                },
            )

        self._last_result = result

        # Cache successful results
        if ih and tool_adapter_cache and result.success:
            tool_adapter_cache.put(f"{self.name}:{ih}", result)

        # Record metrics if available
        if metrics:
            metrics.record_tool_adapter_execution(self.name, result.success, result.duration_ms)

        return result

    # ---- Abstract methods (to be implemented by subclasses) ----
    def _run(self, params: Dict[str, Any]) -> Any:
        """Main execution logic - must be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _run method")

    def _validate(self, params: Dict[str, Any]) -> None:
        """Validate input parameters - can be overridden by subclasses"""
        pass

    def _pre_hook(self, params: Dict[str, Any]) -> None:
        """Pre-execution hook - can be overridden by subclasses"""
        pass

    def _post_hook(self, params: Dict[str, Any], output: Any) -> None:
        """Post-execution hook - can be overridden by subclasses"""
        pass

    def _hash_input(self, params: Dict[str, Any]) -> str:
        """Generate hash for input parameters for caching"""
        # Create a normalized string representation
        param_str = json.dumps(params, sort_keys=True, default=str)
        return hashlib.sha256(param_str.encode()).hexdigest()

# ---- Registry ----
class ToolRegistry:
    def __init__(self):
        self._registry: Dict[str, ToolAdapter] = {}

    def register(self, adapter: ToolAdapter) -> None:
        self._registry[adapter.name] = adapter

    def get(self, name: str) -> Optional[ToolAdapter]:
        return self._registry.get(name)

    def list(self) -> Dict[str, Dict[str, Any]]:
        return {k: {"version": v.version, "description": v.description} for k, v in self._registry.items()}

# Singleton
_tool_registry = ToolRegistry()

def get_tool_registry() -> ToolRegistry:
    return _tool_registry

# ---- Example Adapter ----
class EchoAdapter(ToolAdapter):
    name = "echo"
    version = "0.1.0"
    description = "Dev adapter que retorna los parámetros con eco y métrica simple"

    def _run(self, params: Dict[str, Any]) -> Any:
        # Operación trivial: devolver parámetros + longitud
        return {
            "echo": params,
            "length": len(params),
        }

# Registrar ejemplo al importar
_tool_registry.register(EchoAdapter())