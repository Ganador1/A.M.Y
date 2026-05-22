"""LLM Routing Service (Stub)
Selección heurística de modelo según complejidad / tamaño del prompt.
"""
from __future__ import annotations
from typing import Dict, Any

class LLMRoutingService:
    def __init__(self):
        # catálogos simples
        self.tiers = {
            "small": {"max_tokens": 2_000, "latency_ms": 200},
            "medium": {"max_tokens": 8_000, "latency_ms": 600},
            "large": {"max_tokens": 32_000, "latency_ms": 1500},
        }
        self.models = {
            "small": ["gpt-4o-mini", "claude-haiku"],
            "medium": ["gpt-4o", "claude-sonnet"],
            "large": ["gpt-4o-extended", "claude-opus"],
        }
        self.version = "v0"

    def classify_prompt(self, prompt: str) -> str:
        if (length := len(prompt)) < 1_500:
            return "small"
        if length < 6_000:
            return "medium"
        return "large"

    def route(self, prompt: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
        tier = self.classify_prompt(prompt)
        # heurística: si metadata indica alta_precision -> subir un tier (si posible)
        if metadata and metadata.get("high_precision"):
            tier = "medium" if tier == "small" else tier
        models = self.models[tier]
        chosen = models[0]
        return {
            "tier": tier,
            "candidate_models": models,
            "chosen_model": chosen,
            "est_latency_ms": self.tiers[tier]["latency_ms"],
        }

llm_routing_service = LLMRoutingService()
