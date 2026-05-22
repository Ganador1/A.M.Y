import asyncio
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from enum import Enum
from app.services.base_service import BaseService
import time

class UnifiedToolInterface:
    async def run(self, payload: Dict[str, Any]):
        raise NotImplementedError

@dataclass
class ToolCapability:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    tags: set

class ServiceStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"

@dataclass
class ExecutionConfig:
    timeout_seconds: Optional[float] = None
    retry_attempts: int = 0
    retry_delay_ms: int = 0
    failure_threshold: int = 3
    recovery_timeout_seconds: int = 5
    circuit_breaker_enabled: bool = True

class CircuitBreaker:
    def __init__(self, config: ExecutionConfig):
        self.config = config
        self.failures = 0
        self.status = ServiceStatus.HEALTHY

    async def call(self, fn):
        if self.status == ServiceStatus.CIRCUIT_OPEN:
            raise Exception("Circuit breaker is OPEN")
        try:
            res = await fn()
            self.failures = 0
            self.status = ServiceStatus.HEALTHY
            return res
        except Exception:
            self.failures += 1
            if self.failures >= self.config.failure_threshold:
                self.status = ServiceStatus.CIRCUIT_OPEN
            else:
                self.status = ServiceStatus.DEGRADED
            raise

class ExecutionResult:
    def __init__(self, success: bool, data: Any = None, service_name: Optional[str] = None, error: Optional[str] = None, retry_count: int = 0):
        self.success = success
        self.data = data
        self.service_name = service_name
        self.error = error
        self.retry_count = retry_count

class BaseServiceAdapter:
    def __init__(self, service: BaseService):
        self.service = service

    async def run(self, request_data: Dict[str, Any]):
        start = time.time()
        try:
            res = await self.service.process_request(request_data)
            elapsed_ms = int((time.time() - start) * 1000)
            return {"success": True, "data": res, "service_name": self.service.name, "execution_time_ms": elapsed_ms}
        except Exception as e:
            elapsed_ms = int((time.time() - start) * 1000)
            return {"success": False, "error": str(e), "service_name": self.service.name, "execution_time_ms": elapsed_ms}

    def get_capabilities(self) -> List[ToolCapability]:
        # Provide a basic capability for process_request
        cap = ToolCapability(
            name=f"{self.service.name}.process_request",
            description="Process request",
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            tags={self.service.name.lower()}
        )
        return [cap]

class ToolRegistry:
    def __init__(self):
        self.tools = {}
        self._adapter_configs = {}

    def register_tool(self, name: str, tool: UnifiedToolInterface):
        self.tools[name] = tool

    def get_tool(self, name: str):
        return self.tools.get(name)

    def list_all_capabilities(self) -> List[ToolCapability]:
        caps = []
        for t in self.tools.values():
            if hasattr(t, 'get_capabilities'):
                caps.extend(t.get_capabilities())
        return caps

    def register_base_service(self, service: BaseService, adapter_config: Optional[ExecutionConfig] = None):
        adapter = BaseServiceAdapter(service)
        self.register_tool(service.name, adapter)
        if adapter_config:
            self._adapter_configs[service.name] = adapter_config

    def find_by_capability(self, capability_name: str) -> Optional[UnifiedToolInterface]:
        for t in self.tools.values():
            if hasattr(t, 'get_capabilities'):
                for c in t.get_capabilities():
                    if c.name == capability_name:
                        return t
        return None

    def find_by_tag(self, tag: str) -> List[UnifiedToolInterface]:
        found = []
        for t in self.tools.values():
            if hasattr(t, 'get_capabilities'):
                for c in t.get_capabilities():
                    if tag in c.tags:
                        found.append(t)
                        break
        return found

    async def health_check_all(self):
        result = {}
        for name, tool in self.tools.items():
            result[name] = {"status": "healthy"}
        return result


class UnifiedExecutor:
    def __init__(self, registry: ToolRegistry, config: Optional[ExecutionConfig] = None):
        self.registry = registry
        self.config = config or ExecutionConfig()

    async def execute(self, tool_name: str, payload: Dict[str, Any]) -> ExecutionResult:
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ExecutionResult(False, error=f"{tool_name} not found")

        # Retries
        attempts = 0
        last_exc = None
        while attempts <= self.config.retry_attempts:
            try:
                if isinstance(tool, BaseServiceAdapter):
                    coro = tool.run(payload)
                else:
                    coro = tool.run(payload)

                if self.config.timeout_seconds:
                    res = await asyncio.wait_for(coro, timeout=self.config.timeout_seconds)
                else:
                    res = await coro

                # Standardize ExecutionResult
                success = res.get('success', True) if isinstance(res, dict) else True
                return ExecutionResult(success, data=(res.get('message') if isinstance(res, dict) and 'message' in res else res), service_name=getattr(tool, 'service', getattr(tool, 'name', None)).name if hasattr(getattr(tool, 'service', tool), 'name') else getattr(tool, 'name', None), retry_count=attempts)
            except Exception as e:
                last_exc = e
                attempts += 1
                if attempts <= self.config.retry_attempts:
                    await asyncio.sleep(self.config.retry_delay_ms / 1000.0)
                else:
                    return ExecutionResult(False, error=str(e), retry_count=attempts)

    async def execute_by_capability(self, capability_name: str, payload: Dict[str, Any]) -> ExecutionResult:
        tool = self.registry.find_by_capability(capability_name)
        if not tool:
            return ExecutionResult(False, error=f"Capability {capability_name} not found")
        return await self.execute(tool.name, payload)

    async def execute_batch(self, requests: List[Dict[str, Any]]) -> List[ExecutionResult]:
        tasks = []
        for req in requests:
            if 'tool_name' in req:
                tasks.append(self.execute(req['tool_name'], req['payload']))
            elif 'capability' in req:
                tasks.append(self.execute_by_capability(req['capability'], req['payload']))
            else:
                async def _fail():
                    return ExecutionResult(False, error='invalid request')
                tasks.append(_fail())
        return await asyncio.gather(*tasks)


def auto_register_existing_services(registry: ToolRegistry) -> Dict[str, Any]:
    # Register a minimal mock service to ensure some capabilities exist
    svc = BaseService("AutoRegistered")
    registry.register_base_service(svc)
    return {"registered": 1, "errors": []}


class UnifiedEcosystemContext:
    def __init__(self):
        self.registry = ToolRegistry()
        self.executor = UnifiedExecutor(self.registry)
        self.stats = {"registered": 0}

    async def __aenter__(self):
        # Auto-register minimal services
        stats = auto_register_existing_services(self.registry)
        self.stats.update(stats)
        return {"registry": self.registry, "executor": self.executor, "stats": self.stats}

    async def __aexit__(self, exc_type, exc, tb):
        return False


def unified_ecosystem():
    return UnifiedEcosystemContext()
