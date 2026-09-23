"""
Async Metrics Monitoring for AXIOM ATLAS.

This module provides comprehensive monitoring of async operations,
event loop health, and performance metrics.
"""

import asyncio
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
from pathlib import Path
import psutil
import os
import aiofiles

from prometheus_client import Histogram, Gauge, Counter, start_http_server
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)


# Prometheus metrics
event_loop_lag = Gauge(
    'event_loop_lag_seconds',
    'Event loop lag in seconds',
    ['instance']
)

async_tasks_running = Gauge(
    'async_tasks_running',
    'Number of running async tasks',
    ['instance']
)

slow_callbacks = Counter(
    'slow_callbacks_total',
    'Number of slow async callbacks',
    ['instance', 'callback_type']
)

blocking_operations = Counter(
    'blocking_operations_total',
    'Number of blocking operations detected',
    ['instance', 'operation_type']
)

request_duration = Histogram(
    'request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint', 'status_code']
)

async_operations = Histogram(
    'async_operations_duration_seconds',
    'Async operations duration',
    ['operation_type', 'status']
)

concurrent_requests = Gauge(
    'concurrent_requests',
    'Number of concurrent requests',
    ['instance']
)

memory_usage = Gauge(
    'memory_usage_bytes',
    'Memory usage in bytes',
    ['instance', 'type']
)

cpu_usage = Gauge(
    'cpu_usage_percent',
    'CPU usage percentage',
    ['instance']
)


