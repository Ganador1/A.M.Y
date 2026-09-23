"""
TypedDict definitions for sandbox_executor_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, Any


class ToDictResult(TypedDict, total=False):
    """Response type for to_dict."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ProcessRequestResult(TypedDict, total=False):
    """Implementación del método abstracto de BaseService"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ValidateCodeResult(TypedDict, total=False):
    """Valida el código antes de la ejecución"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExecuteCodeResult(TypedDict, total=False):
    """Ejecuta código en sandbox"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure with stdout, stderr, exit_code
    error: str
    timestamp: str
    stdout: str
    stderr: str
    exit_code: int


class GetExecutionStatusResult(TypedDict, total=False):
    """Obtiene el estado de una ejecución"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify execution status data
    error: str
    timestamp: str
    status: str
    running: bool


class CancelExecutionResult(TypedDict, total=False):
    """Resultado de cancelar una ejecución activa"""
    success: bool
    message: str
    error: str
    timestamp: str
    execution_id: str
    cancelled: bool


class CleanupResult(TypedDict, total=False):
    """Resultado de limpieza de artefactos/recursos del sandbox"""
    success: bool
    message: str
    error: str
    timestamp: str
    details: Dict[str, Any]
    cleaned_items: int

