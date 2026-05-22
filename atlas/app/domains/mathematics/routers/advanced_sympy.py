"""
Advanced SymPy Router for AXIOM Mathematics Domain

Router FastAPI para computación simbólica avanzada utilizando SymPy 1.13+
Proporciona endpoints REST API para álgebra simbólica, cálculo diferencial/integral,
álgebra lineal simbólica, teoría de números y más.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.domains.mathematics.services.advanced_sympy_service import AdvancedSymPyService
from app.domains.mathematics.models import BaseResponse
from app.security.auth import require_scopes
from app.exceptions.domain.mathematics import MathematicsError

router = APIRouter(prefix="/sympy", tags=["Advanced SymPy"])
service = AdvancedSymPyService()


# Modelos de Request
class SymbolicAlgebraRequest(BaseModel):
    """Request para operaciones de álgebra simbólica"""
    expression: str = Field(..., description="Expresión matemática simbólica")
    operations: List[str] = Field(..., description="Operaciones a realizar")


class SymbolicCalculusRequest(BaseModel):
    """Request para operaciones de cálculo simbólico"""
    expression: str = Field(..., description="Expresión matemática")
    operation: str = Field(..., description="Operación: derivative, integral, limit, series, taylor")
    variable: str = Field(default="x", description="Variable de la operación")
    order: int = Field(default=1, description="Orden de la operación")
    limits: Optional[List[float]] = Field(None, description="Límites para integrales o series")


class SymbolicLinearAlgebraRequest(BaseModel):
    """Request para álgebra lineal simbólica"""
    matrix_data: List[List[str]] = Field(..., description="Matriz como lista de listas de strings")
    operation: str = Field(..., description="Operación: determinant, eigenvalues, eigenvectors, etc.")


class NumberTheoryRequest(BaseModel):
    """Request para teoría de números"""
    number: int = Field(..., description="Número entero para análisis")
    operations: List[str] = Field(..., description="Operaciones de teoría de números")


class SolveEquationsRequest(BaseModel):
    """Request para resolución de ecuaciones"""
    equations: List[str] = Field(..., description="Lista de ecuaciones")
    variables: List[str] = Field(..., description="Variables a resolver")


class GeometryRequest(BaseModel):
    """Request para geometría simbólica"""
    geometry_type: str = Field(..., description="Tipo: point, line, circle, polygon")
    parameters: Dict[str, Any] = Field(..., description="Parámetros geométricos")


class PhysicsRequest(BaseModel):
    """Request para física simbólica"""
    physics_type: str = Field(..., description="Tipo: mechanics, quantum, units")
    parameters: Dict[str, Any] = Field(..., description="Parámetros físicos")


class CombinatoricsRequest(BaseModel):
    """Request para combinatoria"""
    operation: str = Field(..., description="Operación: permutation, combination, partition")
    parameters: Dict[str, Any] = Field(..., description="Parámetros combinatorios")


class StatisticsRequest(BaseModel):
    """Request para estadística simbólica"""
    distribution: str = Field(..., description="Distribución: normal, uniform, exponential")
    parameters: Dict[str, Any] = Field(..., description="Parámetros de la distribución")


# Endpoints
@router.post("/algebra", response_model=BaseResponse)
async def symbolic_algebra(
    request: SymbolicAlgebraRequest,
    current_user: dict = Depends(require_scopes(["math:symbolic"]))
):
    """
    Operaciones de álgebra simbólica avanzada
    
    Operaciones disponibles:
    - simplify: Simplificar expresión
    - expand: Expandir expresión
    - factor: Factorizar expresión
    - collect: Recopilar términos
    - cancel: Cancelar factores comunes
    - apart: Descomposición en fracciones parciales
    - latex: Salida LaTeX
    """
    try:
        result = await service.symbolic_algebra(request.expression, request.operations)
        
        return BaseResponse(
            success=result["success"],
            message="Operaciones de álgebra simbólica completadas",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/calculus", response_model=BaseResponse)
async def symbolic_calculus(
    request: SymbolicCalculusRequest,
    current_user: dict = Depends(require_scopes(["math:symbolic"]))
):
    """
    Operaciones de cálculo simbólico
    
    Operaciones disponibles:
    - derivative: Derivada simbólica
    - integral: Integral simbólica (definida o indefinida)
    - limit: Límite simbólico
    - series: Serie de potencias
    - taylor: Serie de Taylor
    """
    try:
        result = await service.symbolic_calculus(
            request.expression,
            request.operation,
            request.variable,
            request.order,
            request.limits
        )
        
        return BaseResponse(
            success=result["success"],
            message=f"Operación de cálculo simbólico '{request.operation}' completada",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/linear-algebra", response_model=BaseResponse)
async def symbolic_linear_algebra(
    request: SymbolicLinearAlgebraRequest,
    current_user: dict = Depends(require_scopes(["math:symbolic"]))
):
    """
    Álgebra lineal simbólica
    
    Operaciones disponibles:
    - determinant: Determinante simbólico
    - eigenvalues: Valores propios
    - eigenvectors: Vectores propios
    - inverse: Matriz inversa
    - rank: Rango de la matriz
    - nullspace: Espacio nulo
    - rref: Forma escalonada reducida
    - lu: Descomposición LU
    - qr: Descomposición QR
    """
    try:
        result = await service.symbolic_linear_algebra(request.matrix_data, request.operation)
        
        return BaseResponse(
            success=result["success"],
            message=f"Operación de álgebra lineal '{request.operation}' completada",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/number-theory", response_model=BaseResponse)
async def number_theory(
    request: NumberTheoryRequest,
    current_user: dict = Depends(require_scopes(["math:number_theory"]))
):
    """
    Teoría de números computacional
    
    Operaciones disponibles:
    - isprime: Verificar primalidad
    - factorint: Factorización prima
    - primefactors: Factores primos únicos
    - totient: Función φ de Euler
    - mobius: Función μ de Möbius
    - divisors: Lista de divisores
    - divisor_count: Número de divisores
    - divisor_sigma: Suma de divisores
    - gcd: Máximo común divisor
    - lcm: Mínimo común múltiplo
    """
    try:
        result = await service.number_theory(request.number, request.operations)
        
        return BaseResponse(
            success=result["success"],
            message="Operaciones de teoría de números completadas",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/solve-equations", response_model=BaseResponse)
async def solve_equations(
    request: SolveEquationsRequest,
    current_user: dict = Depends(require_scopes(["math:symbolic"]))
):
    """
    Resolución simbólica de sistemas de ecuaciones
    
    Soporta sistemas lineales y no lineales con múltiples variables.
    """
    try:
        result = await service.solve_equations(request.equations, request.variables)
        
        return BaseResponse(
            success=result["success"],
            message=f"Sistema de {len(request.equations)} ecuaciones resuelto",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/geometry", response_model=BaseResponse)
async def geometry_operations(
    request: GeometryRequest,
    current_user: dict = Depends(require_scopes(["math:geometry"]))
):
    """
    Operaciones de geometría simbólica
    
    Tipos disponibles:
    - point: Punto en el plano
    - line: Línea entre dos puntos
    - circle: Círculo con centro y radio
    - polygon: Polígono con vértices
    """
    try:
        result = await service.geometry_operations(request.geometry_type, request.parameters)
        
        return BaseResponse(
            success=result["success"],
            message=f"Operación geométrica '{request.geometry_type}' completada",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/physics", response_model=BaseResponse)
async def physics_symbolic(
    request: PhysicsRequest,
    current_user: dict = Depends(require_scopes(["math:physics"]))
):
    """
    Física simbólica
    
    Tipos disponibles:
    - mechanics: Mecánica clásica simbólica
    - quantum: Mecánica cuántica simbólica
    - units: Análisis dimensional
    """
    try:
        result = await service.physics_symbolic(request.physics_type, request.parameters)
        
        return BaseResponse(
            success=result["success"],
            message=f"Física simbólica '{request.physics_type}' completada",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/combinatorics", response_model=BaseResponse)
async def combinatorics(
    request: CombinatoricsRequest,
    current_user: dict = Depends(require_scopes(["math:combinatorics"]))
):
    """
    Operaciones de combinatoria simbólica
    
    Operaciones disponibles:
    - permutation: Permutaciones aleatorias
    - combination: Combinaciones
    - partition: Particiones de enteros
    """
    try:
        result = await service.combinatorics(request.operation, request.parameters)
        
        return BaseResponse(
            success=result["success"],
            message=f"Operación combinatoria '{request.operation}' completada",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/statistics", response_model=BaseResponse)
async def statistics_symbolic(
    request: StatisticsRequest,
    current_user: dict = Depends(require_scopes(["math:statistics"]))
):
    """
    Estadística simbólica con distribuciones
    
    Distribuciones disponibles:
    - normal: Distribución normal
    - uniform: Distribución uniforme
    - exponential: Distribución exponencial
    """
    try:
        result = await service.statistics_symbolic(request.distribution, request.parameters)
        
        return BaseResponse(
            success=result["success"],
            message=f"Estadística simbólica '{request.distribution}' completada",
            data=result,
            execution_time=result.get("processing_time", 0.1)
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/capabilities", response_model=BaseResponse)
async def get_capabilities():
    """
    Obtiene capacidades completas del servicio SymPy
    """
    try:
        capabilities = service.get_capabilities()
        
        return BaseResponse(
            success=True,
            message="Capacidades del servicio SymPy obtenidas",
            data=capabilities
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/examples", response_model=BaseResponse)
async def get_examples():
    """
    Obtiene ejemplos de uso del servicio SymPy
    """
    try:
        examples = {
            "algebra": {
                "expression": "x**2 + 2*x + 1",
                "operations": ["simplify", "factor", "expand"],
                "description": "Simplificar, factorizar y expandir polinomio"
            },
            "calculus": {
                "expression": "x**3 + sin(x)",
                "operation": "derivative",
                "variable": "x",
                "description": "Derivar función polinomial y trigonométrica"
            },
            "linear_algebra": {
                "matrix": [["1", "2"], ["3", "4"]],
                "operation": "eigenvalues",
                "description": "Calcular valores propios de matriz 2x2"
            },
            "number_theory": {
                "number": 60,
                "operations": ["factorint", "divisors", "totient"],
                "description": "Análisis completo de número entero"
            },
            "geometry": {
                "type": "circle",
                "parameters": {"cx": 0, "cy": 0, "radius": 5},
                "description": "Crear círculo con centro en origen y radio 5"
            },
            "physics": {
                "type": "mechanics",
                "parameters": {},
                "description": "Mecánica clásica simbólica básica"
            }
        }
        
        return BaseResponse(
            success=True,
            message="Ejemplos de uso del servicio SymPy",
            data=examples
        )
        
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))