class AsyncMetricsCollector:
    """Collects and manages async performance metrics."""
    
    def __init__(self, instance_name: str = "atlas"):
        self.instance_name = instance_name
        self.metrics_history = deque(maxlen=1000)
        self.event_loop_lag_history = deque(maxlen=100)
        self.blocking_operations_history = deque(maxlen=100)
        self.running = False
        self._monitoring_task = None
        
        # Performance thresholds
        self.thresholds = {
            "event_loop_lag_ms": 100.0,  # 100ms
            "memory_usage_mb": 1000.0,   # 1GB
            "cpu_usage_percent": 80.0,   # 80%
            "slow_callback_ms": 50.0,    # 50ms
        }
    
    async def start_monitoring(self):
        """Start async metrics monitoring."""
        if self.running:
            return
        
        self.running = True
        self._monitoring_task = asyncio.create_task(self._monitor_loop())
        logger.info("Async metrics monitoring started")
    
    async def stop_monitoring(self):
        """Stop async metrics monitoring."""
        if not self.running:
            return
        
        self.running = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Async metrics monitoring stopped")
    
    async def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(1)  # Collect every second
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)  # Wait longer on error
    
    async def _collect_metrics(self):
        """Collect current metrics."""
        timestamp = datetime.now()
        
        # Event loop lag
        lag_ms = await self._measure_event_loop_lag()
        event_loop_lag.labels(instance=self.instance_name).set(lag_ms / 1000.0)
        self.event_loop_lag_history.append({
            "timestamp": timestamp,
            "lag_ms": lag_ms
        })
        
        # Running tasks
        try:
            loop = asyncio.get_event_loop()
            tasks = asyncio.all_tasks(loop)
            running_tasks = len([t for t in tasks if not t.done()])
            async_tasks_running.labels(instance=self.instance_name).set(running_tasks)
        except Exception as e:
            logger.warning(f"Could not count running tasks: {e}")
        
        # System resources
        process = psutil.Process(os.getpid())
        
        # Memory usage
        memory_mb = process.memory_info().rss / 1024 / 1024
        memory_usage.labels(instance=self.instance_name, type="rss").set(memory_mb * 1024 * 1024)
        
        # CPU usage
        cpu_percent = process.cpu_percent()
        cpu_usage.labels(instance=self.instance_name).set(cpu_percent)
        
        # Check thresholds
        await self._check_thresholds(lag_ms, memory_mb, cpu_percent)
        
        # Store metrics
        metrics = {
            "timestamp": timestamp.isoformat(),
            "event_loop_lag_ms": lag_ms,
            "running_tasks": running_tasks,
            "memory_mb": memory_mb,
            "cpu_percent": cpu_percent,
        }
        
        self.metrics_history.append(metrics)
    
    async def _measure_event_loop_lag(self) -> float:
        """Measure event loop lag."""
        start_time = time.perf_counter()
        await asyncio.sleep(0.01)  # 10ms delay
        actual_delay = time.perf_counter() - start_time
        lag_ms = (actual_delay - 0.01) * 1000
        return max(0, lag_ms)
    
    async def _check_thresholds(self, lag_ms: float, memory_mb: float, cpu_percent: float):
        """Check performance thresholds and generate alerts."""
        alerts = []
        
        if lag_ms > self.thresholds["event_loop_lag_ms"]:
            alerts.append(f"High event loop lag: {lag_ms:.1f}ms")
            blocking_operations.labels(
                instance=self.instance_name,
                operation_type="event_loop_lag"
            ).inc()
        
        if memory_mb > self.thresholds["memory_usage_mb"]:
            alerts.append(f"High memory usage: {memory_mb:.1f}MB")
        
        if cpu_percent > self.thresholds["cpu_usage_percent"]:
            alerts.append(f"High CPU usage: {cpu_percent:.1f}%")
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Performance alert: {alert}")
    
    def record_slow_callback(self, callback_type: str, duration_ms: float):
        """Record a slow callback."""
        slow_callbacks.labels(
            instance=self.instance_name,
            callback_type=callback_type
        ).inc()
        
        self.blocking_operations_history.append({
            "timestamp": datetime.now(),
            "type": "slow_callback",
            "callback_type": callback_type,
            "duration_ms": duration_ms
        })
    
    def record_blocking_operation(self, operation_type: str, duration_ms: float):
        """Record a blocking operation."""
        blocking_operations.labels(
            instance=self.instance_name,
            operation_type=operation_type
        ).inc()
        
        self.blocking_operations_history.append({
            "timestamp": datetime.now(),
            "type": "blocking_operation",
            "operation_type": operation_type,
            "duration_ms": duration_ms
        })
    
    def record_request(self, method: str, endpoint: str, status_code: int, duration: float):
        """Record request metrics."""
        request_duration.labels(
            method=method,
            endpoint=endpoint,
            status_code=str(status_code)
        ).observe(duration)
    
    def record_async_operation(self, operation_type: str, status: str, duration: float):
        """Record async operation metrics."""
        async_operations.labels(
            operation_type=operation_type,
            status=status
        ).observe(duration)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary."""
        if not self.metrics_history:
            return {}
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 measurements
        
        # Calculate averages
        avg_lag = sum(m["event_loop_lag_ms"] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m["memory_mb"] for m in recent_metrics) / len(recent_metrics)
        avg_cpu = sum(m["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_tasks = sum(m["running_tasks"] for m in recent_metrics) / len(recent_metrics)
        
        # Get recent blocking operations
        recent_blocking = list(self.blocking_operations_history)[-10:]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "instance": self.instance_name,
            "averages": {
                "event_loop_lag_ms": avg_lag,
                "memory_mb": avg_memory,
                "cpu_percent": avg_cpu,
                "running_tasks": avg_tasks,
            },
            "thresholds": self.thresholds,
            "recent_blocking_operations": recent_blocking,
            "health_status": self._calculate_health_status(avg_lag, avg_memory, avg_cpu),
        }
    
    def _calculate_health_status(self, lag_ms: float, memory_mb: float, cpu_percent: float) -> str:
        """Calculate overall health status."""
        issues = []
        
        if lag_ms > self.thresholds["event_loop_lag_ms"]:
            issues.append("high_lag")
        
        if memory_mb > self.thresholds["memory_usage_mb"]:
            issues.append("high_memory")
        
        if cpu_percent > self.thresholds["cpu_usage_percent"]:
            issues.append("high_cpu")
        
        if not issues:
            return "healthy"
        elif len(issues) == 1:
            return "warning"
        else:
            return "critical"
    
    def export_metrics(self, output_file: Optional[str] = None) -> str:
        """Export metrics to JSON file."""
        if output_file is None:
            output_file = f"async_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        metrics_data = {
            "export_timestamp": datetime.now().isoformat(),
            "summary": self.get_metrics_summary(),
            "metrics_history": list(self.metrics_history),
            "event_loop_lag_history": list(self.event_loop_lag_history),
            "blocking_operations_history": list(self.blocking_operations_history),
            "system_info": {
                "cpu_count": psutil.cpu_count(),
                "memory_gb": psutil.virtual_memory().total / (1024**3),
                "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            }
        }
        
        with aiofiles.open(output_path, 'w') as f:
            json.dump(metrics_data, f, indent=2, default=str)
        
        logger.info(f"Async metrics exported to: {output_path}")
        return str(output_path)


# Global metrics collector
metrics_collector = AsyncMetricsCollector()


# FastAPI router for metrics endpoints
router = APIRouter(prefix="/api/metrics", tags=["metrics"])


class MetricsResponse(BaseModel):
    """Response model for metrics endpoints."""
    timestamp: str
    instance: str
    health_status: str
    metrics: Dict[str, Any]


@router.get("/async/summary", response_model=MetricsResponse)
async def get_async_metrics_summary():
    """Get async metrics summary."""
    try:
        summary = metrics_collector.get_metrics_summary()
        
        return MetricsResponse(
            timestamp=summary["timestamp"],
            instance=summary["instance"],
            health_status=summary["health_status"],
            metrics=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/async/health")
async def get_async_health():
    """Get async health status."""
    try:
        summary = metrics_collector.get_metrics_summary()
        
        return {
            "status": summary["health_status"],
            "timestamp": summary["timestamp"],
            "instance": summary["instance"],
            "checks": {
                "event_loop_lag": summary["averages"]["event_loop_lag_ms"] < summary["thresholds"]["event_loop_lag_ms"],
                "memory_usage": summary["averages"]["memory_mb"] < summary["thresholds"]["memory_usage_mb"],
                "cpu_usage": summary["averages"]["cpu_percent"] < summary["thresholds"]["cpu_usage_percent"],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/async/blocking-operations")
async def get_blocking_operations(limit: int = 10):
    """Get recent blocking operations."""
    try:
        operations = list(metrics_collector.blocking_operations_history)[-limit:]
        return {
            "operations": operations,
            "count": len(operations),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/async/export")
async def export_async_metrics():
    """Export async metrics to file."""
    try:
        output_file = metrics_collector.export_metrics()
        return {
            "message": "Metrics exported successfully",
            "output_file": output_file,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Utility functions
async def start_metrics_server(port: int = 8001):
    """Start Prometheus metrics server."""
    try:
        start_http_server(port)
        logger.info(f"Prometheus metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Failed to start metrics server: {e}")


async def initialize_async_monitoring():
    """Initialize async monitoring."""
    await metrics_collector.start_monitoring()
    await start_metrics_server()
    logger.info("Async monitoring initialized")


# Example usage
if __name__ == "__main__":
    async def test_metrics():
        """Test metrics collection."""
        await metrics_collector.start_monitoring()
        
        # Simulate some operations
        for i in range(10):
            await asyncio.sleep(0.1)
            metrics_collector.record_async_operation("test_operation", "success", 0.1)
        
        # Get summary
        summary = metrics_collector.get_metrics_summary()
        print(f"Metrics summary: {summary}")
        
        # Export metrics
        output_file = metrics_collector.export_metrics()
        print(f"Metrics exported to: {output_file}")
        
        await metrics_collector.stop_monitoring()
    
    # Run test
    asyncio.run(test_metrics())
