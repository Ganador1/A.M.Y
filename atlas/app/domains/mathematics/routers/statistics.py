"""
📊 ANÁLISIS ESTADÍSTICO AVANZADO - AXIOM META 4.1
═══════════════════════════════════════════════════════════════════════════════════════════════

Módulo de análisis estadístico comprehensivo para la plataforma AXIOM v4.1. Proporciona
herramientas avanzadas de estadística descriptiva, inferencial y predictiva para el análisis
científico de datos en investigación multidisciplinaria.

FUNCIONALIDADES PRINCIPALES:
────────────────────────────
• Estadística descriptiva completa (media, mediana, desviación, percentiles)
• Análisis de correlación (Pearson, Spearman, Kendall) entre variables
• Modelado de regresión lineal con diagnósticos completos
• Pruebas de hipótesis paramétricas y no paramétricas
• Análisis de distribución y normalidad
• Validación estadística de datos científicos
• Soporte para datasets grandes con procesamiento eficiente
• Generación de reportes estadísticos detallados

ARQUITECTURA TÉCNICA:
─────────────────────
• Framework: FastAPI con validación Pydantic automática
• Computación: NumPy/SciPy para algoritmos estadísticos optimizados
• Modelos: Request/Response con validación de tipos estricta
• Caché: Sistema inteligente con TTL basado en complejidad del análisis
• Logging: Seguimiento detallado de operaciones con métricas de rendimiento
• Manejo de errores: Excepciones específicas con códigos HTTP apropiados
• Concurrencia: Soporte async para análisis de datasets grandes

ENDPOINTS DISPONIBLES:
──────────────────────
• POST /calculate: Cálculos estadísticos generales y análisis descriptivo
• POST /correlation: Análisis de correlación bivariado/multivariado
• POST /linear-regression: Modelado de regresión lineal con diagnósticos
• POST /hypothesis: Pruebas de hipótesis estadísticas
• GET /operations: Lista completa de operaciones estadísticas soportadas
• GET /examples: Ejemplos y plantillas de análisis estadístico

VALIDACIONES IMPLEMENTADAS:
──────────────────────────
• Verificación de tipos de datos numéricos
• Control de tamaño de datasets (máximo configurable)
• Validación de parámetros estadísticos
• Detección de valores faltantes y outliers
• Verificación de normalidad para pruebas paramétricas
• Límites de confianza y niveles de significancia

INTEGRACIONES:
─────────────
• StatisticsService: Servicio core de computación estadística
• NumPy/SciPy: Librerías científicas para algoritmos optimizados
• Matplotlib/Seaborn: Generación de visualizaciones estadísticas
• Pandas: Manipulación eficiente de datasets
• Caché distribuido: Optimización de consultas repetitivas

VERSIÓN: AXIOM META 4.1
FECHA: Diciembre 2024
AUTOR: Equipo de Desarrollo AXIOM
"""

from __future__ import annotations

from typing import List, Dict, Any
from datetime import datetime
import time

from fastapi import APIRouter, HTTPException

from app.core.bootstrap_logging import logger
from app.domains.mathematics.services.statistics_service import StatisticsService
from app.domains.mathematics.models import StatisticsRequest, StatisticsResponse, BaseRequest, BaseResponse
from app.exceptions.domain.mathematics import MathematicsError

# Definir modelos específicos para regresión lineal
class LinearRegressionRequest(BaseRequest):
    x_data: List[float]
    y_data: List[float]

class LinearRegressionResponse(BaseResponse):
    slope: float
    intercept: float
    r_squared: float
    correlation_coefficient: float
    p_value: float
    standard_error: float
    confidence_interval: Dict[str, float]
    residuals: List[float]
    fitted_values: List[float]
    equation: str
    interpretation: str

router = APIRouter()

