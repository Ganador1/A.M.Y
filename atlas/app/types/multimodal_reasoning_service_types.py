"""
TypedDict definitions for multimodal_reasoning_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class AnalyzeWithClaudeResult(TypedDict, total=False):
    """Analiza texto con Claude 3.5 Sonnet"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeWithGpt4Result(TypedDict, total=False):
    """Analiza texto con GPT-4"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeWithLocalModelsResult(TypedDict, total=False):
    """Análisis con modelos locales"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeImageLocallyResult(TypedDict, total=False):
    """Análisis local de imágenes"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class HealthCheckResult(TypedDict, total=False):
    """Verifica el estado del servicio"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

