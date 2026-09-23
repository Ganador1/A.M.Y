"""
📈 ANÁLISIS DE SERIES TEMPORALES - AXIOM META 4.1
═══════════════════════════════════════════════════════════════════════════════════════════════

Módulo de análisis avanzado de series temporales para la plataforma AXIOM v4.1. Proporciona
herramientas comprehensivas para el análisis temporal de datos, descomposición de tendencias,
modelado predictivo y detección de anomalías en datos secuenciales temporales.

FUNCIONALIDADES PRINCIPALES:
────────────────────────────
• Descomposición de series temporales: tendencia, estacionalidad y componentes residuales
• Pruebas de estacionariedad: ADF, KPSS y otras pruebas estadísticas
• Análisis de autocorrelación: ACF/PACF para identificación de modelos
• Modelado ARIMA/SARIMA: selección automática y ajuste de modelos
• Predicción: pronósticos puntuales e intervalos con límites de confianza
• Detección de anomalías: identificación estadística de valores atípicos
• Análisis espectral: periodograma y análisis en dominio de frecuencia
• Correlación cruzada: relaciones entre múltiples series temporales

ARQUITECTURA TÉCNICA:
─────────────────────
• Framework: FastAPI con validación Pydantic automática
• Computación: Statsmodels para modelado estadístico de series temporales
• Procesamiento: Pandas para manipulación de datos temporales indexados
• Numérico: NumPy/SciPy para análisis espectral y computaciones avanzadas
• ML: Scikit-learn para métodos de forecasting avanzados
• Visualización: Matplotlib/Plotly para gráficos de series temporales
• Validación: Manejo automático de valores faltantes y muestreo irregular

ENDPOINTS DISPONIBLES:
──────────────────────
• POST /decompose: Descomposición de series temporales en componentes
• POST /stationarity-test: Pruebas de estacionariedad y diferenciación
• POST /autocorrelation: Análisis ACF/PACF para identificación de modelos
• POST /arima-fit: Ajuste de modelos ARIMA/SARIMA con diagnósticos
• POST /forecast: Pronóstico de series temporales con intervalos de predicción
• POST /anomaly-detection: Detección estadística de anomalías
• POST /spectral-analysis: Análisis espectral y periodograma
• POST /cross-correlation: Correlación cruzada entre series temporales

VALIDACIONES IMPLEMENTADAS:
──────────────────────────
• Verificación de formato de datos temporales (datetime index)
• Control de frecuencia de muestreo y detección de irregularidades
• Validación de parámetros de modelos (orden ARIMA, etc.)
• Límites de tamaño de datasets para procesamiento eficiente
• Detección automática de valores faltantes y outliers
• Verificación de estacionariedad antes del modelado

INTEGRACIONES:
─────────────
• TimeSeriesService: Servicio core de análisis temporal
• Statsmodels: Librería estadística para series temporales
• Pandas: Manipulación avanzada de datos temporales
• NumPy/SciPy: Computaciones numéricas y análisis espectral
• Scikit-learn: Algoritmos de machine learning para forecasting
• Matplotlib/Seaborn: Generación de visualizaciones temporales

SEGURIDAD Y AUTORIZACIÓN:
─────────────────────────
• Endpoints protegidos con autenticación JWT
• Scopes específicos: time-series:analysis, time-series:forecast
• Validación de permisos para operaciones de modelado predictivo
• Auditoría completa de análisis realizados
• Rate limiting para consultas intensivas de computación

VERSIÓN: AXIOM META 4.1
FECHA: Diciembre 2024
AUTOR: Equipo de Desarrollo AXIOM
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional
from datetime import datetime
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from app.routers.auth import require_scopes
from app.core.bootstrap_logging import logger
from app.services.time_series_service import TimeSeriesService
from app.exceptions.domain.biology import BiologyError

# Modelos de datos para requests y responses

class TimeSeriesData(BaseModel):
    """Datos de serie temporal con timestamps y valores."""
    timestamps: List[str] = Field(..., description="Timestamps en formato ISO 8601")
    values: List[float] = Field(..., description="Valores de la serie temporal")
    frequency: Optional[str] = Field("D", description="Frecuencia de muestreo (D=daily, H=hourly, etc.)")

    @field_validator('values')
    @classmethod
    def validate_lengths_match(cls, v, info):
        if 'timestamps' in info.data and len(v) != len(info.data['timestamps']):
            raise ValueError('timestamps y values deben tener la misma longitud')
        return v

class DecompositionRequest(BaseModel):
    """Request para descomposición de series temporales."""
    data: TimeSeriesData
    model: str = Field("additive", description="Modelo de descomposición (additive/multiplicative)")
    seasonal_periods: Optional[int] = Field(None, description="Período estacional (auto-detectado si None)")

class StationarityTestRequest(BaseModel):
    """Request para pruebas de estacionariedad."""
    data: TimeSeriesData
    test_type: str = Field("adf", description="Tipo de prueba (adf, kpss, pp)")
    regression: str = Field("c", description="Tipo de regresión (c=constante, ct=constante+trend, n=ninguno)")

class AutocorrelationRequest(BaseModel):
    """Request para análisis de autocorrelación."""
    data: TimeSeriesData
    lags: Optional[int] = Field(None, description="Número de lags para analizar")
    alpha: float = Field(0.05, description="Nivel de significancia para intervalos de confianza")

class ARIMAFitRequest(BaseModel):
    """Request para ajuste de modelo ARIMA."""
    data: TimeSeriesData
    order: Optional[tuple] = Field(None, description="Orden (p,d,q) del modelo ARIMA")
    seasonal_order: Optional[tuple] = Field(None, description="Orden estacional (P,D,Q,s)")
    auto_select: bool = Field(True, description="Selección automática de orden si True")

class ForecastRequest(BaseModel):
    """Request para pronóstico de series temporales."""
    data: TimeSeriesData
    steps: int = Field(..., description="Número de pasos a pronosticar")
    confidence_level: float = Field(0.95, description="Nivel de confianza para intervalos")
    model_params: Optional[Dict[str, Any]] = Field(None, description="Parámetros del modelo")

class AnomalyDetectionRequest(BaseModel):
    """Request para detección de anomalías."""
    data: TimeSeriesData
    method: str = Field("zscore", description="Método de detección (zscore, iqr, isolation_forest)")
    threshold: Optional[float] = Field(None, description="Umbral para detección (método específico)")

class SpectralAnalysisRequest(BaseModel):
    """Request para análisis espectral."""
    data: TimeSeriesData
    method: str = Field("periodogram", description="Método de análisis (periodogram, welch)")
    scaling: str = Field("density", description="Escalado del espectro (density, spectrum)")

class CrossCorrelationRequest(BaseModel):
    """Request para correlación cruzada."""
    series1: TimeSeriesData
    series2: TimeSeriesData
    max_lags: Optional[int] = Field(None, description="Máximo número de lags para analizar")

# Modelos de response

class DecompositionResponse(BaseModel):
    """Response para descomposición de series temporales."""
    trend: List[float]
    seasonal: List[float]
    residual: List[float]
    original: List[float]
    model_used: str
    seasonal_periods: int
    diagnostics: Dict[str, Any]
    execution_time_seconds: float
    timestamp: str

class StationarityTestResponse(BaseModel):
    """Response para pruebas de estacionariedad."""
    test_name: str
    test_statistic: float
    p_value: float
    critical_values: Dict[str, float]
    is_stationary: bool
    regression_type: str
    lags_used: int
    execution_time_seconds: float
    timestamp: str

class AutocorrelationResponse(BaseModel):
    """Response para análisis de autocorrelación."""
    acf_values: List[float]
    pacf_values: List[float]
    confidence_intervals: Dict[str, List[float]]
    lags: List[int]
    significant_lags: List[int]
    execution_time_seconds: float
    timestamp: str

class ARIMAFitResponse(BaseModel):
    """Response para ajuste de modelo ARIMA."""
    order: tuple
    seasonal_order: Optional[tuple]
    aic: float
    bic: float
    hqic: float
    coefficients: Dict[str, float]
    diagnostics: Dict[str, Any]
    residuals_stats: Dict[str, float]
    model_summary: str
    execution_time_seconds: float
    timestamp: str

class ForecastResponse(BaseModel):
    """Response para pronóstico de series temporales."""
    forecast_values: List[float]
    confidence_intervals: Dict[str, List[float]]
    forecast_timestamps: List[str]
    model_used: str
    confidence_level: float
    diagnostics: Dict[str, Any]
    execution_time_seconds: float
    timestamp: str

class AnomalyDetectionResponse(BaseModel):
    """Response para detección de anomalías."""
    anomaly_scores: List[float]
    is_anomaly: List[bool]
    anomaly_indices: List[int]
    method_used: str
    threshold_used: float
    total_anomalies: int
    diagnostics: Dict[str, Any]
    execution_time_seconds: float
    timestamp: str

class SpectralAnalysisResponse(BaseModel):
    """Response para análisis espectral."""
    frequencies: List[float]
    power_spectral_density: List[float]
    method_used: str
    scaling: str
    dominant_frequencies: List[float]
    peak_periods: List[float]
    diagnostics: Dict[str, Any]
    execution_time_seconds: float
    timestamp: str

class CrossCorrelationResponse(BaseModel):
    """Response para correlación cruzada."""
    cross_correlation: List[float]
    lags: List[int]
    max_correlation: float
    max_correlation_lag: int
    confidence_intervals: Dict[str, List[float]]
    significant_lags: List[int]
    execution_time_seconds: float
    timestamp: str

router = APIRouter(prefix="/api/time-series", tags=["time-series"])

# Endpoints de análisis de series temporales

@router.post("/decompose", response_model=DecompositionResponse)
async def decompose_time_series(
    request: DecompositionRequest,
    current_user: dict = Depends(require_scopes(["time-series:analysis"]))
) -> DecompositionResponse:
    """
    🔄 DESCOMPOSICIÓN DE SERIES TEMPORALES
    ======================================

    Descompone una serie temporal en sus componentes fundamentales:
    tendencia, estacionalidad y residuales.

    Parámetros:
    - data: Datos de la serie temporal
    - model: Modelo de descomposición (additive/multiplicative)
    - seasonal_periods: Período estacional (auto-detectado si None)

    Retorna:
    - Componentes descompuestos con diagnósticos
    """
    start_time = time.time()
    logger.info(f"🔄 Iniciando descomposición de serie temporal - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.decompose_series(
            timestamps=request.data.timestamps,
            values=request.data.values,
            model=request.model,
            seasonal_periods=request.seasonal_periods
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Descomposición completada en {execution_time:.2f}s")

        return DecompositionResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en descomposición: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en descomposición: {str(e)}")

@router.post("/stationarity-test", response_model=StationarityTestResponse)
async def test_stationarity(
    request: StationarityTestRequest,
    current_user: dict = Depends(require_scopes(["time-series:analysis"]))
) -> StationarityTestResponse:
    """
    📊 PRUEBA DE ESTACIONARIEDAD
    ============================

    Realiza pruebas estadísticas para determinar si una serie temporal
    es estacionaria (ADF, KPSS, Phillips-Perron).

    Parámetros:
    - data: Datos de la serie temporal
    - test_type: Tipo de prueba (adf, kpss, pp)
    - regression: Tipo de regresión para la prueba

    Retorna:
    - Resultados de la prueba con valores críticos
    """
    start_time = time.time()
    logger.info(f"📊 Iniciando prueba de estacionariedad {request.test_type} - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.test_stationarity(
            timestamps=request.data.timestamps,
            values=request.data.values,
            test_type=request.test_type,
            regression=request.regression
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Prueba de estacionariedad completada en {execution_time:.2f}s")

        return StationarityTestResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en prueba de estacionariedad: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en prueba de estacionariedad: {str(e)}")

@router.post("/autocorrelation", response_model=AutocorrelationResponse)
async def analyze_autocorrelation(
    request: AutocorrelationRequest,
    current_user: dict = Depends(require_scopes(["time-series:analysis"]))
) -> AutocorrelationResponse:
    """
    📈 ANÁLISIS DE AUTOCORRELACIÓN
    =============================

    Calcula funciones de autocorrelación (ACF) y autocorrelación parcial (PACF)
    para identificar patrones y determinar órdenes de modelos ARIMA.

    Parámetros:
    - data: Datos de la serie temporal
    - lags: Número de lags para analizar
    - alpha: Nivel de significancia para intervalos

    Retorna:
    - Valores ACF/PACF con intervalos de confianza
    """
    start_time = time.time()
    logger.info(f"📈 Iniciando análisis de autocorrelación - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.analyze_autocorrelation(
            timestamps=request.data.timestamps,
            values=request.data.values,
            lags=request.lags,
            alpha=request.alpha
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Análisis de autocorrelación completado en {execution_time:.2f}s")

        return AutocorrelationResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en análisis de autocorrelación: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en análisis de autocorrelación: {str(e)}")

@router.post("/arima-fit", response_model=ARIMAFitResponse)
async def fit_arima_model(
    request: ARIMAFitRequest,
    current_user: dict = Depends(require_scopes(["time-series:analysis"]))
) -> ARIMAFitResponse:
    """
    🤖 AJUSTE DE MODELO ARIMA
    ========================

    Ajusta modelos ARIMA/SARIMA a series temporales con selección automática
    de parámetros y diagnósticos comprehensivos.

    Parámetros:
    - data: Datos de la serie temporal
    - order: Orden (p,d,q) del modelo ARIMA
    - seasonal_order: Orden estacional (P,D,Q,s)
    - auto_select: Selección automática si True

    Retorna:
    - Modelo ajustado con métricas y diagnósticos
    """
    start_time = time.time()
    logger.info(f"🤖 Iniciando ajuste ARIMA - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.fit_arima_model(
            timestamps=request.data.timestamps,
            values=request.data.values,
            order=request.order,
            seasonal_order=request.seasonal_order,
            auto_select=request.auto_select
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Ajuste ARIMA completado en {execution_time:.2f}s")

        return ARIMAFitResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en ajuste ARIMA: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en ajuste ARIMA: {str(e)}")

@router.post("/forecast", response_model=ForecastResponse)
async def forecast_time_series(
    request: ForecastRequest,
    current_user: dict = Depends(require_scopes(["time-series:forecast"]))
) -> ForecastResponse:
    """
    🔮 PRONÓSTICO DE SERIES TEMPORALES
    =================================

    Genera pronósticos para series temporales usando modelos estadísticos
    con intervalos de confianza y métricas de precisión.

    Parámetros:
    - data: Datos históricos de la serie temporal
    - steps: Número de pasos a pronosticar
    - confidence_level: Nivel de confianza para intervalos
    - model_params: Parámetros específicos del modelo

    Retorna:
    - Pronósticos con intervalos de predicción
    """
    start_time = time.time()
    logger.info(f"🔮 Iniciando pronóstico de {request.steps} pasos - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.forecast_series(
            timestamps=request.data.timestamps,
            values=request.data.values,
            steps=request.steps,
            confidence_level=request.confidence_level,
            model_params=request.model_params
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Pronóstico completado en {execution_time:.2f}s")

        return ForecastResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en pronóstico: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en pronóstico: {str(e)}")

@router.post("/anomaly-detection", response_model=AnomalyDetectionResponse)
async def detect_anomalies(
    request: AnomalyDetectionRequest,
    current_user: dict = Depends(require_scopes(["time-series:analysis"]))
) -> AnomalyDetectionResponse:
    """
    🚨 DETECCIÓN DE ANOMALÍAS
    ========================

    Identifica valores atípicos y anomalías en series temporales usando
    métodos estadísticos y de machine learning.

    Parámetros:
    - data: Datos de la serie temporal
    - method: Método de detección (zscore, iqr, isolation_forest)
    - threshold: Umbral para detección

    Retorna:
    - Anomalías detectadas con scores de confianza
    """
    start_time = time.time()
    logger.info(f"🚨 Iniciando detección de anomalías ({request.method}) - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.detect_anomalies(
            timestamps=request.data.timestamps,
            values=request.data.values,
            method=request.method,
            threshold=request.threshold
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Detección de anomalías completada en {execution_time:.2f}s")

        return AnomalyDetectionResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en detección de anomalías: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en detección de anomalías: {str(e)}")

@router.post("/spectral-analysis", response_model=SpectralAnalysisResponse)
async def analyze_spectrum(
    request: SpectralAnalysisRequest,
    current_user: dict = Depends(require_scopes(["time-series:analysis"]))
) -> SpectralAnalysisResponse:
    """
    🌊 ANÁLISIS ESPECTRAL
    ====================

    Realiza análisis en el dominio de frecuencia para identificar
    periodicidades y patrones cíclicos en series temporales.

    Parámetros:
    - data: Datos de la serie temporal
    - method: Método de análisis (periodogram, welch)
    - scaling: Escalado del espectro

    Retorna:
    - Densidad espectral de potencia con frecuencias dominantes
    """
    start_time = time.time()
    logger.info(f"🌊 Iniciando análisis espectral ({request.method}) - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.analyze_spectrum(
            timestamps=request.data.timestamps,
            values=request.data.values,
            method=request.method,
            scaling=request.scaling
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Análisis espectral completado en {execution_time:.2f}s")

        return SpectralAnalysisResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en análisis espectral: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en análisis espectral: {str(e)}")

@router.post("/cross-correlation", response_model=CrossCorrelationResponse)
async def analyze_cross_correlation(
    request: CrossCorrelationRequest,
    current_user: dict = Depends(require_scopes(["time-series:analysis"]))
) -> CrossCorrelationResponse:
    """
    🔗 ANÁLISIS DE CORRELACIÓN CRUZADA
    =================================

    Analiza las relaciones temporales entre dos series temporales,
    identificando lags de correlación máxima.

    Parámetros:
    - series1: Primera serie temporal
    - series2: Segunda serie temporal
    - max_lags: Máximo número de lags para analizar

    Retorna:
    - Función de correlación cruzada con lags significativos
    """
    start_time = time.time()
    logger.info(f"🔗 Iniciando análisis de correlación cruzada - Usuario: {current_user.get('sub')}")

    try:
        service = TimeSeriesService()
        result = await service.analyze_cross_correlation(
            timestamps1=request.series1.timestamps,
            values1=request.series1.values,
            timestamps2=request.series2.timestamps,
            values2=request.series2.values,
            max_lags=request.max_lags
        )

        execution_time = time.time() - start_time
        logger.info(f"✅ Análisis de correlación cruzada completado en {execution_time:.2f}s")

        return CrossCorrelationResponse(
            **result,
            execution_time_seconds=execution_time,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error en correlación cruzada: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en correlación cruzada: {str(e)}")
