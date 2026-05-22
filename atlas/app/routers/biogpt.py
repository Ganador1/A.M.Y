"""
BioGPT Router

Router FastAPI para generación y análisis de texto biomédico utilizando modelos BioGPT.
Proporciona endpoints REST API para generación de texto biomédico y completado con parámetros configurables,
resumen de literatura científica y generación de resúmenes, respuesta a preguntas clínicas con contexto médico,
desarrollo de hipótesis de investigación y asistencia en escritura científica, clarificación de terminología médica
y explicación de conceptos, síntesis de revisiones de literatura y extracción de hallazgos clave,
mejora de documentación clínica y soporte para propuestas de investigación.

Capacidades principales:
- Generación de texto biomédico y completado con parámetros configurables
- Resumen de literatura científica y generación automática de resúmenes
- Respuesta a preguntas clínicas con contexto médico especializado
- Desarrollo de hipótesis de investigación y asistencia en escritura científica
- Clarificación de terminología médica y explicación de conceptos biomédicos
- Síntesis de revisiones de literatura y extracción de hallazgos clave
- Mejora de documentación clínica y soporte para propuestas de investigación
- Análisis de coherencia científica y validación de contenido médico
- Generación de resúmenes ejecutivos de artículos científicos
- Soporte multi-idioma para literatura biomédica internacional

Endpoints disponibles:
- POST /generate: Generación de texto biomédico con parámetros configurables
- POST /summarize: Resumen de texto biomédico con ratio objetivo
- POST /answer-question: Respuesta a preguntas biomédicas con contexto
- POST /develop-hypothesis: Desarrollo de hipótesis de investigación
- POST /explain-concept: Explicación de conceptos médicos y terminología
- POST /literature-review: Síntesis de revisiones de literatura
- GET /capabilities: Capacidades del servicio BioGPT
- GET /health: Verificación del estado del servicio
- POST /clinical-document: Mejora de documentación clínica
- GET /examples: Ejemplos de uso del servicio BioGPT

Dependencias:
- BioGPTService: Servicio principal de procesamiento BioGPT
- BioGPTGenerationRequest: Solicitud de generación de texto
- BiomedicalSummarizationRequest: Solicitud de resumen biomédico
- BiomedicalQuestionRequest: Solicitud de pregunta biomédica

Uso típico:
    from app.routers.biogpt import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.domains.biology.services.biogpt_service import BioGPTService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError

# Create router
router = APIRouter()

# Initialize service with lazy loading
biogpt_service = None

def get_biogpt_service():
    global biogpt_service
    if biogpt_service is None:
        biogpt_service = BioGPTService()
    return biogpt_service

# Request/Response Models
class BioGPTGenerationRequest(BaseModel):
    prompt: str = Field(..., description="Biomedical text prompt for generation", min_length=10)
    max_length: int = Field(512, description="Maximum length of generated text", ge=50, le=1024)
    temperature: float = Field(0.7, description="Generation temperature (creativity)", ge=0.1, le=2.0)
    top_p: float = Field(0.9, description="Top-p sampling parameter", ge=0.1, le=1.0)

class BiomedicalSummarizationRequest(BaseModel):
    text: str = Field(..., description="Biomedical text to summarize", min_length=50)
    target_ratio: float = Field(0.3, description="Target summary ratio", ge=0.1, le=0.8)

class BiomedicalQuestionRequest(BaseModel):
    question: str = Field(..., description="Biomedical question to answer", min_length=5)
    context: Optional[str] = Field(None, description="Optional context for the question")

@router.post("/generate")
async def generate_biomedical_text(request: BioGPTGenerationRequest):
    """
    Generate biomedical text using BioGPT
    
    **Features:**
    - Scientific text completion and generation
    - Medical literature enhancement
    - Research hypothesis development
    - Clinical writing assistance
    
    **Use Cases:**
    - Scientific writing assistance
    - Literature completion
    - Research proposal development
    - Medical documentation
    """
    try:
        if len(request.prompt.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Prompt must be at least 10 characters long"
            )
        
        service = get_biogpt_service()
        result = await service.generate_biomedical_text(
            prompt=request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Text generation failed')
            )
        
        return {
            "status": "success",
            "message": "Biomedical text generated successfully",
            "data": result['data'],
            "generation_info": {
                "model": "BioGPT",
                "parameters": {
                    "max_length": request.max_length,
                    "temperature": request.temperature,
                    "top_p": request.top_p
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except BiologyError as e:
        logger.error(f"BioGPT generation endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate biomedical text: {str(e)}"
        )

@router.post("/summarize")
async def summarize_biomedical_text(request: BiomedicalSummarizationRequest):
    """
    Summarize biomedical literature using BioGPT
    
    **Features:**
    - Scientific paper summarization
    - Research abstract generation
    - Key finding extraction
    - Clinical report condensation
    
    **Use Cases:**
    - Literature review preparation
    - Abstract generation
    - Research synthesis
    - Clinical documentation
    """
    try:
        service = get_biogpt_service()
        result = await service.summarize_biomedical_text(
            text=request.text,
            target_ratio=request.target_ratio
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Text summarization failed')
            )
        
        return {
            "status": "success",
            "message": "Biomedical text summarized successfully",
            "data": result['data'],
            "summarization_info": {
                "model": "BioGPT",
                "target_ratio": request.target_ratio,
                "compression_achieved": result['data']['summary_ratio'],
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except BiologyError as e:
        logger.error(f"BioGPT summarization endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to summarize biomedical text: {str(e)}"
        )

@router.post("/question-answering")
async def answer_biomedical_question(request: BiomedicalQuestionRequest):
    """
    Answer biomedical questions using BioGPT
    
    **Features:**
    - Clinical question answering
    - Research methodology guidance
    - Scientific concept explanation
    - Medical terminology clarification
    
    **Use Cases:**
    - Research support
    - Clinical decision support
    - Educational assistance
    - Literature interpretation
    """
    try:
        service = get_biogpt_service()
        result = await service.answer_biomedical_question(
            question=request.question,
            context=request.context or ""
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Question answering failed')
            )
        
        return {
            "status": "success",
            "message": "Biomedical question answered successfully",
            "data": result['data'],
            "qa_info": {
                "model": "BioGPT",
                "context_provided": bool(request.context),
                "question_length": len(request.question),
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except BiologyError as e:
        logger.error(f"BioGPT Q&A endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to answer biomedical question: {str(e)}"
        )

@router.get("/service-info")
async def get_biogpt_service_info():
    """Get BioGPT service information and capabilities"""
    try:
        service = get_biogpt_service()
        info = service.get_service_info()
        
        return {
            "status": "success",
            "message": "BioGPT service info retrieved successfully",
            "data": info,
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"BioGPT service info error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service info: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check for BioGPT service"""
    try:
        service = get_biogpt_service()
        is_healthy = service.model is not None
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "service": "BioGPT",
            "model_loaded": is_healthy,
            "capabilities": [
                "biomedical_text_generation",
                "literature_summarization", 
                "clinical_question_answering"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except BiologyError as e:
        logger.error(f"BioGPT health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "BioGPT",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
