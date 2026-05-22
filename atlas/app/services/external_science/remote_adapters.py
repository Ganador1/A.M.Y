"""Configurable remote adapters for external AI-for-science systems."""

from __future__ import annotations

from typing import Any, Dict

from app.services.external_science.base import HttpExternalScienceAdapter


class MatterGenAdapter(HttpExternalScienceAdapter):
    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__("mattergen", config=config)

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        action = request_data.get("action")
        if action != "generate_candidates":
            return {"success": False, "adapter": self.name, "error": f"Unknown action {action}"}
        payload = {
            "target_properties": request_data.get("target_properties", {}),
            "chemical_system": request_data.get("chemical_system"),
            "constraints": request_data.get("constraints", {}),
            "max_candidates": int(request_data.get("max_candidates", 10)),
        }
        return await self._post_json("generate_candidates", payload)


class MatterSimAdapter(HttpExternalScienceAdapter):
    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__("mattersim", config=config)

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        action = request_data.get("action")
        if action != "simulate_candidates":
            return {"success": False, "adapter": self.name, "error": f"Unknown action {action}"}
        payload = {
            "candidates": request_data.get("candidates", []),
            "conditions": request_data.get("conditions", {}),
            "requested_metrics": request_data.get("requested_metrics", []),
        }
        return await self._post_json("simulate_candidates", payload)


class AlphaGenomeAdapter(HttpExternalScienceAdapter):
    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__("alphagenome", config=config)

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        action = request_data.get("action")
        if action != "predict_variant_effects":
            return {"success": False, "adapter": self.name, "error": f"Unknown action {action}"}
        payload = {
            "sequence": request_data.get("sequence"),
            "variants": request_data.get("variants", []),
            "assays": request_data.get("assays", []),
            "metadata": request_data.get("metadata", {}),
        }
        return await self._post_json("predict_variant_effects", payload)
