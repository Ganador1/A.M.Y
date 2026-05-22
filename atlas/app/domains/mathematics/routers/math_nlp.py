"""
Router de Procesamiento de Lenguaje Natural Matemático - AXIOM Meta 4.1
====================================================================

Este módulo implementa el router para el servicio de procesamiento de lenguaje natural matemático
en la plataforma AXIOM. Proporciona capacidades avanzadas para entender, parsear y procesar
expresiones matemáticas expresadas en lenguaje natural.

Capacidades Principales:
----------------------
- **Parsing de Lenguaje Natural**: Conversión de texto matemático natural a expresiones estructuradas
- **Ejecución Automática**: Evaluación directa de expresiones matemáticas parseadas
- **Análisis Semántico Avanzado**: Uso de modelos de Hugging Face para comprensión profunda
- **Cálculos Matemáticos**: Derivadas, integrales, resolución de ecuaciones, simplificación
- **Sugerencias Inteligentes**: Recomendaciones para mejorar expresiones matemáticas
- **Validación de Expresiones**: Verificación de sintaxis y corrección matemática
- **Ejemplos Interactivos**: Biblioteca de ejemplos para aprendizaje y testing

Endpoints Disponibles:
--------------------
- POST /math-nlp/parse: Parsea texto matemático natural a formato estructurado
- POST /math-nlp/execute: Parsea y ejecuta expresión matemática en un paso
- POST /math-nlp/suggestions: Obtiene sugerencias para mejorar texto matemático
- GET /math-nlp/operations: Lista operaciones matemáticas soportadas
- POST /math-nlp/evaluate: Evalúa expresión matemática directamente
- POST /math-nlp/derivative: Calcula derivada de una expresión
- POST /math-nlp/integral: Calcula integral de una expresión
- POST /math-nlp/solve: Resuelve ecuaciones
- POST /math-nlp/simplify: Simplifica expresiones matemáticas
- POST /math-nlp/expand: Expande expresiones matemáticas
- POST /math-nlp/factor: Factoriza expresiones matemáticas
- GET /math-nlp/examples: Obtiene ejemplos de consultas NLP matemáticas
- GET /math-nlp/info: Información sobre capacidades del servicio
- POST /math-nlp/semantic-analysis: Análisis semántico avanzado con Hugging Face

Dependencias:
-----------
- FastAPI: Framework web para APIs REST
- app.services.math_nlp: Servicio principal de NLP matemático
- app.models: Modelos de datos para requests/responses
- sympy: Biblioteca de matemáticas simbólicas
- transformers: Modelos de Hugging Face para análisis semántico

Uso del Servicio:
---------------
```python
from fastapi import FastAPI
from app.domains.mathematics.services.math_nlp import router
from app.exceptions.domain.mathematics import MathematicsError

app = FastAPI()
app.include_router(router)

# Ejemplo de parsing
response = await client.post("/math-nlp/parse",
    json={"text": "find the derivative of x squared plus 2x"})

# Ejemplo de ejecución
response = await client.post("/math-nlp/execute",
    json={"text": "solve x plus 3 equals 7"})
```

Consideraciones de Seguridad:
---------------------------
- Validación de entrada para prevenir ejecución de código malicioso
- Límites en complejidad de expresiones para prevenir abuso de recursos
- Logging de todas las operaciones para auditoría y debugging
- Rate limiting para prevenir sobrecarga del servicio
- Validación de sintaxis antes de evaluación matemática

Notas de Implementación:
----------------------
- Utiliza expresiones regulares y diccionarios de keywords para parsing básico
- Integra modelos de transformers para análisis semántico avanzado
- Soporta operaciones simbólicas con SymPy para cálculos precisos
- Implementa sistema de confianza para validar resultados de parsing
- Proporciona sugerencias automáticas para corrección de expresiones
"""

from fastapi import APIRouter, HTTPException
from app.domains.mathematics.services.math_nlp import MathNLPService
from app.models import MathNLPRequest, BaseResponse, MathNLPResult
import logging

# Configuración de logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/math-nlp", tags=["math-nlp"])
service = MathNLPService()

