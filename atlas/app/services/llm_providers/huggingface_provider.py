"""
Hugging Face Inference API Provider for AXIOM Atlas

Este servicio integra modelos especializados de Hugging Face para el sistema multi-agente.
Soporta modelos grandes a través de la Inference API (serverless) y Dedicated Endpoints.

Modelos especializados recomendados (actualizado 2025-11):
- deepseek-ai/DeepSeek-V3: Razonamiento y planificación de última generación (MoE 671B → 37B activos)
- Qwen/Qwen2.5-72B-Instruct: Conocimiento científico y matemático con contexto de 128K tokens
- Qwen/Qwen2.5-Coder-32B-Instruct: Código científico y automatización experimental
- meta-llama/Meta-Llama-3.1-405B-Instruct: Redacción científica premium y síntesis avanzada
- DeepSeek-R1-Distill-Qwen-32B: Deliberación reflexiva compacta (fallback para cargas medianas)

Características:
- Rate limiting inteligente
- Fallback automático
- Caché de respuestas
- Manejo de errores robusto
- Métricas de performance
"""

import os
import time
import logging
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import asyncio

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class HFModelCategory(str, Enum):
    """Categorías de modelos de Hugging Face"""
    TEXT_GENERATION = "text-generation"
    FEATURE_EXTRACTION = "feature-extraction"
    TEXT_CLASSIFICATION = "text-classification"
    CONVERSATIONAL = "conversational"


@dataclass
class HFModelConfig:
    """Configuración de un modelo de Hugging Face"""
    model_id: str
    category: HFModelCategory
    max_tokens: int = 2048
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    use_cache: bool = True


class HFInferenceRequest(BaseModel):
    """Solicitud para Hugging Face Inference API"""
    model_id: str = Field(..., description="ID del modelo en Hugging Face")
    prompt: str = Field(..., description="Prompt para el modelo")
    max_new_tokens: int = Field(512, ge=1, le=4096, description="Máximo de tokens a generar")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperatura para sampling")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling")
    top_k: int = Field(50, ge=1, le=100, description="Top-K sampling")
    repetition_penalty: float = Field(1.1, ge=1.0, le=2.0, description="Penalización por repetición")
    return_full_text: bool = Field(False, description="Retornar texto completo o solo generado")


class HFInferenceResponse(BaseModel):
    """Respuesta de Hugging Face Inference API"""
    success: bool = Field(..., description="Si la generación fue exitosa")
    generated_text: str = Field("", description="Texto generado")
    model_id: str = Field(..., description="Modelo utilizado")
    tokens_generated: Optional[int] = Field(None, description="Número de tokens generados")
    latency_ms: Optional[float] = Field(None, description="Latencia en milisegundos")
    error: Optional[str] = Field(None, description="Mensaje de error si falla")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata adicional")


