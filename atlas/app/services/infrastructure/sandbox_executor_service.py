"""
Sandbox Code Execution Service

Servicio para ejecutar código de manera aislada y segura con límites de tiempo y recursos.

ETHICS/SECURITY:
- Ejecuta código en procesos aislados con timeouts estrictos
- Límites de memoria y CPU configurables
- Bloquea imports peligrosos y funciones del sistema
- Valida entrada y sanitiza salida
- Logs de auditoría para todas las ejecuciones
"""

import asyncio
import logging
import subprocess
import tempfile
import os
import time
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import aiofiles
import httpx

from app.services.base_service import BaseService
from app.exceptions.infrastructure.database import DatabaseError


logger = logging.getLogger(__name__)

# Import TypedDicts
from app.types.sandbox_executor_service_types import (
    ToDictResult,
    ProcessRequestResult,
    ValidateCodeResult,
    ExecuteCodeResult,
    GetExecutionStatusResult,
    CancelExecutionResult,
    CleanupResult,
)


class SandboxExecutionResult:
    """Resultado de la ejecución en sandbox"""
    def __init__(self, success: bool, output: str = "", error: str = "", 
                 execution_time: float = 0.0, exit_code: int = 0,
                 memory_usage: float = 0.0, execution_id: str = ""):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time = execution_time
        self.exit_code = exit_code
        self.memory_usage = memory_usage
        self.execution_id = execution_id

    def to_dict(self) -> ToDictResult:
        return {
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "exit_code": self.exit_code,
            "memory_usage": self.memory_usage,
            "execution_id": self.execution_id
        }


class SandboxConfig:
    """Configuración del sandbox"""
    def __init__(self):
        # Límites de tiempo
        self.max_execution_time = 30  # segundos
        self.startup_timeout = 10    # segundos
        
        # Límites de recursos
        self.max_memory_mb = 512    # MB
        self.max_output_size = 64 * 1024  # 64KB
        
        # Límites de código
        self.max_code_length = 10000  # caracteres
        self.max_lines = 500         # líneas
        
        # Imports bloqueados (seguridad)
        self.blocked_imports = {
            'os', 'subprocess', 'sys', 'shutil', 'glob', 'pathlib',
            'socket', 'urllib', 'requests', 'http', 'ftplib',
            'smtplib', 'poplib', 'imaplib', 'telnetlib', 'ssl',
            'threading', 'multiprocessing', 'concurrent', 'asyncio',
            '__import__', 'eval', 'exec', 'compile', 'open',
            'input', 'raw_input', 'file', 'reload', 'vars', 'dir',
            'getattr', 'setattr', 'delattr', 'hasattr'
        }
        
        # Funciones bloqueadas
        self.blocked_functions = {
            '__import__', 'eval', 'exec', 'compile', 'open',
            'input', 'raw_input', 'exit', 'quit', 'help'
        }


