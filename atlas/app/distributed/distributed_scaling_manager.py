"""
AXIOM Distributed Scaling System
Kubernetes Integration, Load Balancing, Fault Tolerance, and Auto-scaling
"""

import asyncio
import threading
import time
import logging
import json
import os
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
import psutil
import socket
import requests
from concurrent.futures import ThreadPoolExecutor
import hashlib
import httpx
import aiofiles

from app.distributed.distributed_manager import get_distributed_manager
from app.distributed.gpu_manager import gpu_manager
from app.config import settings

logger = logging.getLogger(__name__)

class ScalingStrategy(Enum):
    """Scaling strategies"""
    CPU_BASED = "cpu_based"
    MEMORY_BASED = "memory_based"
    REQUEST_BASED = "request_based"
    CUSTOM_METRIC = "custom_metric"

class NodeStatus(Enum):
    """Node status in the cluster"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"

@dataclass
class ClusterNode:
    """Represents a node in the distributed cluster"""
    node_id: str
    hostname: str
    ip_address: str
    port: int
    status: NodeStatus = NodeStatus.HEALTHY
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    active_requests: int = 0
    total_requests: int = 0
    last_heartbeat: float = field(default_factory=time.time)
    capabilities: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoadBalancerConfig:
    """Load balancer configuration"""
    algorithm: str = "round_robin"  # round_robin, least_connections, weighted
    health_check_interval: int = 30
    max_connections_per_node: int = 100
    session_stickiness: bool = False

@dataclass
class AutoScalingConfig:
    """Auto-scaling configuration"""
    enabled: bool = True
    min_nodes: int = 1
    max_nodes: int = 10
    scale_up_threshold: float = 80.0  # CPU/memory percentage
    scale_down_threshold: float = 20.0
    cooldown_period: int = 300  # seconds
    scaling_strategy: ScalingStrategy = ScalingStrategy.CPU_BASED

class KubernetesManager:
    """Kubernetes integration for container orchestration"""

    def __init__(self):
        self.namespace = getattr(settings, "KUBERNETES_NAMESPACE", "default")
        self.service_account_token = self._get_service_account_token()
        self.api_server = self._get_api_server_url()
        self.session = requests.Session()
        # TLS verification (default True). For local/dev clusters without proper CA, set K8S_VERIFY_TLS=0.
        self.verify_tls = str(getattr(settings, "K8S_VERIFY_TLS", "true")).lower() in ("1", "true", "yes")
        if not self.verify_tls:
            logger.warning("⚠️ K8S TLS verification disabled (K8S_VERIFY_TLS=0). Use only in trusted local environments.")

        if self.service_account_token:
            self.session.headers.update({
                'Authorization': f'Bearer {self.service_account_token}'
            })

        logger.info("✅ Kubernetes Manager initialized")

    def _get_service_account_token(self) -> Optional[str]:
        """Get Kubernetes service account token"""
        try:
            with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            logger.info("ℹ️  Not running in Kubernetes environment")
            return None

    def _get_api_server_url(self) -> str:
        """Get Kubernetes API server URL"""
        host = getattr(settings, "KUBERNETES_SERVICE_HOST", None)
        return host or "https://kubernetes.default.svc.cluster.local"

    def get_cluster_nodes(self) -> List[Dict[str, Any]]:
        """Get all nodes in the Kubernetes cluster"""
        if not self.service_account_token:
            return []

        try:
            url = f"{self.api_server}/api/v1/nodes"
            response = self.session.get(url, verify=self.verify_tls)
            response.raise_for_status()

            nodes_data = response.json()
            return nodes_data.get('items', [])

        except Exception as e:
            logger.error(f"❌ Failed to get cluster nodes: {e}")
            return []

    async def scale_deployment(self, deployment_name: str, replicas: int) -> bool:
        """Scale a Kubernetes deployment (async)"""
        if not self.service_account_token:
            logger.warning("⚠️  Kubernetes not available for scaling")
            return False

        try:
            async with httpx.AsyncClient() as client:
                # Get current deployment
                get_url = f"{self.api_server}/apis/apps/v1/namespaces/{self.namespace}/deployments/{deployment_name}"
                response = await client.get(get_url, verify=self.verify_tls)
                response.raise_for_status()

                deployment = response.json()

                # Update replicas
                deployment['spec']['replicas'] = replicas

                # Patch deployment
                patch_url = f"{self.api_server}/apis/apps/v1/namespaces/{self.namespace}/deployments/{deployment_name}"
                headers = {'Content-Type': 'application/merge-patch+json'}
                response = await client.patch(patch_url, json=deployment, headers=headers, verify=self.verify_tls)
                response.raise_for_status()

                logger.info(f"✅ Scaled deployment {deployment_name} to {replicas} replicas")
                return True

        except Exception as e:
            logger.error(f"❌ Failed to scale deployment: {e}")
            return False

    async def get_deployment_status(self, deployment_name: str) -> Optional[Dict[str, Any]]:
        """Get deployment status (async)"""
        if not self.service_account_token:
            return None

        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.api_server}/apis/apps/v1/namespaces/{self.namespace}/deployments/{deployment_name}"
                response = await client.get(url, verify=self.verify_tls)
                response.raise_for_status()

                return response.json()

        except Exception as e:
            logger.error(f"❌ Failed to get deployment status: {e}")
            return None

class LoadBalancer:
    """Intelligent load balancer for distributed system"""

    def __init__(self, config: Optional[LoadBalancerConfig] = None):
        self.config = config or LoadBalancerConfig()
        self.nodes: Dict[str, ClusterNode] = {}
        self.current_index = 0
        self.session_map: Dict[str, str] = {}  # session_id -> node_id
        self.lock = threading.Lock()

        # Start health check thread
        self.health_check_thread = threading.Thread(target=self._health_check_worker, daemon=True)
        self.health_check_thread.start()

        logger.info("✅ Load Balancer initialized")

    def register_node(self, node: ClusterNode):
        """Register a new node in the load balancer"""
        with self.lock:
            self.nodes[node.node_id] = node
            logger.info(f"✅ Registered node: {node.node_id} ({node.hostname}:{node.port})")

    def unregister_node(self, node_id: str):
        """Unregister a node from the load balancer"""
        with self.lock:
            if node_id in self.nodes:
                del self.nodes[node_id]

                # Remove from session map
                self.session_map = {k: v for k, v in self.session_map.items() if v != node_id}

                logger.info(f"✅ Unregistered node: {node_id}")

    def get_next_node(self, session_id: Optional[str] = None) -> Optional[ClusterNode]:
        """Get the next node using the configured algorithm"""
        with self.lock:
            healthy_nodes = [node for node in self.nodes.values()
                           if node.status == NodeStatus.HEALTHY]

            if not healthy_nodes:
                logger.warning("⚠️  No healthy nodes available")
                return None

            # Session stickiness
            if self.config.session_stickiness and session_id:
                if session_id in self.session_map:
                    node_id = self.session_map[session_id]
                    if node_id in self.nodes and self.nodes[node_id].status == NodeStatus.HEALTHY:
                        return self.nodes[node_id]

            # Load balancing algorithm
            if self.config.algorithm == "round_robin":
                node = healthy_nodes[self.current_index % len(healthy_nodes)]
                self.current_index += 1

            elif self.config.algorithm == "least_connections":
                node = min(healthy_nodes, key=lambda n: n.active_requests)

            elif self.config.algorithm == "weighted":
                # Simple weighted algorithm based on available capacity
                node = max(healthy_nodes,
                          key=lambda n: (100 - n.cpu_percent) * (100 - n.memory_percent))

            else:
                node = healthy_nodes[0]

            # Update session map for stickiness
            if self.config.session_stickiness and session_id:
                self.session_map[session_id] = node.node_id

            return node

    def update_node_stats(self, node_id: str, cpu_percent: float,
                         memory_percent: float, active_requests: int):
        """Update node statistics"""
        with self.lock:
            if node_id in self.nodes:
                node = self.nodes[node_id]
                node.cpu_percent = cpu_percent
                node.memory_percent = memory_percent
                node.active_requests = active_requests
                node.last_heartbeat = time.time()

    def _health_check_worker(self):
        """Background worker for health checks"""
        while True:
            try:
                current_time = time.time()

                with self.lock:
                    for node_id, node in list(self.nodes.items()):
                        # Check if node is still alive
                        if current_time - node.last_heartbeat > self.config.health_check_interval * 2:
                            node.status = NodeStatus.OFFLINE
                            logger.warning(f"⚠️  Node {node_id} marked as offline")

                        # Check resource utilization
                        elif node.cpu_percent > 90 or node.memory_percent > 90:
                            node.status = NodeStatus.DEGRADED
                        else:
                            node.status = NodeStatus.HEALTHY

                time.sleep(self.config.health_check_interval)

            except Exception as e:
                logger.error(f"Health check error: {e}")
                time.sleep(5)

    def get_load_stats(self) -> Dict[str, Any]:
        """Get load balancing statistics"""
        with self.lock:
            total_requests = sum(node.total_requests for node in self.nodes.values())
            healthy_nodes = sum(1 for node in self.nodes.values()
                              if node.status == NodeStatus.HEALTHY)

            return {
                "total_nodes": len(self.nodes),
                "healthy_nodes": healthy_nodes,
                "total_requests": total_requests,
                "algorithm": self.config.algorithm,
                "session_stickiness": self.config.session_stickiness,
                "nodes": [
                    {
                        "node_id": node.node_id,
                        "status": node.status.value,
                        "cpu_percent": node.cpu_percent,
                        "memory_percent": node.memory_percent,
                        "active_requests": node.active_requests,
                        "total_requests": node.total_requests
                    }
                    for node in self.nodes.values()
                ]
            }

class AutoScaler:
    """Auto-scaling system for dynamic resource management"""

    def __init__(self, config: Optional[AutoScalingConfig] = None):
        self.config = config or AutoScalingConfig()
        self.kubernetes = KubernetesManager()
        self.last_scale_time = 0
        self.current_replicas = self.config.min_nodes

        # Start auto-scaling thread
        if self.config.enabled:
            self.scaling_thread = threading.Thread(target=self._auto_scaling_worker, daemon=True)
            self.scaling_thread.start()

        logger.info("✅ Auto Scaler initialized")

    async def _auto_scaling_worker(self):
        """Background worker for auto-scaling"""
        while True:
            try:
                if time.time() - self.last_scale_time < self.config.cooldown_period:
                    time.sleep(60)  # Wait for cooldown
                    continue

                # Get current system metrics
                metrics = self._get_system_metrics()

                # Determine scaling action
                action = self._determine_scaling_action(metrics)

                if action != 0:
                    self._execute_scaling_action(action)
                    self.last_scale_time = time.time()

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Auto-scaling error: {e}")
                await asyncio.sleep(60)

    def _get_system_metrics(self) -> Dict[str, float]:
        """Get current system metrics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent

        # Get GPU metrics if available
        gpu_metrics = {}
        if gpu_manager.is_gpu_available():
            _gpu_info = gpu_manager.get_device_info()
            gpu_metrics = {
                "gpu_memory_percent": 0.0,  # Would need more detailed GPU monitoring
                "gpu_utilization": 0.0
            }

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            **gpu_metrics
        }

    def _determine_scaling_action(self, metrics: Dict[str, float]) -> int:
        """Determine if scaling is needed"""
        if self.config.scaling_strategy == ScalingStrategy.CPU_BASED:
            metric_value = metrics.get("cpu_percent", 0)
        elif self.config.scaling_strategy == ScalingStrategy.MEMORY_BASED:
            metric_value = metrics.get("memory_percent", 0)
        else:
            # Average of CPU and memory
            metric_value = (metrics.get("cpu_percent", 0) + metrics.get("memory_percent", 0)) / 2

        # Scale up
        if metric_value > self.config.scale_up_threshold:
            if self.current_replicas < self.config.max_nodes:
                return 1

        # Scale down
        elif metric_value < self.config.scale_down_threshold:
            if self.current_replicas > self.config.min_nodes:
                return -1

        return 0  # No scaling needed

    def _execute_scaling_action(self, action: int):
        """Execute scaling action"""
        if action > 0:
            # Scale up
            new_replicas = min(self.current_replicas + action, self.config.max_nodes)
            if self.kubernetes.scale_deployment("axiom-deployment", new_replicas):
                self.current_replicas = new_replicas
                logger.info(f"📈 Scaled up to {new_replicas} replicas")

        elif action < 0:
            # Scale down
            new_replicas = max(self.current_replicas + action, self.config.min_nodes)
            if self.kubernetes.scale_deployment("axiom-deployment", new_replicas):
                self.current_replicas = new_replicas
                logger.info(f"📉 Scaled down to {new_replicas} replicas")

