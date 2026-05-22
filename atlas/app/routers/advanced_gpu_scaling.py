"""
Advanced GPU and Distributed Scaling Router

Este módulo proporciona endpoints para optimización de GPU, computación distribuida y gestión
de auto-escalado. Incluye optimización de memoria GPU, paralelización de streams, integración
con Kubernetes para escalado de clusters, algoritmos de balanceo de carga y monitoreo de
tolerancia a fallos para sistemas de alto rendimiento.

Capacidades principales:
- Optimización de memoria GPU y paralelización de streams
- Perfilado de GPU en tiempo real y monitoreo de rendimiento
- Escalado de clusters distribuidos con integración Kubernetes
- Algoritmos de balanceo de carga y gestión de sesiones
- Monitoreo de tolerancia a fallos y alta disponibilidad
- Auto-escalado basado en métricas de utilización de recursos
- Orquestación de computación multi-GPU
- Analytics de rendimiento y monitoreo de salud del sistema

Endpoints disponibles:
- GET /gpu/advanced/status: Estado avanzado del sistema GPU
- GET /gpu/memory/stats: Estadísticas detalladas de memoria GPU
- GET /gpu/streams/stats: Estadísticas de streams GPU
- GET /gpu/profiling/stats: Estadísticas de perfilado GPU
- POST /gpu/optimize: Ejecutar operación de optimización GPU
- GET /scaling/cluster/status: Estado del cluster distribuido
- GET /scaling/load-balancer/stats: Estadísticas del balanceador de carga
- POST /scaling/cluster/scale: Escalar el cluster manualmente
- PUT /scaling/load-balancer/config: Actualizar configuración del balanceador
- GET /scaling/fault-tolerance/stats: Estadísticas de tolerancia a fallos
- GET /scaling/kubernetes/nodes: Nodos del cluster Kubernetes
- GET /scaling/auto-scaling/status: Estado del auto-escalado
- GET /scaling/performance/summary: Resumen comprehensivo de rendimiento

Dependencias:
- get_advanced_gpu_optimizer(): Optimizador avanzado de GPU
- get_distributed_scaling_manager(): Gestor de escalado distribuido
- GPUOptimizationRequest: Solicitud de optimización GPU
- ScalingRequest: Solicitud de escalado
- LoadBalancingRequest: Solicitud de configuración de balanceo de carga

Uso típico:
    from app.routers.advanced_gpu_scaling import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import time

from app.advanced_ops.advanced_gpu_optimizer import get_advanced_gpu_optimizer
from app.distributed.distributed_scaling_manager import get_distributed_scaling_manager
from app.exceptions.domain.mathematics import MathematicsError

router = APIRouter()
advanced_gpu_scaling_router = router

# Get instances
gpu_optimizer = get_advanced_gpu_optimizer()
scaling_manager = get_distributed_scaling_manager()

# Pydantic models for API
class GPUOptimizationRequest(BaseModel):
    device_id: int = Field(0, description="GPU device ID")
    operation: str = Field(..., description="Operation to optimize: memory_optimization, stream_parallel")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Additional parameters")

class ScalingRequest(BaseModel):
    action: str = Field(..., description="Scaling action: scale_up, scale_down, set_replicas")
    target_replicas: Optional[int] = Field(None, description="Target number of replicas")
    deployment_name: str = Field("axiom-deployment", description="Kubernetes deployment name")

class LoadBalancingRequest(BaseModel):
    algorithm: str = Field("round_robin", description="Load balancing algorithm")
    session_stickiness: bool = Field(False, description="Enable session stickiness")

@router.get("/gpu/advanced/status")
async def get_advanced_gpu_status():
    """Get advanced GPU optimization system status"""
    try:
        status = gpu_optimizer.get_system_status()

        return {
            "status": "success",
            "gpu_optimization": status,
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"GPU status error: {str(e)}")

@router.get("/gpu/memory/stats")
async def get_gpu_memory_stats():
    """Get detailed GPU memory statistics"""
    try:
        memory_stats = gpu_optimizer.get_memory_stats()

        return {
            "status": "success",
            "memory_stats": memory_stats,
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Memory stats error: {str(e)}")

@router.get("/gpu/streams/stats")
async def get_gpu_stream_stats():
    """Get GPU stream statistics"""
    try:
        stream_stats = gpu_optimizer.get_stream_stats()

        return {
            "status": "success",
            "stream_stats": stream_stats,
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Stream stats error: {str(e)}")

@router.get("/gpu/profiling/stats")
async def get_gpu_profiling_stats(device_id: Optional[int] = None, last_n: int = 100):
    """Get GPU profiling statistics"""
    try:
        profiling_data = gpu_optimizer.get_profiling_stats(device_id, last_n)

        # Convert to serializable format
        profiling_stats = [
            {
                "device_id": stat.device_id,
                "kernel_time": stat.kernel_time,
                "memory_bandwidth": stat.memory_bandwidth,
                "compute_utilization": stat.compute_utilization,
                "memory_utilization": stat.memory_utilization,
                "power_consumption": stat.power_consumption,
                "temperature": stat.temperature,
                "timestamp": stat.timestamp
            }
            for stat in profiling_data
        ]

        return {
            "status": "success",
            "profiling_stats": profiling_stats,
            "count": len(profiling_stats),
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Profiling stats error: {str(e)}")

@router.post("/gpu/optimize")
async def optimize_gpu_operation(request: GPUOptimizationRequest, background_tasks: BackgroundTasks):
    """Execute GPU optimization operation"""
    try:
        if request.operation == "memory_optimization":
            # Run memory optimization in background
            background_tasks.add_task(gpu_optimizer.optimize_memory_usage)

            return {
                "status": "success",
                "message": "Memory optimization started in background",
                "operation": request.operation,
                "timestamp": time.time()
            }

        elif request.operation == "stream_parallel":
            # Test parallel stream execution
            def dummy_operation():
                import torch
                if torch.cuda.is_available():
                    x = torch.randn(1000, 1000, device=f'cuda:{request.device_id}')
                    y = torch.randn(1000, 1000, device=f'cuda:{request.device_id}')
                    return torch.mm(x, y).sum().item()
                return 0.0

            operations = [dummy_operation for _ in range(4)]
            results = gpu_optimizer.parallel_gpu_computation(operations, request.device_id)

            return {
                "status": "success",
                "operation": request.operation,
                "results": results,
                "parallel_operations": len(operations),
                "timestamp": time.time()
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {request.operation}")

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"GPU optimization error: {str(e)}")

@router.get("/scaling/cluster/status")
async def get_cluster_status():
    """Get distributed cluster status"""
    try:
        status = scaling_manager.get_cluster_status()

        return {
            "status": "success",
            "cluster_status": status,
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Cluster status error: {str(e)}")

@router.get("/scaling/load-balancer/stats")
async def get_load_balancer_stats():
    """Get load balancer statistics"""
    try:
        stats = scaling_manager.load_balancer.get_load_stats()

        return {
            "status": "success",
            "load_balancer_stats": stats,
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Load balancer stats error: {str(e)}")

@router.post("/scaling/cluster/scale")
async def scale_cluster(request: ScalingRequest, background_tasks: BackgroundTasks):
    """Scale the cluster manually"""
    try:
        if request.action == "set_replicas":
            if request.target_replicas is None:
                raise HTTPException(status_code=400, detail="target_replicas required for set_replicas action")

            success = scaling_manager.scale_cluster(request.target_replicas)

            return {
                "status": "success" if success else "failed",
                "action": request.action,
                "target_replicas": request.target_replicas,
                "deployment": request.deployment_name,
                "timestamp": time.time()
            }

        elif request.action in ["scale_up", "scale_down"]:
            # Get current status and adjust
            current_status = scaling_manager.get_cluster_status()
            current_replicas = current_status.get("auto_scaling", {}).get("current_replicas", 1)

            if request.action == "scale_up":
                target_replicas = min(current_replicas + 1, scaling_manager.auto_scaler.config.max_nodes)
            else:
                target_replicas = max(current_replicas - 1, scaling_manager.auto_scaler.config.min_nodes)

            success = scaling_manager.scale_cluster(target_replicas)

            return {
                "status": "success" if success else "failed",
                "action": request.action,
                "current_replicas": current_replicas,
                "target_replicas": target_replicas,
                "deployment": request.deployment_name,
                "timestamp": time.time()
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported scaling action: {request.action}")

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Scaling error: {str(e)}")

@router.put("/scaling/load-balancer/config")
async def update_load_balancer_config(request: LoadBalancingRequest):
    """Update load balancer configuration"""
    try:
        # Update configuration
        scaling_manager.load_balancer.config.algorithm = request.algorithm
        scaling_manager.load_balancer.config.session_stickiness = request.session_stickiness

        return {
            "status": "success",
            "message": "Load balancer configuration updated",
            "new_config": {
                "algorithm": request.algorithm,
                "session_stickiness": request.session_stickiness
            },
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Load balancer config error: {str(e)}")

@router.get("/scaling/fault-tolerance/stats")
async def get_fault_tolerance_stats():
    """Get fault tolerance statistics"""
    try:
        stats = scaling_manager.fault_tolerance.get_fault_stats()

        return {
            "status": "success",
            "fault_tolerance_stats": stats,
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Fault tolerance stats error: {str(e)}")

@router.get("/scaling/kubernetes/nodes")
async def get_kubernetes_nodes():
    """Get Kubernetes cluster nodes"""
    try:
        nodes = scaling_manager.kubernetes.get_cluster_nodes()

        return {
            "status": "success",
            "kubernetes_available": scaling_manager.kubernetes.service_account_token is not None,
            "nodes": nodes,
            "node_count": len(nodes),
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Kubernetes nodes error: {str(e)}")

@router.get("/scaling/auto-scaling/status")
async def get_auto_scaling_status():
    """Get auto-scaling status"""
    try:
        status = {
            "enabled": scaling_manager.auto_scaler.config.enabled,
            "current_replicas": scaling_manager.auto_scaler.current_replicas,
            "min_nodes": scaling_manager.auto_scaler.config.min_nodes,
            "max_nodes": scaling_manager.auto_scaler.config.max_nodes,
            "scale_up_threshold": scaling_manager.auto_scaler.config.scale_up_threshold,
            "scale_down_threshold": scaling_manager.auto_scaler.config.scale_down_threshold,
            "cooldown_period": scaling_manager.auto_scaler.config.cooldown_period,
            "scaling_strategy": scaling_manager.auto_scaler.config.scaling_strategy.value,
            "last_scale_time": scaling_manager.auto_scaler.last_scale_time,
            "time_since_last_scale": time.time() - scaling_manager.auto_scaler.last_scale_time
        }

        return {
            "status": "success",
            "auto_scaling_status": status,
            "timestamp": time.time()
        }
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Auto-scaling status error: {str(e)}")

@router.get("/scaling/performance/summary")
async def get_scaling_performance_summary():
    """Get comprehensive scaling performance summary"""
    try:
        gpu_status = gpu_optimizer.get_system_status()
        cluster_status = scaling_manager.get_cluster_status()

        summary = {
            "gpu_optimization": gpu_status,
            "distributed_scaling": cluster_status,
            "performance_metrics": {
                "gpu_accelerated": gpu_status.get("gpu_available", False),
                "distributed_enabled": cluster_status.get("distributed_computing", {}).get("distributed_enabled", False),
                "kubernetes_integrated": cluster_status.get("kubernetes_available", False),
                "auto_scaling_active": cluster_status.get("auto_scaling", {}).get("enabled", False),
                "load_balancing_active": len(cluster_status.get("load_balancer", {}).get("nodes", [])) > 0,
                "fault_tolerance_active": True
            },
            "system_health": "optimal"
        }

        # Determine overall system health
        if not gpu_status.get("gpu_available", False):
            summary["system_health"] = "cpu_only"
        elif not cluster_status.get("kubernetes_available", False):
            summary["system_health"] = "single_node"
        elif cluster_status.get("auto_scaling", {}).get("enabled", False):
            summary["system_health"] = "fully_distributed"

        return {
            "status": "success",
            "performance_summary": summary,
            "timestamp": time.time()
        }

    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=f"Performance summary error: {str(e)}")
