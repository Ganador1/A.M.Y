"""
API Router consolidada para el dominio Mathematics
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from app.domains.mathematics.models import requests, responses
from app.domains.mathematics.services import computation, analysis
from app.security.auth import get_current_user
from app.core.logging import get_logger
import httpx
from app.exceptions.domain.mathematics import MathematicsError

logger = get_logger(__name__)
router = APIRouter(prefix="/mathematics", tags=["Mathematics"])


@router.get("/", response_model=Dict[str, str])
async def domain_info():
    """Información básica del dominio Mathematics"""
    return {
        "domain": "mathematics",
        "description": "Domain for mathematics computational services",
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
            metadata={"domain": "mathematics", "operation": request.operation}
        )
        
    except MathematicsError as e:
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
            metadata={"domain": "mathematics", "type": request.analysis_type}
        )
        
    except MathematicsError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# Incluir sub-routers específicos del dominio
from .calculus import router as calculus_router
from .advanced_sympy import router as sympy_router
from .sagemath import router as sagemath_router
from .julia import router as julia_router
from .symengine import router as symengine_router
from .discovery_engine import router as discovery_router
from .advanced_topology import router as topology_router
from .quantum_math import router as quantum_router
from .math_ml import router as ml_router
from .math_visualization import router as visualization_router
from .advanced_math_ai import router as ai_router
from .advanced_number_theory import router as number_theory_router
from .automated_theorem_proving import router as theorem_proving_router
from .distributed_computing import router as distributed_router
from .consolidated_api import router as consolidated_router

# Router principal consolidado
router.include_router(consolidated_router, prefix="")

# Sub-routers especializados
router.include_router(calculus_router, prefix="")
router.include_router(sympy_router, prefix="/advanced")
router.include_router(sagemath_router, prefix="/sagemath")
router.include_router(julia_router, prefix="/julia")
router.include_router(symengine_router, prefix="/symengine")
router.include_router(discovery_router, prefix="/discovery")
router.include_router(topology_router, prefix="/topology")
router.include_router(quantum_router, prefix="/quantum")
router.include_router(ml_router, prefix="/ml")
router.include_router(visualization_router, prefix="/visualization")
router.include_router(ai_router, prefix="/ai")
router.include_router(number_theory_router, prefix="/number-theory")
router.include_router(theorem_proving_router, prefix="/theorem-proving")
router.include_router(distributed_router, prefix="/distributed")
