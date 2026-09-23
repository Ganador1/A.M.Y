"""
Tests para Unified Tool Adapter Interface
Validación completa del ecosistema unificado AXIOM
"""

import asyncio
import pytest

from app.unified_tool_adapter import (
    UnifiedToolInterface,
    BaseServiceAdapter,
    ToolRegistry,
    UnifiedExecutor,
    ExecutionConfig,
    ExecutionResult,
    ToolCapability,
    ServiceStatus,
    CircuitBreaker,
    auto_register_existing_services,
    unified_ecosystem
)
from app.services.base_service import BaseService


class MockService(BaseService):
    """Mock service para testing"""
    
    def __init__(self, name="MockService", should_fail=False):
        super().__init__(name)
        self.should_fail = should_fail
        self.call_count = 0
        
    async def process_request(self, request_data):
        self.call_count += 1
        
        if self.should_fail:
            raise Exception("Mock service failure")
            
        action = request_data.get("action", "default")
        
        if action == "echo":
            return {"success": True, "message": request_data.get("message", "echo")}
        elif action == "slow":
            await asyncio.sleep(0.1)
            return {"success": True, "message": "slow response"}
        else:
            return {"success": True, "action": action}


class MockTool(UnifiedToolInterface):
    """Mock tool para testing"""
    
    def __init__(self, name="MockTool"):
        self.name = name
        self.call_count = 0
        
    async def run(self, payload):
        self.call_count += 1
        return {"success": True, "tool": self.name, "payload": payload}
        
    def get_capabilities(self):
        return [
            ToolCapability(
                name=f"{self.name}.test_capability",
                description="Test capability",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                tags={self.name.lower()}
            )
        ]


@pytest.mark.asyncio
class TestCircuitBreaker:
    """Tests para Circuit Breaker"""
    
    async def test_circuit_breaker_normal_operation(self):
        config = ExecutionConfig(failure_threshold=3, recovery_timeout_seconds=1)
        breaker = CircuitBreaker(config)
        
        async def success_func():
            return "success"
            
        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.status == ServiceStatus.HEALTHY
        
    async def test_circuit_breaker_opens_after_failures(self):
        config = ExecutionConfig(failure_threshold=2, recovery_timeout_seconds=1)
        breaker = CircuitBreaker(config)
        
        async def failing_func():
            raise Exception("Test failure")
            
        # Primera falla
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        assert breaker.status == ServiceStatus.DEGRADED
        
        # Segunda falla - debe abrir el circuit
        with pytest.raises(Exception):
            await breaker.call(failing_func)
        assert breaker.status == ServiceStatus.CIRCUIT_OPEN
        
        # Tercera llamada debe fallar inmediatamente
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await breaker.call(failing_func)


@pytest.mark.asyncio 
class TestBaseServiceAdapter:
    """Tests para BaseServiceAdapter"""
    
    async def test_adapter_success(self):
        service = MockService("TestService")
        adapter = BaseServiceAdapter(service)
        
        result = await adapter.run({"action": "echo", "message": "test"})
        
        assert result["success"] is True
        assert result["data"]["message"] == "test"
        assert result["service_name"] == "TestService"
        assert "execution_time_ms" in result
        
    async def test_adapter_failure(self):
        service = MockService("FailService", should_fail=True)
        adapter = BaseServiceAdapter(service)
        
        result = await adapter.run({"action": "test"})
        
        assert result["success"] is False
        assert "Mock service failure" in result["error"]
        assert result["service_name"] == "FailService"
        
    async def test_adapter_capabilities_discovery(self):
        service = MockService("TestService")
        adapter = BaseServiceAdapter(service)
        
        capabilities = adapter.get_capabilities()
        
        assert len(capabilities) > 0
        # Debe incluir la capacidad principal process_request
        main_cap = next((c for c in capabilities if c.name.endswith("process_request")), None)
        assert main_cap is not None
        assert "testservice" in main_cap.tags  # Tags are lowercased


