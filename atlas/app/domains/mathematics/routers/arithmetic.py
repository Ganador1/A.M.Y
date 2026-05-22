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
from app.domains.mathematics.models import ArithmeticRequest, ArithmeticResponse, BaseResponse
from app.domains.mathematics.services.arithmetic_service import ArithmeticService
import math
import numpy as np
from app.exceptions.domain.mathematics import MathematicsError

router = APIRouter()

@router.post("/calculate", response_model=ArithmeticResponse)
async def calculate_arithmetic(request: ArithmeticRequest):
    """
    Realiza operaciones aritméticas de forma sencilla

    Ejemplos de uso:
    - Suma: {"operation": "add", "operands": [5, 3, 2]}
    - Multiplicación: {"operation": "multiply", "operands": [4, 3]}
    - Potencia: {"operation": "power", "operands": [2, 3]}
    - Raíz cuadrada: {"operation": "sqrt", "operands": [25]}
    - Seno: {"operation": "sin", "operands": [30]}

    Args:
        request: Solicitud con operación y operandos

    Returns:
        Resultado de la operación con explicación
    """
    try:
        return ArithmeticService.calculate(request)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en los datos de entrada: {str(e)}. Revisa los operandos y la operación."
        )
    except MathematicsError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error al calcular: {str(e)}. Prueba con otros valores."
        )
    except Exception as e:
        # Generic exception should be reported as a 400 for user-facing errors in router tests
        raise HTTPException(
            status_code=400,
            detail=f"Error al calcular: {str(e)}"
        )

@router.get("/operations", response_model=BaseResponse)
async def get_operations():
    """
    Obtiene la lista completa de operaciones disponibles con descripciones

    Returns:
        Lista detallada de operaciones disponibles
    """
    operations = ArithmeticService.get_supported_operations()
    detailed_operations = {
        "basic": {
            "add": "Suma de números (+)",
            "subtract": "Resta de números (-)",
            "multiply": "Multiplicación de números (×)",
            "divide": "División de números (÷)"
        },
        "advanced": {
            "power": "Potencia (base^exponente)",
            "sqrt": "Raíz cuadrada",
            "log": "Logaritmo natural",
            "exp": "Exponencial (e^x)"
        },
        "trigonometric": {
            "sin": "Seno (ángulo en grados)",
            "cos": "Coseno (ángulo en grados)",
            "tan": "Tangente (ángulo en grados)",
            "asin": "Arco seno",
            "acos": "Arco coseno",
            "atan": "Arco tangente"
        },
        "other": {
            "factorial": "Factorial (n!)",
            "abs": "Valor absoluto",
            "round": "Redondeo a entero más cercano"
        }
    }

    return BaseResponse(
        success=True,
        message="Operaciones aritméticas disponibles",
        data={
            "available_operations": operations,
            "categorized_operations": detailed_operations,
            "usage_examples": {
                "suma": {"operation": "add", "operands": [10, 5, 3]},
                "potencia": {"operation": "power", "operands": [2, 8]},
                "trigonometria": {"operation": "sin", "operands": [45]}
            }
        }
    )

@router.post("/batch", response_model=BaseResponse)
async def calculate_batch(requests: List[ArithmeticRequest]):
    """
    Ejecuta múltiples operaciones aritméticas de una vez

    Args:
        requests: Lista de solicitudes aritméticas

    Returns:
        Resultados de todas las operaciones con detalles de errores si los hay
    """
    results = []
    errors = []

    for i, request in enumerate(requests):
        try:
            result = ArithmeticService.calculate(request)
            results.append({
                "index": i,
                "success": True,
                "result": result.result,
                "operation": result.operation,
                "operands": result.operands
            })
        except MathematicsError as e:
            errors.append({
                "index": i,
                "success": False,
                "error": str(e),
                "request": request.dict()
            })

    response_data = {
        "total_requests": len(requests),
        "successful": len(results),
        "failed": len(errors),
        "results": results
    }

    if errors:
        response_data["errors"] = errors
        return BaseResponse(
            success=len(results) > 0,
            message=f"Procesadas {len(requests)} operaciones: {len(results)} exitosas, {len(errors)} fallidas",
            data=response_data
        )

    return BaseResponse(
        success=True,
        message=f"Todas las {len(requests)} operaciones se calcularon exitosamente",
        data=response_data
    )

@router.get("/examples", response_model=BaseResponse)
async def get_examples():
    """
    Obtiene ejemplos prácticos de operaciones aritméticas

    Returns:
        Lista de ejemplos con descripciones detalladas
    """
    return BaseResponse(
        success=True,
        message="Ejemplos de operaciones aritméticas",
        data={
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
                },
                {
                    "name": "Logaritmo",
                    "operation": "log",
                    "operands": [10],
                    "description": "Logaritmo natural de 10",
                    "expected_result": 2.302585
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
                },
                {
                    "name": "Tangente",
                    "operation": "tan",
                    "operands": [45],
                    "description": "Tangente de 45 grados",
                    "expected_result": 1.0
                }
            ],
            "tips": [
                "Las funciones trigonométricas usan grados, no radianes",
                "Para potencias usa [base, exponente]",
                "Las raíces cuadradas solo necesitan un número positivo",
                "Los logaritmos usan base e (natural) por defecto"
            ]
        }
    )

@router.post("/quick-calc/{operation}")
async def quick_calculation(
    operation: str,
    a: float,
    b: Optional[float] = None
):
    """
    Cálculo rápido con parámetros simples en la URL

    Ejemplos:
    - /api/arithmetic/quick-calc/add?a=5&b=3
    - /api/arithmetic/quick-calc/sqrt?a=16
    - /api/arithmetic/quick-calc/sin?a=45

    Args:
        operation: Operación a realizar
        a: Primer operando
        b: Segundo operando (opcional)

    Returns:
        Resultado del cálculo
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
        request = ArithmeticRequest(operation=operation, operands=operands)
        result = ArithmeticService.calculate(request)

        return BaseResponse(
            success=True,
            message=f"Resultado de {operation}({', '.join(map(str, operands))})",
            data={
                "operation": operation,
                "operands": operands,
                "result": result.result,
                "explanation": f"{operation} de {', '.join(map(str, operands))} = {result.result}"
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en los parámetros: {str(e)}. Revisa los valores."
        )
    except MathematicsError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error en el cálculo: {str(e)}. Verifica la operación y los valores."
        )
