"""Shared infrastructure for external AI-for-science adapters."""

from __future__ import annotations

from typing import Any, Dict
import os

import httpx

from app.core.base_service import BaseService


class ExternalScienceAdapter(BaseService):
    """Base class for optional external science integrations."""

    def __init__(self, name: str, config: Dict[str, Any] | None = None):
        super().__init__(name)
        self.config = config or {}
        self.enabled = bool(self.config.get("enabled", True))

    def get_status(self) -> Dict[str, Any]:
        return {
            "adapter": self.name,
            "enabled": self.enabled,
            "configured": self.is_configured(),
            "available": self.is_available(),
        }

    def is_configured(self) -> bool:
        return self.enabled

    def is_available(self) -> bool:
        return self.enabled and self.is_configured()

    def unavailable_response(self, reason: str, **extra: Any) -> Dict[str, Any]:
        return {
            "success": False,
            "unavailable": True,
            "adapter": self.name,
            "error": reason,
            **extra,
        }

    def _env(self, key: str, default: str | None = None) -> str | None:
        value = os.getenv(key)
        if value is not None and str(value).strip():
            return value
        return default


class HttpExternalScienceAdapter(ExternalScienceAdapter):
    """Simple configurable HTTP adapter for externally hosted science models."""

    def __init__(self, name: str, config: Dict[str, Any] | None = None):
        super().__init__(name, config=config)
        self.base_url = self._env(str(self.config.get("base_url_env", "")), self.config.get("base_url"))
        self.api_key = self._env(str(self.config.get("api_key_env", "")))
        self.timeout = float(self.config.get("timeout_seconds", 45))

    def is_configured(self) -> bool:
        return self.enabled and bool(self.base_url)

    async def _post_json(self, endpoint_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = ((self.config.get("endpoints") or {}).get(endpoint_key) or "").strip()
        if not self.base_url or not endpoint:
            return self.unavailable_response(
                f"Missing base URL or endpoint for {endpoint_key}",
                endpoint_key=endpoint_key,
            )

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            auth_header = (self.config.get("auth_header") or "Authorization").strip()
            prefix = (self.config.get("auth_prefix") or "Bearer").strip()
            headers[auth_header] = f"{prefix} {self.api_key}".strip()

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}",
                    json=payload,
                    headers=headers,
                )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                data.setdefault("success", True)
                data.setdefault("adapter", self.name)
                data.setdefault("backend", "http")
                return data
            return {"success": True, "adapter": self.name, "backend": "http", "result": data}
        except Exception as exc:
            return {
                "success": False,
                "adapter": self.name,
                "backend": "http",
                "error": str(exc),
            }
