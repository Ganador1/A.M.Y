"""
Advanced Laboratory Automation Router

Este módulo proporciona endpoints para la automatización avanzada de laboratorios científicos,
permitiendo la ejecución coordinada de protocolos complejos en múltiples instrumentos
robóticos. Incluye soporte para protocolos estandarizados como PCR, ELISA, extracción
de ácidos nucleicos y cultivo celular, con validación automática de parámetros y
seguimiento completo del historial de operaciones.

Capacidades principales:
- Inicialización y monitoreo de instrumentos robóticos
- Ejecución de protocolos automatizados multi-paso
- Gestión de plantillas de protocolos predefinidas
- Protocolos especializados: PCR, ELISA, extracción DNA/RNA, cultivo celular
- Validación automática de parámetros y muestras
- Historial completo de operaciones realizadas
- Coordinación multi-instrumento para flujos de trabajo complejos

Endpoints disponibles:
- GET /health: Verificación del estado del servicio
- POST /initialize: Inicialización de todos los instrumentos
- GET /instruments/status: Estado actual de instrumentos
- GET /protocols/templates: Lista de plantillas disponibles
- POST /protocols/run: Ejecución de protocolo personalizado
- GET /protocols/history: Historial de protocolos ejecutados
- POST /protocols/pcr: Protocolo PCR estandarizado
- POST /protocols/elisa: Protocolo ELISA 96 pocillos
- POST /protocols/dna-extraction: Extracción de DNA automatizada
- POST /protocols/cell-culture: Cultivo celular automatizado

Dependencias:
- AdvancedLabAutomationService: Servicio principal de automatización
- ProtocolRequest: Modelo para solicitudes de protocolo personalizado
- SampleRequest: Modelo para información de muestras
- ProtocolParametersRequest: Parámetros específicos de protocolo
- PCRRequest, ELISARequest, DNAExtractionRequest, CellCultureRequest: Modelos especializados

Uso típico:
    from app.domains.mathematics.routers.advanced_lab_automation import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles bajo el prefijo /api/advanced-lab
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.domains.engineering.services.advanced_lab_automation_service import AdvancedLabAutomationService


router = APIRouter(prefix="/api/advanced-lab", tags=["advanced-lab-automation"])


class SampleRequest(BaseModel):
    id: str
    volume_ul: float = Field(20, ge=1, le=1000)
    concentration: Optional[float] = Field(None, description="Concentración si es conocida")
    sample_type: str = Field("unknown", description="Tipo de muestra")


class ProtocolParametersRequest(BaseModel):
    master_mix_volume: Optional[int] = Field(20, description="Volumen master mix por reacción (μL)")
    cycles: Optional[int] = Field(35, ge=10, le=50, description="Número de ciclos PCR")
    annealing_temp: Optional[float] = Field(60, ge=45, le=75, description="Temperatura annealing (°C)")
    incubation_temp: Optional[float] = Field(37, ge=20, le=50, description="Temperatura incubación (°C)")
    wash_cycles: Optional[int] = Field(3, ge=1, le=10, description="Número de lavados")
    cell_density_per_ml: Optional[int] = Field(100000, description="Densidad celular por mL")


class ProtocolRequest(BaseModel):
    protocol_name: str = Field(..., description="Nombre del protocolo a ejecutar")
    samples: List[SampleRequest]
    parameters: Optional[ProtocolParametersRequest] = None


@router.get("/health")
async def advanced_lab_health() -> Dict[str, Any]:
    """Health check para automatización avanzada"""
    return {
        "service": "AdvancedLabAutomation",
        "status": "operational",
        "simulation_mode": True,
        "instruments_available": 6
    }


@router.post("/initialize")
async def initialize_instruments() -> Dict[str, Any]:
    """
    Inicializa todos los instrumentos del laboratorio
    """
    service = AdvancedLabAutomationService()
    return await service.initialize_instruments()


@router.get("/instruments/status")
async def get_instruments_status() -> Dict[str, Any]:
    """
    Obtiene el estado actual de todos los instrumentos
    """
    service = AdvancedLabAutomationService()
    return await service.get_instrument_status()


@router.get("/protocols/templates")
async def get_protocol_templates() -> Dict[str, Any]:
    """
    Obtiene todas las plantillas de protocolos disponibles
    """
    service = AdvancedLabAutomationService()
    return await service.get_protocol_templates()


@router.post("/protocols/run")
async def run_automated_protocol(req: ProtocolRequest) -> Dict[str, Any]:
    """
    Ejecuta un protocolo automatizado completo
    """
    service = AdvancedLabAutomationService()
    
    if not req.protocol_name:
        return {"error": "protocol_name requerido"}
    if not req.samples or len(req.samples) == 0:
        return {"error": "Se requiere al menos 1 muestra"}

    # Convertir request a formato interno
    samples = []
    for sample_req in req.samples:
        if not sample_req.id:
            return {"error": "Cada muestra debe tener id"}
        samples.append({
            'id': sample_req.id,
            'volume_ul': sample_req.volume_ul,
            'concentration': sample_req.concentration,
            'sample_type': sample_req.sample_type
        })
    
    # Convertir parámetros
    parameters = {}
    if req.parameters:
        parameters = {
            'master_mix_volume': req.parameters.master_mix_volume,
            'cycles': req.parameters.cycles,
            'annealing_temp': req.parameters.annealing_temp,
            'incubation_temp': req.parameters.incubation_temp,
            'wash_cycles': req.parameters.wash_cycles,
            'cell_density_per_ml': req.parameters.cell_density_per_ml
        }
        # Remover valores None
        parameters = {k: v for k, v in parameters.items() if v is not None}
        # Validaciones de rangos
        if 'master_mix_volume' in parameters and parameters['master_mix_volume'] <= 0:
            return {"error": "master_mix_volume debe ser > 0"}
    
    return await service.run_automated_protocol(req.protocol_name, samples, parameters)


@router.get("/protocols/history")
async def get_protocol_history(limit: int = Query(10, ge=1, le=100)) -> Dict[str, Any]:
    """
    Obtiene el historial de protocolos ejecutados
    """
    service = AdvancedLabAutomationService()
    return await service.get_protocol_history(limit)


class PCRRequest(BaseModel):
    samples: List[SampleRequest]
    parameters: Optional[ProtocolParametersRequest] = None


class ELISARequest(BaseModel):
    samples: List[SampleRequest]
    parameters: Optional[ProtocolParametersRequest] = None


class DNAExtractionRequest(BaseModel):
    samples: List[SampleRequest]


class CellCultureRequest(BaseModel):
    samples: List[SampleRequest]
    parameters: Optional[ProtocolParametersRequest] = None


@router.post("/protocols/pcr")
async def run_pcr_protocol(req: PCRRequest) -> Dict[str, Any]:
    """
    Ejecuta protocolo PCR estándar (shortcut)
    """
    service = AdvancedLabAutomationService()
    
    if not req.samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir a formato interno
    samples_internal = []
    for sample in req.samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type
        })
    
    # Parámetros
    params = {}
    if req.parameters:
        params = {
            'master_mix_volume': req.parameters.master_mix_volume,
            'cycles': req.parameters.cycles,
            'annealing_temp': req.parameters.annealing_temp
        }
        params = {k: v for k, v in params.items() if v is not None}
    
    return await service.run_automated_protocol('pcr_standard', samples_internal, params)


@router.post("/protocols/elisa")
async def run_elisa_protocol(req: ELISARequest) -> Dict[str, Any]:
    """
    Ejecuta protocolo ELISA 96 pocillos (shortcut)
    """
    service = AdvancedLabAutomationService()
    
    if not req.samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir a formato interno
    samples_internal = []
    for sample in req.samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type
        })
    
    # Parámetros
    params = {}
    if req.parameters:
        params = {
            'incubation_temp': req.parameters.incubation_temp,
            'wash_cycles': req.parameters.wash_cycles
        }
        params = {k: v for k, v in params.items() if v is not None}
    
    return await service.run_automated_protocol('elisa_96well', samples_internal, params)


@router.post("/protocols/dna-extraction")
async def run_dna_extraction(req: DNAExtractionRequest) -> Dict[str, Any]:
    """
    Ejecuta protocolo de extracción de DNA (shortcut)
    """
    service = AdvancedLabAutomationService()
    
    if not req.samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir a formato interno
    samples_internal = []
    for sample in req.samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type
        })
    
    return await service.run_automated_protocol('dna_extraction', samples_internal)


@router.post("/protocols/cell-culture")
async def run_cell_culture(req: CellCultureRequest) -> Dict[str, Any]:
    """
    Ejecuta protocolo de cultivo celular automatizado (shortcut)
    """
    service = AdvancedLabAutomationService()
    
    if not req.samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir a formato interno
    samples_internal = []
    for sample in req.samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type
        })
    
    # Parámetros
    params = {}
    if req.parameters:
        params = {
            'cell_density_per_ml': req.parameters.cell_density_per_ml,
            'incubation_temp': req.parameters.incubation_temp
        }
        params = {k: v for k, v in params.items() if v is not None}
    
    return await service.run_automated_protocol('cell_culture', samples_internal, params)
