"""
TypedDict definitions for cost_metrics_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetServiceInfoResult(TypedDict, total=False):
    """Get information about cost metrics service"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetBudgetStatusResult(TypedDict, total=False):
    """Obtener estado de presupuestos"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class HealthCheckResult(TypedDict, total=False):
    """Realizar health check del servicio"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

