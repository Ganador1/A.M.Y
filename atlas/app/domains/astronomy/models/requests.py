"""
Modelos de request para el dominio Astronomy
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseRequest(BaseModel):
    """Modelo base para requests del dominio"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_context: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None


class TelescopeDataRequest(BaseRequest):
    """Request para análisis de datos telescópicos"""
    telescope_name: str = Field(..., description="Nombre del telescopio (HST, JWST, etc.)")
    data_type: str = Field(..., description="Tipo de datos (imaging, spectroscopy, photometry)")
    coordinates: Dict[str, Any] = Field(..., description="Coordenadas celestiales")
    observation_parameters: Dict[str, Any] = Field(default_factory=dict)


class AstronomicalSimulationRequest(BaseRequest):
    """Request para simulaciones astronómicas"""
    simulation_type: str = Field(..., description="Tipo de simulación (galaxy_formation, star_evolution, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    time_steps: int = Field(default=1000)
    spatial_resolution: float = Field(default=1.0)


class ExoplanetDetectionRequest(BaseRequest):
    """Request para detección de exoplanetas"""
    star_name: str = Field(..., description="Nombre de la estrella anfitriona")
    method: str = Field(default="transit", description="Método de detección")
    time_series_data: List[Dict[str, Any]] = Field(..., description="Datos de serie temporal")
    detection_parameters: Dict[str, Any] = Field(default_factory=dict)


class GalaxyAnalysisRequest(BaseRequest):
    """Request para análisis de galaxias"""
    galaxy_name: str = Field(..., description="Nombre o identificador de la galaxia")
    analysis_type: str = Field(..., description="Tipo de análisis (morphology, kinematics, etc.)")
    data_sources: List[str] = Field(..., description="Fuentes de datos a utilizar")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class CosmologicalAnalysisRequest(BaseRequest):
    """Request para análisis cosmológicos"""
    dataset: str = Field(..., description="Conjunto de datos (CMB, supernovae, etc.)")
    analysis_type: str = Field(..., description="Tipo de análisis (parameter_estimation, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class StarFormationRequest(BaseRequest):
    """Request para análisis de formación estelar"""
    region_coordinates: Dict[str, Any] = Field(..., description="Coordenadas de la región")
    data_sources: List[str] = Field(..., description="Fuentes de datos")
    analysis_parameters: Dict[str, Any] = Field(default_factory=dict)