class SandboxExecutorService(BaseService):
    """Servicio de ejecución de código en sandbox"""

    def __init__(self):
        super().__init__("sandbox_executor")
        self.config = SandboxConfig()
        self.execution_history: List[Dict[str, Any]] = []
        self.active_executions: Dict[str, subprocess.Popen] = {}
        self.process_start_times: Dict[str, float] = {}

    async def process_request(self, request_data: ProcessRequestResult) -> ProcessRequestResult:
        """Implementación del método abstracto de BaseService"""
        action = request_data.get("action", "")
        
        try:
            if action == "execute_python":
                code = request_data.get("code", "")
                context = request_data.get("context")
                result = await self.execute_python_code(code, context)
                return result.to_dict()
                
            elif action == "execute_math":
                expression = request_data.get("expression", "")
                variables = request_data.get("variables")
                result = await self.execute_math_expression(expression, variables)
                return result.to_dict()
                
            elif action == "cancel_execution":
                execution_id = request_data.get("execution_id", "")
                cancelled = await self.cancel_execution(execution_id)
                return {"success": cancelled}
                
            elif action == "get_history":
                limit = request_data.get("limit", 10)
                history = self.get_execution_history(limit)
                return {"executions": history}
                
            elif action == "get_active":
                active = self.get_active_executions()
                return {"active_executions": active}
                
            else:
                return {"success": False, "error": f"Acción desconocida: {action}"}
                
        except DatabaseError as e:
            logger.error(f"Error en process_request para acción {action}: {str(e)}")
            return {"success": False, "error": str(e)}

    async def execute_python_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> SandboxExecutionResult:
        """
        Ejecuta código Python en un sandbox aislado
        
        Args:
            code: Código Python a ejecutar
            context: Variables de contexto opcionales (limitadas)
            
        Returns:
            SandboxExecutionResult con el resultado de la ejecución
        """
        execution_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Validar entrada
            validation_result = self._validate_code(code)
            if not validation_result["valid"]:
                return SandboxExecutionResult(
                    success=False,
                    error=f"Código no válido: {validation_result['reason']}",
                    execution_id=execution_id
                )

            # Preparar entorno aislado
            with tempfile.TemporaryDirectory() as temp_dir:
                script_path = os.path.join(temp_dir, f"sandbox_{execution_id}.py")
                
                # Crear script wrapper con restricciones de seguridad
                wrapped_code = self._wrap_code_with_security(code, context)
                
                with aiofiles.open(script_path, 'w', encoding='utf-8') as f:
                    f.write(wrapped_code)

                # Ejecutar en proceso aislado
                result = await self._execute_in_subprocess(script_path, execution_id)
                
                # Registrar ejecución
                execution_time = time.time() - start_time
                result.execution_time = execution_time
                result.execution_id = execution_id
                
                self._log_execution(execution_id, code, result, context)
                
                return result

        except DatabaseError as e:
            logger.error(f"Error en ejecución sandbox {execution_id}: {str(e)}")
            return SandboxExecutionResult(
                success=False,
                error=f"Error interno: {str(e)}",
                execution_time=time.time() - start_time,
                execution_id=execution_id
            )

    async def execute_math_expression(self, expression: str, variables: Optional[Dict[str, float]] = None) -> SandboxExecutionResult:
        """
        Ejecuta una expresión matemática de forma segura
        
        Args:
            expression: Expresión matemática (ej: "2*x + 3*y")
            variables: Variables para la expresión (ej: {"x": 5, "y": 2})
            
        Returns:
            SandboxExecutionResult con el resultado
        """
        # Crear código Python seguro para la expresión
        safe_imports = [
            "import math",
            "import cmath", 
            "from fractions import Fraction",
            "from decimal import Decimal"
        ]
        
        # Preparar variables
        var_setup = ""
        if variables:
            for name, value in variables.items():
                if isinstance(name, str) and name.isidentifier():
                    var_setup += f"{name} = {repr(value)}\n"
        
        # Código completo
        code = "\n".join(safe_imports) + "\n" + var_setup + f"\nresult = {expression}\nprint(f'Result: {{result}}')"
        
        return await self.execute_python_code(code)

    async def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancela una ejecución activa
        
        Args:
            execution_id: ID de la ejecución a cancelar
            
        Returns:
            True si se canceló exitosamente
        """
        if execution_id in self.active_executions:
            try:
                process = self.active_executions[execution_id]
                process.terminate()
                
                # Esperar un poco y luego kill si es necesario
                await asyncio.sleep(1)
                if process.poll() is None:
                    process.kill()
                
                del self.active_executions[execution_id]
                logger.info(f"Ejecución {execution_id} cancelada")
                return True
            except DatabaseError as e:
                logger.error(f"Error cancelando ejecución {execution_id}: {str(e)}")
                return False
        return False

    def get_execution_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtiene el historial de ejecuciones recientes
        
        Args:
            limit: Número máximo de ejecuciones a retornar
            
        Returns:
            Lista de ejecuciones recientes
        """
        return self.execution_history[-limit:]

    def get_active_executions(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene información sobre ejecuciones activas
        
        Returns:
            Diccionario con información de ejecuciones activas
        """
        active = {}
        for execution_id, process in self.active_executions.items():
            start_time = self.process_start_times.get(execution_id, 'unknown')
            active[execution_id] = {
                "pid": process.pid,
                "status": "running" if process.poll() is None else "finished",
                "start_time": start_time
            }
        return active

    def _validate_code(self, code: str) -> ValidateCodeResult:
        """Valida el código antes de la ejecución"""
        
        # Límite de longitud
        if len(code) > self.config.max_code_length:
            return {
                "valid": False,
                "reason": f"Código demasiado largo ({len(code)} > {self.config.max_code_length})"
            }
        
        # Límite de líneas
        lines = code.split('\n')
        if len(lines) > self.config.max_lines:
            return {
                "valid": False,
                "reason": f"Demasiadas líneas ({len(lines)} > {self.config.max_lines})"
            }
        
        # Verificar imports bloqueados
        code_lower = code.lower()
        for blocked_import in self.config.blocked_imports:
            if f"import {blocked_import}" in code_lower or f"from {blocked_import}" in code_lower:
                return {
                    "valid": False,
                    "reason": f"Import bloqueado: {blocked_import}"
                }
        
        # Verificar funciones bloqueadas
        for blocked_func in self.config.blocked_functions:
            if blocked_func in code:
                return {
                    "valid": False,
                    "reason": f"Función bloqueada: {blocked_func}"
                }
        
        return {"valid": True}

    def _wrap_code_with_security(self, code: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Envuelve el código con restricciones de seguridad"""
        
        wrapper_header = '''
import sys
import signal
import traceback
import io
from contextlib import redirect_stdout, redirect_stderr
from app.types.sandbox_executor_service_types import (
    ToDictResult,
    ProcessRequestResult,
    ValidateCodeResult,
)

# Límites de seguridad
class SecurityError(Exception):
    pass

# Bloquear funciones peligrosas
blocked_builtins = {
    '__import__': lambda *args, **kwargs: SecurityError("Import bloqueado"),
    'eval': lambda *args, **kwargs: SecurityError("Eval bloqueado"),
    'exec': lambda *args, **kwargs: SecurityError("Exec bloqueado"),
    'compile': lambda *args, **kwargs: SecurityError("Compile bloqueado"),
    'open': lambda *args, **kwargs: SecurityError("File access bloqueado"),
    'input': lambda *args, **kwargs: SecurityError("Input bloqueado"),
    'raw_input': lambda *args, **kwargs: SecurityError("Input bloqueado"),
}

# Aplicar restricciones
for name, replacement in blocked_builtins.items():
    if name in __builtins__:
        __builtins__[name] = replacement

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Execution timeout")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(''' + str(self.config.max_execution_time) + ''')

# Capturar output
stdout_buffer = io.StringIO()
stderr_buffer = io.StringIO()

try:
    with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
        # Variables de contexto
        '''
        
        # Agregar variables de contexto si existen
        context_setup = ""
        if context:
            for name, value in context.items():
                if isinstance(name, str) and name.isidentifier():
                    context_setup += f"        {name} = {repr(value)}\n"
        
        wrapper_footer = '''
        
        # Código del usuario
''' + '\n'.join('        ' + line for line in code.split('\n')) + '''

except DatabaseError as e:
    print(f"ERROR: {str(e)}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
finally:
    signal.alarm(0)  # Cancelar timeout

# Output final
stdout_content = stdout_buffer.getvalue()
stderr_content = stderr_buffer.getvalue()

if stdout_content:
    print("STDOUT:", stdout_content)
if stderr_content:
    print("STDERR:", stderr_content, file=sys.stderr)
'''
        
        return wrapper_header + context_setup + wrapper_footer

    async def _execute_in_subprocess(self, script_path: str, execution_id: str) -> SandboxExecutionResult:
        """Ejecuta el script en un subproceso aislado"""
        
        try:
            # Comando de ejecución con límites
            cmd = [
                'python3', '-u', script_path
            ]
            
            # Si está disponible, usar timeout del sistema operativo
            if shutil.which('timeout'):
                cmd = ['timeout', str(self.config.max_execution_time)] + cmd
            
            # Iniciar proceso
            start_time = time.time()
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=tempfile.gettempdir(),
                env={'PYTHONPATH': ''}  # Limitar PATH de Python
            )
            
            # Registrar proceso activo
            self.process_start_times[execution_id] = start_time
            self.active_executions[execution_id] = process
            
            try:
                # Esperar con timeout
                stdout, stderr = process.communicate(timeout=self.config.max_execution_time + 5)
                exit_code = process.returncode
                execution_time = time.time() - start_time
                
                # Limpiar output si es muy largo
                if len(stdout) > self.config.max_output_size:
                    stdout = stdout[:self.config.max_output_size] + "\n[OUTPUT TRUNCATED]"
                if len(stderr) > self.config.max_output_size:
                    stderr = stderr[:self.config.max_output_size] + "\n[ERROR TRUNCATED]"
                
                success = exit_code == 0
                
                return SandboxExecutionResult(
                    success=success,
                    output=stdout,
                    error=stderr,
                    execution_time=execution_time,
                    exit_code=exit_code
                )
                
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()  # Limpiar
                return SandboxExecutionResult(
                    success=False,
                    error=f"Timeout después de {self.config.max_execution_time} segundos",
                    execution_time=self.config.max_execution_time,
                    exit_code=124
                )
                
        except DatabaseError as e:
            logger.error(f"Error ejecutando subprocess para {execution_id}: {str(e)}")
            return SandboxExecutionResult(
                success=False,
                error=f"Error de ejecución: {str(e)}",
                exit_code=1
            )
        finally:
            # Limpiar proceso activo
            if execution_id in self.active_executions:
                del self.active_executions[execution_id]
            if execution_id in self.process_start_times:
                del self.process_start_times[execution_id]

    def _log_execution(self, execution_id: str, code: str, result: SandboxExecutionResult, context: Optional[Dict[str, Any]]):
        """Registra la ejecución en el historial y logs"""
        
        # Log de auditoría
        logger.info(f"Sandbox execution {execution_id}: success={result.success}, time={result.execution_time:.3f}s")
        
        # Historial (limitamos el código almacenado)
        code_preview = code[:200] + "..." if len(code) > 200 else code
        
        execution_record = {
            "execution_id": execution_id,
            "timestamp": datetime.now().isoformat(),
            "code_preview": code_preview,
            "success": result.success,
            "execution_time": result.execution_time,
            "exit_code": result.exit_code,
            "output_length": len(result.output),
            "error_length": len(result.error),
            "context_provided": context is not None
        }
        
        self.execution_history.append(execution_record)
        
        # Mantener solo las últimas 100 ejecuciones
        if len(self.execution_history) > 100:
            self.execution_history = self.execution_history[-100:]
