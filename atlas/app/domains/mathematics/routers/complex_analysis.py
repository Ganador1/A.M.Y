"""
Complex Analysis Router

Router FastAPI para operaciones avanzadas de análisis complejo y teoría de funciones.
Proporciona endpoints REST API para funciones complejas, expansiones en series, integración
de contorno y funciones especiales en análisis complejo.

Este router ofrece capacidades sofisticadas de análisis complejo para:
- Expansiones en series de potencias: series de Laurent y Taylor alrededor de puntos
- Cálculo de residuos: computación de residuos en polos y singularidades esenciales
- Integración de contorno: integrales de línea complejas a lo largo de varios contornos
- Funciones especiales: funciones de Bessel, Legendre, Hermite en dominio complejo
- Convergencia de series: prueba de ratio, prueba de raíz y otros criterios de convergencia
- Continuación analítica: extensión de dominios de funciones a través de cortes de rama
- Teoría de potencial complejo: funciones armónicas y flujos de potencial

El router se integra con ComplexAnalysisService para proporcionar
a investigadores e ingenieros herramientas poderosas de análisis complejo para
resolver problemas en física, ingeniería y matemáticas puras.

Endpoints disponibles:
- POST /power-series: Expansión en series de potencias alrededor de puntos complejos
- POST /residue: Cálculo de residuos en polos y singularidades
- POST /contour-integral: Integración de contorno a lo largo de caminos complejos
- POST /bessel-function: Funciones de Bessel de argumento complejo
- POST /legendre-polynomial: Polinomios de Legendre en variables complejas
- POST /hermite-polynomial: Polinomios de Hermite para análisis complejo
- POST /series-convergence: Pruebas de convergencia de series
- POST /analytic-continuation: Continuación analítica a través de dominios
- GET /series-examples: Ejemplos comunes de series complejas y plantillas

Dependencias:
- ComplexAnalysisService: Motor principal de computación de análisis complejo
- SymPy: Análisis complejo simbólico y funciones especiales
- NumPy/SciPy: Computaciones numéricas complejas y funciones especiales
- mpmath: Aritmética compleja de alta precisión
- BaseResponse: Formato de respuesta API estandarizado

Uso típico:
    Todos los endpoints aceptan expresiones complejas y retornan resultados simbólicos
    o numéricos. La integración de contorno soporta caminos circulares
    y personalizados. Las funciones especiales manejan argumentos complejos
    y órdenes para aplicaciones matemáticas avanzadas.
"""

from fastapi import APIRouter, HTTPException, Query
from app.domains.mathematics.services.advanced_algebra_service import AdvancedAlgebraService
from app.domains.mathematics.models import BaseRequest, BaseResponse
from app.exceptions.domain.mathematics import MathematicsError

router = APIRouter(prefix="/complex", tags=["Complex Analysis"])
service = AdvancedAlgebraService()


@router.post("/power-series", response_model=BaseResponse)
async def power_series_expansion(
    function: str = Query(..., description="Mathematical function to expand"),
    variable: str = Query("z", description="Variable of expansion"),
    center: str = Query("0", description="Center of expansion"),
    order: int = Query(6, description="Order of expansion", ge=1, le=20)
):
    """
    Compute the power series expansion of a function around a point.

    **Example:**
    - function: "exp(z)"
    - variable: "z"
    - center: "0"
    - order: 6
    """
    try:
        result = service.power_series_expansion(function, variable, center, order)
        if result.get('status') == 'failed':
            raise HTTPException(status_code=400, detail=result.get('error', 'Expansion failed'))

        return BaseResponse(
            success=True,
            message="Power series expansion computed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/residue", response_model=BaseResponse)
async def calculate_residue(
    function: str = Query(..., description="Complex function"),
    pole: str = Query(..., description="Location of the pole"),
    variable: str = Query("z", description="Complex variable")
):
    """
    Calculate the residue of a function at a given pole.

    **Example:**
    - function: "1/(z-1)"
    - pole: "1"
    - variable: "z"
    """
    try:
        result = service.residue_calculation(function, pole, variable)
        if result.get('status') == 'failed':
            raise HTTPException(status_code=400, detail=result.get('error', 'Residue calculation failed'))

        return BaseResponse(
            success=True,
            message="Residue calculated successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/contour-integral", response_model=BaseResponse)
