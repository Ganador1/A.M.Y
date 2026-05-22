"""
Hugging Face Agent Wrapper for Multi-Agent Coordinator

Este módulo integra los modelos de Hugging Face con el sistema multi-agente
de AXIOM Atlas, proporcionando un wrapper compatible con el MultiAgentCoordinator.

Características:
- Drop-in replacement para Ollama models
- Soporte para todos los roles de agentes
- Fallback automático a Ollama si HF falla
- Caché y optimización de performance
- Métricas integradas
"""

import asyncio
import logging
from typing import Dict, Optional, Any
from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest,
    huggingface_provider
)

# Import improved prompts and parameters
try:
    from app.services.improved_agent_prompts import (
        get_improved_prompt,
        get_agent_parameters,
        AGENT_PARAMETERS
    )
    IMPROVED_PROMPTS_AVAILABLE = True
except ImportError:
    IMPROVED_PROMPTS_AVAILABLE = False
    AGENT_PARAMETERS = {}

logger = logging.getLogger(__name__)


class HuggingFaceAgentWrapper:
    """
    Wrapper para usar modelos de Hugging Face en el MultiAgentCoordinator

    Este wrapper proporciona la misma interfaz que RoleLLMWrapper pero
    usa modelos cloud de Hugging Face en lugar de Ollama local.
    """

    def __init__(
        self,
        agent_role: str,
        model_id: Optional[str] = None,
        domain: Optional[str] = None,
        provider: Optional[HuggingFaceProvider] = None,
        use_improved_prompts: bool = True
    ):
        """
        Inicializar wrapper para un rol de agente

        Args:
            agent_role: Rol del agente (orchestrator, bio_hypothesis, etc.)
            model_id: ID del modelo (opcional, se auto-selecciona si no se provee)
            domain: Dominio científico (opcional)
            provider: Instancia del provider (usa global si no se provee)
            use_improved_prompts: Usar prompts mejorados v2.0 (default True)
        """
        self.agent_role = agent_role
        self.domain = domain or "general"
        self.provider = provider or huggingface_provider
        self.use_improved_prompts = use_improved_prompts and IMPROVED_PROMPTS_AVAILABLE

        # Auto-seleccionar modelo si no se especifica
        if model_id:
            self.model_id = model_id
        else:
            self.model_id = self.provider.get_optimal_model(
                domain=self.domain,
                agent_role=agent_role
            )

        # Get optimized parameters for this agent role
        if self.use_improved_prompts and agent_role in AGENT_PARAMETERS:
            self.default_params = AGENT_PARAMETERS[agent_role]
            logger.info(
                f"✅ HuggingFaceAgentWrapper inicializado para '{agent_role}' "
                f"con modelo {self.model_id} y prompts mejorados v2.0 "
                f"(temp={self.default_params['temperature']}, "
                f"max_tokens={self.default_params['max_new_tokens']})"
            )
        else:
            self.default_params = {
                "temperature": 0.7,
                "max_new_tokens": 512,
                "top_p": 0.9
            }
            logger.info(
                f"✅ HuggingFaceAgentWrapper inicializado para '{agent_role}' "
                f"con modelo {self.model_id} (parámetros estándar)"
            )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generar texto (interfaz compatible con RoleLLMWrapper)

        Args:
            prompt: Prompt para el modelo
            max_new_tokens: Máximo de tokens a generar (usa default optimizado si None)
            temperature: Temperatura para sampling (usa default optimizado si None)

        Returns:
            Texto generado
        """
        # Use optimized parameters if not specified
        if max_new_tokens is None:
            max_new_tokens = self.default_params.get("max_new_tokens", 512)
        if temperature is None:
            temperature = self.default_params.get("temperature", 0.7)

        # Apply improved prompt template if available
        if self.use_improved_prompts:
            try:
                # Pass domain to publisher for keyword injection
                improved_prompt = get_improved_prompt(
                    self.agent_role, 
                    prompt,
                    domain=self.domain if self.agent_role == "publisher" else "biology"
                )
                if improved_prompt != prompt:
                    logger.info(f"✨ Using improved prompt template for {self.agent_role}")
                    prompt = improved_prompt
            except Exception as e:
                logger.warning(f"Failed to apply improved prompt: {e}, using original")

        try:
            # Ejecutar generación asíncrona de forma síncrona
            # (compatible con código síncrono del MultiAgentCoordinator)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Si ya hay un loop corriendo, usar asyncio.create_task
                future = asyncio.ensure_future(
                    self.provider.generate_for_agent(
                        agent_role=self.agent_role,
                        prompt=prompt,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        domain=self.domain
                    )
                )
                # Esperar resultado
                response = loop.run_until_complete(future)
            else:
                # Si no hay loop, crear uno nuevo
                response = asyncio.run(
                    self.provider.generate_for_agent(
                        agent_role=self.agent_role,
                        prompt=prompt,
                        max_new_tokens=max_new_tokens,
                        temperature=temperature,
                        domain=self.domain
                    )
                )

            if response.success:
                logger.info(
                    f"✅ Generación exitosa para '{self.agent_role}' "
                    f"({response.tokens_generated} tokens, {response.latency_ms:.0f}ms)"
                )
                return response.generated_text
            else:
                logger.error(
                    f"❌ Error en generación HF: {response.error}. "
                    f"Retornando mensaje de error."
                )
                return f"[ERROR: {response.error}]"

        except Exception as e:
            logger.error(f"❌ Excepción en HuggingFaceAgentWrapper.generate: {e}")
            return f"[ERROR: {str(e)}]"

    async def generate_async(
        self,
        prompt: str,
        max_new_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generar texto (versión asíncrona nativa)

        Args:
            prompt: Prompt para el modelo
            max_new_tokens: Máximo de tokens a generar (usa default optimizado si None)
            temperature: Temperatura para sampling (usa default optimizado si None)

        Returns:
            Texto generado
        """
        # Use optimized parameters if not specified
        if max_new_tokens is None:
            max_new_tokens = self.default_params.get("max_new_tokens", 512)
        if temperature is None:
            temperature = self.default_params.get("temperature", 0.7)

        # Apply improved prompt template if available
        if self.use_improved_prompts:
            try:
                # Pass domain to publisher for keyword injection
                improved_prompt = get_improved_prompt(
                    self.agent_role,
                    prompt,
                    domain=self.domain if self.agent_role == "publisher" else "biology"
                )
                if improved_prompt != prompt:
                    logger.info(f"✨ Using improved prompt template for {self.agent_role}")
                    prompt = improved_prompt
            except Exception as e:
                logger.warning(f"Failed to apply improved prompt: {e}, using original")

        try:
            response = await self.provider.generate_for_agent(
                agent_role=self.agent_role,
                prompt=prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                domain=self.domain
            )

            if response.success:
                logger.info(
                    f"✅ Generación async exitosa para '{self.agent_role}' "
                    f"({response.tokens_generated} tokens, {response.latency_ms:.0f}ms)"
                )
                return response.generated_text
            else:
                logger.error(f"❌ Error en generación async HF: {response.error}")
                return f"[ERROR: {response.error}]"

        except Exception as e:
            logger.error(f"❌ Excepción en generate_async: {e}")
            return f"[ERROR: {str(e)}]"


