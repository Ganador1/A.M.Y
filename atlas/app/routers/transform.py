"""
🌊 ROUTER DE TRANSFORMADAS INTEGRALES - AXIOM v4.1
===============================================

Módulo especializado en transformadas matemáticas integrales y procesamiento de señales.
Proporciona una API REST comprehensiva para análisis de Fourier, Laplace, Z-transformadas
y sus aplicaciones en resolución de ecuaciones diferenciales y procesamiento de señales.

**Dominios de aplicación:**
- 🔄 Procesamiento de señales continuas y discretas
- 📊 Análisis de sistemas lineales invariantes en el tiempo (LTI)
- 🧮 Resolución de ecuaciones diferenciales ordinarias (ODE)
- 🎛️ Control automático y teoría de sistemas
- 📡 Procesamiento digital de señales (DSP)
- 🔬 Análisis espectral en física y química
- 🧲 Resonancia magnética nuclear (RMN) y espectroscopía

**Capacidades principales:**
1. **Transformadas de Fourier**: Análisis frecuencial de señales continuas
2. **Transformadas de Laplace**: Análisis de sistemas en dominio complejo
3. **Z-Transformadas**: Procesamiento de señales discretas
4. **DFT/FFT**: Transformadas discretas eficientes para datos muestreados
5. **Resolución ODE**: Solución de ecuaciones diferenciales vía Laplace
6. **Biblioteca de pares**: Referencia de transformadas comunes

**Arquitectura del servicio:**
- **TransformService**: Motor computacional con SymPy y SciPy
- **Modelos Pydantic**: Validación robusta de expresiones matemáticas
- **Logging estructurado**: Seguimiento detallado con emojis descriptivos
- **Manejo de errores**: Excepciones específicas por tipo de transformada
- **Autenticación JWT**: Control de acceso por scopes de transformación

**Endpoints disponibles:**
- POST /api/transform/fourier: Transformada directa de Fourier
- POST /api/transform/inverse-fourier: Transformada inversa de Fourier
- POST /api/transform/laplace: Transformada de Laplace
- POST /api/transform/inverse-laplace: Transformada inversa de Laplace
- POST /api/transform/z-transform: Z-transformada
- POST /api/transform/dft: Transformada discreta de Fourier
- POST /api/transform/idft: Transformada discreta inversa
- POST /api/transform/fft: Transformada rápida de Fourier
- GET /api/transform/pairs/{type}: Pares de transformadas de referencia
- POST /api/transform/solve-ode: Resolución ODE con Laplace

**Ejemplo de uso:**
```python
# Transformada de Fourier
result = await client.post("/api/transform/fourier",
    json={"expression": "exp(-t**2)", "variable": "t"})

# Resolución de ODE
result = await client.post("/api/transform/solve-ode",
    json={"equation": "y'' + 2*y' + y = exp(-t)", "initial_conditions": {"y(0)": 1}})
```

**Dependencias críticas:**
- **SymPy**: Computación simbólica para transformadas analíticas
- **SciPy/NumPy**: Computación numérica para DFT/FFT
- **TransformService**: Servicio core con métodos optimizados
- **Pydantic**: Validación de expresiones y parámetros

**Consideraciones de rendimiento:**
- Transformadas simbólicas: Optimizadas para expresiones analíticas
- DFT/FFT numéricas: Algoritmos O(N log N) para señales grandes
- Caché inteligente: Reutilización de resultados computacionalmente costosos
- Validación sintáctica: Detección temprana de expresiones inválidas

**Integración con AXIOM:**
- Conecta con módulos de análisis de señales y sistemas
- Alimenta pipelines de procesamiento espectral
- Soporta investigación en física matemática y ingeniería
- Interfaz con herramientas de visualización de espectros

**Notas de implementación:**
- Soporte dual analítico/numérico según complejidad
- Validación automática de convergencia para integrales
- Manejo de singularidades y discontinuidades
- Optimización automática para expresiones comunes

**Historial de versiones:**
- v4.0: Implementación básica de transformadas principales
- v4.1: Soporte completo ODE, biblioteca de pares, optimizaciones FFT
- Futuro: Integración con transformadas wavelet y análisis tiempo-frecuencia
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import time

from app.services.transform_service import TransformService
from app.security.auth import require_scopes
from app.exceptions.domain.biology import BiologyError

# Configuración de logging
logger = logging.getLogger(__name__)

# Inicialización del router y servicio
router = APIRouter(prefix="/api/transform", tags=["transform"])
service = TransformService()

# Modelos de request y response

class TransformRequest(BaseModel):
    """Request base para transformadas matemáticas."""
    expression: str = Field(..., description="Expresión matemática a transformar", min_length=1)
    variable: str = Field("t", description="Variable independiente", min_length=1)
    result_variable: Optional[str] = Field(None, description="Variable del resultado (opcional)")

class FourierRequest(TransformRequest):
    """Request específico para transformadas de Fourier."""
    result_variable: Optional[str] = Field("f", description="Variable de frecuencia")
    mode: str = Field("analytical", description="Modo: 'analytical' o 'numerical'")

class LaplaceRequest(TransformRequest):
    """Request específico para transformadas de Laplace."""
    result_variable: Optional[str] = Field("s", description="Variable compleja")
    region_of_convergence: Optional[str] = Field(None, description="Región de convergencia")

class ZTransformRequest(TransformRequest):
    """Request específico para Z-transformadas."""
    result_variable: Optional[str] = Field("z", description="Variable Z")
    causal: bool = Field(True, description="Si la secuencia es causal")

class SignalRequest(BaseModel):
    """Request para señales numéricas (DFT/FFT)."""
    signal: List[float] = Field(..., description="Valores de la señal")
    sampling_rate: float = Field(1.0, description="Frecuencia de muestreo", gt=0)
    window: Optional[str] = Field(None, description="Tipo de ventana (hamming, hanning, etc.)")

class DFTRequest(SignalRequest):
    """Request específico para DFT."""
    normalize: bool = Field(True, description="Normalizar el resultado")

class FFTRequest(SignalRequest):
    """Request específico para FFT."""
    optimize: bool = Field(True, description="Optimizar para potencias de 2")

class ODETransformRequest(BaseModel):
    """Request para resolución de ODE con transformadas."""
    equation: str = Field(..., description="Ecuación diferencial", min_length=1)
    initial_conditions: Optional[Dict[str, float]] = Field(None, description="Condiciones iniciales")
    solve_for: str = Field("y", description="Variable a resolver", min_length=1)

class TransformPairsRequest(BaseModel):
    """Request para obtener pares de transformadas."""
    transform_type: str = Field(..., description="Tipo de transformada")

# Modelos de response

class TransformResponse(BaseModel):
    """Response base para transformadas."""
    transform_type: str
    input_expression: str
    result_expression: str
    computation_mode: str
    symbolic_result: Optional[str]
    numerical_result: Optional[Dict[str, Any]]
    convergence_region: Optional[str]
    execution_time_seconds: float
    timestamp: str

class SignalTransformResponse(BaseModel):
    """Response para transformadas de señales."""
    transform_type: str
    signal_length: int
    sampling_rate: float
    frequencies: List[float]
    magnitudes: List[float]
    phases: List[float]
    power_spectrum: Optional[List[float]]
    execution_time_seconds: float
    timestamp: str

class ODESolutionResponse(BaseModel):
    """Response para soluciones de ODE."""
    equation: str
    solution: str
    particular_solution: Optional[str]
    homogeneous_solution: Optional[str]
    initial_conditions: Optional[Dict[str, float]]
    transform_used: str
    execution_time_seconds: float
    timestamp: str

class TransformPairsResponse(BaseModel):
    """Response para pares de transformadas."""
    transform_type: str
    pairs: List[Dict[str, str]]
    count: int
    execution_time_seconds: float
    timestamp: str

# Endpoints de transformadas

@router.post("/fourier", response_model=TransformResponse)
async def fourier_transform(
    request: FourierRequest,
    current_user: dict = Depends(require_scopes(["transform:compute"]))
) -> TransformResponse:
    """
    🌊 TRANSFORMADA DE FOURIER
    ==========================

    Computa la transformada de Fourier de una función continua en el tiempo,
    convirtiendo del dominio temporal al dominio frecuencial.

    **Parámetros de entrada:**
    - **expression**: Función temporal f(t) a transformar
    - **variable**: Variable temporal (default: 't')
    - **result_variable**: Variable frecuencial (default: 'f')
    - **mode**: Modo de cómputo ('analytical' o 'numerical')

    **Transformada:**
    ```
    F(f) = ∫_{-∞}^∞ f(t) * exp(-j*2π*f*t) dt
    ```

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "fourier",
        "input_expression": "exp(-t**2)",
        "result_expression": "sqrt(pi)*exp(-pi**2*f**2)",
        "computation_mode": "analytical",
        "symbolic_result": "sqrt(pi)*exp(-pi**2*f**2)",
        "execution_time_seconds": 0.145,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación:**
    - **Magnitud |F(f)|**: Contenido frecuencial de la señal
    - **Fase ∠F(f)**: Desplazamiento de fase por frecuencia
    - **Ancho de banda**: Rango frecuencial significativo

    **Códigos de error:**
    - **400**: Expresión inválida, variable no definida
    - **500**: Error en cómputo de la integral
    """
    start_time = time.time()
    logger.info("🌊 Computando transformada de Fourier - Usuario: %s, expr: %s", current_user.get('sub'), request.expression[:50])

    try:
        result = service.fourier_transform(
            expression=request.expression,
            variable=request.variable,
            result_variable=request.result_variable or "f"
        )

        execution_time = time.time() - start_time
        logger.info("✅ Transformada de Fourier completada en %.2fs", execution_time)

        return TransformResponse(
            transform_type="fourier",
            input_expression=request.expression,
            result_expression=result.get("fourier_transform", ""),
            computation_mode="analytical",
            symbolic_result=result.get("simplified"),
            numerical_result=None,
            convergence_region=None,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en transformada de Fourier: %s", str(e))
        raise HTTPException(status_code=500, detail="Error en transformada de Fourier: %s" % str(e)) from e

@router.post("/inverse-fourier", response_model=TransformResponse)
async def inverse_fourier_transform(
    request: FourierRequest,
    current_user: dict = Depends(require_scopes(["transform:compute"]))
) -> TransformResponse:
    """
    🌊 TRANSFORMADA INVERSA DE FOURIER
    ==================================

    Computa la transformada inversa de Fourier, convirtiendo del dominio
    frecuencial al dominio temporal.

    **Parámetros de entrada:**
    - **expression**: Función frecuencial F(f) a transformar
    - **variable**: Variable frecuencial (default: 'f')
    - **result_variable**: Variable temporal (default: 't')
    - **mode**: Modo de cómputo ('analytical' o 'numerical')

    **Transformada inversa:**
    ```
    f(t) = ∫_{-∞}^∞ F(f) * exp(j*2π*f*t) df
    ```

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "inverse_fourier",
        "input_expression": "exp(-pi**2*f**2)",
        "result_expression": "(1/sqrt(pi))*exp(-t**2)",
        "computation_mode": "analytical",
        "symbolic_result": "(1/sqrt(pi))*exp(-t**2)",
        "execution_time_seconds": 0.089,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Propiedades:**
    - **Inversibilidad**: F^(-1)(F(f)) = f(t)
    - **Simetría**: Similar a la transformada directa
    - **Convergencia**: Requiere condiciones de Dirichlet

    **Códigos de error:**
    - **400**: Expresión inválida, convergencia problemática
    - **500**: Error en cómputo de la integral inversa
    """
    start_time = time.time()
    logger.info("🌊 Computando transformada inversa de Fourier - Usuario: %s", current_user.get('sub'))

    try:
        result = service.inverse_fourier_transform(
            expression=request.expression,
            variable=request.variable,
            result_variable=request.result_variable or "t"
        )

        execution_time = time.time() - start_time
        logger.info("✅ Transformada inversa de Fourier completada en %.2fs", execution_time)

        return TransformResponse(
            transform_type="inverse_fourier",
            input_expression=request.expression,
            result_expression=result.get("inverse_transform", ""),
            computation_mode="analytical",
            symbolic_result=result.get("simplified"),
            numerical_result=None,
            convergence_region=None,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en transformada inversa de Fourier: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error en transformada inversa de Fourier: {str(e)}") from e

@router.post("/laplace", response_model=TransformResponse)
async def laplace_transform(
    request: LaplaceRequest,
    current_user: dict = Depends(require_scopes(["transform:compute"]))
) -> TransformResponse:
    """
    🔄 TRANSFORMADA DE LAPLACE
    ==========================

    Computa la transformada de Laplace para análisis de sistemas lineales,
    convirtiendo funciones temporales a funciones complejas.

    **Parámetros de entrada:**
    - **expression**: Función temporal f(t) a transformar
    - **variable**: Variable temporal (default: 't')
    - **result_variable**: Variable compleja (default: 's')
    - **region_of_convergence**: Región de convergencia (opcional)

    **Transformada:**
    ```
    L{f(t)} = ∫₀^∞ f(t) * exp(-s*t) dt
    ```

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "laplace",
        "input_expression": "exp(-a*t)",
        "result_expression": "1/(s+a)",
        "computation_mode": "analytical",
        "symbolic_result": "1/(s+a)",
        "convergence_region": "Re(s) > a",
        "execution_time_seconds": 0.067,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Aplicaciones:**
    - **Análisis de sistemas**: Función de transferencia
    - **Resolución ODE**: Ecuaciones diferenciales lineales
    - **Control automático**: Estabilidad y respuesta

    **Códigos de error:**
    - **400**: Función no causal, región de convergencia inválida
    - **500**: Error en integración, singularidades no tratables
    """
    start_time = time.time()
    logger.info("🔄 Computando transformada de Laplace - Usuario: %s", current_user.get('sub'))

    try:
        result = service.laplace_transform(
            expression=request.expression,
            variable=request.variable,
            result_variable=request.result_variable or "s"
        )

        execution_time = time.time() - start_time
        logger.info("✅ Transformada de Laplace completada en %.2fs", execution_time)

        return TransformResponse(
            transform_type="laplace",
            input_expression=request.expression,
            result_expression=result.get("laplace_transform", ""),
            computation_mode="analytical",
            symbolic_result=result.get("simplified"),
            numerical_result=None,
            convergence_region=result.get("region") or request.region_of_convergence,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en transformada de Laplace: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error en transformada de Laplace: {str(e)}") from e

@router.post("/inverse-laplace", response_model=TransformResponse)
async def inverse_laplace_transform(
    request: LaplaceRequest,
    current_user: dict = Depends(require_scopes(["transform:compute"]))
) -> TransformResponse:
    """
    🔄 TRANSFORMADA INVERSA DE LAPLACE
    ==================================

    Computa la transformada inversa de Laplace utilizando el teorema de residuos
    o métodos numéricos para funciones racionales.

    **Parámetros de entrada:**
    - **expression**: Función compleja F(s) a transformar
    - **variable**: Variable compleja (default: 's')
    - **result_variable**: Variable temporal (default: 't')

    **Transformada inversa:**
    ```
    f(t) = (1/(2πj)) ∮ F(s) * exp(s*t) ds
    ```

    **Métodos de inversión:**
    1. **Fracciones parciales**: Para funciones racionales
    2. **Teorema de residuos**: Contorno complejo
    3. **Transformada de Fourier**: Para casos numéricos

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "inverse_laplace",
        "input_expression": "1/(s**2 + 1)",
        "result_expression": "sin(t)",
        "computation_mode": "analytical",
        "symbolic_result": "sin(t)",
        "execution_time_seconds": 0.089,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Consideraciones:**
    - **Poles**: Determinantes de la respuesta temporal
    - **ROC**: Región de convergencia crítica
    - **Estabilidad**: Poles en semiplano izquierdo

    **Códigos de error:**
    - **400**: Función no invertible, poles en eje imaginario
    - **500**: Error en inversión, convergencia problemática
    """
    start_time = time.time()
    logger.info("🔄 Computando transformada inversa de Laplace - Usuario: %s", current_user.get('sub'))

    try:
        result = service.inverse_laplace_transform(
            expression=request.expression,
            variable=request.variable,
            result_variable=request.result_variable or "t"
        )

        execution_time = time.time() - start_time
        logger.info("✅ Transformada inversa de Laplace completada en %.2fs", execution_time)

        return TransformResponse(
            transform_type="inverse_laplace",
            input_expression=request.expression,
            result_expression=result.get("inverse_transform", ""),
            computation_mode="analytical",
            symbolic_result=result.get("simplified"),
            numerical_result=result.get("numerical"),
            convergence_region=result.get("region"),
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en transformada inversa de Laplace: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error en transformada inversa de Laplace: {str(e)}") from e

@router.post("/z-transform", response_model=TransformResponse)
async def z_transform(
    request: ZTransformRequest,
    current_user: dict = Depends(require_scopes(["transform:compute"]))
) -> TransformResponse:
    """
    🔢 Z-TRANSFORMADA
    ================

    Computa la Z-transformada de secuencias discretas para análisis
    de sistemas de tiempo discreto.

    **Parámetros de entrada:**
    - **expression**: Secuencia x[n] a transformar
    - **variable**: Variable discreta (default: 'n')
    - **result_variable**: Variable Z (default: 'z')
    - **causal**: Si la secuencia es causal (default: true)

    **Transformada:**
    ```
    X(z) = Σ x[n] * z^(-n)  para n ∈ ℤ
    ```

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "z_transform",
        "input_expression": "a**n",
        "result_expression": "z/(z-a)",
        "computation_mode": "analytical",
        "symbolic_result": "z/(z-a)",
        "convergence_region": "|z| > |a|",
        "execution_time_seconds": 0.045,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Propiedades:**
    - **ROC**: Región de convergencia en plano Z
    - **Poles/Ceros**: Determinantes de estabilidad
    - **Respuesta impulsional**: H(z) = Y(z)/X(z)

    **Códigos de error:**
    - **400**: Secuencia no válida, ROC indeterminada
    - **500**: Error en suma infinita, convergencia problemática
    """
    start_time = time.time()
    logger.info("🔢 Computando Z-transformada - Usuario: %s", current_user.get('sub'))

    try:
        result = service.z_transform(
            expression=request.expression,
            variable=request.variable,
            result_variable=request.result_variable or "z"
        )

        execution_time = time.time() - start_time
        logger.info("✅ Z-transformada completada en %.2fs", execution_time)

        return TransformResponse(
            transform_type="z_transform",
            input_expression=request.expression,
            result_expression=result.get("z_transform", ""),
            computation_mode="analytical",
            symbolic_result=result.get("simplified"),
            numerical_result=result.get("numerical"),
            convergence_region=result.get("region"),
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en Z-transformada: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error en Z-transformada: {str(e)}") from e

@router.post("/dft", response_model=SignalTransformResponse)
async def discrete_fourier_transform(
    request: DFTRequest,
    current_user: dict = Depends(require_scopes(["transform:signal"]))
) -> SignalTransformResponse:
    """
    📊 TRANSFORMADA DISCRETA DE FOURIER (DFT)
    ========================================

    Computa la DFT de una señal discreta utilizando el algoritmo directo,
    convirtiendo al dominio frecuencial para análisis espectral.

    **Parámetros de entrada:**
    - **signal**: Valores discretos de la señal
    - **sampling_rate**: Frecuencia de muestreo (Hz)
    - **window**: Tipo de ventana (opcional)
    - **normalize**: Normalizar el resultado

    **Transformada DFT:**
    ```
    X[k] = Σ x[n] * exp(-j*2π*k*n/N)  para k = 0,...,N-1
    ```

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "dft",
        "signal_length": 1024,
        "sampling_rate": 44100,
        "frequencies": [0, 43.1, 86.1, ...],
        "magnitudes": [1.0, 0.8, 0.3, ...],
        "phases": [0, 1.2, -0.5, ...],
        "power_spectrum": [1.0, 0.64, 0.09, ...],
        "execution_time_seconds": 0.234,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación espectral:**
    - **Magnitud**: Contenido frecuencial por bin
    - **Fase**: Relación de fase por frecuencia
    - **Resolución**: fs/N Hz por bin frecuencial

    **Códigos de error:**
    - **400**: Señal vacía, frecuencia de muestreo inválida
    - **500**: Error en computación matricial DFT
    """
    start_time = time.time()
    logger.info("📊 Computando DFT - Usuario: %s, N=%d", current_user.get('sub'), len(request.signal))

    try:
        result = service.discrete_fourier_transform(
            signal=request.signal,
            sampling_rate=request.sampling_rate
        )

        execution_time = time.time() - start_time
        logger.info("✅ DFT completada en %.2fs", execution_time)

        return SignalTransformResponse(
            transform_type="dft",
            signal_length=len(request.signal),
            sampling_rate=request.sampling_rate,
            frequencies=result.get("frequencies", []),
            magnitudes=result.get("magnitude", []),
            phases=result.get("phase", []),
            power_spectrum=None,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en DFT: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error en DFT: {str(e)}") from e

@router.post("/idft", response_model=SignalTransformResponse)
async def inverse_discrete_fourier_transform(
    request: DFTRequest,
    current_user: dict = Depends(require_scopes(["transform:signal"]))
) -> SignalTransformResponse:
    """
    📊 TRANSFORMADA INVERSA DISCRETA DE FOURIER (IDFT)
    ================================================

    Reconstruye la señal temporal desde sus coeficientes frecuenciales DFT.

    **Parámetros de entrada:**
    - **signal**: Coeficientes DFT (complejos)
    - **sampling_rate**: Frecuencia de muestreo original
    - **normalize**: Si la DFT original fue normalizada

    **Transformada IDFT:**
    ```
    x[n] = (1/N) Σ X[k] * exp(j*2π*k*n/N)  para n = 0,...,N-1
    ```

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "idft",
        "signal_length": 1024,
        "sampling_rate": 44100,
        "frequencies": [],
        "magnitudes": [1.0, 0.8, 0.3, ...],
        "phases": [],
        "execution_time_seconds": 0.156,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Propiedades:**
    - **Perfecta reconstrucción**: x[n] = IDFT(DFT(x[n]))
    - **Complejidad**: O(N²) algoritmo directo
    - **Normalización**: Factor 1/N para consistencia

    **Códigos de error:**
    - **400**: Coeficientes inválidos, longitud incorrecta
    - **500**: Error en reconstrucción temporal
    """
    start_time = time.time()
    logger.info("📊 Computando IDFT - Usuario: %s, N=%d", current_user.get('sub'), len(request.signal))

    try:
        # Convertir la señal a complejos para DFT coefficients
        dft_coeffs = [complex(x, 0) for x in request.signal]
        result = service.inverse_discrete_fourier_transform(
            dft_coefficients=dft_coeffs
        )

        execution_time = time.time() - start_time
        logger.info("✅ IDFT completada en %.2fs", execution_time)

        return SignalTransformResponse(
            transform_type="idft",
            signal_length=len(result.get("reconstructed_signal", [])),
            sampling_rate=request.sampling_rate,
            frequencies=[],
            magnitudes=result.get("reconstructed_signal", []),
            phases=[],
            power_spectrum=None,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en IDFT: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error en IDFT: {str(e)}") from e

@router.post("/fft", response_model=SignalTransformResponse)
async def fast_fourier_transform(
    request: FFTRequest,
    current_user: dict = Depends(require_scopes(["transform:signal"]))
) -> SignalTransformResponse:
    """
    ⚡ TRANSFORMADA RÁPIDA DE FOURIER (FFT)
    =====================================

    Computa la FFT eficiente utilizando algoritmos de divide y vencerás,
    logrando complejidad O(N log N) para señales de longitud potencia de 2.

    **Parámetros de entrada:**
    - **signal**: Valores discretos de la señal
    - **sampling_rate**: Frecuencia de muestreo (Hz)
    - **window**: Tipo de ventana para reducción de leakage
    - **optimize**: Optimizar para potencias de 2

    **Algoritmo FFT:**
    - **Radix-2**: Para N potencia de 2
    - **Cooley-Tukey**: Divide and conquer approach
    - **Complejidad**: O(N log N) vs O(N²) DFT

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "fft",
        "signal_length": 1024,
        "sampling_rate": 44100,
        "frequencies": [0, 43.1, 86.1, ...],
        "magnitudes": [1.0, 0.8, 0.3, ...],
        "phases": [0, 1.2, -0.5, ...],
        "power_spectrum": [1.0, 0.64, 0.09, ...],
        "execution_time_seconds": 0.023,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Ventanas disponibles:**
    - **rectangular**: Sin ventana (leakage máximo)
    - **hamming**: Reducción de leakage moderada
    - **hanning**: Similar a Hamming, coeficientes diferentes
    - **blackman**: Mejor reducción de leakage

    **Códigos de error:**
    - **400**: Longitud no optima para FFT, parámetros inválidos
    - **500**: Error en algoritmo FFT, memoria insuficiente
    """
    start_time = time.time()
    logger.info("⚡ Computando FFT - Usuario: %s, N=%d", current_user.get('sub'), len(request.signal))

    try:
        result = service.fast_fourier_transform(
            signal=request.signal,
            sampling_rate=request.sampling_rate
        )

        execution_time = time.time() - start_time
        logger.info("✅ FFT completada en %.2fs", execution_time)

        return SignalTransformResponse(
            transform_type="fft",
            signal_length=len(request.signal),
            sampling_rate=request.sampling_rate,
            frequencies=result.get("frequencies", []),
            magnitudes=result.get("magnitude", []),
            phases=result.get("phase", []),
            power_spectrum=None,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error en FFT: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error en FFT: {str(e)}") from e

@router.get("/pairs/{transform_type}", response_model=TransformPairsResponse)
async def get_transform_pairs(
    transform_type: str,
    current_user: dict = Depends(require_scopes(["transform:read"]))
) -> TransformPairsResponse:
    """
    📚 PARES DE TRANSFORMADAS DE REFERENCIA
    =====================================

    Retorna una biblioteca de pares de transformadas comunes para referencia
    rápida en análisis y resolución de problemas.

    **Parámetros de consulta:**
    - **transform_type**: Tipo de transformada ('fourier', 'laplace', 'z')

    **Pares disponibles:**
    - **Fourier**: Funciones gaussianas, exponenciales, rect, sinc
    - **Laplace**: Funciones elementales, derivadas, integrales
    - **Z**: Secuencias geométricas, exponenciales, impulsos

    **Respuesta exitosa:**
    ```json
    {
        "transform_type": "fourier",
        "pairs": [
            {"time_domain": "δ(t)", "frequency_domain": "1"},
            {"time_domain": "rect(t)", "frequency_domain": "sinc(f)"},
            {"time_domain": "exp(-a|t|)", "frequency_domain": "2a/(a²+ω²)"}
        ],
        "count": 25,
        "execution_time_seconds": 0.012,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Uso educativo:**
    - **Referencia rápida**: Pares comunes memorizados
    - **Verificación**: Comprobación de resultados
    - **Aprendizaje**: Estudio de propiedades de transformadas

    **Códigos de error:**
    - **400**: Tipo de transformada no soportado
    - **404**: No hay pares disponibles para el tipo solicitado
    """
    start_time = time.time()
    logger.info("📚 Consultando pares de transformadas - Usuario: %s, tipo: %s", current_user.get('sub'), transform_type)

    try:
        result = service.get_transform_pairs(transform_type)

        execution_time = time.time() - start_time
        logger.info("✅ Pares de transformadas obtenidos en %.2fs", execution_time)

        return TransformPairsResponse(
            transform_type=transform_type,
            pairs=result.get("pairs", []),
            count=len(result.get("pairs", [])),
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error obteniendo pares de transformadas: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error obteniendo pares de transformadas: {str(e)}") from e

@router.post("/solve-ode", response_model=ODESolutionResponse)
async def solve_ode_with_laplace(
    request: ODETransformRequest,
    current_user: dict = Depends(require_scopes(["transform:compute"]))
) -> ODESolutionResponse:
    """
    🧮 RESOLUCIÓN DE ODE CON TRANSFORMADAS DE LAPLACE
    ================================================

    Resuelve ecuaciones diferenciales ordinarias lineales utilizando
    el método de transformadas de Laplace para conversión algebraica.

    **Parámetros de entrada:**
    - **equation**: Ecuación diferencial (ej: "y'' + 2*y' + y = exp(-t)")
    - **initial_conditions**: Condiciones iniciales (ej: {"y(0)": 1, "y'(0)": 0})
    - **solve_for**: Variable a resolver (default: 'y')

    **Proceso de resolución:**
    1. Aplicar transformada de Laplace a la ODE
    2. Resolver la ecuación algebraica resultante
    3. Aplicar transformada inversa de Laplace
    4. Aplicar condiciones iniciales

    **Respuesta exitosa:**
    ```json
    {
        "equation": "y'' + 2*y' + y = exp(-t)",
        "solution": "(1/2)*exp(-t) + (1/2)*t*exp(-t)",
        "particular_solution": "(1/2)*t*exp(-t)",
        "homogeneous_solution": "(A + B*t)*exp(-t)",
        "initial_conditions": {"y(0)": 1, "y'(0)": 0},
        "transform_used": "laplace",
        "execution_time_seconds": 0.345,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Tipos de ODE soportados:**
    - **Orden constante**: y'' + a*y' + b*y = f(t)
    - **Coeficientes constantes**: Sistema de ODEs
    - **Condiciones iniciales**: Valores en t=0

    **Códigos de error:**
    - **400**: Ecuación mal formada, condiciones iniciales incompletas
    - **500**: Error en transformación, ecuación no resoluble
    """
    start_time = time.time()
    logger.info("🧮 Resolviendo ODE con Laplace - Usuario: %s", current_user.get('sub'))

    try:
        result = service.solve_ode_with_laplace(
            equation=request.equation,
            initial_conditions=request.initial_conditions
        )

        execution_time = time.time() - start_time
        logger.info("✅ ODE resuelta con Laplace en %.2fs", execution_time)

        return ODESolutionResponse(
            equation=request.equation,
            solution=result.get("time_solution", ""),
            particular_solution=result.get("time_solution"),
            homogeneous_solution="",
            initial_conditions=request.initial_conditions,
            transform_used="laplace",
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error resolviendo ODE: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Error resolviendo ODE: {str(e)}") from e
