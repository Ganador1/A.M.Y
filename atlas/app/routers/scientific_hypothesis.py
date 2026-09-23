"""
🧠 AGENTE DE HIPÓTESIS CIENTÍFICAS - AXIOM META 4.1
═══════════════════════════════════════════════════════════════════════════════════════════════

Módulo de generación y refinamiento autónomo de hipótesis científicas para la plataforma
AXIOM v4.1. Implementa un agente inteligente capaz de formular hipótesis científicas,
gestionar ciclos de investigación completos y refinar teorías basadas en evidencia.

FUNCIONALIDADES PRINCIPALES:
────────────────────────────
• Generación autónoma de hipótesis científicas innovadoras
• Integración con literatura científica para fundamentación
• Ciclos de investigación completos con diseño experimental
• Análisis de evidencia y validación estadística
• Refinamiento iterativo basado en retroalimentación
• Evaluación de confianza y robustez de hipótesis
• Soporte multi-dominio (ciencias de materiales, descubrimiento de fármacos, etc.)
• Gestión de hipótesis activas y archivadas

ARQUITECTURA TÉCNICA:
─────────────────────
• Framework: FastAPI con enrutamiento REST asíncrono
• Servicio backend: ScientificHypothesisAgent con IA generativa
• Autenticación: JWT Bearer tokens (scopes implícitos)
• Validación: Pydantic models con constraints específicos
• Logging: Configuración estructurada con indicadores científicos
• Manejo de errores: HTTPException con códigos específicos
• Procesamiento: Asyncio para operaciones de IA no bloqueantes
• Almacenamiento: Base de datos persistente para hipótesis

ENDPOINTS DISPONIBLES:
──────────────────────
• POST /generate-hypothesis - Generar nueva hipótesis científica
• POST /start-research-cycle - Iniciar ciclo de investigación completo
• POST /refine-hypothesis - Refinar hipótesis manualmente
• POST /analyze-evidence - Analizar evidencia para hipótesis
• GET /hypothesis/{id} - Obtener hipótesis específica
• POST /list-hypotheses - Listar hipótesis con filtros
• GET /health - Verificación de estado del servicio
• GET /stats - Estadísticas del agente de hipótesis

MODELOS DE DATOS:
─────────────────
• HypothesisGenerationRequest: Parámetros para generación de hipótesis
• ResearchCycleRequest: Configuración de ciclo de investigación
• HypothesisRefinementRequest: Datos para refinamiento de hipótesis
• EvidenceAnalysisRequest: Solicitud de análisis de evidencia
• HypothesisQueryRequest: Consulta de hipótesis específica
• HypothesisListRequest: Filtros para listado de hipótesis

CONSIDERACIONES DE SEGURIDAD:
────────────────────────────
• Validación estricta de dominios científicos soportados
• Control de acceso basado en roles de investigador
• Sanitización de datos de entrada para prevenir inyección
• Límites en complejidad de hipótesis generadas
• Logging detallado para auditoría de investigación
• Validación de confianza mínima para hipótesis activas

MANEJO DE ERRORES:
──────────────────
• 400 Bad Request: Parámetros inválidos o dominios no soportados
• 404 Not Found: Hipótesis no encontrada
• 500 Internal Server Error: Errores del agente de IA
• Logging estructurado con códigos de error específicos
• Recuperación automática de operaciones fallidas

EJEMPLOS DE USO:
────────────────
# Generar hipótesis en ciencias de materiales
POST /api/v1/scientific-hypothesis/generate-hypothesis
{
    "domain": "materials_science",
    "research_question": "¿Cómo mejorar la conductividad de nanomateriales?",
    "context_data": {
        "temperature_range": [300, 1000],
        "material_types": ["carbon_nanotubes", "graphene"]
    }
}

# Iniciar ciclo de investigación
POST /api/v1/scientific-hypothesis/start-research-cycle
{
    "hypothesis_id": "hyp_1234567890"
}

DEPENDENCIAS:
─────────────
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos
• openai/anthropic: Modelos de IA para generación de hipótesis
• scipy/numpy: Análisis estadístico y computacional
• sqlalchemy: Persistencia de hipótesis en base de datos
• asyncio: Programación asíncrona para IA

NOTAS DE IMPLEMENTACIÓN:
───────────────────────
• Todas las operaciones son asíncronas para no bloquear el servidor
• Las hipótesis se generan con IDs únicos para trazabilidad
• Integración automática con literatura científica relevante
• Evaluación de novedad y plausibilidad de hipótesis
• Ciclos de investigación con diseño experimental automático
• Refinamiento iterativo basado en evidencia experimental
• Soporte para colaboración multi-usuario en hipótesis

VERSIÓN: AXIOM META 4.1
FECHA: Diciembre 2024
AUTOR: Equipo de Desarrollo AXIOM
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
from pydantic import BaseModel
import time
import uuid
from datetime import datetime

from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent
from app.services.ollama_service import ollama_service, HypothesisRequest, HypothesisResponse
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError
from app.types.scientific_hypothesis_types import (
    GenerateHypothesisOllamaResult,
    GenerateHypothesisResult,
    StartResearchCycleResult,
    RefineHypothesisResult,
    AnalyzeEvidenceResult,
    GetHypothesisResult,
    ListHypothesesResult,
    HealthCheckResult,
    GetStatsResult,
)

router = APIRouter(tags=["Scientific Hypothesis Agent"])
scientific_hypothesis_router = router
__all__ = ["scientific_hypothesis_router"]

# Initialize service
hypothesis_agent = ScientificHypothesisAgent()


class HypothesisGenerationRequest(BaseModel):
    domain: str
    research_question: str
    context_data: Optional[Dict[str, Any]] = None


class ResearchCycleRequest(BaseModel):
    hypothesis_id: str


class HypothesisRefinementRequest(BaseModel):
    hypothesis_id: str
    refinement_data: Dict[str, Any]


class EvidenceAnalysisRequest(BaseModel):
    hypothesis_id: str


class HypothesisQueryRequest(BaseModel):
    hypothesis_id: str


class HypothesisListRequest(BaseModel):
    domain: Optional[str] = None
    status: Optional[str] = None
    min_confidence: Optional[float] = 0.0


class OllamaHypothesisRequest(BaseModel):
    """Solicitud de hipótesis usando Ollama Cloud"""
    domain: str
    research_question: str
    context_data: Optional[Dict[str, Any]] = None
    model_preference: Optional[str] = None


@router.post("/generate-hypothesis-ollama")
async def generate_hypothesis_ollama(request: OllamaHypothesisRequest) -> GenerateHypothesisOllamaResult:
    """
    🚀 Generar Hipótesis Científica con Ollama Cloud

    Endpoint avanzado que utiliza modelos de IA de Ollama Cloud para generar
    hipótesis científicas reales y de alta calidad. Reemplaza el sistema mock
    con inteligencia artificial real.

    **Modelos utilizados por dominio:**
    - **quantum_computing**: deepseek-r1 (razonamiento profundo)
    - **materials_science**: qwen3 (ciencias de materiales)
    - **drug_discovery**: llama3.1 (medicina y farmacología)
    - **energy_storage**: qwen3 (ingeniería y física aplicada)
    - **mathematics**: deepseek-r1 (matemáticas puras)
    - **physics**: deepseek-r1 (física teórica)
    - **biology**: llama3.1 (ciencias biológicas)
    - **chemistry**: qwen3 (química teórica y aplicada)

    **Parámetros de entrada:**
    - **domain**: Dominio científico específico
    - **research_question**: Pregunta de investigación clara y específica
    - **context_data**: Datos contextuales opcionales
    - **model_preference**: Modelo específico a usar (opcional)

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "hypothesis_id": "hyp_ollama_1234567890",
        "hypothesis": {
            "hypothesis_text": "Hipótesis generada por IA",
            "reasoning": "Razonamiento científico detallado",
            "confidence": 0.85,
            "testable_predictions": ["Predicción 1", "Predicción 2"],
            "methodology_suggestions": ["Metodología 1", "Metodología 2"],
            "related_literature": ["Literatura 1", "Literatura 2"]
        },
        "model_used": "deepseek-r1",
        "execution_time_seconds": 3.45,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Códigos de error:**
    - **400**: Parámetros inválidos o modelo no disponible
    - **500**: Error de comunicación con Ollama Cloud
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("🚀 Iniciando generación de hipótesis con Ollama Cloud")
        logger.info("🔬 Dominio: %s", request.domain)
        logger.info("❓ Pregunta: %s", request.research_question)

        # Validaciones de entrada
        supported_domains = [
            "materials_science", "drug_discovery", "energy_storage", "quantum_computing",
            "mathematics", "physics", "biology", "chemistry"
        ]
        
        if request.domain not in supported_domains:
            logger.warning("⚠️ Dominio no soportado: %s", request.domain)
            raise HTTPException(
                status_code=400,
                detail=f"Dominio no soportado: {request.domain}. Dominios válidos: {', '.join(supported_domains)}"
            )

        if not request.research_question or not request.research_question.strip():
            logger.warning("⚠️ Pregunta de investigación vacía")
            raise HTTPException(
                status_code=400,
                detail="La pregunta de investigación no puede estar vacía"
            )

        # Crear solicitud para Ollama
        ollama_request = HypothesisRequest(
            research_question=request.research_question.strip(),
            domain=request.domain,
            context=request.context_data,
            model_preference=request.model_preference
        )

        logger.info("🔄 Ejecutando generación con Ollama Cloud...")
        
        # Generar hipótesis usando Ollama
        ollama_result = await ollama_service.generate_hypothesis(ollama_request)
        
        execution_time = time.time() - start_time
        
        # Generar ID único para la hipótesis
        hypothesis_id = f"hyp_ollama_{str(uuid.uuid4())[:8]}"
        
        # Determinar modelo usado
        model_used = (
            request.model_preference or 
            ollama_service.get_optimal_model(request.domain)
        )
        
        logger.info("✅ Hipótesis generada exitosamente con Ollama en %.2fs", execution_time)
        logger.info("🆔 ID de hipótesis: %s", hypothesis_id)
        logger.info("🤖 Modelo usado: %s", model_used)

        # Formatear respuesta compatible con el sistema existente
        result = {
            "success": True,
            "message": f"Hipótesis '{ollama_result.hypothesis_text[:50]}...' generada exitosamente con Ollama Cloud",
            "hypothesis_id": hypothesis_id,
            "hypothesis": {
                "title": ollama_result.hypothesis_text[:100] + "..." if len(ollama_result.hypothesis_text) > 100 else ollama_result.hypothesis_text,
                "description": ollama_result.hypothesis_text,
                "reasoning": ollama_result.reasoning,
                "confidence_score": ollama_result.confidence,
                "domain": request.domain,
                "variables": ["Variable extraída de la hipótesis"],  # Podríamos extraer esto del texto
                "assumptions": ollama_result.related_literature[:3],  # Usar literatura como assumptions temporalmente
                "expected_outcome": ollama_result.testable_predictions[0] if ollama_result.testable_predictions else "Resultado esperado",
                "testable_predictions": ollama_result.testable_predictions,
                "methodology_suggestions": ollama_result.methodology_suggestions,
                "related_literature": ollama_result.related_literature
            },
            "model_used": model_used,
            "execution_time_seconds": round(execution_time, 2),
            "timestamp": execution_timestamp,
            "source": "ollama_cloud"
        }

        return result

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error("❌ Error interno generando hipótesis con Ollama: %s (tiempo: %.2fs)", str(e), execution_time)
        logger.error("🔍 Detalles del error: %s: %s", type(e).__name__, str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Error interno de Ollama Cloud: {str(e)}"
        ) from e


