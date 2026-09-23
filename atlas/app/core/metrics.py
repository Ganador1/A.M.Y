"""
Enhanced Metrics and Monitoring System for AXIOM ATLAS

Features:
- Prometheus metrics collection
- Performance monitoring
- Custom metrics for database operations
- Tool adapter metrics
- Medical imaging metrics
- Health check metrics
- Export capabilities
- Real-time monitoring
"""

import time
import psutil
import threading
from contextlib import contextmanager
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from functools import wraps
import logging
import aiofiles

try:
    from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    # Create dummy classes for when prometheus is not available
    class DummyMetric:
        def __init__(self, name, documentation, **kwargs):
            self.name = name
            self.documentation = documentation

        def inc(self, amount=1):
            pass

        def set(self, value):
            pass

        def observe(self, value):
            pass

    Counter = Gauge = Histogram = Summary = DummyMetric


logger = logging.getLogger(__name__)


class MetricsCollector:
    """Enhanced metrics collector with Prometheus integration"""

    def __init__(self):
        self.registry = CollectorRegistry() if PROMETHEUS_AVAILABLE else None

        # System metrics
        self.cpu_usage = Gauge(
            'axiom_cpu_usage_percent',
            'Current CPU usage percentage',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('cpu_usage', 'CPU usage')

        self.memory_usage = Gauge(
            'axiom_memory_usage_percent',
            'Current memory usage percentage',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('memory_usage', 'Memory usage')

        self.disk_usage = Gauge(
            'axiom_disk_usage_percent',
            'Current disk usage percentage',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('disk_usage', 'Disk usage')

        # Database metrics
        self.db_connections_total = Counter(
            'axiom_db_connections_total',
            'Total database connections',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('db_connections_total', 'DB connections')

        self.db_connection_failures = Counter(
            'axiom_db_connection_failures_total',
            'Total database connection failures',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('db_connection_failures', 'DB connection failures')

        self.db_queries_total = Counter(
            'axiom_db_queries_total',
            'Total database queries',
            ['operation', 'status'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('db_queries_total', 'DB queries')

        self.db_query_duration = Histogram(
            'axiom_db_query_duration_seconds',
            'Database query duration',
            ['operation'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Histogram('db_query_duration', 'DB query duration')

        self.db_pool_size = Gauge(
            'axiom_db_pool_size',
            'Database connection pool size',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('db_pool_size', 'DB pool size')

        self.db_pool_active = Gauge(
            'axiom_db_pool_active_connections',
            'Database connection pool active connections',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('db_pool_active', 'DB pool active')

        # Tool adapter metrics
        self.adapter_executions_total = Counter(
            'axiom_adapter_executions_total',
            'Total tool adapter executions',
            ['adapter_name', 'status'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('adapter_executions_total', 'Adapter executions')

        self.adapter_execution_duration = Histogram(
            'axiom_adapter_execution_duration_seconds',
            'Tool adapter execution duration',
            ['adapter_name'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Histogram('adapter_execution_duration', 'Adapter execution duration')

        self.adapter_circuit_breaker_state = Gauge(
            'axiom_adapter_circuit_breaker_state',
            'Tool adapter circuit breaker state',
            ['adapter_name', 'state'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('adapter_circuit_breaker_state', 'Circuit breaker state')

        self.adapter_rate_limiter_active = Gauge(
            'axiom_adapter_rate_limiter_active',
            'Tool adapter rate limiter active connections',
            ['adapter_name'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('adapter_rate_limiter_active', 'Rate limiter active')

        # Medical imaging metrics
        self.medical_images_processed = Counter(
            'axiom_medical_images_processed_total',
            'Total medical images processed',
            ['modality'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('medical_images_processed', 'Medical images processed')

        self.medical_image_size = Histogram(
            'axiom_medical_image_size_bytes',
            'Medical image size distribution',
            ['modality'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Histogram('medical_image_size', 'Medical image size')

        self.medical_image_validation_errors = Counter(
            'axiom_medical_image_validation_errors_total',
            'Total medical image validation errors',
            ['error_type'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('medical_image_validation_errors', 'Medical image validation errors')

        # Performance metrics
        self.api_requests_total = Counter(
            'axiom_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status_code'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('api_requests_total', 'API requests')

        self.api_request_duration = Histogram(
            'axiom_api_request_duration_seconds',
            'API request duration',
            ['endpoint', 'method'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Histogram('api_request_duration', 'API request duration')

        self.active_connections = Gauge(
            'axiom_active_connections',
            'Number of active connections',
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Gauge('active_connections', 'Active connections')

        # Health check metrics
        self.health_check_success = Counter(
            'axiom_health_check_success_total',
            'Total successful health checks',
            ['check_type'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('health_check_success', 'Health check success')

        self.health_check_failures = Counter(
            'axiom_health_check_failures_total',
            'Total failed health checks',
            ['check_type'],
            registry=self.registry
        ) if PROMETHEUS_AVAILABLE else Counter('health_check_failures', 'Health check failures')

        # Start background collection
        self._start_background_collection()

    def _start_background_collection(self):
        """
        Start background metrics collection.
        
        NOTE: Uses threading.Thread with time.sleep() in daemon thread.
        This is acceptable because:
        - Runs in separate OS thread (not blocking main event loop)
        - Daemon thread (dies with main process)
        - Low-frequency metrics collection (30-60s intervals)
        
        TODO (ROADMAP 5): Consider migrating to asyncio.create_task with
        asyncio.sleep() if this code needs to run in async context.
        """
        def collect_system_metrics():
            while True:
                try:
                    # System metrics
                    self.cpu_usage.set(psutil.cpu_percent(interval=1))
                    self.memory_usage.set(psutil.virtual_memory().percent)
                    self.disk_usage.set(psutil.disk_usage('/').percent)

                    # Connection count
                    self.active_connections.set(len(psutil.net_connections()))

                    # NOTE: time.sleep() in daemon thread - does not block event loop
                    time.sleep(30)  # Collect every 30 seconds
                except Exception:
                    logger.exception("Error collecting system metrics")
                    time.sleep(60)  # Longer sleep on error

        thread = threading.Thread(target=collect_system_metrics, daemon=True)
        thread.start()

    def record_database_connection(self, success: bool):
        """Record database connection attempt"""
        if success:
            self.db_connections_total.inc()
        else:
            self.db_connections_total.inc()
            self.db_connection_failures.inc()

    def record_database_query(self, operation: str, duration_seconds: float, success: bool = True):
        """Record database query metrics"""
        status = "success" if success else "error"
        self.db_queries_total.labels(operation=operation, status=status).inc()
        self.db_query_duration.labels(operation=operation).observe(duration_seconds)

    def update_database_pool_metrics(self, pool_size: int, active_connections: int):
        """Update database pool metrics"""
        self.db_pool_size.set(pool_size)
        self.db_pool_active.set(active_connections)

    def record_tool_adapter_execution(
        self,
        adapter_name: str,
        duration_seconds: float,
        success: bool = True,
        circuit_breaker_state: Optional[str] = None,
        rate_limiter_active: Optional[int] = None
    ):
        """Record tool adapter execution metrics"""
        status = "success" if success else "error"
        self.adapter_executions_total.labels(
            adapter_name=adapter_name,
            status=status
        ).inc()

        self.adapter_execution_duration.labels(
            adapter_name=adapter_name
        ).observe(duration_seconds)

        if circuit_breaker_state:
            # Reset all states to 0
            for state in ['closed', 'open', 'half_open']:
                self.adapter_circuit_breaker_state.labels(
                    adapter_name=adapter_name,
                    state=state
                ).set(0)

            # Set current state to 1
            self.adapter_circuit_breaker_state.labels(
                adapter_name=adapter_name,
                state=circuit_breaker_state
            ).set(1)

        if rate_limiter_active is not None:
            self.adapter_rate_limiter_active.labels(
                adapter_name=adapter_name
            ).set(rate_limiter_active)

    def record_medical_image_processing(
        self,
        modality: str,
        image_size_bytes: int,
        validation_errors: Optional[Dict[str, int]] = None
    ):
        """Record medical image processing metrics"""
        self.medical_images_processed.labels(modality=modality).inc()
        self.medical_image_size.labels(modality=modality).observe(image_size_bytes)

        if validation_errors:
            for error_type, count in validation_errors.items():
                self.medical_image_validation_errors.labels(
                    error_type=error_type
                ).inc(count)

    def record_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_seconds: float
    ):
        """Record API request metrics"""
        self.api_requests_total.labels(
            endpoint=endpoint,
            method=method,
            status_code=str(status_code)
        ).inc()

        self.api_request_duration.labels(
            endpoint=endpoint,
            method=method
        ).observe(duration_seconds)

    def record_health_check(self, check_type: str, success: bool):
        """Record health check metrics"""
        if success:
            self.health_check_success.labels(check_type=check_type).inc()
        else:
            self.health_check_failures.labels(check_type=check_type).inc()

    def get_metrics_text(self) -> str:
        """Get metrics in Prometheus format"""
        if PROMETHEUS_AVAILABLE and self.registry:
            return generate_latest(self.registry).decode('utf-8')
        return "# Prometheus metrics not available"

    def get_custom_metrics(self) -> Dict[str, Any]:
        """Get custom metrics for JSON export"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "active_connections": len(psutil.net_connections())
            },
            "database": {
                "connections_total": self.db_connections_total._value.get() if PROMETHEUS_AVAILABLE else 0,
                "connection_failures": self.db_connection_failures._value.get() if PROMETHEUS_AVAILABLE else 0,
                "pool_size": self.db_pool_size._value.get() if PROMETHEUS_AVAILABLE else 0,
                "pool_active": self.db_pool_active._value.get() if PROMETHEUS_AVAILABLE else 0
            },
            "tool_adapters": {
                "executions_total": sum(
                    label_values[1]._value.get() if PROMETHEUS_AVAILABLE else 0
                    for label_values in self.adapter_executions_total._metrics.items()
                )
            },
            "api": {
                "requests_total": sum(
                    label_values[1]._value.get() if PROMETHEUS_AVAILABLE else 0
                    for label_values in self.api_requests_total._metrics.items()
                )
            }
        }


# Global metrics collector
metrics = MetricsCollector()


async def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics (async with CPU executor)"""
    from app.core.executors import run_cpu_bound
    
    def _get_system_metrics_sync() -> Dict[str, Any]:
        try:
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "cpu": {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "count_logical": psutil.cpu_count(logical=True)
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "percent": psutil.virtual_memory().percent,
                    "used": psutil.virtual_memory().used
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "free": psutil.disk_usage('/').free,
                    "percent": psutil.disk_usage('/').percent
                },
                "network": {
                    "connections": len(psutil.net_connections()),
                    "io_counters": {
                        "bytes_sent": psutil.net_io_counters().bytes_sent,
                        "bytes_recv": psutil.net_io_counters().bytes_recv
                    }
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    return await run_cpu_bound(_get_system_metrics_sync)


def timing_decorator(operation_name: str):
    """Decorator to measure execution time"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                duration = time.perf_counter() - start_time

                # Record performance metric
                metrics.record_api_request(
                    endpoint=operation_name,
                    method="function",
                    status_code=200,
                    duration_seconds=duration
                )

                return result
            except Exception:
                duration = time.perf_counter() - start_time
                metrics.record_api_request(
                    endpoint=operation_name,
                    method="function",
                    status_code=500,
                    duration_seconds=duration
                )
                raise
        return wrapper
    return decorator


@contextmanager
def timing_context(operation_name: str, **labels):
    """Context manager to measure execution time"""
    start_time = time.perf_counter()
    try:
        yield
        duration = time.perf_counter() - start_time

        # Record metric
        if operation_name == "database_query":
            metrics.record_database_query(
                operation=labels.get('operation', 'unknown'),
                duration_seconds=duration,
                success=True
            )
        elif operation_name == "tool_adapter":
            metrics.record_tool_adapter_execution(
                adapter_name=labels.get('adapter_name', 'unknown'),
                duration_seconds=duration,
                success=True
            )

    except Exception:
        duration = time.perf_counter() - start_time

        if operation_name == "database_query":
            metrics.record_database_query(
                operation=labels.get('operation', 'unknown'),
                duration_seconds=duration,
                success=False
            )
        elif operation_name == "tool_adapter":
            metrics.record_tool_adapter_execution(
                adapter_name=labels.get('adapter_name', 'unknown'),
                duration_seconds=duration,
                success=False
            )
        raise


async def export_metrics_to_file(filename: str = "metrics.json"):
    """Export current metrics to JSON file (async)"""
    try:
        import json
        async with aiofiles.open(filename, 'w') as f:
            await f.write(json.dumps(metrics.get_custom_metrics(), indent=2, default=str))
        logger.info("Metrics exported to %s", filename)
    except Exception:
        logger.exception("Error exporting metrics to file")


def print_metrics_summary():
    """Print a summary of current metrics"""
    custom_metrics = metrics.get_custom_metrics()

    print("=== AXIOM ATLAS Metrics Summary ===")
    print(f"Timestamp: {custom_metrics['timestamp']}")
    print("\nSystem:")
    sys_metrics = custom_metrics['system']
    print(f"  CPU Usage: {sys_metrics['cpu']['percent']}%")
    print(f"  Memory Usage: {sys_metrics['memory']['percent']}%")
    print(f"  Disk Usage: {sys_metrics['disk']['percent']}%")
    print(f"  Active Connections: {sys_metrics['active_connections']}")

    print("\nDatabase:")
    db_metrics = custom_metrics['database']
    print(f"  Total Connections: {db_metrics['connections_total']}")
    print(f"  Connection Failures: {db_metrics['connection_failures']}")
    print(f"  Pool Size: {db_metrics['pool_size']}")
    print(f"  Pool Active: {db_metrics['pool_active']}")

    print("\nTool Adapters:")
    adapter_metrics = custom_metrics['tool_adapters']
    print(f"  Total Executions: {adapter_metrics['executions_total']}")

    print("\nAPI:")
    api_metrics = custom_metrics['api']
    print(f"  Total Requests: {api_metrics['requests_total']}")


# Initialize background collection
if __name__ == "__main__":
    # This module can be run standalone for testing
    import time

    logger.info("Starting metrics collection...")
    logger.info("Press Ctrl+C to stop")

    try:
        while True:
            print_metrics_summary()
            logger.info("\n%s\n", "="*50)
            time.sleep(30)
    except KeyboardInterrupt:
        logger.info("Metrics collection stopped.")
        export_metrics_to_file()
