"""
Multi-Scale Modeling Router
==========================

Router FastAPI para el servicio de modelado neuronal multi-escala.
Proporciona endpoints para crear, simular y analizar redes neuronales
a diferentes escalas temporales y espaciales.

Endpoints disponibles:
- POST /multi-scale/networks - Crear nueva red neuronal
- POST /multi-scale/simulate - Simular red neuronal
- GET /multi-scale/analyze/{network_id} - Analizar dinámicas de red
- GET /multi-scale/status/{network_id} - Estado de la red
- POST /multi-scale/compare-scales - Comparar diferentes escalas
- GET /multi-scale/networks - Listar todas las redes
- GET /multi-scale/results/{network_id} - Obtener resultados de simulación

Autor: Sistema AXIOM
Fecha: 2024-12-23
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging

from app.domains.neuroscience.services.neuromorphic.multi_scale_modeling import (
from app.exceptions.domain.neuroscience import NeuroscienceError
    MultiScaleModelingService,
    NetworkParameters,
    SimulationParameters,
    ModelingScale,
    NeuronType
)

logger = logging.getLogger(__name__)

# Instancia global del servicio
multi_scale_service = MultiScaleModelingService()

# Router
router = APIRouter(prefix="/multi-scale", tags=["Multi-Scale Modeling"])


# Modelos Pydantic para requests/responses

class NetworkCreationRequest(BaseModel):
    """Request para crear una red neuronal"""
    network_id: str = Field(..., description="Identificador único de la red")
    n_neurons: int = Field(100, ge=10, le=10000, description="Número de neuronas")
    connectivity_prob: float = Field(0.1, ge=0.0, le=1.0, description="Probabilidad de conectividad")
    synaptic_strength: float = Field(0.5, ge=0.0, le=10.0, description="Fuerza sináptica base")
    exc_inh_ratio: float = Field(0.8, ge=0.0, le=1.0, description="Ratio excitatorio/inhibitorio")
    plasticity_enabled: bool = Field(True, description="Habilitar plasticidad sináptica")
    learning_rate: float = Field(0.01, ge=0.0, le=1.0, description="Tasa de aprendizaje")


class ExternalStimulusModel(BaseModel):
    """Modelo para estímulo externo"""
    type: str = Field("constant", description="Tipo de estímulo: constant, pulse, oscillatory")
    amplitude: float = Field(5.0, description="Amplitud del estímulo")
    target_neurons: List[int] = Field(default_factory=list, description="Neuronas objetivo")
    start_time: Optional[float] = Field(100.0, description="Tiempo de inicio (ms)")
    duration: Optional[float] = Field(50.0, description="Duración (ms)")
    frequency: Optional[float] = Field(10.0, description="Frecuencia para estímulo oscilatorio (Hz)")


class SimulationRequest(BaseModel):
    """Request para simulación"""
    network_id: str = Field(..., description="ID de la red a simular")
    duration: float = Field(1000.0, ge=10.0, le=10000.0, description="Duración de simulación (ms)")
    dt: float = Field(0.01, ge=0.001, le=1.0, description="Paso de tiempo (ms)")
    temperature: float = Field(37.0, ge=0.0, le=50.0, description="Temperatura (°C)")
    noise_level: float = Field(0.1, ge=0.0, le=10.0, description="Nivel de ruido")
    external_stimulus: Optional[ExternalStimulusModel] = Field(None, description="Estímulo externo")


class NetworkResponse(BaseModel):
    """Response para creación/estado de red"""
    network_id: str
    n_neurons: int
    n_synapses: int
    exc_inh_ratio: float
    status: str


class SimulationResponse(BaseModel):
    """Response para simulación"""
    network_id: str
    simulation_time: float
    total_spikes: int
    average_firing_rate: float
    rhythm_analysis: Dict[str, float]
    voltage_traces: List[List[float]]
    spike_times: List[List[float]]
    time_points: List[float]


class NetworkAnalysisResponse(BaseModel):
    """Response para análisis de red"""
    network_id: str
    connectivity_analysis: Dict[str, Any]
    network_properties: Dict[str, Any]


class ScaleComparisonRequest(BaseModel):
    """Request para comparación de escalas"""
    molecular_data: Dict[str, Any] = Field(default_factory=dict, description="Datos moleculares")
    cellular_data: Dict[str, Any] = Field(default_factory=dict, description="Datos celulares")
    network_data: Dict[str, Any] = Field(default_factory=dict, description="Datos de red")


class ScaleComparisonResponse(BaseModel):
    """Response para comparación de escalas"""
    scales_analyzed: List[str]
    temporal_scales: Dict[str, str]
    spatial_scales: Dict[str, str]
    coupling_analysis: Dict[str, str]
    emergent_properties: Dict[str, str]


# Endpoints

@router.post("/networks", response_model=NetworkResponse)
async def create_neural_network(request: NetworkCreationRequest) -> NetworkResponse:
    """
    Crear una nueva red neuronal multi-escala.

    Permite configurar parámetros como número de neuronas, conectividad,
    plasticidad sináptica y características de la red.
    """
    try:
        # Crear parámetros de red
        network_params = NetworkParameters(
            n_neurons=request.n_neurons,
            connectivity_prob=request.connectivity_prob,
            synaptic_strength=request.synaptic_strength,
            exc_inh_ratio=request.exc_inh_ratio,
            plasticity_enabled=request.plasticity_enabled,
            learning_rate=request.learning_rate
        )

        # Crear red
        result = await multi_scale_service.create_network(
            request.network_id,
            network_params
        )

        logger.info(f"✅ Red neuronal '{request.network_id}' creada exitosamente")

        return NetworkResponse(**result)

    except NeuroscienceError as e:
        logger.error(f"❌ Error creando red '{request.network_id}': {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simulate", response_model=SimulationResponse)
async def simulate_neural_network(request: SimulationRequest, background_tasks: BackgroundTasks) -> SimulationResponse:
    """
    Simular una red neuronal existente.

    Ejecuta simulación con parámetros configurables incluyendo duración,
    resolución temporal, ruido y estímulos externos.
    """
    try:
        # Crear parámetros de simulación
        sim_params = SimulationParameters(
            dt=request.dt,
            duration=request.duration,
            temperature=request.temperature,
            noise_level=request.noise_level
        )

        # Preparar estímulo externo si está presente
        external_stimulus = None
        if request.external_stimulus:
            external_stimulus = {
                "type": request.external_stimulus.type,
                "amplitude": request.external_stimulus.amplitude,
                "target_neurons": request.external_stimulus.target_neurons,
                "start_time": request.external_stimulus.start_time,
                "duration": request.external_stimulus.duration,
                "frequency": request.external_stimulus.frequency,
                "dt": request.dt
            }

        # Ejecutar simulación
        result = await multi_scale_service.simulate_network(
            request.network_id,
            sim_params,
            external_stimulus
        )

        logger.info(f"✅ Simulación de '{request.network_id}' completada")

        return SimulationResponse(**result)

    except ValueError as e:
        logger.error(f"❌ Red no encontrada: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except NeuroscienceError as e:
        logger.error(f"❌ Error en simulación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze/{network_id}", response_model=NetworkAnalysisResponse)
async def analyze_network_dynamics(network_id: str) -> NetworkAnalysisResponse:
    """
    Analizar las dinámicas de una red neuronal.

    Proporciona análisis detallado de conectividad, pesos sinápticos,
    distribución de grados y propiedades emergentes de la red.
    """
    try:
        result = await multi_scale_service.analyze_network_dynamics(network_id)

        logger.info(f"✅ Análisis de red '{network_id}' completado")

        return NetworkAnalysisResponse(**result)

    except ValueError as e:
        logger.error(f"❌ Red no encontrada: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except NeuroscienceError as e:
        logger.error(f"❌ Error en análisis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{network_id}", response_model=NetworkResponse)
async def get_network_status(network_id: str) -> NetworkResponse:
    """
    Obtener el estado actual de una red neuronal.

    Retorna información sobre configuración, actividad reciente
    y estado operacional de la red.
    """
    try:
        result = await multi_scale_service.get_network_status(network_id)

        return NetworkResponse(**result)

    except ValueError as e:
        logger.error(f"❌ Red no encontrada: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except NeuroscienceError as e:
        logger.error(f"❌ Error obteniendo estado: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare-scales", response_model=ScaleComparisonResponse)
async def compare_modeling_scales(request: ScaleComparisonRequest) -> ScaleComparisonResponse:
    """
    Comparar diferentes escalas de modelado neuronal.

    Analiza la integración entre escalas molecular, celular y de red,
    identificando propiedades emergentes y acoplamientos multi-escala.
    """
    try:
        result = await multi_scale_service.compare_scales(
            request.molecular_data,
            request.cellular_data,
            request.network_data
        )

        logger.info("✅ Comparación de escalas completada")

        return ScaleComparisonResponse(**result)

    except NeuroscienceError as e:
        logger.error(f"❌ Error en comparación de escalas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/networks")
async def list_neural_networks() -> Dict[str, List[str]]:
    """
    Listar todas las redes neuronales disponibles.

    Retorna una lista de identificadores de todas las redes
    creadas en el servicio.
    """
    try:
        networks = multi_scale_service.list_networks()

        return {
            "networks": networks,
            "count": len(networks)
        }

    except NeuroscienceError as e:
        logger.error(f"❌ Error listando redes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/results/{network_id}")
async def get_simulation_results(network_id: str) -> Dict[str, Any]:
    """
    Obtener resultados de simulación de una red.

    Retorna los resultados más recientes de simulación
    incluyendo actividad, análisis de ritmos y trazos de voltaje.
    """
    try:
        results = multi_scale_service.get_simulation_results(network_id)

        if results is None:
            raise HTTPException(
                status_code=404,
                detail=f"No simulation results found for network '{network_id}'"
            )

        return results

    except HTTPException:
        raise
    except NeuroscienceError as e:
        logger.error(f"❌ Error obteniendo resultados: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scales/info")
async def get_modeling_scales_info() -> Dict[str, Any]:
    """
    Obtener información sobre las escalas de modelado disponibles.

    Retorna descripción de las diferentes escalas temporales y espaciales
    que pueden ser modeladas por el sistema.
    """
    return {
        "available_scales": [scale.value for scale in ModelingScale],
        "neuron_types": [ntype.value for ntype in NeuronType],
        "scale_descriptions": {
            "molecular": {
                "description": "Modelado de canales iónicos y procesos moleculares",
                "temporal_range": "microsegundos a milisegundos",
                "spatial_range": "nanómetros (canales iónicos)",
                "typical_models": ["Hodgkin-Huxley detallado", "Markov chains"]
            },
            "cellular": {
                "description": "Modelado de neuronas individuales",
                "temporal_range": "milisegundos a segundos",
                "spatial_range": "micrómetros (dendritas, soma, axón)",
                "typical_models": ["Hodgkin-Huxley", "Izhikevich", "LIF"]
            },
            "network": {
                "description": "Modelado de circuitos neuronales",
                "temporal_range": "segundos a minutos",
                "spatial_range": "milímetros a centímetros",
                "typical_models": ["Redes de neuronas interconectadas"]
            },
            "population": {
                "description": "Modelado de poblaciones neuronales",
                "temporal_range": "segundos a horas",
                "spatial_range": "centímetros (áreas cerebrales)",
                "typical_models": ["Modelos de campo neural", "Wilson-Cowan"]
            },
            "system": {
                "description": "Modelado de sistemas cerebrales completos",
                "temporal_range": "minutos a días",
                "spatial_range": "cerebro completo",
                "typical_models": ["Modelos cerebrales globales"]
            }
        },
        "coupling_mechanisms": {
            "bottom_up": "Propiedades moleculares afectan dinámicas de red",
            "top_down": "Actividad de red modula canales moleculares",
            "horizontal": "Interacciones entre escalas similares"
        }
    }


@router.delete("/networks/{network_id}")
async def delete_neural_network(network_id: str) -> Dict[str, str]:
    """
    Eliminar una red neuronal del servicio.

    Remueve la red y todos sus datos asociados
    del servicio de modelado multi-escala.
    """
    try:
        if network_id not in multi_scale_service.networks:
            raise HTTPException(
                status_code=404,
                detail=f"Network '{network_id}' not found"
            )

        # Eliminar red
        del multi_scale_service.networks[network_id]

        # Eliminar resultados si existen
        result_key = f"{network_id}_latest"
        if result_key in multi_scale_service.simulation_results:
            del multi_scale_service.simulation_results[result_key]

        logger.info(f"✅ Red '{network_id}' eliminada exitosamente")

        return {
            "message": f"Network '{network_id}' deleted successfully",
            "network_id": network_id
        }

    except HTTPException:
        raise
    except NeuroscienceError as e:
        logger.error(f"❌ Error eliminando red: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint de salud específico para multi-scale modeling
@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Verificar el estado de salud del servicio de modelado multi-escala.

    Retorna información sobre la disponibilidad del servicio,
    número de redes activas y estado de los componentes.
    """
    try:
        networks = multi_scale_service.list_networks()

        return {
            "status": "healthy",
            "service": "Multi-Scale Modeling Service",
            "active_networks": len(networks),
            "available_scales": [scale.value for scale in ModelingScale],
            "neuron_models": ["Hodgkin-Huxley", "Izhikevich"],
            "features": {
                "network_creation": True,
                "simulation": True,
                "plasticity": True,
                "rhythm_analysis": True,
                "multi_scale_comparison": True
            }
        }

    except NeuroscienceError as e:
        logger.error(f"❌ Error en health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
