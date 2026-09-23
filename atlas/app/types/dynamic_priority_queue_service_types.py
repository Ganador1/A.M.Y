"""
TypedDict definitions for dynamic_priority_queue_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Response type for process_request."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class StartQueueManagerResult(TypedDict, total=False):
    """Response type for start_queue_manager."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class StopQueueManagerResult(TypedDict, total=False):
    """Response type for stop_queue_manager."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CancelTaskResult(TypedDict, total=False):
    """Response type for cancel_task."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetTaskPredictionsResult(TypedDict, total=False):
    """Response type for get_task_predictions."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ValidateTaskResult(TypedDict, total=False):
    """Valida una tarea científica"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AssessQueueHealthResult(TypedDict, total=False):
    """Evalúa la salud general del sistema de colas"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TaskSummaryResult(TypedDict, total=False):
    """Crea resumen de una tarea"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckDependenciesResult(TypedDict, total=False):
    """Verifica estado de dependencias de una tarea"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

