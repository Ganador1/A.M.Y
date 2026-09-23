"""
Modelos de response para el dominio Astronomy
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseResponse(BaseModel):
    """Modelo base para responses del dominio"""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None
    trace_id: Optional[str] = None


class TelescopeDataResponse(BaseResponse):
    """Response para análisis de datos telescópicos"""
    telescope_info: Dict[str, Any]
    data_summary: Dict[str, Any]
    processed_data: Optional[Dict[str, Any]] = None
    visualizations: List[str] = Field(default_factory=list)


class AstronomicalSimulationResponse(BaseResponse):
    """Response para simulaciones astronómicas"""
    simulation_id: str
    simulation_results: Dict[str, Any]
    performance_metrics: Dict[str, Any]
    output_files: List[str] = Field(default_factory=list)


class ExoplanetDetectionResponse(BaseResponse):
    """Response para detección de exoplanetas"""
    detection_results: Dict[str, Any]
    candidates: List[Dict[str, Any]] = Field(default_factory=list)
    statistical_significance: float
    detection_method: str


class GalaxyAnalysisResponse(BaseResponse):
    """Response para análisis de galaxias"""
    galaxy_properties: Dict[str, Any]
    morphological_parameters: Dict[str, Any]
    kinematic_analysis: Optional[Dict[str, Any]] = None
    derived_quantities: Dict[str, Any] = Field(default_factory=dict)


class CosmologicalAnalysisResponse(BaseResponse):
    """Response para análisis cosmológicos"""
    cosmological_parameters: Dict[str, Any]
    statistical_analysis: Dict[str, Any]
    model_comparison: Optional[Dict[str, Any]] = None
    confidence_intervals: Dict[str, Any] = Field(default_factory=dict)


class StarFormationResponse(BaseResponse):
    """Response para análisis de formación estelar"""
    star_formation_rate: float
    molecular_clouds: List[Dict[str, Any]] = Field(default_factory=list)
    stellar_populations: Dict[str, Any]
    environmental_analysis: Dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseResponse):
    """Response para errores"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None

