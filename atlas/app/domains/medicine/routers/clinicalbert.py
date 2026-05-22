"""
ClinicalBERT Router

Router FastAPI para análisis de texto clínico y procesamiento de lenguaje natural médico utilizando ClinicalBERT.
Proporciona endpoints REST API para extracción de entidades clínicas de notas médicas y datos EHR,
clasificación de texto clínico por especialidad, urgencia y diagnóstico, análisis de similitud semántica
entre documentos clínicos, reconocimiento y normalización de terminología médica, análisis de notas clínicas
y extracción de datos estructurados, procesamiento de datos EHR e identificación de conceptos clínicos.

Capacidades principales:
- Extracción de entidades clínicas de notas médicas y datos EHR (síntomas, tratamientos, diagnósticos)
- Clasificación de texto clínico por especialidad médica, nivel de urgencia y tipo de diagnóstico
- Análisis de similitud semántica entre documentos clínicos y registros médicos
- Reconocimiento y normalización de terminología médica especializada
- Análisis de notas clínicas y extracción automática de datos estructurados
- Procesamiento de datos EHR e identificación de conceptos clínicos clave
- Análisis de coherencia clínica y validación de información médica
- Extracción de información estructurada de registros médicos no estructurados
- Soporte para múltiples idiomas médicos y terminologías especializadas
- Integración con sistemas de salud electrónicos y bases de datos médicas

Endpoints disponibles:
- POST /extract-entities: Extracción de entidades clínicas de texto médico
- POST /classify-text: Clasificación de texto clínico por especialidad/urgencia
- POST /semantic-similarity: Análisis de similitud semántica entre textos clínicos
- POST /normalize-terminology: Normalización de terminología médica
- POST /analyze-notes: Análisis de notas clínicas y extracción estructurada
- POST /process-ehr: Procesamiento de datos EHR
- GET /capabilities: Capacidades del servicio ClinicalBERT
- GET /health: Verificación del estado del servicio
- POST /validate-clinical: Validación de coherencia clínica

Dependencias:
- ClinicalBERTService: Servicio principal de procesamiento ClinicalBERT
- ClinicalEntityExtractionRequest: Solicitud de extracción de entidades
- ClinicalClassificationRequest: Solicitud de clasificación clínica
- ClinicalSimilarityRequest: Solicitud de similitud semántica

Uso típico:
    from app.domains.medicine.routers.clinicalbert import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

from ..personalized.clinicalbert_service import get_clinical_bert_service
from app.core.bootstrap_logging import logger
from app.exceptions.domain.medicine import MedicalError

# Create router
router = APIRouter()

# Initialize service with lazy loading
clinicalbert_service = None

def get_clinicalbert_service():
    """Get ClinicalBERT service instance"""
    return get_clinical_bert_service()

# Request Models
class ClinicalEntityExtractionRequest(BaseModel):
    clinical_text: str = Field(..., description="Clinical text for entity extraction", min_length=10)

class ClinicalClassificationRequest(BaseModel):
    clinical_text: str = Field(..., description="Clinical text to classify", min_length=10)
    classification_type: str = Field("specialty", description="Classification type: specialty, urgency, etc.")

class ClinicalSimilarityRequest(BaseModel):
    text1: str = Field(..., description="First clinical text", min_length=10)
    text2: str = Field(..., description="Second clinical text", min_length=10)

@router.post("/extract-entities")
async def extract_clinical_entities(request: ClinicalEntityExtractionRequest):
    """Extract clinical entities from medical text"""
    try:
        service = get_clinicalbert_service()
        result = await service.extract_clinical_entities(request.clinical_text)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Clinical entity extraction failed')
            )
        
        return {
            "status": "success",
            "message": "Clinical entities extracted successfully",
            "data": result['data'],
            "timestamp": datetime.now().isoformat()
        }
        
    except MedicalError as e:
        logger.error(f"Clinical entity extraction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract clinical entities: {str(e)}"
        )

@router.post("/classify")
async def classify_clinical_text(request: ClinicalClassificationRequest):
    """Classify clinical text by specialty or other criteria"""
    try:
        service = get_clinicalbert_service()
        result = await service.classify_clinical_text(
            request.clinical_text,
            request.classification_type
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Clinical classification failed')
            )
        
        return {
            "status": "success",
            "message": "Clinical text classified successfully",
            "data": result['data'],
            "timestamp": datetime.now().isoformat()
        }
        
    except MedicalError as e:
        logger.error(f"Clinical classification error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to classify clinical text: {str(e)}"
        )

@router.post("/similarity")
async def analyze_clinical_similarity(request: ClinicalSimilarityRequest):
    """Analyze similarity between clinical texts"""
    try:
        service = get_clinicalbert_service()
        result = await service.analyze_clinical_similarity(
            request.text1,
            request.text2
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Clinical similarity analysis failed')
            )
        
        return {
            "status": "success",
            "message": "Clinical similarity analyzed successfully",
            "data": result['data'],
            "timestamp": datetime.now().isoformat()
        }
        
    except MedicalError as e:
        logger.error(f"Clinical similarity analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze clinical similarity: {str(e)}"
        )

@router.get("/service-info")
async def get_clinicalbert_service_info():
    """Get ClinicalBERT service information"""
    try:
        service = get_clinicalbert_service()
        info = await service.get_service_health()
        
        return {
            "status": "success",
            "data": info,
            "timestamp": datetime.now().isoformat()
        }
        
    except MedicalError as e:
        logger.error(f"ClinicalBERT service info error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service info: {str(e)}"
        )
