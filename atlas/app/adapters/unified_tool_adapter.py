"""
Unified Tool Adapter Interface para AXIOM Ecosystem
Consolida 100+ servicios existentes bajo una interfaz común unificada
con patrones de resilencia, circuit breakers, y auto-discovery.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set, Union
from contextlib import asynccontextmanager

from app.core.bootstrap_logging import logger
from app.services.base_service import BaseService


class ServiceStatus(Enum):
    """Estados del servicio para circuit breaker"""
    HEALTHY = "healthy"
    DEGRADED = "degraded" 
    UNHEALTHY = "unhealthy"
    CIRCUIT_OPEN = "circuit_open"


@dataclass
class ToolCapability:
    """Metadatos de capacidad de herramienta"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    tags: Set[str] = field(default_factory=set)
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)
    estimated_duration_ms: Optional[int] = None
    
    
@dataclass
class ExecutionConfig:
    """Configuración unificada de ejecución"""
    timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_ms: int = 1000
    circuit_breaker_enabled: bool = True
    failure_threshold: int = 5
    recovery_timeout_seconds: int = 60
    max_concurrent: int = 10
    

@dataclass
class ExecutionResult:
    """Resultado estandarizado de ejecución"""
    success: bool
    data: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: int = 0
    service_name: str = ""
    capability_used: Optional[str] = None
    retry_count: int = 0
    from_cache: bool = False


class CircuitBreaker:
    """Circuit breaker pattern para servicios"""
    
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = 0
        self.status = ServiceStatus.HEALTHY
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Ejecuta función con circuit breaker protection"""
        if not self.config.circuit_breaker_enabled:
            # Si circuit breaker está deshabilitado, ejecutar directamente
            return await func(*args, **kwargs)
            
        async with self._lock:
            if self.status == ServiceStatus.CIRCUIT_OPEN:
                if time.time() - self.last_failure_time > self.config.recovery_timeout_seconds:
                    self.status = ServiceStatus.DEGRADED  # Half-open state
                    logger.info("Circuit breaker entering half-open state")
                else:
                    raise Exception("Circuit breaker is OPEN")
                    
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
            
    async def _on_success(self):
        """Reset en caso de éxito"""
        async with self._lock:
            self.failure_count = 0
            self.status = ServiceStatus.HEALTHY
            
    async def _on_failure(self):
        """Incrementa fallas y evalúa circuit breaking"""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.status = ServiceStatus.CIRCUIT_OPEN
                logger.error(f"Circuit breaker OPENED after {self.failure_count} failures")
            elif self.failure_count >= self.config.failure_threshold // 2:
                self.status = ServiceStatus.DEGRADED


class UnifiedToolInterface(ABC):
    """Interfaz unificada para todas las herramientas del ecosistema AXIOM"""
    
    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Método unificado de ejecución - TODAS las herramientas deben implementar esto"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[ToolCapability]:
        """Retorna las capacidades que este tool puede realizar"""
        pass
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check básico - puede ser sobrescrito"""
        return {"status": "healthy", "timestamp": time.time()}