@router.post("/parse", response_model=None)
async def parse_mathematical_text(request: dict):
    """
    Parsea texto matemático natural en lenguaje natural a formato estructurado.

    Este endpoint analiza texto matemático expresado en lenguaje natural y lo convierte
    en una expresión matemática estructurada que puede ser evaluada o manipulada.

    Args:
        request: Objeto MathNLPRequest con el texto a parsear

    Returns:
        MathNLPResult con la expresión parseada, resultado y nivel de confianza

    Raises:
        HTTPException: Si ocurre un error durante el parsing
    """
    try:
        logger.info(f"🔢 Parsing mathematical text: '{request.get('text', '')[:50]}...'")

        result = service.parse_natural_language(request.get('text', ''))

        logger.info(f"✅ Successfully parsed expression with confidence {result['confidence']}")
        return MathNLPResult(
            parsed_expression=result['parsed_expression'],
            result=result.get('result'),
            confidence=result['confidence']
        )

    except MathematicsError as e:
        logger.exception("❌ Error parsing mathematical text")
        raise HTTPException(status_code=400, detail=f"Error parsing mathematical text: {str(e)}") from e

@router.post("/execute", response_model=None)
async def execute_parsed_expression(request: dict):
    """
    Parsea y ejecuta texto matemático en un solo paso.

    Este endpoint combina el parsing y la ejecución de expresiones matemáticas,
    proporcionando un flujo simplificado para evaluación directa.

    Args:
        request: Objeto MathNLPRequest con el texto matemático

    Returns:
        BaseResponse con resultados del parsing y ejecución

    Raises:
        HTTPException: Si ocurre un error durante el proceso
    """
    try:
        logger.info(f"⚡ Executing mathematical text: '{request.get('text', '')[:50]}...'")

        # First parse the text
        parsed_result = service.parse_natural_language(request.get('text', ''))

        # Then execute the parsed expression
        execution_result = service.execute_parsed_expression(parsed_result)

        logger.info("✅ Successfully executed mathematical expression")
        return BaseResponse(
            success=True,
            message="Mathematical expression parsed and executed successfully",
            data={
                "parsed": parsed_result,
                "execution": execution_result
            }
        )

    except MathematicsError as e:
        logger.exception("❌ Error executing mathematical expression")
        raise HTTPException(status_code=400, detail=f"Error executing mathematical expression: {str(e)}") from e

@router.post("/suggestions", response_model=None)
async def get_text_suggestions(text: str):
    """
    Obtiene sugerencias para mejorar texto matemático.

    Este endpoint analiza texto matemático y proporciona recomendaciones
    para mejorar claridad, precisión y formato.

    Args:
        text: Texto matemático a analizar

    Returns:
        BaseResponse con sugerencias de mejora

    Raises:
        HTTPException: Si ocurre un error generando sugerencias
    """
    try:
        logger.info(f"💡 Generating suggestions for text: '{text[:50]}...'")

        suggestions = service.suggest_corrections(text)

        logger.info(f"✅ Generated {len(suggestions)} suggestions")
        return BaseResponse(
            success=True,
            message="Suggestions generated successfully",
            data={"text": text, "suggestions": suggestions}
        )

    except MathematicsError as e:
        logger.exception("❌ Error generating suggestions")
        raise HTTPException(status_code=400, detail=f"Error generating suggestions: {str(e)}") from e

@router.get("/operations", response_model=None)
async def get_supported_operations():
    """
    Obtiene la lista de operaciones matemáticas soportadas.

    Returns:
        BaseResponse con lista de operaciones disponibles

    Raises:
        HTTPException: Si ocurre un error obteniendo operaciones
    """
    try:
        operations = service.get_supported_operations()

        logger.info(f"📋 Retrieved {len(operations)} supported operations")
        return BaseResponse(
            success=True,
            message="Supported operations retrieved successfully",
            data={"operations": operations}
        )

    except MathematicsError as e:
        logger.exception("❌ Error getting supported operations")
        raise HTTPException(status_code=500, detail=f"Error getting supported operations: {str(e)}") from e

