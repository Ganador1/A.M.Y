"""Unified entrypoint for optional external AI-for-science adapters."""

from __future__ import annotations

from typing import Any, Dict

from app.config.config_loader import load_config_section
from app.core.base_service import BaseService
from app.services.external_science.paperqa2_adapter import PaperQA2Adapter
from app.services.external_science.remote_adapters import AlphaGenomeAdapter, MatterGenAdapter, MatterSimAdapter


class ExternalScienceService(BaseService):
    def __init__(self, adapters: Dict[str, Any] | None = None):
        super().__init__("ExternalScienceService")
        self.config = load_config_section("external_science") or {}
        self.adapters = adapters or {
            "paperqa2": PaperQA2Adapter((self.config.get("paperqa2") or {})),
            "mattergen": MatterGenAdapter((self.config.get("mattergen") or {})),
            "mattersim": MatterSimAdapter((self.config.get("mattersim") or {})),
            "alphagenome": AlphaGenomeAdapter((self.config.get("alphagenome") or {})),
        }

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        action = str(request_data.get("action") or "").strip()
        if action == "list_adapters":
            return {
                "success": True,
                "adapters": {
                    name: adapter.get_status()
                    for name, adapter in self.adapters.items()
                },
            }

        if action == "paperqa2_verify_claim":
            return await self.adapters["paperqa2"].process_request(
                {
                    **request_data,
                    "action": "verify_claim",
                }
            )
        if action == "paperqa2_answer_question":
            return await self.adapters["paperqa2"].process_request(
                {
                    **request_data,
                    "action": "answer_question",
                }
            )
        if action == "mattergen_generate_candidates":
            return await self.adapters["mattergen"].process_request(
                {
                    **request_data,
                    "action": "generate_candidates",
                }
            )
        if action == "mattersim_simulate_candidates":
            return await self.adapters["mattersim"].process_request(
                {
                    **request_data,
                    "action": "simulate_candidates",
                }
            )
        if action == "alphagenome_predict_variant_effects":
            return await self.adapters["alphagenome"].process_request(
                {
                    **request_data,
                    "action": "predict_variant_effects",
                }
            )
        return {"success": False, "error": f"Unknown action {action}", "service": self.name}


external_science_service = ExternalScienceService()
