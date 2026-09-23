"""
TypedDict definitions for circuit_breaker_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetStatsResult(TypedDict, total=False):
    """Obtener estadísticas del circuit breaker"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Get information about circuit breaker service"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CacheFallbackResult(TypedDict, total=False):
    """Fallback que retorna datos cacheados"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DefaultResponseFallbackResult(TypedDict, total=False):
    """Fallback que retorna respuesta por defecto"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DegradedServiceFallbackResult(TypedDict, total=False):
    """Fallback que proporciona servicio degradado"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetAllStatsResult(TypedDict, total=False):
    """Obtener estadísticas de todos los circuit breakers"""
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

