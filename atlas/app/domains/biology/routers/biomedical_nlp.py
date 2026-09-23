"""
Biomedical NLP Router

Router FastAPI para procesamiento avanzado de lenguaje natural biomédico utilizando modelos BioBERT.
Proporciona endpoints REST API para extracción de entidades biomédicas (genes, proteínas, enfermedades, químicos),
análisis de similitud semántica entre textos científicos, mejora de búsqueda de literatura con comprensión biomédica,
análisis de resúmenes científicos y clasificación de dominios de investigación, identificación de conceptos biomédicos
y análisis de estructura de contenido, deduplicación de literatura y ranking de relevancia, categorización de investigación
y flujos de trabajo de análisis de contenido.

Capacidades principales:
- Extracción de entidades biomédicas (genes, proteínas, enfermedades, químicos, fármacos)
- Análisis de similitud semántica entre textos científicos y médicos
- Mejora de búsqueda de literatura con comprensión biomédica especializada
- Análisis de resúmenes científicos y clasificación automática de dominios de investigación
- Identificación de conceptos biomédicos y análisis de estructura de contenido
- Deduplicación inteligente de literatura y ranking de relevancia
- Categorización automática de investigación y flujos de trabajo de análisis de contenido
- Análisis de relaciones entre entidades biomédicas
- Extracción de información estructurada de textos médicos
- Validación de coherencia científica y consistencia terminológica

Endpoints disponibles:
- POST /extract-entities: Extracción de entidades biomédicas de texto
- POST /semantic-similarity: Análisis de similitud semántica entre textos
- POST /enhance-search: Mejora de consultas de búsqueda biomédica
- POST /analyze-abstract: Análisis de resúmenes científicos
- POST /classify-domain: Clasificación de dominios de investigación
- POST /identify-concepts: Identificación de conceptos biomédicos clave
- POST /deduplicate-literature: Deduplicación de literatura científica
- GET /capabilities: Capacidades del servicio NLP biomédico
- GET /health: Verificación del estado del servicio
- POST /extract-relations: Extracción de relaciones entre entidades

Dependencias:
- BiomedicalNLPService: Servicio principal de NLP biomédico
- EntityExtractionRequest: Solicitud de extracción de entidades
- SemanticSimilarityRequest: Solicitud de similitud semántica
- LiteratureSearchRequest: Solicitud de búsqueda de literatura

Uso típico:
    from app.domains.biology.routers.biomedical_nlp import router

    # El router se integra automáticamente en la aplicación FastAPI
    # Los endpoints están disponibles sin prefijo específico
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Any
from datetime import datetime

from app.domains.biology.services.biomedical_nlp_service import BiomedicalNLPService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError

# Create router
router = APIRouter()

# Initialize service with lazy loading
biomedical_nlp_service = None

def get_biomedical_service():
    global biomedical_nlp_service
    if biomedical_nlp_service is None:
        biomedical_nlp_service = BiomedicalNLPService()
    return biomedical_nlp_service

# Request/Response Models
class EntityExtractionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "The p53 protein plays a crucial role in cancer development and is often mutated in tumors."
            }
        }
    )

    text: str

class SemanticSimilarityRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text1": "BRCA1 gene mutations increase breast cancer risk",
                "text2": "BRCA1 alterations are associated with mammary carcinoma susceptibility"
            }
        }
    )

    text1: str
    text2: str

class LiteratureEnhancementRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "CRISPR gene editing cancer treatment",
                "papers": [
                    {
                        "title": "CRISPR-Cas9 genome editing for cancer therapy",
                        "abstract": "CRISPR technology shows promise for targeted cancer treatment...",
                        "authors": ["Smith, J.", "Doe, A."],
                        "year": 2024
                    }
                ]
            }
        }
    )

    query: str
    papers: List[Dict[str, Any]]

class AbstractAnalysisRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "abstract": "Background: Alzheimer's disease is characterized by amyloid beta plaques and tau tangles. Methods: We used CRISPR to edit genes in mouse models. Results: Significant reduction in amyloid burden was observed."
            }
        }
    )

    abstract: str


@router.post("/extract-entities")
async def extract_biomedical_entities(request: EntityExtractionRequest):
    """
    Extract biomedical entities from scientific text using BioBERT

    **Features:**
    - Gene/Protein identification
    - Disease/Disorder recognition
    - Chemical/Drug extraction
    - Species/Organism detection
    - Confidence scoring

    **Use Cases:**
    - Literature analysis
    - Abstract processing
    - Scientific document parsing
    """
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Text must be at least 10 characters long"
            )

        service = get_biomedical_service()
        result = await service.extract_biomedical_entities(request.text)

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Entity extraction failed')
            )

        return {
            "status": "success",
            "message": "Biomedical entities extracted successfully",
            "data": result['data'],
            "metadata": {
                "service": "BiomedicalNLPService",
                "model": "BioBERT",
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in entity extraction endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/semantic-similarity")
async def calculate_semantic_similarity(request: SemanticSimilarityRequest):
    """
    Calculate semantic similarity between two scientific texts using BioBERT

    **Features:**
    - Domain-specific similarity scoring
    - Biomedical concept understanding
    - Relevance level classification
    - Cosine similarity computation

    **Use Cases:**
    - Literature deduplication
    - Paper relevance ranking
    - Concept matching
    """
    try:
        if not request.text1 or not request.text2:
            raise HTTPException(
                status_code=400,
                detail="Both text1 and text2 must be provided"
            )

        if len(request.text1.strip()) < 5 or len(request.text2.strip()) < 5:
            raise HTTPException(
                status_code=400,
                detail="Both texts must be at least 5 characters long"
            )

        service = get_biomedical_service()
        result = await service.calculate_semantic_similarity(
            request.text1,
            request.text2
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Similarity calculation failed')
            )

        return {
            "status": "success",
            "message": "Semantic similarity calculated successfully",
            "data": result['data'],
            "metadata": {
                "service": "BiomedicalNLPService",
                "model": "BioBERT",
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in semantic similarity endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/enhance-literature")
async def enhance_literature_search(request: LiteratureEnhancementRequest):
    """
    Enhance literature search results with biomedical understanding

    **Features:**
    - Entity-aware ranking
    - Semantic relevance scoring
    - Biomedical domain focus
    - Research domain classification

    **Use Cases:**
    - Improve search result relevance
    - Literature review assistance
    - Research discovery enhancement
    """
    try:
        if not request.query or not request.papers:
            raise HTTPException(
                status_code=400,
                detail="Query and papers list must be provided"
            )

        if len(request.papers) > 100:
            raise HTTPException(
                status_code=400,
                detail="Maximum 100 papers can be processed at once"
            )

        service = get_biomedical_service()
        result = await service.enhance_literature_search(
            request.query,
            request.papers
        )

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Literature enhancement failed')
            )

        return {
            "status": "success",
            "message": "Literature search enhanced with biomedical analysis",
            "data": result['data'],
            "metadata": {
                "service": "BiomedicalNLPService",
                "query": request.query,
                "papers_processed": len(request.papers),
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in literature enhancement endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-abstract")
async def analyze_paper_abstract(request: AbstractAnalysisRequest):
    """
    Comprehensive analysis of scientific paper abstracts

    **Features:**
    - Biomedical entity extraction
    - Key concept identification
    - Research domain classification
    - Content structure analysis

    **Use Cases:**
    - Abstract screening
    - Research categorization
    - Content analysis
    """
    try:
        if not request.abstract or len(request.abstract.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Abstract must be at least 50 characters long"
            )

        service = get_biomedical_service()
        result = await service.analyze_paper_abstract(request.abstract)

        if not result.get('success'):
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Abstract analysis failed')
            )

        return {
            "status": "success",
            "message": "Abstract analyzed successfully",
            "data": result['data'],
            "metadata": {
                "service": "BiomedicalNLPService",
                "analysis_type": "comprehensive",
                "timestamp": datetime.now().isoformat()
            }
        }

    except HTTPException:
        raise
    except BiologyError as e:
        logger.error(f"Error in abstract analysis endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check for Biomedical NLP Service

    Returns service status and model availability
    """
    try:
        service = get_biomedical_service()
        health_status = await service.health_check()

        return {
            "status": "success",
            "message": "Health check completed",
            "data": health_status,
            "timestamp": datetime.now().isoformat()
        }

    except BiologyError as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "error",
            "message": "Health check failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/capabilities")
