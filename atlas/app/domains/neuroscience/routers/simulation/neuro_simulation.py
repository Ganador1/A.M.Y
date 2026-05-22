"""
Router Neuro Simulation para AXIOM - Simulación de Sistemas Neuronales

Este módulo proporciona endpoints especializados para la simulación computacional
de sistemas neuronales utilizando motores avanzados como Brian2 y NEURON,
permitiendo modelado detallado de redes neuronales y comportamiento celular.

== CAPACIDADES ==
• Simulación de redes neuronales con Brian2 (hasta 10,000 neuronas)
• Modelado detallado de neuronas individuales con NEURON
• Análisis de conectividad neuronal y dinámica de red
• Simulaciones de tiempo configurable (hasta 10 minutos)
• Integración con servicios de biología computacional

== ENDPOINTS DISPONIBLES ==
• GET /health - Estado de disponibilidad de motores de simulación
• POST /brian2 - Ejecutar simulación de red neuronal con Brian2
• POST /neuron - Ejecutar modelado detallado de neurona con NEURON

== DEPENDENCIAS ==
• ComputationalBiologyService: Servicio principal de biología computacional
• brian2: Motor de simulación neuronal para redes grandes
• neuron: Motor de simulación para modelado detallado de neuronas
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos de solicitud

== USO ==
Este router permite investigación en neurociencia computacional, desde
simulaciones de redes neuronales hasta modelado detallado de células
nerviosas individuales, con parámetros configurables y resultados estructurados.

== SEGURIDAD ==
• Validación estricta de parámetros de simulación
• Límites superiores en tamaño de red y tiempo de simulación
• Logging detallado de operaciones de simulación
• Manejo seguro de errores sin exposición de información sensible
• Rate limiting recomendado para simulaciones intensivas
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

from app.domains.neuroscience.services.computational_biology import ComputationalBiologyService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.neuroscience import NeuroscienceError


router = APIRouter(prefix="/api/neuro-sim", tags=["neuroscience-sim"])


class Brian2Request(BaseModel):
    num_neurons: int = Field(100, ge=1, le=10000)
    sim_time_ms: int = Field(1000, ge=1, le=600000)
    connectivity: float = Field(0.1, ge=0.0, le=1.0)


class NeuronModelRequest(BaseModel):
    soma_length: float = 30.0
    soma_diameter: float = 30.0
    current_amplitude: float = 0.1


# Response Models
class SimulationResponse(BaseModel):
    status: str = Field(..., description="Estado de la simulación")
    message: str = Field(..., description="Mensaje descriptivo")
    data: Optional[Dict[str, Any]] = Field(None, description="Resultados de la simulación")
    timestamp: str = Field(..., description="Timestamp de la respuesta")

class HealthResponse(BaseModel):
    brian2_available: bool = Field(..., description="Disponibilidad del motor Brian2")
    neuron_available: bool = Field(..., description="Disponibilidad del motor NEURON")
    timestamp: str = Field(..., description="Timestamp del check")


@router.get("/health", response_model=HealthResponse)
async def neuro_sim_health():
    """
    Verifica la disponibilidad de los motores de simulación neuronal.

    Evalúa si Brian2 y NEURON están disponibles y correctamente
    configurados para ejecutar simulaciones neuronales.

    Returns:
        Estado de disponibilidad de ambos motores de simulación

    Raises:
        HTTPException: Si hay problemas al verificar la disponibilidad
    """
    try:
        logger.info("🏥 Verificando salud de motores de simulación neuronal")
        svc = ComputationalBiologyService()

        health_data = HealthResponse(
            brian2_available=svc.brian2_available,
            neuron_available=svc.neuron_available,
            timestamp=datetime.now().isoformat()
        )

        logger.info("📊 Estado de motores - Brian2: %s, NEURON: %s",
                   health_data.brian2_available, health_data.neuron_available)
        return health_data

    except NeuroscienceError as e:
        logger.exception("❌ Error verificando salud de simulación neuronal")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/brian2", response_model=SimulationResponse)
async def run_brian2_sim(req: Brian2Request):
    """
    Ejecuta simulación de red neuronal utilizando Brian2.

    Simula una red neuronal con parámetros configurables de tamaño,
    tiempo de simulación y conectividad, utilizando el motor Brian2
    para simulaciones eficientes de redes grandes.

    Args:
        req: Parámetros de la simulación neuronal

    Returns:
        Resultados de la simulación incluyendo actividad neuronal

    Raises:
        HTTPException: Si la simulación falla o parámetros son inválidos
    """
    try:
        logger.info("🧠 Ejecutando simulación Brian2: %d neuronas, %dms, conectividad %.2f",
                   req.num_neurons, req.sim_time_ms, req.connectivity)

        svc = ComputationalBiologyService()
        payload = {
            "num_neurons": req.num_neurons,
            "sim_time_ms": req.sim_time_ms,
            "connectivity": req.connectivity,
        }

        result = await svc.neural_network_simulation(payload)

        if not result.get("success", False):
            logger.error("❌ Simulación Brian2 falló: %s", result.get("error", "Unknown error"))
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Brian2 simulation failed")
            )

        logger.info("✅ Simulación Brian2 completada exitosamente")
        return SimulationResponse(
            status="success",
            message="Brian2 neural simulation completed successfully",
            data=result.get("data"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except NeuroscienceError as e:
        logger.exception("❌ Error inesperado en simulación Brian2")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/neuron", response_model=SimulationResponse)
async def run_neuron_model(req: NeuronModelRequest):
    """
    Ejecuta modelado detallado de neurona utilizando NEURON.

    Simula el comportamiento electrofisiológico de una neurona individual
    con parámetros morfológicos y de estimulación configurables,
    utilizando el motor NEURON para modelado biofísico detallado.

    Args:
        req: Parámetros morfológicos y de estimulación de la neurona

    Returns:
        Resultados del modelado incluyendo potenciales de membrana

    Raises:
        HTTPException: Si el modelado falla o parámetros son inválidos
    """
    try:
        logger.info("🧪 Ejecutando modelado NEURON: soma %.1f×%.1f, corriente %.3f",
                   req.soma_length, req.soma_diameter, req.current_amplitude)

        svc = ComputationalBiologyService()
        payload = {
            "soma_length": req.soma_length,
            "soma_diameter": req.soma_diameter,
            "current_amplitude": req.current_amplitude,
        }

        result = await svc.neuron_detailed_model(payload)

        if not result.get("success", False):
            logger.error("❌ Modelado NEURON falló: %s", result.get("error", "Unknown error"))
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "NEURON modeling failed")
            )

        logger.info("✅ Modelado NEURON completado exitosamente")
        return SimulationResponse(
            status="success",
            message="NEURON neuron modeling completed successfully",
            data=result.get("data"),
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except NeuroscienceError as e:
        logger.exception("❌ Error inesperado en modelado NEURON")
        raise HTTPException(status_code=500, detail="Internal server error") from e
