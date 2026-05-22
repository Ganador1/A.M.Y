"""
🔬 Motor de Reproducibilidad Activa - API para reproducción activa de experimentos científicos

Este módulo proporciona endpoints para el motor de reproducibilidad activa que puede
analizar métodos científicos de artículos académicos y ejecutar intentos de reproducción
de experimentos con validación automática de resultados.

Características principales:
- 📝 Análisis sintáctico de secciones de métodos científicos
- 🛠️ Mapeo automático a herramientas disponibles en AXIOM
- 🔄 Aplicación de perturbaciones controladas para robustez
- ⚡ Ejecución paralela de variaciones experimentales
- 📊 Validación automática contra resultados esperados
- 📈 Análisis de patrones de reproducibilidad
- 🧹 Gestión inteligente de almacenamiento de intentos

Dominios científicos soportados:
- 🧬 Biología molecular y computacional
- 🧪 Química computacional y simulación
- 🔬 Física computacional y modelado
- 📊 Ciencia de datos y aprendizaje automático
- 🧮 Matemáticas aplicadas y computación simbólica

El motor utiliza técnicas avanzadas de procesamiento de lenguaje natural para interpretar
métodos científicos, mapea automáticamente a herramientas disponibles, y ejecuta
experimentos con múltiples variaciones para evaluar la robustez y reproducibilidad.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
Version: 4.1
"""

import logging
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field, ConfigDict

from app.security import require_scopes
from app.exceptions.domain.biology import BiologyError
from app.types.reproducibility_engine_types import (
    ParseMethodsOnlyResult,
    AnalyzeReproductionsResult,
    GetReproductionAttemptResult,
    HealthCheckResult,
)
from app.services.active_reproducibility_engine import (
    get_reproducibility_engine,
    ReproductionAttempt,
    PerturbationType,
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router with authentication
router = APIRouter(
    prefix="/api/v1/reproducibility",
    tags=["reproducibility", "validation"],
    dependencies=[Depends(require_scopes(["reproducibility"]))]
)


class ReproductionRequest(BaseModel):
    """Request model for attempting experiment reproduction"""
    paper_id: str = Field(..., description="Unique identifier for the paper")
    methods_text: str = Field(..., description="Full text of methods section")
    title: Optional[str] = Field(default="", description="Paper title")
    expected_results: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Expected results for validation (metric_name -> value)"
    )
    perturbation_types: Optional[List[str]] = Field(
        default=None,
        description="Types of perturbations to apply"
    )
    n_variations: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of experimental variations to run"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "paper_id": "arxiv:2301.12345",
                "methods_text": "We performed molecular dynamics simulations...",
                "title": "Novel protein interactions revealed by MD",
                "expected_results": {
                    "binding_energy": -45.2,
                    "rmsd": 2.3
                },
                "perturbation_types": ["parameter", "noise"],
                "n_variations": 3
            }
        }
    )


class MethodsParsingRequest(BaseModel):
    """Request model for parsing methods only"""
    paper_id: str = Field(..., description="Paper identifier")
    methods_text: str = Field(..., description="Methods section text")
    title: Optional[str] = Field(default="", description="Paper title")


class BatchReproductionRequest(BaseModel):
    """Request for batch reproduction attempts"""
    papers: List[ReproductionRequest] = Field(
        ...,
        description="List of papers to reproduce"
    )
    parallel: bool = Field(
        default=False,
        description="Whether to run reproductions in parallel"
    )


class ReproductionAnalysisRequest(BaseModel):
    """Request for analyzing reproduction patterns"""
    attempt_ids: Optional[List[str]] = Field(
        default=None,
        description="Specific attempt IDs to analyze (None = all)"
    )
    domain_filter: Optional[str] = Field(
        default=None,
        description="Filter by scientific domain"
    )
    success_only: bool = Field(
        default=False,
        description="Include only successful reproductions"
    )


# Storage for reproduction attempts (in production, use database)
_reproduction_attempts: Dict[str, ReproductionAttempt] = {}


