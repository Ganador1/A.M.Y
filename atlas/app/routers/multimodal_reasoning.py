"""
Router para Multimodal Scientific Reasoning System

Endpoints para análisis científico multimodal usando Claude 3.5 y GPT-4V
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import json
import asyncio
import logging

from app.services.multimodal_reasoning_service import MultimodalReasoningService
from app.exceptions.domain.biology import BiologyError

logger = logging.getLogger(__name__)

router = APIRouter()

# Instancia global del servicio
reasoning_service = None

def get_reasoning_service():
    """Obtiene la instancia del servicio de razonamiento multimodal"""
    global reasoning_service
    if reasoning_service is None:
        reasoning_service = MultimodalReasoningService()
    return reasoning_service

# Modelos Pydantic para requests/responses

class DocumentAnalysisRequest(BaseModel):
    """Request para análisis de documento científico"""
    text: str = Field(..., description="Texto del documento científico")
    analysis_type: str = Field(default="comprehensive", description="Tipo de análisis")
    model_preference: str = Field(default="claude", description="Modelo preferido")
    include_images: bool = Field(default=False, description="Si incluir análisis de imágenes")

class DocumentAnalysisResponse(BaseModel):
    """Response del análisis de documento"""
    text_analysis: Dict[str, Any] = Field(..., description="Análisis del texto")
    image_analysis: Dict[str, Any] = Field(default={}, description="Análisis de imágenes")
    multimodal_synthesis: Dict[str, Any] = Field(default={}, description="Síntesis multimodal")
    scientific_insights: Dict[str, Any] = Field(..., description="Insights científicos")
    metadata: Dict[str, Any] = Field(..., description="Metadatos del análisis")

class ComparisonRequest(BaseModel):
    """Request para comparación de enfoques científicos"""
    documents: List[Dict[str, Any]] = Field(..., description="Lista de documentos a comparar")
    comparison_criteria: Optional[List[str]] = Field(default=None, description="Criterios de comparación")

class ComparisonResponse(BaseModel):
    """Response de comparación científica"""
    documents_analyzed: int = Field(..., description="Número de documentos analizados")
    criteria: List[str] = Field(..., description="Criterios utilizados")
    comparative_analysis: Dict[str, Any] = Field(..., description="Análisis comparativo")
    ranking: List[Dict[str, Any]] = Field(default=[], description="Ranking de documentos")
    recommendations: List[str] = Field(default=[], description="Recomendaciones")

class HypothesisRequest(BaseModel):
    """Request para generación de hipótesis"""
    research_context: str = Field(..., description="Contexto de investigación")
    existing_literature: Optional[List[str]] = Field(default=None, description="Literatura existente")
    constraints: Optional[Dict[str, Any]] = Field(default=None, description="Restricciones")

class HypothesisResponse(BaseModel):
    """Response de generación de hipótesis"""
    research_context: str = Field(..., description="Contexto original")
    generated_hypotheses: Dict[str, Any] = Field(..., description="Hipótesis generadas")
    methodology_suggestions: Dict[str, Any] = Field(default={}, description="Sugerencias metodológicas")
    testability_assessment: Dict[str, Any] = Field(default={}, description="Evaluación de testabilidad")
    timestamp: float = Field(..., description="Timestamp de generación")

# Endpoints

@router.post("/analyze-document", response_model=DocumentAnalysisResponse)
async def analyze_scientific_document(request: DocumentAnalysisRequest):
    """
    Analiza un documento científico usando modelos de IA multimodal
    
    - **text**: Texto del documento científico
    - **analysis_type**: Tipo de análisis (comprehensive, summary, critique)
    - **model_preference**: Modelo preferido (claude, gpt4v, hybrid)
    - **include_images**: Si incluir análisis de imágenes
    """
    try:
        service = get_reasoning_service()
        
        result = await service.analyze_scientific_document(
            text=request.text,
            images=None,  # Las imágenes se manejan por separado
            analysis_type=request.analysis_type,
            model_preference=request.model_preference
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return DocumentAnalysisResponse(**result)
        
    except BiologyError as e:
        logger.error(f"Error en análisis de documento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-multimodal")
async def analyze_multimodal_document(
    text: str = Form(...),
    analysis_type: str = Form(default="comprehensive"),
    model_preference: str = Form(default="claude"),
    images: List[UploadFile] = File(default=[])
):
    """
    Analiza un documento científico multimodal con texto e imágenes
    
    - **text**: Texto del documento
    - **analysis_type**: Tipo de análisis
    - **model_preference**: Modelo preferido
    - **images**: Lista de archivos de imagen
    """
    try:
        service = get_reasoning_service()
        
        # Procesar imágenes subidas
        image_data = []
        for image_file in images:
            content = await image_file.read()
            image_data.append(content)
        
        result = await service.analyze_scientific_document(
            text=text,
            images=image_data if image_data else None,
            analysis_type=analysis_type,
            model_preference=model_preference
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return JSONResponse(content=result)
        
    except BiologyError as e:
        logger.error(f"Error en análisis multimodal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare-approaches", response_model=ComparisonResponse)
async def compare_scientific_approaches(request: ComparisonRequest):
    """
    Compara múltiples enfoques científicos
    
    - **documents**: Lista de documentos con texto e imágenes
    - **comparison_criteria**: Criterios específicos de comparación
    """
    try:
        service = get_reasoning_service()
        
        result = await service.compare_scientific_approaches(
            documents=request.documents,
            comparison_criteria=request.comparison_criteria
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ComparisonResponse(**result)
        
    except BiologyError as e:
        logger.error(f"Error en comparación de enfoques: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-hypothesis", response_model=HypothesisResponse)
async def generate_research_hypothesis(request: HypothesisRequest):
    """
    Genera hipótesis de investigación basadas en contexto y literatura
    
    - **research_context**: Contexto de la investigación
    - **existing_literature**: Literatura existente relevante
    - **constraints**: Restricciones o limitaciones
    """
    try:
        service = get_reasoning_service()
        
        result = await service.generate_research_hypothesis(
            research_context=request.research_context,
            existing_literature=request.existing_literature,
            constraints=request.constraints
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return HypothesisResponse(**result)
        
    except BiologyError as e:
        logger.error(f"Error generando hipótesis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models():
    """
    Obtiene información sobre los modelos disponibles
    """
    try:
        service = get_reasoning_service()
        
        models_info = {
            "text_models": {
                "claude-3-5-sonnet": {
                    "provider": "Anthropic",
                    "capabilities": ["text_analysis", "scientific_reasoning", "image_analysis"],
                    "available": bool(service.anthropic_client)
                },
                "gpt-4-turbo": {
                    "provider": "OpenAI",
                    "capabilities": ["text_analysis", "scientific_reasoning"],
                    "available": bool(service.openai_client)
                }
            },
            "vision_models": {
                "gpt-4-vision": {
                    "provider": "OpenAI",
                    "capabilities": ["image_analysis", "multimodal_reasoning"],
                    "available": bool(service.openai_client)
                },
                "claude-3-5-sonnet-vision": {
                    "provider": "Anthropic",
                    "capabilities": ["image_analysis", "multimodal_reasoning"],
                    "available": bool(service.anthropic_client)
                }
            },
            "local_models": {
                "sentiment_analysis": {
                    "provider": "HuggingFace",
                    "capabilities": ["sentiment_analysis"],
                    "available": "sentiment" in service.local_models
                },
                "text_classification": {
                    "provider": "HuggingFace",
                    "capabilities": ["text_classification"],
                    "available": "classification" in service.local_models
                }
            }
        }
        
        return JSONResponse(content=models_info)
        
    except BiologyError as e:
        logger.error(f"Error obteniendo modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis-types")
async def get_analysis_types():
    """
    Obtiene los tipos de análisis disponibles
    """
    analysis_types = {
        "comprehensive": {
            "description": "Análisis completo y detallado",
            "includes": [
                "resumen_ejecutivo",
                "conceptos_clave",
                "metodología",
                "resultados",
                "limitaciones",
                "implicaciones",
                "recomendaciones"
            ]
        },
        "summary": {
            "description": "Resumen conciso del contenido",
            "includes": [
                "puntos_principales",
                "conclusiones_clave",
                "relevancia"
            ]
        },
        "critique": {
            "description": "Análisis crítico y evaluativo",
            "includes": [
                "fortalezas",
                "debilidades",
                "sesgos_potenciales",
                "validez_metodológica",
                "sugerencias_mejora"
            ]
        },
        "comparative": {
            "description": "Análisis comparativo entre documentos",
            "includes": [
                "similitudes",
                "diferencias",
                "ventajas_relativas",
                "ranking_calidad"
            ]
        },
        "hypothesis_generation": {
            "description": "Generación de hipótesis de investigación",
            "includes": [
                "hipótesis_principales",
                "hipótesis_nulas",
                "variables",
                "metodología_sugerida",
                "predicciones"
            ]
        }
    }
    
    return JSONResponse(content=analysis_types)

@router.get("/examples")
async def get_usage_examples():
    """
    Obtiene ejemplos de uso del sistema
    """
    examples = {
        "document_analysis": {
            "description": "Análisis de un paper científico",
            "example_request": {
                "text": "Abstract: This study investigates the effects of...",
                "analysis_type": "comprehensive",
                "model_preference": "claude"
            }
        },
        "multimodal_analysis": {
            "description": "Análisis de documento con gráficos",
            "example_request": {
                "text": "Results section with statistical analysis...",
                "images": ["graph1.png", "table1.jpg"],
                "analysis_type": "critique"
            }
        },
        "comparison": {
            "description": "Comparación de múltiples estudios",
            "example_request": {
                "documents": [
                    {"title": "Study A", "text": "..."},
                    {"title": "Study B", "text": "..."}
                ],
                "comparison_criteria": ["methodology", "sample_size", "statistical_power"]
            }
        },
        "hypothesis_generation": {
            "description": "Generación de hipótesis de investigación",
            "example_request": {
                "research_context": "Climate change effects on marine ecosystems",
                "existing_literature": ["Previous study 1", "Previous study 2"],
                "constraints": {"budget": "limited", "timeframe": "6_months"}
            }
        }
    }
    
    return JSONResponse(content=examples)

@router.get("/health")
async def health_check():
    """
    Verifica el estado del servicio de razonamiento multimodal
    """
    try:
        service = get_reasoning_service()
        health_status = await service.health_check()
        
        return JSONResponse(content=health_status)
        
    except BiologyError as e:
        logger.error(f"Error en health check: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "service": "MultimodalReasoningService",
                "status": "unhealthy",
                "error": str(e)
            }
        )

@router.post("/configure")
async def configure_service(config: Dict[str, Any]):
    """
    Configura el servicio con nuevos parámetros
    
    - **anthropic_api_key**: Clave API de Anthropic
    - **openai_api_key**: Clave API de OpenAI
    - **max_image_size**: Tamaño máximo de imagen
    - **max_text_length**: Longitud máxima de texto
    """
    try:
        global reasoning_service
        reasoning_service = MultimodalReasoningService(config)
        
        return JSONResponse(content={
            "status": "configured",
            "message": "Servicio reconfigurado exitosamente",
            "config_applied": list(config.keys())
        })
        
    except BiologyError as e:
        logger.error(f"Error configurando servicio: {e}")
        raise HTTPException(status_code=500, detail=str(e))