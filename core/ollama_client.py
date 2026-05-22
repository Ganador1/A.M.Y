"""
Ollama Cloud Client — Dual API key load balancer for A.M.Y.

Connects to Ollama Cloud (https://ollama.com/api) using two API keys
in round-robin with automatic failover. If one key is rate-limited or
fails, the other takes over seamlessly.

Implements the /api/chat endpoint (OpenAI-compatible messages format).
"""
import asyncio
import json
import os
import time
from itertools import cycle

import httpx
import structlog

log = structlog.get_logger()

# Load API keys from environment / .env
def _load_env():
    """Load .env file if it exists."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()


class OllamaCloudClient:
    """
    Async client for Ollama Cloud API with dual-key round-robin.

    Usage:
        client = OllamaCloudClient(config)
        response = await client.chat(model="glm5.1", messages=[...])
    """

    def __init__(self, config: dict):
        self.base_url = config.get("base_url", "https://ollama.com/api")
        self.config = config

        # Load API keys (supports single or dual key config)
        key1 = os.environ.get("OLLAMA_CLOUD_API_KEY_1", "") or os.environ.get("OLLAMA_CLOUD_API_KEY", "")
        key2 = os.environ.get("OLLAMA_CLOUD_API_KEY_2", "")

        self._keys = [k for k in [key1, key2] if k]
        if not self._keys:
            raise ValueError(
                "No Ollama Cloud API keys found. "
                "Set OLLAMA_CLOUD_API_KEY_1 and/or OLLAMA_CLOUD_API_KEY_2 in .env"
            )

        self._key_cycle = cycle(range(len(self._keys)))
        self._key_failures: dict[int, float] = {}  # key_index → last_failure_time
        self._cooldown_seconds = 120  # Wait 2 min before retrying a rate-limited key

        # Shared httpx async client (connection pooling)
        self._http: httpx.AsyncClient | None = None

        log.info(
            "ollama_cloud.initialized",
            base_url=self.base_url,
            keys_loaded=len(self._keys),
        )

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            # 120s read timeout — necesario cuando Ollama Cloud está bajo carga
            self._http = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=10.0))
        return self._http

    def _pick_key(self) -> tuple[int, str]:
        """Pick the next available API key (round-robin with cooldown)."""
        now = time.time()
        for _ in range(len(self._keys)):
            idx = next(self._key_cycle)
            last_fail = self._key_failures.get(idx, 0)
            if now - last_fail > self._cooldown_seconds:
                return idx, self._keys[idx]

        # All keys in cooldown — use the least recently failed one
        idx = min(self._key_failures, key=self._key_failures.get, default=0)
        return idx, self._keys[idx]

    async def chat(
        self,
        model: str,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        format_json: bool = False,
        num_ctx: int | None = None,
    ) -> dict:
        """
        Send a chat completion request to Ollama Cloud.

        Returns the full response dict with 'message' containing the assistant reply.
        """
        payload: dict = {
            "model": model,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if num_ctx:
            payload["options"]["num_ctx"] = num_ctx
        if format_json:
            payload["format"] = "json"

        # Try with failover
        last_error = None
        for attempt in range(len(self._keys)):
            key_idx, api_key = self._pick_key()
            try:
                result = await self._do_request(
                    endpoint="/chat",
                    payload=payload,
                    api_key=api_key,
                )
                # Clear failure record on success
                self._key_failures.pop(key_idx, None)
                return result
            except Exception as e:
                last_error = e
                self._key_failures[key_idx] = time.time()
                err_msg = type(e).__name__ + (f': {e}' if str(e) else '')
                log.warning(
                    "ollama_cloud.key_failed",
                    key_index=key_idx,
                    error=err_msg,
                    attempt=attempt + 1,
                )
                # Pequeña pausa antes de intentar la siguiente key
                if attempt < len(self._keys) - 1:
                    await asyncio.sleep(3)

        raise RuntimeError(f"All Ollama Cloud keys failed. Last error: {type(last_error).__name__}: {last_error}")

    async def generate(
        self,
        model: str,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        format_json: bool = False,
    ) -> dict:
        """Simple generate (non-chat) endpoint."""
        payload: dict = {
            "model": model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if format_json:
            payload["format"] = "json"

        last_error = None
        for attempt in range(len(self._keys)):
            key_idx, api_key = self._pick_key()
            try:
                result = await self._do_request("/generate", payload, api_key)
                self._key_failures.pop(key_idx, None)
                return result
            except Exception as e:
                last_error = e
                self._key_failures[key_idx] = time.time()

        raise RuntimeError(f"All keys failed. Last error: {last_error}")

    async def embed(self, model: str, input_text: str | list[str]) -> list[list[float]]:
        """Generate embeddings."""
        payload = {
            "model": model,
            "input": input_text,
        }
        key_idx, api_key = self._pick_key()
        result = await self._do_request("/embed", payload, api_key)
        return result.get("embeddings", [])

    async def _do_request(self, endpoint: str, payload: dict, api_key: str) -> dict:
        """Execute a single HTTP request to Ollama Cloud."""
        http = await self._get_http()
        url = f"{self.base_url}{endpoint}"

        response = await http.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code != 200:
            body = response.text[:500]
            raise httpx.HTTPStatusError(
                f"Ollama Cloud returned {response.status_code}: {body}",
                request=response.request,
                response=response,
            )

        return response.json()

    async def close(self):
        """Close the HTTP client."""
        if self._http and not self._http.is_closed:
            await self._http.aclose()

    async def health_check(self) -> dict:
        """Check if both API keys work."""
        results = {}
        for i, key in enumerate(self._keys):
            try:
                http = await self._get_http()
                resp = await http.get(
                    f"{self.base_url}/../api/version",
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=10.0,
                )
                results[f"key_{i+1}"] = {
                    "status": "ok" if resp.status_code == 200 else f"error_{resp.status_code}",
                }
            except Exception as e:
                results[f"key_{i+1}"] = {"status": "error", "message": str(e)}
        return results