async def contour_integral(
    function: str = Query(..., description="Function to integrate"),
    contour_type: str = Query("circle", description="Type of contour"),
    center: str = Query("0", description="Center of contour"),
    radius: str = Query("1", description="Radius of contour"),
    variable: str = Query("z", description="Complex variable")
):
    """
    Compute contour integral along different types of contours.

    **Supported contour types:** circle

    **Example:**
    - function: "1/z"
    - contour_type: "circle"
    - center: "0"
    - radius: "1"
    """
    try:
        result = service.contour_integral(function, contour_type, center, radius, variable)
        if result.get('status') in ['failed', 'unsupported']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Contour integral failed'))

        return BaseResponse(
            success=True,
            message="Contour integral computed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bessel-function", response_model=BaseResponse)
async def bessel_function(
    order: float = Query(..., description="Order of Bessel function", ge=0),
    argument: str = Query(..., description="Argument of the function"),
    function_type: str = Query("J", description="Type of Bessel function")
):
    """
    Compute Bessel functions and their properties.

    **Supported types:** J (first kind), Y (second kind), I (modified first), K (modified second)

    **Example:**
    - order: 0
    - argument: "1"
    - function_type: "J"
    """
    try:
        result = service.bessel_function(order, argument, function_type)
        if result.get('status') == 'failed':
            raise HTTPException(status_code=400, detail=result.get('error', 'Bessel function calculation failed'))

        return BaseResponse(
            success=True,
            message="Bessel function computed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/legendre-polynomial", response_model=BaseResponse)
async def legendre_polynomial(
    degree: int = Query(..., description="Degree of polynomial", ge=0, le=20),
    argument: str = Query("x", description="Argument of the polynomial")
):
    """
    Compute Legendre polynomials and their properties.

    **Example:**
    - degree: 2
    - argument: "x"
    """
    try:
        result = service.legendre_polynomial(degree, argument)
        if result.get('status') == 'failed':
            raise HTTPException(status_code=400, detail=result.get('error', 'Legendre polynomial calculation failed'))

        return BaseResponse(
            success=True,
            message="Legendre polynomial computed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hermite-polynomial", response_model=BaseResponse)
async def hermite_polynomial(
    degree: int = Query(..., description="Degree of polynomial", ge=0, le=20),
    argument: str = Query("x", description="Argument of the polynomial")
):
    """
    Compute Hermite polynomials and their properties.

    **Example:**
    - degree: 2
    - argument: "x"
    """
    try:
        result = service.hermite_polynomial(degree, argument)
        if result.get('status') == 'failed':
            raise HTTPException(status_code=400, detail=result.get('error', 'Hermite polynomial calculation failed'))

        return BaseResponse(
            success=True,
            message="Hermite polynomial computed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/series-convergence", response_model=BaseResponse)
async def series_convergence_test(
    series: str = Query(..., description="Series expression"),
    variable: str = Query("n", description="Summation variable"),
    test_type: str = Query("ratio", description="Type of convergence test")
):
    """
    Test convergence of a series using various tests.

    **Supported tests:** ratio, root

    **Example:**
    - series: "1/n**2"
    - variable: "n"
    - test_type: "ratio"
    """
    try:
        result = service.series_convergence_test(series, variable, test_type)
        if result.get('status') in ['failed', 'invalid_test']:
            raise HTTPException(status_code=400, detail=result.get('error', 'Convergence test failed'))

        return BaseResponse(
            success=True,
            message="Series convergence test completed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analytic-continuation", response_model=BaseResponse)
async def analytic_continuation(
    function: str = Query(..., description="Function to continue analytically"),
    original_domain: str = Query(..., description="Original domain of definition"),
    extension_domain: str = Query(..., description="Target domain for extension"),
    variable: str = Query("z", description="Complex variable")
):
    """
    Perform analytic continuation of a function to a larger domain.

    **Example:**
    - function: "sqrt(z)"
    - original_domain: "Re(z) > 0"
    - extension_domain: "C \\ {0}"
    - variable: "z"
    """
    try:
        result = service.analytic_continuation(function, original_domain, extension_domain, variable)
        if result.get('status') == 'failed':
            raise HTTPException(status_code=400, detail=result.get('error', 'Analytic continuation failed'))

        return BaseResponse(
            success=True,
            message="Analytic continuation performed successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/series-examples", response_model=BaseResponse)
async def get_series_examples():
    """
    Get examples of common series in complex analysis.
    """
    try:
        result = service.get_series_examples()
        return BaseResponse(
            success=True,
            message="Series examples retrieved successfully",
            data=result
        )
    except MathematicsError as e:
        raise HTTPException(status_code=500, detail=str(e))
