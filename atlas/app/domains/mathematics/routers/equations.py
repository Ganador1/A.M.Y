"""
Router de Ecuaciones - Sistema de Resolución Matemática Avanzada

Módulo FastAPI para resolución integral de ecuaciones y sistemas matemáticos.
Proporciona endpoints REST API para resolver ecuaciones algebraicas, sistemas de ecuaciones
y procesamiento por lotes de problemas matemáticos complejos.

Capacidades principales:
- Resolución de ecuaciones simples: polinomiales, trascendentales y complejas
- Resolución de sistemas: lineales y no lineales con múltiples ecuaciones
- Procesamiento por lotes: resolución eficiente de múltiples ecuaciones
- Biblioteca de ejemplos: colección completa de tipos de ecuaciones y soluciones
- Manejo de errores: reporte detallado de soluciones fallidas
- Soporte simbólico y numérico: integración con SymPy y SciPy

Catálogo de Endpoints:
- POST /solve: Resolución de ecuación única con métodos simbólicos/numéricos
- POST /system: Sistemas lineales y no lineales de ecuaciones
- GET /examples: Biblioteca completa de ejemplos y plantillas de ecuaciones
- POST /batch: Procesamiento por lotes con agregación de errores

Dependencias:
- EquationService: Motor central de resolución de ecuaciones
- SymPy: Matemáticas simbólicas para soluciones analíticas
- NumPy/SciPy: Métodos numéricos de resolución de ecuaciones
- EquationRequest/EquationResponse: Modelos estandarizados de ecuaciones

Uso del Servicio:
    Soporta expresiones simbólicas con notación matemática estándar.
    Las variables pueden especificarse o detectarse automáticamente.
    Los sistemas aceptan múltiples ecuaciones y variables.
    El procesamiento por lotes permite manejo eficiente de múltiples problemas
    con reporte integral de errores y resultados exitosos.
"""

from fastapi import APIRouter, HTTPException
from typing import List
from app.domains.mathematics.models import EquationRequest, EquationResponse
from app.domains.mathematics.services.equation_service import EquationService
from app.exceptions.domain.mathematics import MathematicsError

router = APIRouter()

@router.post("/solve", response_model=EquationResponse)
async def solve_equation(request: EquationRequest):
    """
    Resuelve una ecuación matemática
    
    Args:
        request: Solicitud con ecuación y variable
        
    Returns:
        Soluciones de la ecuación
    """
    try:
        return EquationService.solve_equation(request)
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/system")
async def solve_system(equations: List[str], variables: List[str]):
    """
    Resuelve un sistema de ecuaciones
    
    Args:
        equations: Lista de ecuaciones
        variables: Lista de variables
        
    Returns:
        Soluciones del sistema
    """
    try:
        return EquationService.solve_system(equations, variables)
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/examples")
async def get_examples():
    """
    Obtiene ejemplos de ecuaciones
    
    Returns:
        Lista de ejemplos
    """
    return EquationService.get_equation_examples()

@router.post("/batch", response_model=List[EquationResponse])
async def solve_batch(requests: List[EquationRequest]):
    """
    Resuelve múltiples ecuaciones
    
    Args:
        requests: Lista de solicitudes
        
    Returns:
        Lista de soluciones
    """
    results = []
    errors = []
    
    for i, request in enumerate(requests):
        try:
            result = EquationService.solve_equation(request)
            results.append(result)
        except MathematicsError as e:
            errors.append({
                "index": i,
                "error": str(e),
                "request": request.dict()
            })
    
    if errors:
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "Algunas ecuaciones fallaron",
                "errors": errors,
                "successful_results": results
            }
        )
    
    return results
