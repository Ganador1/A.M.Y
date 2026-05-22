"""
Router MatSciBERT para AXIOM - Análisis de Texto en Ciencias de Materiales

Este módulo proporciona endpoints especializados para el análisis inteligente de texto
en el dominio de las ciencias de materiales utilizando el modelo MatSciBERT.

== CAPACIDADES ==
• Extracción y análisis de propiedades de materiales
• Análisis de rutas de síntesis química
• Comparación de similitud entre materiales
• Predicción de propiedades a partir de descripciones textuales
• Procesamiento de literatura científica en materiales

== ENDPOINTS DISPONIBLES ==
• POST /analyze - Análisis comprehensivo de texto de materiales
• POST /similarity - Cálculo de similitud entre textos de investigación
• POST /predict-properties - Predicción de propiedades de materiales
• GET /service-info - Información del servicio MatSciBERT

== DEPENDENCIAS ==
• MatSciBERTService: Servicio principal de análisis de texto
• transformers: Biblioteca de modelos de lenguaje
• torch: Framework de deep learning
• fastapi: Framework web asíncrono
• pydantic: Validación de datos

== USO ==
Este router se integra con el servicio MatSciBERT para proporcionar análisis
inteligente de texto en el contexto de investigación en ciencias de materiales,
permitiendo extraer información estructurada de literatura científica no estructurada.

== SEGURIDAD ==
• Validación estricta de entradas de texto
• Logging comprehensivo de operaciones
• Manejo seguro de errores sin exposición de información sensible
• Rate limiting recomendado para endpoints de análisis intensivo
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Dict, Any, List, Optional

from app.services.matscibert_service import MatSciBERTService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError

# Create router
router = APIRouter()

# Initialize service with lazy loading
matscibert_service = None

def get_matscibert_service():
    global matscibert_service
    if matscibert_service is None:
        matscibert_service = MatSciBERTService()
    return matscibert_service

# Request Models
class MaterialsAnalysisRequest(BaseModel):
    text: str = Field(..., description="Materials science text for analysis", min_length=20)

class MaterialsSimilarityRequest(BaseModel):
    text1: str = Field(..., description="First materials text", min_length=20)
    text2: str = Field(..., description="Second materials text", min_length=20)

class MaterialPropertyPredictionRequest(BaseModel):
    material_description: str = Field(..., description="Material description for property prediction", min_length=10)

class SynthesisRouteAnalysisRequest(BaseModel):
    synthesis_description: str = Field(..., description="Synthesis route description", min_length=20)
    material_target: Optional[str] = Field(None, description="Target material if known")

class MaterialsBatchAnalysisRequest(BaseModel):
    texts: List[str] = Field(..., description="List of materials texts to analyze")
    analysis_type: str = Field("comprehensive", description="Type of analysis to perform")

# Response Models
class AnalysisResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Analysis results")
    timestamp: str = Field(..., description="Response timestamp")

class SimilarityResponse(BaseModel):
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Similarity results")
    timestamp: str = Field(..., description="Response timestamp")

class ServiceInfoResponse(BaseModel):
    status: str = Field(..., description="Response status")
    data: Dict[str, Any] = Field(..., description="Service information")
    timestamp: str = Field(..., description="Response timestamp")

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_materials_text(request: MaterialsAnalysisRequest):
    """
    Análisis comprehensivo de texto en ciencias de materiales.

    Realiza extracción de propiedades, análisis de síntesis y caracterización
    de materiales a partir de texto científico no estructurado.

    Args:
        request: Solicitud con texto de materiales para analizar

    Returns:
        Resultados del análisis incluyendo propiedades extraídas y metadatos

    Raises:
        HTTPException: Si el análisis falla o el texto es inválido
    """
    try:
        logger.info("🔬 Iniciando análisis de texto de materiales (longitud: %d caracteres)", len(request.text))
        service = get_matscibert_service()
        result = await service.analyze_materials_text(request.text)

        if not result.get('success'):
            logger.error("❌ Análisis de materiales falló: %s", result.get('error', 'Unknown error'))
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Materials analysis failed')
            )

        logger.info("✅ Análisis de materiales completado exitosamente")
        return AnalysisResponse(
            status="success",
            message="Materials text analyzed successfully",
            data=result['data'],
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        logger.exception("❌ Error inesperado en análisis de materiales")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during materials analysis"
        ) from e

@router.post("/similarity", response_model=SimilarityResponse)
async def calculate_materials_similarity(request: MaterialsSimilarityRequest):
    """
    Calcula similitud semántica entre textos de investigación en materiales.

    Compara dos textos científicos de materiales utilizando embeddings
    contextuales para determinar grado de similitud temática y técnica.

    Args:
        request: Solicitud con dos textos de materiales para comparar

    Returns:
        Puntaje de similitud y análisis detallado de diferencias

    Raises:
        HTTPException: Si el cálculo de similitud falla
    """
    try:
        logger.info("🔍 Calculando similitud entre textos de materiales (longitudes: %d, %d)",
                   len(request.text1), len(request.text2))
        service = get_matscibert_service()
        result = await service.calculate_materials_similarity(
            request.text1,
            request.text2
        )

        if not result.get('success'):
            logger.error("❌ Cálculo de similitud falló: %s", result.get('error', 'Unknown error'))
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Materials similarity calculation failed')
            )

        logger.info("✅ Similitud de materiales calculada exitosamente")
        return SimilarityResponse(
            status="success",
            message="Materials similarity calculated successfully",
            data=result['data'],
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        logger.exception("❌ Error inesperado en cálculo de similitud")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during similarity calculation"
        ) from e

@router.post("/predict-properties", response_model=AnalysisResponse)
async def predict_material_properties(request: MaterialPropertyPredictionRequest):
    """
    Predice propiedades de materiales a partir de descripciones textuales.

    Utiliza procesamiento de lenguaje natural para inferir propiedades
    físicas, químicas y estructurales de materiales descritos en texto.

    Args:
        request: Solicitud con descripción del material

    Returns:
        Propiedades predichas con niveles de confianza

    Raises:
        HTTPException: Si la predicción falla
    """
    try:
        logger.info("🔮 Prediciendo propiedades de material (longitud descripción: %d)",
                   len(request.material_description))
        service = get_matscibert_service()
        result = await service.predict_material_properties(request.material_description)

        if not result.get('success'):
            logger.error("❌ Predicción de propiedades falló: %s", result.get('error', 'Unknown error'))
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Material property prediction failed')
            )

        logger.info("✅ Propiedades de material predichas exitosamente")
        return AnalysisResponse(
            status="success",
            message="Material properties predicted successfully",
            data=result['data'],
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        logger.exception("❌ Error inesperado en predicción de propiedades")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during property prediction"
        ) from e

@router.post("/analyze-synthesis", response_model=AnalysisResponse)
async def analyze_synthesis_route(request: SynthesisRouteAnalysisRequest):
    """
    Analiza rutas de síntesis química descritas en texto.

    Extrae información sobre métodos de síntesis, condiciones experimentales,
    precursores y productos a partir de descripciones textuales.

    Args:
        request: Solicitud con descripción de ruta de síntesis

    Returns:
        Análisis estructurado de la ruta de síntesis

    Raises:
        HTTPException: Si el análisis de síntesis falla
    """
    try:
        logger.info("⚗️ Analizando ruta de síntesis (longitud: %d)", len(request.synthesis_description))
        service = get_matscibert_service()
        result = await service.analyze_synthesis_route(
            request.synthesis_description,
            request.material_target
        )

        if not result.get('success'):
            logger.error("❌ Análisis de síntesis falló: %s", result.get('error', 'Unknown error'))
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Synthesis route analysis failed')
            )

        logger.info("✅ Ruta de síntesis analizada exitosamente")
        return AnalysisResponse(
            status="success",
            message="Synthesis route analyzed successfully",
            data=result['data'],
            timestamp=datetime.now().isoformat()
        )

    except HTTPException:
        raise
    except BiologyError as e:
        logger.exception("❌ Error inesperado en análisis de síntesis")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during synthesis analysis"
        ) from e

@router.get("/service-info", response_model=ServiceInfoResponse)
async def get_matscibert_service_info():
    """
    Obtiene información detallada del servicio MatSciBERT.

    Proporciona metadatos sobre el modelo, capacidades disponibles,
    configuración actual y estadísticas de uso.

    Returns:
        Información comprehensiva del servicio MatSciBERT

    Raises:
        HTTPException: Si no se puede obtener la información del servicio
    """
    try:
        logger.info("📊 Obteniendo información del servicio MatSciBERT")
        service = get_matscibert_service()
        info = service.get_service_info()

        logger.info("✅ Información del servicio obtenida exitosamente")
        return ServiceInfoResponse(
            status="success",
            data=info,
            timestamp=datetime.now().isoformat()
        )

    except BiologyError as e:
        logger.exception("❌ Error obteniendo información del servicio MatSciBERT")
        raise HTTPException(
            status_code=500,
            detail="Failed to get MatSciBERT service information"
        ) from e
