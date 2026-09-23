"""
🏥 Router Médico Unificado - AXIOM v4.1

Este módulo proporciona un sistema de routing unificado para todos los servicios médicos
del dominio, utilizando el MedicineRegistry para descubrimiento dinámico de servicios
y routing inteligente basado en capacidades.

Características principales:
- Routing dinámico basado en MedicineRegistry
- Descubrimiento automático de servicios médicos
- Gestión centralizada de endpoints médicos
- Integración de AlphaFold3, ClinicalBERT, Medicina Personalizada, Biomecánica
- Validación unificada y manejo de errores
- Monitoreo y métricas de rendimiento
- Autenticación y autorización centralizadas

Servicios integrados:
- 🧬 AlphaFold3ProteinStructureService: Predicción de estructuras proteicas
- 📝 ClinicalBERTService: Procesamiento de texto clínico y NLP médico
- 💊 PersonalizedMedicineService: Farmacogenómica y medicina personalizada
- 🦴 BiomechanicsService: Análisis biomecánico y cinemática
- 🏥 MedicalImagingService: Procesamiento de imágenes médicas
- 🧪 GenomicsService: Análisis genómico y secuenciación

Arquitectura del Router:
- Endpoint único de entrada: /medical/*
- Routing inteligente basado en tipo de servicio
- Middleware de validación y seguridad
- Cache distribuido para optimización
- Streaming de datos en tiempo real
- Respuestas estandarizadas con metadatos

Endpoints principales:
- GET /medical/services: Lista todos los servicios médicos disponibles
- GET /medical/service/{service_name}/capabilities: Capacidades de un servicio
- POST /medical/analyze: Endpoint genérico para análisis médicos
- POST /medical/predict: Endpoint genérico para predicciones médicas
- POST /medical/process: Endpoint genérico para procesamiento médico
- GET /medical/health: Estado de salud de todos los servicios

Dependencias:
- MedicineRegistry: Registry principal de servicios médicos
- FastAPI: Framework web asíncrono
- Pydantic: Validación de modelos de datos
- Security: Autenticación y autorización

Ejemplo de uso:
    POST /medical/analyze
    {
        "service_type": "genomics",
        "analysis_type": "variant_calling",
        "data": {...}
    }

Autor: AXIOM Development Team
Versión: 4.1
Última actualización: 2024
"""

from typing import Dict, Any, Optional
from datetime import datetime
import asyncio
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator, ConfigDict

# Internal imports
from ..registry import MedicineRegistry
from app.security.auth import get_current_user
from app.core.logging import get_logger
from app.exceptions.domain.medicine import MedicalError

# Initialize logger and router
logger = get_logger(__name__)
router = APIRouter(prefix="/medical", tags=["Unified Medical Services"])

# Global registry instance
medicine_registry = None

def get_medicine_registry() -> MedicineRegistry:
    """Get or create MedicineRegistry instance"""
    global medicine_registry
    if medicine_registry is None:
        medicine_registry = MedicineRegistry()
    return medicine_registry

# =====================================================================================
# REQUEST/RESPONSE MODELS
# =====================================================================================

class MedicalAnalysisRequest(BaseModel):
    """Solicitud genérica para análisis médicos"""
    service_type: str = Field(..., description="Tipo de servicio: genomics, imaging, biomechanics, etc.")
    analysis_type: str = Field(..., description="Tipo específico de análisis")
    data: Dict[str, Any] = Field(..., description="Datos para análisis")
    parameters: Optional[Dict[str, Any]] = Field(default=None, description="Parámetros adicionales")
    options: Optional[Dict[str, Any]] = Field(default=None, description="Opciones de configuración")
    patient_id: Optional[str] = Field(default=None, description="ID del paciente (para contexto)")
    session_id: Optional[str] = Field(default=None, description="ID de sesión médica")

    @validator('service_type')
    def validate_service_type(cls, v):
        allowed_types = [
            'genomics', 'imaging', 'biomechanics', 'personalized_medicine',
            'alphafold3', 'clinicalbert', 'protein_structure', 'nlp'
        ]
        if v.lower() not in allowed_types:
            raise ValueError(f'service_type must be one of {allowed_types}')
        return v.lower()

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "service_type": "genomics",
                "analysis_type": "variant_calling",
                "data": {
                    "sequence": "ATCGATCGATCG",
                    "reference_genome": "hg38"
                },
                "parameters": {
                    "quality_threshold": 30,
                    "coverage_min": 10
                },
                "patient_id": "PATIENT_001",
                "session_id": "SESSION_ABC123"
            }
        }
    )

