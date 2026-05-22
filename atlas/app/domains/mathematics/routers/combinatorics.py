"""
Combinatorics Router

Router FastAPI para matemáticas combinatorias y principios de conteo.
Proporciona endpoints REST API para permutaciones, combinaciones y cálculos
combinatorios avanzados para probabilidad, estadística y matemáticas discretas.

Este router ofrece capacidades combinatorias comprehensivas para:
- Permutaciones: arreglos ordenados con/sin repetición
- Combinaciones: selecciones no ordenadas con/sin repetición
- Coeficientes multinomiales: combinaciones generalizadas
- Números de Stirling: de primera y segunda clase para particiones de conjuntos
- Números de Bell: número total de particiones
- Números de Catalan: conteo de varios objetos combinatorios
- Aplicaciones del principio de inclusión-exclusión
- Funciones generadoras para secuencias combinatorias

El router se integra con CombinatoricsService para proporcionar
a investigadores y estudiantes herramientas esenciales combinatorias para
problemas de conteo, cálculos de probabilidad y estructuras discretas.

Endpoints disponibles:
- POST /calculate: Cálculos principales de permutaciones y combinaciones
- GET /examples: Ejemplos comprehensivos de combinatoria y aplicaciones

Dependencias:
- CombinatoricsService: Motor principal de computación combinatoria
- SymPy: Combinatoria simbólica y teoría de números
- NumPy: Computaciones numéricas eficientes para factoriales grandes
- CombinatoricsRequest/Result: Modelos de combinatoria estandarizados

Uso típico:
    Soporta tanto aplicaciones matemáticas como estadísticas.
    Maneja números grandes a través de algoritmos eficientes y
    aritmética de precisión arbitraria. Los ejemplos incluyen cálculos
    de probabilidad, teoría de conjuntos y teoría de diseño combinatorio.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.domains.mathematics.models import BaseRequest, BaseResponse
from app.domains.mathematics.services.combinatorics_service import CombinatoricsService
from app.exceptions.domain.mathematics import MathematicsError

# Definir modelos específicos para combinatorics
class CombinatoricsRequest(BaseRequest):
    """Request para operaciones de combinatoria"""
    n: int = Field(..., description="Número total de elementos")
    k: Optional[int] = Field(None, description="Número de elementos a seleccionar")
    operation: str = Field(..., description="Tipo de operación (permutations, combinations)")

class CombinatoricsResult(BaseResponse):
    """Resultado de operaciones de combinatoria"""
    result: int = Field(..., description="Resultado de la operación")
    operation: str = Field(..., description="Operación realizada")
    n: int = Field(..., description="Número total de elementos")
    k: Optional[int] = Field(None, description="Número de elementos seleccionados")

router = APIRouter()

@router.post("/calculate", response_model=CombinatoricsResult)
async def calculate_combinatorics(request: CombinatoricsRequest):
    """
    Calcula permutaciones o combinaciones
    
    Args:
        request: Solicitud con n, k y operación
        
    Returns:
        Resultado de la operación de combinatoria
    """
    try:
        if request.k is None:
            raise HTTPException(status_code=400, detail="Parameter k is required for combinatorics operations")
        
        if request.operation == "permutations":
            result = CombinatoricsService.permutations(request.n, request.k)
        elif request.operation == "combinations":
            result = CombinatoricsService.combinations(request.n, request.k)
        else:
            raise HTTPException(status_code=400, detail="Operación no soportada")
        
        return CombinatoricsResult(**result)
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/examples")
async def get_examples():
    """
    Obtiene ejemplos de operaciones de combinatoria
    
    Returns:
        Lista de ejemplos
    """
    return CombinatoricsService.get_combinatorics_examples()
