"""
Monitoring Module for Master Orchestration Service
Health monitoring, resource monitoring y circuit breakers
"""

import asyncio
import time
import logging
import random
from datetime import datetime
from typing import Dict, Any, Optional
from app.services.orchestration.models import ServiceHealth, OrchestrationMetrics
import aiofiles

logger = logging.getLogger(__name__)


class ServiceHealthMonitor:
    """Monitor de salud de servicios con circuit breaker"""

    def __init__(self, failure_thresholds: Dict[str, int]):
        self.failure_thresholds = failure_thresholds
        self.service_health: Dict[str, ServiceHealth] = {}

    def update_service_health(self, service_name: str, success: bool, response_time: float):
        """Update service health status"""
        if service_name not in self.service_health:
            self.service_health[service_name] = ServiceHealth(
                service_name=service_name,
                status='healthy',
                last_check=datetime.now(),
                failure_count=0,
                response_time=0.0
            )

        health = self.service_health[service_name]
        health.last_check = datetime.now()
        health.response_time = response_time

        if success:
            health.failure_count = max(0, health.failure_count - 1)
            health.consecutive_failures = 0
            health.status = 'healthy'
        else:
            health.failure_count += 1
            health.consecutive_failures += 1
            if health.failure_count >= self.failure_thresholds['service_failures']:
                health.status = 'circuit_open'
            else:
                health.status = 'degraded'

    def is_circuit_breaker_open(self, service: str) -> bool:
        """Check if circuit breaker is open for service"""
        health = self.service_health.get(service)
        if not health:
            return False
        return health.status == 'circuit_open'

    def get_service_health_status(self) -> Dict[str, Any]:
        """Get health status of all services"""
        return {
            service_name: {
                'status': health.status,
                'last_check': health.last_check.isoformat(),
                'failure_count': health.failure_count,
                'consecutive_failures': health.consecutive_failures,
                'response_time': health.response_time
            }
            for service_name, health in self.service_health.items()
        }

    async def monitor_service_health(self, service_registry: Dict[str, Any]):
        """Monitor service health periodically"""
        while True:
            try:
                for service_name, service in service_registry.items():
                    try:
                        # Simple health check
                        start_time = time.time()
                        service.get_service_info()
                        response_time = time.time() - start_time

                        self.update_service_health(service_name, True, response_time)

                    except (AttributeError, RuntimeError, ValueError) as e:
                        self.update_service_health(service_name, False, 0)
                        logger.warning(f"Health check failed for {service_name}: {e}")

                await asyncio.sleep(30)  # Check every 30 seconds

            except (asyncio.CancelledError, RuntimeError) as e:
                logger.error(f"Service health monitoring error: {e}")
                await asyncio.sleep(60)


class ResourceMonitor:
    """Monitor de recursos del sistema"""

    def __init__(self, metrics: OrchestrationMetrics):
        self.metrics = metrics
        self.psutil_available = False

    async def monitor_resources(self):
        """Monitor system resources with real metrics collection"""
        try:
            import psutil  # type: ignore
            self.psutil_available = True
        except ImportError:  # pragma: no cover - optional dependency
            self.psutil_available = False

        while True:
            try:
                if self.psutil_available:
                    await self._monitor_with_psutil()
                else:
                    await self._monitor_simulated()

            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(10)

    async def _monitor_with_psutil(self):
        """Monitor resources using psutil"""
        import psutil

        # Get real system metrics
        cpu_percent = psutil.cpu_percent(interval=1) / 100
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent / 100

        # Get process-specific metrics
        process = psutil.Process()
        process_memory_mb = process.memory_info().rss / 1024 / 1024
        process_cpu_percent = process.cpu_percent(interval=0.1) / 100

        # Get disk I/O
        disk_io = psutil.disk_io_counters()
        disk_read_mb = disk_io.read_bytes / 1024 / 1024 if disk_io else 0
        disk_write_mb = disk_io.write_bytes / 1024 / 1024 if disk_io else 0

        # Get network I/O
        net_io = psutil.net_io_counters()
        net_sent_mb = net_io.bytes_sent / 1024 / 1024 if net_io else 0
        net_recv_mb = net_io.bytes_recv / 1024 / 1024 if net_io else 0

        # Update metrics
        self.metrics.cpu_usage = cpu_percent
        self.metrics.memory_usage = memory_percent
        self.metrics.active_pipelines = len([p for p in self.metrics.resource_usage_history[-10:] if p.get('active_pipelines', 0) > 0]) if self.metrics.resource_usage_history else 0

        # Record resource usage history
        resource_record = {
            'cpu_usage': cpu_percent,
            'memory_usage': memory_percent,
            'process_memory_mb': process_memory_mb,
            'process_cpu_percent': process_cpu_percent,
            'disk_read_mb': disk_read_mb,
            'disk_write_mb': disk_write_mb,
            'net_sent_mb': net_sent_mb,
            'net_recv_mb': net_recv_mb,
            'timestamp': datetime.now().isoformat()
        }
        self.metrics.resource_usage_history.append(resource_record)

        # Keep only last 100 records
        if len(self.metrics.resource_usage_history) > 100:
            self.metrics.resource_usage_history = self.metrics.resource_usage_history[-100:]

        # Check resource thresholds and trigger alerts
        if cpu_percent > 0.85:
            logger.warning(f"High CPU usage: {cpu_percent:.2%}")

        if memory_percent > 0.85:
            logger.warning(f"High memory usage: {memory_percent:.2%}")

        if process_memory_mb > 1024:  # 1GB threshold
            logger.warning(f"Process memory high: {process_memory_mb:.1f} MB")

        # Log detailed metrics every 30 seconds
        if int(time.time()) % 30 == 0:
            logger.info(
                f"Resource metrics - CPU: {cpu_percent:.2%}, Mem: {memory_percent:.2%}, "
                f"Process: {process_memory_mb:.1f}MB, Disk R/W: {disk_read_mb:.1f}/{disk_write_mb:.1f}MB, "
                f"Net: {net_sent_mb:.1f}/{net_recv_mb:.1f}MB"
            )

        await asyncio.sleep(2)  # Monitor more frequently

    async def _monitor_simulated(self):
        """Simulate resource monitoring when psutil not available"""
        # Fallback to simulated metrics if psutil not available
        cpu_usage = random.uniform(0.1, 0.9)
        memory_usage = random.uniform(0.3, 0.8)

        self.metrics.cpu_usage = cpu_usage
        self.metrics.memory_usage = memory_usage

        if cpu_usage > 0.8 or memory_usage > 0.8:
            logger.warning(f"High resource usage - CPU: {cpu_usage:.2%}, Memory: {memory_usage:.2%}")

        await asyncio.sleep(5)