class TestToolRegistry:
    """Tests para ToolRegistry"""
    
    def test_register_tool(self):
        registry = ToolRegistry()
        tool = MockTool("TestTool")
        
        registry.register_tool("test", tool)
        
        assert registry.get_tool("test") == tool
        assert len(registry.list_all_capabilities()) > 0
        
    def test_register_base_service(self):
        registry = ToolRegistry()
        service = MockService("TestService")
        
        registry.register_base_service(service)
        
        tool = registry.get_tool("TestService")
        assert tool is not None
        assert isinstance(tool, BaseServiceAdapter)
        
    def test_find_by_capability(self):
        registry = ToolRegistry()
        tool = MockTool("TestTool")
        registry.register_tool("test", tool)
        
        found_tool = registry.find_by_capability("TestTool.test_capability")
        assert found_tool == tool
        
    def test_find_by_tag(self):
        registry = ToolRegistry()
        tool = MockTool("TestTool")
        registry.register_tool("test", tool)
        
        found_tools = registry.find_by_tag("testtool")
        assert len(found_tools) == 1
        assert found_tools[0] == tool
        
    @pytest.mark.asyncio
    async def test_health_check_all(self):
        registry = ToolRegistry()
        tool = MockTool("TestTool")
        registry.register_tool("test", tool)
        
        health = await registry.health_check_all()
        
        assert "test" in health
        assert health["test"]["status"] == "healthy"


@pytest.mark.asyncio
class TestUnifiedExecutor:
    """Tests para UnifiedExecutor"""
    
    async def test_execute_by_name(self):
        registry = ToolRegistry()
        service = MockService("TestService")
        registry.register_base_service(service)
        
        executor = UnifiedExecutor(registry)
        result = await executor.execute("TestService", {"action": "echo", "message": "test"})
        
        assert result.success is True
        assert result.data["message"] == "test"  # Data contiene directamente la respuesta del service
        assert result.service_name == "TestService"
        
    async def test_execute_by_capability(self):
        registry = ToolRegistry()
        tool = MockTool("TestTool")
        registry.register_tool("test", tool)
        
        executor = UnifiedExecutor(registry)
        result = await executor.execute_by_capability("TestTool.test_capability", {"test": "data"})
        
        assert result.success is True
        assert result.data["tool"] == "TestTool"
        
    async def test_execute_not_found(self):
        registry = ToolRegistry()
        executor = UnifiedExecutor(registry)
        
        result = await executor.execute("NonExistent", {})
        
        assert result.success is False
        assert result.error and "not found" in result.error
        
    async def test_execute_with_timeout(self):
        registry = ToolRegistry()
        service = MockService("SlowService")
        registry.register_base_service(service)
        
        config = ExecutionConfig(timeout_seconds=1)  # 1s timeout
        executor = UnifiedExecutor(registry, config)
        
        # Crear un service que haga timeout
        class TimeoutService(BaseService):
            def __init__(self):
                super().__init__("TimeoutService")
                
            async def process_request(self, request_data):
                await asyncio.sleep(2)  # Mayor que timeout
                return {"success": True}
        
        timeout_service = TimeoutService()
        registry.register_base_service(timeout_service)
        
        result = await executor.execute("TimeoutService", {"action": "test"})
        
        assert result.success is False
        assert result.error and "Timeout" in result.error
        
    async def test_execute_with_retry(self):
        registry = ToolRegistry()
        
        # Service que falla las primeras 2 veces, luego funciona
        class FlakyService(BaseService):
            def __init__(self):
                super().__init__("FlakyService")
                self.attempts = 0
                
            async def process_request(self, request_data):
                self.attempts += 1
                if self.attempts < 3:
                    raise Exception("Flaky failure")
                return {"success": True, "attempts": self.attempts}
        
        service = FlakyService()
        
        # Registrar con config que deshabilite circuit breaker para este test
        adapter_config = ExecutionConfig(
            retry_attempts=3, 
            retry_delay_ms=10,
            circuit_breaker_enabled=False  # Deshabilitar circuit breaker
        )
        registry.register_base_service(service, adapter_config)
        
        config = ExecutionConfig(retry_attempts=3, retry_delay_ms=10)
        executor = UnifiedExecutor(registry, config)
        
        result = await executor.execute("FlakyService", {"action": "test"})
        
        assert result.success is True
        assert result.retry_count == 2  # Falló 2 veces antes de funcionar
        
    async def test_execute_batch(self):
        registry = ToolRegistry()
        service = MockService("TestService")
        tool = MockTool("TestTool")
        registry.register_base_service(service)
        registry.register_tool("test", tool)
        
        executor = UnifiedExecutor(registry)
        
        requests = [
            {"tool_name": "TestService", "payload": {"action": "echo", "message": "1"}},
            {"capability": "TestTool.test_capability", "payload": {"test": "2"}},
            {"invalid": "request"}  # Este debe fallar
        ]
        
        results = await executor.execute_batch(requests)
        
        assert len(results) == 3
        assert results[0].success is True
        assert results[1].success is True  
        assert results[2].success is False