@router.post("/reproduce",
    dependencies=[Depends(require_scopes(["reproducibility:execute"]))],
    response_model=Dict[str, Any]
)
async def attempt_reproduction(
    request: ReproductionRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    🔬 Intenta reproducir un experimento científico desde métodos de artículo

    Este endpoint analiza la sección de métodos, mapea automáticamente a herramientas
    disponibles en AXIOM, aplica perturbaciones controladas y ejecuta experimentos
    con validación automática de resultados contra valores esperados.

    Args:
        request: Solicitud de reproducción con ID del artículo, texto de métodos y configuración
        background_tasks: Tareas en segundo plano para procesamiento asíncrono

    Returns:
        Dict[str, Any]: Resultado del intento de reproducción con métricas detalladas

    Raises:
        HTTPException: Si hay error en el análisis, mapeo o ejecución

    Example:
        POST /reproduce
        {
            "paper_id": "arxiv:2301.12345",
            "methods_text": "Realizamos simulaciones de dinámica molecular...",
            "title": "Interacciones proteicas reveladas por MD",
            "expected_results": {"energia_union": -45.2, "rmsd": 2.3},
            "perturbation_types": ["parametro", "ruido"],
            "n_variations": 3
        }
    """
    start_time = datetime.datetime.now()

    try:
        # Validación de entrada
        if not request.paper_id or not request.paper_id.strip():
            logger.warning("🚫 ID del artículo vacío o inválido")
            raise HTTPException(
                status_code=400,
                detail="paper_id es requerido y no puede estar vacío"
            )

        if not request.methods_text or not request.methods_text.strip():
            logger.warning("🚫 Texto de métodos vacío o inválido")
            raise HTTPException(
                status_code=400,
                detail="methods_text es requerido y no puede estar vacío"
            )

        if len(request.methods_text.strip()) < 50:
            logger.warning("🚫 Texto de métodos demasiado corto: %d caracteres", len(request.methods_text))
            raise HTTPException(
                status_code=400,
                detail="methods_text debe tener al menos 50 caracteres"
            )

        logger.info("🔬 Iniciando intento de reproducción para artículo %s", request.paper_id)
        logger.info("📊 Configuración: %d variaciones, tipos de perturbación: %s",
                   request.n_variations, request.perturbation_types or [])

        # Parse perturbation types
        perturbation_types = None
        if request.perturbation_types:
            try:
                perturbation_types = [
                    PerturbationType[pt.upper()]
                    for pt in request.perturbation_types
                ]
                logger.info("🔧 Tipos de perturbación mapeados: %s", [pt.name for pt in perturbation_types])
            except KeyError as e:
                logger.warning("🚫 Tipo de perturbación inválido: %s", str(e))
                raise HTTPException(
                    status_code=400,
                    detail=f"Tipo de perturbación inválido: {str(e)}"
                )

        # Ejecutar intento de reproducción
        engine = await get_reproducibility_engine()
        attempt = await engine.attempt_reproduction(
            paper_id=request.paper_id,
            methods_text=request.methods_text,
            title=request.title or "",
            expected_results=request.expected_results,
            perturbation_types=perturbation_types,
            n_variations=request.n_variations
        )

        # Almacenar intento
        _reproduction_attempts[attempt.attempt_id] = attempt

        # Calcular tiempo de ejecución
        execution_time = (datetime.datetime.now() - start_time).total_seconds()

        # Enriquecer respuesta con metadatos
        response = {
            "status": "success",
            "attempt_id": attempt.attempt_id,
            "paper_id": attempt.paper_id,
            "reproduction_status": attempt.status.value,
            "success": attempt.success,
            "reproducibility_score": attempt.reproducibility_score,
            "steps_parsed": len(attempt.original_methods.steps) if attempt.original_methods else 0,
            "tools_mapped": len(attempt.tool_mappings),
            "experiments_run": len(attempt.execution_results),
            "issues": attempt.issues,
            "validation_results": attempt.validation_results,
            "timestamp": attempt.timestamp.isoformat(),
            "metadata": {
                "execution_time_seconds": execution_time,
                "n_variations_requested": request.n_variations,
                "perturbation_types_applied": [pt.name for pt in (perturbation_types or [])],
                "methods_text_length": len(request.methods_text),
                "has_expected_results": request.expected_results is not None
            }
        }

        logger.info("✅ Intento de reproducción completado: %s (éxito: %s, puntuación: %.3f, tiempo: %.4fs)",
                   attempt.attempt_id, attempt.success, attempt.reproducibility_score, execution_time)

        return response

    except HTTPException:
        raise
    except BiologyError as e:
        execution_time = (datetime.datetime.now() - start_time).total_seconds()
        logger.error("❌ Error interno en intento de reproducción: %s (tiempo: %.4fs)", str(e), execution_time)
        raise HTTPException(
            status_code=500,
            detail=f"Intento de reproducción fallido: {str(e)}"
        ) from e


@router.post("/parse-methods",
    dependencies=[Depends(require_scopes(["reproducibility:read"]))],
    response_model=Dict[str, Any]
)
async def parse_methods_only(request: MethodsParsingRequest) -> ParseMethodsOnlyResult:
    """
    Parse methods section without executing experiments

    Useful for testing the parsing capabilities and understanding
    how methods are interpreted.
    """
    try:
        engine = await get_reproducibility_engine()

        # Parse methods
        parsed = await engine.parser.parse_methods(
            methods_text=request.methods_text,
            paper_id=request.paper_id,
            title=request.title or ""
        )

        # Map to tools
        mappings = await engine.mapper.map_to_tools(parsed)

        # Convert to response
        return {
            "status": "success",
            "paper_id": parsed.paper_id,
            "parsing_confidence": parsed.parsing_confidence,
            "domain": parsed.domain,
            "experimental_type": parsed.experimental_type,
            "key_molecules": parsed.key_molecules,
            "key_parameters": parsed.key_parameters,
            "steps": [
                {
                    "step_number": step.step_number,
                    "description": step.description,
                    "tool_hint": step.tool_hint,
                    "parameters": step.parameters,
                    "chemicals": step.chemicals,
                    "equipment": step.equipment
                }
                for step in parsed.steps
            ],
            "tool_mappings": [
                {
                    "step_number": mapping.step_number,
                    "tool_domain": mapping.tool_domain,
                    "tool_name": mapping.tool_name,
                    "method": mapping.method,
                    "confidence": mapping.confidence,
                    "parameters": mapping.mapped_parameters
                }
                for mapping in mappings
            ]
        }

    except BiologyError as e:
        logger.error(f"Error parsing methods: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Methods parsing failed: {str(e)}"
        )


@router.post("/batch-reproduce",
    dependencies=[Depends(require_scopes(["reproducibility:execute"]))],
    response_model=Dict[str, Any]
)
async def batch_reproduction(
    request: BatchReproductionRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Attempt to reproduce multiple papers in batch

    Can run reproductions in parallel or sequentially.
    """
    try:
        engine = await get_reproducibility_engine()

        results = []

        if request.parallel:
            # Run in parallel using asyncio
            import asyncio

            tasks = []
            for paper_req in request.papers:
                perturbation_types = None
                if paper_req.perturbation_types:
                    perturbation_types = [
                        PerturbationType[pt.upper()]
                        for pt in paper_req.perturbation_types
                    ]

                task = engine.attempt_reproduction(
                    paper_id=paper_req.paper_id,
                    methods_text=paper_req.methods_text,
                    title=paper_req.title or "",
                    expected_results=paper_req.expected_results,
                    perturbation_types=perturbation_types,
                    n_variations=paper_req.n_variations
                )
                tasks.append(task)

            attempts = await asyncio.gather(*tasks)

        else:
            # Run sequentially
            attempts = []
            for paper_req in request.papers:
                perturbation_types = None
                if paper_req.perturbation_types:
                    perturbation_types = [
                        PerturbationType[pt.upper()]
                        for pt in paper_req.perturbation_types
                    ]

                attempt = await engine.attempt_reproduction(
                    paper_id=paper_req.paper_id,
                    methods_text=paper_req.methods_text,
                    title=paper_req.title or "",
                    expected_results=paper_req.expected_results,
                    perturbation_types=perturbation_types,
                    n_variations=paper_req.n_variations
                )
                attempts.append(attempt)

        # Store all attempts
        for attempt in attempts:
            _reproduction_attempts[attempt.attempt_id] = attempt
            results.append({
                "attempt_id": attempt.attempt_id,
                "paper_id": attempt.paper_id,
                "success": attempt.success,
                "score": attempt.reproducibility_score
            })

        return {
            "status": "success",
            "batch_id": f"batch_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "total_papers": len(request.papers),
            "successful": sum(1 for a in attempts if a.success),
            "failed": sum(1 for a in attempts if not a.success),
            "results": results
        }

    except BiologyError as e:
        logger.error(f"Error in batch reproduction: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch reproduction failed: {str(e)}"
        )


@router.post("/analyze",
    dependencies=[Depends(require_scopes(["reproducibility:read"]))],
    response_model=Dict[str, Any]
)
async def analyze_reproductions(request: ReproductionAnalysisRequest) -> AnalyzeReproductionsResult:
    """
    Analyze patterns in reproduction attempts

    Provides insights into success rates, common issues, and reliability.
    """
    try:
        engine = await get_reproducibility_engine()

        # Filter attempts
        attempts = list(_reproduction_attempts.values())

        if request.attempt_ids:
            attempts = [a for a in attempts if a.attempt_id in request.attempt_ids]

        if request.domain_filter:
            attempts = [
                a for a in attempts
                if a.original_methods and
                a.original_methods.domain == request.domain_filter
            ]

        if request.success_only:
            attempts = [a for a in attempts if a.success]

        # Analyze
        analysis = await engine.analyze_reproduction_patterns(attempts)

        return {
            "status": "success",
            "analysis": analysis,
            "filters_applied": {
                "domain": request.domain_filter,
                "success_only": request.success_only,
                "n_attempts": len(attempts)
            }
        }

    except BiologyError as e:
        logger.error(f"Error analyzing reproductions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/attempt/{attempt_id}",
    dependencies=[Depends(require_scopes(["reproducibility:read"]))],
    response_model=Dict[str, Any]
)
async def get_reproduction_attempt(attempt_id: str) -> GetReproductionAttemptResult:
    """
    Get details of a specific reproduction attempt
    """
    if attempt_id not in _reproduction_attempts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reproduction attempt {attempt_id} not found"
        )

    attempt = _reproduction_attempts[attempt_id]

    return {
        "status": "success",
        "attempt": {
            "attempt_id": attempt.attempt_id,
            "paper_id": attempt.paper_id,
            "status": attempt.status.value,
            "success": attempt.success,
            "reproducibility_score": attempt.reproducibility_score,
            "original_methods": {
                "title": attempt.original_methods.title if attempt.original_methods else "",
                "n_steps": len(attempt.original_methods.steps) if attempt.original_methods else 0,
                "domain": attempt.original_methods.domain if attempt.original_methods else None,
                "parsing_confidence": attempt.original_methods.parsing_confidence if attempt.original_methods else 0
            },
            "tool_mappings": len(attempt.tool_mappings),
            "experiments_run": len(attempt.execution_results),
            "validation_results": attempt.validation_results,
            "issues": attempt.issues,
            "timestamp": attempt.timestamp.isoformat()
        }
    }