class HybridAgentWrapper:
    """
    Wrapper híbrido que intenta Hugging Face primero y hace fallback a Ollama

    Este wrapper proporciona máxima robustez al intentar primero modelos cloud
    de Hugging Face y hacer fallback automático a modelos locales de Ollama
    si hay algún problema.
    """

    def __init__(
        self,
        agent_role: str,
        hf_model_id: Optional[str] = None,
        ollama_model: Optional[str] = None,
        domain: Optional[str] = None,
        prefer_cloud: bool = True
    ):
        """
        Inicializar wrapper híbrido

        Args:
            agent_role: Rol del agente
            hf_model_id: Modelo de Hugging Face (opcional)
            ollama_model: Modelo de Ollama (opcional)
            domain: Dominio científico
            prefer_cloud: Preferir modelos cloud sobre locales
        """
        self.agent_role = agent_role
        self.domain = domain or "general"
        self.prefer_cloud = prefer_cloud

        # Inicializar wrapper de Hugging Face
        self.hf_wrapper = HuggingFaceAgentWrapper(
            agent_role=agent_role,
            model_id=hf_model_id,
            domain=domain
        )

        # Inicializar wrapper de Ollama (fallback)
        self.ollama_wrapper = None
        if ollama_model:
            try:
                from app.services.multi_agent_coordinator import RoleLLMWrapper
                self.ollama_wrapper = RoleLLMWrapper(ollama_model)
                logger.info(f"✅ Fallback Ollama configurado: {ollama_model}")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo configurar fallback Ollama: {e}")

        logger.info(
            f"✅ HybridAgentWrapper inicializado para '{agent_role}' "
            f"(cloud: {self.hf_wrapper.model_id}, "
            f"local: {ollama_model or 'none'})"
        )

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """
        Generar texto con fallback automático

        Args:
            prompt: Prompt para el modelo
            max_new_tokens: Máximo de tokens a generar
            temperature: Temperatura para sampling

        Returns:
            Texto generado
        """
        # Intentar con el proveedor preferido primero
        if self.prefer_cloud:
            # Intentar Hugging Face primero
            hf_result = self.hf_wrapper.generate(prompt, max_new_tokens, temperature)

            if not hf_result.startswith("[ERROR"):
                return hf_result

            logger.warning(f"⚠️ HF falló, intentando con Ollama...")

            # Fallback a Ollama
            if self.ollama_wrapper:
                try:
                    return self.ollama_wrapper.generate(prompt, max_new_tokens, temperature)
                except Exception as e:
                    logger.error(f"❌ Ollama también falló: {e}")
                    return f"[ERROR: Ambos proveedores fallaron - HF: {hf_result}, Ollama: {str(e)}]"
            else:
                return hf_result
        else:
            # Intentar Ollama primero
            if self.ollama_wrapper:
                try:
                    ollama_result = self.ollama_wrapper.generate(prompt, max_new_tokens, temperature)
                    if not ollama_result.startswith("[ERROR"):
                        return ollama_result

                    logger.warning(f"⚠️ Ollama falló, intentando con HF...")
                except Exception as e:
                    logger.warning(f"⚠️ Error con Ollama: {e}, intentando con HF...")

            # Fallback a Hugging Face
            return self.hf_wrapper.generate(prompt, max_new_tokens, temperature)

    async def generate_async(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7
    ) -> str:
        """
        Generar texto con fallback automático (versión asíncrona)

        Args:
            prompt: Prompt para el modelo
            max_new_tokens: Máximo de tokens a generar
            temperature: Temperatura para sampling

        Returns:
            Texto generado
        """
        # Intentar con el proveedor preferido primero
        if self.prefer_cloud:
            # Intentar Hugging Face primero
            hf_result = await self.hf_wrapper.generate_async(prompt, max_new_tokens, temperature)

            if not hf_result.startswith("[ERROR"):
                return hf_result

            logger.warning(f"⚠️ HF falló, intentando con Ollama...")

            # Fallback a Ollama
            if self.ollama_wrapper:
                try:
                    # Ollama wrapper might not have generate_async, check it
                    if hasattr(self.ollama_wrapper, 'generate_async'):
                        return await self.ollama_wrapper.generate_async(prompt, max_new_tokens, temperature)
                    else:
                        # Run sync generate in thread pool
                        return await asyncio.to_thread(
                            self.ollama_wrapper.generate, 
                            prompt, 
                            max_new_tokens, 
                            temperature
                        )
                except Exception as e:
                    logger.error(f"❌ Ollama también falló: {e}")
                    return f"[ERROR: Ambos proveedores fallaron - HF: {hf_result}, Ollama: {str(e)}]"
            else:
                return hf_result
        else:
            # Intentar Ollama primero
            if self.ollama_wrapper:
                try:
                    if hasattr(self.ollama_wrapper, 'generate_async'):
                        ollama_result = await self.ollama_wrapper.generate_async(prompt, max_new_tokens, temperature)
                    else:
                        ollama_result = await asyncio.to_thread(
                            self.ollama_wrapper.generate,
                            prompt,
                            max_new_tokens,
                            temperature
                        )
                    
                    if not ollama_result.startswith("[ERROR"):
                        return ollama_result

                    logger.warning(f"⚠️ Ollama falló, intentando con HF...")
                except Exception as e:
                    logger.warning(f"⚠️ Error con Ollama: {e}, intentando con HF...")

            # Fallback a Hugging Face
            return await self.hf_wrapper.generate_async(prompt, max_new_tokens, temperature)