class FaultToleranceManager:
    """Fault tolerance and recovery system"""

    def __init__(self):
        self.failed_nodes: Dict[str, float] = {}
        self.recovery_attempts: Dict[str, int] = {}
        self.max_recovery_attempts = 3
        self.recovery_cooldown = 300  # 5 minutes

        # Start fault detection thread
        self.fault_thread = threading.Thread(target=self._fault_detection_worker, daemon=True)
        self.fault_thread.start()

        logger.info("✅ Fault Tolerance Manager initialized")

    def report_node_failure(self, node_id: str, failure_reason: str):
        """Report a node failure"""
        current_time = time.time()

        with threading.Lock():
            self.failed_nodes[node_id] = current_time
            attempts = self.recovery_attempts.get(node_id, 0) + 1
            self.recovery_attempts[node_id] = attempts

        logger.warning(f"🚨 Node {node_id} failed: {failure_reason} (attempt {attempts})")

        # Trigger recovery if under max attempts
        if attempts <= self.max_recovery_attempts:
            self._attempt_node_recovery(node_id)

    def _attempt_node_recovery(self, node_id: str):
        """Attempt to recover a failed node"""
        try:
            # This would integrate with Kubernetes or other orchestration
            # For now, just log the attempt
            logger.info(f"🔄 Attempting recovery of node {node_id}")

            # Simulate recovery process
            time.sleep(5)  # Simulate recovery time

            # In a real implementation, this would:
            # 1. Check if node is back online
            # 2. Restart services if needed
            # 3. Re-register with load balancer
            # 4. Update cluster state

            logger.info(f"✅ Recovery attempt completed for node {node_id}")

        except Exception as e:
            logger.error(f"❌ Recovery failed for node {node_id}: {e}")

    def _fault_detection_worker(self):
        """Background worker for fault detection and cleanup"""
        while True:
            try:
                current_time = time.time()

                # Clean up old failure records
                with threading.Lock():
                    to_remove = []
                    for node_id, failure_time in self.failed_nodes.items():
                        if current_time - failure_time > self.recovery_cooldown:
                            to_remove.append(node_id)

                    for node_id in to_remove:
                        del self.failed_nodes[node_id]
                        if node_id in self.recovery_attempts:
                            del self.recovery_attempts[node_id]

                time.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Fault detection error: {e}")
                time.sleep(30)

    def get_fault_stats(self) -> Dict[str, Any]:
        """Get fault tolerance statistics"""
        with threading.Lock():
            return {
                "total_failures": len(self.failed_nodes),
                "active_failures": list(self.failed_nodes.keys()),
                "recovery_attempts": dict(self.recovery_attempts),
                "max_recovery_attempts": self.max_recovery_attempts,
                "recovery_cooldown_seconds": self.recovery_cooldown
            }

