"""
TypedDict definitions for causal_discovery_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class CheckPositivityResult(TypedDict, total=False):
    """Verifica supuesto de positividad."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckOverlapResult(TypedDict, total=False):
    """Verifica supuesto de overlap."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckConfoundingResult(TypedDict, total=False):
    """Verifica supuesto de no confounding no medido."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckConsistencyResult(TypedDict, total=False):
    """Verifica supuesto de consistencia."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ComputeGraphStatisticsResult(TypedDict, total=False):
    """Calcula estadísticas del grafo causal."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Retorna información del servicio."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

