"""
Multi-Model Hypothesis Generation Service

Este servicio integra múltiples proveedores de LLMs para generar hipótesis
científicas de alta calidad mediante consensus voting y validación cruzada.

Proveedores soportados:
- Ollama (local): deepseek-r1, qwen3, llama3.1
- HuggingFace Inference API: Galactica, BioGPT, SciBERT
- Groq: llama3-70b (ultra-rápido)
- Together AI: Mixtral, Llama-3-70b

Estrategia:
1. Generación paralela en 3-5 modelos
2. Consensus voting para identificar insights comunes
3. Refinamiento usando el mejor modelo
4. Validación de testabilidad y fundamentación
"""

import asyncio
import json
import os
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Set

import httpx
from pydantic import BaseModel, Field

from app.services.ollama_service import HypothesisRequest, HypothesisResponse, ollama_service
from app.core.bootstrap_logging import logger

# Configuración de timeouts y rate limits
DEFAULT_TIMEOUT = 30.0
MAX_PARALLEL_REQUESTS = 5
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"


class ModelProvider(str, Enum):
    """Proveedores de modelos LLM"""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    GROQ = "groq"
    TOGETHER = "together"


class ModelTier(str, Enum):
    """Niveles de modelos por capacidad"""
    FAST = "fast"  # <2s, para exploración rápida
    BALANCED = "balanced"  # 2-10s, balance calidad/velocidad
    QUALITY = "quality"  # >10s, máxima calidad


@dataclass
class ModelConfig:
    """Configuración de un modelo LLM"""
    name: str
    provider: ModelProvider
    tier: ModelTier
    domain_specialty: Optional[str] = None  # e.g., "biology", "mathematics"
    api_key_env: Optional[str] = None
    max_tokens: int = 2048
    temperature: float = 0.7
    enabled: bool = True


@dataclass
class HypothesisCandidate:
    """Candidato de hipótesis con metadata de generación"""
    hypothesis_text: str
    reasoning: str
    confidence: float
    testable_predictions: List[str]
    methodology_suggestions: List[str]
    related_literature: List[str]
    model_name: str
    provider: ModelProvider
    generation_time: float
    tokens_used: int = 0


class ConsensusResult(BaseModel):
    """Resultado del proceso de consensus"""
    final_hypothesis: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    supporting_models: List[str]
    common_predictions: List[str]
    unique_insights: List[str]
    contradictions: List[str]
    quality_metrics: Dict[str, float]


