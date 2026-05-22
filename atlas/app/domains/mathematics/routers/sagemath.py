"""
SageMath Router for AXIOM Mathematics Domain

Router para endpoints de álgebra computacional utilizando SageMath.
Proporciona acceso a teoría de números avanzada, geometría algebraica,
combinatoria y criptografía matemática.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import asyncio

from ..models import BaseRequest, BaseResponse
from ..services.sagemath_service import SageMathService
from app.exceptions.domain.mathematics import MathematicsError

# Crear router
router = APIRouter(
    prefix="/sagemath",
    tags=["SageMath", "Algebraic Computation", "Number Theory"],
    responses={404: {"description": "Not found"}}
)

# Instancia del servicio
sagemath_service = SageMathService()


@router.get("/capabilities", response_model=BaseResponse)
async def get_sagemath_capabilities():
    """
    Obtener capacidades del servicio SageMath
    """
    try:
        capabilities = sagemath_service.get_capabilities()
        return BaseResponse(
            success=True,
            message="SageMath capabilities retrieved successfully",
            data=capabilities
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/number-theory/{operation}", response_model=BaseResponse)
async def number_theory_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones avanzadas de teoría de números con SageMath
    
    Operaciones disponibles:
    - elliptic_curves: Análisis de curvas elípticas
    - modular_forms: Formas modulares
    - l_functions: Funciones L
    - algebraic_numbers: Números algebraicos
    """
    try:
        result = await sagemath_service.number_theory_advanced(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Number theory operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/algebraic-geometry/{operation}", response_model=BaseResponse)
async def algebraic_geometry_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de geometría algebraica con SageMath
    
    Operaciones disponibles:
    - varieties: Variedades algebraicas
    - schemes: Esquemas algebraicos
    - cohomology: Cohomología
    """
    try:
        result = await sagemath_service.algebraic_geometry(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Algebraic geometry operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/combinatorics/{operation}", response_model=BaseResponse)
async def combinatorics_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones avanzadas de combinatoria con SageMath
    
    Operaciones disponibles:
    - symmetric_functions: Funciones simétricas
    - tableaux: Tableaux de Young
    - posets: Conjuntos parcialmente ordenados
    """
    try:
        result = await sagemath_service.combinatorics_advanced(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Combinatorics operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cryptography/{operation}", response_model=BaseResponse)
async def cryptography_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de criptografía matemática con SageMath
    
    Operaciones disponibles:
    - rsa: Algoritmo RSA
    - elliptic_curve_crypto: Criptografía de curva elíptica
    - discrete_log: Logaritmo discreto
    """
    try:
        result = await sagemath_service.cryptography(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Cryptography operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph-theory/{operation}", response_model=BaseResponse)
async def graph_theory_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de teoría de grafos con SageMath
    
    Operaciones disponibles:
    - graph_properties: Propiedades de grafos
    - graph_algorithms: Algoritmos de grafos
    - network_analysis: Análisis de redes
    """
    try:
        result = await sagemath_service.graph_theory(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Graph theory operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/abstract-algebra/{operation}", response_model=BaseResponse)
async def abstract_algebra_operation(
    operation: str,
    request: BaseRequest
):
    """
    Operaciones de álgebra abstracta con SageMath
    
    Operaciones disponibles:
    - groups: Teoría de grupos
    - rings: Teoría de anillos
    - fields: Teoría de cuerpos
    """
    try:
        result = await sagemath_service.abstract_algebra(
            operation=operation,
            parameters=request.data or {}
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Abstract algebra operation '{operation}' completed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=BaseResponse)
async def execute_sagemath_code(request: BaseRequest):
    """
    Ejecutar código SageMath personalizado
    
    Parámetros:
    - code: Código SageMath a ejecutar
    """
    try:
        code = request.data.get("code", "") if request.data else ""
        if not code:
            raise HTTPException(status_code=400, detail="Code parameter is required")
        
        result = await sagemath_service._execute_sage_code(code)
        
        return BaseResponse(
            success=result["success"],
            message="SageMath code executed",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def sagemath_status():
    """
    Estado del servicio SageMath
    """
    return {
        "service": "SageMath",
        "status": "active",
        "sage_available": sagemath_service.sage_available,
        "version": sagemath_service.version,
        "simulation_mode": not sagemath_service.sage_available
    }






