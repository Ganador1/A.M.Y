#!/usr/bin/env python3
"""
AXIOM Horizontal Scalability System
Load balancing, service discovery, and worker management for horizontal scaling
"""

import asyncio
import hashlib
import logging
import os
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import aiofiles

import aiohttp
import psutil

from app.core.config import settings

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    RANDOM = "random"


class InstanceStatus(Enum):
    """Instance health status"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    DRAINING = "draining"


@dataclass
class ServiceInstance:
    """Service instance information"""
    id: str
    host: str
    port: int
    weight: int = 1
    status: InstanceStatus = InstanceStatus.HEALTHY
    connections: int = 0
    last_health_check: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def url(self) -> str:
        """Get instance URL"""
        return f"http://{self.host}:{self.port}"

    @property
    def is_healthy(self) -> bool:
        """Check if instance is healthy"""
        return self.status == InstanceStatus.HEALTHY

    def update_health(self, healthy: bool):
        """Update instance health status"""
        self.status = InstanceStatus.HEALTHY if healthy else InstanceStatus.UNHEALTHY
        self.last_health_check = datetime.now()


@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.ROUND_ROBIN
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5  # seconds
    max_connections_per_instance: int = 100
    session_timeout: int = 300  # seconds
    enable_sticky_sessions: bool = False


class LoadBalancer:
    """Advanced load balancer with multiple strategies"""

    def __init__(self, config: Optional[LoadBalancerConfig] = None):
        self.config = config or LoadBalancerConfig()
        self.instances: List[ServiceInstance] = []
        self.current_index = 0
        self.session_store: Dict[str, str] = {}  # session_id -> instance_id
        self._lock = asyncio.Lock()

    def add_instance(self, instance: ServiceInstance):
        """Add service instance to load balancer"""
        self.instances.append(instance)
        logger.info(f"Added instance {instance.id} at {instance.url}")

    def remove_instance(self, instance_id: str):
        """Remove service instance"""
        self.instances = [i for i in self.instances if i.id != instance_id]
        logger.info(f"Removed instance {instance_id}")

    def get_healthy_instances(self) -> List[ServiceInstance]:
        """Get all healthy instances"""
        return [i for i in self.instances if i.is_healthy]

    async def select_instance(self, client_ip: Optional[str] = None, session_id: Optional[str] = None) -> Optional[ServiceInstance]:
        """Select instance using configured strategy"""
        healthy_instances = self.get_healthy_instances()
        if not healthy_instances:
            return None

        async with self._lock:
            if self.config.enable_sticky_sessions and session_id:
                return self._select_sticky_instance(session_id, healthy_instances)

            strategy_method = getattr(self, f"_strategy_{self.config.strategy.value}")
            return await strategy_method(healthy_instances, client_ip)

    def _select_sticky_instance(self, session_id: str, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """Select instance for sticky session"""
        if session_id in self.session_store:
            instance_id = self.session_store[session_id]
            instance = next((i for i in instances if i.id == instance_id), None)
            if instance:
                return instance

        # Create new sticky session
        instance = random.choice(instances)
        self.session_store[session_id] = instance.id
        return instance

    async def _strategy_round_robin(self, instances: List[ServiceInstance], client_ip: Optional[str] = None) -> ServiceInstance:
        """Round-robin load balancing"""
        instance = instances[self.current_index % len(instances)]
        self.current_index = (self.current_index + 1) % len(instances)
        return instance

    async def _strategy_least_connections(self, instances: List[ServiceInstance], client_ip: Optional[str] = None) -> ServiceInstance:
        """Least connections load balancing"""
        return min(instances, key=lambda i: i.connections)

    async def _strategy_weighted_round_robin(self, instances: List[ServiceInstance], client_ip: Optional[str] = None) -> ServiceInstance:
        """Weighted round-robin load balancing"""
        total_weight = sum(i.weight for i in instances)
        if total_weight == 0:
            return random.choice(instances)

        # Simple weighted selection
        rand = random.randint(1, total_weight)
        current_weight = 0

        for instance in instances:
            current_weight += instance.weight
            if rand <= current_weight:
                return instance

        return instances[-1]  # Fallback

    async def _strategy_ip_hash(self, instances: List[ServiceInstance], client_ip: str) -> ServiceInstance:
        """IP hash load balancing"""
        if not client_ip:
            return random.choice(instances)

        hash_value = int(hashlib.sha256(client_ip.encode()).hexdigest(), 16)
        return instances[hash_value % len(instances)]

    async def _strategy_random(self, instances: List[ServiceInstance], client_ip: Optional[str] = None) -> ServiceInstance:
        """Random load balancing"""
        return random.choice(instances)

    def record_connection(self, instance_id: str, increment: bool = True):
        """Record connection count for instance"""
        for instance in self.instances:
            if instance.id == instance_id:
                instance.connections += 1 if increment else -1
                instance.connections = max(0, instance.connections)
                break

    def get_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        healthy_instances = self.get_healthy_instances()
        total_connections = sum(i.connections for i in self.instances)

        return {
            "total_instances": len(self.instances),
            "healthy_instances": len(healthy_instances),
            "total_connections": total_connections,
            "strategy": self.config.strategy.value,
            "sticky_sessions_enabled": self.config.enable_sticky_sessions,
            "active_sessions": len(self.session_store),
            "instances": [
                {
                    "id": i.id,
                    "url": i.url,
                    "status": i.status.value,
                    "connections": i.connections,
                    "weight": i.weight
                }
                for i in self.instances
            ]
        }


class HealthChecker:
    """Service health checker"""

    def __init__(self, health_check_url: str = "/health", timeout: int = 5):
        self.health_check_url = health_check_url
        self.timeout = timeout
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def check_instance(self, instance: ServiceInstance) -> bool:
        """Check health of service instance"""
        if not self.session:
            async with aiohttp.ClientSession() as session:
                return await self._check_health(session, instance)

        return await self._check_health(self.session, instance)

    async def _check_health(self, session: aiohttp.ClientSession, instance: ServiceInstance) -> bool:
        """Perform health check"""
        try:
            url = f"{instance.url}{self.health_check_url}"
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with session.get(url, timeout=timeout) as response:
                return response.status == 200
        except Exception as e:
            logger.warning(f"Health check failed for {instance.id}: {e}")
            return False


class ServiceDiscovery:
    """Service discovery for dynamic instance registration"""

    def __init__(self):
        self.instances: Dict[str, ServiceInstance] = {}
        self._lock = asyncio.Lock()

    async def register_instance(self, instance: ServiceInstance):
        """Register service instance"""
        async with self._lock:
            self.instances[instance.id] = instance
            logger.info(f"Registered instance {instance.id}")

    async def deregister_instance(self, instance_id: str):
        """Deregister service instance"""
        async with self._lock:
            if instance_id in self.instances:
                del self.instances[instance_id]
                logger.info(f"Deregistered instance {instance_id}")

    async def get_instances(self, service_name: Optional[str] = None) -> List[ServiceInstance]:
        """Get all registered instances"""
        async with self._lock:
            return list(self.instances.values())

    async def get_healthy_instances(self, service_name: Optional[str] = None) -> List[ServiceInstance]:
        """Get healthy instances"""
        instances = await self.get_instances(service_name)
        return [i for i in instances if i.is_healthy]


class WorkerManager:
    """Worker process manager for horizontal scaling"""

    def __init__(self, worker_module: str = "main", worker_count: int = 4):
        self.worker_module = worker_module
        self.worker_count = worker_count
        self.workers: Dict[int, psutil.Process] = {}
        self._lock = asyncio.Lock()

    async def start_workers(self):
        """Start worker processes"""
        async with self._lock:
            for i in range(self.worker_count):
                if i not in self.workers:
                    await self._start_worker(i)

    async def _start_worker(self, worker_id: int):
        """Start a single worker process"""
        try:
            import subprocess
            import sys

            # Start worker process
            cmd = [sys.executable, "-m", self.worker_module, "--worker", str(worker_id)]
            process = subprocess.Paiofiles.aiofiles.open(cmd, env=dict(os.environ, WORKER_ID=str(worker_id)))

            # Store process info
            ps_process = psutil.Process(process.pid)
            self.workers[worker_id] = ps_process

            logger.info(f"Started worker {worker_id} (PID: {process.pid})")

        except Exception as e:
            logger.error(f"Failed to start worker {worker_id}: {e}")

    async def stop_workers(self):
        """Stop all worker processes"""
        async with self._lock:
            for worker_id, process in self.workers.items():
                try:
                    process.terminate()
                    process.wait(timeout=5)
                    logger.info(f"Stopped worker {worker_id}")
                except Exception as e:
                    logger.error(f"Failed to stop worker {worker_id}: {e}")
                    try:
                        process.kill()
                    except Exception:
                        pass

            self.workers.clear()

    def get_worker_stats(self) -> Dict[str, Any]:
        """Get worker statistics"""
        stats = {
            "total_workers": self.worker_count,
            "active_workers": len(self.workers),
            "workers": []
        }

        for worker_id, process in self.workers.items():
            try:
                worker_info = {
                    "id": worker_id,
                    "pid": process.pid,
                    "status": process.status(),
                    "cpu_percent": process.cpu_percent(),
                    "memory_percent": process.memory_percent(),
                    "threads": process.num_threads()
                }
                stats["workers"].append(worker_info)
            except Exception as e:
                logger.warning(f"Failed to get stats for worker {worker_id}: {e}")

        return stats


class ScalabilityManager:
    """Main scalability manager coordinating all components"""

    def __init__(self):
        self.load_balancer = LoadBalancer()
        self.service_discovery = ServiceDiscovery()
        self.worker_manager = WorkerManager()
        self.health_checker = HealthChecker()
        self._health_check_task = None
        self._running = False

    async def start(self):
        """Start scalability system"""
        if self._running:
            return

        self._running = True

        # Start worker processes
        await self.worker_manager.start_workers()

        # Register local instance
        local_instance = ServiceInstance(
            id=f"instance_{os.getpid()}",
            host="localhost",
            port=settings.port,
            weight=1
        )
        await self.service_discovery.register_instance(local_instance)
        self.load_balancer.add_instance(local_instance)

        # Start health checking
        self._health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info("Scalability system started")

    async def stop(self):
        """Stop scalability system"""
        if not self._running:
            return

        self._running = False

        # Stop health checking
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Stop workers
        await self.worker_manager.stop_workers()

        logger.info("Scalability system stopped")

    async def _health_check_loop(self):
        """Continuous health checking loop"""
        while self._running:
            try:
                instances = await self.service_discovery.get_instances()
                async with self.health_checker:
                    for instance in instances:
                        is_healthy = await self.health_checker.check_instance(instance)
                        instance.update_health(is_healthy)

                await asyncio.sleep(self.load_balancer.config.health_check_interval)

            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)

    async def get_scalability_status(self) -> Dict[str, Any]:
        """Get comprehensive scalability status"""
        instances = await self.service_discovery.get_instances()
        healthy_instances = [i for i in instances if i.is_healthy]

        return {
            "system_status": "running" if self._running else "stopped",
            "load_balancer": self.load_balancer.get_stats(),
            "service_discovery": {
                "total_instances": len(instances),
                "healthy_instances": len(healthy_instances)
            },
            "worker_manager": self.worker_manager.get_worker_stats(),
            "health_checker": {
                "status": "active" if self._running else "inactive",
                "check_interval": self.load_balancer.config.health_check_interval
            }
        }


# Global scalability instance
scalability_manager = ScalabilityManager()
