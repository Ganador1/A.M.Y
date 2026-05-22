#!/usr/bin/env python3
"""
Unit tests for AXIOM Horizontal Scalability System
"""

import pytest

from app.scalability import (
    LoadBalancer, ServiceInstance, LoadBalancerConfig,
    LoadBalancingStrategy, HealthChecker, ServiceDiscovery,
    WorkerManager, ScalabilityManager, InstanceStatus
)


class TestLoadBalancer:
    """Test load balancer functionality"""

    def setup_method(self):
        """Setup test instances"""
        self.config = LoadBalancerConfig(strategy=LoadBalancingStrategy.ROUND_ROBIN)
        self.load_balancer = LoadBalancer(self.config)

        # Create test instances
        self.instance1 = ServiceInstance("inst1", "localhost", 8001, 1, InstanceStatus.HEALTHY)
        self.instance2 = ServiceInstance("inst2", "localhost", 8002, 1, InstanceStatus.HEALTHY)
        self.instance3 = ServiceInstance("inst3", "localhost", 8003, 1, InstanceStatus.UNHEALTHY)

        self.load_balancer.add_instance(self.instance1)
        self.load_balancer.add_instance(self.instance2)
        self.load_balancer.add_instance(self.instance3)

    def test_get_healthy_instances(self):
        """Test getting healthy instances"""
        healthy = self.load_balancer.get_healthy_instances()
        assert len(healthy) == 2
        assert self.instance1 in healthy
        assert self.instance2 in healthy
        assert self.instance3 not in healthy

    @pytest.mark.asyncio
    async def test_round_robin_strategy(self):
        """Test round-robin load balancing"""
        # First call
        instance1 = await self.load_balancer.select_instance()
        assert instance1 is not None
        assert instance1.id == "inst1"

        # Second call
        instance2 = await self.load_balancer.select_instance()
        assert instance2 is not None
        assert instance2.id == "inst2"

        # Third call (should wrap around)
        instance3 = await self.load_balancer.select_instance()
        assert instance3 is not None
        assert instance3.id == "inst1"  # Wraps to first healthy instance

    @pytest.mark.asyncio
    async def test_least_connections_strategy(self):
        """Test least connections load balancing"""
        self.load_balancer.config.strategy = LoadBalancingStrategy.LEAST_CONNECTIONS

        # Set different connection counts
        self.instance1.connections = 5
        self.instance2.connections = 3

        instance = await self.load_balancer.select_instance()
        assert instance is not None
        assert instance.id == "inst2"  # Should select instance with fewer connections

    @pytest.mark.asyncio
    async def test_weighted_round_robin_strategy(self):
        """Test weighted round-robin load balancing"""
        self.load_balancer.config.strategy = LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN

        # Set different weights
        self.instance1.weight = 3
        self.instance2.weight = 1

        # Should select higher weight instance more often
        selections = {}
        for _ in range(10):
            instance = await self.load_balancer.select_instance()
            assert instance is not None
            selections[instance.id] = selections.get(instance.id, 0) + 1

        assert selections["inst1"] > selections["inst2"]  # inst1 should be selected more

    @pytest.mark.asyncio
    async def test_ip_hash_strategy(self):
        """Test IP hash load balancing"""
        self.load_balancer.config.strategy = LoadBalancingStrategy.IP_HASH

        # Same IP should always get same instance
        instance1 = await self.load_balancer.select_instance("192.168.1.1")
        instance2 = await self.load_balancer.select_instance("192.168.1.1")
        assert instance1 is not None
        assert instance2 is not None
        assert instance1.id == instance2.id

    @pytest.mark.asyncio
    async def test_random_strategy(self):
        """Test random load balancing"""
        self.load_balancer.config.strategy = LoadBalancingStrategy.RANDOM

        # Should get different instances over multiple calls
        instances = set()
        for _ in range(20):
            instance = await self.load_balancer.select_instance()
            assert instance is not None
            instances.add(instance.id)

        assert len(instances) > 1  # Should get multiple different instances

    def test_record_connection(self):
        """Test connection recording"""
        self.load_balancer.record_connection("inst1", increment=True)
        assert self.instance1.connections == 1

        self.load_balancer.record_connection("inst1", increment=False)
        assert self.instance1.connections == 0

    def test_get_stats(self):
        """Test getting load balancer statistics"""
        stats = self.load_balancer.get_stats()

        assert stats["total_instances"] == 3
        assert stats["healthy_instances"] == 2
        assert stats["strategy"] == "round_robin"
        assert len(stats["instances"]) == 3


class TestServiceDiscovery:
    """Test service discovery functionality"""

    def setup_method(self):
        """Setup test service discovery"""
        self.discovery = ServiceDiscovery()
        self.instance = ServiceInstance("test_inst", "localhost", 8001)

    @pytest.mark.asyncio
    async def test_register_deregister_instance(self):
        """Test instance registration and deregistration"""
        # Register instance
        await self.discovery.register_instance(self.instance)
        instances = await self.discovery.get_instances()
        assert len(instances) == 1
        assert instances[0].id == "test_inst"

        # Deregister instance
        await self.discovery.deregister_instance("test_inst")
        instances = await self.discovery.get_instances()
        assert len(instances) == 0

    @pytest.mark.asyncio
    async def test_get_healthy_instances(self):
        """Test getting healthy instances"""
        healthy_instance = ServiceInstance("healthy", "localhost", 8001, status=InstanceStatus.HEALTHY)
        unhealthy_instance = ServiceInstance("unhealthy", "localhost", 8002, status=InstanceStatus.UNHEALTHY)

        await self.discovery.register_instance(healthy_instance)
        await self.discovery.register_instance(unhealthy_instance)

        healthy = await self.discovery.get_healthy_instances()
        assert len(healthy) == 1
        assert healthy[0].id == "healthy"


class TestWorkerManager:
    """Test worker manager functionality"""

    def setup_method(self):
        """Setup test worker manager"""
        self.worker_manager = WorkerManager(worker_count=2)

    def test_get_worker_stats(self):
        """Test getting worker statistics"""
        stats = self.worker_manager.get_worker_stats()

        assert stats["total_workers"] == 2
        assert stats["active_workers"] == 0  # No workers started yet
        assert len(stats["workers"]) == 0


class TestHealthChecker:
    """Test health checker functionality"""

    def setup_method(self):
        """Setup test health checker"""
        self.health_checker = HealthChecker()
        self.instance = ServiceInstance("test", "localhost", 8001)

    @pytest.mark.asyncio
    async def test_health_check_failure(self):
        """Test health check failure for non-existent service"""
        async with self.health_checker:
            is_healthy = await self.health_checker.check_instance(self.instance)
            assert not is_healthy


class TestScalabilityManager:
    """Test scalability manager functionality"""

    def setup_method(self):
        """Setup test scalability manager"""
        self.manager = ScalabilityManager()

    @pytest.mark.asyncio
    async def test_get_scalability_status(self):
        """Test getting scalability status"""
        status = await self.manager.get_scalability_status()

        assert "system_status" in status
        assert "load_balancer" in status
        assert "service_discovery" in status
        assert "worker_manager" in status
        assert "health_checker" in status


if __name__ == "__main__":
    pytest.main([__file__])
