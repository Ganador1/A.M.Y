"""
TypedDict definitions for earth_sciences_light router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ClimateTimeseriesResult(TypedDict, total=False):
    """Response type for climate_timeseries."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SeismicAnalysisResult(TypedDict, total=False):
    """Response type for seismic_analysis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class OceanStatsResult(TypedDict, total=False):
    """Response type for ocean_stats."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ClimateFromFileResult(TypedDict, total=False):
    """Response type for climate_from_file."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SeismicPsdResult(TypedDict, total=False):
    """Response type for seismic_psd."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DetectEddies2dResult(TypedDict, total=False):
    """Response type for detect_eddies_2d."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class MapHeatResult(TypedDict, total=False):
    """Genera un heatmap base64 PNG desde una grilla 2D (visualización ligera)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class MapCurrentsResult(TypedDict, total=False):
    """Genera un mapa quiver (corrientes) en PNG base64 (visualización ligera)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class MapHeatCurrentsResult(TypedDict, total=False):
    """Genera una figura combinada (heatmap + quiver) y devuelve PNG base64."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class EarthLightHistoryResult(TypedDict, total=False):
    """Devuelve las últimas N solicitudes procesadas (buffer circular)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class EarthLightHealthResult(TypedDict, total=False):
    """Health check ligero del servicio Earth Sciences Light"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class EarthLightMetricsResult(TypedDict, total=False):
    """Métricas ligeras (dummy) del servicio Earth Sciences Light"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

