"""
API Router consolidada para el dominio Biology
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from app.domains.biology.models import requests, responses
from app.domains.biology.services import computation, analysis
from app.security.auth import get_current_user
from app.core.logging import get_logger
import httpx
from app.exceptions.domain.biology import BiologyError

logger = get_logger(__name__)
router = APIRouter(prefix="/biology", tags=["Biology"])


@router.get("/", response_model=Dict[str, str])
async def domain_info():
    """Información básica del dominio Biology"""
    return {
        "domain": "biology",
        "description": "Domain for biology computational services",
        "version": "2.0.0",
        "status": "active"
    }


@router.get("/services", response_model=List[str])
async def list_services():
    """Lista servicios disponibles en el dominio"""
    return [
        "computation",
        "analysis", 
        "visualization"
    ]


@router.post("/compute")
async def compute_operation(
    request: requests.ComputationRequest,
    current_user = Depends(get_current_user)
):
    """Operación de computación genérica del dominio"""
    try:
        logger.info(f"Computing {request.operation} for user {current_user.get('username', 'unknown')}")
        
        result = await computation.execute_computation(
            operation=request.operation,
            parameters=request.parameters,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )
        
        return responses.ComputationResponse(
            success=True,
            result=result,
            metadata={"domain": "biology", "operation": request.operation}
        )
        
    except BiologyError as e:
        logger.error(f"Computation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Computation failed: {str(e)}"
        )


@router.post("/analyze")
async def analyze_data(
    request: requests.AnalysisRequest,
    current_user = Depends(get_current_user)
):
    """Análisis de datos del dominio"""
    try:
        logger.info(f"Analyzing data for user {current_user.get('username', 'unknown')}")
        
        result = await analysis.execute_analysis(
            data=request.data,
            analysis_type=request.analysis_type,
            parameters=request.parameters,
            user_id=current_user.get('sub', current_user.get('username', 'unknown'))
        )
        
        return responses.AnalysisResponse(
            success=True,
            analysis_result=result,
            metadata={"domain": "biology", "type": request.analysis_type}
        )
        
    except BiologyError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# Incluir sub-routers específicos del dominio
from .biogpt import router as biogpt_router
from .dnabert2 import router as dnabert2_router
from .genomics import router as genomics_router
from .advanced_genomics import router as advanced_genomics_router
from .protgpt2_router import router as protgpt2_router

router.include_router(biogpt_router)
router.include_router(dnabert2_router)
router.include_router(genomics_router)
router.include_router(advanced_genomics_router)
router.include_router(protgpt2_router)