class MedicalPredictionRequest(BaseModel):
    """Solicitud genérica para predicciones médicas"""
    service_type: str = Field(..., description="Tipo de servicio médico")
    prediction_type: str = Field(..., description="Tipo de predicción")
    input_data: Dict[str, Any] = Field(..., description="Datos de entrada")
    model_configuration: Optional[Dict[str, Any]] = Field(default=None, description="Configuración del modelo")
    confidence_threshold: Optional[float] = Field(default=0.7, ge=0.0, le=1.0, description="Umbral de confianza")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "service_type": "alphafold3",
                "prediction_type": "protein_structure",
                "input_data": {
                    "sequence": "MKTVRQERLKSIVRILERSKEPVSGAQLAEELSVSRQVIVQDIAYLRSLGYNIVATPRGYVLAGG"
                },
                "confidence_threshold": 0.8
            }
        }
    )

class MedicalProcessingRequest(BaseModel):
    """Solicitud genérica para procesamiento médico"""
    service_type: str = Field(..., description="Tipo de servicio")
    processing_type: str = Field(..., description="Tipo de procesamiento")
    data_source: Dict[str, Any] = Field(..., description="Fuente de datos")
    processing_options: Optional[Dict[str, Any]] = Field(default=None, description="Opciones de procesamiento")
    output_format: Optional[str] = Field(default="json", description="Formato de salida: json, xml, csv")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "service_type": "clinicalbert",
                "processing_type": "entity_extraction",
                "data_source": {
                    "clinical_text": "Patient presents with chest pain and shortness of breath."
                },
                "processing_options": {
                    "extract_medications": True,
                    "extract_symptoms": True
                }
            }
        }
    )

class MedicalResponse(BaseModel):
    """Respuesta estandarizada para servicios médicos"""
    success: bool = Field(..., description="Indica si la operación fue exitosa")
    service_info: Dict[str, str] = Field(..., description="Información del servicio")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Resultado de la operación")
    error: Optional[str] = Field(default=None, description="Mensaje de error si aplica")
    metadata: Dict[str, Any] = Field(..., description="Metadatos de la respuesta")
    performance_metrics: Optional[Dict[str, float]] = Field(default=None, description="Métricas de rendimiento")

# =====================================================================================
# MAIN ENDPOINTS
# =====================================================================================

@router.get("/services", response_model=Dict[str, Any])
async def list_medical_services(
    include_capabilities: bool = False,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    📋 Lista todos los servicios médicos disponibles

    Proporciona una lista comprehensiva de todos los servicios médicos registrados
    en el sistema, incluyendo sus capacidades y estado actual.

    Args:
        include_capabilities: Si incluir información detallada de capacidades
        current_user: Usuario autenticado

    Returns:
        Dict con lista de servicios y sus capacidades

    Example:
        GET /medical/services?include_capabilities=true
    """
    start_time = datetime.now()

    try:
        logger.info(f"🏥 Usuario {current_user.get('username', 'unknown')} consultando servicios médicos")

        registry = get_medicine_registry()
        services = await registry.list_services()

        # Obtener capacidades si se solicita
        service_details = {}
        for service_name in services:
            service_info = {
                "name": service_name,
                "status": await registry.get_service_health(service_name),
                "version": await registry.get_service_version(service_name)
            }

            if include_capabilities:
                capabilities = await registry.get_service_capabilities(service_name)
                service_info["capabilities"] = capabilities

            service_details[service_name] = service_info

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "services": service_details,
            "total_services": len(services),
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "user": current_user.get('username', 'unknown'),
                "include_capabilities": include_capabilities
            }
        }

    except MedicalError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error listando servicios médicos: {e} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno listando servicios: {str(e)}"
        )

@router.get("/service/{service_name}/capabilities")
async def get_service_capabilities(
    service_name: str,
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🔍 Obtiene las capacidades detalladas de un servicio específico

    Args:
        service_name: Nombre del servicio médico
        current_user: Usuario autenticado

    Returns:
        Dict con capacidades detalladas del servicio
    """
    start_time = datetime.now()

    try:
        logger.info(f"🔍 Consultando capacidades de servicio: {service_name}")

        registry = get_medicine_registry()

        # Verificar que el servicio existe
        services = await registry.list_services()
        if service_name not in services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio '{service_name}' no encontrado"
            )

        # Obtener capacidades
        capabilities = await registry.get_service_capabilities(service_name)
        health = await registry.get_service_health(service_name)
        version = await registry.get_service_version(service_name)

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "success": True,
            "service": service_name,
            "capabilities": capabilities,
            "health": health,
            "version": version,
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "user": current_user.get('username', 'unknown')
            }
        }

    except HTTPException:
        raise
    except MedicalError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error obteniendo capacidades de {service_name}: {e} (tiempo: {execution_time:.4f}s)")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno obteniendo capacidades: {str(e)}"
        )

