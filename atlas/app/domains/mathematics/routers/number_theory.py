"""
Router Number Theory para AXIOM - Teoría de Números y Matemática Discreta

Este módulo proporciona endpoints completos para operaciones avanzadas de teoría
de números, incluyendo aritmética modular, factorización, funciones especiales
y análisis de propiedades numéricas para investigación matemática y criptografía.

== CAPACIDADES ==
• Pruebas de primalidad: métodos determinísticos y probabilísticos optimizados
• Factorización prima: factorización completa con multiplicidad
• Funciones divisoras: enumeración completa, conteo y suma de divisores
• Aritmética modular: exponenciación rápida, cálculo de inversos, sistemas de residuos
• Propiedades numéricas: números perfectos, clasificación abundante/deficiente
• Secuencias: Fibonacci, Lucas y otras secuencias de enteros
• Teoría de grupos: generadores de grupos cíclicos y propiedades
• Primitivas criptográficas: exponenciación modular para RSA/Diffie-Hellman

== ENDPOINTS DISPONIBLES ==
• POST /prime-check - Pruebas de primalidad con algoritmos optimizados
• POST /factorization - Factorización prima completa
• POST /gcd - Cálculo del máximo común divisor
• POST /lcm - Cálculo del mínimo común múltiplo
• POST /euler-phi - Función totiente de Euler φ(n)
• POST /fibonacci - Generación de secuencia de Fibonacci
• POST /divisors - Enumeración completa de divisores
• POST /modular-exponentiation - Exponenciación modular rápida
• POST /perfect-check - Clasificación de números perfectos
• POST /operations - Operaciones unificadas de teoría de números
• POST /cyclic-group-generator - Pruebas de generadores de grupos cíclicos
• GET /info - Capacidades del servicio y operaciones soportadas

== DEPENDENCIAS ==
• NumberTheoryService: Motor principal de computación en teoría de números
• SymPy: Computación simbólica y algebraica
• NumPy: Operaciones numéricas eficientes para enteros grandes
• NumberTheoryRequest/Result: Modelos estandarizados para teoría de números
• CyclicGroupGeneratorRequest/Response: Modelos para teoría de grupos

== USO ==
Todos los endpoints aceptan entradas enteras y retornan resultados matemáticamente
precisos. Las operaciones modulares soportan módulos grandes para aplicaciones
criptográficas. Los endpoints de teoría de grupos funcionan con grupos cíclicos
finitos bajo aritmética modular.

== SEGURIDAD ==
• Validación estricta de entradas numéricas y parámetros
• Límites superiores en tamaños de números para prevenir DoS
• Logging detallado de operaciones matemáticas
• Manejo seguro de errores sin exposición de información sensible
• Rate limiting recomendado para operaciones computacionalmente intensivas
"""

from fastapi import APIRouter, HTTPException, Body
from app.domains.mathematics.services.number_theory_service import NumberTheoryService
from app.domains.mathematics.models import BaseRequest, BaseResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import datetime
import contextlib
from app.exceptions.domain.mathematics import MathematicsError

# Configuración de logging
logger = logging.getLogger(__name__)

class PrimeCheckResponse(BaseModel):
    """Respuesta para verificación de primalidad"""
    number: int = Field(..., description="Número a verificar")
    is_prime: bool = Field(..., description="Resultado de la verificación")
    method: str = Field(..., description="Método utilizado para la verificación")
    confidence: Optional[float] = Field(None, description="Confianza para métodos probabilísticos")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp de la operación")

class FactorizationResponse(BaseModel):
    """Respuesta para factorización prima"""
    number: int = Field(..., description="Número a factorizar")
    factors: Dict[int, int] = Field(..., description="Factores primos con multiplicidad")
    prime_factors: List[int] = Field(..., description="Lista de factores primos únicos")
    is_prime: bool = Field(..., description="Si el número es primo")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp de la operación")

class DivisorsResponse(BaseModel):
    """Respuesta para cálculo de divisores"""
    number: int = Field(..., description="Número del cual calcular divisores")
    divisors: List[int] = Field(..., description="Lista completa de divisores")
    count: int = Field(..., description="Cantidad total de divisores")
    sum: int = Field(..., description="Suma de todos los divisores")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp de la operación")

