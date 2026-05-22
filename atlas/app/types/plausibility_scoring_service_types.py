"""
TypedDict definitions for plausibility_scoring_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class HeuristicScoreResult(TypedDict, total=False):
    """Response type for _heuristic_score."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetFeatureImportanceResult(TypedDict, total=False):
    """Obtener importancia de características usando SHAP y feature importance"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExplainPredictionResult(TypedDict, total=False):
    """Explicar predicción individual con análisis detallado"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetModelStatisticsResult(TypedDict, total=False):
    """Obtener estadísticas del modelo y rendimiento"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AddReferenceHypothesisResult(TypedDict, total=False):
    """Response type for add_reference_hypothesis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

