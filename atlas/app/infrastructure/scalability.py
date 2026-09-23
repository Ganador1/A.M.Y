#!/usr/bin/env python3
"""
Compatibility shim for AXIOM Horizontal Scalability System.
Re-exports public classes from app.distributed.scalability so existing imports
like `from app.scalability import LoadBalancer` continue to work.
"""

from .distributed.scalability import (
    LoadBalancer,
    ServiceInstance,
    LoadBalancerConfig,
    LoadBalancingStrategy,
    HealthChecker,
    ServiceDiscovery,
    WorkerManager,
    ScalabilityManager,
    InstanceStatus,
)

__all__ = [
    "LoadBalancer",
    "ServiceInstance",
    "LoadBalancerConfig",
    "LoadBalancingStrategy",
    "HealthChecker",
    "ServiceDiscovery",
    "WorkerManager",
    "ScalabilityManager",
    "InstanceStatus",
]