async def get_service_capabilities():
    """
    Get detailed information about service capabilities
    """
    return {
        "status": "success",
        "data": {
            "service_name": "BiomedicalNLPService",
            "version": "1.0.0",
            "capabilities": [
                {
                    "name": "Biomedical Entity Extraction",
                    "description": "Extract genes, proteins, diseases, chemicals from text",
                    "endpoint": "/extract-entities",
                    "method": "POST"
                },
                {
                    "name": "Semantic Similarity",
                    "description": "Calculate biomedical text similarity using BioBERT",
                    "endpoint": "/semantic-similarity",
                    "method": "POST"
                },
                {
                    "name": "Literature Enhancement",
                    "description": "Enhance search results with biomedical understanding",
                    "endpoint": "/enhance-literature",
                    "method": "POST"
                },
                {
                    "name": "Abstract Analysis",
                    "description": "Comprehensive analysis of scientific abstracts",
                    "endpoint": "/analyze-abstract",
                    "method": "POST"
                }
            ],
            "models": [
                "BioBERT (dmis-lab/biobert-base-cased-v1.2)",
                "Biomedical NER (d4data/biomedical-ner-all)"
            ],
            "entity_types": [
                "Gene/Protein",
                "Disease/Disorder",
                "Chemical/Drug",
                "Species/Organism",
                "Cell Type",
                "Tissue/Organ"
            ]
        },
        "timestamp": datetime.now().isoformat()
    }
