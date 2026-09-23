"""
Local LLM Service for AXIOM
- Supports Hugging Face transformers and MLX LM (Apple Silicon) backends
- Focus: lightweight text generation usable for hypothesis generation and scientific reasoning

Notes:
- Avoid external paid APIs; run locally.
- Keep defaults small to minimize VRAM/RAM usage; allow env overrides via settings.
- Prefer instruction-tuned models for better following.
"""
from __future__ import annotations
from typing import Any, Dict, Optional
import httpx
import asyncio
import os

from app.services.base_service import BaseService
from app.core.config import settings
from app.core.bootstrap_logging import logger
from app.exceptions.domain.biology import BiologyError

class LocalLLMService(BaseService):
    def __init__(self):
        super().__init__("LocalLLM")
        self.backend = settings.llm_backend
        self.enabled = settings.enable_local_llm
        self.max_new_tokens = settings.llm_max_new_tokens
        self.temperature = settings.llm_temperature
        self.model_id = settings.hf_model_id_science or settings.hf_model_id
        self._ready = False
        self._init_backend()

    def _init_backend(self) -> None:
        if not self.enabled:
            logger.info("LocalLLM disabled by settings")
            return
        if os.getenv("AXIOM_DISABLE_NET", "0").lower() in {"1", "true", "yes"}:
            logger.info("LocalLLM backend disabled (offline mode)")
            self._ready = False
            return
        try:
            if self.backend == "ollama":
                # Ollama API backend
                import requests
                self._requests = requests
                self._ollama_url = settings.ollama_api_url
                self._ollama_model = settings.ollama_model
                # Test connection to Ollama
                response = httpx.get(f"{self._ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name", "") for m in models]
                    if self._ollama_model in model_names:
                        self._ready = True
                        logger.info(f"✅ LocalLLM (Ollama) ready: {self._ollama_model} at {self._ollama_url}")
                    else:
                        logger.warning(f"⚠️ Model {self._ollama_model} not found in Ollama. Available: {model_names}")
                        self._ready = False
                else:
                    logger.warning(f"⚠️ Ollama API not responding at {self._ollama_url}")
                    self._ready = False
            elif self.backend == "mlx":
                # Try mlx-lm simple generate API
                try:
                    # generate from mlx_lm.generate; load from mlx_lm.utils
                    from mlx_lm.generate import generate as mlx_generate
                    from mlx_lm.utils import load as mlx_load
                except BiologyError as e:
                    logger.warning(f"MLX backend not available: {e}")
                    self._ready = False
                    return
                self._mlx_generate = mlx_generate
                self._mlx_load = mlx_load
                self._mlx_model_path = settings.mlx_model_id or self.model_id
                self._mlx_model, self._mlx_tokenizer = self._mlx_load(self._mlx_model_path)
                self._ready = True
                logger.info(f"✅ LocalLLM (MLX) ready: {self._mlx_model_path}")
            else:
                # transformers backend
                from transformers import AutoModelForCausalLM, AutoTokenizer
                import torch
                trust_remote = getattr(settings, 'llm_trust_remote_code', True)
                self._tok = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=trust_remote)
                # Select device and dtype safely
                use_cuda = torch.cuda.is_available()
                use_mps = (hasattr(torch.backends, 'mps') and torch.backends.mps.is_available())
                self._device = "cuda" if use_cuda else ("mps" if use_mps else "cpu")
                dtype = torch.float16 if use_cuda else (torch.float32 if use_mps else torch.float32)
                self._model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=dtype,
                    trust_remote_code=trust_remote
                )
                self._model.to(self._device)
                self._ready = True
                logger.info(f"✅ LocalLLM (transformers) ready: {self.model_id} on {self._device}")
        except BiologyError as e:
            logger.warning(f"⚠️ LocalLLM init failed ({self.backend}): {e}")
            self._ready = False

    def is_ready(self) -> bool:
        return self._ready and self.enabled

    def generate_text(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        if not self.is_ready():
            return {"success": False, "error": "Local LLM not ready"}

        max_new_tokens = int(kwargs.get("max_new_tokens", self.max_new_tokens))
        temperature = float(kwargs.get("temperature", self.temperature))

        try:
            if self.backend == "ollama" and hasattr(self, "_ollama_model"):
                # Ollama API call
                payload = {
                    "model": self._ollama_model,
                    "prompt": prompt,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_new_tokens
                    },
                    "stream": False
                }
                response = httpx.post(
                    f"{self._ollama_url}/api/generate",
                    json=payload,
                    timeout=120  # Increased timeout for 7B+ models
                )
                if response.status_code == 200:
                    result = response.json()
                    return {"success": True, "text": result.get("response", "")}
                else:
                    return {"success": False, "error": f"Ollama API error: {response.status_code}"}
            elif self.backend == "mlx" and hasattr(self, "_mlx_generate"):
                # mlx-lm streaming generate returns iterator; collect text
                output = []
                for tok in self._mlx_generate(self._mlx_model, self._mlx_tokenizer, prompt, temp=temperature, max_tokens=max_new_tokens):
                    output.append(tok)
                text = "".join(output)
                return {"success": True, "text": text}
            else:
                # transformers backend
                inputs = self._tok(prompt, return_tensors="pt").to(self._device)
                gen_ids = self._model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    pad_token_id=self._tok.eos_token_id,
                )
                text = self._tok.batch_decode(gen_ids, skip_special_tokens=True)[0]
                # return only the completion tail
                completion = text[len(prompt):].strip() if text.startswith(prompt) else text
                return {"success": True, "text": completion}
        except BiologyError as e:
            return {"success": False, "error": str(e)}

    def generate_json(self, prompt: str, schema_hint: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Lightweight JSON-style generation with simple postprocessing."""
        res = self.generate_text(prompt, **kwargs)
        if not res.get("success"):
            return res
        txt = res.get("text", "")
        # naive bracket extraction
        start = txt.find("{")
        end = txt.rfind("}")
        if start != -1 and end != -1 and end > start:
            import json
            try:
                return {"success": True, "json": json.loads(txt[start:end+1])}
            except BiologyError:
                pass
        return {"success": True, "text": txt}

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Local LLM requests.
        Supported actions: 'generate_text', 'generate_json'.
        """
        try:
            action = request_data.get("action")
            if action == "generate_text":
                prompt = request_data.get("prompt", "")
                if not prompt:
                    return {"success": False, "error": "prompt is required"}
                params = {k: request_data.get(k) for k in ("max_new_tokens", "temperature") if k in request_data}
                return self.generate_text(prompt, **params)
            elif action == "generate_json":
                prompt = request_data.get("prompt", "")
                if not prompt:
                    return {"success": False, "error": "prompt is required"}
                params = {k: request_data.get(k) for k in ("max_new_tokens", "temperature") if k in request_data}
                return self.generate_json(prompt, **params)
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except BiologyError as e:
            return {"success": False, "error": str(e)}
