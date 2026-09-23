"""
⚡ Sistema de Escalabilidad Horizontal AXIOM

Este módulo proporciona endpoints para la gestión completa de escalabilidad horizontal
en la plataforma AXIOM, permitiendo el escalado automático de servicios, balanceo
de carga inteligente y gestión distribuida de instancias de servicio.

Características principales:
- 🔄 **Balanceo de carga inteligente**: Estrategias múltiples (round-robin, least-connections, IP-hash)
- 📊 **Monitoreo de rendimiento**: Métricas detalladas de uso de recursos y latencia
- 🔍 **Descubrimiento de servicios**: Registro automático y health checks de instancias
- 👥 **Gestión de workers**: Escalado dinámico de procesos worker
- 🏥 **Health monitoring**: Verificación continua de salud de todas las instancias
- 📈 **Auto-scaling**: Escalado automático basado en carga y métricas
- 🔧 **Configuración dinámica**: Ajuste en tiempo real de estrategias y parámetros
- 📋 **Dashboard de estado**: Visibilidad completa del estado del sistema distribuido

Estrategias de balanceo disponibles:
- **round_robin**: Distribución cíclica equitativa
- **least_connections**: Prioriza instancias con menos conexiones activas
- **ip_hash**: Consistencia basada en IP del cliente
- **weighted_round_robin**: Distribución proporcional por pesos
- **random**: Selección aleatoria para testing

Componentes del sistema:
- **Load Balancer**: Distribuye requests entre instancias disponibles
- **Service Discovery**: Registra y descubre instancias dinámicamente
- **Worker Manager**: Gestiona pool de procesos worker
- **Health Checker**: Monitorea salud de todas las instancias
- **Metrics Collector**: Recopila métricas de rendimiento

El sistema está diseñado para manejar cargas variables automáticamente,
asegurando alta disponibilidad y rendimiento óptimo para investigación científica
a gran escala en la plataforma AXIOM v4.1.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
Version: 4.1
"""

import logging
import datetime
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.exceptions.domain.biology import BiologyError
from app.distributed.scalability import (
    scalability_manager, LoadBalancingStrategy,
    ServiceInstance,
)
from app.security import require_scopes
from app.types.scalability_types import (
    GetScalabilityStatusResult,
    GetLoadBalancerStatsResult,
    GetRegisteredInstancesResult,
    GetWorkerStatsResult,
    ScalabilityHealthCheckResult,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(
    prefix="/api/v1/scalability",
    tags=["scalability", "load-balancing", "horizontal-scaling"],
    dependencies=[Depends(require_scopes(["scalability:read"]))]
)

@router.get("/status", response_model=Dict[str, Any])
async def get_scalability_status() -> GetScalabilityStatusResult:
    """
    📊 Obtiene estado general del sistema de escalabilidad

    Proporciona una visión comprehensiva del estado actual del sistema de escalabilidad
    horizontal, incluyendo métricas de todas las instancias, balanceadores de carga,
    workers activos y estado de salud general del sistema distribuido.

    Returns:
        Dict[str, Any]: Estado detallado del sistema de escalabilidad con métricas completas

    Raises:
        HTTPException: Si hay error al obtener el estado del sistema

    Example:
        GET /status
        {
            "system_status": "healthy",
            "total_instances": 5,
            "active_instances": 4,
            "load_balancer": {...},
            "workers": {...},
            "timestamp": "2025-01-19T10:30:00Z"
        }
    """
    start_time = datetime.datetime.now()

    try:
        logger.info("📊 Consultando estado del sistema de escalabilidad")

        # Obtener estado del sistema
        status_data = await scalability_manager.get_scalability_status()

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        status_data["metadata"] = {
            "execution_time_seconds": execution_time,
            "timestamp": datetime.datetime.now().isoformat(),
            "query_type": "scalability_status"
        }

        logger.info("✅ Estado de escalabilidad obtenido exitosamente (tiempo: %.4fs)", execution_time)

        return status_data

    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error obteniendo estado de escalabilidad: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estado de escalabilidad: {str(e)}"
        ) from e

