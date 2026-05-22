"""
Router de Síntesis de Evidencia - Análisis Avanzado de Evidencia Científica

Módulo FastAPI para síntesis avanzada de evidencia científica y análisis de investigación.
Proporciona endpoints REST API para integrar múltiples fuentes de evidencia, resolver conflictos
y generar insights coherentes a través de análisis automatizado de literatura científica.

Capacidades principales:
- Síntesis completa de evidencia: clustering de fuentes relacionadas y análisis de consenso
- Análisis de conflictos: identificación y resolución de contradicciones en evidencia
- Conexiones entre dominios: identificación de vínculos científicos interdisciplinarios
- Evaluación metodológica: análisis de calidad y fiabilidad de evidencia
- Síntesis rápida: procesamiento simplificado para casos de uso básicos
- Caché inteligente: optimización de rendimiento con almacenamiento en caché

Catálogo de Endpoints:
- POST /evidence-synthesis/synthesize: Síntesis completa de múltiples fuentes de evidencia
- POST /evidence-synthesis/quick-synthesis: Síntesis rápida con entrada simplificada
- GET /evidence-synthesis/supported-types: Tipos de evidencia y dominios soportados
- GET /evidence-synthesis/synthesis-examples: Ejemplos de solicitudes de síntesis
- GET /evidence-synthesis/health: Estado de salud del servicio de síntesis
- GET /evidence-synthesis/cache-status: Estado y estadísticas del caché

Dependencias:
- AdvancedEvidenceSynthesisService: Servicio central de síntesis de evidencia
- EvidenceSource/EvidenceType/ConfidenceLevel: Modelos de datos de evidencia
- ConflictResolution: Estrategias de resolución de conflictos
- Pydantic BaseModel: Modelos de validación de API
- FastAPI BackgroundTasks: Procesamiento asíncrono de tareas

Uso del Servicio:
    El router procesa múltiples fuentes de evidencia científica para generar
    síntesis coherentes. Soporta diferentes tipos de evidencia (ensayos clínicos,
    revisiones teóricas, estudios experimentales) con evaluación automática de
    calidad y fiabilidad. Incluye resolución inteligente de conflictos y
    identificación de conexiones interdisciplinarias.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.services.evidence_synthesis_service import (
from app.exceptions.domain.biology import BiologyError
    AdvancedEvidenceSynthesisService,
    EvidenceSource,
    EvidenceType,
    ConfidenceLevel,
    ConflictResolution
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize service
evidence_synthesis_service = AdvancedEvidenceSynthesisService()

# Create router
router = APIRouter(
    prefix="/evidence-synthesis",
    tags=["Evidence Synthesis"],
    responses={404: {"description": "Not found"}}
)

# Pydantic models for API
class EvidenceSourceModel(BaseModel):
    """Model for evidence source input"""
    id: Optional[str] = None
    title: str = Field(..., description="Title of the evidence")
    content: str = Field(..., description="Main content/abstract")
    evidence_type: str = Field(..., description="Type of evidence")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    reliability_score: float = Field(..., ge=0.0, le=1.0, description="Reliability score")
    publication_date: str = Field(..., description="Publication date (ISO format)")
    domain: str = Field(..., description="Scientific domain")
    authors: List[str] = Field(default_factory=list, description="List of authors")
    doi: Optional[str] = Field(None, description="DOI if available")
    citations: int = Field(default=0, description="Number of citations")
    peer_reviewed: bool = Field(default=True, description="Is peer reviewed")
    methodology_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Methodology quality score")
    sample_size: Optional[int] = Field(None, description="Sample size if applicable")
    statistical_power: Optional[float] = Field(None, ge=0.0, le=1.0, description="Statistical power")
    tags: List[str] = Field(default_factory=list, description="Tags")

class SynthesisRequest(BaseModel):
    """Model for evidence synthesis request"""
    query: str = Field(..., description="Research question")
    evidence_sources: List[EvidenceSourceModel] = Field(..., description="List of evidence sources")
    synthesis_parameters: Dict[str, Any] = Field(default_factory=dict, description="Synthesis parameters")
    
class QuickSynthesisRequest(BaseModel):
    """Model for quick evidence synthesis request"""
    query: str = Field(..., description="Research question")
    evidence_titles: List[str] = Field(..., description="List of evidence titles/abstracts")
    domains: List[str] = Field(default_factory=list, description="Domains for each evidence")
    confidence_scores: List[float] = Field(default_factory=list, description="Confidence scores")
    query: str = Field(..., description="Research question or topic")
    evidence_sources: List[EvidenceSourceModel] = Field(..., description="List of evidence sources")
    synthesis_parameters: Optional[Dict[str, Any]] = Field(None, description="Optional synthesis parameters")
    
class SynthesisParametersModel(BaseModel):
    """Model for synthesis parameters"""
    min_confidence: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="Minimum confidence threshold")
    cluster_threshold: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Clustering similarity threshold")
    max_clusters: Optional[int] = Field(10, ge=1, le=50, description="Maximum number of clusters")
    conflict_resolution: Optional[str] = Field("weighted_average", description="Conflict resolution strategy")

# API Endpoints
@router.post("/synthesize")
async def synthesize_evidence(
    request: SynthesisRequest,
    background_tasks: BackgroundTasks
):
    """
    Synthesize multiple evidence sources into coherent insights
    
    This endpoint performs advanced evidence synthesis by:
    - Clustering related evidence sources
    - Analyzing consensus and conflicts
    - Identifying cross-domain connections  
    - Resolving evidence conflicts
    - Generating main conclusions and limitations
    """
    try:
        # Convert Pydantic models to service objects
        evidence_sources = []
        for source_model in request.evidence_sources:
            
            # Parse publication date
            try:
                pub_date = datetime.fromisoformat(source_model.publication_date.replace('Z', '+00:00'))
            except ValueError:
                pub_date = datetime.now()
            
            # Convert evidence type
            try:
                evidence_type = EvidenceType(source_model.evidence_type.lower())
            except ValueError:
                evidence_type = EvidenceType.LITERATURE_REVIEW  # Default
            
            evidence_source = EvidenceSource(
                id=source_model.id or f"ev_{len(evidence_sources)}",
                title=source_model.title,
                content=source_model.content,
                evidence_type=evidence_type,
                confidence_score=source_model.confidence_score,
                reliability_score=source_model.reliability_score,
                publication_date=pub_date,
                domain=source_model.domain,
                authors=source_model.authors,
                doi=source_model.doi,
                citations=source_model.citations,
                peer_reviewed=source_model.peer_reviewed,
                methodology_score=source_model.methodology_score,
                sample_size=source_model.sample_size,
                statistical_power=source_model.statistical_power,
                tags=source_model.tags
            )
            evidence_sources.append(evidence_source)
        
        logger.info(f"🔬 Starting evidence synthesis for {len(evidence_sources)} sources")
        
        # Perform synthesis
        result = await evidence_synthesis_service.synthesize_evidence(
            evidence_sources=evidence_sources,
            query=request.query,
            synthesis_parameters=request.synthesis_parameters
        )
        
        # Convert result to JSON-serializable format
        synthesis_result = {
            "synthesis_id": result.id,
            "query": result.query,
            "timestamp": result.timestamp.isoformat(),
            "overall_confidence": result.overall_confidence,
            "main_conclusions": result.main_conclusions,
            "limitations": result.limitations,
            "future_research_directions": result.future_research_directions,
            "evidence_gaps": result.evidence_gaps,
            "cross_domain_connections": result.cross_domain_connections,
            "conflict_resolutions": result.conflict_resolutions,
            "methodology_assessment": result.methodology_assessment,
            "evidence_clusters": [
                {
                    "id": cluster.id,
                    "topic": cluster.topic,
                    "evidence_count": len(cluster.evidence_sources),
                    "consensus_level": cluster.consensus_level,
                    "conflict_level": cluster.conflict_level,
                    "main_findings": cluster.main_findings,
                    "conflicting_points": cluster.conflicting_points,
                    "confidence_distribution": cluster.confidence_distribution
                }
                for cluster in result.evidence_clusters
            ],
            "summary": {
                "total_evidence_sources": len(evidence_sources),
                "total_clusters": len(result.evidence_clusters),
                "high_confidence_clusters": len([
                    c for c in result.evidence_clusters if c.consensus_level > 0.7
                ]),
                "conflicted_clusters": len([
                    c for c in result.evidence_clusters if c.conflict_level > 0.3
                ]),
                "cross_domain_connections": len(result.cross_domain_connections),
                "resolved_conflicts": len(result.conflict_resolutions)
            }
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Evidence synthesis completed successfully",
                "data": synthesis_result
            }
        )
        
    except BiologyError as e:
        logger.error(f"Evidence synthesis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Evidence synthesis failed: {str(e)}"
        )

@router.post("/quick-synthesis")
async def quick_evidence_synthesis(request: QuickSynthesisRequest):
    """
    Quick evidence synthesis for simple use cases
    
    Simplified endpoint for rapid evidence synthesis with minimal input.
    """
    try:
        # Create evidence sources from simple inputs
        evidence_sources = []
        
        for i, title in enumerate(request.evidence_titles):
            domain = request.domains[i] if i < len(request.domains) else "general"
            confidence = request.confidence_scores[i] if i < len(request.confidence_scores) else 0.7
            
            evidence_source = EvidenceSource(
                id=f"quick_ev_{i}",
                title=title,
                content=title,  # Use title as content for quick synthesis
                evidence_type=EvidenceType.LITERATURE_REVIEW,
                confidence_score=confidence,
                reliability_score=0.7,  # Default reliability
                publication_date=datetime.now(),
                domain=domain,
                authors=["Unknown"],
                tags=[]
            )
            evidence_sources.append(evidence_source)
        
        # Perform quick synthesis
        result = await evidence_synthesis_service.synthesize_evidence(
            evidence_sources=evidence_sources,
            query=request.query,
            synthesis_parameters={
                "min_confidence": 0.3,
                "cluster_threshold": 0.5,  # Lower threshold for quick synthesis
                "max_clusters": 5
            }
        )
        
        # Return simplified result
        quick_result = {
            "query": request.query,
            "overall_confidence": result.overall_confidence,
            "main_conclusions": result.main_conclusions[:3],  # Top 3
            "evidence_clusters": len(result.evidence_clusters),
            "cross_domain_connections": len(result.cross_domain_connections),
            "key_insights": [
                f"Analyzed {len(evidence_sources)} evidence sources",
                f"Found {len(result.evidence_clusters)} main topic areas",
                f"Overall confidence: {result.overall_confidence:.2f}"
            ],
            "synthesis_id": result.id
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Quick evidence synthesis completed",
                "data": quick_result
            }
        )
        
    except BiologyError as e:
        logger.error(f"Quick evidence synthesis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Quick synthesis failed: {str(e)}"
        )

@router.get("/supported-types")
async def get_supported_evidence_types():
    """Get list of supported evidence types and domains"""
    try:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": {
                    "evidence_types": [et.value for et in EvidenceType],
                    "confidence_levels": [cl.value for cl in ConfidenceLevel],
                    "conflict_resolution_methods": [cr.value for cr in ConflictResolution],
                    "supported_domains": [
                        "medicine", "physics", "biology", "chemistry", 
                        "materials_science", "neuroscience", "computer_science",
                        "engineering", "psychology", "environmental_science"
                    ]
                }
            }
        )
    except BiologyError as e:
        logger.error(f"Failed to get supported types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/synthesis-examples")
async def get_synthesis_examples():
    """Get example synthesis requests for testing"""
    try:
        examples = {
            "biomedical_research": {
                "query": "Effectiveness of CRISPR gene therapy for genetic diseases",
                "evidence_sources": [
                    {
                        "title": "CRISPR-Cas9 clinical trials for sickle cell disease",
                        "content": "Phase I clinical trial showing promising results...",
                        "evidence_type": "clinical_trial",
                        "confidence_score": 0.85,
                        "reliability_score": 0.90,
                        "publication_date": "2023-06-15T00:00:00Z",
                        "domain": "medicine",
                        "authors": ["Smith J", "Johnson A"],
                        "peer_reviewed": True
                    },
                    {
                        "title": "Theoretical framework for CRISPR delivery systems",
                        "content": "Comprehensive analysis of delivery mechanisms...",
                        "evidence_type": "theoretical",
                        "confidence_score": 0.75,
                        "reliability_score": 0.80,
                        "publication_date": "2023-08-20T00:00:00Z",
                        "domain": "biology",
                        "authors": ["Brown M", "Davis K"],
                        "peer_reviewed": True
                    }
                ]
            },
            "materials_science": {
                "query": "Properties and applications of graphene nanocomposites",
                "evidence_sources": [
                    {
                        "title": "Mechanical properties of graphene-polymer composites",
                        "content": "Experimental study of tensile strength...",
                        "evidence_type": "experimental",
                        "confidence_score": 0.90,
                        "reliability_score": 0.85,
                        "publication_date": "2023-05-10T00:00:00Z",
                        "domain": "materials_science",
                        "authors": ["Wilson R", "Taylor S"],
                        "peer_reviewed": True
                    }
                ]
            }
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Example synthesis requests",
                "data": examples
            }
        )
        
    except BiologyError as e:
        logger.error(f"Failed to get examples: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_service_health():
    """Get health status of the evidence synthesis service"""
    try:
        health_status = await evidence_synthesis_service.get_synthesis_health_status()
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Evidence synthesis service is healthy",
                "data": health_status
            }
        )
        
    except BiologyError as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache-status")
async def get_cache_status():
    """Get synthesis cache status and statistics"""
    try:
        cache_info = {
            "current_cache_size": len(evidence_synthesis_service.synthesis_cache),
            "max_cache_size": evidence_synthesis_service.cache_size,
            "cache_utilization": len(evidence_synthesis_service.synthesis_cache) / evidence_synthesis_service.cache_size,
            "cached_syntheses": list(evidence_synthesis_service.synthesis_cache.keys())[:10]  # First 10
        }
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Cache status retrieved successfully",
                "data": cache_info
            }
        )
        
    except BiologyError as e:
        logger.error(f"Failed to get cache status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add startup event
@router.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Evidence Synthesis Service started successfully")

# Add shutdown event  
@router.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Evidence Synthesis Service shutting down")