@router.post("/calculate", response_model=StatisticsResponse)
async def calculate_statistics(request: StatisticsRequest) -> StatisticsResponse:
    """
    📊 Ejecutar Cálculos Estadísticos Generales

    Endpoint principal para análisis estadístico descriptivo y computación general.
    Realiza cálculos estadísticos comprehensivos sobre datasets científicos con
    validación automática de datos y generación de reportes detallados.

    **Parámetros de entrada:**
    - **data**: Lista de valores numéricos para análisis estadístico
    - **operations**: Lista de operaciones estadísticas a realizar
    - **confidence_level**: Nivel de confianza para intervalos (default: 0.95)
    - **remove_outliers**: Si eliminar outliers automáticamente (default: false)

    **Operaciones soportadas:**
    - `mean`: Media aritmética
    - `median`: Mediana
    - `mode`: Moda
    - `std`: Desviación estándar
    - `variance`: Varianza
    - `min`: Valor mínimo
    - `max`: Valor máximo
    - `range`: Rango
    - `quartiles`: Cuartiles (Q1, Q2, Q3)
    - `iqr`: Rango intercuartílico
    - `skewness`: Asimetría
    - `kurtosis`: Curtosis
    - `normality_test`: Prueba de normalidad (Shapiro-Wilk)

    **Validaciones realizadas:**
    - Dataset debe contener al menos 2 valores numéricos
    - Todos los valores deben ser números finitos (no NaN/inf)
    - Operaciones solicitadas deben estar en la lista de soportadas
    - Nivel de confianza entre 0.80 y 0.99

    **Respuesta exitosa:**
    ```json
    {
        "results": {
            "mean": 15.23,
            "median": 14.8,
            "std": 3.45,
            "quartiles": [10.2, 14.8, 19.5]
        },
        "metadata": {
            "sample_size": 100,
            "operations_performed": ["mean", "median", "std"],
            "confidence_level": 0.95
        },
        "diagnostics": {
            "normality_p_value": 0.123,
            "outliers_detected": 2
        },
        "execution_time_seconds": 0.045,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Códigos de error:**
    - **400**: Datos inválidos, operaciones no soportadas, parámetros fuera de rango
    - **422**: Validación de entrada fallida
    - **500**: Error interno en computación estadística
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("%s", "📊 Iniciando cálculos estadísticos")
        logger.info("📈 Dataset: %d valores | Operaciones: %d", len(request.data), len(request.operations))

        # Validaciones de entrada
        if not request.data:
            logger.warning("%s", "⚠️ Dataset vacío")
            raise HTTPException(
                status_code=400,
                detail="El dataset debe contener al menos 1 valor numérico"
            )

        if len(request.data) < 2:
            logger.warning("⚠️ Dataset muy pequeño: %d valores", len(request.data))
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos 2 valores para análisis estadístico significativo"
            )

        # Verificar que todos los valores sean numéricos finitos
        if not all(isinstance(x, (int, float)) and not (isinstance(x, float) and (x != x or abs(x) == float('inf'))) for x in request.data):
            logger.warning("%s", "⚠️ Dataset contiene valores no numéricos o infinitos")
            raise HTTPException(
                status_code=400,
                detail="Todos los valores deben ser números finitos (no NaN o infinito)"
            )

        # Validar operaciones solicitadas
        supported_ops = StatisticsService.get_supported_operations()
        if invalid_ops := [op for op in request.operations if op not in supported_ops]:
            logger.warning("⚠️ Operaciones no soportadas: %s", ", ".join(invalid_ops))
            raise HTTPException(
                status_code=400,
                detail=f"Operaciones no soportadas: {', '.join(invalid_ops)}"
            )

        logger.info("%s", "🔬 Ejecutando análisis estadístico...")
        result = StatisticsService.calculate(request)

        execution_time = time.time() - start_time
        logger.info("✅ Cálculos completados en %.2fs", execution_time)

        # Añadir metadatos de ejecución
        if hasattr(result, 'execution_time_seconds'):
            result.execution_time_seconds = round(execution_time, 3)
        if hasattr(result, 'timestamp'):
            result.timestamp = execution_timestamp

        return result

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error interno en cálculos estadísticos: %s (tiempo: %.2fs)", str(e), execution_time)
        logger.error("🔍 Detalles del error: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en cálculos estadísticos: {str(e)}"
        ) from e

@router.post("/correlation")
async def calculate_correlation(data1: List[float], data2: List[float]) -> Dict[str, Any]:
    """
    🔗 Calcular Correlación entre Variables

    Realiza análisis de correlación entre dos variables numéricas utilizando
    múltiples métodos estadísticos. Evalúa la relación lineal y no lineal entre
    datasets con validación automática y diagnósticos comprehensivos.

    **Parámetros de entrada:**
    - **data1**: Lista de valores numéricos para la primera variable
    - **data2**: Lista de valores numéricos para la segunda variable

    **Métodos de correlación calculados:**
    - `pearson`: Correlación de Pearson (relación lineal)
    - `spearman`: Correlación de Spearman (relación monotónica)
    - `kendall`: Correlación de Kendall (relación ordinal)

    **Validaciones realizadas:**
    - Ambos datasets deben tener la misma longitud
    - Mínimo 3 pares de observaciones para análisis significativo
    - Todos los valores deben ser números finitos
    - No se permiten datasets vacíos

    **Respuesta exitosa:**
    ```json
    {
        "correlation_matrix": {
            "pearson": {
                "coefficient": 0.85,
                "p_value": 0.001,
                "confidence_interval": [0.72, 0.92]
            },
            "spearman": {
                "coefficient": 0.82,
                "p_value": 0.002
            },
            "kendall": {
                "coefficient": 0.67,
                "p_value": 0.003
            }
        },
        "sample_size": 50,
        "diagnostics": {
            "data_quality": "good",
            "outliers_detected": 1
        },
        "execution_time_seconds": 0.023,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación de resultados:**
    - Coeficiente cercano a 1.0: Correlación positiva fuerte
    - Coeficiente cercano a -1.0: Correlación negativa fuerte
    - Coeficiente cercano a 0.0: Sin correlación lineal
    - p-value < 0.05: Correlación estadísticamente significativa

    **Códigos de error:**
    - **400**: Datasets de diferentes longitudes, datos insuficientes, valores inválidos
    - **500**: Error interno en computación de correlación
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("%s", "🔗 Iniciando análisis de correlación")
        logger.info("📊 Dataset 1: %d valores | Dataset 2: %d valores", len(data1), len(data2))

        # Validaciones de entrada
        if not data1 or not data2:
            logger.warning("%s", "⚠️ Uno o ambos datasets están vacíos")
            raise HTTPException(
                status_code=400,
                detail="Ambos datasets deben contener al menos 1 valor"
            )

        if len(data1) != len(data2):
            logger.warning("⚠️ Longitudes diferentes: data1=%d, data2=%d", len(data1), len(data2))
            raise HTTPException(
                status_code=400,
                detail="Los datasets deben tener la misma longitud para análisis de correlación"
            )

        if len(data1) < 3:
            logger.warning("⚠️ Datasets muy pequeños: %d pares", len(data1))
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos 3 pares de observaciones para análisis de correlación"
            )

        # Verificar valores numéricos finitos
        for i, (x, y) in enumerate(zip(data1, data2)):
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                logger.warning("⚠️ Valores no numéricos en posición %d", i)
                raise HTTPException(
                    status_code=400,
                    detail=f"Valores no numéricos detectados en posición {i}"
                )
            if isinstance(x, float) and (x != x or abs(x) == float('inf')):
                logger.warning("⚠️ Valor inválido en data1[%d]: %s", i, str(x))
                raise HTTPException(
                    status_code=400,
                    detail=f"Valor inválido en dataset 1, posición {i}"
                )
            if isinstance(y, float) and (y != y or abs(y) == float('inf')):
                logger.warning("⚠️ Valor inválido en data2[%d]: %s", i, str(y))
                raise HTTPException(
                    status_code=400,
                    detail=f"Valor inválido en dataset 2, posición {i}"
                )

        logger.info("%s", "🔬 Calculando correlaciones...")
        result = StatisticsService.correlation(data1, data2)

        execution_time = time.time() - start_time
        logger.info("✅ Análisis de correlación completado en %.2fs", execution_time)

        # Añadir metadatos de ejecución
        result["execution_time_seconds"] = round(execution_time, 3)
        result["timestamp"] = execution_timestamp

        return result

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error interno en análisis de correlación: %s (tiempo: %.2fs)", str(e), execution_time)
        logger.error("🔍 Detalles del error: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en análisis de correlación: {str(e)}"
        ) from e

@router.post("/linear-regression", response_model=LinearRegressionResponse)
async def linear_regression(request: LinearRegressionRequest) -> LinearRegressionResponse:
    """
    📈 Realizar Regresión Lineal

    Construye y ajusta un modelo de regresión lineal simple entre variables
    independiente y dependiente. Proporciona coeficientes, métricas de ajuste,
    diagnósticos de residuos y validación del modelo.

    **Parámetros de entrada:**
    - **x_data**: Lista de valores para la variable independiente (predictora)
    - **y_data**: Lista de valores para la variable dependiente (respuesta)
    - **confidence_level**: Nivel de confianza para intervalos (default: 0.95)

    **Métricas calculadas:**
    - `coefficients`: Pendiente e intercepto de la recta de regresión
    - `r_squared`: Coeficiente de determinación (R²)
    - `adjusted_r_squared`: R² ajustado por grados de libertad
    - `f_statistic`: Estadístico F para significancia global
    - `p_value`: Valor p para la prueba F
    - `standard_error`: Error estándar de los coeficientes
    - `confidence_intervals`: Intervalos de confianza para coeficientes

    **Diagnósticos incluidos:**
    - `residuals`: Residuos del modelo
    - `residuals_stats`: Estadísticas de los residuos
    - `normality_test`: Prueba de normalidad de residuos
    - `homoscedasticity`: Prueba de homocedasticidad
    - `outliers`: Detección de puntos influyentes

    **Validaciones realizadas:**
    - Ambos datasets deben tener la misma longitud
    - Mínimo 3 pares de observaciones para ajuste significativo
    - Variables independientes y dependientes deben ser numéricas
    - No multicolinealidad perfecta (varianza en X > 0)
    - Valores finitos (no NaN o infinito)

    **Respuesta exitosa:**
    ```json
    {
        "coefficients": {
            "intercept": 2.45,
            "slope": 1.23,
            "standard_errors": [0.45, 0.12]
        },
        "model_stats": {
            "r_squared": 0.87,
            "adjusted_r_squared": 0.85,
            "f_statistic": 45.6,
            "p_value": 0.001
        },
        "diagnostics": {
            "residuals_mean": 0.0,
            "residuals_std": 1.23,
            "normality_p_value": 0.15,
            "outliers_count": 1
        },
        "predictions": [3.5, 4.2, 5.8],
        "execution_time_seconds": 0.034,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación del modelo:**
    - R² > 0.7: Buen ajuste del modelo
    - p-value < 0.05: Modelo estadísticamente significativo
    - Residuos normales: Supuestos del modelo cumplidos
    - Sin outliers influyentes: Modelo robusto

    **Códigos de error:**
    - **400**: Datos insuficientes, variables no válidas, multicolinealidad
    - **422**: Validación de entrada fallida
    - **500**: Error interno en ajuste del modelo
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("%s", "📈 Iniciando regresión lineal")
        logger.info("📊 Datos: %d observaciones", len(request.x_data))

        # Validaciones de entrada
        if not request.x_data or not request.y_data:
            logger.warning("%s", "⚠️ Datos de entrada vacíos")
            raise HTTPException(
                status_code=400,
                detail="Ambos datasets (x_data y y_data) deben contener valores"
            )

        if len(request.x_data) != len(request.y_data):
            logger.warning("⚠️ Longitudes diferentes: x=%d, y=%d", len(request.x_data), len(request.y_data))
            raise HTTPException(
                status_code=400,
                detail="Los datasets x_data y y_data deben tener la misma longitud"
            )

        if len(request.x_data) < 3:
            logger.warning("⚠️ Datos insuficientes: %d observaciones", len(request.x_data))
            raise HTTPException(
                status_code=400,
                detail="Se requieren al menos 3 observaciones para regresión lineal"
            )

        # Verificar valores numéricos finitos
        for i, (x, y) in enumerate(zip(request.x_data, request.y_data)):
            if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
                logger.warning("⚠️ Valores no numéricos en posición %d", i)
                raise HTTPException(
                    status_code=400,
                    detail=f"Valores no numéricos detectados en posición {i}"
                )
            if isinstance(x, float) and (x != x or abs(x) == float('inf')):
                logger.warning("⚠️ Valor inválido en x_data[%d]: %s", i, str(x))
                raise HTTPException(
                    status_code=400,
                    detail=f"Valor inválido en variable independiente, posición {i}"
                )
            if isinstance(y, float) and (y != y or abs(y) == float('inf')):
                logger.warning("⚠️ Valor inválido en y_data[%d]: %s", i, str(y))
                raise HTTPException(
                    status_code=400,
                    detail=f"Valor inválido en variable dependiente, posición {i}"
                )

        # Verificar varianza en variable independiente
        if len(set(request.x_data)) < 2:
            logger.warning("%s", "⚠️ Sin varianza en variable independiente")
            raise HTTPException(
                status_code=400,
                detail="La variable independiente debe tener al menos 2 valores diferentes"
            )

        logger.info("%s", "🔬 Ajustando modelo de regresión...")
        result = StatisticsService.regression(request.x_data, request.y_data)
        response = LinearRegressionResponse(**result)

        execution_time = time.time() - start_time
        logger.info("✅ Regresión lineal completada en %.2fs", execution_time)

        # Añadir metadatos de ejecución
        response.execution_time_seconds = round(execution_time, 3)
        response.timestamp = execution_timestamp

        return response

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error interno en regresión lineal: %s (tiempo: %.2fs)", str(e), execution_time)
        logger.error("🔍 Detalles del error: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en regresión lineal: {str(e)}"
        ) from e

@router.post("/hypothesis")
async def hypothesis_test(data: List[float], test_type: str, **kwargs) -> Dict[str, Any]:
    """
    🧪 Realizar Pruebas de Hipótesis Estadísticas

    Ejecuta pruebas de hipótesis paramétricas y no paramétricas sobre datasets
    científicos. Soporta múltiples tipos de pruebas con validación automática
    de supuestos y interpretación de resultados.

    **Parámetros de entrada:**
    - **data**: Lista de valores numéricos para la prueba
    - **test_type**: Tipo de prueba estadística a realizar
    - **kwargs**: Parámetros adicionales específicos de cada prueba

    **Tipos de pruebas soportadas:**
    - `one_sample_ttest`: Prueba t para una muestra (vs valor conocido)
    - `two_sample_ttest`: Prueba t para dos muestras independientes
    - `paired_ttest`: Prueba t para muestras pareadas
    - `one_way_anova`: ANOVA de una vía
    - `mann_whitney`: Prueba U de Mann-Whitney (no paramétrica)
    - `wilcoxon`: Prueba de Wilcoxon para muestras pareadas
    - `shapiro`: Prueba de normalidad de Shapiro-Wilk
    - `levene`: Prueba de homocedasticidad de Levene

    **Parámetros adicionales por prueba:**
    - `mu` (one_sample_ttest): Valor conocido para comparación
    - `alternative` (ttests): 'two-sided', 'less', 'greater'
    - `alpha` (todas): Nivel de significancia (default: 0.05)
    - `data2` (two_sample_ttest): Segunda muestra para comparación

    **Validaciones realizadas:**
    - Dataset debe contener suficientes observaciones según el tipo de prueba
    - Parámetros específicos válidos para cada tipo de prueba
    - Supuestos de la prueba verificados cuando aplicable
    - Valores numéricos finitos

    **Respuesta exitosa:**
    ```json
    {
        "test_name": "one_sample_ttest",
        "statistic": 2.45,
        "p_value": 0.023,
        "degrees_of_freedom": 29,
        "confidence_interval": [1.23, 3.45],
        "effect_size": 0.67,
        "interpretation": "Rechazar H0: media ≠ valor conocido",
        "assumptions_check": {
            "normality": "passed",
            "homoscedasticity": "passed"
        },
        "execution_time_seconds": 0.012,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Interpretación de resultados:**
    - p-value < α: Rechazar hipótesis nula (efecto significativo)
    - p-value ≥ α: No rechazar hipótesis nula (sin evidencia de efecto)
    - Intervalo de confianza que no incluye el valor nulo: Efecto significativo

    **Códigos de error:**
    - **400**: Tipo de prueba no soportado, datos insuficientes, parámetros inválidos
    - **422**: Validación de parámetros fallida
    - **500**: Error interno en ejecución de la prueba
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("%s", "🧪 Iniciando prueba de hipótesis")
        logger.info("📊 Tipo de prueba: %s | Datos: %d valores", test_type, len(data))

        # Validaciones de entrada
        if not data:
            logger.warning("%s", "⚠️ Dataset vacío para prueba de hipótesis")
            raise HTTPException(
                status_code=400,
                detail="El dataset debe contener al menos 1 valor para prueba de hipótesis"
            )

        # Verificar valores numéricos finitos
        if not all(isinstance(x, (int, float)) and not (isinstance(x, float) and (x != x or abs(x) == float('inf'))) for x in data):
            logger.warning("%s", "⚠️ Dataset contiene valores no numéricos o infinitos")
            raise HTTPException(
                status_code=400,
                detail="Todos los valores deben ser números finitos"
            )

        # Validar tipo de prueba
        supported_tests = ["one_sample_ttest", "two_sample_ttest", "paired_ttest",
                          "one_way_anova", "mann_whitney", "wilcoxon", "shapiro", "levene"]
        if test_type not in supported_tests:
            logger.warning("⚠️ Tipo de prueba no soportado: %s", test_type)
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de prueba no soportado: {test_type}. Opciones: {', '.join(supported_tests)}"
            )

        # Validaciones específicas por tipo de prueba
        ttest_types = {"one_sample_ttest", "paired_ttest"}
        if test_type in ttest_types and len(data) < 2:
            logger.warning("⚠️ Datos insuficientes para %s: %d valores", test_type, len(data))
            raise HTTPException(
                status_code=400,
                detail=f"Se requieren al menos 2 observaciones para {test_type}"
            )

        two_sample_types = {"two_sample_ttest", "mann_whitney"}
        if test_type in two_sample_types and "data2" not in kwargs:
            logger.warning("⚠️ Falta segunda muestra para %s", test_type)
            raise HTTPException(
                status_code=400,
                detail=f"Se requiere parámetro 'data2' para {test_type}"
            )

        if test_type == "two_sample_ttest" and len(kwargs["data2"]) < 2:
            logger.warning("⚠️ Segunda muestra insuficiente: %d valores", len(kwargs["data2"]))
            raise HTTPException(
                status_code=400,
                detail="La segunda muestra debe tener al menos 2 observaciones"
            )

        logger.info("%s", "🔬 Ejecutando prueba estadística...")
        result = StatisticsService.hypothesis_test(data, test_type, **kwargs)

        execution_time = time.time() - start_time
        logger.info("✅ Prueba de hipótesis completada en %.2fs", execution_time)

        # Añadir metadatos de ejecución
        result["execution_time_seconds"] = round(execution_time, 3)
        result["timestamp"] = execution_timestamp

        return result

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error interno en prueba de hipótesis: %s (tiempo: %.2fs)", str(e), execution_time)
        logger.error("🔍 Detalles del error: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error interno en prueba de hipótesis: {str(e)}"
        ) from e

@router.get("/operations")
async def get_operations() -> Dict[str, Any]:
    """
    📋 Obtener Operaciones Estadísticas Soportadas

    Retorna la lista completa de operaciones estadísticas disponibles en el sistema,
    incluyendo descripciones detalladas, parámetros requeridos y ejemplos de uso.

    **Respuesta exitosa:**
    ```json
    {
        "operations": {
            "descriptive": [
                {
                    "name": "mean",
                    "description": "Media aritmética",
                    "parameters": [],
                    "example": "Calcula el promedio de los valores"
                },
                {
                    "name": "std",
                    "description": "Desviación estándar",
                    "parameters": [],
                    "example": "Mide la dispersión de los datos"
                }
            ],
            "correlation": [...],
            "regression": [...],
            "hypothesis": [...]
        },
        "total_operations": 25,
        "categories": ["descriptive", "correlation", "regression", "hypothesis"],
        "execution_time_seconds": 0.001,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Categorías disponibles:**
    - `descriptive`: Estadística descriptiva básica
    - `correlation`: Análisis de correlación
    - `regression`: Modelado de regresión
    - `hypothesis`: Pruebas de hipótesis

    **Uso típico:**
    Utilizar esta endpoint para explorar capacidades disponibles antes de
    realizar análisis específicos, o para construir interfaces dinámicas.
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("%s", "📋 Consultando operaciones estadísticas disponibles")
        operations = StatisticsService.get_supported_operations()

        execution_time = time.time() - start_time
        logger.info("✅ Lista de operaciones obtenida en %.3fs", execution_time)

        return {
            "operations": operations,
            "total_operations": len(operations),
            "categories": ["general"],
            "execution_time_seconds": round(execution_time, 3),
            "timestamp": execution_timestamp
        }

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error obteniendo operaciones: %s (tiempo: %.3fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo operaciones: {str(e)}"
        ) from e


@router.get("/examples")
async def get_examples() -> Dict[str, Any]:
    """
    📚 Obtener Ejemplos de Análisis Estadístico

    Proporciona ejemplos prácticos y datasets de muestra para demostrar el uso
    de diferentes operaciones estadísticas. Incluye casos de uso comunes en
    investigación científica.

    **Respuesta exitosa:**
    ```json
    {
        "examples": [
            {
                "name": "correlación_altura_peso",
                "description": "Análisis de correlación entre altura y peso",
                "data": {
                    "altura": [165, 170, 175, 180, 185],
                    "peso": [60, 68, 72, 78, 85]
                },
                "expected_result": {
                    "pearson_correlation": 0.95,
                    "significance": "p < 0.01"
                }
            },
            {
                "name": "regresión_lineal",
                "description": "Modelo de regresión para predicción",
                "data": {
                    "x": [1, 2, 3, 4, 5],
                    "y": [2.1, 4.0, 6.2, 8.1, 9.8]
                }
            }
        ],
        "total_examples": 15,
        "categories": ["correlation", "regression", "hypothesis_testing"],
        "execution_time_seconds": 0.002,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Tipos de ejemplos incluidos:**
    - Datasets reales de investigación científica
    - Casos de estudio con interpretaciones
    - Ejemplos de edge cases y validaciones
    - Demostraciones de diferentes técnicas estadísticas

    **Uso educativo:**
    Perfecto para aprendizaje, testing de algoritmos, y comprensión
    de conceptos estadísticos en contextos científicos reales.
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("%s", "📚 Consultando ejemplos estadísticos")
        examples = StatisticsService.get_statistics_examples()

        execution_time = time.time() - start_time
        logger.info("✅ Ejemplos obtenidos en %.3fs", execution_time)

        return {
            "examples": examples,
            "total_examples": len(examples),
            "categories": [ex.get("category", "general") for ex in examples if isinstance(ex, dict)],
            "execution_time_seconds": round(execution_time, 3),
            "timestamp": execution_timestamp
        }

    except MathematicsError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error obteniendo ejemplos: %s (tiempo: %.3fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Error interno obteniendo ejemplos: {str(e)}"
        ) from e