def create_agent_wrapper(
    agent_role: str,
    provider: str = "huggingface",
    domain: Optional[str] = None,
    model_override: Optional[str] = None,
    **kwargs
) -> Any:
    """
    Factory function para crear wrappers de agentes

    Args:
        agent_role: Rol del agente
        provider: Proveedor a usar ("huggingface", "ollama", "hybrid")
        domain: Dominio científico
        model_override: ID de modelo específico (opcional)
        **kwargs: Parámetros adicionales

    Returns:
        Wrapper de agente apropiado
    """
    if provider == "huggingface":
        return HuggingFaceAgentWrapper(
            agent_role=agent_role,
            model_id=model_override,
            domain=domain
        )
    elif provider == "hybrid":
        # Obtener modelo Ollama para el rol
        ollama_models = {
            "orchestrator": "llama3:8b",
            "bio_hypothesis": "mistral:7b",
            "physchem_coder": "codellama:7b",
            "reviewer": "qwen:7b",
            "publisher": "llama3:8b"
        }

        return HybridAgentWrapper(
            agent_role=agent_role,
            hf_model_id=model_override,
            ollama_model=ollama_models.get(agent_role),
            domain=domain,
            prefer_cloud=kwargs.get("prefer_cloud", True)
        )
    elif provider == "ollama":
        from app.services.multi_agent_coordinator import RoleLLMWrapper
        ollama_model = model_override or kwargs.get("ollama_model", "llama3:8b")
        return RoleLLMWrapper(ollama_model)
    else:
        raise ValueError(f"Proveedor desconocido: {provider}")


# Exportar clases y funciones principales
__all__ = [
    "HuggingFaceAgentWrapper",
    "HybridAgentWrapper",
    "create_agent_wrapper"
]