class PerfectNumberResponse(BaseModel):
    """Respuesta para clasificación de números perfectos"""
    number: int = Field(..., description="Número a clasificar")
    is_perfect: bool = Field(..., description="Si es un número perfecto")
    is_abundant: bool = Field(..., description="Si es un número abundante")
    is_deficient: bool = Field(..., description="Si es un número deficiente")
    aliquot_sum: int = Field(..., description="Suma alícuota (suma de divisores propios)")
    classification: str = Field(..., description="Clasificación completa")
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now, description="Timestamp de la operación")

router = APIRouter()
service = NumberTheoryService()

# Definir modelos específicos para teoría de números
class NumberTheoryRequest(BaseRequest):
    number: int
    operation: str
    parameters: dict = {}

class CyclicGroupGeneratorRequest(BaseRequest):
    modulus: int
    order: Optional[int] = None

class NumberTheoryResponse(BaseResponse):
    message: str
    data: Dict[str, Any]

class CyclicGroupGeneratorResponse(BaseResponse):
    generators: List[int]
    modulus: int
    order: int
    properties: dict

@router.post("/prime-check", response_model=NumberTheoryResponse)
async def check_prime(number: int = Body(..., embed=True)):
    """
    🔍 Verificar si un número es primo usando algoritmos optimizados

    Este endpoint determina si un número entero dado es primo, utilizando
    métodos determinísticos eficientes para números pequeños y probabilísticos
    para números grandes. Incluye validación de entrada y logging detallado.

    Args:
        number (int): Número entero a verificar (debe ser positivo)

    Returns:
        BaseResponse: Respuesta con resultado de primalidad y metadatos

    Raises:
        HTTPException: Si el número es inválido o ocurre un error interno

    Example:
        POST /prime-check
        Body: 17
        Response: {"success": true, "message": "Prime check completed", "data": {"number": 17, "is_prime": true}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if number < 2:
            logger.warning(f"🚫 Intento de verificar primalidad de número inválido: {number}")
            raise HTTPException(
                status_code=400,
                detail=f"El número debe ser mayor o igual a 2. Recibido: {number}"
            )

        if number > 10**18:  # Límite para prevenir DoS
            logger.warning(f"🚫 Número demasiado grande para verificación: {number}")
            raise HTTPException(
                status_code=400,
                detail="Número demasiado grande. Máximo soportado: 10^18"
            )

        logger.info(f"🔍 Iniciando verificación de primalidad para: {number}")

        # Realizar verificación
        result = service.is_prime(type('R', (), {'number': number, 'operation': 'is_prime'})())
        is_prime = bool(result.result)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Verificación completada para {number}: {'PRIMO' if is_prime else 'NO PRIMO'} (tiempo: {execution_time:.4f}s)")

        return NumberTheoryResponse(
            success=True,
            message=f"Verificación de primalidad completada para {number}",
            data={
                "number": number,
                "is_prime": is_prime,
                "method": "deterministic" if number < 2**64 else "probabilistic",
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error en verificación de primalidad para {number}: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor durante verificación de primalidad: {str(e)}"
        )

@router.post("/factorization", response_model=NumberTheoryResponse)
async def prime_factorization(number: int = Body(..., embed=True)):
    """
    🔢 Factorizar un número en sus factores primos con multiplicidad completa

    Este endpoint descompone un número entero en sus factores primos, retornando
    tanto la factorización completa como la lista de factores primos únicos.
    Utiliza algoritmos eficientes optimizados para diferentes rangos numéricos.

    Args:
        number (int): Número entero a factorizar (debe ser positivo)

    Returns:
        BaseResponse: Respuesta con factorización completa y metadatos

    Raises:
        HTTPException: Si el número es inválido o ocurre un error interno

    Example:
        POST /factorization
        Body: 60
        Response: {"success": true, "data": {"number": 60, "factors": {"2": 2, "3": 1, "5": 1}, "prime_factors": [2, 3, 5]}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if number < 2:
            logger.warning(f"🚫 Intento de factorizar número inválido: {number}")
            raise HTTPException(
                status_code=400,
                detail=f"El número debe ser mayor o igual a 2. Recibido: {number}"
            )

        if number > 10**15:  # Límite para factorización
            logger.warning(f"🚫 Número demasiado grande para factorización: {number}")
            raise HTTPException(
                status_code=400,
                detail="Número demasiado grande para factorización. Máximo soportado: 10^15"
            )

        logger.info(f"🔢 Iniciando factorización prima de: {number}")

        # Realizar factorización
        result = service.prime_factors(type('R', (), {'number': number, 'operation': 'prime_factors'})())
        factors = result.result.get('factors', {}) if isinstance(result.result, dict) else {}
        prime_factors = list(factors.keys())

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Factorización completada para {number} (tiempo: {execution_time:.4f}s)")

        return NumberTheoryResponse(
            success=True,
            message=f"Factorización prima completada para {number}",
            data={
                "number": number,
                "factors": factors,
                "prime_factors": prime_factors,
                "is_prime": len(prime_factors) == 1 and factors.get(number, 0) == 1,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error en factorización de {number}: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno durante factorización: {str(e)}"
        )

@router.post("/gcd", response_model=NumberTheoryResponse)
async def greatest_common_divisor(a: int = Body(...), b: int = Body(...)):
    """
    Calculate greatest common divisor of two numbers
    """
    try:
        result = service.gcd(a, b)
        
        return NumberTheoryResponse(
            success=True,
            message=f"GCD of {a} and {b} calculated",
            data={"a": a, "b": b, "gcd": result.result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/lcm", response_model=NumberTheoryResponse)
async def least_common_multiple(a: int = Body(...), b: int = Body(...)):
    """
    Calculate least common multiple of two numbers
    """
    try:
        result = service.lcm(a, b)
        
        return NumberTheoryResponse(
            success=True,
            message=f"LCM of {a} and {b} calculated",
            data={"a": a, "b": b, "lcm": result.result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/euler-phi", response_model=NumberTheoryResponse)
async def euler_totient(n: int = Body(..., embed=True)):
    """
    Calculate Euler's totient function φ(n)
    """
    try:
        result = service.euler_totient(type('R', (), {'number': n, 'operation': 'euler_totient'})())
        
        return NumberTheoryResponse(
            success=True,
            message=f"Euler's totient function φ({n}) calculated",
            data={"n": n, "phi": result.result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/fibonacci", response_model=NumberTheoryResponse)
async def fibonacci_sequence(n: int = Body(..., embed=True)):
    """
    Generate Fibonacci sequence up to n terms
    """
    try:
        result = service.fibonacci(type('R', (), {'number': n, 'operation': 'fibonacci'})())
        
        return NumberTheoryResponse(
            success=True,
            message=f"Fibonacci sequence with {n} terms generated",
            data={"n": n, "sequence": result.result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/divisors", response_model=NumberTheoryResponse)
async def get_divisors(number: int = Body(..., embed=True)):
    """
    📊 Calcular todos los divisores de un número entero positivo

    Este endpoint calcula la lista completa de divisores de un número dado,
    incluyendo tanto divisores propios como el número mismo. También calcula
    estadísticas adicionales como cantidad total y suma de divisores.

    Args:
        number (int): Número entero del cual calcular divisores (debe ser positivo)

    Returns:
        BaseResponse: Respuesta con lista de divisores y estadísticas

    Raises:
        HTTPException: Si el número es inválido o ocurre un error interno

    Example:
        POST /divisors
        Body: 12
        Response: {"success": true, "data": {"number": 12, "divisors": [1, 2, 3, 4, 6, 12], "count": 6, "sum": 28}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if number < 1:
            logger.warning(f"🚫 Intento de calcular divisores de número inválido: {number}")
            raise HTTPException(
                status_code=400,
                detail=f"El número debe ser positivo. Recibido: {number}"
            )

        if number > 10**12:  # Límite para cálculo de divisores
            logger.warning(f"🚫 Número demasiado grande para cálculo de divisores: {number}")
            raise HTTPException(
                status_code=400,
                detail="Número demasiado grande. Máximo soportado: 10^12"
            )

        logger.info(f"📊 Calculando divisores de: {number}")

        result = service.divisors(number)
        div_data = result.result if isinstance(result.result, dict) else {}
        divisors = div_data.get('divisors', [])
        divisor_sum = div_data.get('sum', 0)

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Cálculo de divisores completado para {number}: {len(divisors)} divisores (tiempo: {execution_time:.4f}s)")

        return NumberTheoryResponse(
            success=True,
            message=f"Cálculo de divisores completado para {number}",
            data={
                "number": number,
                "divisors": divisors,
                "count": len(divisors),
                "sum": divisor_sum,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error calculando divisores de {number}: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno durante cálculo de divisores: {str(e)}"
        )

@router.post("/modular-exponentiation", response_model=NumberTheoryResponse)
async def modular_exponentiation(base: int = Body(...), exponent: int = Body(...), modulus: int = Body(...)):
    """
    Calculate (base^exponent) mod modulus efficiently
    """
    try:
        result = service.modular_exponentiation(base, exponent, modulus)
        
        return NumberTheoryResponse(
            success=True,
            message=f"Modular exponentiation ({base}^{exponent}) mod {modulus} calculated",
            data={"base": base, "exponent": exponent, "modulus": modulus, "result": result.result}
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/perfect-check", response_model=NumberTheoryResponse)
async def check_perfect_number(number: int = Body(..., embed=True)):
    """
    ✨ Clasificar un número como perfecto, abundante o deficiente

    Este endpoint determina si un número es perfecto (igual a la suma de sus
    divisores propios), abundante (mayor que la suma de sus divisores propios),
    o deficiente (menor que la suma de sus divisores propios).

    Args:
        number (int): Número entero a clasificar (debe ser positivo)

    Returns:
        BaseResponse: Respuesta con clasificación completa y suma alícuota

    Raises:
        HTTPException: Si el número es inválido o ocurre un error interno

    Example:
        POST /perfect-check
        Body: 6
        Response: {"success": true, "data": {"number": 6, "is_perfect": true, "classification": "perfect"}}
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if number < 1:
            logger.warning(f"🚫 Intento de clasificar número inválido: {number}")
            raise HTTPException(
                status_code=400,
                detail=f"El número debe ser positivo. Recibido: {number}"
            )

        if number > 10**8:  # Límite para clasificación de números perfectos
            logger.warning(f"🚫 Número demasiado grande para clasificación: {number}")
            raise HTTPException(
                status_code=400,
                detail="Número demasiado grande. Máximo soportado: 10^8"
            )

        logger.info(f"✨ Clasificando número: {number}")

        req = type('R', (), {'number': number, 'operation': 'perfect_number'})()
        perfect_res = service.perfect_number(req)
        abundant_res = service.abundant_number(req)
        deficient_res = service.deficient_number(req)

        is_perfect = bool(perfect_res.result)
        is_abundant = bool(abundant_res.result)
        is_deficient = bool(deficient_res.result)

        if is_perfect:
            classification = "perfect"
        elif is_abundant:
            classification = "abundant"
        else:
            classification = "deficient"

        div_res = service.divisors(number)
        aliquot_sum = (div_res.result.get('sum', 0) - number) if isinstance(div_res.result, dict) else 0

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        logger.info(f"✅ Clasificación completada para {number}: {classification} (tiempo: {execution_time:.4f}s)")

        return NumberTheoryResponse(
            success=True,
            message=f"Clasificación de número completada para {number}",
            data={
                "number": number,
                "is_perfect": is_perfect,
                "is_abundant": is_abundant,
                "is_deficient": is_deficient,
                "aliquot_sum": aliquot_sum,
                "classification": classification,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.datetime.now().isoformat()
            }
        )

    except HTTPException:
        raise
    except MathematicsError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error clasificando número {number}: {str(e)} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno durante clasificación: {str(e)}"
        )

@router.post("/operations", response_model=NumberTheoryResponse)
async def perform_number_theory_operation(request: NumberTheoryRequest):
    """
    Perform various number theory operations
    """
    try:
        operation = request.operation
        number = request.number
        parameters = getattr(request, 'parameters', {}) or {}

        if operation in ("prime_check", "is_prime"):
            result = service.is_prime(type('R', (), {'number': number, 'operation': operation})())
            operation_result = {"is_prime": result.result}
        elif operation in ("factorization", "prime_factors"):
            result = service.prime_factors(type('R', (), {'number': number, 'operation': operation})())
            operation_result = result.result
        elif operation == "divisors":
            result = service.divisors(number)
            operation_result = result.result
        elif operation in ("euler_totient", "phi"):
            result = service.euler_totient(type('R', (), {'number': number, 'operation': operation})())
            operation_result = {"phi": result.result}
        elif operation == "perfect_check":
            p_res = service.perfect_number(type('R', (), {'number': number, 'operation': operation})())
            operation_result = {"is_perfect": p_res.result}
        elif operation == "gcd":
            b = parameters.get('b', 1)
            result = service.gcd(number, b)
            operation_result = {"gcd": result.result}
        elif operation == "lcm":
            b = parameters.get('b', 1)
            result = service.lcm(number, b)
            operation_result = {"lcm": result.result}
        elif operation == "fibonacci":
            result = service.fibonacci(type('R', (), {'number': number, 'operation': operation})())
            operation_result = {"fibonacci": result.result}
        elif operation == "modular_exponentiation":
            exponent = parameters.get('exponent', 1)
            modulus = parameters.get('modulus', 2)
            result = service.modular_exponentiation(number, exponent, modulus)
            operation_result = {"result": result.result}
        else:
            # Fallback a operaciones unificadas
            result = service.operations(number, operation)
            operation_result = result.result if not isinstance(result.result, NumberTheoryResult) else {"result": result.result}
        
        return NumberTheoryResponse(
            success=True,
            message=f"Number theory operation '{operation}' completed successfully",
            data=operation_result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cyclic-group-generator", response_model=NumberTheoryResponse)
async def check_cyclic_group_generator(request: CyclicGroupGeneratorRequest):
    """
    Find generators of a cyclic group Z*_modulus (multiplicative integers modulo modulus).
    """
    try:
        result = service.cyclic_group_generator(request.modulus, getattr(request, 'order', None))
        data = result.result if isinstance(result.result, dict) else {}
        return NumberTheoryResponse(
            success=True,
            message=f"Cyclic group generators calculated for modulus {request.modulus}",
            data=data
        )
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/info")
async def get_number_theory_info():
    """
    📋 Obtener información completa sobre las capacidades del servicio de teoría de números

    Este endpoint retorna información detallada sobre todas las operaciones
    soportadas por el servicio de teoría de números, incluyendo capacidades,
    algoritmos disponibles y límites de operación.

    Returns:
        dict: Información completa del servicio con capacidades y operaciones soportadas

    Example:
        GET /info
        Response: {"description": "...", "supported_operations": [...], "capabilities": [...]}
    """
    logger.info("📋 Solicitud de información del servicio de teoría de números")

    info = {
        "description": "Servicio completo de teoría de números para AXIOM - Matemáticas Discretas y Criptografía",
        "version": "1.0.0",
        "supported_operations": [
            "prime_check",
            "factorization",
            "gcd",
            "lcm",
            "euler_totient",
            "fibonacci",
            "divisors",
            "modular_exponentiation",
            "perfect_check",
            "cyclic_group_generator"
        ],
        "capabilities": [
            "Pruebas de primalidad determinísticas y probabilísticas",
            "Factorización prima completa con multiplicidad",
            "Cálculo del máximo común divisor (GCD)",
            "Cálculo del mínimo común múltiplo (LCM)",
            "Función totiente de Euler φ(n)",
            "Generación de secuencias de Fibonacci",
            "Enumeración completa de divisores",
            "Exponenciación modular eficiente",
            "Clasificación de números perfectos, abundantes y deficientes",
            "Análisis de generadores de grupos cíclicos"
        ],
        "algorithms": {
            "primality": ["Trial division", "Miller-Rabin", "Deterministic variants"],
            "factorization": ["Pollard rho", "Quadratic sieve", "Trial division"],
            "modular_arithmetic": ["Binary exponentiation", "Extended Euclidean"],
            "group_theory": ["Order calculation", "Generator testing"]
        },
        "limits": {
            "max_prime_check": 10**18,
            "max_factorization": 10**15,
            "max_divisors": 10**12,
            "max_perfect_check": 10**8,
            "max_fibonacci_terms": 10000
        },
        "mathematical_properties": [
            "Resultados matemáticamente precisos",
            "Soporte para enteros arbitrariamente grandes",
            "Validación completa de entradas",
            "Manejo robusto de casos límite"
        ],
        "timestamp": datetime.datetime.now().isoformat()
    }

    logger.info("✅ Información del servicio retornada exitosamente")
    return info