@router.get("/health")
async def health_check() -> HealthCheckResult:
    """
    🏥 Verificación de salud del motor de reproducibilidad

    Verifica el estado operativo del motor de reproducibilidad activa,
    incluyendo conectividad con servicios subyacentes y estadísticas de uso.

    Returns:
        Dict[str, Any]: Estado de salud con métricas operativas
    """
    try:
        # Verificar conectividad básica (sin almacenar la variable)
        await get_reproducibility_engine()

        return {
            "status": "healthy",
            "service": "reproducibility_engine",
            "attempts_stored": len(_reproduction_attempts),
            "message": "Reproducibility engine operational",
            "timestamp": datetime.datetime.now().isoformat()
        }
    except BiologyError as e:
        return {
            "status": "unhealthy",
            "service": "reproducibility_engine",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }


@router.post("/advanced-robustness-analysis", summary="Advanced Robustness Analysis")
async def advanced_robustness_analysis(request: Dict[str, Any]):
    """
    Perform advanced robustness analysis using perturbation engine.

    This endpoint combines perturbation engine capabilities with reproducibility tracking:
    - Generates multiple parameter perturbations
    - Simulates experiments with each parameter set
    - Records results in reproducibility database
    - Calculates comprehensive robustness metrics
    """
    try:
        engine = await get_reproducibility_engine()
        result = await engine.advanced_robustness_analysis(request)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except BiologyError as e:
        logger.error(f"❌ Error in advanced robustness analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Advanced robustness analysis failed: {str(e)}")


