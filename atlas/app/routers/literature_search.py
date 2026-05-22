"""
Router de Búsqueda de Literatura - AXIOM Meta 4.1
==============================================

Módulo especializado para búsqueda automatizada, análisis y síntesis de literatura
científica en el ecosistema AXIOM. Proporciona capacidades avanzadas de minería
literaria para descubrimiento científico, análisis de papers individuales y generación
automatizada de revisiones bibliográficas.

Capacidades Principales
----------------------
- **Búsqueda Multi-fuente**: Literatura científica desde Semantic Scholar, CrossRef, arXiv, PubMed
- **Cache Offline**: Gestión de cache local para rendimiento y confiabilidad mejorados
- **Análisis de Papers**: Extracción de insights clave y análisis individual de documentos
- **Descubrimiento Relacional**: Identificación de trabajos relacionados y análisis de redes de citas
- **Síntesis Automatizada**: Generación de revisiones bibliográficas comprehensivas
- **Ranking por Relevancia**: Mejora de búsqueda específica por dominio científico

Endpoints Disponibles
--------------------
**Búsqueda:**
- `POST /literature-search/search-literature` - Búsqueda multi-fuente con filtros
- `POST /literature-search/search-offline` - Búsqueda en cache offline local

**Cache:**
- `POST /literature-search/cache-upsert` - Insertar/actualizar papers en cache

**Análisis:**
- `POST /literature-search/analyze-paper` - Extraer insights de paper individual
- `POST /literature-search/get-related-papers` - Encontrar papers relacionados
- `POST /literature-search/extract-key-findings` - Extraer hallazgos clave de múltiples papers

**Síntesis:**
- `POST /literature-search/generate-literature-review` - Generar revisión bibliográfica

**Información:**
- `GET /literature-search/health` - Estado de salud del servicio
- `GET /literature-search/stats` - Estadísticas detalladas del servicio
- `GET /literature-search/domains` - Lista de dominios científicos soportados

Dependencias
-----------
- **LiteratureSearchService**: Servicio principal de búsqueda y análisis literario
- **APIs Externas**: Semantic Scholar, CrossRef, arXiv, PubMed
- **Cache Local**: Almacenamiento offline de papers para rendimiento mejorado
- **logging_config**: Configuración de logging del sistema

Uso y Ejemplos
--------------
**Búsqueda multi-fuente:**
```python
response = await client.post("/literature-search/search-literature", json={
    "query": "CRISPR gene editing applications",
    "domain": "molecular_biology",
    "max_results": 25,
    "sources": ["semantic_scholar", "pubmed", "arxiv"]
})
# Retorna resultados de múltiples fuentes con ranking por relevancia
```

**Análisis de paper individual:**
```python
response = await client.post("/literature-search/analyze-paper", json={
    "paper_id": "10.1038/nature12345",
    "doi": "10.1038/nature12345"
})
# Retorna insights clave, métodos, resultados y conclusiones extraídas
```

**Generación de revisión bibliográfica:**
```python
response = await client.post("/literature-search/generate-literature-review", json={
    "topic": "Neural networks for drug discovery",
    "domain": "drug_discovery",
    "max_papers": 30
})
# Retorna revisión bibliográfica completa con síntesis automática
```

**Búsqueda offline:**
```python
response = await client.post("/literature-search/search-offline", json={
    "query": "quantum algorithms optimization",
    "domain": "quantum_computing",
    "max_results": 15
})
# Busca solo en cache local para acceso rápido sin dependencias externas
```

Dominios Científicos Soportados
-------------------------------
- **materials_science**: Ciencia de materiales e ingeniería
- **drug_discovery**: Descubrimiento de fármacos y farmacología
- **energy_storage**: Almacenamiento de energía y tecnología de baterías
- **quantum_computing**: Computación cuántica y algoritmos

Fuentes de Datos
---------------
- **Semantic Scholar**: Base de datos académica con metadatos enriquecidos
- **CrossRef**: Registro DOI con metadatos de publicaciones
- **arXiv**: Preprints en física, matemáticas, ciencias de la computación
- **PubMed**: Base de datos biomédica del NIH

Notas de Seguridad
-----------------
- Validación estricta de consultas y parámetros de búsqueda
- Rate limiting aplicado globalmente en main.py para APIs externas
- Logging detallado de todas las operaciones de búsqueda y análisis
- Manejo seguro de excepciones sin exposición de credenciales de API
- Cache local protegido contra manipulación externa
- Validación de DOIs y IDs de papers antes del procesamiento

Consideraciones de Rendimiento
-----------------------------
- Cache offline para reducir dependencias de APIs externas
- Procesamiento asíncrono para búsquedas de gran escala
- Optimización de consultas con índices por dominio
- Límite configurable de resultados para controlar carga
- Reintentos automáticos para fallos temporales de API
- Monitoreo de uso de recursos en operaciones de síntesis complejas
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.services.literature_search_improved import LiteratureSearchService
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.literature_search_types import (
    SearchLiteratureResult,
    SearchOfflineResult,
    CacheUpsertResult,
    AnalyzePaperResult,
    GetRelatedPapersResult,
    ExtractKeyFindingsResult,
    GenerateLiteratureReviewResult,
    HealthCheckResult,
    GetStatsResult,
    GetSupportedDomainsResult,
)

router = APIRouter(tags=["Literature Search"])
literature_search_router = router

# Initialize service
literature_service = LiteratureSearchService()


class LiteratureSearchRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    max_results: Optional[int] = 20
    sources: Optional[List[str]] = None


class OfflineSearchRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    max_results: Optional[int] = 20


class CacheUpsertRequest(BaseModel):
    papers: List[Dict[str, Any]]


class PaperAnalysisRequest(BaseModel):
    paper_id: str
    doi: Optional[str] = None


class RelatedPapersRequest(BaseModel):
    paper_id: str
    max_results: Optional[int] = 10


class KeyFindingsRequest(BaseModel):
    paper_ids: List[str]


class LiteratureReviewRequest(BaseModel):
    topic: str
    domain: Optional[str] = None
    max_papers: Optional[int] = 20


@router.post("/search-literature")
async def search_literature(request: LiteratureSearchRequest) -> SearchLiteratureResult:
    """
    Search scientific literature across multiple sources

    - **query**: Search query for literature
    - **domain**: Scientific domain for enhanced search
    - **max_results**: Maximum number of results to return
    - **sources**: List of sources to search (semantic_scholar, crossref, arxiv)
    """
    try:
        result = await literature_service.process_request({
            "action": "search_literature",
            "query": request.query,
            "domain": request.domain,
            "max_results": request.max_results,
            "sources": request.sources or ["semantic_scholar", "crossref"]
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Literature search failed"))

        return result

    except BiologyError as e:
        logger.exception("❌ Error searching literature")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/search-offline")
async def search_offline(request: OfflineSearchRequest) -> SearchOfflineResult:
    """Search only in the local offline cache."""
    try:
        result = await literature_service.process_request({
            "action": "search_offline",
            "query": request.query,
            "domain": request.domain,
            "max_results": request.max_results,
        })
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Offline search failed"))
        return result
    except BiologyError as e:
        logger.exception("❌ Error in offline search")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/cache-upsert")
async def cache_upsert(request: CacheUpsertRequest) -> CacheUpsertResult:
    """Insert or update papers in the offline cache."""
    try:
        result = await literature_service.process_request({
            "action": "cache_upsert",
            "papers": request.papers,
        })
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Cache upsert failed"))
        return result
    except BiologyError as e:
        logger.exception("❌ Error in cache upsert")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/analyze-paper")
async def analyze_paper(request: PaperAnalysisRequest) -> AnalyzePaperResult:
    """
    Analyze a specific paper for key insights

    - **paper_id**: ID of the paper to analyze
    - **doi**: DOI of the paper (alternative to paper_id)
    """
    try:
        result = await literature_service.process_request({
            "action": "analyze_paper",
            "paper_id": request.paper_id,
            "doi": request.doi
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Paper analysis failed"))

        return result

    except BiologyError as e:
        logger.exception("❌ Error analyzing paper")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/get-related-papers")
async def get_related_papers(request: RelatedPapersRequest) -> GetRelatedPapersResult:
    """
    Get papers related to a given paper

    - **paper_id**: ID of the paper to find related papers for
    - **max_results**: Maximum number of related papers to return
    """
    try:
        result = await literature_service.process_request({
            "action": "get_related_papers",
            "paper_id": request.paper_id,
            "max_results": request.max_results
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Related papers search failed"))

        return result

    except BiologyError as e:
        logger.exception("❌ Error getting related papers")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/extract-key-findings")
async def extract_key_findings(request: KeyFindingsRequest) -> ExtractKeyFindingsResult:
    """
    Extract key findings from a set of papers

    - **paper_ids**: List of paper IDs to analyze
    """
    try:
        result = await literature_service.process_request({
            "action": "extract_key_findings",
            "paper_ids": request.paper_ids
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Key findings extraction failed"))

        return result

    except BiologyError as e:
        logger.exception("❌ Error extracting key findings")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post("/generate-literature-review")
async def generate_literature_review(request: LiteratureReviewRequest) -> GenerateLiteratureReviewResult:
    """
    Generate a comprehensive literature review

    - **topic**: Topic for the literature review
    - **domain**: Scientific domain
    - **max_papers**: Maximum number of papers to analyze
    """
    try:
        result = await literature_service.process_request({
            "action": "generate_literature_review",
            "topic": request.topic,
            "domain": request.domain,
            "max_papers": request.max_papers
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Literature review generation failed"))

        return result

    except BiologyError as e:
        logger.exception("❌ Error generating literature review")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/health")
async def health_check() -> HealthCheckResult:
    """Health check for the Literature Search service"""
    return {
        "service": "LiteratureSearchService",
        "status": "healthy",
        "version": "2.0",
        "supported_sources": [
            "semantic_scholar",
            "crossref",
            "arxiv",
            "pubmed"
        ],
        "supported_domains": [
            "materials_science",
            "drug_discovery",
            "energy_storage",
            "quantum_computing"
        ]
    }


@router.get("/stats")
async def get_stats() -> GetStatsResult:
    """Get statistics about the Literature Search service"""
    try:
        return {
            "service": "LiteratureSearchService",
            "status": "operational",
            "capabilities": [
                "Multi-source literature search",
                "Paper analysis and insights",
                "Related paper discovery",
                "Key findings extraction",
                "Automated literature review generation"
            ],
            "supported_domains": [
                "materials_science",
                "drug_discovery",
                "energy_storage",
                "quantum_computing"
            ],
            "api_endpoints": {
                "semantic_scholar": "https://api.semanticscholar.org",
                "crossref": "https://api.crossref.org",
                "arxiv": "http://export.arxiv.org/api"
            },
            "features": [
                "Relevance ranking",
                "Citation analysis",
                "Domain-specific search enhancement",
                "Automated synthesis"
            ]
        }

    except BiologyError as e:
        logger.exception("❌ Error getting stats")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get("/domains")
async def get_supported_domains() -> GetSupportedDomainsResult:
    """Get list of supported scientific domains"""
    return {
        "domains": [
            {
                "name": "materials_science",
                "description": "Materials science and engineering",
                "keywords": ["materials", "nanomaterials", "composites", "polymers"],
                "journals": ["Nature Materials", "Advanced Materials"]
            },
            {
                "name": "drug_discovery",
                "description": "Drug discovery and pharmacology",
                "keywords": ["drug discovery", "pharmacology", "molecular docking"],
                "journals": ["Journal of Medicinal Chemistry", "Nature Chemical Biology"]
            },
            {
                "name": "energy_storage",
                "description": "Energy storage and battery technology",
                "keywords": ["battery", "lithium-ion", "supercapacitor"],
                "journals": ["Nature Energy", "Advanced Energy Materials"]
            },
            {
                "name": "quantum_computing",
                "description": "Quantum computing and algorithms",
                "keywords": ["quantum computing", "qubit", "quantum algorithm"],
                "journals": ["Nature Physics", "Physical Review Letters"]
            }
        ]
    }
