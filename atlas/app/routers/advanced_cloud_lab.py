"""
Advanced Cloud Laboratory Router

FastAPI router for advanced integration with remote laboratories and cloud-based scientific instrumentation
in the AXIOM scientific computing platform. Provides REST API endpoints for remote experiment submission,
monitoring, and data retrieval from cloud-based scientific facilities.

This router offers comprehensive cloud laboratory capabilities for:
- Remote laboratory experiment submission with automated validation
- Mass spectrometry analysis with customizable ionization and mass range parameters
- Protein expression and purification workflows with temperature control
- Next-generation sequencing (NGS) with configurable read lengths and coverage
- Flow cytometry analysis with customizable antibody panels
- High-throughput drug screening campaigns with compound libraries
- Real-time experiment status tracking and progress monitoring
- Automated results retrieval and data processing
- Cost estimation for experimental protocols and resource usage
- Historical experiment data analytics and performance metrics

The router integrates with the AdvancedCloudLabService to provide
researchers with seamless access to remote scientific instrumentation,
enabling distributed experimentation while maintaining data security
and experimental reproducibility across cloud-based laboratory networks.

Endpoints:
- GET /api/advanced-cloud-lab/health: Cloud lab service health check and status
- GET /api/advanced-cloud-lab/protocols: List all available experimental protocols
- POST /api/advanced-cloud-lab/experiments/submit: Submit experiment to remote laboratory
- GET /api/advanced-cloud-lab/experiments/{experiment_id}/status: Monitor experiment progress
- GET /api/advanced-cloud-lab/experiments/{experiment_id}/results: Retrieve experiment results
- GET /api/advanced-cloud-lab/experiments/history: Get historical experiment data
- GET /api/advanced-cloud-lab/cost-estimate: Calculate experiment cost estimation
- POST /api/advanced-cloud-lab/experiments/mass-spec: Submit mass spectrometry experiment
- POST /api/advanced-cloud-lab/experiments/protein-expression: Submit protein expression experiment
- POST /api/advanced-cloud-lab/experiments/ngs-sequencing: Submit NGS sequencing experiment
- POST /api/advanced-cloud-lab/experiments/flow-cytometry: Submit flow cytometry experiment
- POST /api/advanced-cloud-lab/experiments/drug-screening: Submit drug screening experiment

Dependencies:
- AdvancedCloudLabService: Core cloud laboratory orchestration and management
- CloudSampleRequest/ExperimentParametersRequest: Structured experiment request models
- RemoteLabAPI: Cloud laboratory instrumentation interfaces
- ExperimentTrackingService: Experiment lifecycle and status management
- DataValidationService: Sample and parameter validation
- CostCalculationService: Resource usage and cost estimation

Usage:
    All experiments require validated sample information and protocol-specific parameters.
    Remote experiments run asynchronously with real-time status monitoring.
    Results include raw data, processed analytics, and quality metrics.
    Cost estimation helps researchers plan experimental budgets.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.advanced_cloud_lab_service import AdvancedCloudLabService
from app.types.advanced_cloud_lab_types import (
    AdvancedCloudLabHealthResult,
    GetAvailableProtocolsResult,
    SubmitExperimentResult,
    MonitorExperimentResult,
    GetExperimentResultsResult,
)


router = APIRouter(prefix="/api/advanced-cloud-lab", tags=["advanced-cloud-lab"])


class CloudSampleRequest(BaseModel):
    """Request model for cloud sample information.

    Defines the structure for sample data submitted to cloud lab experiments,
    including identification, physical properties, and handling requirements.
    """

    id: str = Field(..., description="Unique identifier for the sample")
    volume_ul: Optional[float] = Field(None, description="Sample volume in microliters (μL)")
    concentration: Optional[float] = Field(None, description="Sample concentration (unit depends on sample type)")
    sample_type: str = Field("unknown", description="Type of sample (e.g., protein, DNA, chemical)")
    storage_conditions: Optional[str] = Field("room_temp", description="Required storage conditions (e.g., -80C, 4C, room_temp)")


class ExperimentParametersRequest(BaseModel):
    """Request model for experiment-specific parameters.

    Contains configurable parameters for various experimental protocols,
    allowing customization of instrument settings and protocol conditions.
    """

    ionization_mode: Optional[str] = Field("ESI", description="Ionization mode for mass spectrometry (e.g., ESI, MALDI)")
    mass_range: Optional[List[int]] = Field([100, 2000], description="Mass range for spectrometry [min, max]")
    resolution: Optional[str] = Field("high", description="Instrument resolution level (low, medium, high)")
    cell_line: Optional[str] = Field("E.coli_BL21", description="Cell line for protein expression")
    inducer: Optional[str] = Field("IPTG", description="Inducer chemical for expression")
    temperature: Optional[float] = Field(37, description="Incubation temperature in Celsius")
    protein_concentration: Optional[float] = Field(10, description="Target protein concentration (mg/mL)")
    read_length: Optional[int] = Field(150, description="Read length for NGS sequencing")
    coverage: Optional[int] = Field(30, description="Sequencing coverage depth")
    antibody_panel: Optional[List[str]] = Field(None, description="List of antibodies for flow cytometry")
    compound_library: Optional[str] = Field("FDA_approved", description="Compound library for drug screening")


class CloudExperimentRequest(BaseModel):
    """Request model for submitting cloud experiments.

    Encapsulates the protocol selection, sample list, and optional parameters
    for submitting experiments to remote cloud laboratories.
    """

    protocol_name: str = Field(..., description="Name of the experimental protocol to execute")
    samples: List[CloudSampleRequest] = Field(..., description="List of samples to process")
    parameters: Optional[ExperimentParametersRequest] = Field(None, description="Protocol-specific parameters")


@router.get("/health")
async def advanced_cloud_lab_health() -> AdvancedCloudLabHealthResult:
    """Health check para Cloud Lab avanzado"""
    return {
        "service": "AdvancedCloudLab",
        "status": "operational",
        "simulation_mode": True,
        "protocols_available": 6
    }


@router.get("/protocols")
async def get_available_protocols() -> GetAvailableProtocolsResult:
    """
    Obtiene todos los protocolos disponibles en el laboratorio remoto
    """
    service = AdvancedCloudLabService()
    return await service.get_available_protocols()


@router.post("/experiments/submit")
async def submit_experiment(req: CloudExperimentRequest) -> SubmitExperimentResult:
    """
    Envía un experimento al laboratorio remoto
    """
    service = AdvancedCloudLabService()
    
    # Validaciones básicas
    if not req.protocol_name:
        return {"error": "protocol_name requerido"}
    if not req.samples or len(req.samples) == 0:
        return {"error": "Se requiere al menos 1 muestra"}

    # Convertir request a formato interno
    samples = []
    for sample_req in req.samples:
        if not sample_req.id:
            return {"error": "Cada muestra debe tener id"}
        if sample_req.volume_ul is not None and sample_req.volume_ul <= 0:
            return {"error": "volume_ul debe ser > 0 si se especifica"}
        samples.append({
            'id': sample_req.id,
            'volume_ul': sample_req.volume_ul,
            'concentration': sample_req.concentration,
            'sample_type': sample_req.sample_type,
            'storage_conditions': sample_req.storage_conditions
        })
    
    # Convertir parámetros
    parameters = {}
    if req.parameters:
        parameters = {
            'ionization_mode': req.parameters.ionization_mode,
            'mass_range': req.parameters.mass_range,
            'resolution': req.parameters.resolution,
            'cell_line': req.parameters.cell_line,
            'inducer': req.parameters.inducer,
            'temperature': req.parameters.temperature,
            'protein_concentration': req.parameters.protein_concentration,
            'read_length': req.parameters.read_length,
            'coverage': req.parameters.coverage,
            'antibody_panel': req.parameters.antibody_panel,
            'compound_library': req.parameters.compound_library
        }
        # Remover valores None
        parameters = {k: v for k, v in parameters.items() if v is not None}

        # Validaciones de parámetros comunes
        if 'mass_range' in parameters:
            mr = parameters['mass_range']
            if not isinstance(mr, list) or len(mr) != 2 or mr[0] <= 0 or mr[1] <= mr[0]:
                return {"error": "mass_range inválido [min,max]"}
        if 'temperature' in parameters and (parameters['temperature'] < 0 or parameters['temperature'] > 95):
            return {"error": "temperature fuera de rango [0,95]"}
        if 'read_length' in parameters and parameters['read_length'] <= 0:
            return {"error": "read_length debe ser > 0"}
        if 'coverage' in parameters and parameters['coverage'] <= 0:
            return {"error": "coverage debe ser > 0"}
    
    return await service.submit_advanced_experiment(req.protocol_name, samples, parameters)


@router.get("/experiments/{experiment_id}/status")
async def monitor_experiment(experiment_id: str) -> MonitorExperimentResult:
    """
    Monitorea el progreso de un experimento
    """
    service = AdvancedCloudLabService()
    return await service.monitor_experiment(experiment_id)


@router.get("/experiments/{experiment_id}/results")
async def get_experiment_results(experiment_id: str) -> GetExperimentResultsResult:
    """
    Obtiene los resultados de un experimento completado
    """
    service = AdvancedCloudLabService()
    return await service.get_experiment_results(experiment_id)


@router.get("/experiments/history")
async def get_experiment_history(limit: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    """
    Obtiene el historial de experimentos
    """
    service = AdvancedCloudLabService()
    return await service.get_experiment_history(limit)


@router.get("/cost-estimate")
async def get_cost_estimate(protocol_name: str, samples_count: int = Query(..., ge=1)) -> Dict[str, Any]:
    """
    Calcula estimación de costos para un experimento
    """
    service = AdvancedCloudLabService()
    return await service.get_cost_estimate(protocol_name, samples_count)


# Endpoints específicos para protocolos comunes
@router.post("/experiments/mass-spec")
async def submit_mass_spec(samples: List[CloudSampleRequest],
                          parameters: Optional[ExperimentParametersRequest] = None) -> Dict[str, Any]:
    """
    Envía experimento de espectrometría de masas (shortcut)
    """
    service = AdvancedCloudLabService()
    
    if not samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir samples
    samples_internal = []
    for sample in samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type,
            'storage_conditions': sample.storage_conditions
        })
    
    # Convertir parámetros
    params = {}
    if parameters:
        params = {
            'ionization_mode': parameters.ionization_mode,
            'mass_range': parameters.mass_range,
            'resolution': parameters.resolution
        }
        params = {k: v for k, v in params.items() if v is not None}
        if 'mass_range' in params:
            mr = params['mass_range']
            if not isinstance(mr, list) or len(mr) != 2 or mr[0] <= 0 or mr[1] <= mr[0]:
                return {"error": "mass_range inválido [min,max]"}
    
    return await service.submit_advanced_experiment('mass_spec_analysis', samples_internal, params)


@router.post("/experiments/protein-expression")
async def submit_protein_expression(samples: List[CloudSampleRequest],
                                  parameters: Optional[ExperimentParametersRequest] = None) -> Dict[str, Any]:
    """
    Envía experimento de expresión de proteínas (shortcut)
    """
    service = AdvancedCloudLabService()
    
    if not samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir samples
    samples_internal = []
    for sample in samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type,
            'storage_conditions': sample.storage_conditions
        })
    
    # Convertir parámetros
    params = {}
    if parameters:
        params = {
            'cell_line': parameters.cell_line,
            'inducer': parameters.inducer,
            'temperature': parameters.temperature
        }
        params = {k: v for k, v in params.items() if v is not None}
        if 'temperature' in params and (params['temperature'] < 0 or params['temperature'] > 95):
            return {"error": "temperature fuera de rango [0,95]"}
    
    return await service.submit_advanced_experiment('protein_expression', samples_internal, params)


@router.post("/experiments/ngs-sequencing")
async def submit_ngs_sequencing(samples: List[CloudSampleRequest],
                               parameters: Optional[ExperimentParametersRequest] = None) -> Dict[str, Any]:
    """
    Envía experimento de secuenciación NGS (shortcut)
    """
    service = AdvancedCloudLabService()
    
    if not samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir samples
    samples_internal = []
    for sample in samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type,
            'storage_conditions': sample.storage_conditions
        })
    
    # Convertir parámetros
    params = {}
    if parameters:
        params = {
            'read_length': parameters.read_length,
            'coverage': parameters.coverage
        }
        params = {k: v for k, v in params.items() if v is not None}
        if 'read_length' in params and params['read_length'] <= 0:
            return {"error": "read_length debe ser > 0"}
        if 'coverage' in params and params['coverage'] <= 0:
            return {"error": "coverage debe ser > 0"}
    
    return await service.submit_advanced_experiment('ngs_sequencing', samples_internal, params)


@router.post("/experiments/flow-cytometry")
async def submit_flow_cytometry(samples: List[CloudSampleRequest],
                               parameters: Optional[ExperimentParametersRequest] = None) -> Dict[str, Any]:
    """
    Envía experimento de citometría de flujo (shortcut)
    """
    service = AdvancedCloudLabService()
    
    if not samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir samples
    samples_internal = []
    for sample in samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type,
            'storage_conditions': sample.storage_conditions
        })
    
    # Convertir parámetros
    params = {}
    if parameters:
        params = {
            'antibody_panel': parameters.antibody_panel
        }
        params = {k: v for k, v in params.items() if v is not None}
    
    return await service.submit_advanced_experiment('flow_cytometry', samples_internal, params)


@router.post("/experiments/drug-screening")
async def submit_drug_screening(samples: List[CloudSampleRequest],
                               parameters: Optional[ExperimentParametersRequest] = None) -> Dict[str, Any]:
    """
    Envía experimento de screening de fármacos (shortcut)
    """
    service = AdvancedCloudLabService()
    
    if not samples:
        return {"error": "Se requiere al menos 1 muestra"}
    # Convertir samples
    samples_internal = []
    for sample in samples:
        if not sample.id:
            return {"error": "Cada muestra debe tener id"}
        samples_internal.append({
            'id': sample.id,
            'volume_ul': sample.volume_ul,
            'concentration': sample.concentration,
            'sample_type': sample.sample_type,
            'storage_conditions': sample.storage_conditions
        })
    
    # Convertir parámetros
    params = {}
    if parameters:
        params = {
            'compound_library': parameters.compound_library
        }
        params = {k: v for k, v in params.items() if v is not None}
    
    return await service.submit_advanced_experiment('drug_screening', samples_internal, params)