@router.post("/analyze-failure-patterns", summary="Analyze Failure Patterns")
async def analyze_failure_patterns(request: Dict[str, Any]):
    """
    Analyze patterns in reproducibility failures.

    This endpoint:
    - Identifies common failure patterns
    - Analyzes parameter-related failures
    - Detects error message patterns
    - Generates pattern-based recommendations
    """
    try:
        engine = await get_reproducibility_engine()
        result = await engine.analyze_failure_patterns(request)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except BiologyError as e:
        logger.error(f"❌ Error analyzing failure patterns: {e}")
        raise HTTPException(status_code=500, detail=f"Failure pattern analysis failed: {str(e)}")


@router.post("/generate-reproducibility-recommendations", summary="Generate Reproducibility Recommendations")
async def generate_reproducibility_recommendations(request: Dict[str, Any]):
    """
    Generate recommendations for improving reproducibility.

    This endpoint:
    - Analyzes failure patterns
    - Generates evidence-based recommendations
    - Prioritizes recommendations by impact
    - Provides implementation guidance
    """
    try:
        engine = await get_reproducibility_engine()
        result = await engine.generate_reproducibility_recommendations(request)

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except BiologyError as e:
        logger.error(f"❌ Error generating reproducibility recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Reproducibility recommendations generation failed: {str(e)}")


@router.get("/reproducibility-statistics", summary="Get Reproducibility Statistics")
async def get_reproducibility_statistics(experiment_type: Optional[str] = None, time_range: int = 30):
    """
    Get comprehensive reproducibility statistics.

    This endpoint provides:
    - Overall success/failure rates
    - Performance metrics by experiment type
    - Temporal trends
    - Database statistics
    """
    try:
        engine = await get_reproducibility_engine()
        result = await engine.get_reproducibility_statistics({
            "experiment_type": experiment_type,
            "time_range": time_range
        })

        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])

    except BiologyError as e:
        logger.error(f"❌ Error getting reproducibility statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Reproducibility statistics retrieval failed: {str(e)}")
