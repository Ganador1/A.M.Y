"""
Arithmetic Router

Router FastAPI para operaciones aritméticas fundamentales y avanzadas.
Proporciona endpoints REST API para cálculos matemáticos básicos, funciones trigonométricas,
operaciones exponenciales y procesamiento por lotes de problemas aritméticos.

Este router ofrece capacidades aritméticas comprehensivas para:
- Operaciones básicas: suma, resta, multiplicación, división
- Operaciones avanzadas: potencias, raíces, logaritmos, exponenciales
- Funciones trigonométricas: seno, coseno, tangente con entrada en grados
- Funciones trigonométricas inversas: arcoseno, arcocoseno, arcotangente
- Funciones especiales: factorial, valor absoluto, redondeo
- Procesamiento por lotes: cálculo eficiente de múltiples operaciones
- Cálculos rápidos: aritmética basada en URL con parámetros simples

El router se integra con ArithmeticService para proporcionar
herramientas educativas y utilidades computacionales para cálculos matemáticos
en aplicaciones científicas e ingenieriles.

Endpoints disponibles:
- POST /calculate: Operación aritmética individual con respuesta detallada
- GET /operations: Lista completa de operaciones soportadas y categorías
- POST /batch: Procesamiento por lotes de múltiples operaciones aritméticas
- GET /examples: Ejemplos comprehensivos de operaciones aritméticas
- POST /quick-calc/{operation}: Cálculos rápidos basados en URL

Dependencias:
- ArithmeticService: Motor principal de computación aritmética
- NumPy: Funciones matemáticas de alto rendimiento
- Math: Biblioteca matemática estándar de Python
- ArithmeticRequest/ArithmeticResponse: Modelos aritméticos estandarizados
- BaseResponse: Formato unificado de respuesta API

Uso típico:
    Las funciones trigonométricas aceptan ángulos en grados (no en radianes).
    Las operaciones por lotes proporcionan reportes detallados de errores para cálculos fallidos.
    Los endpoints de cálculo rápido soportan parámetros URL para operaciones simples.
    Todas las operaciones incluyen validación de entrada y mensajes de error comprehensivos.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models import ArithmeticRequest, ArithmeticResponse, BaseResponse
from app.services.arithmetic import ArithmeticService
# Use generic Exception handling for compatibility with tests and environments
# The APIError type may not be available in all test contexts, so avoid importing it

router = APIRouter()

@router.post("/calculate", response_model=ArithmeticResponse)
async def calculate_arithmetic(request: ArithmeticRequest):
    """
    Realiza una operación aritmética individual
    
    Args:
        request: Solicitud con operación y operandos
        
    Returns:
        Respuesta con resultado del cálculo
        
    Raises:
        HTTPException: Si la operación falla o es inválida
    """
    try:
        result = ArithmeticService.calculate(request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Report generic exceptions as 400 in router for simplicity and to match tests
        raise HTTPException(status_code=400, detail=f"Error al calcular: {str(e)}")

@router.get("/operations", response_model=BaseResponse)
async def get_operations():
    """
    Obtiene lista de operaciones aritméticas disponibles
    
    Returns:
        Lista categorizada de operaciones soportadas
    """
    operations = ArithmeticService.get_supported_operations()
    return {
        "success": True,
        "message": "Operaciones aritméticas disponibles",
        "data": {
            "available_operations": operations,
            "categorized_operations": {
                "basic": ["add", "subtract", "multiply", "divide"],
                "advanced": ["power", "sqrt", "log", "exp"],
                "trigonometric": ["sin", "cos", "tan"]
            },
            "usage_examples": {
                "suma": {"operation": "add", "operands": [10, 5, 3]},
                "potencia": {"operation": "power", "operands": [2, 8]},
                "trigonometria": {"operation": "sin", "operands": [45]}
            }
        }
    }

@router.post("/batch", response_model=BaseResponse)
async def calculate_batch(requests: List[ArithmeticRequest]):
    """
    Procesa múltiples operaciones aritméticas en lote
    
    Args:
        requests: Lista de solicitudes aritméticas
        
    Returns:
        Resultados de todas las operaciones procesadas
    """
    results = []
    errors = []
    
    for i, request in enumerate(requests):
        try:
            result = ArithmeticService.calculate(request)
            results.append({
                "index": i,
                "operation": request.operation,
                "result": result.result,
                "success": True
            })
        except Exception as e:
            errors.append({
                "index": i,
                "operation": request.operation,
                "error": str(e),
                "success": False
            })
    
    response_data = {
        "total_requests": len(requests),
        "successful": len(results),
        "failed": len(errors),
        "results": results
    }

    if errors:
        response_data["errors"] = errors

    return {
        "success": len(results) > 0,
        "message": f"Procesadas {len(requests)} operaciones: {len(results)} exitosas, {len(errors)} fallidas",
        "data": response_data
    }

@router.get("/examples", response_model=BaseResponse)
async def get_examples():
    """
    Obtiene ejemplos de operaciones aritméticas
    
    Returns:
        Ejemplos comprehensivos de uso de operaciones
    """
    return {
        "success": True,
        "message": "Ejemplos de operaciones aritméticas obtenidos exitosamente",
        "data": {
            "basic_operations": [
                {
                    "name": "Suma simple",
                    "operation": "add",
                    "operands": [5, 3, 2],
                    "description": "Suma de tres números",
                    "expected_result": 10
                },
                {
                    "name": "Resta",
                    "operation": "subtract",
                    "operands": [10, 4],
                    "description": "Resta de dos números",
                    "expected_result": 6
                },
                {
                    "name": "Multiplicación",
                    "operation": "multiply",
                    "operands": [6, 7],
                    "description": "Multiplicación de dos números",
                    "expected_result": 42
                }
            ],
            "advanced_operations": [
                {
                    "name": "Potencia",
                    "operation": "power",
                    "operands": [2, 3],
                    "description": "2 elevado a la potencia 3",
                    "expected_result": 8
                },
                {
                    "name": "Raíz cuadrada",
                    "operation": "sqrt",
                    "operands": [25],
                    "description": "Raíz cuadrada de 25",
                    "expected_result": 5
                }
            ],
            "trigonometric_operations": [
                {
                    "name": "Seno",
                    "operation": "sin",
                    "operands": [30],
                    "description": "Seno de 30 grados",
                    "expected_result": 0.5
                },
                {
                    "name": "Coseno",
                    "operation": "cos",
                    "operands": [60],
                    "description": "Coseno de 60 grados",
                    "expected_result": 0.5
                }
            ],
            "tips": [
                "Las funciones trigonométricas usan grados, no radianes",
                "Para potencias usa [base, exponente]",
                "Las raíces cuadradas solo necesitan un número positivo",
                "Los logaritmos usan base e (natural) por defecto"
            ]
        }
    }

@router.post("/quick-calc/{operation}")
async def quick_calculation(
    operation: str,
    a: float,
    b: Optional[float] = None
):
    """
    Cálculo rápido basado en URL
    
    Args:
        operation: Tipo de operación a realizar
        a: Primer operando
        b: Segundo operando (opcional para operaciones unarias)
        
    Returns:
        Resultado del cálculo rápido
    """
    try:
        binary_ops = {"add", "subtract", "multiply", "divide", "power"}
        unary_ops = {"sqrt", "log", "exp", "sin", "cos", "tan", "factorial", "abs"}

        if operation in binary_ops and b is None:
            raise HTTPException(
                status_code=400,
                detail=f"La operación '{operation}' requiere dos operandos. Usa /quick-calc/{operation}?a=X&b=Y"
            )

        if operation in unary_ops and b is not None:
            raise HTTPException(
                status_code=400,
                detail=f"La operación '{operation}' solo requiere un operando. Usa /quick-calc/{operation}?a=X"
            )

        operands = [a] if b is None else [a, b]
        request = ArithmeticRequest(
            operation=operation,
            operands=operands
        )
        result = ArithmeticService.calculate(request)
        return {
            "success": True,
            "message": f"Resultado de {operation}({', '.join(map(str, operands))})",
            "data": {
                "operation": operation,
                "operands": operands,
                "result": result.result,
                "explanation": f"{operation} de {', '.join(map(str, operands))} = {result.result}"
            }
        }
    except HTTPException:
        # Re-raise HTTPExceptions raised by our validation above
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error en el cálculo: {str(e)}")