class DistributedScalingManager:
    """Main distributed scaling manager coordinating all components"""

    def __init__(self):
        self.kubernetes = KubernetesManager()
        self.load_balancer = LoadBalancer()
        self.auto_scaler = AutoScaler()
        self.fault_tolerance = FaultToleranceManager()
        self.distributed_mgr = get_distributed_manager()

        # Register current node
        self._register_current_node()

        logger.info("✅ Distributed Scaling Manager initialized")

    def _register_current_node(self):
        """Register the current node with the system"""
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        node = ClusterNode(
            node_id=f"node_{hostname}_{int(time.time())}",
            hostname=hostname,
            ip_address=ip_address,
            port=8002,  # Default port
            capabilities={
                "gpu_available": gpu_manager.is_gpu_available(),
                "cpu_count": psutil.cpu_count(logical=True),
                "memory_gb": psutil.virtual_memory().total / (1024**3)
            }
        )

        self.load_balancer.register_node(node)
        logger.info(f"✅ Registered current node: {node.node_id}")

    def get_cluster_status(self) -> Dict[str, Any]:
        """Get comprehensive cluster status"""
        return {
            "kubernetes_available": self.kubernetes.service_account_token is not None,
            "cluster_nodes": len(self.kubernetes.get_cluster_nodes()) if self.kubernetes.service_account_token else 0,
            "load_balancer": self.load_balancer.get_load_stats(),
            "auto_scaling": {
                "enabled": self.auto_scaler.config.enabled,
                "current_replicas": self.auto_scaler.current_replicas,
                "min_nodes": self.auto_scaler.config.min_nodes,
                "max_nodes": self.auto_scaler.config.max_nodes,
                "strategy": self.auto_scaler.config.scaling_strategy.value
            },
            "fault_tolerance": self.fault_tolerance.get_fault_stats(),
            "distributed_computing": self.distributed_mgr.get_system_status()
        }

    def scale_cluster(self, target_replicas: int) -> bool:
        """Manually scale the cluster"""
        if not self.kubernetes.service_account_token:
            logger.warning("⚠️  Kubernetes not available for manual scaling")
            return False

        return self.kubernetes.scale_deployment("axiom-deployment", target_replicas)

    def get_node_for_request(self, session_id: Optional[str] = None) -> Optional[ClusterNode]:
        """Get the best node for handling a request"""
        return self.load_balancer.get_next_node(session_id)

# Global distributed scaling manager instance
distributed_scaling_manager = DistributedScalingManager()

def get_distributed_scaling_manager() -> DistributedScalingManager:
    """Get the global distributed scaling manager instance"""
    return distributed_scaling_manager
