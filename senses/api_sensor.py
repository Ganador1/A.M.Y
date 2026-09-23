"""
API Sensor — Monitors external APIs for new data.

Monitors external data sources like financial markets,
weather APIs, news feeds, etc.
"""
import asyncio
from datetime import datetime

import httpx
import structlog

log = structlog.get_logger()


class APISensor:
    """Sensor that polls external APIs for new data."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.endpoints = self.config.get("endpoints", [])
        self.poll_interval = self.config.get("poll_interval_seconds", 300)
        self._last_poll = 0.0
        self._http: httpx.AsyncClient | None = None

    async def _get_http(self) -> httpx.AsyncClient:
        if self._http is None or self._http.is_closed:
            self._http = httpx.AsyncClient(timeout=30.0)
        return self._http

    async def sense(self) -> list[dict]:
        """Poll configured endpoints and return new data."""
        now = datetime.now().timestamp()
        if now - self._last_poll < self.poll_interval:
            return []

        self._last_poll = now
        observations = []

        for endpoint in self.endpoints:
            try:
                http = await self._get_http()
                response = await http.get(
                    endpoint["url"],
                    headers=endpoint.get("headers", {}),
                    params=endpoint.get("params", {}),
                )
                if response.status_code == 200:
                    data = response.json() if endpoint.get("parse_json", True) else response.text
                    observations.append({
                        "source": endpoint.get("name", endpoint["url"]),
                        "type": "api_data",
                        "timestamp": now,
                        "data": data,
                    })
            except Exception as e:
                log.warning("api_sensor.poll_failed", url=endpoint.get("url", "unknown"), error=str(e))

        return observations

    async def close(self):
        if self._http and not self._http.is_closed:
            await self._http.aclose()
