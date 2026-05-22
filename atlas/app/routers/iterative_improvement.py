"""
Router de Mejora Iterativa - AXIOM Meta 4.1
==========================================

Módulo especializado para el sistema de aprendizaje continuo y optimización
adaptativa en el ecosistema AXIOM. Implementa pipelines de mejora iterativa
que optimizan la calidad del análisis científico mediante bucles de retroalimentación
y optimización adaptativa basada en datos.

Capacidades Principales
----------------------
- **Registro de Retroalimentación**: Captura feedback de resultados de análisis
- **Métricas de Rendimiento**: Análisis de tendencias y estadísticas de desempeño
- **Recomendaciones de Optimización**: Sugerencias basadas en datos históricos
- **Simulación de Impacto**: Predicción de mejoras con cambios de parámetros
- **Insights de Aprendizaje**: Análisis de patrones de aprendizaje del sistema
- **Monitoreo de Salud**: Estado operacional del pipeline de mejora
- **Estado del Pipeline**: Información detallada del proceso de optimización

Endpoints Disponibles
--------------------
**Retroalimentación:**
- `POST /api/iterative-improvement/feedback` - Registrar feedback de análisis

**Métricas y Monitoreo:**
- `GET /api/iterative-improvement/metrics` - Obtener métricas de rendimiento
- `GET /api/iterative-improvement/health` - Estado de salud del servicio
- `GET /api/iterative-improvement/status` - Estado detallado del pipeline

**Optimización:**
- `GET /api/iterative-improvement/recommendations/{type}` - Recomendaciones de optimización
- `POST /api/iterative-improvement/simulate` - Simular impacto de mejoras

**Insights:**
- `GET /api/iterative-improvement/insights` - Insights de aprendizaje del sistema

Dependencias
-----------
- **iterative_improvement_service**: Servicio principal de mejora iterativa
- **IterativeImprovementPipeline**: Pipeline de optimización adaptativa
- **AnalysisType**: Enumeración de tipos de análisis soportados
- **FeedbackType**: Enumeración de tipos de feedback
- **logging_config**: Configuración de logging del sistema

Uso y Ejemplos
--------------
**Registro de feedback de usuario:**
```python
response = await client.post("/api/iterative-improvement/feedback", json={
    "analysis_type": "hypothesis_generation",
    "feedback_type": "user_rating",
    "value": 0.85,
    "parameters": {"model": "gpt-4", "temperature": 0.7},
    "context": {"user_id": "researcher_001", "session_id": "sess_123"}
})
```

**Obtener métricas de rendimiento:**
```python
response = await client.get("/api/iterative-improvement/metrics?analysis_type=literature_search")
# Retorna tendencias de accuracy, tiempo de completion, tasas de error
```

**Simular impacto de optimización:**
```python
response = await client.post("/api/iterative-improvement/simulate", json={
    "analysis_type": "evidence_synthesis",
    "parameter_changes": {
        "confidence_threshold": 0.8,
        "max_evidence_sources": 25
    }
})
# Retorna predicción de mejora y intervalos de confianza
```

**Obtener recomendaciones de optimización:**
```python
response = await client.get("/api/iterative-improvement/recommendations/experimental_design")
# Retorna sugerencias basadas en datos históricos con niveles de confianza
```

Notas de Seguridad
-----------------
- Validación estricta de tipos de análisis y feedback permitidos
- Rate limiting aplicado globalmente en main.py
- Logging detallado de todas las operaciones de feedback
- Validación de rangos de valores de feedback (0-1 para ratings)
- Manejo seguro de excepciones sin exposición de información interna
- Dependencias inyectadas mediante FastAPI Depends para testabilidad

Consideraciones de Rendimiento
-----------------------------
- Operaciones asíncronas para procesamiento de feedback masivo
- Caching de métricas de rendimiento para consultas frecuentes
- Optimización de consultas de base de datos para análisis históricos
- Simulaciones limitadas a cambios de parámetros razonables
- Monitoreo de salud del servicio con indicadores en tiempo real
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum

from app.exceptions.domain.biology import BiologyError
from app.services.iterative_improvement_service import (
    get_improvement_pipeline,
    IterativeImprovementPipeline,
    AnalysisType,
    FeedbackType,
)
from app.core.bootstrap_logging import logger

# Create router
router = APIRouter()

# Pydantic models for API requests/responses

class AnalysisTypeEnum(str, Enum):
    """Analysis types for API"""
    literature_search = "literature_search"
    evidence_synthesis = "evidence_synthesis"
    hypothesis_generation = "hypothesis_generation"
    model_prediction = "model_prediction"
    experimental_design = "experimental_design"
    peer_review = "peer_review"
    tool_orchestration = "tool_orchestration"

class FeedbackTypeEnum(str, Enum):
    """Feedback types for API"""
    user_rating = "user_rating"
    accuracy_score = "accuracy_score"
    completion_time = "completion_time"
    error_rate = "error_rate"
    coherence_score = "coherence_score"
    relevance_score = "relevance_score"
    scientific_validity = "scientific_validity"

class FeedbackRequest(BaseModel):
    """Request model for recording feedback"""
    analysis_type: AnalysisTypeEnum = Field(..., description="Type of analysis being evaluated")
    feedback_type: FeedbackTypeEnum = Field(..., description="Type of feedback being provided")
    value: float = Field(..., description="Feedback value (0-1 for ratings, actual value for metrics)", ge=0)
    parameters: Dict[str, Any] = Field(..., description="Parameters used in the analysis")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context information")
    source: str = Field(default="api", description="Source of the feedback")

class SimulationRequest(BaseModel):
    """Request model for improvement simulation"""
    analysis_type: AnalysisTypeEnum = Field(..., description="Type of analysis to simulate")
    parameter_changes: Dict[str, Any] = Field(..., description="Parameter changes to simulate")

def get_improvement_service():
    """Get improvement pipeline service instance"""
    return get_improvement_pipeline()

@router.post("/feedback", response_model=Dict[str, Any])
async def record_feedback(
    request: FeedbackRequest,
    service: IterativeImprovementPipeline = Depends(get_improvement_service)
):
    """
    Record feedback for a specific analysis to improve future performance
    
    This endpoint allows recording various types of feedback including:
    - User ratings and satisfaction scores
    - Objective accuracy measurements
    - Performance metrics (completion time, error rates)
    - Quality assessments (coherence, relevance, scientific validity)
    """
    try:
        logger.info(f"Recording {request.feedback_type} feedback for {request.analysis_type}")
        
        # Convert enums to internal types
        analysis_type = AnalysisType(request.analysis_type.value)
        feedback_type = FeedbackType(request.feedback_type.value)
        
        # Record feedback
        feedback_id = await service.record_feedback(
            analysis_type=analysis_type,
            feedback_type=feedback_type,
            value=request.value,
            parameters=request.parameters,
            context=request.context,
            source=request.source
        )
        
        return {
            "success": True,
            "feedback_id": feedback_id,
            "message": "Feedback recorded successfully",
            "analysis_type": request.analysis_type,
            "feedback_type": request.feedback_type,
            "value": request.value
        }
        
    except BiologyError as e:
        logger.error(f"Failed to record feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=Dict[str, Any])
async def get_performance_metrics(
    analysis_type: Optional[AnalysisTypeEnum] = None,
    service: IterativeImprovementPipeline = Depends(get_improvement_service)
):
    """
    Get current performance metrics for analysis types
    
    Returns comprehensive performance metrics including:
    - Accuracy trends and statistics
    - Completion time analysis
    - Error rates and reliability metrics
    - Quality scores (coherence, relevance, validity)
    - Improvement trends over time
    """
    try:
        logger.info(f"Retrieving metrics for {analysis_type or 'all analysis types'}")
        
        # Convert enum if provided
        at = AnalysisType(analysis_type.value) if analysis_type else None
        
        metrics = await service.get_performance_metrics(at)
        
        return {
            "success": True,
            "data": metrics,
            "requested_type": analysis_type.value if analysis_type else "all"
        }
        
    except BiologyError as e:
        logger.error(f"Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{analysis_type}", response_model=Dict[str, Any])
async def get_optimization_recommendations(
    analysis_type: AnalysisTypeEnum,
    service: IterativeImprovementPipeline = Depends(get_improvement_service)
):
    """
    Get optimization recommendations for a specific analysis type
    
    Returns data-driven recommendations for improving analysis performance:
    - Parameter optimization suggestions
    - Expected improvement estimates
    - Confidence levels and rationale
    - Based on historical performance patterns
    """
    try:
        logger.info(f"Retrieving optimization recommendations for {analysis_type}")
        
        # Convert enum
        at = AnalysisType(analysis_type.value)
        
        recommendations = await service.get_optimization_recommendations(at)
        
        return {
            "success": True,
            "data": recommendations,
            "analysis_type": analysis_type.value
        }
        
    except BiologyError as e:
        logger.error(f"Failed to get optimization recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate", response_model=Dict[str, Any])
async def simulate_improvement_impact(
    request: SimulationRequest,
    service: IterativeImprovementPipeline = Depends(get_improvement_service)
):
    """
    Simulate the potential impact of parameter changes on analysis performance
    
    Predicts performance improvements based on:
    - Historical data patterns
    - Similar parameter configurations
    - Machine learning-based impact estimation
    - Confidence intervals and uncertainty quantification
    """
    try:
        logger.info(f"Simulating improvement impact for {request.analysis_type}")
        
        # Convert enum
        analysis_type = AnalysisType(request.analysis_type.value)
        
        simulation = await service.simulate_improvement_impact(
            analysis_type=analysis_type,
            parameter_changes=request.parameter_changes
        )
        
        return {
            "success": True,
            "data": simulation,
            "analysis_type": request.analysis_type.value,
            "parameter_changes": request.parameter_changes
        }
        
    except BiologyError as e:
        logger.error(f"Failed to simulate improvement impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/insights", response_model=Dict[str, Any])
async def get_learning_insights(
    service: IterativeImprovementPipeline = Depends(get_improvement_service)
):
    """
    Get insights about what the system has learned from feedback
    
    Provides comprehensive analysis of:
    - Learning patterns and trends across all analysis types
    - Performance evolution over time
    - Most effective optimization strategies
    - System-wide improvement statistics
    - Knowledge discovery and insights
    """
    try:
        logger.info("Retrieving learning insights")
        
        insights = await service.get_learning_insights()
        
        return {
            "success": True,
            "data": insights,
            "message": "Learning insights retrieved successfully"
        }
        
    except BiologyError as e:
        logger.error(f"Failed to get learning insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=Dict[str, Any])
async def get_service_health(
    service: IterativeImprovementPipeline = Depends(get_improvement_service)
):
    """
    Get improvement pipeline service health status
    
    Returns:
    - Service operational status
    - Data availability and statistics
    - Configuration parameters
    - System health indicators
    """
    try:
        health = await service.get_service_health()
        
        return {
            "success": True,
            "health": health,
            "timestamp": health.get('timestamp', 'unknown')
        }
        
    except BiologyError as e:
        logger.error(f"Failed to get service health: {e}")
        return {
            "success": False,
            "error": str(e),
            "service": "IterativeImprovementPipeline"
        }

@router.get("/status", response_model=Dict[str, Any])
async def get_pipeline_status(
    service: IterativeImprovementPipeline = Depends(get_improvement_service)
):
    """
    Get detailed status of the improvement pipeline
    
    Returns comprehensive status including:
    - Active learning processes
    - Recent feedback statistics
    - Optimization recommendation counts
    - Performance trend summaries
    """
    try:
        # Get basic health
        health = await service.get_service_health()
        
        # Get summary metrics
        metrics = await service.get_performance_metrics()
        
        # Get learning insights
        insights = await service.get_learning_insights()
        
        return {
            "success": True,
            "status": {
                "service_health": health,
                "metrics_summary": {
                    "analysis_types_tracked": metrics.get('analysis_types_tracked', 0),
                    "total_feedback_entries": metrics.get('total_feedback_entries', 0)
                },
                "learning_summary": {
                    "total_recommendations": insights.get('overall_trends', {}).get('total_recommendations_generated', 0),
                    "most_improved": insights.get('overall_trends', {}).get('most_improved_analysis', 'none'),
                    "most_accurate": insights.get('overall_trends', {}).get('most_accurate_analysis', 'none')
                }
            },
            "message": "Pipeline status retrieved successfully"
        }
        
    except BiologyError as e:
        logger.error(f"Failed to get pipeline status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
