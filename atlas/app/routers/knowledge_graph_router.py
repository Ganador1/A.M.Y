"""
Router del Grafo de Conocimiento - AXIOM Meta 4.1
===============================================

Módulo especializado para gestión integral del grafo de conocimiento científico
en el ecosistema AXIOM. Proporciona capacidades avanzadas de representación,
búsqueda y análisis de conocimiento estructurado mediante grafos de nodos
y relaciones con soporte para inferencia, detección de contradicciones y
sugerencias experimentales.

Capacidades Principales
----------------------
- **Gestión de Nodos**: CRUD completo de nodos de conocimiento (conceptos, hipótesis, métodos)
- **Relaciones Estructuradas**: Creación y gestión de relaciones dirigidas con pesos
- **Búsqueda Avanzada**: Búsqueda semántica con filtros por dominio, tipo y confianza
- **Análisis de Subgrafos**: Extracción y análisis de subgrafos con control de profundidad
- **Detección de Contradicciones**: Identificación automática de evidencia contradictoria
- **Sugerencias Experimentales**: Recomendaciones de experimentos basadas en gaps de conocimiento
- **Condiciones Experimentales**: Captura y búsqueda de setups experimentales
- **Estadísticas del Grafo**: Métricas comprehensivas de estructura y calidad

Endpoints Disponibles
--------------------
**Nodos de Conocimiento:**
- `POST /knowledge-graph/nodes` - Crear nuevo nodo de conocimiento
- `GET /knowledge-graph/nodes/{id}` - Obtener detalles de nodo específico
- `POST /knowledge-graph/nodes/search` - Búsqueda avanzada de nodos

**Relaciones:**
- `POST /knowledge-graph/relations` - Crear relación entre nodos

**Análisis de Grafos:**
- `POST /knowledge-graph/subgraph` - Extraer subgrafo desde nodo raíz
- `GET /knowledge-graph/statistics` - Estadísticas del grafo completo
- `POST /knowledge-graph/detect-contradictions` - Detectar contradicciones
- `POST /knowledge-graph/suggest-experiments` - Sugerir experimentos

**Condiciones Experimentales:**
- `POST /knowledge-graph/capture-conditions` - Capturar condiciones experimentales
- `POST /knowledge-graph/find-similar-experiments` - Encontrar experimentos similares

**Utilidades:**
- `GET /knowledge-graph/health` - Estado de salud del servicio
- `GET /knowledge-graph/schema` - Información del esquema del grafo

Dependencias
-----------
- **KnowledgeGraphService**: Servicio principal de gestión del grafo de conocimiento
- **fastapi**: Framework web para APIs REST
- **pydantic**: Validación de datos y modelos de request/response

Uso y Ejemplos
--------------
**Crear nodo de conocimiento:**
```python
response = await client.post("/knowledge-graph/nodes", json={
    "name": "CRISPR-Cas9",
    "type": "method",
    "domain": "molecular_biology",
    "properties": {
        "description": "Sistema de edición genética",
        "discovery_year": 2012,
        "nobel_prize": 2020
    },
    "confidence_score": 0.95,
    "source_papers": ["doi:10.1126/science.1231143"],
    "created_by": "researcher_001"
})
```

**Buscar nodos por dominio:**
```python
response = await client.post("/knowledge-graph/nodes/search", json={
    "domain": "neuroscience",
    "type": "hypothesis",
    "min_confidence": 0.8,
    "limit": 20
})
```

**Crear relación entre nodos:**
```python
response = await client.post("/knowledge-graph/relations", json={
    "subject_id": 123,
    "object_id": 456,
    "predicate": "supports",
    "strength": 0.85,
    "context": {"experiment_type": "in_vitro"},
    "evidence_papers": ["doi:10.1038/nature12345"],
    "created_by": "researcher_001"
})
```

**Extraer subgrafo:**
```python
response = await client.post("/knowledge-graph/subgraph", json={
    "root_node_id": 123,
    "max_depth": 3,
    "include_relation_types": ["supports", "contradicts"],
    "min_strength": 0.5
})
```

**Detectar contradicciones:**
```python
response = await client.post("/knowledge-graph/detect-contradictions", json={
    "node_id": 123,
    "max_depth": 2
})
```

**Capturar condiciones experimentales:**
```python
response = await client.post("/knowledge-graph/capture-conditions", json={
    "experiment_id": "exp_2025_001",
    "conditions": {
        "temperature": "37°C",
        "ph": 7.4,
        "concentration": "10μM"
    },
    "instrument": "PCR_machine_v2",
    "protocol": "qPCR_standard",
    "domain": "molecular_biology",
    "purpose": "gene_expression_analysis",
    "hypothesis_tested": "Gene X is upregulated in condition Y"
})
```

Tipos de Nodos Soportados
------------------------
- **concept**: Conceptos científicos fundamentales
- **hypothesis**: Hipótesis científicas
- **method**: Métodos y técnicas experimentales
- **result**: Resultados experimentales
- **theory**: Teorías científicas
- **evidence**: Evidencia empírica
- **contradiction**: Nodos de contradicción detectados

Tipos de Relaciones Soportados
-----------------------------
- **supports**: Evidencia que apoya una hipótesis/concepto
- **contradicts**: Evidencia que contradice una hipótesis/concepto
- **related_to**: Relación general entre conceptos
- **part_of**: Relación de composición (parte-todo)
- **causes**: Relación causal
- **precedes**: Relación temporal/secuencial
- **similar_to**: Similitud semántica

Notas de Seguridad
-----------------
- Validación estricta de tipos de nodos y relaciones permitidos
- Límites de profundidad en análisis de subgrafos para prevenir sobrecarga
- Control de rate limiting en operaciones de búsqueda masiva
- Logging detallado de operaciones de creación y modificación
- Manejo seguro de excepciones sin exposición de estructura interna
- Validación de confianza y fuerza de relaciones dentro de rangos permitidos

Consideraciones de Rendimiento
-----------------------------
- Indexación optimizada para búsquedas por dominio y tipo
- Caching de estadísticas del grafo para consultas frecuentes
- Procesamiento asíncrono para operaciones de análisis complejas
- Límites configurables en resultados de búsqueda y profundidad de subgrafos
- Optimización de consultas de detección de contradicciones
- Monitoreo de uso de memoria en operaciones de subgrafo grandes
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel, Field

from ..services.knowledge_graph_service import KnowledgeGraphService
from app.exceptions.domain.biology import BiologyError

# Initialize router and service
router = APIRouter(prefix="/knowledge-graph", tags=["Knowledge Graph"])
kg_service = KnowledgeGraphService()


# === PYDANTIC MODELS ===

class NodeCreateRequest(BaseModel):
    """Request model for creating a knowledge node"""
    name: str = Field(..., min_length=1, max_length=200, description="Name of the knowledge node")
    type: str = Field(..., description="Type of the node (concept, hypothesis, method, etc.)")
    domain: str = Field(default="general", description="Scientific domain")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    confidence_score: float = Field(default=0.8, ge=0.0, le=1.0, description="Confidence score")
    source_papers: List[str] = Field(default_factory=list, description="Source paper IDs/URLs")
    created_by: Optional[str] = Field(None, description="Creator identifier")


class RelationCreateRequest(BaseModel):
    """Request model for creating a knowledge relation"""
    subject_id: int = Field(..., description="ID of the subject node")
    object_id: int = Field(..., description="ID of the object node")
    predicate: str = Field(..., description="Relation type/predicate")
    strength: float = Field(default=1.0, ge=0.0, le=1.0, description="Relation strength")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    evidence_papers: List[str] = Field(default_factory=list, description="Evidence paper IDs/URLs")
    created_by: Optional[str] = Field(None, description="Creator identifier")


class NodeSearchRequest(BaseModel):
    """Request model for searching knowledge nodes"""
    query: Optional[str] = Field(None, description="Search query")
    domain: Optional[str] = Field(None, description="Filter by domain")
    type: Optional[str] = Field(None, description="Filter by node type")
    min_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum confidence score")
    validated_only: bool = Field(default=False, description="Only validated nodes")
    limit: int = Field(default=50, ge=1, le=100, description="Results limit")
    offset: int = Field(default=0, ge=0, description="Results offset")


class SubgraphRequest(BaseModel):
    """Request model for subgraph extraction"""
    root_node_id: int = Field(..., description="ID of the root node")
    max_depth: int = Field(default=2, ge=1, le=5, description="Maximum depth")
    include_relation_types: Optional[List[str]] = Field(None, description="Relation types to include")
    min_strength: float = Field(default=0.1, ge=0.0, le=1.0, description="Minimum relation strength")


class ContradictionDetectionRequest(BaseModel):
    """Request model for contradiction detection"""
    node_id: int = Field(..., description="ID of the node to analyze for contradictions")
    max_depth: int = Field(default=2, ge=1, le=5, description="Maximum analysis depth")

class ExperimentSuggestionRequest(BaseModel):
    """Request model for experiment suggestions"""
    node_id: int = Field(..., description="ID of the node to suggest experiments for")
    max_suggestions: int = Field(default=5, ge=1, le=20, description="Maximum number of suggestions")

class ExperimentalConditionsRequest(BaseModel):
    """Request model for capturing experimental conditions"""
    experiment_id: Optional[str] = Field(None, description="Unique experiment identifier")
    conditions: Dict[str, Any] = Field(..., description="Dictionary of experimental conditions")
    instrument: Optional[str] = Field(None, description="Instrument used")
    protocol: Optional[str] = Field(None, description="Experimental protocol")
    domain: str = Field("general", description="Scientific domain")
    purpose: Optional[str] = Field(None, description="Experiment purpose")
    hypothesis_tested: Optional[str] = Field(None, description="Hypothesis being tested")

class SimilarExperimentsRequest(BaseModel):
    """Request model for finding similar experiments"""
    conditions: Dict[str, Any] = Field(..., description="Conditions to search for")
    domain: str = Field("general", description="Scientific domain to search in")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results")


# === NODE ENDPOINTS ===

@router.post("/nodes", summary="Create Knowledge Node")
async def create_node(request: NodeCreateRequest):
    """
    Create a new knowledge node in the graph.
    
    Creates a new node with the specified properties and validates
    the node type against allowed types.
    """
    try:
        result = await kg_service.create_knowledge_node({
            "action": "create_node",
            "name": request.name,
            "type": request.type,
            "domain": request.domain,
            "properties": request.properties,
            "confidence_score": request.confidence_score,
            "source_papers": request.source_papers,
            "created_by": request.created_by
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create node"))
        
        return result
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@router.get("/nodes/{node_id}", summary="Get Knowledge Node")
async def get_node(
    node_id: int = Path(..., description="ID of the knowledge node"),
    include_relations: bool = Query(True, description="Include node relations")
):
    """
    Get detailed information about a specific knowledge node.
    
    Returns the node details and optionally its incoming and outgoing relations.
    """
    try:
        result = await kg_service.get_knowledge_node({
            "action": "get_node",
            "node_id": node_id,
            "include_relations": include_relations
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Node not found"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@router.post("/nodes/search", summary="Search Knowledge Nodes")
async def search_nodes(request: NodeSearchRequest):
    """
    Search knowledge nodes with advanced filtering options.
    
    Supports text search, domain filtering, type filtering, confidence thresholds,
    and validation status filtering with pagination.
    """
    try:
        result = await kg_service.search_knowledge_nodes({
            "action": "search_nodes",
            "query": request.query,
            "domain": request.domain,
            "type": request.type,
            "min_confidence": request.min_confidence,
            "validated_only": request.validated_only,
            "limit": request.limit,
            "offset": request.offset
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Search failed"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


# === RELATION ENDPOINTS ===

@router.post("/relations", summary="Create Knowledge Relation")
async def create_relation(request: RelationCreateRequest):
    """
    Create a new relation between two knowledge nodes.
    
    Creates a directed relation with specified predicate and strength.
    Validates that both nodes exist and the predicate type is valid.
    """
    try:
        result = await kg_service.create_knowledge_relation({
            "action": "create_relation",
            "subject_id": request.subject_id,
            "object_id": request.object_id,
            "predicate": request.predicate,
            "strength": request.strength,
            "context": request.context,
            "evidence_papers": request.evidence_papers,
            "created_by": request.created_by
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to create relation"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


# === GRAPH ANALYSIS ENDPOINTS ===

@router.post("/subgraph", summary="Extract Subgraph")
async def get_subgraph(request: SubgraphRequest):
    """
    Extract a subgraph starting from a root node.
    
    Performs breadth-first traversal from the root node up to the specified
    maximum depth, including only relations that match the filtering criteria.
    """
    try:
        result = await kg_service.get_subgraph({
            "action": "get_subgraph",
            "root_node_id": request.root_node_id,
            "max_depth": request.max_depth,
            "include_relation_types": request.include_relation_types,
            "min_strength": request.min_strength
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to extract subgraph"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@router.get("/statistics", summary="Get Graph Statistics")
async def get_statistics():
    """
    Get comprehensive statistics about the knowledge graph.
    
    Returns basic metrics like node count, relation count, validation statistics,
    confidence score distributions, and graph density.
    """
    try:
        result = await kg_service.get_graph_statistics({
            "action": "get_statistics"
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to get statistics"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


@router.post("/detect-contradictions", summary="Detect Knowledge Contradictions")
async def detect_contradictions(request: ContradictionDetectionRequest):
    """
    Detect contradictory evidence for a specific knowledge node.
    
    Analyzes the knowledge graph to find nodes that have both supporting
    and contradicting evidence, indicating potential knowledge gaps or
    areas requiring further investigation.
    """
    try:
        result = await kg_service.detect_contradictions(request.node_id, request.max_depth)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Contradiction detection failed"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@router.post("/suggest-experiments", summary="Suggest Experiments for Knowledge Gaps")
async def suggest_experiments(request: ExperimentSuggestionRequest):
    """
    Suggest experiments to resolve knowledge gaps or validate hypotheses.
    
    Based on the node type and domain, provides specific experiment
    recommendations using available scientific tools and services.
    """
    try:
        result = await kg_service.suggest_experiments(request.node_id, request.max_suggestions)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Experiment suggestion failed"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@router.post("/capture-conditions", summary="Capture Experimental Conditions")
async def capture_experimental_conditions(request: ExperimentalConditionsRequest):
    """
    Capture experimental conditions as specialized knowledge graph nodes.
    
    Creates detailed nodes for parameters, instruments, and experimental
    setups to enable reproducibility analysis and condition-based searching.
    """
    try:
        result = await kg_service.capture_experimental_conditions({
            "experiment_id": request.experiment_id,
            "conditions": request.conditions,
            "instrument": request.instrument,
            "protocol": request.protocol,
            "domain": request.domain,
            "purpose": request.purpose,
            "hypothesis_tested": request.hypothesis_tested
        })
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to capture conditions"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e

@router.post("/find-similar-experiments", summary="Find Similar Experiments by Conditions")
async def find_similar_experiments(request: SimilarExperimentsRequest):
    """
    Find experiments with similar conditions in the knowledge graph.
    
    Searches for experiments that used similar parameters, instruments,
    or conditions to enable cross-experiment analysis and reproducibility.
    """
    try:
        result = await kg_service.find_similar_experiments(
            request.conditions, request.domain, request.max_results
        )
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to find similar experiments"))
        
        return result
    except HTTPException:
        raise
    except BiologyError as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") from e


# === UTILITY ENDPOINTS ===

@router.get("/health", summary="Knowledge Graph Health Check")
async def health_check():
    """
    Health check endpoint for the knowledge graph service.
    
    Returns service status and basic configuration information.
    """
    return {
        "service": "KnowledgeGraphService",
        "status": "healthy",
        "version": kg_service.version,
        "description": kg_service.description,
        "max_search_results": kg_service.max_search_results,
        "max_subgraph_depth": kg_service.max_subgraph_depth,
        "valid_node_types": kg_service.valid_node_types,
        "valid_relation_types": kg_service.valid_relation_types
    }


@router.get("/schema", summary="Get Graph Schema Information")
async def get_schema():
    """
    Get schema information about valid node types and relation types.
    
    Useful for client applications to understand the available
    node and relation types for validation.
    """
    return {
        "node_types": kg_service.valid_node_types,
        "relation_types": kg_service.valid_relation_types,
        "constraints": {
            "node_name_max_length": 200,
            "confidence_score_range": [0.0, 1.0],
            "relation_strength_range": [0.0, 1.0],
            "max_search_results": kg_service.max_search_results,
            "max_subgraph_depth": kg_service.max_subgraph_depth
        }
    }
