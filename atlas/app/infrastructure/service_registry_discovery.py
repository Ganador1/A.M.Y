"""
Service Registry & Discovery
===========================

Sistema de registro y descubrimiento de servicios para ecosistema AXIOM.
Auto-discovery de capabilities, metadata management, health monitoring,
y intelligent routing basado en compatibility matrix results.

Características principales:
- Registry distribuido con persistence
- Auto-discovery de servicios y capabilities
- Health monitoring y status tracking  
- Intelligent routing con compatibility scoring
- Service metadata management
- Load balancing basado en performance metrics
- Circuit breaker integration
- Real-time capability updates
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
from collections import defaultdict
import aiofiles

# Importaciones del ecosistema AXIOM
from app.validation.operational_cross_validation_matrix import OperationalCrossValidationMatrix

logger = logging.getLogger("axiom.service_registry")


class ServiceStatus(Enum):
    """Estados de servicios en el registry"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class CapabilityType(Enum):
    """Tipos de capabilities de servicios"""
    COMPUTATIONAL = "computational"
    ANALYTICAL = "analytical"
    PREDICTIVE = "predictive"
    OPTIMIZATION = "optimization"
    SIMULATION = "simulation"
    PROCESSING = "processing"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    VISUALIZATION = "visualization"
    STORAGE = "storage"
    COMMUNICATION = "communication"
    SECURITY = "security"


@dataclass
class ServiceCapability:
    """Capability individual de un servicio"""
    name: str
    type: CapabilityType
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    compatibility_domains: List[str] = field(default_factory=list)
    requirements: Dict[str, Any] = field(default_factory=dict)
    version: str = "1.0.0"
    last_updated: float = field(default_factory=time.time)


@dataclass
class ServiceMetadata:
    """Metadata completa de un servicio"""
    service_id: str
    name: str
    version: str
    description: str
    endpoint: Optional[str]
    capabilities: List[ServiceCapability]
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    health_status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: float = field(default_factory=time.time)
    registration_time: float = field(default_factory=time.time)
    compatibility_scores: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceDiscoveryQuery:
    """Query para descubrimiento de servicios"""
    capability_types: Optional[List[CapabilityType]] = None
    tags: Optional[List[str]] = None
    compatibility_domains: Optional[List[str]] = None
    min_performance_score: Optional[float] = None
    max_response_time: Optional[float] = None
    required_status: List[ServiceStatus] = field(default_factory=lambda: [ServiceStatus.HEALTHY])
    exclude_services: List[str] = field(default_factory=list)
    limit: int = 10
    sort_by: str = "compatibility_score"  # compatibility_score, performance, response_time


@dataclass
class RoutingDecision:
    """Decisión de routing inteligente"""
    target_service: str
    confidence: float
    reasoning: str
    alternatives: List[str] = field(default_factory=list)
    estimated_performance: Dict[str, float] = field(default_factory=dict)
    compatibility_score: float = 0.0
    routing_metadata: Dict[str, Any] = field(default_factory=dict)


