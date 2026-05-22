"""
Ollama Cloud Integration Service

Este servicio integra con Ollama Cloud para generar hipótesis científicas reales
usando modelos de IA avanzados en lugar de respuestas mock.

Modelos recomendados:
- deepseek-r1: Para razonamiento científico profundo
- qwen3: Para ciencias generales y matemáticas
- llama3.1: Como modelo de respaldo confiable
- gemma3: Para tareas específicas y eficiencia
"""

import json
import logging
import os
import time
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import asyncio

import httpx

logger = logging.getLogger(__name__)

class HypothesisRequest(BaseModel):
    """Estructura de solicitud para generación de hipótesis"""
    research_question: str = Field(..., description="Pregunta de investigación científica")
    domain: str = Field(..., description="Dominio científico (materials_science, quantum_computing, etc.)")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Contexto adicional y parámetros")
    model_preference: Optional[str] = Field(default=None, description="Modelo específico a usar")

class HypothesisResponse(BaseModel):
    """Estructura de respuesta de hipótesis generada"""
    hypothesis_text: str = Field(..., description="Texto de la hipótesis científica")
    reasoning: str = Field(..., description="Razonamiento científico detrás de la hipótesis")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Nivel de confianza en la hipótesis")
    testable_predictions: List[str] = Field(..., description="Predicciones verificables")
    methodology_suggestions: List[str] = Field(..., description="Sugerencias metodológicas")
    related_literature: List[str] = Field(..., description="Literatura relacionada sugerida")

