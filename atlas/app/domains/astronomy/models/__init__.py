"""
Modelos del dominio Astronomy
"""

from .requests import (
    BaseRequest,
    TelescopeDataRequest,
    AstronomicalSimulationRequest,
    ExoplanetDetectionRequest,
    GalaxyAnalysisRequest,
    CosmologicalAnalysisRequest,
    StarFormationRequest
)

from .responses import (
    BaseResponse,
    TelescopeDataResponse,
    AstronomicalSimulationResponse,
    ExoplanetDetectionResponse,
    GalaxyAnalysisResponse,
    CosmologicalAnalysisResponse,
    StarFormationResponse,
    ErrorResponse
)

__all__ = [
    # Requests
    'BaseRequest',
    'TelescopeDataRequest',
    'AstronomicalSimulationRequest',
    'ExoplanetDetectionRequest',
    'GalaxyAnalysisRequest',
    'CosmologicalAnalysisRequest',
    'StarFormationRequest',
    # Responses
    'BaseResponse',
    'TelescopeDataResponse',
    'AstronomicalSimulationResponse',
    'ExoplanetDetectionResponse',
    'GalaxyAnalysisResponse',
    'CosmologicalAnalysisResponse',
    'StarFormationResponse',
    'ErrorResponse'
]