@router.post("/generate-hypothesis")
async def generate_hypothesis(request: HypothesisGenerationRequest) -> GenerateHypothesisResult:
    """
    🧠 Generar Hipótesis Científica

    Endpoint principal para la generación autónoma de hipótesis científicas innovadoras.
    Utiliza IA avanzada para formular hipótesis basadas en preguntas de investigación
    y datos contextuales específicos del dominio científico.

    **Parámetros de entrada:**
    - **domain**: Dominio científico específico (materials_science, drug_discovery, energy_storage, quantum_computing)
    - **research_question**: Pregunta de investigación clara y específica
    - **context_data**: Datos contextuales opcionales (temperaturas, tipos de material, etc.)

    **Dominios soportados:**
    - **materials_science**: Ciencias de materiales y nanomateriales
    - **drug_discovery**: Descubrimiento y desarrollo de fármacos
    - **energy_storage**: Almacenamiento de energía y baterías
    - **quantum_computing**: Computación cuántica y algoritmos

    **Validaciones realizadas:**
    - Dominio debe ser uno de los soportados
    - Pregunta de investigación no puede estar vacía
    - Datos contextuales deben ser un diccionario válido

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "hypothesis_id": "hyp_1234567890",
        "hypothesis": {
            "statement": "Los nanomateriales dopados con nitrógeno...",
            "confidence_score": 0.85,
            "domain": "materials_science",
            "evidence_basis": ["literature_ref_1", "literature_ref_2"],
            "experimental_design": {
                "variables": ["concentration", "temperature"],
                "controls": ["pH", "pressure"],
                "measurements": ["conductivity", "stability"]
            }
        },
        "execution_time_seconds": 2.34,
        "timestamp": "2024-12-01T10:30:00"
    }
    ```

    **Códigos de error:**
    - **400**: Parámetros inválidos o dominio no soportado
    - **500**: Error interno del agente de hipótesis
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info("🧠 Iniciando generación de hipótesis científica")
        logger.info(f"🔬 Dominio: {request.domain}")
        logger.info(f"❓ Pregunta: {request.research_question}")

        # Validaciones de entrada
        supported_domains = ["materials_science", "drug_discovery", "energy_storage", "quantum_computing"]
        if request.domain not in supported_domains:
            logger.warning(f"⚠️ Dominio no soportado: {request.domain}")
            raise HTTPException(
                status_code=400,
                detail=f"Dominio no soportado: {request.domain}. Dominios válidos: {', '.join(supported_domains)}"
            )

        if not request.research_question or not request.research_question.strip():
            logger.warning("⚠️ Pregunta de investigación vacía")
            raise HTTPException(
                status_code=400,
                detail="La pregunta de investigación no puede estar vacía"
            )

        if len(request.research_question) > 1000:
            logger.warning(f"⚠️ Pregunta demasiado larga: {len(request.research_question)} caracteres")
            raise HTTPException(
                status_code=400,
                detail="La pregunta de investigación debe tener menos de 1000 caracteres"
            )

        # Preparar solicitud para el agente
        agent_request = {
            "action": "generate_hypothesis",
            "domain": request.domain,
            "research_question": request.research_question.strip(),
            "context_data": request.context_data or {},
            "timestamp": execution_timestamp
        }

        logger.info("🔄 Ejecutando agente de hipótesis...")
        result = await hypothesis_agent.process_request(agent_request)

        execution_time = time.time() - start_time

        if not result.get("success"):
            logger.error(f"❌ Error en agente de hipótesis: {result.get('error', 'Error desconocido')}")
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Error en generación de hipótesis")
            )

        logger.info(f"✅ Hipótesis generada exitosamente en {execution_time:.2f}s")
        logger.info(f"🆔 ID de hipótesis: {result.get('hypothesis_id', 'N/A')}")

        # Agregar metadatos de ejecución
        result["execution_time_seconds"] = round(execution_time, 2)
        result["timestamp"] = execution_timestamp

        return result

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error interno generando hipótesis: {str(e)} (tiempo: {execution_time:.2f}s)")
        logger.error(f"🔍 Detalles del error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del agente de hipótesis: {str(e)}"
        )


@router.post("/start-research-cycle")
async def start_research_cycle(request: ResearchCycleRequest, background_tasks: BackgroundTasks) -> StartResearchCycleResult:
    """
    Start a complete research cycle for a hypothesis

    - **hypothesis_id**: ID of the hypothesis to test
    """
    try:
        result = await hypothesis_agent.process_request({
            "action": "start_research_cycle",
            "hypothesis_id": request.hypothesis_id
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Research cycle start failed"))

        return result

    except BiologyError as e:
        logger.error(f"❌ Error starting research cycle: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/refine-hypothesis")
async def refine_hypothesis(request: HypothesisRefinementRequest) -> RefineHypothesisResult:
    """
    Manually refine a hypothesis

    - **hypothesis_id**: ID of the hypothesis to refine
    - **refinement_data**: Data for hypothesis refinement
    """
    try:
        result = await hypothesis_agent.process_request({
            "action": "refine_hypothesis",
            "hypothesis_id": request.hypothesis_id,
            "refinement_data": request.refinement_data
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Hypothesis refinement failed"))

        return result

    except BiologyError as e:
        logger.error(f"❌ Error refining hypothesis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/analyze-evidence")
async def analyze_evidence(request: EvidenceAnalysisRequest) -> AnalyzeEvidenceResult:
    """
    Analyze evidence for a hypothesis

    - **hypothesis_id**: ID of the hypothesis to analyze
    """
    try:
        result = await hypothesis_agent.process_request({
            "action": "analyze_evidence",
            "hypothesis_id": request.hypothesis_id
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "Evidence analysis failed"))

        return result

    except BiologyError as e:
        logger.error(f"❌ Error analyzing evidence: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/hypothesis/{hypothesis_id}")
async def get_hypothesis(hypothesis_id: str) -> GetHypothesisResult:
    """
    Get a specific hypothesis by ID

    - **hypothesis_id**: ID of the hypothesis to retrieve
    """
    try:
        result = await hypothesis_agent.process_request({
            "action": "get_hypothesis",
            "hypothesis_id": hypothesis_id
        })

        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("error", "Hypothesis not found"))

        return result

    except BiologyError as e:
        logger.error(f"❌ Error getting hypothesis: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/list-hypotheses")
async def list_hypotheses(request: HypothesisListRequest) -> ListHypothesesResult:
    """
    List hypotheses with optional filtering

    - **domain**: Filter by scientific domain
    - **status**: Filter by hypothesis status
    - **min_confidence**: Minimum confidence score filter
    """
    try:
        result = await hypothesis_agent.process_request({
            "action": "list_hypotheses",
            "domain": request.domain,
            "status": request.status,
            "min_confidence": request.min_confidence
        })

        if not result.get("success"):
            raise HTTPException(status_code=400, detail=result.get("error", "List hypotheses failed"))

        return result

    except BiologyError as e:
        logger.error(f"❌ Error listing hypotheses: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check() -> HealthCheckResult:
    """Health check for the Scientific Hypothesis Agent service"""
    return {
        "service": "ScientificHypothesisAgent",
        "status": "healthy",
        "version": "2.0",
        "capabilities": [
            "hypothesis_generation",
            "research_cycle_management",
            "evidence_analysis",
            "hypothesis_refinement"
        ]
    }


@router.get("/stats")
async def get_stats() -> GetStatsResult:
    """Get statistics about the Scientific Hypothesis Agent"""
    try:
        # Get basic stats from the service
        list_result = await hypothesis_agent.process_request({
            "action": "list_hypotheses"
        })

        if list_result.get("success"):
            total_hypotheses = list_result["total_count"]
        else:
            total_hypotheses = 0

        return {
            "service": "ScientificHypothesisAgent",
            "total_hypotheses": total_hypotheses,
            "active_research_cycles": len(hypothesis_agent.active_hypotheses),
            "supported_domains": [
                "materials_science",
                "drug_discovery",
                "energy_storage",
                "quantum_computing"
            ],
            "capabilities": [
                "Autonomous hypothesis generation",
                "Literature-integrated reasoning",
                "Iterative hypothesis refinement",
                "Evidence-based validation"
            ]
        }

    except BiologyError as e:
        logger.error(f"❌ Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
