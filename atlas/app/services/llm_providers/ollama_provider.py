"""
Ollama API Provider for AXIOM Atlas.

Uses the REST API directly so cloud-only features such as ``think=false`` can be
controlled explicitly from Atlas pipelines.
"""
from typing import Dict, Any, Optional
import os

import httpx

from app.services.base_service import BaseService
from app.core.bootstrap_logging import logger

class OllamaProvider(BaseService):
    """Ollama LLM provider for local and cloud inference.

    Supported models (example):
    - gemini-3-flash-preview:cloud
    - minimax-m2.1:cloud
    - glm-4.7:cloud
    - deepseek-v3.1:671b-cloud
    """

    def __init__(self):
        super().__init__("OllamaProvider")
        self.base_url = os.environ.get('OLLAMA_BASE_URL', "http://localhost:11434")
        self.default_model = "gemini-3-flash-preview:cloud"  # High performance default
        api_key = os.environ.get('OLLAMA_API_KEY', '')
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
        self.client = httpx.AsyncClient(base_url=self.base_url.rstrip("/"), headers=headers)
        self.enabled = True
        
        logger.info(f"✅ OllamaProvider initialized - Host: {self.base_url}, Auth: {'yes' if api_key else 'no'}, Default model: {self.default_model}")

    def is_available(self) -> bool:
        """Check if Ollama provider is available"""
        return self.enabled

    async def generate_async(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Ollama"""
        if not self.enabled:
            return {"error": "OllamaProvider disabled"}

        target_model = model or self.default_model
        # Modelos GLM (y otros thinking models) requieren think=False para poblar
        # el campo 'response'; si think=True solo llenan 'thinking' y response queda vacío
        is_thinking_model = any(kw in target_model.lower() for kw in ("glm", "qwq", "deepseek-r", "o1"))
        think = bool(kwargs.pop("think", False))
        if is_thinking_model:
            think = False  # siempre False para estos modelos en Atlas
        timeout_seconds = float(kwargs.pop("timeout_seconds", os.environ.get("OLLAMA_TIMEOUT_SECONDS", "180")))
        if "max_new_tokens" in kwargs and "max_tokens" not in kwargs:
            max_tokens = int(kwargs.pop("max_new_tokens"))

        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
            **kwargs
        }
        
        try:
            response = await self.client.post(
                "/api/generate",
                json={
                    "model": target_model,
                    "prompt": prompt,
                    "options": options,
                    "stream": False,
                    "think": think,
                },
                timeout=timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            
            # Map Ollama response to Groq-like response for compatibility
            eval_count = payload.get('eval_count', 0) or 0
            prompt_eval_count = payload.get('prompt_eval_count', 0) or 0
            text = (payload.get('response') or "").strip()
            if not text:
                logger.warning(
                    "⚠️ Ollama returned empty response for model=%s done_reason=%s thinking_len=%s",
                    target_model,
                    payload.get("done_reason"),
                    len(payload.get("thinking") or ""),
                )
                return {
                    "success": False,
                    "error": "empty_response",
                    "text": "",
                    "model": target_model,
                    "thinking": payload.get("thinking"),
                    "usage": {
                        "completion_tokens": eval_count,
                        "prompt_tokens": prompt_eval_count,
                        "total_tokens": eval_count + prompt_eval_count
                    }
                }
            
            return {
                "success": True,
                "text": text,
                "model": target_model,
                "thinking": payload.get("thinking"),
                "usage": {
                    "completion_tokens": eval_count,
                    "prompt_tokens": prompt_eval_count,
                    "total_tokens": eval_count + prompt_eval_count
                }
            }
            
        except Exception as e:
            logger.error(f"Ollama generation failed for {target_model}: {e}")
            return {"success": False, "error": str(e), "text": ""}
            
    async def chat_async(
        self,
        messages: list,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Chat completion using Ollama"""
        target_model = model or self.default_model
        think = bool(kwargs.pop("think", False))
        timeout_seconds = float(kwargs.pop("timeout_seconds", os.environ.get("OLLAMA_TIMEOUT_SECONDS", "180")))
        if "max_new_tokens" in kwargs and "max_tokens" not in kwargs:
            max_tokens = int(kwargs.pop("max_new_tokens"))
        options = {
            "temperature": temperature,
            "num_predict": max_tokens,
            **kwargs
        }
        
        try:
            response = await self.client.post(
                "/api/chat",
                json={
                    "model": target_model,
                    "messages": messages,
                    "options": options,
                    "stream": False,
                    "think": think,
                },
                timeout=timeout_seconds,
            )
            response.raise_for_status()
            payload = response.json()
            
            eval_count = payload.get('eval_count', 0) or 0
            prompt_eval_count = payload.get('prompt_eval_count', 0) or 0
            message = payload.get('message') or {}
            text = (message.get('content') or "").strip()
            if not text:
                logger.warning(
                    "⚠️ Ollama chat returned empty response for model=%s done_reason=%s thinking_len=%s",
                    target_model,
                    payload.get("done_reason"),
                    len(payload.get("thinking") or ""),
                )
                return {
                    "success": False,
                    "error": "empty_response",
                    "text": "",
                    "model": target_model,
                    "thinking": payload.get("thinking"),
                    "usage": {
                        "completion_tokens": eval_count,
                        "prompt_tokens": prompt_eval_count,
                        "total_tokens": eval_count + prompt_eval_count
                    }
                }

            return {
                "success": True,
                "text": text,
                "model": target_model,
                "thinking": payload.get("thinking"),
                "usage": {
                    "completion_tokens": eval_count,
                    "prompt_tokens": prompt_eval_count,
                    "total_tokens": eval_count + prompt_eval_count
                }
            }
        except Exception as e:
            logger.error(f"Ollama chat failed for {target_model}: {e}")
            return {"success": False, "error": str(e), "text": ""}

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a generation request (BaseService interface)"""
        prompt = request_data.get("prompt", "")
        model = request_data.get("model", self.default_model)
        temperature = request_data.get("temperature", 0.7)
        max_tokens = request_data.get("max_tokens", 1024)
        
        return await self.generate_async(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

# Global instance
ollama_provider = OllamaProvider()