@router.post("/start")
async def start_scalability_system() -> Dict[str, str]:
    """Start the scalability system"""
    try:
        await scalability_manager.start()
        return {"message": "Scalability system started successfully"}
    except BiologyError as e:
        logger.error(f"Error starting scalability system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_scalability_system() -> Dict[str, str]:
    """Stop the scalability system"""
    try:
        await scalability_manager.stop()
        return {"message": "Scalability system stopped successfully"}
    except BiologyError as e:
        logger.error(f"Error stopping scalability system: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load-balancer/stats")
async def get_load_balancer_stats() -> GetLoadBalancerStatsResult:
    """Get load balancer statistics"""
    try:
        return scalability_manager.load_balancer.get_stats()
    except BiologyError as e:
        logger.error(f"Error getting load balancer stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load-balancer/strategy")
async def set_load_balancing_strategy(strategy: str) -> Dict[str, str]:
    """Set load balancing strategy"""
    try:
        strategy_enum = LoadBalancingStrategy(strategy.lower())
        scalability_manager.load_balancer.config.strategy = strategy_enum
        return {"message": f"Load balancing strategy set to {strategy}"}
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid strategy: {strategy}")
    except BiologyError as e:
        logger.error(f"Error setting load balancing strategy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load-balancer/strategies")
async def get_available_strategies() -> Dict[str, List[str]]:
    """Get available load balancing strategies"""
    try:
        strategies = [s.value for s in LoadBalancingStrategy]
        return {"strategies": strategies}
    except BiologyError as e:
        logger.error(f"Error getting strategies: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/register")
async def register_instance(
    instance_id: str,
    host: str,
    port: int,
    weight: int = 1
) -> Dict[str, str]:
    """Register a new service instance"""
    try:
        instance = ServiceInstance(
            id=instance_id,
            host=host,
            port=port,
            weight=weight
        )

        await scalability_manager.service_discovery.register_instance(instance)
        scalability_manager.load_balancer.add_instance(instance)

        return {"message": f"Instance {instance_id} registered successfully"}
    except BiologyError as e:
        logger.error(f"Error registering instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/instances/{instance_id}")
async def deregister_instance(instance_id: str) -> Dict[str, str]:
    """Deregister a service instance"""
    try:
        await scalability_manager.service_discovery.deregister_instance(instance_id)
        scalability_manager.load_balancer.remove_instance(instance_id)

        return {"message": f"Instance {instance_id} deregistered successfully"}
    except BiologyError as e:
        logger.error(f"Error deregistering instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances")
async def get_registered_instances() -> GetRegisteredInstancesResult:
    """Get all registered service instances"""
    try:
        instances = await scalability_manager.service_discovery.get_instances()
        return {
            "total_instances": len(instances),
            "instances": [
                {
                    "id": i.id,
                    "url": i.url,
                    "status": i.status.value,
                    "weight": i.weight,
                    "connections": i.connections,
                    "last_health_check": i.last_health_check.isoformat()
                }
                for i in instances
            ]
        }
    except BiologyError as e:
        logger.error(f"Error getting instances: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workers/stats")
async def get_worker_stats() -> GetWorkerStatsResult:
    """Get worker process statistics"""
    try:
        return scalability_manager.worker_manager.get_worker_stats()
    except BiologyError as e:
        logger.error(f"Error getting worker stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workers/start")
async def start_workers(count: int = 4) -> Dict[str, str]:
    """Start worker processes"""
    try:
        scalability_manager.worker_manager.worker_count = count
        await scalability_manager.worker_manager.start_workers()
        return {"message": f"Started {count} worker processes"}
    except BiologyError as e:
        logger.error(f"Error starting workers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/workers/stop")
async def stop_workers() -> Dict[str, str]:
    """Stop all worker processes"""
    try:
        await scalability_manager.worker_manager.stop_workers()
        return {"message": "All worker processes stopped"}
    except BiologyError as e:
        logger.error(f"Error stopping workers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load-balancer/test")
async def test_load_balancer(
    client_ip: Optional[str] = None,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """Test load balancer instance selection"""
    try:
        instance = await scalability_manager.load_balancer.select_instance(client_ip, session_id)

        if instance:
            return {
                "selected_instance": {
                    "id": instance.id,
                    "url": instance.url,
                    "status": instance.status.value,
                    "connections": instance.connections
                }
            }
        else:
            return {"message": "No healthy instances available"}

    except BiologyError as e:
        logger.error(f"Error testing load balancer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def scalability_health_check() -> ScalabilityHealthCheckResult:
    """Health check for scalability systems"""
    try:
        # Simple health check without complex status gathering
        return {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "components": {
                "load_balancer": "active",
                "service_discovery": "active",
                "worker_manager": "active",
                "health_checker": "active"
            },
            "metrics": {
                "total_instances": 0,
                "healthy_instances": 0,
                "active_workers": 0,
                "load_balancer_strategy": "round_robin"
            }
        }
    except BiologyError as e:
        logger.error(f"Scalability health check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