@router.post("/analyze", response_model=MedicalResponse)
async def unified_medical_analysis(
    request: MedicalAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
) -> MedicalResponse:
    """
    🔬 Endpoint unificado para análisis médicos

    Procesa solicitudes de análisis médico routing automáticamente al servicio
    apropiado basado en el tipo de servicio y análisis especificado.

    Args:
        request: Solicitud de análisis médico
        background_tasks: Tareas en segundo plano
        current_user: Usuario autenticado

    Returns:
        MedicalResponse con resultados del análisis
    """
    start_time = datetime.now()
    session_id = request.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    try:
        logger.info(f"🔬 Iniciando análisis médico: {request.service_type}/{request.analysis_type} "
                   f"para usuario {current_user.get('username', 'unknown')}")

        registry = get_medicine_registry()

        # Verificar que el servicio está disponible
        services = await registry.list_services()
        if request.service_type not in services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio '{request.service_type}' no disponible"
            )

        # Routing dinámico basado en tipo de servicio
        result = await _route_analysis_request(registry, request, current_user, session_id)

        execution_time = (datetime.now() - start_time).total_seconds()

        # Añadir tarea de logging en segundo plano
        background_tasks.add_task(
            _log_medical_operation,
            "analysis",
            request.service_type,
            current_user.get('username', 'unknown'),
            execution_time,
            success=True
        )

        return MedicalResponse(
            success=True,
            service_info={
                "service": request.service_type,
                "analysis_type": request.analysis_type,
                "version": await registry.get_service_version(request.service_type)
            },
            result=result,
            metadata={
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "session_id": session_id,
                "user": current_user.get('username', 'unknown'),
                "patient_id": request.patient_id
            },
            performance_metrics={
                "processing_time": execution_time,
                "data_size": len(str(request.data)),
                "memory_usage": _estimate_memory_usage(request.data)
            }
        )

    except HTTPException:
        # Añadir tarea de logging de error en segundo plano
        execution_time = (datetime.now() - start_time).total_seconds()
        background_tasks.add_task(
            _log_medical_operation,
            "analysis",
            request.service_type,
            current_user.get('username', 'unknown'),
            execution_time,
            success=False
        )
        raise
    except MedicalError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error en análisis médico: {e} (tiempo: {execution_time:.4f}s)")

        background_tasks.add_task(
            _log_medical_operation,
            "analysis",
            request.service_type,
            current_user.get('username', 'unknown'),
            execution_time,
            success=False
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en análisis médico: {str(e)}"
        )

@router.post("/predict", response_model=MedicalResponse)
async def unified_medical_prediction(
    request: MedicalPredictionRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
) -> MedicalResponse:
    """
    🔮 Endpoint unificado para predicciones médicas

    Procesa solicitudes de predicción médica routing automáticamente al servicio
    de machine learning apropiado.

    Args:
        request: Solicitud de predicción médica
        background_tasks: Tareas en segundo plano
        current_user: Usuario autenticado

    Returns:
        MedicalResponse con resultados de la predicción
    """
    start_time = datetime.now()

    try:
        logger.info(f"🔮 Iniciando predicción médica: {request.service_type}/{request.prediction_type} "
                   f"para usuario {current_user.get('username', 'unknown')}")

        registry = get_medicine_registry()

        # Routing dinámico para predicciones
        result = await _route_prediction_request(registry, request, current_user)

        execution_time = (datetime.now() - start_time).total_seconds()

        background_tasks.add_task(
            _log_medical_operation,
            "prediction",
            request.service_type,
            current_user.get('username', 'unknown'),
            execution_time,
            success=True
        )

        return MedicalResponse(
            success=True,
            service_info={
                "service": request.service_type,
                "prediction_type": request.prediction_type,
                "confidence_threshold": str(request.confidence_threshold)
            },
            result=result,
            metadata={
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "user": current_user.get('username', 'unknown')
            },
            performance_metrics={
                "prediction_confidence": result.get('confidence', 0.0),
                "processing_time": execution_time
            }
        )

    except MedicalError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error en predicción médica: {e} (tiempo: {execution_time:.4f}s)")

        background_tasks.add_task(
            _log_medical_operation,
            "prediction",
            request.service_type,
            current_user.get('username', 'unknown'),
            execution_time,
            success=False
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en predicción médica: {str(e)}"
        )

