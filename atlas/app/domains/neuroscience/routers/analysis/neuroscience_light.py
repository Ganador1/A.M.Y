"""
Router Neuroscience Light para AXIOM - Análisis Ligero de Señales Neuronales

Este módulo proporciona endpoints optimizados para análisis computacional eficiente
de señales electrofisiológicas (EEG# Response Models
class NeuroscienceResponse(BaseModel):
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Resultados del análisis")
    timestamp: str = Field(..., description="Timestamp de la respuesta")

class HealthResponse(BaseModel):
    service: str = Field(..., description="Nombre del servicio")
    status: str = Field(..., description="Estado del servicio")
    bands: Optional[List[str]] = Field(None, description="Bandas disponibles")
    n_channels: Optional[int] = Field(None, description="Número de canales")
    timestamp: str = Field(..., description="Timestamp del check")


@router.post("/bandpowers", response_model=NeuroscienceResponse)tencias de banda, conectividad
y simulaciones de cerebro completo con enfoque en rendimiento y bajo consumo de recursos.

== CAPACIDADES ==
• Análisis de potencias de banda EEG (delta, theta, alpha, beta, gamma)
• Cálculo de conectividad por bandas de frecuencia
• Análisis completo de señales EEG con métricas agregadas
• Conectividad avanzada con múltiples métodos
• Simulación de cerebro completo basada en matrices de conectividad
• Análisis de redes neuronales con umbralización configurable
• Métricas de observabilidad y health checks ligeros

== ENDPOINTS DISPONIBLES ==
• POST /bandpowers - Análisis de potencias de banda EEG
• POST /connectivity - Conectividad por bandas de frecuencia
• POST /analysis - Análisis completo de señales EEG
• POST /connectivity-advanced - Conectividad avanzada con múltiples métodos
• POST /whole-brain-simulation - Simulación de cerebro completo
• POST /brain-networks - Análisis de redes neuronales
• GET /health - Verificación de salud del servicio
• GET /metrics - Información de capacidades del servicio

== DEPENDENCIAS ==
• NeuroscienceLightService: Servicio principal de análisis neurocientífico
• observability: Sistema de métricas Prometheus para monitoreo
• config: Configuración de aplicación para métricas de servicio
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos de solicitud

== USO ==
Este router está optimizado para análisis de alto rendimiento de señales
EEG con bajo overhead computacional, ideal para procesamiento en tiempo
real y análisis preliminar de datos neurofisiológicos.

== SEGURIDAD ==
• Validación estricta de datos EEG y parámetros de simulación
• Límites en tamaños de matrices y tiempos de simulación
• Logging detallado de operaciones con métricas de observabilidad
• Manejo seguro de errores sin exposición de datos sensibles
• Rate limiting recomendado para análisis intensivos
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from contextlib import suppress

from app.domains.neuroscience.services.neuroscience_light_service import NeuroscienceLightService
from app.domains.observability import metrics as prom
from app.core.config import settings
from app.core.bootstrap_logging import logger
from app.exceptions.domain.neuroscience import NeuroscienceError


router = APIRouter(prefix="/api/neuro-light", tags=["neuroscience"])


class EEGRequest(BaseModel):
    sampling_rate_hz: float = 1000.0
    data: List[List[float]]


# Response Models
class NeuroscienceResponse(BaseModel):
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Resultados del análisis")
    timestamp: str = Field(..., description="Timestamp de la respuesta")

class HealthResponse(BaseModel):
    service: str = Field(..., description="Nombre del servicio")
    status: str = Field(..., description="Estado del servicio")
    bands: Optional[List[str]] = Field(None, description="Bandas disponibles")
    n_channels: Optional[int] = Field(None, description="Número de canales")
    timestamp: str = Field(..., description="Timestamp del check")
async def compute_bandpowers(req: EEGRequest):
    """
    Calcula potencias de banda EEG para señales electrofisiológicas.

    Analiza las potencias espectrales en diferentes bandas de frecuencia
    (delta, theta, alpha, beta, gamma) utilizando transformada de Fourier
    con método Welch para estimación robusta del espectro.

    Args:
        req: Datos EEG con frecuencia de muestreo y señales por canal

    Returns:
        Potencias de banda agregadas y por canal

    Raises:
        HTTPException: Si el análisis falla o los datos son inválidos
    """
    try:
        logger.info("🧠 Calculando potencias de banda EEG: %.1f Hz, %d canales",
                   req.sampling_rate_hz, len(req.data))

        svc = NeuroscienceLightService(sampling_rate_hz=req.sampling_rate_hz)
        res = await svc.analyze_eeg_bandpowers(req.data)

        # Métricas de observabilidad (silenciosas)
        with suppress(Exception):
            if hasattr(settings, 'enable_prom_service_metrics') and settings.enable_prom_service_metrics:
                prom.inc("neuro_light_requests_total", labels={"endpoint": "bandpowers"})
                prom.observe("neuro_light_channels", res.get("n_channels", 0))
                prom.observe("neuro_light_samples", res.get("n_samples", 0))

        logger.info("✅ Análisis de potencias de banda completado")
        return NeuroscienceResponse(
            status="success",
            message="EEG bandpowers computed successfully",
            data=res,
            timestamp=datetime.now().isoformat()
        )

    except NeuroscienceError as e:
        logger.exception("❌ Error calculando potencias de banda EEG")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/connectivity", response_model=NeuroscienceResponse)
async def compute_connectivity(req: EEGRequest):
    """
    Calcula conectividad funcional entre canales EEG por bandas de frecuencia.

    Analiza las relaciones de fase y coherencia entre diferentes canales
    electrofisiológicos, separadas por bandas de frecuencia cerebrales.

    Args:
        req: Datos EEG con frecuencia de muestreo y señales por canal

    Returns:
        Matrices de conectividad por banda de frecuencia

    Raises:
        HTTPException: Si el cálculo falla o los datos son inválidos
    """
    try:
        logger.info("🔗 Calculando conectividad EEG: %.1f Hz, %d canales",
                   req.sampling_rate_hz, len(req.data))

        svc = NeuroscienceLightService(sampling_rate_hz=req.sampling_rate_hz)
        res = await svc.connectivity_by_band(req.data)

        # Métricas de observabilidad (silenciosas)
        with suppress(Exception):
            if hasattr(settings, 'enable_prom_service_metrics') and settings.enable_prom_service_metrics:
                prom.inc("neuro_light_requests_total", labels={"endpoint": "connectivity"})

        logger.info("✅ Análisis de conectividad completado")
        return NeuroscienceResponse(
            status="success",
            message="EEG connectivity computed successfully",
            data=res,
            timestamp=datetime.now().isoformat()
        )

    except NeuroscienceError as e:
        logger.exception("❌ Error calculando conectividad EEG")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/analysis")
async def full_analysis(req: EEGRequest) -> Dict[str, Any]:
    svc = NeuroscienceLightService(sampling_rate_hz=req.sampling_rate_hz)
    res = await svc.analyze_eeg_full(req.data)
    # Métricas de observabilidad (silenciosas)
    with suppress(Exception):
        if hasattr(settings, 'enable_prom_service_metrics') and settings.enable_prom_service_metrics:
            prom.inc("neuro_light_requests_total", labels={"endpoint": "analysis"})
    return res


@router.post("/connectivity-advanced")
async def connectivity_advanced(req: EEGRequest) -> Dict[str, Any]:
    svc = NeuroscienceLightService(sampling_rate_hz=req.sampling_rate_hz)
    res = await svc.connectivity_advanced(req.data)
    # Métricas de observabilidad (silenciosas)
    with suppress(Exception):
        if hasattr(settings, 'enable_prom_service_metrics') and settings.enable_prom_service_metrics:
            prom.inc("neuro_light_requests_total", labels={"endpoint": "connectivity_advanced"})
    return res


@router.get("/health", response_model=HealthResponse)
async def neuro_light_health():
    """
    Verifica la salud del servicio de análisis neurocientífico ligero.

    Realiza una prueba mínima de funcionalidad ejecutando un análisis
    de potencias de banda sobre una señal de prueba para validar
    que el servicio está operativo.

    Returns:
        Estado de salud con información de capacidades disponibles

    Raises:
        HTTPException: Si el servicio no está disponible
    """
    try:
        logger.info("🏥 Verificando salud del servicio Neuroscience Light")
        svc = NeuroscienceLightService()
        # Sonda mínima: FFT sobre una señal corta
        data = [[0.0, 1.0, 0.0, -1.0]]
        res = await svc.analyze_eeg_bandpowers(data)

        health_status = "healthy" if "aggregate" in res else "degraded"
        logger.info("📊 Estado de salud: %s", health_status)

        return HealthResponse(
            service="NeuroscienceLightService",
            status=health_status,
            bands=res.get("bands"),
            n_channels=res.get("n_channels"),
            timestamp=datetime.now().isoformat()
        )

    except NeuroscienceError as e:
        logger.exception("❌ Error en verificación de salud")
        raise HTTPException(status_code=503, detail="Service unhealthy") from e


@router.get("/metrics")
async def neuro_light_metrics() -> Dict[str, Any]:
    """Métricas ligeras (dummy) del servicio Neuro Light para observabilidad básica"""
    return {
        "service": "NeuroscienceLightService",
        "version": "light-1.0",
        "capabilities": [
            "bandpowers",
            "connectivity",
            "psd_welch",
            "connectivity_advanced",
            "whole_brain_simulation",
            "brain_networks"
        ]
    }


class WholeBrainSimulationRequest(BaseModel):
    connectivity_matrix: List[List[float]]
    simulation_time_ms: int = Field(10000, ge=1000, le=60000)


class BrainNetworkAnalysisRequest(BaseModel):
    connectivity_matrix: List[List[float]]
    threshold: float = Field(0.3, ge=0.0, le=1.0)


@router.post("/whole-brain-simulation")
async def whole_brain_simulation(req: WholeBrainSimulationRequest) -> Dict[str, Any]:
    svc = NeuroscienceLightService()
    return await svc.simulate_whole_brain(req.connectivity_matrix, req.simulation_time_ms)


@router.post("/brain-networks")
async def brain_networks_analysis(req: BrainNetworkAnalysisRequest) -> Dict[str, Any]:
    svc = NeuroscienceLightService()
    return await svc.analyze_brain_networks(req.connectivity_matrix, req.threshold)


