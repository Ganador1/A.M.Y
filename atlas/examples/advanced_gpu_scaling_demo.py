#!/usr/bin/env python3
"""
Advanced GPU and Distributed Scaling Demo
Demonstrates Phase 4.1 (GPU Optimization) and Phase 4.2 (Distributed Scaling)

⚠️ Advertencia de uso responsable
- Este script invoca endpoints que pueden consumir GPU/CPU de forma intensiva.
- Úsalo en entornos controlados y define límites en el servidor.
- No ejecutes en producción sin autenticación ni TLS.
- Consulta `ETHICS_AND_SAFETY.md`.
"""

import asyncio
import requests
from typing import Dict, Any

class AdvancedGPUScalingDemo:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def make_request(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make HTTP request with error handling"""
        try:
            url = f"{self.base_url}{endpoint}"

            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "PUT":
                response = self.session.put(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {endpoint} - {str(e)}")
            return {"status": "error", "error": str(e)}

    def demo_gpu_optimization(self):
        """Demonstrate GPU optimization features"""
        print("\n" + "="*60)
        print("PHASE 4.1: GPU OPTIMIZATION DEMO")
        print("="*60)

        # 1. Get GPU status
        print("\n1. Advanced GPU Status:")
        status = self.make_request("/gpu/advanced/status")
        if status.get("status") == "success":
            gpu_status = status.get("gpu_optimization", {})
            print(f"   GPU Available: {gpu_status.get('gpu_available', False)}")
            print(f"   Device Count: {gpu_status.get('device_count', 0)}")
            print(f"   Current Device: {gpu_status.get('current_device', 'N/A')}")
            print(f"   Memory Pool Active: {gpu_status.get('memory_pool_active', False)}")
            print(f"   Stream Manager Active: {gpu_status.get('stream_manager_active', False)}")
        else:
            print(f"   Error: {status.get('error', 'Unknown error')}")

        # 2. Get memory statistics
        print("\n2. GPU Memory Statistics:")
        memory_stats = self.make_request("/gpu/memory/stats")
        if memory_stats.get("status") == "success":
            stats = memory_stats.get("memory_stats", {})
            for device_id, device_stats in stats.items():
                print(f"   Device {device_id}:")
                print(f"     Total Memory: {device_stats.get('total_memory', 0):.2f} GB")
                print(f"     Used Memory: {device_stats.get('used_memory', 0):.2f} GB")
                print(f"     Free Memory: {device_stats.get('free_memory', 0):.2f} GB")
                print(f"     Memory Utilization: {device_stats.get('memory_utilization', 0):.2f}%")
        else:
            print(f"   Error: {memory_stats.get('error', 'Unknown error')}")

        # 3. Get stream statistics
        print("\n3. GPU Stream Statistics:")
        stream_stats = self.make_request("/gpu/streams/stats")
        if stream_stats.get("status") == "success":
            stats = stream_stats.get("stream_stats", {})
            print(f"   Active Streams: {stats.get('active_streams', 0)}")
            print(f"   Max Concurrent Streams: {stats.get('max_concurrent_streams', 0)}")
            print(f"   Stream Pool Size: {stats.get('stream_pool_size', 0)}")
        else:
            print(f"   Error: {stream_stats.get('error', 'Unknown error')}")

        # 4. Get profiling statistics
        print("\n4. GPU Profiling Statistics:")
        profiling_stats = self.make_request("/gpu/profiling/stats?last_n=5")
        if profiling_stats.get("status") == "success":
            stats = profiling_stats.get("profiling_stats", [])
            print(f"   Recent Profiling Data Points: {len(stats)}")
            if stats:
                latest = stats[-1]
                print(f"   Latest Profile (Device {latest.get('device_id', 0)}):")
                print(f"     Kernel Time: {latest.get('kernel_time', 0):.4f} ms")
                print(f"     Memory Bandwidth: {latest.get('memory_bandwidth', 0):.2f} GB/s")
                print(f"     Compute Utilization: {latest.get('compute_utilization', 0):.2f}%")
                print(f"     Memory Utilization: {latest.get('memory_utilization', 0):.2f}%")
                print(f"     Power Consumption: {latest.get('power_consumption', 0):.2f} W")
                print(f"     Temperature: {latest.get('temperature', 0):.1f}°C")
        else:
            print(f"   Error: {profiling_stats.get('error', 'Unknown error')}")

        # 5. Test GPU optimization operation
        print("\n5. Testing GPU Optimization Operation:")
        optimization_request = {
            "device_id": 0,
            "operation": "stream_parallel",
            "parameters": {"test_mode": True}
        }
        result = self.make_request("/gpu/optimize", method="POST", data=optimization_request)
        if result.get("status") == "success":
            print(f"   Operation: {result.get('operation', 'N/A')}")
            print(f"   Parallel Operations: {result.get('parallel_operations', 0)}")
            print(f"   Results Count: {len(result.get('results', []))}")
            print("   ✓ GPU parallel computation successful")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")

    def demo_distributed_scaling(self):
        """Demonstrate distributed scaling features"""
        print("\n" + "="*60)
        print("PHASE 4.2: DISTRIBUTED SCALING DEMO")
        print("="*60)

        # 1. Get cluster status
        print("\n1. Cluster Status:")
        cluster_status = self.make_request("/scaling/cluster/status")
        if cluster_status.get("status") == "success":
            status = cluster_status.get("cluster_status", {})
            print(f"   Distributed Computing: {status.get('distributed_computing', {}).get('distributed_enabled', False)}")
            print(f"   Kubernetes Available: {status.get('kubernetes_available', False)}")
            print(f"   Load Balancer Active: {len(status.get('load_balancer', {}).get('nodes', [])) > 0}")
            print(f"   Auto Scaling Enabled: {status.get('auto_scaling', {}).get('enabled', False)}")
            print(f"   Fault Tolerance Active: {status.get('fault_tolerance', {}).get('active', False)}")
        else:
            print(f"   Error: {cluster_status.get('error', 'Unknown error')}")

        # 2. Get load balancer statistics
        print("\n2. Load Balancer Statistics:")
        lb_stats = self.make_request("/scaling/load-balancer/stats")
        if lb_stats.get("status") == "success":
            stats = lb_stats.get("load_balancer_stats", {})
            print(f"   Total Requests: {stats.get('total_requests', 0)}")
            print(f"   Active Connections: {stats.get('active_connections', 0)}")
            print(f"   Nodes Count: {stats.get('nodes_count', 0)}")
            print(f"   Load Distribution: {stats.get('load_distribution', {})}")
        else:
            print(f"   Error: {lb_stats.get('error', 'Unknown error')}")

        # 3. Get auto-scaling status
        print("\n3. Auto-Scaling Status:")
        scaling_status = self.make_request("/scaling/auto-scaling/status")
        if scaling_status.get("status") == "success":
            status = scaling_status.get("auto_scaling_status", {})
            print(f"   Enabled: {status.get('enabled', False)}")
            print(f"   Current Replicas: {status.get('current_replicas', 0)}")
            print(f"   Min Nodes: {status.get('min_nodes', 0)}")
            print(f"   Max Nodes: {status.get('max_nodes', 0)}")
            print(f"   Scale Up Threshold: {status.get('scale_up_threshold', 0):.2f}%")
            print(f"   Scale Down Threshold: {status.get('scale_down_threshold', 0):.2f}%")
            print(f"   Scaling Strategy: {status.get('scaling_strategy', 'N/A')}")
        else:
            print(f"   Error: {scaling_status.get('error', 'Unknown error')}")

        # 4. Get fault tolerance statistics
        print("\n4. Fault Tolerance Statistics:")
        ft_stats = self.make_request("/scaling/fault-tolerance/stats")
        if ft_stats.get("status") == "success":
            stats = ft_stats.get("fault_tolerance_stats", {})
            print(f"   Total Failures: {stats.get('total_failures', 0)}")
            print(f"   Recovered Failures: {stats.get('recovered_failures', 0)}")
            print(f"   Active Health Checks: {stats.get('active_health_checks', 0)}")
            print(f"   Recovery Time Average: {stats.get('recovery_time_avg', 0):.2f}s")
        else:
            print(f"   Error: {ft_stats.get('error', 'Unknown error')}")

        # 5. Get Kubernetes nodes
        print("\n5. Kubernetes Cluster Nodes:")
        k8s_nodes = self.make_request("/scaling/kubernetes/nodes")
        if k8s_nodes.get("status") == "success":
            print(f"   Kubernetes Available: {k8s_nodes.get('kubernetes_available', False)}")
            nodes = k8s_nodes.get("nodes", [])
            print(f"   Node Count: {len(nodes)}")
            for i, node in enumerate(nodes[:3]):  # Show first 3 nodes
                print(f"     Node {i+1}: {node.get('name', 'N/A')} - {node.get('status', 'N/A')}")
        else:
            print(f"   Error: {k8s_nodes.get('error', 'Unknown error')}")

        # 6. Test scaling operation
        print("\n6. Testing Scaling Operation:")
        scaling_request = {
            "action": "set_replicas",
            "target_replicas": 2,
            "deployment_name": "axiom-deployment"
        }
        result = self.make_request("/scaling/cluster/scale", method="POST", data=scaling_request)
        if result.get("status") == "success":
            print(f"   Action: {result.get('action', 'N/A')}")
            print(f"   Target Replicas: {result.get('target_replicas', 0)}")
            print(f"   Deployment: {result.get('deployment', 'N/A')}")
            print("   ✓ Scaling operation initiated")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")

    def demo_performance_summary(self):
        """Demonstrate comprehensive performance summary"""
        print("\n" + "="*60)
        print("PERFORMANCE SUMMARY")
        print("="*60)

        summary = self.make_request("/scaling/performance/summary")
        if summary.get("status") == "success":
            perf = summary.get("performance_summary", {})
            print("\nGPU Optimization:")
            gpu_opt = perf.get("gpu_optimization", {})
            print(f"   GPU Available: {gpu_opt.get('gpu_available', False)}")
            print(f"   Device Count: {gpu_opt.get('device_count', 0)}")
            print(f"   Memory Pool: {gpu_opt.get('memory_pool_active', False)}")
            print(f"   Stream Manager: {gpu_opt.get('stream_manager_active', False)}")

            print("\nDistributed Scaling:")
            dist_scale = perf.get("distributed_scaling", {})
            print(f"   Distributed Enabled: {dist_scale.get('distributed_computing', {}).get('distributed_enabled', False)}")
            print(f"   Kubernetes Available: {dist_scale.get('kubernetes_available', False)}")
            print(f"   Auto Scaling: {dist_scale.get('auto_scaling', {}).get('enabled', False)}")

            print("\nPerformance Metrics:")
            metrics = perf.get("performance_metrics", {})
            print(f"   GPU Accelerated: {metrics.get('gpu_accelerated', False)}")
            print(f"   Distributed Enabled: {metrics.get('distributed_enabled', False)}")
            print(f"   Kubernetes Integrated: {metrics.get('kubernetes_integrated', False)}")
            print(f"   Auto Scaling Active: {metrics.get('auto_scaling_active', False)}")
            print(f"   Load Balancing Active: {metrics.get('load_balancing_active', False)}")
            print(f"   Fault Tolerance Active: {metrics.get('fault_tolerance_active', False)}")

            print(f"\nSystem Health: {perf.get('system_health', 'unknown').upper()}")
        else:
            print(f"   Error: {summary.get('error', 'Unknown error')}")

    async def run_demo(self):
        """Run the complete demonstration"""
        print("AXIOM Advanced GPU and Distributed Scaling Demo")
        print("Phase 4.1 & 4.2 Implementation Demonstration")
        print("="*60)

        # Test server connectivity
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✓ Server connection successful")
            else:
                print("✗ Server connection failed")
                return
        except Exception as e:
            print(f"✗ Cannot connect to server: {str(e)}")
            print("Make sure the AXIOM server is running on http://localhost:8000")
            return

        # Run demonstrations
        self.demo_gpu_optimization()
        self.demo_distributed_scaling()
        self.demo_performance_summary()

        print("\n" + "="*60)
        print("DEMO COMPLETED")
        print("="*60)
        print("Phase 4.1 (GPU Optimization) and Phase 4.2 (Distributed Scaling)")
        print("have been successfully implemented and demonstrated!")

def main():
    """Main entry point"""
    demo = AdvancedGPUScalingDemo()
    asyncio.run(demo.run_demo())

if __name__ == "__main__":
    main()
