"""
Advanced Earth Sciences Router

Este módulo proporciona endpoints para análisis avanzado de ciencias de la tierra, incluyendo
modelado climático, sismología y oceanografía. Soporta análisis de modelos CMIP6, procesamiento
de eventos sísmicos, modelado oceanográfico con detección de eddies, evaluación de riesgos
de tsunami y análisis de eventos climáticos extremos.

Capacidades principales:
- Análisis de modelos climáticos CMIP6 con múltiples escenarios y variables
- Procesamiento avanzado de eventos sísmicos y análisis de terremotos
- Modelado oceanográfico con detección de eddies y análisis de corrientes
- Detección de ondas de calor marinas y evaluación de productividad primaria
- Evaluación de riesgo de tsunami y análisis de eventos climáticos extremos
- Análisis de tendencias climáticas regionales e históricos
- Monitoreo ambiental en tiempo real y pronósticos

Endpoints disponibles:
- GET /health: Verificación del estado del servicio
- GET /supported-models: Modelos climáticos y análisis soportados
- POST /climate-model/cmip6: Análisis de modelo climático CMIP6
- POST /seismic/advanced-analysis: Procesamiento avanzado de eventos sísmicos
- POST /ocean/advanced-modeling: Modelado oceanográfico avanzado
- GET /analysis-history: Historial de análisis de ciencias de la tierra
- POST /quick/climate-analysis: Análisis climático rápido
- POST /quick/seismic-monitoring: Monitoreo sísmico rápido
- POST /quick/ocean-currents: Análisis rápido de corrientes oceánicas
- POST /quick/marine-heatwave-detection: Detección rápida de ondas de calor marinas
- POST /climate/temperature-trends: Análisis de tendencias de temperatura
- POST /seismic/tsunami-risk: Evaluación de riesgo de tsunami
- POST /ocean/eddy-detection: Detección de eddies oceánicos
- POST /climate/extreme-events: Análisis de eventos extremos climáticos
- POST /ocean/productivity-analysis: Análisis de productividad primaria oceánica

Dependencias:
- AdvancedEarthSciencesService: Servicio principal de ciencias de la tierra
- RegionBounds: Modelo para límites regionales de análisis
- ClimateModelRequest: Solicitud de análisis de modelo climático
- SeismicAnalysisRequest: Solicitud de análisis sísmico
- OceanModelingRequest: Solicitud de modelado oceanográfico

Uso típico:
    from app.routers.advanced_earth_sciences import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /api/advanced-earth-sciences
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.advanced_earth_sciences_service import AdvancedEarthSciencesService
from app.types.advanced_earth_sciences_types import (
    AdvancedEarthSciencesHealthResult,
    GetSupportedModelsResult,
    AnalyzeClimateModelCmip6Result,
    ProcessSeismicEventsAdvancedResult,
    OceanModelingAdvancedResult,
    QuickClimateAnalysisResult,
)


router = APIRouter(prefix="/api/advanced-earth-sciences", tags=["advanced-earth-sciences"])


class RegionBounds(BaseModel):
    lat_min: float = Field(..., ge=-90, le=90, description="Latitud mínima")
    lat_max: float = Field(..., ge=-90, le=90, description="Latitud máxima")
    lon_min: float = Field(..., ge=-180, le=180, description="Longitud mínima")
    lon_max: float = Field(..., ge=-180, le=180, description="Longitud máxima")


class ClimateModelRequest(BaseModel):
    model_name: str = Field(..., description="Nombre del modelo climático")
    scenario: str = Field(..., description="Escenario climático (SSP)")
    region: Optional[RegionBounds] = Field(None, description="Región de análisis")
    start_year: str = Field("2020", description="Año de inicio")
    end_year: str = Field("2100", description="Año final")
    variables: Optional[List[str]] = Field(None, description="Variables a analizar")


class SeismicAnalysisRequest(BaseModel):
    min_magnitude: float = Field(4.0, ge=0, le=10, description="Magnitud mínima")
    max_magnitude: float = Field(8.0, ge=0, le=10, description="Magnitud máxima")
    time_window_hours: int = Field(24, ge=1, le=8760, description="Ventana temporal en horas")
    region: Optional[RegionBounds] = Field(None, description="Región de análisis")
    analysis_types: List[str] = Field(
        ["magnitude_estimation", "location_refinement"], 
        description="Tipos de análisis sísmico"
    )


class OceanModelingRequest(BaseModel):
    region: RegionBounds
    analysis_type: str = Field("regional", description="Tipo de análisis oceanográfico")
    time_span_days: int = Field(30, ge=1, le=365, description="Período de análisis en días")
    variables: Optional[List[str]] = Field(None, description="Variables oceanográficas")
    include_eddies: bool = Field(True, description="Incluir detección de eddies")
    include_fronts: bool = Field(True, description="Incluir detección de frentes")


@router.get("/health")
async def advanced_earth_sciences_health() -> AdvancedEarthSciencesHealthResult:
    """Health check para ciencias de la tierra avanzadas"""
    return {
        "service": "AdvancedEarthSciences",
        "status": "operational",
        "simulation_mode": True,
        "models_available": 3
    }


@router.get("/supported-models")
async def get_supported_models() -> GetSupportedModelsResult:
    """
    Obtiene modelos climáticos y análisis soportados
    """
    service = AdvancedEarthSciencesService()
    return await service.get_supported_models()


@router.post("/climate-model/cmip6")
async def analyze_climate_model_cmip6(req: ClimateModelRequest) -> AnalyzeClimateModelCmip6Result:
    """
    Ejecuta análisis de modelo climático CMIP6
    """
    service = AdvancedEarthSciencesService()
    
    # Convertir region a dict si existe
    region = None
    if req.region:
        region = {
            'lat_min': req.region.lat_min,
            'lat_max': req.region.lat_max,
            'lon_min': req.region.lon_min,
            'lon_max': req.region.lon_max
        }
    
    return await service.analyze_climate_model_cmip6(
        req.model_name, 
        req.scenario, 
        region, 
        (req.start_year, req.end_year)
    )


@router.post("/seismic/advanced-analysis")
async def process_seismic_events_advanced(req: SeismicAnalysisRequest) -> ProcessSeismicEventsAdvancedResult:
    """
    Ejecuta procesamiento avanzado de eventos sísmicos
    """
    service = AdvancedEarthSciencesService()
    
    # Convertir request a dict
    event_criteria = {
        'min_magnitude': req.min_magnitude,
        'max_magnitude': req.max_magnitude,
        'time_window_hours': req.time_window_hours
    }
    
    if req.region:
        event_criteria['region'] = {
            'lat_min': req.region.lat_min,
            'lat_max': req.region.lat_max,
            'lon_min': req.region.lon_min,
            'lon_max': req.region.lon_max
        }
    
    return await service.process_seismic_events_advanced(event_criteria, req.analysis_types)


@router.post("/ocean/advanced-modeling")
async def ocean_modeling_advanced(req: OceanModelingRequest) -> OceanModelingAdvancedResult:
    """
    Ejecuta modelado oceanográfico avanzado
    """
    service = AdvancedEarthSciencesService()
    
    # Convertir region a dict
    region = {
        'lat_min': req.region.lat_min,
        'lat_max': req.region.lat_max,
        'lon_min': req.region.lon_min,
        'lon_max': req.region.lon_max
    }
    
    return await service.ocean_modeling_advanced(region, req.analysis_type, req.time_span_days)


@router.get("/analysis-history")
async def get_analysis_history(limit: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    """
    Obtiene historial de análisis de ciencias de la tierra
    """
    service = AdvancedEarthSciencesService()
    return await service.get_analysis_history(limit)


# Endpoints simplificados para análisis rápidos
@router.post("/quick/climate-analysis")
async def quick_climate_analysis(model: str = "CESM2", scenario: str = "SSP245") -> QuickClimateAnalysisResult:
    """
    Análisis climático rápido (shortcut)
    """
    service = AdvancedEarthSciencesService()
    return await service.analyze_climate_model_cmip6(model, scenario)


@router.post("/quick/seismic-monitoring")
async def quick_seismic_monitoring(min_magnitude: float = 5.0, 
                                 hours: int = 24) -> Dict[str, Any]:
    """
    Monitoreo sísmico rápido (shortcut)
    """
    service = AdvancedEarthSciencesService()
    
    event_criteria = {
        'min_magnitude': min_magnitude,
        'max_magnitude': 9.0,
        'time_window_hours': hours
    }
    
    analysis_types = ['magnitude_estimation', 'location_refinement', 'tsunami_assessment']
    
    return await service.process_seismic_events_advanced(event_criteria, analysis_types)


@router.post("/quick/ocean-currents")
async def quick_ocean_currents(lat_min: float, lat_max: float, 
                              lon_min: float, lon_max: float,
                              days: int = 7) -> Dict[str, Any]:
    """
    Análisis rápido de corrientes oceánicas (shortcut)
    """
    service = AdvancedEarthSciencesService()
    
    region = {
        'lat_min': lat_min,
        'lat_max': lat_max,
        'lon_min': lon_min,
        'lon_max': lon_max
    }
    
    return await service.ocean_modeling_advanced(region, 'currents', days)


@router.post("/quick/marine-heatwave-detection")
async def quick_marine_heatwave_detection(lat_min: float, lat_max: float,
                                        lon_min: float, lon_max: float,
                                        days: int = 30) -> Dict[str, Any]:
    """
    Detección rápida de ondas de calor marinas (shortcut)
    """
    service = AdvancedEarthSciencesService()
    
    region = {
        'lat_min': lat_min,
        'lat_max': lat_max,
        'lon_min': lon_min,
        'lon_max': lon_max
    }
    
    return await service.ocean_modeling_advanced(region, 'heatwave_detection', days)


# Endpoints para tipos específicos de análisis
@router.post("/climate/temperature-trends")
async def analyze_temperature_trends(model: str, scenario: str,
                                   start_year: int = 2020, end_year: int = 2100) -> Dict[str, Any]:
    """
    Análisis específico de tendencias de temperatura
    """
    service = AdvancedEarthSciencesService()
    return await service.analyze_climate_model_cmip6(
        model, scenario, None, (str(start_year), str(end_year))
    )


@router.post("/seismic/tsunami-risk")
async def assess_tsunami_risk(lat_min: float, lat_max: float,
                             lon_min: float, lon_max: float,
                             min_magnitude: float = 6.0) -> Dict[str, Any]:
    """
    Evaluación específica de riesgo de tsunami
    """
    service = AdvancedEarthSciencesService()
    
    event_criteria = {
        'min_magnitude': min_magnitude,
        'max_magnitude': 9.0,
        'time_window_hours': 168,  # 1 semana
        'region': {
            'lat_min': lat_min,
            'lat_max': lat_max,
            'lon_min': lon_min,
            'lon_max': lon_max
        }
    }
    
    return await service.process_seismic_events_advanced(event_criteria, ['tsunami_assessment'])


@router.post("/ocean/eddy-detection")
async def detect_ocean_eddies(lat_min: float, lat_max: float,
                             lon_min: float, lon_max: float,
                             days: int = 30) -> Dict[str, Any]:
    """
    Detección específica de eddies oceánicos
    """
    service = AdvancedEarthSciencesService()
    
    region = {
        'lat_min': lat_min,
        'lat_max': lat_max,
        'lon_min': lon_min,
        'lon_max': lon_max
    }
    
    return await service.ocean_modeling_advanced(region, 'eddy_detection', days)


@router.post("/climate/extreme-events")
async def analyze_extreme_events(model: str = "CESM2", scenario: str = "SSP585",
                                region: Optional[RegionBounds] = None) -> Dict[str, Any]:
    """
    Análisis específico de eventos extremos climáticos
    """
    service = AdvancedEarthSciencesService()
    
    region_dict = None
    if region:
        region_dict = {
            'lat_min': region.lat_min,
            'lat_max': region.lat_max,
            'lon_min': region.lon_min,
            'lon_max': region.lon_max
        }
    
    return await service.analyze_climate_model_cmip6(model, scenario, region_dict)


@router.post("/ocean/productivity-analysis")
async def analyze_primary_productivity(lat_min: float, lat_max: float,
                                     lon_min: float, lon_max: float,
                                     days: int = 90) -> Dict[str, Any]:
    """
    Análisis específico de productividad primaria oceánica
    """
    service = AdvancedEarthSciencesService()
    
    region = {
        'lat_min': lat_min,
        'lat_max': lat_max,
        'lon_min': lon_min,
        'lon_max': lon_max
    }
    
    return await service.ocean_modeling_advanced(region, 'productivity', days)