class MultiModelHypothesisService:
    """Servicio de generación de hipótesis multi-modelo con consensus voting"""

    # Configuración de modelos disponibles
    MODEL_CONFIGS = [
        # Ollama local (rápido, siempre disponible)
        ModelConfig(
            name="deepseek-r1:7b",
            provider=ModelProvider.OLLAMA,
            tier=ModelTier.FAST,
            domain_specialty="mathematics",
        ),
        ModelConfig(
            name="qwen3:72b",
            provider=ModelProvider.OLLAMA,
            tier=ModelTier.BALANCED,
            domain_specialty="materials_science",
        ),
        # HuggingFace (modelos científicos especializados)
        ModelConfig(
            name="facebook/galactica-120b",
            provider=ModelProvider.HUGGINGFACE,
            tier=ModelTier.QUALITY,
            domain_specialty="physics",
            api_key_env="HUGGINGFACE_API_KEY",
        ),
        ModelConfig(
            name="microsoft/biogpt",
            provider=ModelProvider.HUGGINGFACE,
            tier=ModelTier.BALANCED,
            domain_specialty="biology",
            api_key_env="HUGGINGFACE_API_KEY",
        ),
        # Groq (ultra-rápido con LPU)
        ModelConfig(
            name="llama3-70b-8192",
            provider=ModelProvider.GROQ,
            tier=ModelTier.FAST,
            api_key_env="GROQ_API_KEY",
        ),
        # Together AI (modelos grandes de alta calidad)
        ModelConfig(
            name="mistralai/Mixtral-8x7B-Instruct-v0.1",
            provider=ModelProvider.TOGETHER,
            tier=ModelTier.QUALITY,
            api_key_env="TOGETHER_API_KEY",
        ),
    ]

    def __init__(self):
        """Inicializar servicio multi-modelo"""
        self.client = httpx.AsyncClient(timeout=DEFAULT_TIMEOUT)
        self._enabled_models: List[ModelConfig] = []
        self._initialize_models()
        logger.info(f"MultiModelHypothesisService initialized with {len(self._enabled_models)} models")

    def _initialize_models(self) -> None:
        """Inicializar y validar modelos disponibles"""
        for config in self.MODEL_CONFIGS:
            # Verificar si el modelo requiere API key
            if config.api_key_env:
                api_key = os.getenv(config.api_key_env)
                if not api_key:
                    logger.warning(f"API key not found for {config.name} ({config.api_key_env})")
                    continue

            # Marcar como habilitado
            self._enabled_models.append(config)
            logger.info(
                f"Enabled model: {config.name} ({config.provider.value}, {config.tier.value})"
            )

    def get_models_for_domain(
        self,
        domain: str,
        tier: Optional[ModelTier] = None,
        max_models: int = 3,
    ) -> List[ModelConfig]:
        """Seleccionar modelos óptimos para un dominio específico"""
        candidates = []

        for config in self._enabled_models:
            # Priorizar modelos especializados en el dominio
            score = 0.0
            if config.domain_specialty == domain:
                score += 2.0
            elif config.domain_specialty is None:
                score += 1.0  # Modelos generales

            # Ajustar por tier si se especifica
            if tier and config.tier == tier:
                score += 1.0

            # Preferir modelos más rápidos en igualdad de condiciones
            if config.tier == ModelTier.FAST:
                score += 0.5

            candidates.append((score, config))

        # Ordenar por score y limitar
        candidates.sort(key=lambda x: x[0], reverse=True)
        selected = [config for _, config in candidates[:max_models]]

        # Asegurar diversidad de proveedores
        providers_used: Set[ModelProvider] = set()
        diverse_selection = []
        for config in selected:
            if len(diverse_selection) >= max_models:
                break
            if config.provider not in providers_used or len(diverse_selection) < 2:
                diverse_selection.append(config)
                providers_used.add(config.provider)

        # Rellenar si faltan
        while len(diverse_selection) < min(max_models, len(selected)):
            for config in selected:
                if config not in diverse_selection:
                    diverse_selection.append(config)
                    if len(diverse_selection) >= max_models:
                        break

        return diverse_selection[:max_models]

    async def _generate_with_ollama(
        self,
        config: ModelConfig,
        request: HypothesisRequest,
    ) -> HypothesisCandidate:
        """Generar hipótesis usando Ollama"""
        start_time = time.time()

        try:
            # Usar el servicio existente con el modelo específico
            request.model_preference = config.name
            response = await ollama_service.generate_hypothesis(request)

            return HypothesisCandidate(
                hypothesis_text=response.hypothesis_text,
                reasoning=response.reasoning,
                confidence=response.confidence,
                testable_predictions=response.testable_predictions,
                methodology_suggestions=response.methodology_suggestions,
                related_literature=response.related_literature,
                model_name=config.name,
                provider=config.provider,
                generation_time=time.time() - start_time,
            )

        except Exception as e:
            logger.error(f"Error generating with Ollama ({config.name}): {e}")
            raise

    async def _generate_with_huggingface(
        self,
        config: ModelConfig,
        request: HypothesisRequest,
    ) -> HypothesisCandidate:
        """Generar hipótesis usando HuggingFace Inference API"""
        start_time = time.time()

        api_key = os.getenv(config.api_key_env or "")
        if not api_key:
            raise ValueError(f"API key not found: {config.api_key_env}")

        prompt = self._create_scientific_prompt(request)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": config.max_tokens,
                "temperature": config.temperature,
                "return_full_text": False,
            },
        }

        try:
            response = await self.client.post(
                f"{HUGGINGFACE_API_URL}/{config.name}",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            result = response.json()

            # HuggingFace devuelve formato diferente según el modelo
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            elif isinstance(result, dict):
                generated_text = result.get("generated_text", "")
            else:
                generated_text = str(result)

            # Intentar parsear JSON si está disponible
            try:
                hypothesis_data = json.loads(generated_text)
            except json.JSONDecodeError:
                # Fallback: crear estructura básica
                hypothesis_data = {
                    "hypothesis_text": generated_text[:500],
                    "reasoning": "Generated by HuggingFace model",
                    "confidence": 0.7,
                    "testable_predictions": [],
                    "methodology_suggestions": [],
                    "related_literature": [],
                }

            return HypothesisCandidate(
                hypothesis_text=hypothesis_data.get("hypothesis_text", ""),
                reasoning=hypothesis_data.get("reasoning", ""),
                confidence=hypothesis_data.get("confidence", 0.7),
                testable_predictions=hypothesis_data.get("testable_predictions", []),
                methodology_suggestions=hypothesis_data.get("methodology_suggestions", []),
                related_literature=hypothesis_data.get("related_literature", []),
                model_name=config.name,
                provider=config.provider,
                generation_time=time.time() - start_time,
            )

        except httpx.HTTPError as e:
            logger.error(f"HuggingFace API error ({config.name}): {e}")
            raise

    async def _generate_with_groq(
        self,
        config: ModelConfig,
        request: HypothesisRequest,
    ) -> HypothesisCandidate:
        """Generar hipótesis usando Groq (ultra-rápido)"""
        start_time = time.time()

        api_key = os.getenv(config.api_key_env or "")
        if not api_key:
            raise ValueError(f"API key not found: {config.api_key_env}")

        prompt = self._create_scientific_prompt(request)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": config.name,
            "messages": [
                {"role": "system", "content": "You are an expert scientific researcher."},
                {"role": "user", "content": prompt},
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }

        try:
            response = await self.client.post(
                GROQ_API_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]

            # Intentar parsear JSON
            try:
                hypothesis_data = json.loads(generated_text)
            except json.JSONDecodeError:
                hypothesis_data = {
                    "hypothesis_text": generated_text[:500],
                    "reasoning": "Generated by Groq",
                    "confidence": 0.75,
                    "testable_predictions": [],
                    "methodology_suggestions": [],
                    "related_literature": [],
                }

            return HypothesisCandidate(
                hypothesis_text=hypothesis_data.get("hypothesis_text", ""),
                reasoning=hypothesis_data.get("reasoning", ""),
                confidence=hypothesis_data.get("confidence", 0.75),
                testable_predictions=hypothesis_data.get("testable_predictions", []),
                methodology_suggestions=hypothesis_data.get("methodology_suggestions", []),
                related_literature=hypothesis_data.get("related_literature", []),
                model_name=config.name,
                provider=config.provider,
                generation_time=time.time() - start_time,
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
            )

        except httpx.HTTPError as e:
            logger.error(f"Groq API error ({config.name}): {e}")
            raise

    async def _generate_with_together(
        self,
        config: ModelConfig,
        request: HypothesisRequest,
    ) -> HypothesisCandidate:
        """Generar hipótesis usando Together AI"""
        start_time = time.time()

        api_key = os.getenv(config.api_key_env or "")
        if not api_key:
            raise ValueError(f"API key not found: {config.api_key_env}")

        prompt = self._create_scientific_prompt(request)

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": config.name,
            "messages": [
                {"role": "system", "content": "You are an expert scientific researcher."},
                {"role": "user", "content": prompt},
            ],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }

        try:
            response = await self.client.post(
                TOGETHER_API_URL,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]

            try:
                hypothesis_data = json.loads(generated_text)
            except json.JSONDecodeError:
                hypothesis_data = {
                    "hypothesis_text": generated_text[:500],
                    "reasoning": "Generated by Together AI",
                    "confidence": 0.75,
                    "testable_predictions": [],
                    "methodology_suggestions": [],
                    "related_literature": [],
                }

            return HypothesisCandidate(
                hypothesis_text=hypothesis_data.get("hypothesis_text", ""),
                reasoning=hypothesis_data.get("reasoning", ""),
                confidence=hypothesis_data.get("confidence", 0.75),
                testable_predictions=hypothesis_data.get("testable_predictions", []),
                methodology_suggestions=hypothesis_data.get("methodology_suggestions", []),
                related_literature=hypothesis_data.get("related_literature", []),
                model_name=config.name,
                provider=config.provider,
                generation_time=time.time() - start_time,
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
            )

        except httpx.HTTPError as e:
            logger.error(f"Together AI API error ({config.name}): {e}")
            raise

    def _create_scientific_prompt(self, request: HypothesisRequest) -> str:
        """Crear prompt científico optimizado"""
        return f"""Generate a rigorous scientific hypothesis for the following research question.

RESEARCH QUESTION: {request.research_question}

SCIENTIFIC DOMAIN: {request.domain}

CONTEXT: {json.dumps(request.context, indent=2) if request.context else "None provided"}

REQUIREMENTS:
1. The hypothesis must be specific, testable, and falsifiable
2. Provide solid scientific reasoning based on current knowledge
3. Suggest concrete, verifiable predictions
4. Recommend appropriate research methodologies
5. Reference relevant literature areas

RESPONSE FORMAT (valid JSON):
{{
    "hypothesis_text": "Clear, specific hypothesis statement",
    "reasoning": "Detailed scientific reasoning and theoretical foundation",
    "confidence": 0.85,
    "testable_predictions": [
        "Specific prediction 1",
        "Specific prediction 2",
        "Specific prediction 3"
    ],
    "methodology_suggestions": [
        "Experimental methodology 1",
        "Data analysis approach 2",
        "Validation strategy 3"
    ],
    "related_literature": [
        "Relevant research area 1",
        "Relevant research area 2",
        "Relevant research area 3"
    ]
}}

IMPORTANT: Respond ONLY with valid JSON, no additional text.
"""

    async def generate_hypothesis_parallel(
        self,
        request: HypothesisRequest,
        num_models: int = 3,
        tier: Optional[ModelTier] = None,
    ) -> List[HypothesisCandidate]:
        """Generar hipótesis en paralelo usando múltiples modelos"""
        # Seleccionar modelos para el dominio
        selected_models = self.get_models_for_domain(
            domain=request.domain,
            tier=tier,
            max_models=num_models,
        )

        if not selected_models:
            logger.warning("No models available, falling back to Ollama")
            selected_models = [
                config for config in self._enabled_models
                if config.provider == ModelProvider.OLLAMA
            ][:1]

        logger.info(
            f"Generating hypothesis with {len(selected_models)} models: "
            f"{[m.name for m in selected_models]}"
        )

        # Generar en paralelo
        tasks = []
        for config in selected_models:
            if config.provider == ModelProvider.OLLAMA:
                task = self._generate_with_ollama(config, request)
            elif config.provider == ModelProvider.HUGGINGFACE:
                task = self._generate_with_huggingface(config, request)
            elif config.provider == ModelProvider.GROQ:
                task = self._generate_with_groq(config, request)
            elif config.provider == ModelProvider.TOGETHER:
                task = self._generate_with_together(config, request)
            else:
                continue

            tasks.append(task)

        # Ejecutar con manejo de errores
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filtrar errores
        candidates = []
        for result in results:
            if isinstance(result, HypothesisCandidate):
                candidates.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Model generation failed: {result}")

        return candidates

    def compute_consensus(
        self,
        candidates: List[HypothesisCandidate],
    ) -> ConsensusResult:
        """Computar consensus entre múltiples hipótesis"""
        if not candidates:
            raise ValueError("No candidates provided for consensus")

        # Análisis de predicciones comunes
        all_predictions: Dict[str, int] = {}
        for candidate in candidates:
            for pred in candidate.testable_predictions:
                pred_lower = pred.lower().strip()
                all_predictions[pred_lower] = all_predictions.get(pred_lower, 0) + 1

        # Predicciones con consensus (aparecen en al menos 2 modelos)
        common_predictions = [
            pred for pred, count in all_predictions.items()
            if count >= min(2, len(candidates))
        ]

        # Identificar insights únicos (solo en 1 modelo)
        unique_insights = [
            pred for pred, count in all_predictions.items()
            if count == 1
        ]

        # Hipótesis con mayor confianza
        best_candidate = max(candidates, key=lambda c: c.confidence)

        # Score de consensus basado en acuerdo entre modelos
        consensus_score = len(common_predictions) / max(1, len(all_predictions))

        # Confidence promedio ponderado
        avg_confidence = sum(c.confidence for c in candidates) / len(candidates)
        final_confidence = (avg_confidence * 0.6 + consensus_score * 0.4)

        # Métricas de calidad
        quality_metrics = {
            "num_models": len(candidates),
            "avg_generation_time": sum(c.generation_time for c in candidates) / len(candidates),
            "consensus_score": consensus_score,
            "avg_confidence": avg_confidence,
            "total_predictions": len(all_predictions),
            "common_predictions_ratio": consensus_score,
        }

        return ConsensusResult(
            final_hypothesis=best_candidate.hypothesis_text,
            confidence_score=final_confidence,
            supporting_models=[c.model_name for c in candidates],
            common_predictions=common_predictions[:5],  # Top 5
            unique_insights=unique_insights[:3],  # Top 3
            contradictions=[],  # TODO: implementar detección de contradicciones
            quality_metrics=quality_metrics,
        )

    async def generate_hypothesis_with_consensus(
        self,
        request: HypothesisRequest,
        num_models: int = 3,
        tier: Optional[ModelTier] = None,
    ) -> tuple[HypothesisResponse, ConsensusResult]:
        """Generar hipótesis con consensus voting"""
        # Generar candidatos en paralelo
        candidates = await self.generate_hypothesis_parallel(
            request=request,
            num_models=num_models,
            tier=tier,
        )

        if not candidates:
            raise RuntimeError("Failed to generate any hypothesis candidates")

        # Computar consensus
        consensus = self.compute_consensus(candidates)

        # Crear respuesta final usando el mejor candidato
        best_candidate = max(candidates, key=lambda c: c.confidence)

        final_response = HypothesisResponse(
            hypothesis_text=best_candidate.hypothesis_text,
            reasoning=best_candidate.reasoning,
            confidence=consensus.confidence_score,
            testable_predictions=consensus.common_predictions + best_candidate.testable_predictions[:3],
            methodology_suggestions=best_candidate.methodology_suggestions,
            related_literature=best_candidate.related_literature,
        )

        return final_response, consensus

    async def close(self):
        """Cerrar cliente HTTP"""
        await self.client.aclose()


# Instancia global del servicio
multi_model_service = MultiModelHypothesisService()
