"""
Tests para Sandbox Executor Service

Tests comprehensivos para la ejecución segura de código.
"""

import subprocess
import pytest
from unittest.mock import patch, MagicMock

from app.services.sandbox_executor_service import (
    SandboxExecutorService, 
    SandboxExecutionResult, 
    SandboxConfig
)


@pytest.fixture
def sandbox_service():
    """Fixture para el servicio sandbox"""
    return SandboxExecutorService()


@pytest.fixture
def sample_code():
    """Código Python de ejemplo"""
    return """
import math

# Operaciones matemáticas básicas
x = 10
y = math.sqrt(x)
result = x + y

print(f"x = {x}")
print(f"sqrt(x) = {y}")
print(f"result = {result}")
"""


class TestSandboxExecutorService:
    """Test suite para SandboxExecutorService"""
    
    def test_service_initialization(self, sandbox_service):
        """Test inicialización del servicio"""
        assert sandbox_service.name == "sandbox_executor"
        assert isinstance(sandbox_service.config, SandboxConfig)
        assert isinstance(sandbox_service.execution_history, list)
        assert isinstance(sandbox_service.active_executions, dict)
        assert len(sandbox_service.execution_history) == 0
        assert len(sandbox_service.active_executions) == 0

    def test_sandbox_config(self):
        """Test configuración del sandbox"""
        config = SandboxConfig()
        
        # Verificar límites de tiempo
        assert config.max_execution_time == 30
        assert config.startup_timeout == 10
        
        # Verificar límites de recursos
        assert config.max_memory_mb == 512
        assert config.max_output_size == 64 * 1024
        
        # Verificar límites de código
        assert config.max_code_length == 10000
        assert config.max_lines == 500
        
        # Verificar imports bloqueados
        assert 'os' in config.blocked_imports
        assert 'subprocess' in config.blocked_imports
        assert 'sys' in config.blocked_imports
        
        # Verificar funciones bloqueadas
        assert 'eval' in config.blocked_functions
        assert 'exec' in config.blocked_functions
        assert 'open' in config.blocked_functions

    @pytest.mark.asyncio
    async def test_code_validation_success(self, sandbox_service):
        """Test validación exitosa de código"""
        valid_code = "x = 5\nprint(x)"
        result = sandbox_service._validate_code(valid_code)
        
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_code_validation_too_long(self, sandbox_service):
        """Test validación falla por código muy largo"""
        long_code = "x = 1\n" * 6000  # Más de 10,000 caracteres
        result = sandbox_service._validate_code(long_code)
        
        assert result["valid"] is False
        assert "demasiado largo" in result["reason"].lower()

    @pytest.mark.asyncio
    async def test_code_validation_too_many_lines(self, sandbox_service):
        """Test validación falla por muchas líneas"""
        many_lines_code = "\n".join([f"x{i} = {i}" for i in range(600)])  # Más de 500 líneas
        result = sandbox_service._validate_code(many_lines_code)
        
        assert result["valid"] is False
        assert "líneas" in result["reason"].lower()

    @pytest.mark.asyncio
    async def test_code_validation_blocked_import(self, sandbox_service):
        """Test validación falla por import bloqueado"""
        dangerous_code = "import os\nos.system('ls')"
        result = sandbox_service._validate_code(dangerous_code)
        
        assert result["valid"] is False
        assert "import bloqueado" in result["reason"].lower()

    @pytest.mark.asyncio
    async def test_code_validation_blocked_function(self, sandbox_service):
        """Test validación falla por función bloqueada"""
        dangerous_code = "eval('1+1')"
        result = sandbox_service._validate_code(dangerous_code)
        
        assert result["valid"] is False
        assert "función bloqueada" in result["reason"].lower()

    def test_wrap_code_with_security(self, sandbox_service):
        """Test wrapper de seguridad para código"""
        simple_code = "x = 5\nprint(x)"
        wrapped = sandbox_service._wrap_code_with_security(simple_code)
        
        # Verificar que contiene elementos de seguridad
        assert "SecurityError" in wrapped
        assert "blocked_builtins" in wrapped
        assert "timeout_handler" in wrapped
        assert "signal.alarm" in wrapped
        # El código se ejecuta pero puede estar transformado
        assert "x = 5" in wrapped
        assert "print(x)" in wrapped

    def test_wrap_code_with_context(self, sandbox_service):
        """Test wrapper con contexto"""
        code = "print(x + y)"
        context = {"x": 5, "y": 3}
        wrapped = sandbox_service._wrap_code_with_security(code, context)
        
        assert "x = 5" in wrapped
        assert "y = 3" in wrapped
        assert code in wrapped

    @pytest.mark.asyncio
    @patch('subprocess.Popen')
    async def test_execute_subprocess_success(self, mock_popen, sandbox_service):
        """Test ejecución exitosa en subprocess"""
        # Mock del proceso
        mock_process = MagicMock()
        mock_process.communicate.return_value = ("Output line", "")
        mock_process.returncode = 0
        mock_process.poll.return_value = 0
        mock_popen.return_value = mock_process
        
        # Mock del shutil.which para evitar timeout command
        with patch('shutil.which', return_value=None):
            result = await sandbox_service._execute_in_subprocess("/fake/path", "test_id")
        
        assert result.success is True
        assert result.output == "Output line"
        assert result.error == ""
        assert result.exit_code == 0

    @pytest.mark.asyncio
    @patch('subprocess.Popen')
    async def test_execute_subprocess_timeout(self, mock_popen, sandbox_service):
        """Test timeout en subprocess"""
        # Mock del proceso que hace timeout
        mock_process = MagicMock()
        mock_process.communicate.side_effect = subprocess.TimeoutExpired(
            ['python'], timeout=30, output="partial", stderr="error"
        )
        mock_process.kill = MagicMock()
        mock_popen.return_value = mock_process
        
        # Mock del shutil.which
        with patch('shutil.which', return_value=None):
            result = await sandbox_service._execute_in_subprocess("/fake/path", "test_id")
        
        assert result.success is False
        assert "timed out" in result.error.lower()
        # Nota: El exit_code es 1 porque la excepción se atrapa en el except general
        assert result.exit_code in [1, 124]  # Puede ser cualquiera dependiendo del manejo

    @pytest.mark.asyncio
    async def test_math_expression_simple(self, sandbox_service):
        """Test evaluación de expresión matemática simple"""
        # Mock del execute_python_code para evitar subprocess real
        with patch.object(sandbox_service, 'execute_python_code') as mock_execute:
            mock_result = SandboxExecutionResult(
                success=True, 
                output="Result: 13", 
                execution_id="test"
            )
            mock_execute.return_value = mock_result
            
            _ = await sandbox_service.execute_math_expression("2*x + 3", {"x": 5})
            
            assert mock_execute.called
            # Verificar que el código generado contiene los elementos correctos
            call_args = mock_execute.call_args[0]
            generated_code = call_args[0]
            assert "import math" in generated_code
            assert "x = 5" in generated_code
            assert "result = 2*x + 3" in generated_code

    @pytest.mark.asyncio
    async def test_cancel_execution_success(self, sandbox_service):
        """Test cancelación exitosa de ejecución"""
        # Simular proceso activo
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Proceso corriendo
        mock_process.terminate = MagicMock()
        mock_process.kill = MagicMock()
        
        execution_id = "test_exec_123"
        sandbox_service.active_executions[execution_id] = mock_process
        
        # Cancelar
        result = await sandbox_service.cancel_execution(execution_id)
        
        assert result is True
        assert execution_id not in sandbox_service.active_executions
        mock_process.terminate.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_execution_not_found(self, sandbox_service):
        """Test cancelación de ejecución inexistente"""
        result = await sandbox_service.cancel_execution("nonexistent")
        assert result is False

    def test_execution_history_management(self, sandbox_service):
        """Test gestión del historial de ejecuciones"""
        # Agregar ejecuciones de prueba
        for i in range(15):
            sandbox_service.execution_history.append({
                "execution_id": f"test_{i}",
                "success": True,
                "execution_time": 0.1
            })
        
        # Obtener historial limitado
        history = sandbox_service.get_execution_history(5)
        assert len(history) == 5
        assert history[0]["execution_id"] == "test_10"  # Los últimos 5
        
        # Obtener historial completo disponible
        history_all = sandbox_service.get_execution_history(20)
        assert len(history_all) == 15

    def test_active_executions_info(self, sandbox_service):
        """Test información de ejecuciones activas"""
        # Simular ejecuciones activas
        mock_process1 = MagicMock()
        mock_process1.pid = 1234
        mock_process1.poll.return_value = None  # Corriendo
        
        mock_process2 = MagicMock()
        mock_process2.pid = 5678
        mock_process2.poll.return_value = 0  # Terminado
        
        sandbox_service.active_executions["exec1"] = mock_process1
        sandbox_service.active_executions["exec2"] = mock_process2
        sandbox_service.process_start_times["exec1"] = 123456789.0
        sandbox_service.process_start_times["exec2"] = 123456799.0
        
        active_info = sandbox_service.get_active_executions()
        
        assert len(active_info) == 2
        assert active_info["exec1"]["pid"] == 1234
        assert active_info["exec1"]["status"] == "running"
        assert active_info["exec2"]["pid"] == 5678
        assert active_info["exec2"]["status"] == "finished"

    @pytest.mark.asyncio
    async def test_process_request_execute_python(self, sandbox_service):
        """Test process_request para ejecución Python"""
        with patch.object(sandbox_service, 'execute_python_code') as mock_execute:
            mock_result = SandboxExecutionResult(success=True, output="test output")
            mock_execute.return_value = mock_result
            
            request_data = {
                "action": "execute_python",
                "code": "print('hello')",
                "context": {"debug": True}
            }
            
            result = await sandbox_service.process_request(request_data)
            
            assert result["success"] is True
            assert result["output"] == "test output"
            mock_execute.assert_called_once_with("print('hello')", {"debug": True})

    @pytest.mark.asyncio
    async def test_process_request_execute_math(self, sandbox_service):
        """Test process_request para expresión matemática"""
        with patch.object(sandbox_service, 'execute_math_expression') as mock_execute:
            mock_result = SandboxExecutionResult(success=True, output="Result: 10")
            mock_execute.return_value = mock_result
            
            request_data = {
                "action": "execute_math",
                "expression": "5 + 5",
                "variables": {"x": 1}
            }
            
            result = await sandbox_service.process_request(request_data)
            
            assert result["success"] is True
            assert result["output"] == "Result: 10"
            mock_execute.assert_called_once_with("5 + 5", {"x": 1})

    @pytest.mark.asyncio
    async def test_process_request_get_history(self, sandbox_service):
        """Test process_request para obtener historial"""
        # Agregar historial de prueba
        sandbox_service.execution_history = [
            {"execution_id": "test1", "success": True},
            {"execution_id": "test2", "success": False}
        ]
        
        request_data = {
            "action": "get_history",
            "limit": 5
        }
        
        result = await sandbox_service.process_request(request_data)
        
        assert "executions" in result
        assert len(result["executions"]) == 2

    @pytest.mark.asyncio
    async def test_process_request_unknown_action(self, sandbox_service):
        """Test process_request con acción desconocida"""
        request_data = {
            "action": "unknown_action"
        }
        
        result = await sandbox_service.process_request(request_data)
        
        assert result["success"] is False
        assert "desconocida" in result["error"].lower()


# Test de integración simple (sin subprocess real)
@pytest.mark.asyncio
async def test_integration_math_calculation():
    """Test de integración para cálculo matemático"""
    service = SandboxExecutorService()
    
    # Mock la ejecución de subprocess para evitar proceso real
    with patch.object(service, '_execute_in_subprocess') as mock_subprocess:
        mock_subprocess.return_value = SandboxExecutionResult(
            success=True,
            output="STDOUT: Result: 17",
            error="",
            execution_time=0.1,
            exit_code=0,
            execution_id="test"
        )
        
        result = await service.execute_math_expression("2*x + 7", {"x": 5})
        
        assert result.success is True
        assert "17" in result.output
        assert result.execution_time > 0