@pytest.mark.asyncio
class TestAutoRegistration:
    """Tests para auto-registration de servicios"""
    
    async def test_auto_register_existing_services(self):
        # Clear registry primero
        test_registry = ToolRegistry()
        
        stats = await auto_register_existing_services(test_registry)
        
        assert stats["registered"] > 0
        assert isinstance(stats["errors"], list)
        
        # Verificar que algunos servicios conocidos están registrados
        capabilities = test_registry.list_all_capabilities()
        assert len(capabilities) > 0


@pytest.mark.asyncio
class TestUnifiedEcosystem:
    """Tests para el context manager del ecosistema"""
    
    async def test_unified_ecosystem_context(self):
        async with unified_ecosystem() as ecosystem:
            assert "registry" in ecosystem
            assert "executor" in ecosystem
            assert "stats" in ecosystem
            
            registry = ecosystem["registry"]
            executor = ecosystem["executor"]
            
            # Debe tener servicios auto-registrados
            capabilities = registry.list_all_capabilities()
            assert len(capabilities) > 0
            
            # Debe poder ejecutar algún servicio
            # (asumiendo que existe al menos un servicio funcional)
            if len(capabilities) > 0:
                result = await executor.execute_by_capability(
                    capabilities[0].name, 
                    {"action": "test"}
                )
                # No necesariamente debe funcionar, pero no debe explotar
                assert isinstance(result, ExecutionResult)


@pytest.mark.asyncio
class TestIntegration:
    """Tests de integración completa"""
    
    async def test_full_ecosystem_integration(self):
        """Test end-to-end del ecosistema unificado"""
        registry = ToolRegistry()
        
        # Registrar servicios de prueba
        service1 = MockService("Service1")
        service2 = MockService("Service2") 
        tool1 = MockTool("Tool1")
        
        registry.register_base_service(service1)
        registry.register_base_service(service2)
        registry.register_tool("tool1", tool1)
        
        executor = UnifiedExecutor(registry)
        
        # Test discovery de capacidades
        capabilities = registry.list_all_capabilities()
        assert len(capabilities) >= 3
        
        # Test ejecución paralela
        requests = [
            {"tool_name": "Service1", "payload": {"action": "echo", "message": "test1"}},
            {"tool_name": "Service2", "payload": {"action": "echo", "message": "test2"}},
            {"capability": "Tool1.test_capability", "payload": {"data": "test3"}}
        ]
        
        results = await executor.execute_batch(requests)
        
        assert len(results) == 3
        assert all(r.success for r in results)
        
        # Test health check
        health = await registry.health_check_all()
        assert len(health) == 3
        assert all(h["status"] == "healthy" for h in health.values())
        
        # Test búsqueda por tag
        service_tools = registry.find_by_tag("service1")
        assert len(service_tools) > 0