class BaseServiceAdapter(UnifiedToolInterface):
    """Adapter para servicios existentes que heredan de BaseService"""
    
    def __init__(self, service: BaseService, config: Optional[ExecutionConfig] = None):
        self.service = service
        self.config = config or ExecutionConfig()
        self.circuit_breaker = CircuitBreaker(self.config)
        self._capabilities_cache: Optional[List[ToolCapability]] = None
        
    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Implementación unificada usando process_request del BaseService"""
        start_time = time.time()
        
        try:
            # Circuit breaker protection
            result_data = await self.circuit_breaker.call(
                self.service.process_request, payload
            )
            
            execution_time = int((time.time() - start_time) * 1000)
            
            return {
                "success": result_data.get("success", True),
                "data": result_data,
                "execution_time_ms": execution_time,
                "service_name": self.service.name
            }
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Service {self.service.name} failed: {str(e)}")
            
            return {
                "success": False,
                "data": {},
                "error": str(e),
                "execution_time_ms": execution_time,
                "service_name": self.service.name
            }
    
    def get_capabilities(self) -> List[ToolCapability]:
        """Auto-discovery de capacidades basado en introspección"""
        if self._capabilities_cache:
            return self._capabilities_cache
            
        capabilities = []
        
        # Analizar métodos públicos del service
        for method_name in dir(self.service):
            if not method_name.startswith('_') and method_name not in ['log_request', 'log_response', 'handle_error']:
                method = getattr(self.service, method_name)
                if callable(method) and method_name != 'process_request':
                    # Auto-generar capability
                    capability = ToolCapability(
                        name=f"{self.service.name}.{method_name}",
                        description=f"Execute {method_name} on {self.service.name}",
                        input_schema=self._infer_schema(method),
                        output_schema={"type": "object"},  # Generic schema
                        tags={self.service.name.lower(), method_name}
                    )
                    capabilities.append(capability)
        
        # Capacidad general process_request
        main_capability = ToolCapability(
            name=f"{self.service.name}.process_request", 
            description=f"Main processing capability for {self.service.name}",
            input_schema={"type": "object", "properties": {"action": {"type": "string"}}},
            output_schema={"type": "object", "properties": {"success": {"type": "boolean"}}},
            tags={self.service.name.lower(), "main"}
        )
        capabilities.append(main_capability)
        
        self._capabilities_cache = capabilities
        return capabilities
    
    def _infer_schema(self, method: Callable) -> Dict[str, Any]:
        """Inferir schema básico de un método"""
        try:
            sig = inspect.signature(method)
            properties = {}
            
            for param_name, param in sig.parameters.items():
                if param_name in ['self', 'request_data']:
                    continue
                    
                param_type = "string"  # Default
                if param.annotation != inspect.Parameter.empty:
                    if param.annotation is int:
                        param_type = "integer"
                    elif param.annotation is float:
                        param_type = "number" 
                    elif param.annotation is bool:
                        param_type = "boolean"
                        
                properties[param_name] = {"type": param_type}
                
            return {"type": "object", "properties": properties}
        except Exception:
            return {"type": "object"}


class ToolRegistry:
    """Registry central para todos los tools unificados"""
    
    def __init__(self):
        self._tools: Dict[str, UnifiedToolInterface] = {}
        self._capabilities_index: Dict[str, str] = {}  # capability_name -> tool_name
        self._tags_index: Dict[str, List[str]] = {}     # tag -> [tool_names]
        
    def register_tool(self, name: str, tool: UnifiedToolInterface):
        """Registrar una nueva herramienta"""
        self._tools[name] = tool
        
        # Indexar capacidades
        for capability in tool.get_capabilities():
            self._capabilities_index[capability.name] = name
            
            # Indexar tags
            for tag in capability.tags:
                if tag not in self._tags_index:
                    self._tags_index[tag] = []
                self._tags_index[tag].append(name)
                
        logger.info(f"✅ Tool '{name}' registered with {len(tool.get_capabilities())} capabilities")
    
    def register_base_service(self, service: BaseService, config: Optional[ExecutionConfig] = None):
        """Registrar un BaseService mediante adapter"""
        adapter = BaseServiceAdapter(service, config)
        self.register_tool(service.name, adapter)
        
    def get_tool(self, name: str) -> Optional[UnifiedToolInterface]:
        """Obtener tool por nombre"""
        return self._tools.get(name)
        
    def find_by_capability(self, capability_name: str) -> Optional[UnifiedToolInterface]:
        """Encontrar tool por capacidad específica"""
        tool_name = self._capabilities_index.get(capability_name)
        return self._tools.get(tool_name) if tool_name else None
        
    def find_by_tag(self, tag: str) -> List[UnifiedToolInterface]:
        """Encontrar tools por tag"""
        tool_names = self._tags_index.get(tag, [])
        return [self._tools[name] for name in tool_names if name in self._tools]
    
    def list_all_capabilities(self) -> List[ToolCapability]:
        """Listar todas las capacidades disponibles"""
        all_capabilities = []
        for tool in self._tools.values():
            all_capabilities.extend(tool.get_capabilities())
        return all_capabilities
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Health check de todos los tools registrados"""
        results = {}
        for name, tool in self._tools.items():
            try:
                health = await tool.health_check()
                results[name] = health
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
        return results


# Singleton global registry
global_tool_registry = ToolRegistry()


