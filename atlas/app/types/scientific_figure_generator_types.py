"""
TypedDict definitions for scientific_figure_generator router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process figure generation requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateFigureResult(TypedDict, total=False):
    """Generate a scientific figure based on type and data"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GeneratePlotResult(TypedDict, total=False):
    """Convenience method for generating plots"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateDiagramResult(TypedDict, total=False):
    """Convenience method for generating diagrams"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateFlowchartResult(TypedDict, total=False):
    """Convenience method for generating flowcharts"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateHeatmapResult(TypedDict, total=False):
    """Convenience method for generating heatmaps"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateNetworkResult(TypedDict, total=False):
    """Convenience method for generating network diagrams"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

