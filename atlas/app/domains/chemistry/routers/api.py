"""
API Router consolidada para el dominio Chemistry
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from app.domains.chemistry.models import requests, responses
from app.domains.chemistry.services import computation, analysis
from app.security.auth import get_current_user
from app.core.logging import get_logger
from app.autonomous.pipelines.enhanced_chemistry_loop import EnhancedChemistryLoop
from app.services.unified_research_orchestrator import get_unified_orchestrator, OrchestrationTask, ResearchPhase
from dataclasses import asdict
import httpx
from app.exceptions.domain.chemistry import ChemistryError

logger = get_logger(__name__)
router = APIRouter(prefix="/chemistry", tags=["Chemistry"])


@router.get("/", response_model=Dict[str, str])
async def domain_info():
    """Información básica del dominio Chemistry"""
    return {
        "domain": "chemistry",
        "description": "Domain for chemistry computational services",
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
            metadata={"domain": "chemistry", "operation": request.operation}
        )
        
    except ChemistryError as e:
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
            metadata={"domain": "chemistry", "type": request.analysis_type}
        )
        
    except ChemistryError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# Incluir sub-routers específicos del dominio
# from .specialized_router import specialized_router
# router.include_router(specialized_router, prefix="/specialized")


# Singleton para el EnhancedChemistryLoop
_enhanced_loop: Optional[EnhancedChemistryLoop] = None


def get_enhanced_loop() -> EnhancedChemistryLoop:
    global _enhanced_loop
    if _enhanced_loop is None:
        _enhanced_loop = EnhancedChemistryLoop()
    return _enhanced_loop


@router.post("/enhanced/electrocatalysis/run", response_model=Dict[str, Any])
async def run_enhanced_electrocatalysis(
    top_n: int = 8,
    current_user = Depends(get_current_user)
):
    """Ejecuta una iteración mejorada de electrocatálisis"""
    try:
        logger.info(
            f"Running enhanced electrocatalysis iteration top_n={top_n} for user {current_user.get('username', 'unknown')}"
        )
        loop = get_enhanced_loop()
        result = await loop.run_enhanced_electrocatalysis_iteration(top_n=top_n)
        return result
    except ChemistryError as e:
        logger.error(f"Enhanced electrocatalysis error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced electrocatalysis failed: {str(e)}"
        )


@router.post("/enhanced/electrocatalysis/orchestrate", response_model=Dict[str, Any])
async def orchestrate_enhanced_electrocatalysis(
    top_n: int = 8,
    current_user = Depends(get_current_user)
):
    """Orquesta la iteración de electrocatálisis usando el UnifiedResearchOrchestrator"""
    try:
        logger.info(
            f"Orchestrating enhanced electrocatalysis iteration top_n={top_n} for user {current_user.get('username', 'unknown')}"
        )
        loop = get_enhanced_loop()
        orchestrator = get_unified_orchestrator()
        # registrar servicio en el orquestador (idempotente)
        orchestrator.register_service("EnhancedChemistryLoop", loop)

        task = OrchestrationTask(
            task_id=f"chem_enhanced_{loop.iteration + 1}",
            task_type="domain_loop",
            service_name="EnhancedChemistryLoop",
            operation="run_enhanced_electrocatalysis_iteration",
            parameters={"top_n": top_n},
            phase=ResearchPhase.EXECUTION,
            metadata={
                "domain": "chemistry",
                "mode": "enhanced",
                "user": current_user.get('username', 'unknown'),
            },
        )
        orchestration_result = await orchestrator.execute_task(task)
        # convertir dataclass a dict
        try:
            return asdict(orchestration_result)
        except ChemistryError:
            return {
                "task_id": orchestration_result.task_id,
                "success": orchestration_result.success,
                "result": orchestration_result.result,
                "error": orchestration_result.error,
                "execution_time_sec": orchestration_result.execution_time_sec,
                "phase": orchestration_result.phase.value if orchestration_result.phase else None,
                "metadata": orchestration_result.metadata,
            }
    except ChemistryError as e:
        logger.error(f"Enhanced electrocatalysis orchestration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enhanced electrocatalysis orchestration failed: {str(e)}"
        )