@router.post("/evaluate", response_model=None)
async def evaluate_expression(expression: str):
    """
    Evaluate a mathematical expression directly
    """
    try:
        result = service._evaluate_expression(expression)
        
        return BaseResponse(
            success=True,
            message="Expression evaluated successfully",
            data={"expression": expression, "result": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/derivative", response_model=None)
async def compute_derivative(expression: str, variable: str = "x"):
    """
    Compute derivative of an expression
    """
    try:
        result = service._compute_derivative(expression, variable)
        
        return BaseResponse(
            success=True,
            message="Derivative computed successfully",
            data={"expression": expression, "variable": variable, "derivative": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/integral", response_model=None)
async def compute_integral(expression: str, variable: str = "x"):
    """
    Compute integral of an expression
    """
    try:
        result = service._compute_integral(expression, variable)
        
        return BaseResponse(
            success=True,
            message="Integral computed successfully",
            data={"expression": expression, "variable": variable, "integral": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/solve", response_model=None)
async def solve_equation(equation: str, variable: str = "x"):
    """
    Solve an equation
    """
    try:
        result = service._solve_equation(equation, variable)
        
        return BaseResponse(
            success=True,
            message="Equation solved successfully",
            data={"equation": equation, "variable": variable, "solutions": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/simplify", response_model=None)
async def simplify_expression(expression: str):
    """
    Simplify a mathematical expression
    """
    try:
        result = service._simplify_expression(expression)
        
        return BaseResponse(
            success=True,
            message="Expression simplified successfully",
            data={"expression": expression, "simplified": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/expand", response_model=None)
async def expand_expression(expression: str):
    """
    Expand a mathematical expression
    """
    try:
        result = service._expand_expression(expression)
        
        return BaseResponse(
            success=True,
            message="Expression expanded successfully",
            data={"expression": expression, "expanded": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/factor", response_model=None)
async def factor_expression(expression: str):
    """
    Factor a mathematical expression
    """
    try:
        result = service._factor_expression(expression)
        
        return BaseResponse(
            success=True,
            message="Expression factored successfully",
            data={"expression": expression, "factored": result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/examples", response_model=None)
async def get_nlp_examples():
    """
    Get examples of natural language mathematical queries
    """
    examples = [
        {
            "text": "find the derivative of x squared plus 2x",
            "expected_operation": "derivative",
            "expected_expression": "x**2 + 2*x"
        },
        {
            "text": "solve x plus 3 equals 7",
            "expected_operation": "solve",
            "expected_expression": "x + 3 - 7"
        },
        {
            "text": "integrate sin of x",
            "expected_operation": "integral",
            "expected_expression": "sin(x)"
        },
        {
            "text": "simplify two times x plus three times x",
            "expected_operation": "simplify",
            "expected_expression": "2*x + 3*x"
        },
        {
            "text": "what is the square root of 16",
            "expected_operation": "evaluate",
            "expected_expression": "sqrt(16)"
        }
    ]
    
    return BaseResponse(
        success=True,
        message="NLP examples retrieved successfully",
        data={"examples": examples}
    )

@router.get("/info")
async def get_nlp_info():
    """
    Get information about mathematical NLP capabilities
    """
    return {
        "description": "Mathematical Natural Language Processing service",
        "supported_operations": [
            "derivative",
            "integral",
            "solve",
            "limit",
            "plot",
            "evaluate",
            "expand",
            "factor",
            "simplify"
        ],
        "capabilities": [
            "Natural language parsing of mathematical expressions",
            "Automatic operation detection",
            "Mathematical keyword recognition",
            "Expression evaluation and manipulation",
            "Suggestion system for text improvement",
            "Confidence scoring for parsed expressions"
        ],
        "examples": [
            "find the derivative of x squared",
            "solve x plus 3 equals 7",
            "integrate sin of x",
            "simplify two x plus three x",
            "what is the square root of 16"
        ]
    }

@router.post("/semantic-analysis", response_model=None)
async def semantic_analysis(request: dict):
    """
    Perform advanced semantic analysis using Hugging Face model.
    """
    try:
        # Pass the request.text as the question parameter
        result = service.process_with_huggingface(request.get('text', ''), question=request.get('text', ''))
        return BaseResponse(
            success=True,
            message="Semantic analysis performed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))