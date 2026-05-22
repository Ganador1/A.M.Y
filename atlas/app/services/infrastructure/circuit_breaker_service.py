"""
Circuit Breaker Service for AXIOM
Implementa patrones de circuit breaker y graceful degradation

Ethics & Safety:
- Previene cascadas de fallos que podrían afectar servicios críticos.
- Implementa timeouts apropiados para evitar bloqueos indefinidos.
- Registra todos los fallos para análisis post-mortem.
- Proporciona fallbacks seguros para operaciones críticas.

Ver ETHICS_AND_SAFETY.md para detalles y checklist.
"""

import logging
import asyncio
import time
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field
import threading
from functools import wraps
import json
import aiofiles

from app.services.base_service import BaseService
from app.exceptions import AtlasInfrastructureError
from app.exceptions.domain.biology import BiologyError
from app.types.circuit_breaker_service_types import (
    GetStatsResult,
    GetServiceInfoResult,
    CacheFallbackResult,
    DefaultResponseFallbackResult,
    DegradedServiceFallbackResult,
    GetAllStatsResult,
    HealthCheckResult,
)

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Estados del circuit breaker"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, blocking requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class FailureType(Enum):
    """Tipos de fallos"""
    TIMEOUT = "timeout"
    EXCEPTION = "exception"
    RATE_LIMIT = "rate_limit"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    DEPENDENCY_FAILURE = "dependency_failure"


@dataclass
class CircuitBreakerConfig:
    """Configuración del circuit breaker"""
    failure_threshold: int = 5          # Fallos antes de abrir
    recovery_timeout: int = 60          # Segundos antes de intentar recovery
    success_threshold: int = 3          # Éxitos para cerrar desde half-open
    timeout: float = 30.0               # Timeout por defecto
    max_concurrent_calls: int = 100     # Máximo de llamadas concurrentes
    failure_rate_threshold: float = 0.5 # Tasa de fallos para abrir (50%)
    min_calls_threshold: int = 10       # Mínimo de llamadas para evaluar tasa


