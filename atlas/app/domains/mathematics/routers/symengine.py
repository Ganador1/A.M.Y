"""
SymEngine Router for AXIOM Mathematics Domain

Router para endpoints de computación simbólica de alto rendimiento utilizando SymEngine.
Proporciona acceso a álgebra simbólica optimizada, manipulación de expresiones
y cálculo simbólico acelerado.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import asyncio

from ..models import BaseRequest, BaseResponse
from ..services.symengine_service import SymEngineService
from app.exceptions.domain.mathematics import MathematicsError

# Crear router
router = APIRouter(
    prefix="/symengine",
    tags=["SymEngine", "Symbolic Computation", "High Performance"],
    responses={404: {"description": "Not found"}}
)

# Instancia del servicio
symengine_service = SymEngineService()


@router.get("/capabilities", response_model=BaseResponse)
async def get_symengine_capabilities():
    """
    Obtener capacidades del servicio SymEngine
    """
    try:
        capabilities = symengine_service.get_capabilities()
        return BaseResponse(
            success=True,
            message="SymEngine capabilities retrieved successfully",
            data=capabilities
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/symbolic-algebra/{operation}", response_model=BaseResponse)
async def symbolic_algebra_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de álgebra simbólica con SymEngine
    
    Operaciones disponibles:
    - expression_creation: Creación de expresiones
    - polynomial_operations: Operaciones con polinomios
    - rational_functions: Funciones racionales
    """
    try:
        result = await symengine_service.symbolic_algebra(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Symbolic algebra operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/calculus/{operation}", response_model=BaseResponse)
async def calculus_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de cálculo simbólico con SymEngine
    
    Operaciones disponibles:
    - differentiation: Diferenciación
    - integration: Integración
    - limits: Límites
    """
    try:
        result = await symengine_service.calculus(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Calculus operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/equation-solving/{operation}", response_model=BaseResponse)
async def equation_solving_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de resolución de ecuaciones con SymEngine
    
    Operaciones disponibles:
    - algebraic_equations: Ecuaciones algebraicas
    - system_of_equations: Sistema de ecuaciones
    - differential_equations: Ecuaciones diferenciales
    """
    try:
        result = await symengine_service.equation_solving(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Equation solving operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/series-expansion/{operation}", response_model=BaseResponse)
async def series_expansion_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de expansión en series con SymEngine
    
    Operaciones disponibles:
    - taylor_series: Serie de Taylor
    - laurent_series: Serie de Laurent
    """
    try:
        result = await symengine_service.series_expansion(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Series expansion operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/matrix-operations/{operation}", response_model=BaseResponse)
async def matrix_operations_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones con matrices con SymEngine
    
    Operaciones disponibles:
    - symbolic_matrix: Matriz simbólica
    - eigenvalues: Valores propios
    """
    try:
        result = await symengine_service.matrix_operations(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Matrix operations '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def symengine_status():
    """
    Estado del servicio SymEngine
    """
    return {
        "service": "SymEngine",
        "status": "active",
        "symengine_available": symengine_service.symengine_available,
        "version": symengine_service.version,
        "simulation_mode": not symengine_service.symengine_available
    }






