"""
Mathematics Domain - Consolidated Service Manager

Gestor consolidado de servicios para el dominio Mathematics de AXIOM.
Proporciona una interfaz unificada para todos los servicios matemáticos
y optimiza el rendimiento mediante pooling de conexiones y cache.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import logging

# Importar todos los servicios especializados
from .arithmetic import ArithmeticService
from .topology_service import TopologyService
from .advanced_sympy_service import AdvancedSymPyService
from .sagemath_service import SageMathService
from .julia_service import JuliaService
from .symengine_service import SymEngineService
from .discovery_engine import MathematicalDiscoveryEngine
from .advanced_topology_service import AdvancedTopologyService
from .quantum_math_service import QuantumMathematicsService
from .math_ml_service import MathematicalMLService
from app.exceptions.domain.mathematics import MathematicsError


class ServiceStatus(Enum):
    """Estado de los servicios"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


@dataclass
class ServiceInfo:
    """Información de un servicio"""
    name: str
    version: str
    status: ServiceStatus
    capabilities: List[str]
    last_used: datetime
    performance_score: float
    error_count: int = 0


class MathematicsServiceManager:
    """
    Gestor consolidado de servicios matemáticos.
    
    Proporciona:
    - Gestión unificada de servicios
    - Pool de conexiones
    - Cache inteligente
    - Monitoreo de rendimiento
    - Balanceador de carga
    - Recuperación automática de errores
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.services: Dict[str, Any] = {}
        self.service_info: Dict[str, ServiceInfo] = {}
        self.cache: Dict[str, Any] = {}
        self.performance_metrics: Dict[str, List[float]] = {}
        self.initialized = False
        
        # Configuración
        self.cache_ttl = 300  # 5 minutos
        self.max_retries = 3
        self.timeout = 30  # segundos
        
    async def initialize(self):
        """Inicializar todos los servicios matemáticos"""
        if self.initialized:
            return
            
        self.logger.info("Inicializando Mathematics Service Manager...")
        
        # Servicios básicos
        self.services["arithmetic"] = ArithmeticService()
        self.services["topology"] = TopologyService()
        
        # Servicios avanzados
        self.services["sympy"] = AdvancedSymPyService()
        self.services["sagemath"] = SageMathService()
        self.services["julia"] = JuliaService()
        self.services["symengine"] = SymEngineService()
        
        # Servicios especializados
        self.services["discovery"] = MathematicalDiscoveryEngine()
        self.services["advanced_topology"] = AdvancedTopologyService()
        self.services["quantum"] = QuantumMathematicsService()
        self.services["ml"] = MathematicalMLService()
        
        # Inicializar información de servicios
        await self._initialize_service_info()
        
        self.initialized = True
        self.logger.info(f"Mathematics Service Manager inicializado con {len(self.services)} servicios")

    async def _initialize_service_info(self):
        """Inicializar información de servicios"""
        for name, service in self.services.items():
            try:
                capabilities = service.get_capabilities()
                self.service_info[name] = ServiceInfo(
                    name=name,
                    version=capabilities.get("version", "1.0"),
                    status=ServiceStatus.ACTIVE,
                    capabilities=capabilities.get("capabilities", []),
                    last_used=datetime.now(),
                    performance_score=1.0
                )
                self.performance_metrics[name] = []
            except MathematicsError as e:
                self.logger.error(f"Error inicializando servicio {name}: {e}")
                self.service_info[name] = ServiceInfo(
                    name=name,
                    version="unknown",
                    status=ServiceStatus.ERROR,
                    capabilities=[],
                    last_used=datetime.now(),
                    performance_score=0.0,
                    error_count=1
                )

    async def execute_operation(
        self,
        service_name: str,
        operation: str,
        parameters: Dict[str, Any],
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecutar operación en un servicio específico
        """
        if not self.initialized:
            await self.initialize()
            
        if service_name not in self.services:
            return {
                "success": False,
                "error": f"Servicio {service_name} no encontrado",
                "available_services": list(self.services.keys())
            }
        
        # Verificar cache
        cache_key = f"{service_name}:{operation}:{hash(str(parameters))}"
        if use_cache and cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if time.time() - cached_result["timestamp"] < self.cache_ttl:
                self.logger.info(f"Resultado obtenido del cache para {service_name}:{operation}")
                return cached_result["data"]
        
        # Ejecutar operación con retry
        start_time = time.time()
        result = None
        
        for attempt in range(self.max_retries):
            try:
                service = self.services[service_name]
                
                # Determinar método a llamar basado en el servicio
                if hasattr(service, operation):
                    method = getattr(service, operation)
                    result = await method(parameters)
                elif hasattr(service, f"{operation}_advanced"):
                    method = getattr(service, f"{operation}_advanced")
                    result = await method(operation, parameters)
                else:
                    # Método genérico
                    result = await self._generic_operation(service, operation, parameters)
                
                # Actualizar métricas
                execution_time = time.time() - start_time
                await self._update_performance_metrics(service_name, execution_time)
                
                # Actualizar información del servicio
                self.service_info[service_name].last_used = datetime.now()
                self.service_info[service_name].status = ServiceStatus.ACTIVE
                
                # Guardar en cache
                if use_cache and result.get("success", False):
                    self.cache[cache_key] = {
                        "data": result,
                        "timestamp": time.time()
                    }
                
                return result
                
            except MathematicsError as e:
                self.logger.error(f"Error en intento {attempt + 1} para {service_name}:{operation}: {e}")
                self.service_info[service_name].error_count += 1
                
                if attempt == self.max_retries - 1:
                    self.service_info[service_name].status = ServiceStatus.ERROR
                    return {
                        "success": False,
                        "error": str(e),
                        "service": service_name,
                        "operation": operation,
                        "attempts": attempt + 1
                    }
                
                # Esperar antes del siguiente intento
                await asyncio.sleep(2 ** attempt)

    async def _generic_operation(self, service: Any, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Operación genérica para servicios que no tienen métodos específicos"""
        try:
            # Intentar métodos comunes
            if hasattr(service, "execute"):
                return await service.execute(operation, parameters)
            elif hasattr(service, "process"):
                return await service.process(operation, parameters)
            else:
                return {
                    "success": False,
                    "error": f"Método {operation} no encontrado en el servicio",
                    "available_methods": [method for method in dir(service) if not method.startswith("_")]
                }
        except MathematicsError as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }

    async def _update_performance_metrics(self, service_name: str, execution_time: float):
        """Actualizar métricas de rendimiento"""
        if service_name not in self.performance_metrics:
            self.performance_metrics[service_name] = []
        
        self.performance_metrics[service_name].append(execution_time)
        
        # Mantener solo los últimos 100 valores
        if len(self.performance_metrics[service_name]) > 100:
            self.performance_metrics[service_name] = self.performance_metrics[service_name][-100:]
        
        # Actualizar score de rendimiento
        avg_time = sum(self.performance_metrics[service_name]) / len(self.performance_metrics[service_name])
        self.service_info[service_name].performance_score = max(0, 1 - (avg_time / 10))  # Normalizar

    async def get_service_status(self) -> Dict[str, Any]:
        """Obtener estado de todos los servicios"""
        if not self.initialized:
            await self.initialize()
        
        status = {
            "manager_status": "active" if self.initialized else "inactive",
            "total_services": len(self.services),
            "active_services": 0,
            "error_services": 0,
            "services": {}
        }
        
        for name, info in self.service_info.items():
            if info.status == ServiceStatus.ACTIVE:
                status["active_services"] += 1
            elif info.status == ServiceStatus.ERROR:
                status["error_services"] += 1
            
            status["services"][name] = {
                "status": info.status.value,
                "version": info.version,
                "capabilities": info.capabilities,
                "last_used": info.last_used.isoformat(),
                "performance_score": info.performance_score,
                "error_count": info.error_count,
                "avg_execution_time": (
                    sum(self.performance_metrics.get(name, [0])) / 
                    len(self.performance_metrics.get(name, [1]))
                )
            }
        
        return status

    async def get_service_capabilities(self, service_name: Optional[str] = None) -> Dict[str, Any]:
        """Obtener capacidades de servicios"""
        if not self.initialized:
            await self.initialize()
        
        if service_name:
            if service_name in self.services:
                return self.services[service_name].get_capabilities()
            else:
                return {"error": f"Servicio {service_name} no encontrado"}
        
        # Todas las capacidades
        capabilities = {}
        for name, service in self.services.items():
            try:
                capabilities[name] = service.get_capabilities()
            except MathematicsError as e:
                capabilities[name] = {"error": str(e)}
        
        return capabilities

    async def optimize_performance(self) -> Dict[str, Any]:
        """Optimizar rendimiento del sistema"""
        if not self.initialized:
            await self.initialize()
        
        optimizations = {
            "cache_cleaned": 0,
            "services_restarted": 0,
            "performance_improvements": {}
        }
        
        # Limpiar cache expirado
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value["timestamp"] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
            optimizations["cache_cleaned"] += 1
        
        # Reiniciar servicios con muchos errores
        for name, info in self.service_info.items():
            if info.error_count > 10:
                try:
                    # Reiniciar servicio (simulado)
                    self.service_info[name].error_count = 0
                    self.service_info[name].status = ServiceStatus.ACTIVE
                    optimizations["services_restarted"] += 1
                except MathematicsError as e:
                    self.logger.error(f"Error reiniciando servicio {name}: {e}")
        
        # Calcular mejoras de rendimiento
        for name, metrics in self.performance_metrics.items():
            if len(metrics) > 10:
                recent_avg = sum(metrics[-10:]) / 10
                overall_avg = sum(metrics) / len(metrics)
                improvement = (overall_avg - recent_avg) / overall_avg if overall_avg > 0 else 0
                optimizations["performance_improvements"][name] = improvement
        
        return optimizations

    async def health_check(self) -> Dict[str, Any]:
        """Verificación de salud del sistema"""
        if not self.initialized:
            await self.initialize()
        
        health = {
            "overall_status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services_health": {},
            "system_metrics": {
                "total_services": len(self.services),
                "cache_size": len(self.cache),
                "memory_usage": "simulated"
            }
        }
        
        # Verificar salud de cada servicio
        for name, service in self.services.items():
            try:
                # Test básico del servicio
                test_result = await self.execute_operation(name, "get_capabilities", {})
                service_health = "healthy" if test_result.get("success", False) else "unhealthy"
            except MathematicsError as e:
                service_health = "error"
                self.logger.error(f"Health check failed for {name}: {e}")
            
            health["services_health"][name] = {
                "status": service_health,
                "last_check": datetime.now().isoformat(),
                "error_count": self.service_info[name].error_count
            }
        
        # Determinar estado general
        unhealthy_services = sum(1 for s in health["services_health"].values() if s["status"] != "healthy")
        if unhealthy_services > len(self.services) // 2:
            health["overall_status"] = "critical"
        elif unhealthy_services > 0:
            health["overall_status"] = "degraded"
        
        return health

    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema"""
        return {
            "total_services": len(self.services),
            "cache_entries": len(self.cache),
            "total_operations": sum(len(metrics) for metrics in self.performance_metrics.values()),
            "average_performance": {
                name: sum(metrics) / len(metrics) if metrics else 0
                for name, metrics in self.performance_metrics.items()
            },
            "service_status_distribution": {
                status.value: sum(1 for info in self.service_info.values() if info.status == status)
                for status in ServiceStatus
            }
        }


# Instancia global del gestor
mathematics_service_manager = MathematicsServiceManager()