@dataclass
class CircuitBreakerStats:
    """Estadísticas del circuit breaker"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    timeout_calls: int = 0
    concurrent_calls: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    failure_rate: float = 0.0
    average_response_time: float = 0.0
    response_times: List[float] = field(default_factory=list)


class CircuitBreaker:
    """
    Implementación de Circuit Breaker pattern
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.last_failure_time = None
        self.lock = threading.RLock()
        
        # Fallback functions
        self.fallback_functions: Dict[str, Callable] = {}
        
        # Event listeners
        self.state_change_listeners: List[Callable] = []
    
    def add_fallback(self, operation: str, fallback_func: Callable):
        """Agregar función de fallback para una operación"""
        self.fallback_functions[operation] = fallback_func
    
    def add_state_change_listener(self, listener: Callable):
        """Agregar listener para cambios de estado"""
        self.state_change_listeners.append(listener)
    
    def _notify_state_change(self, old_state: CircuitState, new_state: CircuitState):
        """Notificar cambio de estado"""
        for listener in self.state_change_listeners:
            try:
                listener(self.name, old_state, new_state, self.stats)
            except BiologyError as e:
                logger.warning(f"State change listener failed: {e}")
    
    def _change_state(self, new_state: CircuitState):
        """Cambiar estado del circuit breaker"""
        old_state = self.state
        self.state = new_state
        
        if old_state != new_state:
            logger.info(f"Circuit breaker {self.name} changed from {old_state.value} to {new_state.value}")
            self._notify_state_change(old_state, new_state)
    
    def _should_open(self) -> bool:
        """Determinar si el circuit breaker debe abrirse"""
        # Check failure threshold
        if self.consecutive_failures >= self.config.failure_threshold:
            return True
        
        # Check failure rate
        if (self.stats.total_calls >= self.config.min_calls_threshold and
            self.stats.failure_rate >= self.config.failure_rate_threshold):
            return True
        
        return False
    
    def _should_attempt_reset(self) -> bool:
        """Determinar si se debe intentar reset desde estado OPEN"""
        if not self.last_failure_time:
            return True
        
        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.config.recovery_timeout
    
    def _record_success(self, response_time: float):
        """Registrar llamada exitosa"""
        with self.lock:
            self.stats.total_calls += 1
            self.stats.successful_calls += 1
            self.stats.concurrent_calls = max(0, self.stats.concurrent_calls - 1)
            self.stats.last_success_time = datetime.now()
            
            # Update response times
            self.stats.response_times.append(response_time)
            if len(self.stats.response_times) > 100:  # Keep last 100
                self.stats.response_times.pop(0)
            
            self.stats.average_response_time = sum(self.stats.response_times) / len(self.stats.response_times)
            
            # Update failure rate
            if self.stats.total_calls > 0:
                self.stats.failure_rate = self.stats.failed_calls / self.stats.total_calls
            
            self.consecutive_failures = 0
            self.consecutive_successes += 1
            
            # State transitions
            if self.state == CircuitState.HALF_OPEN:
                if self.consecutive_successes >= self.config.success_threshold:
                    self._change_state(CircuitState.CLOSED)
    
    def _record_failure(self, failure_type: FailureType, response_time: float = 0.0):
        """Registrar llamada fallida"""
        with self.lock:
            self.stats.total_calls += 1
            self.stats.failed_calls += 1
            self.stats.concurrent_calls = max(0, self.stats.concurrent_calls - 1)
            self.stats.last_failure_time = datetime.now()
            self.last_failure_time = time.time()
            
            if failure_type == FailureType.TIMEOUT:
                self.stats.timeout_calls += 1
            
            # Update failure rate
            if self.stats.total_calls > 0:
                self.stats.failure_rate = self.stats.failed_calls / self.stats.total_calls
            
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            
            # State transitions
            if self.state == CircuitState.CLOSED and self._should_open():
                self._change_state(CircuitState.OPEN)
            elif self.state == CircuitState.HALF_OPEN:
                self._change_state(CircuitState.OPEN)
    
    async def call(self, func: Callable, *args, operation: str = "default", **kwargs) -> Any:
        """Ejecutar función con circuit breaker"""
        
        # Check concurrent calls limit
        if self.stats.concurrent_calls >= self.config.max_concurrent_calls:
            raise AtlasInfrastructureError(
                f"Circuit breaker {self.name}: Too many concurrent calls",
                details={"breaker": self.name, "limit": self.config.max_concurrent_calls}
            )
        
        # State-based behavior
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._change_state(CircuitState.HALF_OPEN)
            else:
                # Try fallback
                if operation in self.fallback_functions:
                    logger.info(f"Circuit breaker {self.name} OPEN, using fallback for {operation}")
                    return await self._execute_fallback(operation, *args, **kwargs)
                else:
                    raise AtlasInfrastructureError(
                        f"Circuit breaker {self.name} is OPEN",
                        details={"breaker": self.name, "state": "open"}
                    )
        
        # Execute the function
        self.stats.concurrent_calls += 1
        start_time = time.time()
        
        try:
            # Apply timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs),
                timeout=self.config.timeout
            )
            
            response_time = time.time() - start_time
            self._record_success(response_time)
            return result
        
        except asyncio.TimeoutError:
            response_time = time.time() - start_time
            self._record_failure(FailureType.TIMEOUT, response_time)
            
            # Try fallback
            if operation in self.fallback_functions:
                logger.warning(f"Circuit breaker {self.name} timeout, using fallback for {operation}")
                return await self._execute_fallback(operation, *args, **kwargs)
            else:
                raise AtlasInfrastructureError(
                    f"Circuit breaker {self.name}: Operation timed out",
                    details={"breaker": self.name, "reason": "timeout", "timeout": self.config.timeout}
                )
        
        except BiologyError as e:
            response_time = time.time() - start_time
            self._record_failure(FailureType.EXCEPTION, response_time)
            
            # Try fallback
            if operation in self.fallback_functions:
                logger.warning(f"Circuit breaker {self.name} exception, using fallback for {operation}: {e}")
                return await self._execute_fallback(operation, *args, **kwargs)
            else:
                raise AtlasInfrastructureError(
                    f"Circuit breaker {self.name}: Operation failed",
                    details={"breaker": self.name, "operation": operation, "error": str(e)},
                    cause=e
                ) from e
    
    async def _execute_fallback(self, operation: str, *args, **kwargs) -> Any:
        """Ejecutar función de fallback"""
        try:
            fallback_func = self.fallback_functions[operation]
            if asyncio.iscoroutinefunction(fallback_func):
                return await fallback_func(*args, **kwargs)
            else:
                return fallback_func(*args, **kwargs)
        except BiologyError as e:
            logger.error(f"Fallback function failed for {operation}: {e}")
            raise AtlasInfrastructureError(
                f"Both primary and fallback functions failed for {operation}",
                details={"breaker": self.name, "operation": operation, "error": str(e)},
                cause=e
            ) from e
    
    def get_stats(self) -> GetStatsResult:
        """Obtener estadísticas del circuit breaker"""
        return {
            'name': self.name,
            'state': self.state.value,
            'total_calls': self.stats.total_calls,
            'successful_calls': self.stats.successful_calls,
            'failed_calls': self.stats.failed_calls,
            'timeout_calls': self.stats.timeout_calls,
            'concurrent_calls': self.stats.concurrent_calls,
            'failure_rate': self.stats.failure_rate,
            'average_response_time': self.stats.average_response_time,
            'consecutive_failures': self.consecutive_failures,
            'consecutive_successes': self.consecutive_successes,
            'last_failure_time': self.stats.last_failure_time.isoformat() if self.stats.last_failure_time else None,
            'last_success_time': self.stats.last_success_time.isoformat() if self.stats.last_success_time else None
        }
    
    def reset(self):
        """Reset circuit breaker to CLOSED state"""
        with self.lock:
            self._change_state(CircuitState.CLOSED)
            self.consecutive_failures = 0
            self.consecutive_successes = 0
            self.last_failure_time = None


