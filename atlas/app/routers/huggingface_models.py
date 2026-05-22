"""
Hugging Face Cloud Models Router for AXIOM Atlas

Router FastAPI para gestión de modelos cloud de Hugging Face especializados
para investigación científica en el sistema multi-agente.

Endpoints disponibles:
- POST /generate: Generación de texto con modelo específico
- POST /generate-for-agent: Generación optimizada por rol de agente
- GET /models: Lista de modelos especializados disponibles
- GET /models/by-domain: Modelos organizados por dominio científico
- GET /models/by-agent: Modelos mapeados por rol de agente
- GET /metrics: Métricas de uso del servicio
- POST /clear-cache: Limpiar caché de respuestas
- POST /test-connection: Probar conectividad con Hugging Face API

Características:
- Modelos especializados para biología, química, física, matemáticas
- Sistema de caché para optimizar respuestas
- Rate limiting automático
- Fallback a modelos alternativos
- Métricas de performance detalladas
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional, Any, List
import logging
from pydantic import BaseModel, Field

from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest,
    HFInferenceResponse,
    huggingface_provider
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/huggingface",
    tags=["Hugging Face", "Cloud Models", "AI", "Multi-Agent"]
)

# Modelos de solicitud para API


class GenerateRequest(BaseModel):
    """Solicitud de generación de texto"""
    model_id: str = Field(..., description="ID del modelo en Hugging Face", examples=["microsoft/biogpt"])
    prompt: str = Field(..., description="Prompt para el modelo", examples=["Generate a hypothesis about protein folding"])
    max_new_tokens: int = Field(512, ge=1, le=4096, description="Máximo de tokens a generar")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperatura para sampling")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling")
    top_k: int = Field(50, ge=1, le=100, description="Top-K sampling")


class AgentGenerateRequest(BaseModel):
    """Solicitud de generación optimizada por rol de agente"""
    agent_role: str = Field(
        ...,
        description="Rol del agente",
        examples=["orchestrator", "bio_hypothesis", "physchem_coder", "reviewer", "publisher"]
    )
    prompt: str = Field(..., description="Prompt para el modelo")
    domain: Optional[str] = Field(None, description="Dominio científico", examples=["biology", "chemistry", "physics"])
    max_new_tokens: int = Field(512, ge=1, le=4096, description="Máximo de tokens a generar")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperatura para sampling")


@router.post("/generate", response_model=HFInferenceResponse)
async def generate_text(request: GenerateRequest):
    """
    🤖 Generar texto con modelo específico de Hugging Face

    Utiliza un modelo específico de Hugging Face para generar texto científico.
    Ideal para experimentación con diferentes modelos.

    Ejemplo:
    ```json
    {
        "model_id": "microsoft/biogpt",
        "prompt": "Generate a hypothesis about cancer immunotherapy",
        "max_new_tokens": 512,
        "temperature": 0.7
    }
    ```
    """
    try:
        logger.info(f"🤖 Generando con modelo: {request.model_id}")

        hf_request = HFInferenceRequest(
            model_id=request.model_id,
            prompt=request.prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
            top_k=request.top_k
        )

        response = await huggingface_provider.generate_text(hf_request)

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando texto: {response.error}"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en generación: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-for-agent", response_model=HFInferenceResponse)
async def generate_for_agent(request: AgentGenerateRequest):
    """
    🎭 Generar texto optimizado por rol de agente

    Selecciona automáticamente el modelo óptimo según el rol del agente
    y el dominio científico.

    Roles disponibles:
    - **orchestrator**: Planificación estratégica → Meta-Llama-3.1-70B-Instruct
    - **bio_hypothesis**: Hipótesis biológicas → microsoft/biogpt
    - **physchem_coder**: Código científico → Qwen/Qwen2.5-Coder-32B-Instruct
    - **reviewer**: Revisión crítica → Meta-Llama-3.1-70B-Instruct
    - **publisher**: Generación de reportes → Mixtral-8x7B-Instruct
    - **scientific_reasoner**: Razonamiento científico → facebook/galactica-30b

    Ejemplo:
    ```json
    {
        "agent_role": "bio_hypothesis",
        "prompt": "Generate a hypothesis about CRISPR gene editing",
        "domain": "biology",
        "max_new_tokens": 800,
        "temperature": 0.65
    }
    ```
    """
    try:
        logger.info(f"🎭 Generando para agente: {request.agent_role} (dominio: {request.domain or 'general'})")

        response = await huggingface_provider.generate_for_agent(
            agent_role=request.agent_role,
            prompt=request.prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            domain=request.domain
        )

        if not response.success:
            raise HTTPException(
                status_code=500,
                detail=f"Error generando para agente: {response.error}"
            )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en generación para agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_specialized_models():
    """
    📋 Listar modelos especializados disponibles

    Retorna todos los modelos de Hugging Face configurados para
    investigación científica, organizados por categoría.
    """
    try:
        models_info = {
            "total_models": len(huggingface_provider.SPECIALIZED_MODELS) * 2,  # primary + fallback
            "agent_models": huggingface_provider.AGENT_MODEL_MAP,
            "specialized_by_domain": huggingface_provider.SPECIALIZED_MODELS,
            "description": {
                "microsoft/biogpt": "Modelo especializado en biología (entrenado con 15M papers PubMed)",
                "facebook/galactica-30b": "Conocimiento científico general (48M papers)",
                "Qwen/Qwen2.5-Coder-32B-Instruct": "Generación de código científico",
                "meta-llama/Meta-Llama-3.1-70B-Instruct": "Razonamiento general de alto nivel",
                "mistralai/Mixtral-8x7B-Instruct-v0.1": "Generación de texto científico",
                "allenai/scibert_scivocab_uncased": "Embeddings científicos",
                "stanford/biomedlm": "Medicina y biomedicina"
            }
        }

        return {
            "success": True,
            "message": f"Encontrados {models_info['total_models']} modelos especializados",
            "models": models_info
        }

    except Exception as e:
        logger.error(f"❌ Error listando modelos: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/by-domain/{domain}")
async def get_models_by_domain(domain: str):
    """
    🔬 Obtener modelos por dominio científico

    Retorna los modelos primarios y de respaldo para un dominio específico.

    Dominios disponibles:
    - biology
    - chemistry
    - physics
    - mathematics
    - medicine
    - general
    - code
    """
    try:
        if domain not in huggingface_provider.SPECIALIZED_MODELS:
            raise HTTPException(
                status_code=404,
                detail=f"Dominio '{domain}' no encontrado. Dominios disponibles: {list(huggingface_provider.SPECIALIZED_MODELS.keys())}"
            )

        models = huggingface_provider.SPECIALIZED_MODELS[domain]

        return {
            "success": True,
            "domain": domain,
            "models": models,
            "recommendation": f"Usa '{models['primary']}' para mejor rendimiento, '{models['fallback']}' como respaldo"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo modelos por dominio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models/by-agent/{agent_role}")
async def get_model_by_agent(agent_role: str):
    """
    🤖 Obtener modelo recomendado por rol de agente

    Retorna el modelo óptimo para un rol de agente específico.

    Roles disponibles:
    - orchestrator
    - bio_hypothesis
    - physchem_coder
    - reviewer
    - publisher
    - scientific_reasoner
    """
    try:
        if agent_role not in huggingface_provider.AGENT_MODEL_MAP:
            raise HTTPException(
                status_code=404,
                detail=f"Rol '{agent_role}' no encontrado. Roles disponibles: {list(huggingface_provider.AGENT_MODEL_MAP.keys())}"
            )

        model_id = huggingface_provider.AGENT_MODEL_MAP[agent_role]

        # Obtener dominio relacionado
        domain = "general"
        for d, models in huggingface_provider.SPECIALIZED_MODELS.items():
            if model_id in models.values():
                domain = d
                break

        return {
            "success": True,
            "agent_role": agent_role,
            "recommended_model": model_id,
            "domain": domain,
            "description": f"Modelo optimizado para el rol '{agent_role}' en dominio '{domain}'"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error obteniendo modelo por agente: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics():
    """
    📊 Obtener métricas de uso del servicio

    Retorna estadísticas de uso incluyendo:
    - Total de solicitudes
    - Tasa de éxito
    - Hits de caché
    - Tokens generados
    - Latencia promedio
    """
    try:
        metrics = huggingface_provider.get_metrics()

        return {
            "success": True,
            "message": "Métricas de Hugging Face Provider",
            "metrics": metrics,
            "cache_status": "enabled" if huggingface_provider.cache_enabled else "disabled",
            "api_key_configured": bool(huggingface_provider.api_key)
        }

    except Exception as e:
        logger.error(f"❌ Error obteniendo métricas: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache():
    """
    🗑️ Limpiar caché de respuestas

    Elimina todas las respuestas en caché. Útil para:
    - Forzar regeneración con nuevos parámetros
    - Liberar memoria
    - Testing
    """
    try:
        cache_count = len(huggingface_provider.cache)
        huggingface_provider.clear_cache()

        return {
            "success": True,
            "message": f"Caché limpiado exitosamente",
            "entries_cleared": cache_count
        }

    except Exception as e:
        logger.error(f"❌ Error limpiando caché: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection")
async def test_connection():
    """
    🔍 Probar conexión con Hugging Face API

    Realiza una solicitud de prueba para verificar:
    - Conectividad con la API
    - Validez del API key
    - Disponibilidad de modelos
    """
    try:
        # Probar con modelo ligero
        test_request = HFInferenceRequest(
            model_id="gpt2",  # Modelo pequeño para prueba rápida
            prompt="Test connection",
            max_new_tokens=10,
            temperature=0.7
        )

        response = await huggingface_provider.generate_text(test_request)

        if response.success:
            return {
                "success": True,
                "message": "✅ Conexión exitosa con Hugging Face API",
                "api_key_status": "✓ Configurado" if huggingface_provider.api_key else "✗ No configurado (usando modelos públicos)",
                "test_model": test_request.model_id,
                "latency_ms": response.latency_ms,
                "test_response": response.generated_text[:100]
            }
        else:
            raise HTTPException(
                status_code=503,
                detail=f"Fallo en prueba de conexión: {response.error}"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error en prueba de conexión: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_service_status():
    """
    📊 Obtener estado del servicio

    Retorna información general del servicio incluyendo:
    - Estado operacional
    - Modelos disponibles
    - Configuración
    - Estadísticas de uso
    """
    try:
        metrics = huggingface_provider.get_metrics()

        return {
            "success": True,
            "service": {
                "name": "Hugging Face Cloud Models",
                "status": "operational",
                "version": "1.0.0",
                "api_url": huggingface_provider.api_url
            },
            "configuration": {
                "cache_enabled": huggingface_provider.cache_enabled,
                "cache_ttl_seconds": huggingface_provider.cache_ttl,
                "max_retries": huggingface_provider.max_retries,
                "timeout_seconds": huggingface_provider.timeout,
                "rate_limit_per_minute": huggingface_provider.max_requests_per_minute,
                "api_key_configured": bool(huggingface_provider.api_key)
            },
            "models": {
                "total_specialized": len(huggingface_provider.SPECIALIZED_MODELS) * 2,
                "agent_models": len(huggingface_provider.AGENT_MODEL_MAP),
                "domains": list(huggingface_provider.SPECIALIZED_MODELS.keys()),
                "agents": list(huggingface_provider.AGENT_MODEL_MAP.keys())
            },
            "usage_stats": metrics,
            "capabilities": [
                "Generación de texto científico",
                "Modelos especializados por dominio",
                "Optimización por rol de agente",
                "Caché automático",
                "Rate limiting",
                "Fallback automático",
                "Métricas de performance"
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error obteniendo estado: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/domains")
async def list_domains():
    """
    🔬 Listar dominios científicos disponibles

    Retorna todos los dominios científicos soportados con sus
    modelos especializados.
    """
    try:
        domains_info = []

        for domain, models in huggingface_provider.SPECIALIZED_MODELS.items():
            domains_info.append({
                "domain": domain,
                "primary_model": models["primary"],
                "fallback_model": models["fallback"],
                "description": {
                    "biology": "Biología y ciencias de la vida",
                    "chemistry": "Química y ciencias moleculares",
                    "physics": "Física y astrofísica",
                    "mathematics": "Matemáticas y lógica formal",
                    "medicine": "Medicina y biomedicina",
                    "general": "Razonamiento científico general",
                    "code": "Generación de código científico"
                }.get(domain, "Dominio científico especializado")
            })

        return {
            "success": True,
            "message": f"Encontrados {len(domains_info)} dominios científicos",
            "domains": domains_info,
            "total_domains": len(domains_info)
        }

    except Exception as e:
        logger.error(f"❌ Error listando dominios: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents")
async def list_agent_roles():
    """
    🤖 Listar roles de agentes disponibles

    Retorna todos los roles de agentes del sistema multi-agente
    con sus modelos asociados.
    """
    try:
        agents_info = []

        agent_descriptions = {
            "orchestrator": "Planificación estratégica y descomposición de objetivos científicos",
            "bio_hypothesis": "Generación de hipótesis biológicas y médicas falsables",
            "physchem_coder": "Diseño experimental computacional y generación de código",
            "reviewer": "Revisión crítica y evaluación basada en evidencia",
            "publisher": "Síntesis y generación de reportes científicos",
            "scientific_reasoner": "Razonamiento científico profundo con conocimiento de papers"
        }

        for agent_role, model_id in huggingface_provider.AGENT_MODEL_MAP.items():
            agents_info.append({
                "agent_role": agent_role,
                "model_id": model_id,
                "description": agent_descriptions.get(agent_role, "Agente especializado"),
                "capabilities": {
                    "orchestrator": ["Planificación", "Delegación", "Coordinación"],
                    "bio_hypothesis": ["Hipótesis biológicas", "Predicciones testables", "Diseño experimental"],
                    "physchem_coder": ["Código Python", "Simulaciones", "Análisis computacional"],
                    "reviewer": ["Revisión crítica", "Evaluación de evidencia", "Identificación de debilidades"],
                    "publisher": ["Redacción científica", "Síntesis", "Formato académico"],
                    "scientific_reasoner": ["Razonamiento profundo", "Conocimiento científico", "Conexiones interdisciplinarias"]
                }.get(agent_role, [])
            })

        return {
            "success": True,
            "message": f"Encontrados {len(agents_info)} roles de agentes",
            "agents": agents_info,
            "total_agents": len(agents_info),
            "multi_agent_workflow": [
                "1. Orchestrator → Planificación",
                "2. Bio Hypothesis / Scientific Reasoner → Generación hipótesis",
                "3. PhysChem Coder → Diseño experimental",
                "4. Reviewer → Revisión crítica",
                "5. Publisher → Reporte final"
            ]
        }

    except Exception as e:
        logger.error(f"❌ Error listando agentes: {e}")
        raise HTTPException(status_code=500, detail=str(e))
