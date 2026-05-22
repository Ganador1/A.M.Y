"""
API Router consolidada para el dominio Astronomy
"""

from contextlib import suppress
from datetime import datetime
from typing import Any, Dict, List
import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from app.domains.astronomy.models import requests, responses
from app.domains.astronomy.domain_config import DOMAIN_INFO
from app.domains.astronomy.services import astronomy_service
from app.security.auth import get_current_user
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/astronomy", tags=["Astronomy"])


def _parse_timestamp(payload: Dict[str, Any]) -> datetime:
    """Convierte timestamps de la fachada a objetos datetime."""

    stamp = payload.get('timestamp')
    if isinstance(stamp, datetime):
        return stamp
    if isinstance(stamp, str):
        with suppress(ValueError):
            return datetime.fromisoformat(stamp)
    return datetime.utcnow()


@router.get("/", response_model=Dict[str, str])
async def domain_info():
    """Información básica del dominio Astronomy"""
    return {
        "domain": "astronomy",
        "description": "Domain for astronomical data analysis and computational astrophysics",
        "version": DOMAIN_INFO.version,
        "status": "active"
    }


@router.get("/services", response_model=List[str])
async def list_services():
    """Lista servicios disponibles en el dominio"""
    return DOMAIN_INFO.metadata.get("capabilities", [
        "telescope_data_analysis",
        "astronomical_simulation",
        "exoplanet_detection",
        "galaxy_analysis",
        "cosmological_analysis",
        "star_formation_analysis",
    ])


@router.post("/analyze-telescope-data")
async def analyze_telescope_data(
    request: requests.TelescopeDataRequest,
    current_user = Depends(get_current_user)
):
    """Análisis de datos telescópicos"""
    try:
        logger.info(
            "Analyzing telescope data for user %s",
            current_user.get('username', 'unknown')
        )

        result = await astronomy_service.analyze_telescope_data(
            telescope_name=request.telescope_name,
            data_type=request.data_type,
            coordinates=request.coordinates,
            observation_parameters=request.observation_parameters,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )

        if not result.get("success", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Telescope data analysis failed"
            )

        return responses.TelescopeDataResponse(
            success=True,
            telescope_info=result.get('telescope_info', {}),
            data_summary=result.get('data_summary', {}),
            processed_data=result.get('processed_data'),
            visualizations=result.get('visualizations', []),
            execution_time=result.get('execution_time'),
            timestamp=_parse_timestamp(result)
        )

    except Exception as e:
        logger.error("Telescope data analysis error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Telescope data analysis failed: {str(e)}"
        ) from e


@router.post("/run-simulation")
async def run_astronomical_simulation(
    request: requests.AstronomicalSimulationRequest,
    current_user = Depends(get_current_user)
):
    """Ejecutar simulación astronómica"""
    try:
        logger.info(
            "Running astronomical simulation for user %s",
            current_user.get('username', 'unknown')
        )

        result = await astronomy_service.run_astronomical_simulation(
            simulation_type=request.simulation_type,
            parameters=request.parameters,
            time_steps=request.time_steps,
            spatial_resolution=request.spatial_resolution,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )

        return responses.AstronomicalSimulationResponse(
            success=result.get('success', True),
            simulation_id=result.get('simulation_id', ''),
            simulation_results=result.get('simulation_results', {}),
            performance_metrics=result.get('performance_metrics', {}),
            output_files=result.get('output_files', []),
            execution_time=result.get('execution_time'),
            timestamp=_parse_timestamp(result)
        )

    except Exception as e:
        logger.error("Astronomical simulation error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Astronomical simulation failed: {str(e)}"
        ) from e


