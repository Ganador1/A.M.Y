"""
TypedDict definitions for advanced_earth_sciences router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class AdvancedEarthSciencesHealthResult(TypedDict, total=False):
    """Health check para ciencias de la tierra avanzadas"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSupportedModelsResult(TypedDict, total=False):
    """Response type for get_supported_models."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeClimateModelCmip6Result(TypedDict, total=False):
    """Response type for analyze_climate_model_cmip6."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ProcessSeismicEventsAdvancedResult(TypedDict, total=False):
    """Response type for process_seismic_events_advanced."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class OceanModelingAdvancedResult(TypedDict, total=False):
    """Response type for ocean_modeling_advanced."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class QuickClimateAnalysisResult(TypedDict, total=False):
    """Response type for quick_climate_analysis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