class CircuitBreakerService(BaseService):
    """
    Servicio de Circuit Breakers para AXIOM
    Gestiona múltiples circuit breakers y proporciona graceful degradation
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("CircuitBreaker")
        self.config = config or {}
        
        # Circuit breakers registry
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # Default configurations for different service types
        self.default_configs = {
            'api_service': CircuitBreakerConfig(
                failure_threshold=5,
                recovery_timeout=60,
                timeout=30.0,
                max_concurrent_calls=50
            ),
            'database_service': CircuitBreakerConfig(
                failure_threshold=3,
                recovery_timeout=30,
                timeout=10.0,
                max_concurrent_calls=20
            ),
            'ml_service': CircuitBreakerConfig(
                failure_threshold=2,
                recovery_timeout=120,
                timeout=300.0,  # ML operations can take longer
                max_concurrent_calls=5
            ),
            'external_api': CircuitBreakerConfig(
                failure_threshold=10,
                recovery_timeout=300,
                timeout=60.0,
                max_concurrent_calls=100
            )
        }
        
        # Global fallback strategies
        self.global_fallbacks = {
            'cache_fallback': self._cache_fallback,
            'default_response': self._default_response_fallback,
            'degraded_service': self._degraded_service_fallback
        }
        
        # Monitoring
        self.monitoring_enabled = self.config.get('monitoring_enabled', True)
        self.alert_thresholds = {
            'failure_rate': 0.8,
            'consecutive_failures': 10,
            'open_circuits': 3
        }
        
        # Start monitoring task
        if self.monitoring_enabled:
            asyncio.create_task(self._monitor_circuit_breakers())
    
    def get_service_info(self) -> GetServiceInfoResult:
        """Get information about circuit breaker service"""
        return {
            "active_circuit_breakers": len(self.circuit_breakers),
            "default_configurations": list(self.default_configs.keys()),
            "global_fallbacks": list(self.global_fallbacks.keys()),
            "monitoring_enabled": self.monitoring_enabled,
            "features": [
                "Automatic failure detection",
                "Configurable thresholds",
                "Multiple fallback strategies",
                "Real-time monitoring",
                "State change notifications",
                "Performance metrics"
            ],
            "circuit_breaker_states": {
                name: cb.state.value for name, cb in self.circuit_breakers.items()
            }
        }
    
    def create_circuit_breaker(self,
                             name: str,
                             service_type: str = 'api_service',
                             custom_config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        """
        Crear un nuevo circuit breaker
        """
        
        if name in self.circuit_breakers:
            logger.warning(f"Circuit breaker {name} already exists")
            return self.circuit_breakers[name]
        
        # Use custom config or default for service type
        config = custom_config or self.default_configs.get(service_type, self.default_configs['api_service'])
        
        # Create circuit breaker
        circuit_breaker = CircuitBreaker(name, config)
        
        # Add state change listener
        circuit_breaker.add_state_change_listener(self._on_state_change)
        
        # Register
        self.circuit_breakers[name] = circuit_breaker
        
        logger.info(f"Created circuit breaker {name} with type {service_type}")
        return circuit_breaker
    
    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Obtener circuit breaker por nombre"""
        return self.circuit_breakers.get(name)
    
    def add_fallback_strategy(self,
                            circuit_breaker_name: str,
                            operation: str,
                            fallback_func: Callable):
        """Agregar estrategia de fallback a un circuit breaker"""
        
        circuit_breaker = self.circuit_breakers.get(circuit_breaker_name)
        if circuit_breaker:
            circuit_breaker.add_fallback(operation, fallback_func)
            logger.info(f"Added fallback for {operation} in circuit breaker {circuit_breaker_name}")
        else:
            logger.error(f"Circuit breaker {circuit_breaker_name} not found")
    
    async def execute_with_circuit_breaker(self,
                                         circuit_breaker_name: str,
                                         func: Callable,
                                         *args,
                                         operation: str = "default",
                                         **kwargs) -> Any:
        """
        Ejecutar función con circuit breaker
        """
        
        circuit_breaker = self.circuit_breakers.get(circuit_breaker_name)
        if not circuit_breaker:
            # Create default circuit breaker if not exists
            circuit_breaker = self.create_circuit_breaker(circuit_breaker_name)
        
        return await circuit_breaker.call(func, *args, operation=operation, **kwargs)
    
    def circuit_breaker_decorator(self, name: str, operation: str = "default"):
        """
        Decorador para aplicar circuit breaker a funciones
        """
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                return await self.execute_with_circuit_breaker(
                    name, func, *args, operation=operation, **kwargs
                )
            return wrapper
        return decorator
    
    async def _cache_fallback(self, *args, **kwargs) -> CacheFallbackResult:
        """Fallback que retorna datos cacheados"""
        return {
            'status': 'fallback',
            'source': 'cache',
            'data': None,
            'message': 'Service unavailable, using cached data'
        }
    
    async def _default_response_fallback(self, *args, **kwargs) -> DefaultResponseFallbackResult:
        """Fallback que retorna respuesta por defecto"""
        return {
            'status': 'fallback',
            'source': 'default',
            'data': {},
            'message': 'Service unavailable, using default response'
        }
    
    async def _degraded_service_fallback(self, *args, **kwargs) -> DegradedServiceFallbackResult:
        """Fallback que proporciona servicio degradado"""
        return {
            'status': 'degraded',
            'source': 'fallback',
            'data': {'limited': True},
            'message': 'Service running in degraded mode'
        }
    
    def _on_state_change(self, name: str, old_state: CircuitState, 
                        new_state: CircuitState, stats: CircuitBreakerStats):
        """Manejar cambios de estado de circuit breakers"""
        
        logger.info(f"Circuit breaker {name} state changed: {old_state.value} -> {new_state.value}")
        
        # Check for alerts
        if new_state == CircuitState.OPEN:
            self._trigger_alert(f"Circuit breaker {name} opened", {
                'circuit_breaker': name,
                'failure_rate': stats.failure_rate,
                'consecutive_failures': stats.failed_calls,
                'last_failure': stats.last_failure_time
            })
        
        # Log metrics
        if self.monitoring_enabled:
            self._log_circuit_breaker_metrics(name, stats)
    
    def _trigger_alert(self, message: str, context: Dict[str, Any]):
        """Disparar alerta"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'context': context,
            'severity': 'warning'
        }
        
        # Log the alert
        logger.warning(f"Circuit breaker alert: {alert['message']}", extra=alert)
        
        logger.warning(f"ALERT: {message} - Context: {context}")
        
        # Here you would integrate with alerting systems
        # (Slack, email, PagerDuty, etc.)
    
    def _log_circuit_breaker_metrics(self, name: str, stats: CircuitBreakerStats):
        """Log métricas del circuit breaker"""
        metrics = {
            'circuit_breaker': name,
            'timestamp': datetime.now().isoformat(),
            'total_calls': stats.total_calls,
            'failure_rate': stats.failure_rate,
            'average_response_time': stats.average_response_time,
            'concurrent_calls': stats.concurrent_calls
        }
        
        # Here you would send to metrics collection system
        logger.debug(f"Circuit breaker metrics: {json.dumps(metrics)}")
    
    async def _monitor_circuit_breakers(self):
        """Monitorear circuit breakers periódicamente"""
        while True:
            try:
                open_circuits = 0
                high_failure_rate_circuits = 0
                
                for name, cb in self.circuit_breakers.items():
                    stats = cb.get_stats()
                    
                    # Count open circuits
                    if cb.state == CircuitState.OPEN:
                        open_circuits += 1
                    
                    # Check failure rate
                    if stats['failure_rate'] > self.alert_thresholds['failure_rate']:
                        high_failure_rate_circuits += 1
                        
                        if stats['total_calls'] > 10:  # Only alert if significant traffic
                            self._trigger_alert(
                                f"High failure rate in circuit breaker {name}",
                                {'failure_rate': stats['failure_rate'], 'total_calls': stats['total_calls']}
                            )
                
                # Global alerts
                if open_circuits >= self.alert_thresholds['open_circuits']:
                    self._trigger_alert(
                        f"Multiple circuit breakers open: {open_circuits}",
                        {'open_circuits': open_circuits}
                    )
                
                # Log overall health
                logger.info(f"Circuit breaker health check: {len(self.circuit_breakers)} total, "
                          f"{open_circuits} open, {high_failure_rate_circuits} high failure rate")
                
                await asyncio.sleep(60)  # Check every minute
            
            except BiologyError as e:
                logger.error(f"Circuit breaker monitoring error: {e}")
                await asyncio.sleep(120)  # Wait longer on error
    
    def get_all_stats(self) -> GetAllStatsResult:
        """Obtener estadísticas de todos los circuit breakers"""
        return {
            'circuit_breakers': {name: cb.get_stats() for name, cb in self.circuit_breakers.items()},
            'summary': {
                'total_circuit_breakers': len(self.circuit_breakers),
                'open_circuits': sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.OPEN),
                'half_open_circuits': sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.HALF_OPEN),
                'closed_circuits': sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.CLOSED)
            }
        }
    
    def reset_circuit_breaker(self, name: str) -> bool:
        """Reset un circuit breaker específico"""
        circuit_breaker = self.circuit_breakers.get(name)
        if circuit_breaker:
            circuit_breaker.reset()
            logger.info(f"Reset circuit breaker {name}")
            return True
        return False
    
    def reset_all_circuit_breakers(self):
        """Reset todos los circuit breakers"""
        for name, cb in self.circuit_breakers.items():
            cb.reset()
        logger.info("Reset all circuit breakers")
    
    async def health_check(self) -> HealthCheckResult:
        """Realizar health check del servicio"""
        healthy_circuits = sum(1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.CLOSED)
        total_circuits = len(self.circuit_breakers)
        
        health_percentage = (healthy_circuits / total_circuits * 100) if total_circuits > 0 else 100
        
        return {
            'status': 'healthy' if health_percentage >= 80 else 'degraded' if health_percentage >= 50 else 'unhealthy',
            'health_percentage': health_percentage,
            'healthy_circuits': healthy_circuits,
            'total_circuits': total_circuits,
            'monitoring_enabled': self.monitoring_enabled,
            'timestamp': datetime.now().isoformat()
        }