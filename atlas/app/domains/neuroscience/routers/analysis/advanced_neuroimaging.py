"""
Advanced Neuroimaging Analysis Router
====================================

Router FastAPI para análisis avanzado de neuroimágenes con procesamiento en tiempo real.

Author: AXIOM Team
Date: 2025-09-23
Version: 1.0.0
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import numpy as np
import logging

from app.domains.neuroscience.services.neuroimaging.advanced_neuroimaging_analysis import (
from app.exceptions.domain.neuroscience import NeuroscienceError
    AdvancedNeuroimagingAnalysis,
    NeuroimagingData,
    ImagingModality,
    ProcessingMode
)

# Configurar logging
logger = logging.getLogger(__name__)

# Inicializar servicio
neuroimaging_service = AdvancedNeuroimagingAnalysis()

# Router
router = APIRouter(prefix="/neuroimaging", tags=["neuroimaging"])

# Modelos Pydantic

class SessionCreateRequest(BaseModel):
    """Modelo para crear sesión de análisis."""
    session_id: str = Field(..., description="ID único de la sesión")
    modality: str = Field(..., description="Modalidad de neuroimaging (fmri, eeg, meg, dti, pet, spect, structural_mri)")
    processing_mode: str = Field(default="batch", description="Modo de procesamiento (real_time, batch, streaming)")
    config: Optional[Dict[str, Any]] = Field(default=None, description="Configuración específica")

class NeuroimagingDataRequest(BaseModel):
    """Modelo para datos de neuroimaging."""
    data: List[List[float]] = Field(..., description="Datos de neuroimaging (matriz 2D)")
    modality: str = Field(..., description="Modalidad de neuroimaging")
    sampling_rate: float = Field(..., description="Frecuencia de muestreo en Hz")
    channels: Optional[List[str]] = Field(default=None, description="Nombres de canales")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadatos adicionales")

class ConnectivityAnalysisRequest(BaseModel):
    """Modelo para análisis de conectividad."""
    data: NeuroimagingDataRequest
    method: str = Field(default="correlation", description="Método de análisis (correlation, coherence, mutual_info)")

class SegmentationRequest(BaseModel):
    """Modelo para segmentación cerebral."""
    data: NeuroimagingDataRequest
    atlas: str = Field(default="aal", description="Atlas cerebral a usar")

class PatternDetectionRequest(BaseModel):
    """Modelo para detección de patrones."""
    data: NeuroimagingDataRequest
    pattern_types: Optional[List[str]] = Field(default=None, description="Tipos de patrones a detectar")

class RealTimeDataRequest(BaseModel):
    """Modelo para datos en tiempo real."""
    session_id: str = Field(..., description="ID de la sesión")
    data: List[List[float]] = Field(..., description="Nuevos datos a procesar")
    timestamps: Optional[List[float]] = Field(default=None, description="Timestamps de los datos")

# Endpoints

@router.post("/sessions", summary="Crear sesión de análisis")
async def create_analysis_session(request: SessionCreateRequest) -> Dict[str, Any]:
    """
    Crear una nueva sesión de análisis de neuroimaging.

    - **session_id**: Identificador único para la sesión
    - **modality**: Modalidad de neuroimaging (fmri, eeg, meg, dti, pet, spect, structural_mri)
    - **processing_mode**: Modo de procesamiento (real_time, batch, streaming)
    - **config**: Configuración opcional específica para la sesión

    Returns:
        Información de la sesión creada incluyendo configuración y estado
    """
    try:
        # Validar modalidad
        try:
            modality = ImagingModality(request.modality)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Modalidad no soportada: {request.modality}"
            )

        # Validar modo de procesamiento
        try:
            processing_mode = ProcessingMode(request.processing_mode)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Modo de procesamiento no soportado: {request.processing_mode}"
            )

        result = await neuroimaging_service.create_analysis_session(
            session_id=request.session_id,
            modality=modality,
            processing_mode=processing_mode,
            config=request.config
        )

        return {
            "status": "success",
            "data": result,
            "message": f"Sesión {request.session_id} creada exitosamente"
        }

    except NeuroscienceError as e:
        logger.error(f"Error creando sesión: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preprocess", summary="Preprocesar datos de neuroimaging")
async def preprocess_data(request: NeuroimagingDataRequest) -> Dict[str, Any]:
    """
    Preprocesar datos de neuroimaging aplicando filtros y normalización.

    - **data**: Matriz de datos de neuroimaging
    - **modality**: Modalidad de los datos
    - **sampling_rate**: Frecuencia de muestreo
    - **channels**: Nombres de canales (opcional)
    - **metadata**: Metadatos adicionales (opcional)

    Returns:
        Datos preprocesados y estadísticas del procesamiento
    """
    try:
        # Validar modalidad
        try:
            modality = ImagingModality(request.modality)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Modalidad no soportada: {request.modality}"
            )

        # Convertir datos a NeuroimagingData
        data = NeuroimagingData(
            data=np.array(request.data),
            modality=modality,
            sampling_rate=request.sampling_rate,
            channels=request.channels or [],
            metadata=request.metadata or {}
        )

        preprocessed_data = await neuroimaging_service.preprocess_data(data)

        return {
            "status": "success",
            "data": {
                "processed_data": preprocessed_data.data.tolist(),
                "modality": preprocessed_data.modality.value,
                "sampling_rate": preprocessed_data.sampling_rate,
                "channels": preprocessed_data.channels,
                "metadata": preprocessed_data.metadata,
                "preprocessing_stats": {
                    "original_shape": data.data.shape,
                    "processed_shape": preprocessed_data.data.shape,
                    "mean_amplitude": float(np.mean(np.abs(preprocessed_data.data))),
                    "std_amplitude": float(np.std(preprocessed_data.data))
                }
            },
            "message": "Datos preprocesados exitosamente"
        }

    except NeuroscienceError as e:
        logger.error(f"Error en preprocesamiento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/connectivity", summary="Analizar conectividad funcional")
async def analyze_connectivity(request: ConnectivityAnalysisRequest) -> Dict[str, Any]:
    """
    Analizar conectividad funcional entre regiones cerebrales.

    - **data**: Datos de neuroimaging multi-canal
    - **method**: Método de análisis (correlation, coherence, mutual_info)

    Returns:
        Matriz de conectividad, métricas de red y medidas de grafo
    """
    try:
        # Validar modalidad
        try:
            modality = ImagingModality(request.data.modality)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Modalidad no soportada: {request.data.modality}"
            )

        # Convertir datos
        data = NeuroimagingData(
            data=np.array(request.data.data),
            modality=modality,
            sampling_rate=request.data.sampling_rate,
            channels=request.data.channels or [],
            metadata=request.data.metadata or {}
        )

        connectivity_results = await neuroimaging_service.analyze_functional_connectivity(
            data=data,
            method=request.method
        )

        return {
            "status": "success",
            "data": {
                "functional_connectivity": connectivity_results.functional_connectivity.tolist(),
                "network_metrics": connectivity_results.network_metrics,
                "graph_measures": {
                    key: value.tolist() if isinstance(value, np.ndarray) else value
                    for key, value in connectivity_results.graph_measures.items()
                },
                "analysis_method": request.method,
                "n_channels": data.data.shape[0]
            },
            "message": f"Análisis de conectividad completado usando {request.method}"
        }

    except NeuroscienceError as e:
        logger.error(f"Error en análisis de conectividad: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/segmentation", summary="Segmentar regiones cerebrales")
async def segment_brain_regions(request: SegmentationRequest) -> Dict[str, Any]:
    """
    Segmentar regiones cerebrales usando atlas anatómicos.

    - **data**: Datos de neuroimaging estructural
    - **atlas**: Atlas cerebral a utilizar

    Returns:
        Regiones identificadas, volúmenes y coordenadas
    """
    try:
        # Validar modalidad
        try:
            modality = ImagingModality(request.data.modality)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Modalidad no soportada: {request.data.modality}"
            )

        # Convertir datos
        data = NeuroimagingData(
            data=np.array(request.data.data),
            modality=modality,
            sampling_rate=request.data.sampling_rate,
            channels=request.data.channels or [],
            metadata=request.data.metadata or {}
        )

        segmentation_results = await neuroimaging_service.segment_brain_regions(
            data=data,
            atlas=request.atlas
        )

        # Preparar regiones para serialización
        regions_info = {}
        for region_name, region_data in segmentation_results.regions.items():
            if isinstance(region_data, np.ndarray):
                regions_info[region_name] = {
                    "shape": region_data.shape,
                    "data_type": str(region_data.dtype),
                    "mean_value": float(np.mean(region_data)),
                    "std_value": float(np.std(region_data))
                }
            else:
                regions_info[region_name] = {"data": region_data.tolist() if hasattr(region_data, 'tolist') else region_data}

        return {
            "status": "success",
            "data": {
                "regions_info": regions_info,
                "volumes": segmentation_results.volumes,
                "coordinates": segmentation_results.coordinates,
                "confidence_scores": segmentation_results.confidence_scores,
                "atlas_used": request.atlas,
                "n_regions": len(segmentation_results.regions)
            },
            "message": f"Segmentación completada usando atlas {request.atlas}"
        }

    except NeuroscienceError as e:
        logger.error(f"Error en segmentación: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/patterns", summary="Detectar patrones en neuroimaging")
async def detect_patterns(request: PatternDetectionRequest) -> Dict[str, Any]:
    """
    Detectar patrones específicos en datos de neuroimaging.

    - **data**: Datos de neuroimaging
    - **pattern_types**: Tipos de patrones a detectar (opcional)

    Returns:
        Patrones detectados, scores de anomalía y clasificación
    """
    try:
        # Validar modalidad
        try:
            modality = ImagingModality(request.data.modality)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Modalidad no soportada: {request.data.modality}"
            )

        # Convertir datos
        data = NeuroimagingData(
            data=np.array(request.data.data),
            modality=modality,
            sampling_rate=request.data.sampling_rate,
            channels=request.data.channels or [],
            metadata=request.data.metadata or {}
        )

        pattern_results = await neuroimaging_service.detect_patterns(
            data=data,
            pattern_types=request.pattern_types
        )

        return {
            "status": "success",
            "data": {
                "detected_patterns": pattern_results.detected_patterns,
                "anomaly_scores": pattern_results.anomaly_scores.tolist(),
                "classification_results": pattern_results.classification_results,
                "temporal_features": {
                    key: value.tolist() if isinstance(value, np.ndarray) else value
                    for key, value in pattern_results.temporal_features.items()
                },
                "n_patterns": len(pattern_results.detected_patterns),
                "pattern_types_requested": request.pattern_types or ["oscillations", "anomalies", "connectivity_patterns"]
            },
            "message": f"Detección de patrones completada: {len(pattern_results.detected_patterns)} patrones encontrados"
        }

    except NeuroscienceError as e:
        logger.error(f"Error en detección de patrones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/real-time", summary="Procesar datos en tiempo real")
async def process_real_time_stream(request: RealTimeDataRequest) -> Dict[str, Any]:
    """
    Procesar nuevos datos en una sesión de tiempo real.

    - **session_id**: ID de la sesión activa
    - **data**: Nuevos datos a procesar
    - **timestamps**: Timestamps opcionales

    Returns:
        Resultados del análisis en tiempo real y estado del buffer
    """
    try:
        new_data = np.array(request.data)
        timestamps = np.array(request.timestamps) if request.timestamps else None

        result = await neuroimaging_service.process_real_time_stream(
            session_id=request.session_id,
            new_data=new_data,
            timestamps=timestamps
        )

        return {
            "status": "success",
            "data": result,
            "message": f"Datos procesados en tiempo real para sesión {request.session_id}"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NeuroscienceError as e:
        logger.error(f"Error en procesamiento tiempo real: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}", summary="Obtener estado de sesión")
async def get_session_status(session_id: str) -> Dict[str, Any]:
    """
    Obtener el estado actual de una sesión de análisis.

    - **session_id**: ID de la sesión

    Returns:
        Estado completo de la sesión incluyendo estadísticas
    """
    try:
        status = await neuroimaging_service.get_session_status(session_id)

        # Convertir datetime a string para serialización
        if 'created_at' in status:
            status['created_at'] = status['created_at'].isoformat()
        if 'closed_at' in status:
            status['closed_at'] = status['closed_at'].isoformat()

        return {
            "status": "success",
            "data": status,
            "message": f"Estado de sesión {session_id} obtenido"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NeuroscienceError as e:
        logger.error(f"Error obteniendo estado: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}", summary="Cerrar sesión de análisis")
async def close_analysis_session(session_id: str) -> Dict[str, Any]:
    """
    Cerrar una sesión de análisis y limpiar recursos.

    - **session_id**: ID de la sesión a cerrar

    Returns:
        Resumen de la sesión cerrada
    """
    try:
        result = await neuroimaging_service.close_session(session_id)

        return {
            "status": "success",
            "data": result,
            "message": f"Sesión {session_id} cerrada exitosamente"
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except NeuroscienceError as e:
        logger.error(f"Error cerrando sesión: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions", summary="Listar todas las sesiones")
async def list_sessions() -> Dict[str, Any]:
    """
    Listar todas las sesiones de análisis existentes.

    Returns:
        Lista de sesiones con sus estados
    """
    try:
        sessions = {}
        for session_id in neuroimaging_service.processing_pipelines.keys():
            session_status = await neuroimaging_service.get_session_status(session_id)

            # Convertir datetime a string
            if 'created_at' in session_status:
                session_status['created_at'] = session_status['created_at'].isoformat()
            if 'closed_at' in session_status:
                session_status['closed_at'] = session_status['closed_at'].isoformat()

            sessions[session_id] = session_status

        return {
            "status": "success",
            "data": {
                "sessions": sessions,
                "total_sessions": len(sessions),
                "active_sessions": len([s for s in sessions.values() if s.get('status') == 'active'])
            },
            "message": f"{len(sessions)} sesiones encontradas"
        }

    except NeuroscienceError as e:
        logger.error(f"Error listando sesiones: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/modalities", summary="Obtener modalidades soportadas")
async def get_supported_modalities() -> Dict[str, Any]:
    """
    Obtener lista de modalidades de neuroimaging soportadas.

    Returns:
        Lista de modalidades disponibles con descripciones
    """
    modalities = {
        "fmri": {
            "name": "Functional Magnetic Resonance Imaging",
            "description": "Imágenes de resonancia magnética funcional",
            "typical_sampling_rate": "0.5-2 Hz",
            "use_cases": ["Conectividad funcional", "Activación cerebral", "Redes neuronales"]
        },
        "eeg": {
            "name": "Electroencephalography",
            "description": "Electroencefalografía",
            "typical_sampling_rate": "250-1000 Hz",
            "use_cases": ["Ritmos cerebrales", "Estados de consciencia", "Epilepsia"]
        },
        "meg": {
            "name": "Magnetoencephalography",
            "description": "Magnetoencefalografía",
            "typical_sampling_rate": "600-6000 Hz",
            "use_cases": ["Localización de fuentes", "Dinámicas rápidas", "Conectividad"]
        },
        "dti": {
            "name": "Diffusion Tensor Imaging",
            "description": "Imágenes de tensor de difusión",
            "typical_sampling_rate": "Static",
            "use_cases": ["Tractografía", "Integridad de materia blanca", "Conectividad estructural"]
        },
        "pet": {
            "name": "Positron Emission Tomography",
            "description": "Tomografía por emisión de positrones",
            "typical_sampling_rate": "Variable",
            "use_cases": ["Metabolismo cerebral", "Neurotransmisores", "Patología"]
        },
        "spect": {
            "name": "Single Photon Emission Computed Tomography",
            "description": "Tomografía computarizada por emisión de fotón único",
            "typical_sampling_rate": "Variable",
            "use_cases": ["Flujo sanguíneo cerebral", "Perfusión", "Actividad neuronal"]
        },
        "structural_mri": {
            "name": "Structural Magnetic Resonance Imaging",
            "description": "Resonancia magnética estructural",
            "typical_sampling_rate": "Static",
            "use_cases": ["Anatomía cerebral", "Segmentación", "Volumetría"]
        }
    }

    return {
        "status": "success",
        "data": {
            "modalities": modalities,
            "total_modalities": len(modalities)
        },
        "message": f"{len(modalities)} modalidades soportadas"
    }

# Documentación adicional para OpenAPI
router.openapi_extra = {
    "description": """
    ## Advanced Neuroimaging Analysis API

    Esta API proporciona análisis avanzado de neuroimágenes con capacidades de procesamiento en tiempo real.

    ### Características principales:
    - **Múltiples modalidades**: fMRI, EEG, MEG, DTI, PET, SPECT, MRI estructural
    - **Procesamiento en tiempo real**: Análisis streaming con buffers inteligentes
    - **Análisis de conectividad**: Correlación, coherencia e información mutua
    - **Segmentación cerebral**: Atlas anatómicos automáticos
    - **Detección de patrones**: Oscilaciones, anomalías y patrones de conectividad
    - **Preprocesamiento**: Filtros, normalización y eliminación de artefactos

    ### Flujo de trabajo típico:
    1. Crear sesión de análisis
    2. Preprocesar datos (opcional)
    3. Ejecutar análisis específicos
    4. Procesar resultados
    5. Cerrar sesión

    ### Modos de procesamiento:
    - **batch**: Procesamiento por lotes tradicional
    - **real_time**: Análisis en tiempo real con buffers
    - **streaming**: Procesamiento continuo de flujo de datos
    """
}

logger.info("🧠 Advanced Neuroimaging Analysis Router cargado con 10 endpoints")
