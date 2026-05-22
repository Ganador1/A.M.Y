"""
🛡️ Ejecutor de Código en Sandbox Seguro

Este módulo proporciona endpoints para la ejecución segura e aislada de código Python
y expresiones matemáticas en un entorno sandbox controlado, diseñado específicamente
para investigación científica y computación segura en AXIOM.

Características principales:
- 🔒 **Ejecución aislada**: Entorno sandbox con restricciones de seguridad estrictas
- 🐍 **Código Python**: Ejecución de scripts Python con límites de tiempo y memoria
- 🔢 **Expresiones matemáticas**: Evaluación segura de fórmulas matemáticas complejas
- 📊 **Monitoreo detallado**: Seguimiento de uso de recursos y tiempos de ejecución
- 🚫 **Bloqueo de funciones peligrosas**: Prevención de acceso al sistema y operaciones inseguras
- 📝 **Historial de ejecuciones**: Registro completo de todas las ejecuciones realizadas
- ⚡ **Ejecución asíncrona**: Soporte para operaciones en segundo plano
- 🛑 **Cancelación de procesos**: Capacidad para detener ejecuciones activas

Restricciones de seguridad implementadas:
- Timeout máximo de 30 segundos por ejecución
- Límite de memoria de 512MB por proceso
- Bloqueo de imports peligrosos (os, subprocess, sys, socket, etc.)
- Deshabilitación de funciones críticas (eval, exec, open, input, etc.)
- Truncado automático de output a 64KB
- Límite de 10,000 caracteres por código Python
- Máximo 1,000 líneas de output

Funciones matemáticas disponibles:
- Módulo math completo (sin, cos, tan, sqrt, log, exp, etc.)
- Módulo cmath para números complejos
- Tipos Fraction y Decimal para precisión arbitraria
- Operadores matemáticos estándar (+, -, *, /, **, %)

El sandbox utiliza técnicas avanzadas de aislamiento para garantizar que el código
ejecutado no pueda afectar el sistema host ni comprometer la seguridad de AXIOM.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
Version: 4.1
"""

import logging
import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, Optional, List
import aiofiles

from app.services.sandbox_executor_service import SandboxExecutorService
from app.security import require_scopes
from app.exceptions.infrastructure.database import DatabaseError

# Configure logging
logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(
    prefix="/api/v1/sandbox",
    tags=["sandbox", "code-execution", "security"],
    dependencies=[Depends(require_scopes(["sandbox:execute"]))]
)

# Service instance
_sandbox_service: Optional[SandboxExecutorService] = None


def get_sandbox_service() -> SandboxExecutorService:
    """Get or create sandbox service instance"""
    global _sandbox_service
    if _sandbox_service is None:
        _sandbox_service = SandboxExecutorService()
    return _sandbox_service


# Pydantic Models
class PythonCodeRequest(BaseModel):
    """Request para ejecutar código Python"""
    code: str = Field(..., description="Código Python a ejecutar", max_length=10000)
    context: Optional[Dict[str, Any]] = Field(None, description="Variables de contexto opcionales")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "import math\nx = 5\ny = math.sqrt(x)\nprint(f'sqrt({x}) = {y}')",
                "context": {"debug": True}
            }
        }
    )


class MathExpressionRequest(BaseModel):
    """Request para evaluar expresión matemática"""
    expression: str = Field(..., description="Expresión matemática", max_length=1000)
    variables: Optional[Dict[str, float]] = Field(None, description="Variables de la expresión")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "expression": "2*x + 3*y + math.sin(z)",
                "variables": {"x": 5, "y": 2, "z": 1.57}
            }
        }
    )


class ExecutionResponse(BaseModel):
    """Response de ejecución"""
    success: bool
    output: str
    error: str
    execution_time: float
    exit_code: int
    memory_usage: float
    execution_id: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "success": True,
                "output": "sqrt(5) = 2.23606797749979",
                "error": "",
                "execution_time": 0.125,
                "exit_code": 0,
                "memory_usage": 0.0,
                "execution_id": "550e8400-e29b-41d4-a716-446655440000"
            }
        }
    )


class ExecutionHistoryResponse(BaseModel):
    """Response del historial de ejecuciones"""
    executions: List[Dict[str, Any]]
    total_count: int


class ActiveExecutionsResponse(BaseModel):
    """Response de ejecuciones activas"""
    active_executions: Dict[str, Dict[str, Any]]
    count: int