class ServiceRegistry:
    """Registry principal de servicios del ecosistema AXIOM"""
    
    def __init__(self, 
                 cache: Optional[Any] = None,
                 cross_validation_matrix: Optional[OperationalCrossValidationMatrix] = None,
                 persistence_path: str = "data/service_registry.json"):
        self.cache = cache  # Optional cache implementation
        self.cross_validation_matrix = cross_validation_matrix or OperationalCrossValidationMatrix()
        self.persistence_path = persistence_path
        
        # Registry interno
        self._services: Dict[str, ServiceMetadata] = {}
        self._capability_index: Dict[str, Set[str]] = defaultdict(set)
        self._tag_index: Dict[str, Set[str]] = defaultdict(set)
        self._performance_cache: Dict[str, Dict[str, float]] = {}
        self._compatibility_cache: Dict[str, float] = {}  # Cambiar a Dict[str, float] para simplicidad
        
        # Health monitoring
        self._health_check_interval = 30  # segundos
        self._health_check_tasks: Dict[str, asyncio.Task] = {}
        self._circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # Discovery automático
        self._discovery_tasks: Set[asyncio.Task] = set()
        self._auto_discovery_enabled = True
        
        logger.info("🗂️ Service Registry initialized")
    
    async def register_service(self, metadata: ServiceMetadata) -> bool:
        """Registrar un servicio en el registry"""
        try:
            service_id = metadata.service_id
            
            # Validar metadata
            if not await self._validate_service_metadata(metadata):
                logger.error(f"Invalid metadata for service {service_id}")
                return False
            
            # Actualizar registry
            self._services[service_id] = metadata
            
            # Actualizar índices
            await self._update_indices(service_id, metadata)
            
            # Iniciar health monitoring
            await self._start_health_monitoring(service_id)
            
            # Persist al cache y storage
            await self._persist_service_metadata(service_id, metadata)
            
            # Auto-discovery de capabilities si está habilitado
            if self._auto_discovery_enabled:
                await self._auto_discover_capabilities(service_id)
            
            logger.info(f"✅ Service {service_id} registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to register service {metadata.service_id}: {e}")
            return False
    
    async def unregister_service(self, service_id: str) -> bool:
        """Desregistrar un servicio"""
        try:
            if service_id not in self._services:
                logger.warning(f"Service {service_id} not found for unregistration")
                return False
            
            # Detener health monitoring
            await self._stop_health_monitoring(service_id)
            
            # Remover de índices
            await self._remove_from_indices(service_id)
            
            # Remover del registry
            del self._services[service_id]
            
            # Limpiar cache
            await self._cleanup_service_cache(service_id)
            
            # Persist cambios
            await self._persist_registry_state()
            
            logger.info(f"❌ Service {service_id} unregistered")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unregister service {service_id}: {e}")
            return False
    
    async def discover_services(self, query: ServiceDiscoveryQuery) -> List[ServiceMetadata]:
        """Descubrir servicios basado en query"""
        try:
            candidates = set(self._services.keys())
            
            # Filtrar por capability types
            if query.capability_types:
                capability_candidates = set()
                for cap_type in query.capability_types:
                    capability_candidates.update(
                        self._capability_index.get(cap_type.value, set())
                    )
                candidates &= capability_candidates
            
            # Filtrar por tags
            if query.tags:
                tag_candidates = set()
                for tag in query.tags:
                    tag_candidates.update(self._tag_index.get(tag, set()))
                candidates &= tag_candidates
            
            # Filtrar por status
            status_candidates = {
                service_id for service_id, metadata in self._services.items()
                if metadata.health_status in query.required_status
            }
            candidates &= status_candidates
            
            # Excluir servicios específicos
            candidates -= set(query.exclude_services)
            
            # Aplicar filtros de performance
            if query.min_performance_score or query.max_response_time:
                performance_candidates = await self._filter_by_performance(
                    candidates, 
                    query.min_performance_score,
                    query.max_response_time
                )
                candidates &= performance_candidates
            
            # Obtener metadata de candidatos
            results = [self._services[service_id] for service_id in candidates]
            
            # Ordenar resultados
            if query.sort_by == "compatibility_score":
                results.sort(
                    key=lambda s: max(s.compatibility_scores.values()) if s.compatibility_scores else 0.0,
                    reverse=True
                )
            elif query.sort_by == "performance":
                results.sort(
                    key=lambda s: s.performance_metrics.get("overall_score", 0.0),
                    reverse=True
                )
            elif query.sort_by == "response_time":
                results.sort(
                    key=lambda s: s.performance_metrics.get("avg_response_time", float('inf'))
                )
            
            # Aplicar límite
            return results[:query.limit]
            
        except Exception as e:
            logger.error(f"Service discovery failed: {e}")
            return []
    
    async def get_intelligent_routing(self, 
                                    request_payload: Dict[str, Any],
                                    target_capability: CapabilityType,
                                    context: Optional[Dict[str, Any]] = None) -> Optional[RoutingDecision]:
        """Intelligent routing basado en compatibility y performance"""
        try:
            # Descubrir servicios candidatos
            query = ServiceDiscoveryQuery(
                capability_types=[target_capability],
                required_status=[ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
            )
            
            candidates = await self.discover_services(query)
            
            if not candidates:
                logger.warning(f"No candidates found for capability {target_capability}")
                return None
            
            # Calcular scores de routing para cada candidato
            routing_scores = []
            
            for candidate in candidates:
                score_data = await self._calculate_routing_score(
                    candidate, request_payload, context
                )
                routing_scores.append((candidate.service_id, score_data))
            
            # Ordenar por score total
            routing_scores.sort(key=lambda x: x[1]["total_score"], reverse=True)
            
            # Seleccionar mejor candidato
            best_service_id, best_score_data = routing_scores[0]
            alternatives = [service_id for service_id, _ in routing_scores[1:6]]  # Top 5 alternatives
            
            return RoutingDecision(
                target_service=best_service_id,
                confidence=best_score_data["confidence"],
                reasoning=best_score_data["reasoning"],
                alternatives=alternatives,
                estimated_performance=best_score_data["performance_estimate"],
                compatibility_score=best_score_data["compatibility_score"],
                routing_metadata={
                    "selection_criteria": target_capability.value,
                    "total_candidates": len(candidates),
                    "selection_timestamp": time.time()
                }
            )
            
        except Exception as e:
            logger.error(f"Intelligent routing failed: {e}")
            return None
    
    async def update_performance_metrics(self, 
                                       service_id: str, 
                                       metrics: Dict[str, float]) -> bool:
        """Actualizar métricas de performance de un servicio"""
        try:
            if service_id not in self._services:
                logger.warning(f"Service {service_id} not found for metrics update")
                return False
            
            # Actualizar métricas del servicio
            self._services[service_id].performance_metrics.update(metrics)
            self._services[service_id].last_health_check = time.time()
            
            # Actualizar cache de performance
            self._performance_cache[service_id] = metrics
            
            # Persist al cache distribuido
            await self._persist_performance_metrics(service_id, metrics)
            
            # Actualizar circuit breaker si es necesario
            await self._update_circuit_breaker(service_id, metrics)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update performance metrics for {service_id}: {e}")
            return False
    
    async def get_service_compatibility_matrix(self, service_ids: List[str]) -> Dict[str, Any]:
        """Obtener matriz de compatibilidad entre servicios"""
        try:
            compatibility_matrix = {}
            
            # Generar todas las combinaciones de pares
            for i, service_a in enumerate(service_ids):
                compatibility_matrix[service_a] = {}
                
                for service_b in service_ids:
                    if service_a == service_b:
                        compatibility_matrix[service_a][service_b] = 1.0
                        continue
                    
                    # Buscar en cache primero
                    cache_key = f"{min(service_a, service_b)}:{max(service_a, service_b)}"
                    if cache_key in self._compatibility_cache:
                        score = self._compatibility_cache[cache_key]
                    else:
                        # Calcular compatibilidad usando cross-validation matrix
                        score = await self._calculate_service_compatibility(service_a, service_b)
                        self._compatibility_cache[cache_key] = score
                    
                    compatibility_matrix[service_a][service_b] = score
            
            return {
                "matrix": compatibility_matrix,
                "services": service_ids,
                "generated_at": time.time(),
                "cache_hits": len([k for k in self._compatibility_cache.keys() 
                                 if any(s in k for s in service_ids)])
            }
            
        except Exception as e:
            logger.error(f"Failed to generate compatibility matrix: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check del registry completo"""
        try:
            total_services = len(self._services)
            healthy_services = len([
                s for s in self._services.values() 
                if s.health_status == ServiceStatus.HEALTHY
            ])
            
            degraded_services = len([
                s for s in self._services.values() 
                if s.health_status == ServiceStatus.DEGRADED
            ])
            
            unhealthy_services = len([
                s for s in self._services.values() 
                if s.health_status == ServiceStatus.UNHEALTHY
            ])
            
            # Estado general del registry
            registry_health = "healthy"
            if unhealthy_services > total_services * 0.2:  # Más del 20% unhealthy
                registry_health = "unhealthy"
            elif degraded_services > total_services * 0.3:  # Más del 30% degraded
                registry_health = "degraded"
            
            return {
                "status": registry_health,
                "total_services": total_services,
                "healthy_services": healthy_services,
                "degraded_services": degraded_services,
                "unhealthy_services": unhealthy_services,
                "cache_status": await self.cache.health_check() if self.cache else "unavailable",
                "cross_validation_status": await self.cross_validation_matrix.health_check(),
                "active_health_checks": len(self._health_check_tasks),
                "capability_index_size": len(self._capability_index),
                "tag_index_size": len(self._tag_index),
                "compatibility_cache_size": len(self._compatibility_cache),
                "last_updated": time.time()
            }
            
        except Exception as e:
            logger.error(f"Registry health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    # Métodos internos
    
    async def _validate_service_metadata(self, metadata: ServiceMetadata) -> bool:
        """Validar metadata de servicio"""
        if not metadata.service_id or not metadata.name:
            return False
        
        if not metadata.capabilities:
            return False
        
        # Validar cada capability
        for capability in metadata.capabilities:
            if not capability.name or not capability.type:
                return False
        
        return True
    
    async def _update_indices(self, service_id: str, metadata: ServiceMetadata):
        """Actualizar índices de búsqueda"""
        # Índice de capabilities
        for capability in metadata.capabilities:
            self._capability_index[capability.type.value].add(service_id)
        
        # Índice de tags
        for tag in metadata.tags:
            self._tag_index[tag].add(service_id)
    
    async def _remove_from_indices(self, service_id: str):
        """Remover servicio de todos los índices"""
        # Remover de capability index
        for capability_set in self._capability_index.values():
            capability_set.discard(service_id)
        
        # Remover de tag index
        for tag_set in self._tag_index.values():
            tag_set.discard(service_id)
    
    async def _start_health_monitoring(self, service_id: str):
        """Iniciar health monitoring para un servicio"""
        if service_id in self._health_check_tasks:
            self._health_check_tasks[service_id].cancel()
        
        task = asyncio.create_task(self._periodic_health_check(service_id))
        self._health_check_tasks[service_id] = task
    
    async def _stop_health_monitoring(self, service_id: str):
        """Detener health monitoring"""
        if service_id in self._health_check_tasks:
            self._health_check_tasks[service_id].cancel()
            del self._health_check_tasks[service_id]
    
    async def _periodic_health_check(self, service_id: str):
        """Health check periódico de un servicio"""
        while True:
            try:
                await asyncio.sleep(self._health_check_interval)
                
                if service_id not in self._services:
                    break
                
                # Realizar health check básico
                health_status = await self._check_service_health(service_id)
                
                # Actualizar status
                self._services[service_id].health_status = health_status
                self._services[service_id].last_health_check = time.time()
                
                # Log cambios de estado
                if health_status != ServiceStatus.HEALTHY:
                    logger.warning(f"Service {service_id} health status: {health_status.value}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check failed for {service_id}: {e}")
                if service_id in self._services:
                    self._services[service_id].health_status = ServiceStatus.UNKNOWN
    
    async def _check_service_health(self, service_id: str) -> ServiceStatus:
        """Verificar salud de un servicio específico"""
        try:
            metadata = self._services[service_id]
            
            # Verificar métricas recientes
            if metadata.performance_metrics:
                error_rate = metadata.performance_metrics.get("error_rate", 0.0)
                response_time = metadata.performance_metrics.get("avg_response_time", 0.0)
                
                if error_rate > 0.5:  # Más del 50% de errores
                    return ServiceStatus.UNHEALTHY
                elif error_rate > 0.1 or response_time > 5000:  # Más del 10% errores o >5s
                    return ServiceStatus.DEGRADED
            
            # Verificar si el servicio responde
            # (Esto se podría extender para hacer ping real al endpoint)
            
            return ServiceStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Health check error for {service_id}: {e}")
            return ServiceStatus.UNKNOWN
    
    async def _auto_discover_capabilities(self, service_id: str):
        """Auto-discovery de capabilities de un servicio"""
        try:
            # Esta función se podría extender para hacer introspección real
            # del servicio y descubrir sus capabilities automáticamente
            
            metadata = self._services[service_id]
            
            # Ejemplo de discovery básico basado en nombre/tags
            discovered_capabilities = []
            
            if "math" in metadata.name.lower() or "calculation" in metadata.tags:
                discovered_capabilities.append(CapabilityType.COMPUTATIONAL)
            
            if "predict" in metadata.name.lower() or "ml" in metadata.tags:
                discovered_capabilities.append(CapabilityType.PREDICTIVE)
            
            if "optimize" in metadata.name.lower():
                discovered_capabilities.append(CapabilityType.OPTIMIZATION)
            
            # Actualizar capabilities si se descubrieron nuevas
            for cap_type in discovered_capabilities:
                if not any(c.type == cap_type for c in metadata.capabilities):
                    new_capability = ServiceCapability(
                        name=f"auto_discovered_{cap_type.value}",
                        type=cap_type,
                        description=f"Auto-discovered {cap_type.value} capability",
                        input_schema={},
                        output_schema={}
                    )
                    metadata.capabilities.append(new_capability)
                    
                    # Actualizar índice
                    self._capability_index[cap_type.value].add(service_id)
            
        except Exception as e:
            logger.error(f"Auto-discovery failed for {service_id}: {e}")
    
    async def _calculate_routing_score(self, 
                                     candidate: ServiceMetadata,
                                     request_payload: Dict[str, Any],
                                     context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular score de routing para un candidato"""
        try:
            # Factores de scoring
            performance_score = 0.0
            compatibility_score = 0.0
            health_score = 0.0
            load_score = 0.0
            
            # Performance score
            if candidate.performance_metrics:
                response_time = candidate.performance_metrics.get("avg_response_time", 1000)
                error_rate = candidate.performance_metrics.get("error_rate", 0.1)
                throughput = candidate.performance_metrics.get("throughput", 1.0)
                
                performance_score = max(0, min(1, (
                    (1000 / max(response_time, 100)) * 0.4 +  # Tiempo de respuesta
                    (1 - error_rate) * 0.4 +                 # Tasa de error
                    min(throughput / 100, 1) * 0.2           # Throughput normalizado
                )))
            
            # Health score
            health_mapping = {
                ServiceStatus.HEALTHY: 1.0,
                ServiceStatus.DEGRADED: 0.7,
                ServiceStatus.UNHEALTHY: 0.3,
                ServiceStatus.UNKNOWN: 0.5,
                ServiceStatus.MAINTENANCE: 0.1
            }
            health_score = health_mapping.get(candidate.health_status, 0.0)
            
            # Compatibility score (promedio de scores existentes)
            if candidate.compatibility_scores:
                compatibility_score = sum(candidate.compatibility_scores.values()) / len(candidate.compatibility_scores)
            
            # Load score (basado en circuit breaker state)
            load_score = 1.0  # Por defecto asumimos baja carga
            if candidate.service_id in self._circuit_breakers:
                cb_state = self._circuit_breakers[candidate.service_id]
                if cb_state.get("state") == "OPEN":
                    load_score = 0.0
                elif cb_state.get("state") == "HALF_OPEN":
                    load_score = 0.5
            
            # Score total ponderado
            total_score = (
                performance_score * 0.3 +
                compatibility_score * 0.3 +
                health_score * 0.25 +
                load_score * 0.15
            )
            
            # Confidence basado en variabilidad de métricas
            confidence = min(0.9, max(0.1, total_score * 0.8 + 0.2))
            
            # Reasoning
            reasoning_parts = []
            if performance_score > 0.8:
                reasoning_parts.append("excellent performance")
            elif performance_score > 0.6:
                reasoning_parts.append("good performance")
            else:
                reasoning_parts.append("moderate performance")
            
            if health_score == 1.0:
                reasoning_parts.append("healthy status")
            elif health_score >= 0.7:
                reasoning_parts.append("acceptable health")
            else:
                reasoning_parts.append("health concerns")
            
            reasoning = f"Selected based on {', '.join(reasoning_parts)}"
            
            return {
                "total_score": total_score,
                "performance_score": performance_score,
                "compatibility_score": compatibility_score,
                "health_score": health_score,
                "load_score": load_score,
                "confidence": confidence,
                "reasoning": reasoning,
                "performance_estimate": {
                    "expected_response_time": candidate.performance_metrics.get("avg_response_time", 1000),
                    "expected_success_rate": 1 - candidate.performance_metrics.get("error_rate", 0.1),
                    "estimated_throughput": candidate.performance_metrics.get("throughput", 1.0)
                }
            }
            
        except Exception as e:
            logger.error(f"Routing score calculation failed: {e}")
            return {
                "total_score": 0.0,
                "confidence": 0.0,
                "reasoning": f"Calculation error: {str(e)}",
                "performance_estimate": {}
            }
    
    async def _calculate_service_compatibility(self, service_a: str, service_b: str) -> float:
        """Calcular compatibilidad entre dos servicios"""
        try:
            # Usar cross-validation matrix si está disponible
            run = await self.cross_validation_matrix.validate_cross_compatibility([service_a, service_b])
            return run.aggregate_score
        except Exception as e:
            logger.error(f"Compatibility calculation failed for {service_a}, {service_b}: {e}")
            return 0.5  # Score neutral por defecto
    
    async def _filter_by_performance(self, 
                                   candidates: Set[str],
                                   min_performance_score: Optional[float],
                                   max_response_time: Optional[float]) -> Set[str]:
        """Filtrar candidatos por criterios de performance"""
        filtered = set()
        
        for service_id in candidates:
            if service_id not in self._services:
                continue
            
            metrics = self._services[service_id].performance_metrics
            
            # Verificar score mínimo de performance
            if min_performance_score is not None:
                overall_score = metrics.get("overall_score", 0.0)
                if overall_score < min_performance_score:
                    continue
            
            # Verificar tiempo de respuesta máximo
            if max_response_time is not None:
                response_time = metrics.get("avg_response_time", float('inf'))
                if response_time > max_response_time:
                    continue
            
            filtered.add(service_id)
        
        return filtered
    
    async def _persist_service_metadata(self, service_id: str, metadata: ServiceMetadata):
        """Persistir metadata de servicio"""
        try:
            if self.cache:
                await self.cache.set(f"service_metadata:{service_id}", metadata.__dict__, ttl=3600)
        except Exception as e:
            logger.error(f"Failed to persist metadata for {service_id}: {e}")
    
    async def _persist_performance_metrics(self, service_id: str, metrics: Dict[str, float]):
        """Persistir métricas de performance"""
        try:
            if self.cache:
                await self.cache.set(f"service_metrics:{service_id}", metrics, ttl=300)
        except Exception as e:
            logger.error(f"Failed to persist metrics for {service_id}: {e}")
    
    async def _persist_registry_state(self):
        """Persistir estado completo del registry"""
        try:
            registry_state = {
                "services": {sid: metadata.__dict__ for sid, metadata in self._services.items()},
                "last_update": time.time()
            }
            
            # Simple file persistence (sin aiofiles)
            import os
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            
            with aiofiles.aiofiles.open(self.persistence_path, 'w') as f:
                f.write(json.dumps(registry_state, indent=2, default=str))
                
        except Exception as e:
            logger.error(f"Failed to persist registry state: {e}")
    
    async def _cleanup_service_cache(self, service_id: str):
        """Limpiar cache de un servicio"""
        try:
            if self.cache:
                await self.cache.delete(f"service_metadata:{service_id}")
                await self.cache.delete(f"service_metrics:{service_id}")
        except Exception as e:
            logger.error(f"Failed to cleanup cache for {service_id}: {e}")
    
    async def _update_circuit_breaker(self, service_id: str, metrics: Dict[str, float]):
        """Actualizar estado del circuit breaker"""
        try:
            error_rate = metrics.get("error_rate", 0.0)
            response_time = metrics.get("avg_response_time", 0.0)
            
            if service_id not in self._circuit_breakers:
                self._circuit_breakers[service_id] = {
                    "state": "CLOSED",
                    "failure_count": 0,
                    "last_failure": 0,
                    "next_attempt": 0
                }
            
            cb = self._circuit_breakers[service_id]
            
            # Lógica simple de circuit breaker
            if error_rate > 0.5 or response_time > 10000:  # Condiciones de falla
                cb["failure_count"] += 1
                cb["last_failure"] = time.time()
                
                if cb["failure_count"] >= 5:  # Umbral de fallas
                    cb["state"] = "OPEN"
                    cb["next_attempt"] = time.time() + 60  # 60 segundos de timeout
            else:
                # Condiciones de éxito
                if cb["state"] == "HALF_OPEN":
                    cb["state"] = "CLOSED"
                    cb["failure_count"] = 0
                elif cb["state"] == "OPEN" and time.time() > cb["next_attempt"]:
                    cb["state"] = "HALF_OPEN"
            
        except Exception as e:
            logger.error(f"Circuit breaker update failed for {service_id}: {e}")


class ServiceDiscoveryClient:
    """Cliente para interactuar con el Service Registry"""
    
    def __init__(self, registry: ServiceRegistry):
        self.registry = registry
    
    async def find_service(self, 
                          capability: CapabilityType,
                          tags: Optional[List[str]] = None,
                          context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Encontrar el mejor servicio para una capability específica"""
        query = ServiceDiscoveryQuery(
            capability_types=[capability],
            tags=tags or [],
            required_status=[ServiceStatus.HEALTHY, ServiceStatus.UNKNOWN],  # Incluir UNKNOWN por defecto
            limit=50
        )
        
        services = await self.registry.discover_services(query)
        preferred_services = {
            CapabilityType.VALIDATION: "cross_validation_matrix",
        }
        preferred_service_id = preferred_services.get(capability)
        if preferred_service_id:
            for service in services:
                if service.service_id == preferred_service_id:
                    return service.service_id
        return services[0].service_id if services else None
    
    async def get_routing_recommendation(self,
                                       payload: Dict[str, Any],
                                       capability: CapabilityType,
                                       context: Optional[Dict[str, Any]] = None) -> Optional[RoutingDecision]:
        """Obtener recomendación de routing inteligente"""
        return await self.registry.get_intelligent_routing(payload, capability, context)
    
    async def bulk_compatibility_check(self, service_ids: List[str]) -> Dict[str, Any]:
        """Verificación masiva de compatibilidad"""
        return await self.registry.get_service_compatibility_matrix(service_ids)


# Factory functions para inicialización

async def create_service_registry(
    cache: Optional[Any] = None,
    cross_validation_matrix: Optional[OperationalCrossValidationMatrix] = None,
    auto_discovery: bool = True) -> ServiceRegistry:
    """Factory para crear Service Registry configurado"""
    
    registry = ServiceRegistry(
        cache=cache,
        cross_validation_matrix=cross_validation_matrix
    )
    
    registry._auto_discovery_enabled = auto_discovery
    
    # Cargar estado persistido si existe
    try:
        async with aiofiles.open(registry.persistence_path, 'r') as f:
            content = await f.read()
            state = json.loads(content)
            
            # Restaurar servicios
            for service_id, service_data in state.get("services", {}).items():
                # Reconstruir ServiceMetadata desde dict
                # (aquí se implementaría la deserialización completa)
                pass
                
    except FileNotFoundError:
        logger.info("No previous registry state found, starting fresh")
    except Exception as e:
        logger.error(f"Failed to load registry state: {e}")
    
    return registry


# Funciones de utilidad para integración con ecosistema AXIOM

async def auto_register_axiom_services(registry: ServiceRegistry) -> int:
    """Auto-registrar servicios conocidos del ecosistema AXIOM con Knowledge Graph capabilities"""
    registered_count = 0
    
    # Lista de servicios conocidos (extendida con Knowledge Graph)
    known_services = [
        {
            "service_id": "unified_tool_adapter",
            "name": "Unified Tool Adapter",
            "description": "Unified interface for 100+ AXIOM services",
            "capabilities": [
                ServiceCapability(
                    name="service_execution",
                    type=CapabilityType.COMPUTATIONAL,
                    description="Execute unified service operations",
                    input_schema={"payload": "dict"},
                    output_schema={"result": "dict"}
                )
            ],
            "tags": ["core", "adapter", "unified"]
        },
        {
            "service_id": "cross_validation_matrix",
            "name": "Cross-Validation Matrix",
            "description": "Operational cross-validation across scientific domains",
            "capabilities": [
                ServiceCapability(
                    name="compatibility_validation",
                    type=CapabilityType.VALIDATION,
                    description="Validate service compatibility",
                    input_schema={"services": "list"},
                    output_schema={"validation_run": "CrossValidationRun"}
                )
            ],
            "tags": ["validation", "compatibility", "scientific"]
        },
        {
            "service_id": "uncertainty_quantification",
            "name": "Uncertainty Quantification Service",
            "description": "Probabilistic uncertainty analysis",
            "capabilities": [
                ServiceCapability(
                    name="uncertainty_analysis",
                    type=CapabilityType.ANALYTICAL,
                    description="Quantify uncertainty in results",
                    input_schema={"data": "dict"},
                    output_schema={"uncertainty_metrics": "dict"}
                )
            ],
            "tags": ["uncertainty", "probabilistic", "analysis"]
        },
        # Knowledge Graph Services
        {
            "service_id": "knowledge_graph_service",
            "name": "Knowledge Graph Service",
            "description": "Scientific knowledge graph management and querying",
            "capabilities": [
                ServiceCapability(
                    name="knowledge_storage",
                    type=CapabilityType.STORAGE,
                    description="Store and manage scientific knowledge",
                    input_schema={"knowledge": "dict", "domain": "str"},
                    output_schema={"stored_nodes": "int", "stored_relations": "int"}
                ),
                ServiceCapability(
                    name="knowledge_retrieval",
                    type=CapabilityType.ANALYTICAL,
                    description="Query and retrieve scientific knowledge",
                    input_schema={"query": "str", "filters": "dict"},
                    output_schema={"nodes": "list", "relations": "list"}
                ),
                ServiceCapability(
                    name="concept_mapping",
                    type=CapabilityType.TRANSFORMATION,
                    description="Map concepts across scientific domains",
                    input_schema={"source_concept": "str", "target_domains": "list"},
                    output_schema={"mappings": "list", "similarity_scores": "dict"}
                )
            ],
            "tags": ["knowledge", "graph", "ontology", "scientific"]
        },
        {
            "service_id": "semantic_search_service",
            "name": "Semantic Search Service",
            "description": "Advanced semantic search for scientific literature and knowledge",
            "capabilities": [
                ServiceCapability(
                    name="semantic_literature_search",
                    type=CapabilityType.ANALYTICAL,
                    description="Semantic similarity-based literature search",
                    input_schema={"query": "str", "similarity_threshold": "float"},
                    output_schema={"papers": "list", "relevance_scores": "dict"}
                ),
                ServiceCapability(
                    name="concept_similarity",
                    type=CapabilityType.ANALYTICAL,
                    description="Calculate semantic similarity between concepts",
                    input_schema={"concept1": "str", "concept2": "str"},
                    output_schema={"similarity_score": "float", "explanation": "str"}
                ),
                ServiceCapability(
                    name="knowledge_embedding",
                    type=CapabilityType.TRANSFORMATION,
                    description="Generate embeddings for scientific knowledge",
                    input_schema={"text": "str", "domain": "str"},
                    output_schema={"embedding": "list", "dimensions": "int"}
                )
            ],
            "tags": ["semantic", "search", "embeddings", "similarity"]
        },
        {
            "service_id": "ontology_management_service",
            "name": "Ontology Management Service",
            "description": "Scientific ontology creation, validation, and management",
            "capabilities": [
                ServiceCapability(
                    name="ontology_creation",
                    type=CapabilityType.COMPUTATIONAL,
                    description="Create domain-specific scientific ontologies",
                    input_schema={"domain": "str", "concepts": "list", "relations": "list"},
                    output_schema={"ontology_id": "str", "validation_status": "str"}
                ),
                ServiceCapability(
                    name="ontology_validation",
                    type=CapabilityType.VALIDATION,
                    description="Validate ontology consistency and completeness",
                    input_schema={"ontology_id": "str", "validation_rules": "list"},
                    output_schema={"is_valid": "bool", "validation_report": "dict"}
                ),
                ServiceCapability(
                    name="cross_domain_alignment",
                    type=CapabilityType.ANALYTICAL,
                    description="Align ontologies across scientific domains",
                    input_schema={"source_ontology": "str", "target_ontology": "str"},
                    output_schema={"alignments": "list", "confidence_scores": "dict"}
                )
            ],
            "tags": ["ontology", "validation", "alignment", "cross-domain"]
        },
        {
            "service_id": "knowledge_enhanced_literature_service",
            "name": "Knowledge-Enhanced Literature Service",
            "description": "Literature search with knowledge graph integration",
            "capabilities": [
                ServiceCapability(
                    name="knowledge_extraction",
                    type=CapabilityType.ANALYTICAL,
                    description="Extract structured knowledge from scientific papers",
                    input_schema={"paper_ids": "list", "extraction_types": "list"},
                    output_schema={"extracted_knowledge": "dict", "confidence_scores": "dict"}
                ),
                ServiceCapability(
                    name="cross_domain_discovery",
                    type=CapabilityType.ANALYTICAL,
                    description="Discover cross-domain research connections",
                    input_schema={"source_domain": "str", "concept": "str"},
                    output_schema={"connections": "list", "strength_scores": "dict"}
                ),
                ServiceCapability(
                    name="research_hypothesis_generation",
                    type=CapabilityType.PREDICTIVE,
                    description="Generate novel research hypotheses from knowledge gaps",
                    input_schema={"research_area": "str", "creativity_level": "str"},
                    output_schema={"hypotheses": "list", "novelty_scores": "dict"}
                )
            ],
            "tags": ["literature", "knowledge", "extraction", "hypothesis", "discovery"]
        },
        {
            "service_id": "knowledge_enhanced_research_cycle_service",
            "name": "Knowledge-Enhanced Research Cycle Service",
            "description": "Research cycle management with knowledge graph integration",
            "capabilities": [
                ServiceCapability(
                    name="knowledge_enhanced_cycle",
                    type=CapabilityType.COMPUTATIONAL,
                    description="Execute research cycles with domain knowledge integration",
                    input_schema={"research_question": "str", "domain": "str", "enhancement_level": "str"},
                    output_schema={"cycle_id": "str", "knowledge_enhancement": "dict"}
                ),
                ServiceCapability(
                    name="hypothesis_validation",
                    type=CapabilityType.VALIDATION,
                    description="Validate hypotheses against knowledge graph and literature",
                    input_schema={"hypothesis": "str", "validation_depth": "str"},
                    output_schema={"validation_result": "dict", "confidence": "float"}
                ),
                ServiceCapability(
                    name="research_direction_suggestion",
                    type=CapabilityType.PREDICTIVE,
                    description="Suggest research directions based on knowledge analysis",
                    input_schema={"current_research": "str", "creativity_level": "str"},
                    output_schema={"suggestions": "list", "impact_scores": "dict"}
                )
            ],
            "tags": ["research", "cycle", "knowledge", "validation", "prediction"]
        },
        {
            "service_id": "interdisciplinary_discovery_service",
            "name": "Interdisciplinary Discovery Service",
            "description": "Advanced interdisciplinary research opportunity discovery",
            "capabilities": [
                ServiceCapability(
                    name="cross_domain_opportunity_detection",
                    type=CapabilityType.ANALYTICAL,
                    description="Detect interdisciplinary research opportunities",
                    input_schema={"primary_domain": "str", "research_interest": "str"},
                    output_schema={"opportunities": "list", "collaboration_potential": "dict"}
                ),
                ServiceCapability(
                    name="methodology_transfer_analysis",
                    type=CapabilityType.ANALYTICAL,
                    description="Analyze potential for methodology transfer between domains",
                    input_schema={"source_domain": "str", "target_domain": "str", "methodology": "str"},
                    output_schema={"transferability_score": "float", "adaptation_requirements": "list"}
                ),
                ServiceCapability(
                    name="collaborative_research_matching",
                    type=CapabilityType.PREDICTIVE,
                    description="Match researchers and projects for interdisciplinary collaboration",
                    input_schema={"researcher_profile": "dict", "research_interests": "list"},
                    output_schema={"matches": "list", "collaboration_scores": "dict"}
                )
            ],
            "tags": ["interdisciplinary", "collaboration", "discovery", "methodology"]
        }
    ]
    
    for service_data in known_services:
        try:
            metadata = ServiceMetadata(
                service_id=service_data["service_id"],
                name=service_data["name"],
                version="2.0.0" if "knowledge" in service_data["service_id"] else "1.0.0",  # Version upgrade for KG services
                description=service_data["description"],
                endpoint=None,  # Local services
                capabilities=service_data["capabilities"],
                tags=service_data["tags"]
            )
            
            if await registry.register_service(metadata):
                registered_count += 1
                
        except Exception as e:
            logger.error(f"Failed to auto-register {service_data['service_id']}: {e}")
    
    logger.info(f"🔄 Auto-registered {registered_count} AXIOM services (including Knowledge Graph services)")
    return registered_count


if __name__ == "__main__":
    # Ejemplo de uso
    async def main():
        # Crear registry
        registry = await create_service_registry()
        
        # Auto-registrar servicios AXIOM
        await auto_register_axiom_services(registry)
        
        # Ejemplo de discovery
        client = ServiceDiscoveryClient(registry)
        
        # Buscar servicio de validación
        validation_service = await client.find_service(
            capability=CapabilityType.VALIDATION,
            tags=["compatibility"]
        )
        
        print(f"Found validation service: {validation_service}")
        
        # Health check
        health = await registry.health_check()
        print(f"Registry health: {health}")
    
    # asyncio.run(main())
