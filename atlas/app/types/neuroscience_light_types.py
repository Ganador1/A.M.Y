"""
TypedDict definitions for neuroscience_light router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class FullAnalysisResult(TypedDict, total=False):
    """Response type for full_analysis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ConnectivityAdvancedResult(TypedDict, total=False):
    """Response type for connectivity_advanced."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class NeuroLightMetricsResult(TypedDict, total=False):
    """Métricas ligeras (dummy) del servicio Neuro Light para observabilidad básica"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class WholeBrainSimulationResult(TypedDict, total=False):
    """Response type for whole_brain_simulation."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class BrainNetworksAnalysisResult(TypedDict, total=False):
    """Response type for brain_networks_analysis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