class UnifiedExecutor:
    """Ejecutor unificado con capabilities avanzadas"""
    
    def __init__(self, registry: Optional[ToolRegistry] = None, config: Optional[ExecutionConfig] = None):
        self.registry = registry or global_tool_registry
        self.config = config or ExecutionConfig()
        self._semaphore = asyncio.Semaphore(self.config.max_concurrent)
        
    async def execute(self, tool_name: str, payload: Dict[str, Any]) -> ExecutionResult:
        """Ejecutar herramienta por nombre con retry y timeout"""
        async with self._semaphore:
            tool = self.registry.get_tool(tool_name)
            if not tool:
                return ExecutionResult(
                    success=False,
                    error=f"Tool '{tool_name}' not found",
                    service_name=tool_name
                )
            
            return await self._execute_with_retry(tool, payload, tool_name)
    
    async def execute_by_capability(self, capability_name: str, payload: Dict[str, Any]) -> ExecutionResult:
        """Ejecutar por capacidad específica"""
        async with self._semaphore:
            tool = self.registry.find_by_capability(capability_name)
            if not tool:
                return ExecutionResult(
                    success=False,
                    error=f"No tool found for capability '{capability_name}'",
                    capability_used=capability_name
                )
            
            return await self._execute_with_retry(tool, payload, capability_name)
    
    async def _execute_with_retry(self, tool: UnifiedToolInterface, payload: Dict[str, Any], identifier: str) -> ExecutionResult:
        """Ejecutar con retry automático"""
        last_error = None
        
        for attempt in range(self.config.retry_attempts):
            try:
                start_time = time.time()
                
                # Timeout protection
                result_data = await asyncio.wait_for(
                    tool.run(payload),
                    timeout=self.config.timeout_seconds
                )
                
                execution_time = int((time.time() - start_time) * 1000)
                
                # Check if the tool itself reported failure
                tool_success = result_data.get("success", True)
                tool_error = result_data.get("error")
                
                if tool_success:
                    # Success case
                    return ExecutionResult(
                        success=True,
                        data=result_data.get("data", result_data),
                        error=tool_error,
                        execution_time_ms=execution_time,
                        service_name=result_data.get("service_name", identifier),
                        retry_count=attempt
                    )
                else:
                    # Tool reported failure - treat as retryable error
                    last_error = tool_error or "Tool reported failure"
                    logger.warning(f"Tool {identifier} reported failure on attempt {attempt + 1}: {last_error}")
                    
                    # Only continue retry loop if we have attempts left
                    if attempt == self.config.retry_attempts - 1:
                        break
                        
                    # Delay before retry
                    await asyncio.sleep(self.config.retry_delay_ms / 1000.0)
                    continue
                
            except asyncio.TimeoutError:
                last_error = f"Timeout after {self.config.timeout_seconds}s"
                logger.warning(f"Tool {identifier} timed out on attempt {attempt + 1}")
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Tool {identifier} failed on attempt {attempt + 1}: {last_error}")
            
            # Delay antes del retry (solo si no es el último intento)
            if attempt < self.config.retry_attempts - 1:
                await asyncio.sleep(self.config.retry_delay_ms / 1000.0)
        
        return ExecutionResult(
            success=False,
            error=last_error or "All retry attempts failed",
            service_name=identifier,
            retry_count=self.config.retry_attempts
        )
    
    async def execute_batch(self, requests: List[Dict[str, Any]]) -> List[ExecutionResult]:
        """Ejecutar múltiples requests en paralelo"""
        tasks = []
        
        for req in requests:
            if "tool_name" in req:
                task = self.execute(req["tool_name"], req.get("payload", {}))
            elif "capability" in req:
                task = self.execute_by_capability(req["capability"], req.get("payload", {}))
            else:
                # Resultado de error inmediato para malformed requests
                async def error_task():
                    return ExecutionResult(
                        success=False, 
                        error="Request must have 'tool_name' or 'capability'"
                    )
                task = error_task()
            
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [r for r in results if isinstance(r, ExecutionResult)]


# Auto-discovery helper para registrar servicios existentes
async def auto_register_existing_services(registry: Optional[ToolRegistry] = None) -> Dict[str, Any]:
    """Auto-registra servicios existentes encontrados en el módulo app.services"""
    registry = registry or global_tool_registry
    
    import importlib
    import pkgutil
    import app.services
    
    registered_count = 0
    errors = []
    
    # Discover all service modules
    for importer, modname, ispkg in pkgutil.iter_modules(app.services.__path__, app.services.__name__ + "."):
        try:
            module = importlib.import_module(modname)
            
            # Find BaseService subclasses
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (inspect.isclass(attr) and 
                    issubclass(attr, BaseService) and 
                    attr != BaseService):
                    
                    # Instantiate and register - skip abstract BaseService
                    if attr.__name__ != 'BaseService':
                        service_instance = attr()  # type: ignore
                        registry.register_base_service(service_instance)
                    registered_count += 1
                    
        except Exception as e:
            errors.append(f"Error loading {modname}: {str(e)}")
            logger.warning(f"Could not auto-register from {modname}: {str(e)}")
    
    logger.info(f"🚀 Auto-registered {registered_count} services")
    return {"registered": registered_count, "errors": errors}


# Context manager para easy setup
@asynccontextmanager
async def unified_ecosystem():
    """Context manager para setup completo del ecosistema unificado"""
    logger.info("🌟 Initializing Unified AXIOM Ecosystem...")
    
    # Auto-register existing services
    stats = await auto_register_existing_services()
    
    executor = UnifiedExecutor()
    
    try:
        yield {
            "registry": global_tool_registry,
            "executor": executor,
            "stats": stats
        }
    finally:
        logger.info("🔽 Unified AXIOM Ecosystem shutdown")