# Endpoints
@router.post("/python", response_model=ExecutionResponse, dependencies=[Depends(require_scopes(["sandbox:execute"]))])
async def execute_python_code(request: PythonCodeRequest) -> ExecutionResponse:
    """
    🐍 Ejecuta código Python en entorno sandbox seguro

    Ejecuta código Python de manera aislada y segura con restricciones estrictas
    para prevenir acceso al sistema y operaciones peligrosas, ideal para
    prototipado y validación de algoritmos científicos.

    Args:
        request: Código Python y contexto opcional para ejecución

    Returns:
        ExecutionResponse: Resultado de la ejecución con output, errores y métricas

    Raises:
        HTTPException: Si hay error de validación o ejecución

    Example:
        POST /python
        {
            "code": "import math\\nx = 5\\ny = math.sqrt(x)\\nprint(f'sqrt({x}) = {y}')",
            "context": {"debug": true}
        }

    Restricciones de seguridad:
    - Timeout máximo: 30 segundos
    - Memoria máxima: 512MB
    - Output máximo: 64KB
    - Código máximo: 10,000 caracteres
    - Imports bloqueados: os, subprocess, sys, socket, etc.
    - Funciones bloqueadas: eval, exec, open, input, etc.
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not request.code or not request.code.strip():
            logger.warning("🚫 Código Python vacío o inválido")
            raise HTTPException(
                status_code=400,
                detail="code es requerido y no puede estar vacío"
            )

        code_length = len(request.code.strip())
        if code_length > 10000:
            logger.warning("🚫 Código Python demasiado largo: %d caracteres", code_length)
            raise HTTPException(
                status_code=400,
                detail=f"Código demasiado largo ({code_length} caracteres). Máximo permitido: 10,000"
            )

        # Validar que no contenga imports peligrosos básicos
        dangerous_imports = ['import os', 'import subprocess', 'import sys', 'import socket',
                           'from os', 'from subprocess', 'from sys', 'from socket']
        code_lower = request.code.lower()
        for dangerous in dangerous_imports:
            if dangerous in code_lower:
                logger.warning("🚫 Intento de importar módulo peligroso: %s", dangerous)
                raise HTTPException(
                    status_code=403,
                    detail=f"Import no permitido detectado: {dangerous}"
                )

        # Validar funciones peligrosas
        dangerous_functions = ['eval(', 'exec(', 'aiofiles.open(', 'input(', '__import__(']
        for dangerous in dangerous_functions:
            if dangerous in request.code:
                logger.warning("🚫 Función peligrosa detectada: %s", dangerous)
                raise HTTPException(
                    status_code=403,
                    detail=f"Función no permitida detectada: {dangerous}"
                )

        logger.info("🐍 Iniciando ejecución de código Python (%d caracteres)", code_length)
        if request.context:
            logger.info("📊 Contexto proporcionado con %d variables", len(request.context))

        # Ejecutar código
        service = get_sandbox_service()
        result = await service.execute_python_code(request.code, request.context)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        response_dict = result.to_dict()
        response_dict["metadata"] = {
            "total_execution_time_seconds": execution_time,
            "code_length": code_length,
            "has_context": request.context is not None,
            "timestamp": datetime.datetime.now().isoformat(),
            "execution_type": "python_code"
        }

        logger.info("✅ Código Python ejecutado exitosamente (tiempo: %.4fs, exit_code: %d)",
                   execution_time, response_dict.get("exit_code", -1))

        return ExecutionResponse(**response_dict)

    except HTTPException:
        raise
    except DatabaseError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error interno en ejecución de código Python: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en ejecución: {str(e)}"
        ) from e


@router.post("/math", response_model=ExecutionResponse, dependencies=[Depends(require_scopes(["sandbox"]))])
async def evaluate_math_expression(request: MathExpressionRequest):
    """
    Evalúa una expresión matemática de forma segura

    - **expression**: Expresión matemática (ej: "2*x + 3*y + math.sin(z)")
    - **variables**: Variables para la expresión (ej: {"x": 5, "y": 2, "z": 1.57})

    Funciones matemáticas disponibles:
    - Funciones básicas: +, -, *, /, **, %
    - math.*: sin, cos, tan, sqrt, log, exp, etc.
    - cmath.*: funciones complejas
    - Fraction, Decimal para cálculos precisos
    """
    try:
        service = get_sandbox_service()
        result = await service.execute_math_expression(request.expression, request.variables)

        return ExecutionResponse(**result.to_dict())

    except DatabaseError as e:
        logger.error(f"Error en evaluación matemática: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete("/executions/{execution_id}", dependencies=[Depends(require_scopes(["sandbox"]))])
async def cancel_execution(execution_id: str):
    """
    Cancela una ejecución activa

    - **execution_id**: ID de la ejecución a cancelar

    Returns:
        Status de la cancelación
    """
    try:
        service = get_sandbox_service()
        cancelled = await service.cancel_execution(execution_id)

        if cancelled:
            return {"success": True, "message": f"Ejecución {execution_id} cancelada"}
        else:
            raise HTTPException(status_code=404, detail="Ejecución no encontrada o ya terminada")

    except HTTPException:
        raise
    except DatabaseError as e:
        logger.error(f"Error cancelando ejecución {execution_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/executions/history", response_model=ExecutionHistoryResponse, dependencies=[Depends(require_scopes(["sandbox"]))])
async def get_execution_history(limit: int = 10):
    """
    Obtiene el historial de ejecuciones recientes

    - **limit**: Número máximo de ejecuciones a retornar (por defecto 10, máximo 50)
    """
    try:
        if limit > 50:
            limit = 50
        if limit < 1:
            limit = 1

        service = get_sandbox_service()
        history = service.get_execution_history(limit)

        return ExecutionHistoryResponse(
            executions=history,
            total_count=len(history)
        )

    except DatabaseError as e:
        logger.error(f"Error obteniendo historial: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/executions/active", response_model=ActiveExecutionsResponse, dependencies=[Depends(require_scopes(["sandbox"]))])
async def get_active_executions():
    """
    Obtiene información sobre ejecuciones activas

    Returns:
        Información de todas las ejecuciones que están corriendo actualmente
    """
    try:
        service = get_sandbox_service()
        active = service.get_active_executions()

        return ActiveExecutionsResponse(
            active_executions=active,
            count=len(active)
        )

    except DatabaseError as e:
        logger.error(f"Error obteniendo ejecuciones activas: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/config", dependencies=[Depends(require_scopes(["sandbox"]))])
async def get_sandbox_config():
    """
    Obtiene la configuración actual del sandbox

    Returns:
        Configuración de límites y restricciones del sandbox
    """
    try:
        service = get_sandbox_service()
        config = service.config

        return {
            "max_execution_time": config.max_execution_time,
            "startup_timeout": config.startup_timeout,
            "max_memory_mb": config.max_memory_mb,
            "max_output_size": config.max_output_size,
            "max_code_length": config.max_code_length,
            "max_lines": config.max_lines,
            "blocked_imports_count": len(config.blocked_imports),
            "blocked_functions_count": len(config.blocked_functions)
        }

    except DatabaseError as e:
        logger.error(f"Error obteniendo configuración: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get("/health", dependencies=[Depends(require_scopes(["sandbox"]))])
async def health_check():
    """
    Verifica el estado del servicio sandbox

    Returns:
        Estado de salud del servicio
    """
    try:
        service = get_sandbox_service()
        active_count = len(service.get_active_executions())
        history_count = len(service.execution_history)

        return {
            "status": "healthy",
            "service": "sandbox_executor",
            "active_executions": active_count,
            "total_executions": history_count,
            "config": {
                "max_execution_time": service.config.max_execution_time,
                "max_memory_mb": service.config.max_memory_mb
            }
        }

    except DatabaseError as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            "status": "unhealthy",
            "service": "sandbox_executor",
            "error": str(e)
        }


@router.post("/demo", dependencies=[Depends(require_scopes(["sandbox"]))])
async def demo_execution():
    """
    Ejecuta una demostración del sandbox

    Returns:
        Resultado de una ejecución de demostración
    """
    demo_code = """
import math

# Cálculos matemáticos seguros
numbers = [1, 2, 3, 4, 5]
sum_numbers = sum(numbers)
mean = sum_numbers / len(numbers)

# Operaciones matemáticas
result = math.sqrt(25) + math.sin(math.pi/2)

print(f"Números: {numbers}")
print(f"Suma: {sum_numbers}")
print(f"Promedio: {mean}")
print(f"sqrt(25) + sin(π/2) = {result}")
print("Demo completada exitosamente!")
"""

    try:
        service = get_sandbox_service()
        result = await service.execute_python_code(demo_code)

        return {
            "demo": "Sandbox execution demo",
            "result": result.to_dict(),
            "message": "Demo ejecutada exitosamente"
        }

    except DatabaseError as e:
        logger.error(f"Error en demo: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en demo: {str(e)}")