class HuggingFaceProvider:
    """
    Proveedor de modelos Hugging Face para AXIOM Atlas

    Características:
    - Inference API gratuita para modelos públicos
    - Soporte para Dedicated Endpoints (PRO)
    - Rate limiting automático
    - Sistema de caché
    - Fallback a modelos alternativos
    """

    # Modelos especializados por dominio científico
    # OPTIMIZADOS: Solo modelos VERIFICADOS disponibles en Inference API 2025
    SPECIALIZED_MODELS = {
        "biology": {
            "primary": "Qwen/Qwen2.5-72B-Instruct",  # Hipótesis biomédicas con 72B parámetros
            "fallback": "meta-llama/Meta-Llama-3.1-70B-Instruct"
        },
        "chemistry": {
            "primary": "deepseek-ai/DeepSeek-V3",  # MoE 37B activos optimizado para ciencias físicas
            "fallback": "Qwen/Qwen2.5-Math-32B-Instruct"
        },
        "physics": {
            "primary": "deepseek-ai/DeepSeek-V3",  # Benchmarks top en física/matemáticas (DeepSeek, 2024)
            "fallback": "Qwen/Qwen2.5-Math-72B-Instruct"
        },
        "mathematics": {
            "primary": "Qwen/Qwen2.5-Math-72B-Instruct",  # Especializado en matemáticas avanzadas
            "fallback": "deepseek-ai/DeepSeek-V3"
        },
        "medicine": {
            "primary": "Qwen/Qwen2.5-72B-Instruct",  # Conocimiento clínico + long context
            "fallback": "meta-llama/Meta-Llama-3.1-70B-Instruct"
        },
        "general": {
            "primary": "meta-llama/Meta-Llama-3.1-405B-Instruct",  # Modelo Frontier 405B para síntesis
            "fallback": "deepseek-ai/DeepSeek-V3"
        },
        "code": {
            "primary": "Qwen/Qwen2.5-Coder-32B-Instruct",  # Código científico y herramientas de laboratorio
            "fallback": "DeepSeek-R1-Distill-Qwen-32B"
        }
    }

    # Configuraciones predefinidas por rol de agente
    # OPTIMIZADOS: Máxima potencia con modelos VERIFICADOS disponibles
    AGENT_MODEL_MAP = {
        "orchestrator": "deepseek-ai/DeepSeek-V3",  # Planner con razonamiento multi-token (DeepSeek, 2024)
        "bio_hypothesis": "Qwen/Qwen2.5-72B-Instruct",  # Hipótesis biomédicas con 72B params
        "physchem_coder": "Qwen/Qwen2.5-Coder-32B-Instruct",  # Código experimental y simulaciones
        "reviewer": "deepseek-ai/DeepSeek-V3",  # Evaluación crítica con distillation R1
        "publisher": "meta-llama/Meta-Llama-3.1-405B-Instruct",  # Síntesis y redacción frontier 405B
        "scientific_reasoner": "Qwen/Qwen2.5-Math-72B-Instruct"  # Pruebas matemáticas y física teórica
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: str = "https://router.huggingface.co/v1",
        cache_enabled: bool = True,
        max_retries: int = 3,
        timeout: int = 180  # Aumentado de 60s a 180s para modelos grandes (Qwen-72B)
    ):
        """
        Inicializar proveedor de Hugging Face (API 2025)

        Args:
            api_key: API key de Hugging Face (opcional)
            api_url: URL base de la Inference API (nueva: router.huggingface.co/v1)
            cache_enabled: Habilitar caché de respuestas
            max_retries: Número máximo de reintentos
            timeout: Timeout en segundos
        """
        # Obtener API key de forma segura (prioridad: parámetro > almacenamiento seguro > env)
        if api_key:
            self.api_key = api_key
        else:
            try:
                from app.config.api_keys_manager import get_api_key
                self.api_key = get_api_key("HUGGINGFACE") or os.getenv("HUGGINGFACE_API_KEY", "")
                if self.api_key and self.api_key != os.getenv("HUGGINGFACE_API_KEY", ""):
                    logger.info("🔐 Usando API key desde almacenamiento seguro cifrado")
            except Exception as e:
                logger.debug(f"Almacenamiento seguro no disponible, usando env: {e}")
                self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")

        self.api_url = api_url
        self.cache_enabled = cache_enabled
        self.max_retries = max_retries
        self.timeout = timeout

        # Inicializar InferenceClient oficial (nuevo en 2025)
        try:
            from huggingface_hub import InferenceClient
            self.hf_client = InferenceClient(token=self.api_key) if self.api_key else None
            logger.info("✅ InferenceClient inicializado con API 2025")
        except ImportError:
            self.hf_client = None
            logger.warning("⚠️ huggingface_hub no disponible. Usando httpx directo.")

        # Sistema de caché simple
        self.cache: Dict[str, Any] = {}
        self.cache_ttl = 3600  # 1 hora

        # Rate limiting
        self.request_history: List[float] = []
        self.max_requests_per_minute = 60  # Límite conservador

        # Métricas
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "total_tokens": 0,
            "total_latency_ms": 0.0
        }

        if not HTTPX_AVAILABLE:
            logger.warning("httpx no está instalado. Usando requests como fallback.")

        # Persistent client para evitar warnings de cleanup
        self._http_client: Optional[Any] = None  # httpx.AsyncClient cuando disponible

        logger.info(f"✅ HuggingFaceProvider inicializado (API key: {'✓' if self.api_key else '✗'})")

    def _get_cache_key(self, model_id: str, prompt: str, params: Dict[str, Any]) -> str:
        """Generar clave de caché única"""
        cache_data = f"{model_id}:{prompt}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(cache_data.encode()).hexdigest()

    def _check_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Verificar si hay respuesta en caché"""
        if not self.cache_enabled:
            return None

        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            # Verificar TTL
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                self.metrics["cache_hits"] += 1
                logger.info(f"💾 Cache hit para key: {cache_key[:8]}...")
                return cached_data["response"]
            else:
                # Eliminar entrada expirada
                del self.cache[cache_key]

        return None

    def _save_to_cache(self, cache_key: str, response: Dict[str, Any]):
        """Guardar respuesta en caché"""
        if self.cache_enabled:
            self.cache[cache_key] = {
                "response": response,
                "timestamp": time.time()
            }

    def _check_rate_limit(self) -> bool:
        """Verificar límite de tasa de solicitudes"""
        current_time = time.time()

        # Limpiar solicitudes antiguas (> 1 minuto)
        self.request_history = [
            req_time for req_time in self.request_history
            if current_time - req_time < 60
        ]

        # Verificar si estamos bajo el límite
        if len(self.request_history) < self.max_requests_per_minute:
            self.request_history.append(current_time)
            return True

        return False

    def _wait_for_rate_limit(self):
        """Esperar hasta que se pueda hacer una solicitud"""
        if not self._check_rate_limit():
            oldest_request = min(self.request_history)
            wait_time = 60 - (time.time() - oldest_request) + 1

            if wait_time > 0:
                logger.info(f"⏳ Rate limit alcanzado. Esperando {wait_time:.1f}s...")
                time.sleep(wait_time)

        self._check_rate_limit()

    def get_optimal_model(
        self,
        domain: str = "general",
        agent_role: Optional[str] = None,
        use_fallback: bool = False
    ) -> str:
        """
        Obtener modelo óptimo según dominio o rol de agente

        Args:
            domain: Dominio científico
            agent_role: Rol del agente (orchestrator, bio_hypothesis, etc.)
            use_fallback: Usar modelo de respaldo

        Returns:
            ID del modelo en Hugging Face
        """
        # Prioridad 1: Modelo específico de rol
        if agent_role and agent_role in self.AGENT_MODEL_MAP:
            return self.AGENT_MODEL_MAP[agent_role]

        # Prioridad 2: Modelo especializado por dominio
        if domain in self.SPECIALIZED_MODELS:
            key = "fallback" if use_fallback else "primary"
            return self.SPECIALIZED_MODELS[domain][key]

        # Prioridad 3: Modelo general
        key = "fallback" if use_fallback else "primary"
        return self.SPECIALIZED_MODELS["general"][key]

    async def _generate_with_client(
        self,
        request: HFInferenceRequest,
        start_time: float,
        cache_key: str
    ) -> HFInferenceResponse:
        """
        Generar texto usando InferenceClient oficial (API 2025)

        Args:
            request: Solicitud de inferencia
            start_time: Tiempo de inicio para métricas
            cache_key: Clave de caché

        Returns:
            Respuesta con texto generado
        """
        try:
            # Usar chat_completion si el modelo lo soporta
            response = self.hf_client.chat_completion(
                messages=[{"role": "user", "content": request.prompt}],
                model=request.model_id,
                max_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=request.top_p
            )

            # Extraer texto generado
            generated_text = response.choices[0].message.content

            # Calcular latencia
            latency_ms = (time.time() - start_time) * 1000

            # Estimar tokens
            tokens_generated = len(generated_text.split())

            # Construir respuesta
            success_response = HFInferenceResponse(
                success=True,
                generated_text=generated_text,
                model_id=request.model_id,
                tokens_generated=tokens_generated,
                latency_ms=latency_ms,
                metadata={
                    "method": "InferenceClient",
                    "cache_used": False
                }
            )

            # Guardar en caché
            self._save_to_cache(cache_key, success_response.model_dump())

            # Actualizar métricas
            self.metrics["successful_requests"] += 1
            self.metrics["total_tokens"] += tokens_generated
            self.metrics["total_latency_ms"] += latency_ms

            logger.info(
                f"✅ Generación exitosa con InferenceClient - {request.model_id} "
                f"({tokens_generated} tokens, {latency_ms:.0f}ms)"
            )

            return success_response

        except Exception as e:
            logger.warning(f"❌ InferenceClient error: {e}")
            raise

    async def generate_text(
        self,
        request: HFInferenceRequest,
        use_fallback: bool = False
    ) -> HFInferenceResponse:
        """
        Generar texto usando Hugging Face Inference API

        Args:
            request: Solicitud de inferencia
            use_fallback: Usar modelo de respaldo si falla

        Returns:
            Respuesta con texto generado
        """
        # --- Security Guard: Prompt Injection & Misuse Check ---
        try:
            from app.security.misuse_guard import require_safe_operation
            require_safe_operation(
                operation="hf_generation",
                content=request.inputs,
                domain="llm_inference",
                tool_name="HuggingFaceProvider"
            )
        except Exception as e:
            from app.core.bootstrap_logging import logger
            logger.warning(f"HF request blocked by security guard: {e}")
            return HFInferenceResponse(
                generated_text="",
                error=f"Security Guard blocked prompt: {e}"
            )
        # -------------------------------------------------------

        start_time = time.time()
        self.metrics["total_requests"] += 1

        # Verificar caché
        cache_key = self._get_cache_key(
            request.model_id,
            request.prompt,
            {
                "max_new_tokens": request.max_new_tokens,
                "temperature": request.temperature,
                "top_p": request.top_p,
                "top_k": request.top_k
            }
        )

        cached_response = self._check_cache(cache_key)
        if cached_response:
            return HFInferenceResponse(**cached_response)

        # Rate limiting
        self._wait_for_rate_limit()

        # Usar InferenceClient si está disponible (preferido en API 2025)
        if self.hf_client:
            try:
                result = await self._generate_with_client(request, start_time, cache_key)
                return result
            except Exception as e:
                logger.warning(f"⚠️ InferenceClient falló, intentando con httpx directo: {e}")
                # Continuar con httpx como fallback

        # Construir URL y headers (formato chat compatible con API 2025)
        url = f"{self.api_url}/chat/completions"
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # Payload formato OpenAI-compatible (nuevo en API 2025)
        payload = {
            "model": request.model_id,
            "messages": [
                {"role": "user", "content": request.prompt}
            ],
            "max_tokens": request.max_new_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "stream": False
        }

        # Intentar generación con reintentos
        for attempt in range(self.max_retries):
            try:
                if HTTPX_AVAILABLE:
                    # Usar cliente persistente si existe, sino crear uno temporal
                    if self._http_client:
                        response = await self._http_client.post(url, headers=headers, json=payload)
                        response.raise_for_status()
                        result = response.json()
                    else:
                        import httpx as httpx_module
                        async with httpx_module.AsyncClient(timeout=self.timeout) as client:
                            response = await client.post(url, headers=headers, json=payload)
                            response.raise_for_status()
                            result = response.json()
                else:
                    # Fallback a requests síncronos
                    import requests
                    response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
                    response.raise_for_status()
                    result = response.json()

                # Procesar respuesta (formato OpenAI-compatible de API 2025)
                if isinstance(result, dict):
                    # Formato chat completions
                    if "choices" in result and len(result["choices"]) > 0:
                        generated_text = result["choices"][0].get("message", {}).get("content", "")
                    # Formato antiguo (fallback)
                    elif "generated_text" in result:
                        generated_text = result.get("generated_text", "")
                    else:
                        generated_text = str(result)
                elif isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get("generated_text", "")
                else:
                    generated_text = str(result)

                # Calcular latencia
                latency_ms = (time.time() - start_time) * 1000

                # Estimar tokens generados (aproximación)
                tokens_generated = len(generated_text.split())

                # Construir respuesta exitosa
                success_response = HFInferenceResponse(
                    success=True,
                    generated_text=generated_text,
                    model_id=request.model_id,
                    tokens_generated=tokens_generated,
                    latency_ms=latency_ms,
                    metadata={
                        "attempt": attempt + 1,
                        "cache_used": False
                    }
                )

                # Guardar en caché
                self._save_to_cache(cache_key, success_response.model_dump())

                # Actualizar métricas
                self.metrics["successful_requests"] += 1
                self.metrics["total_tokens"] += tokens_generated
                self.metrics["total_latency_ms"] += latency_ms

                logger.info(
                    f"✅ Generación exitosa con {request.model_id} "
                    f"({tokens_generated} tokens, {latency_ms:.0f}ms)"
                )

                return success_response

            except Exception as e:
                logger.warning(
                    f"⚠️ Intento {attempt + 1}/{self.max_retries} falló para {request.model_id}: {e}"
                )

                if attempt < self.max_retries - 1:
                    # Esperar antes del siguiente intento (backoff exponencial)
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                    continue

                # Último intento: intentar con modelo de respaldo
                if not use_fallback and attempt == self.max_retries - 1:
                    logger.info(f"🔄 Intentando con modelo de respaldo...")

                    # Obtener dominio del modelo original
                    domain = "general"
                    for d, models in self.SPECIALIZED_MODELS.items():
                        if request.model_id in models.values():
                            domain = d
                            break

                    fallback_model = self.get_optimal_model(domain=domain, use_fallback=True)
                    fallback_request = request.model_copy()
                    fallback_request.model_id = fallback_model

                    return await self.generate_text(fallback_request, use_fallback=True)

                # Error final
                self.metrics["failed_requests"] += 1

                return HFInferenceResponse(
                    success=False,
                    generated_text="",
                    model_id=request.model_id,
                    error=str(e),
                    metadata={"attempts": self.max_retries}
                )

        # No debería llegar aquí, pero por seguridad
        return HFInferenceResponse(
            success=False,
            generated_text="",
            model_id=request.model_id,
            error="Max retries exceeded",
            metadata={"attempts": self.max_retries}
        )

    async def generate_for_agent(
        self,
        agent_role: str,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        domain: Optional[str] = None
    ) -> HFInferenceResponse:
        """
        Generar texto para un rol de agente específico

        Args:
            agent_role: Rol del agente (orchestrator, bio_hypothesis, etc.)
            prompt: Prompt para el modelo
            max_new_tokens: Máximo de tokens a generar
            temperature: Temperatura para sampling
            domain: Dominio científico opcional

        Returns:
            Respuesta con texto generado
        """
        # --- Security Guard: Prompt Injection & Misuse Check ---
        try:
            from app.security.misuse_guard import require_safe_operation
            require_safe_operation(
                operation="hf_agent_generation",
                content=prompt,
                domain=domain or "llm_inference",
                tool_name="HuggingFaceProvider"
            )
        except Exception as e:
            from app.core.bootstrap_logging import logger
            logger.warning(f"HF request blocked by security guard (agent role {agent_role}): {e}")
            return HFInferenceResponse(
                generated_text="",
                error=f"Security Guard blocked prompt: {e}"
            )
        # -------------------------------------------------------

        model_id = self.get_optimal_model(domain=domain or "general", agent_role=agent_role)

        request = HFInferenceRequest(
            model_id=model_id,
            prompt=prompt,
            max_new_tokens=max_new_tokens,
            temperature=temperature
        )

        logger.info(f"🤖 Generando para rol '{agent_role}' con modelo {model_id}")

        return await self.generate_text(request)

    def get_metrics(self) -> Dict[str, Any]:
        """Obtener métricas de uso"""
        avg_latency = (
            self.metrics["total_latency_ms"] / self.metrics["successful_requests"]
            if self.metrics["successful_requests"] > 0
            else 0
        )

        return {
            "total_requests": self.metrics["total_requests"],
            "successful_requests": self.metrics["successful_requests"],
            "failed_requests": self.metrics["failed_requests"],
            "success_rate": (
                self.metrics["successful_requests"] / self.metrics["total_requests"] * 100
                if self.metrics["total_requests"] > 0
                else 0
            ),
            "cache_hits": self.metrics["cache_hits"],
            "cache_hit_rate": (
                self.metrics["cache_hits"] / self.metrics["total_requests"] * 100
                if self.metrics["total_requests"] > 0
                else 0
            ),
            "total_tokens": self.metrics["total_tokens"],
            "average_latency_ms": avg_latency
        }

    def clear_cache(self):
        """Limpiar caché de respuestas"""
        self.cache.clear()
        logger.info("🗑️ Caché limpiado")

    async def __aenter__(self):
        """Context manager entry"""
        if HTTPX_AVAILABLE and self._http_client is None:
            import httpx as httpx_module
            self._http_client = httpx_module.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cierre limpio de recursos"""
        await self.aclose()

    async def aclose(self):
        """Cerrar recursos async de forma limpia"""
        if self._http_client:
            try:
                await self._http_client.aclose()
                logger.info("✅ HTTP client cerrado limpiamente")
            except Exception as e:
                logger.warning(f"⚠️ Error cerrando HTTP client: {e}")
            finally:
                self._http_client = None


# Instancia global del proveedor
huggingface_provider = HuggingFaceProvider()