@router.post("/detect-exoplanets")
async def detect_exoplanets(
    request: requests.ExoplanetDetectionRequest,
    current_user = Depends(get_current_user)
):
    """Detección de exoplanetas"""
    try:
        logger.info(
            "Detecting exoplanets for user %s",
            current_user.get('username', 'unknown')
        )

        result = await astronomy_service.detect_exoplanets(
            star_name=request.star_name,
            method=request.method,
            time_series_data=request.time_series_data,
            detection_parameters=request.detection_parameters,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )

        detection_results = result.get('detection_results', {})
        if analysis_bundle := result.get('analysis_bundle'):
            detection_results = {**detection_results, "analysis_bundle": analysis_bundle}

        return responses.ExoplanetDetectionResponse(
            success=result.get('success', True),
            detection_results=detection_results,
            candidates=result.get('candidates', []),
            statistical_significance=result.get('statistical_significance', 0.0),
            detection_method=request.method,
            execution_time=result.get('execution_time'),
            timestamp=_parse_timestamp(result)
        )

    except Exception as e:
        logger.error("Exoplanet detection error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Exoplanet detection failed: {str(e)}"
        ) from e


@router.post("/analyze-galaxy")
async def analyze_galaxy(
    request: requests.GalaxyAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Análisis de galaxias"""
    try:
        logger.info(
            "Analyzing galaxy for user %s",
            current_user.get('username', 'unknown')
        )

        result = await astronomy_service.analyze_galaxy(
            galaxy_name=request.galaxy_name,
            analysis_type=request.analysis_type,
            data_sources=request.data_sources,
            parameters=request.parameters,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )

        return responses.GalaxyAnalysisResponse(
            success=result.get('success', True),
            galaxy_properties=result.get('galaxy_properties', {}),
            morphological_parameters=result.get('morphological_parameters', {}),
            kinematic_analysis=result.get('kinematic_analysis'),
            derived_quantities=result.get('derived_quantities', {}),
            execution_time=result.get('execution_time'),
            timestamp=_parse_timestamp(result)
        )

    except Exception as e:
        logger.error("Galaxy analysis error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Galaxy analysis failed: {str(e)}"
        ) from e


@router.post("/analyze-cosmology")
async def analyze_cosmology(
    request: requests.CosmologicalAnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Análisis cosmológicos"""
    try:
        logger.info(
            "Performing cosmological analysis for user %s",
            current_user.get('username', 'unknown')
        )

        result = await astronomy_service.analyze_cosmology(
            dataset=request.dataset,
            analysis_type=request.analysis_type,
            parameters=request.parameters,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )

        return responses.CosmologicalAnalysisResponse(
            success=result.get('success', True),
            cosmological_parameters=result.get('cosmological_parameters', {}),
            statistical_analysis=result.get('statistical_analysis', {}),
            model_comparison=result.get('model_comparison'),
            confidence_intervals=result.get('confidence_intervals', {}),
            execution_time=result.get('execution_time'),
            timestamp=_parse_timestamp(result)
        )

    except Exception as e:
        logger.error("Cosmological analysis error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cosmological analysis failed: {str(e)}"
        ) from e


@router.post("/analyze-star-formation")
async def analyze_star_formation(
    request: requests.StarFormationRequest,
    current_user = Depends(get_current_user)
):
    """Análisis de formación estelar"""
    try:
        logger.info(
            "Analyzing star formation for user %s",
            current_user.get('username', 'unknown')
        )

        result = await astronomy_service.analyze_star_formation(
            region_coordinates=request.region_coordinates,
            data_sources=request.data_sources,
            analysis_parameters=request.analysis_parameters,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )

        return responses.StarFormationResponse(
            success=result.get('success', True),
            star_formation_rate=result.get('star_formation_rate', 0.0),
            molecular_clouds=result.get('molecular_clouds', []),
            stellar_populations=result.get('stellar_populations', {}),
            environmental_analysis=result.get('environmental_analysis', {}),
            execution_time=result.get('execution_time'),
            timestamp=_parse_timestamp(result)
        )

    except Exception as e:
        logger.error("Star formation analysis error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Star formation analysis failed: {str(e)}"
        ) from e

