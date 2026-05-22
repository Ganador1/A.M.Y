"""
TypedDict definitions for statistical_validation_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process statistical validation requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckAvailabilityResult(TypedDict, total=False):
    """Verificar disponibilidad de dependencias estadísticas"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CheckTestAssumptionsResult(TypedDict, total=False):
    """Verificar supuestos estadísticos para el test"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CalculateEffectSizeResult(TypedDict, total=False):
    """Calcular tamaño del efecto"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class InterpretTestResultsResult(TypedDict, total=False):
    """Interpretar resultados del test estadístico"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CalculateStatisticalPowerResult(TypedDict, total=False):
    """Calcular poder estadístico post-hoc"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackHypothesisTestResult(TypedDict, total=False):
    """Fallback para tests de hipótesis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackPowerAnalysisResult(TypedDict, total=False):
    """Fallback para análisis de poder"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackBiasDetectionResult(TypedDict, total=False):
    """Fallback para detección de sesgos"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackCrossValidationResult(TypedDict, total=False):
    """Fallback para validación cruzada"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackBayesianAnalysisResult(TypedDict, total=False):
    """Fallback para análisis bayesiano"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackMultipleComparisonsResult(TypedDict, total=False):
    """Fallback para corrección de múltiples comparaciones"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Obtener información del servicio"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

