"""
TypedDict definitions for federated_learning_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class CheckAvailabilityResult(TypedDict, total=False):
    """Verificar disponibilidad del servicio"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSessionStatusResult(TypedDict, total=False):
    """Obtener estado de una sesión"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListSessionsResult(TypedDict, total=False):
    """Listar todas las sesiones"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSessionMetricsResult(TypedDict, total=False):
    """Obtener métricas detalladas de una sesión"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class StopSessionResult(TypedDict, total=False):
    """Detener una sesión activa"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

