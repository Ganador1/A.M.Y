"""
Groq API Provider for AXIOM Atlas
Ultra-fast inference with Llama-3-70B and other models
"""
from typing import Dict, Any, Optional
import httpx
import asyncio
import os
from app.services.base_service import BaseService
from app.core.config import settings
from app.core.bootstrap_logging import logger


class GroqProvider(BaseService):
    """Groq LLM provider with ultra-low latency inference.

    Free tier available at: https://console.groq.com

    Supported models:
    - llama-3-70b-groq-tool-use
    - llama-3.1-70b-versatile
    - mixtral-8x7b-32768
    - llama-3.1-8b-instant (fast fallback)
    """

    def __init__(self):
        super().__init__("GroqProvider")
        # Try environment variable first, then settings
        self.api_key = os.environ.get('GROQ_API_KEY') or getattr(settings, 'groq_api_key', None)
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = "llama-3.3-70b-versatile"
        self.enabled = bool(self.api_key)

        if self.enabled:
            logger.info(f"✅ GroqProvider initialized - Default model: {self.default_model}")
        else:
            logger.warning("⚠️ GroqProvider disabled - No API key found (set GROQ_API_KEY)")

    def is_available(self) -> bool:
        """Check if Groq provider is available"""
        return self.enabled

    async def generate_async(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Groq API (async)

        Args:
            prompt: Input prompt
            model: Model name (default: llama-3.1-70b-versatile)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Dict with 'text', 'model', 'usage', 'latency_ms'
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "Groq provider not enabled - missing API key"
            }
        # --- Security Guard: Prompt Injection & Misuse Check ---
        try:
            from app.security.misuse_guard import require_safe_operation
            require_safe_operation(
                operation="groq_generation",
                content=prompt,
                domain="llm_inference",
                tool_name="GroqProvider"
            )
        except Exception as e:
            logger.warning(f"Groq request blocked by security guard: {e}")
            return {"success": False, "error": f"Security Guard blocked prompt: {e}"}
        # -------------------------------------------------------
        model = model or self.default_model

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": kwargs.get("top_p", 1.0),
            "stream": False
        }

        try:
            import time
            start = time.time()

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()

            latency_ms = (time.time() - start) * 1000
            data = response.json()

            return {
                "success": True,
                "text": data["choices"][0]["message"]["content"],
                "model": data["model"],
                "usage": data.get("usage", {}),
                "latency_ms": round(latency_ms, 2),
                "finish_reason": data["choices"][0].get("finish_reason"),
                "provider": "groq"
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Groq API error: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text[:200]}"
            }
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using Groq API (sync wrapper)"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(
            self.generate_async(prompt, model, temperature, max_tokens, **kwargs)
        )

    async def list_models(self) -> Dict[str, Any]:
        """List available Groq models"""
        if not self.enabled:
            return {"success": False, "error": "Provider not enabled"}

        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=headers
                )
                response.raise_for_status()

            data = response.json()
            models = [
                {
                    "id": m["id"],
                    "owned_by": m.get("owned_by", "groq"),
                    "created": m.get("created")
                }
                for m in data.get("data", [])
            ]

            return {
                "success": True,
                "models": models,
                "count": len(models)
            }

        except Exception as e:
            logger.error(f"Failed to list Groq models: {e}")
            return {"success": False, "error": str(e)}

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


# Singleton instance
groq_provider = GroqProvider()


__all__ = ["GroqProvider", "groq_provider"]