class OllamaHypothesisService:
    """Servicio para generar hipótesis científicas usando Ollama Cloud"""

    # Domain-specific model mapping (prefer local aliases, fallback via AVAILABLE_MODELS)
    DOMAIN_MODEL_MAP = {
        "quantum_computing": "deepseek-r1",
        "mathematics": "deepseek-r1",
        "physics": "deepseek-r1",
        "materials_science": "qwen3",
        "chemistry": "qwen3",
        "biology": "qwen3",
        "drug_discovery": "qwen3",
        "machine_learning": "qwen3",
        "climate_science": "gemma3",
        "geoscience": "gemma3"
    }

    # Fallback model alias (se resuelve a variantes locales/cloud según disponibilidad)
    FALLBACK_MODEL_ALIAS = "deepseek-r1"

    # Modelos disponibles actualmente (intentamos modelos locales antes de recurrir a la nube)
    AVAILABLE_MODELS = {
        "deepseek-r1": [
            "deepseek-r1:7b",
            "deepseek-r1",
            "deepseek-v3.1:671b-cloud"
        ],
        "qwen3": [
            "qwen3:72b",
            "qwen3",
            "qwen3-coder:480b-cloud"
        ],
        "llama3.1": [
            "llama3.1",
            "llama3.1:8b-instruct",
            "llama3.1:70b",
            "llama3.1:405b"
        ],
        "gemma3": [
            "gemma3:27b",
            "gemma3",
            "gemma3-instruct:405b-cloud"
        ]
    }

    # Tamaños aproximados de contexto por modelo
    CONTEXT_LIMITS = {
        "deepseek-r1": 4096,
        "qwen3": 8192,
        "llama3.1": 8192,
        "gemma3": 4096
    }

    def __init__(self, base_url: Optional[str] = None):
        """Initialize the Ollama service with connection details and rate limiting."""
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.api_key = os.environ.get("OLLAMA_API_KEY", "") or os.environ.get("OLLAMA_CLOUD_API_KEY", "")
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        self._async_client: Optional[httpx.AsyncClient] = None
        self._sync_client: Optional[httpx.Client] = None
        self._headers = headers
        self.request_count = 0
        self.last_reset_time = time.time()
        self.max_requests_per_minute = 10  # Límite conservador para evitar rate limiting
        self.request_history = []
        logger.info("OllamaHypothesisService initialized - Host: %s, Auth: %s", self.base_url, "yes" if self.api_key else "no")

    def _get_sync_client(self) -> httpx.Client:
        if self._sync_client is None or self._sync_client.is_closed:
            self._sync_client = httpx.Client(base_url=self.base_url, headers=self._headers, timeout=180.0)
        return self._sync_client

    async def _get_async_client(self) -> httpx.AsyncClient:
        if self._async_client is None or self._async_client.is_closed:
            self._async_client = httpx.AsyncClient(base_url=self.base_url, headers=self._headers, timeout=180.0)
        return self._async_client

    def _check_rate_limit(self) -> bool:
        """Verifica si podemos hacer una petición sin exceder el límite.

        Returns:
            True si podemos hacer la petición, False si hay que esperar.
        """
        current_time = time.time()

        # Limpiar peticiones antigas (más de 1 minuto)
        self.request_history = [
            req_time for req_time in self.request_history
            if current_time - req_time < 60
        ]

        # Verificar si estamos bajo el límite
        if len(self.request_history) < self.max_requests_per_minute:
            self.request_history.append(current_time)
            return True

        return False

    def _wait_for_rate_limit(self) -> None:
        """Espera hasta que se pueda hacer una petición sin exceder el límite."""
        if not self._check_rate_limit():
            # Calcular tiempo de espera hasta la próxima ventana disponible
            oldest_request = min(self.request_history)
            wait_time = 60 - (time.time() - oldest_request) + 1  # +1 segundo de margen

            if wait_time > 0:
                logger.info("Rate limit alcanzado. Esperando %.1f segundos...", wait_time)
                time.sleep(wait_time)

        # Verificar nuevamente después de esperar
        self._check_rate_limit()

    def get_optimal_model(self, domain: str, request_complexity: str = "medium") -> str:
        """Selecciona el modelo óptimo según dominio y complejidad.

        Args:
            domain: Dominio científico objetivo.
            request_complexity: Complejidad de la solicitud (simple, medium, complex).

        Returns:
            Nombre del modelo recomendado.
        """
        preferred_alias = self.DOMAIN_MODEL_MAP.get(domain, self.FALLBACK_MODEL_ALIAS)

        # Para solicitudes complejas, preferir modelos de razonamiento profundo
        if request_complexity == "complex" and domain in ["quantum_computing", "mathematics", "physics"]:
            preferred_alias = "deepseek-r1"

        return preferred_alias

    def _get_available_model(self, preferred_model: str) -> str:
        """Obtiene un modelo disponible considerando la preferencia.

        Args:
            preferred_model: Modelo preferido o alias.

        Returns:
            Nombre del modelo disponible en la instancia de Ollama.
        """
        resolved_alias = preferred_model or self.FALLBACK_MODEL_ALIAS

        available_models: List[str] = []
        try:
            resp = self._get_sync_client().get("/api/tags")
            if resp.status_code == 200:
                available_models = [model.get("name") or model.get("model") for model in resp.json().get("models", [])]
        except Exception as e:
            logger.warning("No se pudo verificar modelos disponibles: %s", e)

        # Si el usuario pasa un modelo exacto y está disponible, úsalo directamente
        if resolved_alias in available_models:
            return resolved_alias

        # Resolver alias a modelo disponible conocido
        if resolved_alias in self.AVAILABLE_MODELS:
            for model_option in self.AVAILABLE_MODELS[resolved_alias]:
                if model_option in available_models:
                    return model_option
            # Si no encontramos coincidencia local, devolver primera opción como fallback controlado
            return self.AVAILABLE_MODELS[resolved_alias][0]

        # Último recurso: utilizar fallback configurado
        fallback_options = self.AVAILABLE_MODELS.get(self.FALLBACK_MODEL_ALIAS, ["llama3.1"])
        return fallback_options[0]

    def _create_scientific_prompt(self, request: HypothesisRequest) -> str:
        """
        Crea un prompt optimizado para generación de hipótesis científicas

        Args:
            request: Solicitud de hipótesis

        Returns:
            Prompt estructurado para el modelo
        """
        prompt_template = f"""
Eres un científico experto en {request.domain} con amplio conocimiento en metodología científica.

TAREA: Generar una hipótesis científica rigurosa y bien fundamentada.

PREGUNTA DE INVESTIGACIÓN: {request.research_question}

DOMINIO CIENTÍFICO: {request.domain}

CONTEXTO ADICIONAL: {json.dumps(request.context, indent=2) if request.context else "No especificado"}

INSTRUCCIONES:
1. Genera una hipótesis específica, testeable y falsificable
2. Proporciona razonamiento científico sólido basado en conocimiento actual
3. Sugiere predicciones verificables experimentalmente
4. Recomienda metodologías de investigación apropiadas
5. Referencias literatura relevante del campo

FORMATO DE RESPUESTA (JSON válido):
{{
    "hypothesis_text": "Hipótesis científica clara y concisa",
    "reasoning": "Razonamiento científico detallado con base teórica",
    "confidence": 0.85,
    "testable_predictions": [
        "Predicción específica 1",
        "Predicción específica 2",
        "Predicción específica 3"
    ],
    "methodology_suggestions": [
        "Metodología experimental 1",
        "Metodología experimental 2",
        "Metodología de análisis de datos"
    ],
    "related_literature": [
        "Referencia o área de estudio 1",
    "Referencia o área de estudio 2",
        "Referencia o área de estudio 3"
    ]
}}

IMPORTANTE: Responde ÚNICAMENTE con el JSON válido, sin texto adicional.
"""
        return prompt_template.strip()

    async def generate_hypothesis(self, request: HypothesisRequest) -> HypothesisResponse:
        """
        Genera una hipótesis científica usando Ollama Cloud con rate limiting

        Args:
            request: Solicitud de hipótesis científica

        Returns:
            Respuesta con hipótesis generada

        Raises:
            Exception: Si hay error en la comunicación con Ollama
        """
        try:
            # Verificar rate limiting antes de hacer la petición
            self._wait_for_rate_limit()

            # Seleccionar modelo óptimo
            preferred = request.model_preference or self.get_optimal_model(request.domain)
            model = self._get_available_model(preferred)

            # Crear prompt científico
            prompt = self._create_scientific_prompt(request)

            logger.info("Generando hipótesis para dominio '%s' usando modelo '%s'", request.domain, model)

            # Generar respuesta usando Ollama
            client = await self._get_async_client()
            resp = await client.post(
                "/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "format": "json",
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_predict": 2048,
                        "repeat_penalty": 1.1,
                        "seed": None,
                    },
                    "stream": False,
                },
            )
            resp.raise_for_status()
            response = resp.json()
            response_text = (response.get("response") or "").strip()

            # Parsear respuesta JSON
            try:
                hypothesis_data = json.loads(response_text)
                logger.info("Hipótesis generada exitosamente con confianza: %s", hypothesis_data.get('confidence', 'N/A'))

                # Validar y crear respuesta estructurada
                return HypothesisResponse(**hypothesis_data)

            except json.JSONDecodeError as e:
                logger.error("Error parseando JSON de Ollama: %s", e)
                logger.error("Respuesta cruda: %s", response_text)

                # Fallback: extraer información básica de texto plano
                return self._create_fallback_hypothesis(request, response_text)

        except Exception as e:
            logger.error("Error generando hipótesis con Ollama: %s", e)

            # Fallback completo: generar hipótesis básica
            return self._create_emergency_fallback_hypothesis(request)

    def _create_fallback_hypothesis(self, request: HypothesisRequest, raw_response: str) -> HypothesisResponse:
        """
        Crea una hipótesis de respaldo cuando falla el parsing JSON

        Args:
            request: Solicitud original
            raw_response: Respuesta cruda del modelo

        Returns:
            Hipótesis estructurada extraída del texto
        """
        logger.warning("Usando fallback: extrayendo información de texto plano")

        # Extraer información básica del texto
        hypothesis_text = raw_response[:500] if raw_response else f"Hipótesis sobre: {request.research_question}"

        return HypothesisResponse(
            hypothesis_text=hypothesis_text,
            reasoning=f"Generado para dominio {request.domain} con modelo Ollama",
            confidence=0.6,  # Confianza reducida para fallback
            testable_predictions=[
                f"Experimento exploratorio en {request.domain}",
                f"Análisis de datos relacionado con {request.research_question}",
                "Validación mediante revisión de literatura"
            ],
            methodology_suggestions=[
                f"Revisión sistemática en {request.domain}",
                "Diseño experimental controlado",
                "Análisis estadístico apropiado"
            ],
            related_literature=[
                f"Literatura en {request.domain}",
                "Metodología científica aplicada",
                "Estudios previos relacionados"
            ]
        )

    def _create_emergency_fallback_hypothesis(self, request: HypothesisRequest) -> HypothesisResponse:
        """
        Crea una hipótesis de emergencia cuando falla completamente Ollama

        Args:
            request: Solicitud original

        Returns:
            Hipótesis básica estructurada
        """
        logger.error("Usando emergency fallback: generando hipótesis básica")

        return HypothesisResponse(
            hypothesis_text=f"Hipótesis exploratoria: {request.research_question} puede ser investigada mediante métodos experimentales en {request.domain}",
            reasoning=f"Esta hipótesis se basa en la necesidad de investigar {request.research_question} dentro del contexto de {request.domain}",
            confidence=0.4,  # Baja confianza para fallback de emergencia
            testable_predictions=[
                f"Observación de fenómenos relacionados con {request.research_question}",
                f"Medición de variables relevantes en {request.domain}",
                "Comparación con datos existentes"
            ],
            methodology_suggestions=[
                "Revisión de literatura previa",
                "Diseño de experimento piloto",
                "Recopilación de datos preliminares"
            ],
            related_literature=[
                f"Fundamentos de {request.domain}",
                "Metodología de investigación científica",
                "Estudios exploratorios relacionados"
            ]
        )

    async def check_model_availability(self, model: str) -> bool:
        """
        Verifica si un modelo está disponible en Ollama

        Args:
            model: Nombre del modelo a verificar

        Returns:
            True si el modelo está disponible
        """
        try:
            client = await self._get_async_client()
            resp = await client.get("/api/tags")
            if resp.status_code == 200:
                available_models = [m.get('model') or m.get('name') for m in resp.json().get('models', [])]
                return model in available_models
            return False
        except Exception as e:
            logger.error("Error verificando disponibilidad del modelo %s: %s", model, e)
            return False

    async def get_available_models(self) -> List[str]:
        """
        Obtiene lista de modelos disponibles en Ollama

        Returns:
            Lista de nombres de modelos disponibles
        """
        try:
            client = await self._get_async_client()
            resp = await client.get("/api/tags")
            if resp.status_code == 200:
                return [m.get('model') or m.get('name') for m in resp.json().get('models', [])]
            return []
        except Exception as e:
            logger.error("Error obteniendo modelos disponibles: %s", e)
            return []

# Instancia global del servicio
ollama_service = OllamaHypothesisService()