@router.post("/process", response_model=MedicalResponse)
async def unified_medical_processing(
    request: MedicalProcessingRequest,
    current_user: Dict = Depends(get_current_user)
) -> MedicalResponse:
    """
    ⚙️ Endpoint unificado para procesamiento médico

    Args:
        request: Solicitud de procesamiento médico
        current_user: Usuario autenticado

    Returns:
        MedicalResponse con resultados del procesamiento
    """
    start_time = datetime.now()

    try:
        logger.info(f"⚙️ Iniciando procesamiento médico: {request.service_type}/{request.processing_type}")

        registry = get_medicine_registry()
        result = await _route_processing_request(registry, request, current_user)

        execution_time = (datetime.now() - start_time).total_seconds()

        return MedicalResponse(
            success=True,
            service_info={
                "service": request.service_type,
                "processing_type": request.processing_type,
                "output_format": request.output_format or "json"
            },
            result=result,
            metadata={
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "user": current_user.get('username', 'unknown')
            }
        )

    except MedicalError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error en procesamiento médico: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno en procesamiento: {str(e)}"
        )

@router.get("/health")
async def medical_services_health(
    current_user: Dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    🏥 Estado de salud de todos los servicios médicos

    Returns:
        Dict con estado de salud de todos los servicios
    """
    start_time = datetime.now()

    try:
        logger.info("🏥 Verificando estado de salud de servicios médicos")

        registry = get_medicine_registry()
        services = await registry.list_services()

        health_status = {}
        overall_status = "healthy"

        for service_name in services:
            try:
                service_health = await registry.get_service_health(service_name)
                health_status[service_name] = service_health

                if service_health.get("status") != "healthy":
                    overall_status = "degraded"

            except MedicalError as e:
                health_status[service_name] = {
                    "status": "error",
                    "error": str(e)
                }
                overall_status = "degraded"

        execution_time = (datetime.now() - start_time).total_seconds()

        return {
            "overall_status": overall_status,
            "services": health_status,
            "total_services": len(services),
            "healthy_services": len([s for s in health_status.values() if s.get("status") == "healthy"]),
            "metadata": {
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat(),
                "checked_by": current_user.get('username', 'unknown')
            }
        }

    except MedicalError as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        logger.error(f"❌ Error verificando salud de servicios: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error verificando salud de servicios: {str(e)}"
        )

# =====================================================================================
# STREAMING ENDPOINTS
# =====================================================================================

@router.get("/stream/{service_type}/{stream_type}")
async def stream_medical_data(
    service_type: str,
    stream_type: str,
    current_user: Dict = Depends(get_current_user)
) -> StreamingResponse:
    """
    📡 Streaming de datos médicos en tiempo real

    Args:
        service_type: Tipo de servicio médico
        stream_type: Tipo de stream (monitoring, analysis, etc.)
        current_user: Usuario autenticado

    Returns:
        StreamingResponse con datos médicos
    """
    async def generate_medical_stream():
        registry = get_medicine_registry()

        try:
            # Inicializar stream
            stream = await registry.create_medical_stream(service_type, stream_type)

            async for data in stream:
                # Formatear datos para streaming
                formatted_data = {
                    "timestamp": datetime.now().isoformat(),
                    "service": service_type,
                    "stream_type": stream_type,
                    "data": data
                }

                yield f"data: {formatted_data}\n\n"
                await asyncio.sleep(0.1)  # Control de flujo

        except MedicalError as e:
            error_data = {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        generate_medical_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )

# =====================================================================================
# HELPER FUNCTIONS
# =====================================================================================

async def _route_analysis_request(
    registry: MedicineRegistry,
    request: MedicalAnalysisRequest,
    user: Dict,
    session_id: str
) -> Dict[str, Any]:
    """Routing inteligente para solicitudes de análisis"""

    if request.service_type == "genomics":
        service = await registry.get_genomics_service()
        return await service.analyze_variants(
            request.data,
            analysis_type=request.analysis_type,
            parameters=request.parameters
        )

    elif request.service_type == "imaging":
        service = await registry.get_medical_imaging_service()
        return await service.analyze_medical_image(
            request.data,
            analysis_type=request.analysis_type,
            options=request.options
        )

    elif request.service_type == "biomechanics":
        service = await registry.get_biomechanics_service()
        return await service.analyze_movement_data(
            request.data,
            analysis_type=request.analysis_type
        )

    elif request.service_type in ["personalized_medicine", "pharmacogenomics"]:
        service = await registry.get_personalized_medicine_service()
        return await service.analyze_pharmacogenomics(request.data)

    else:
        # Routing genérico
        service = await registry.get_service(request.service_type)
        if hasattr(service, 'analyze'):
            return await service.analyze(request.data, request.analysis_type)
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Análisis no implementado para servicio {request.service_type}"
            )

async def _route_prediction_request(
    registry: MedicineRegistry,
    request: MedicalPredictionRequest,
    user: Dict
) -> Dict[str, Any]:
    """Routing para solicitudes de predicción"""

    if request.service_type == "alphafold3":
        service = await registry.get_protein_structure_service()
        return await service.predict_protein_structure(
            request.input_data.get("sequence"),
            options=request.model_configuration
        )

    elif request.service_type in ["personalized_medicine", "pharmacogenomics"]:
        service = await registry.get_personalized_medicine_service()
        return await service.predict_drug_response(request.input_data)

    else:
        # Routing genérico
        service = await registry.get_service(request.service_type)
        if hasattr(service, 'predict'):
            return await service.predict(request.input_data, request.prediction_type)
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Predicción no implementada para servicio {request.service_type}"
            )

async def _route_processing_request(
    registry: MedicineRegistry,
    request: MedicalProcessingRequest,
    user: Dict
) -> Dict[str, Any]:
    """Routing para solicitudes de procesamiento"""

    if request.service_type == "clinicalbert":
        service = await registry.get_nlp_service()
        return await service.extract_clinical_entities(
            request.data_source.get("clinical_text")
        )

    else:
        # Routing genérico
        service = await registry.get_service(request.service_type)
        if hasattr(service, 'process'):
            return await service.process(request.data_source, request.processing_type)
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Procesamiento no implementado para servicio {request.service_type}"
            )

async def _log_medical_operation(
    operation_type: str,
    service_type: str,
    username: str,
    execution_time: float,
    success: bool
):
    """Log operaciones médicas en segundo plano"""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_type,
            "service": service_type,
            "user": username,
            "execution_time": execution_time,
            "success": success
        }

        # Aquí se podría escribir a base de datos, archivo, etc.
        logger.info(f"📊 Medical Operation Log: {log_entry}")

    except MedicalError as e:
        logger.error(f"❌ Error logging medical operation: {e}")

def _estimate_memory_usage(data: Any) -> float:
    """Estima el uso de memoria de los datos"""
    try:
        import sys
        return sys.getsizeof(str(data)) / (1024 * 1024)  # MB
    except MedicalError:
        return 0.0

# =====================================================================================
# LEGACY COMPATIBILITY ENDPOINTS
# =====================================================================================

@router.get("/legacy/api", include_in_schema=False)
async def legacy_api_redirect():
    """Redirección para compatibilidad con API legacy"""
    return {
        "message": "This endpoint has been moved to /medical/services",
        "new_endpoint": "/medical/services",
        "deprecated": True
    }

@router.post("/legacy/compute", include_in_schema=False)
async def legacy_compute_redirect():
    """Redirección para compatibilidad con endpoint compute legacy"""
    return {
        "message": "This endpoint has been moved to /medical/analyze",
        "new_endpoint": "/medical/analyze",
        "deprecated": True
    }
