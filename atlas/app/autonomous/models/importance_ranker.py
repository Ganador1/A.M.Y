"""Heurístico de ranking de importancia científica.

Combina señales ligeras (frecuencia en literatura, dependencia de otras conjeturas,
impacto potencial declarado) en un score normalizado 0..1.

API:
    rank(items: List[dict]) -> List[dict] (añade 'importance')
"""
from __future__ import annotations

from typing import List, Dict, Any
from math import log1p
from app.core.bootstrap_logging import logger


class ImportanceRanker:
    def __init__(self, w_freq: float = 0.4, w_dependency: float = 0.3, w_impact: float = 0.3):
        self.w_freq = w_freq
        self.w_dependency = w_dependency
        self.w_impact = w_impact

    def compute_importance(self, item: Dict[str, Any]) -> float:
        citations = float(item.get("literature_frequency", 0.0))  # conteo bruto
        deps = float(item.get("dependency_count", 0.0))
        impact = float(item.get("impact_potential", 0.0))  # 0..1 estimado
        # Escalado log para frecuencia
        freq_component = log1p(citations) / 10.0  # amortiguar > ~22000 => ~1
        dep_component = min(1.0, deps / 25.0)  # saturar en 25 dependencias
        impact_component = max(0.0, min(1.0, impact))
        score = self.w_freq * freq_component + self.w_dependency * dep_component + self.w_impact * impact_component
        return max(0.0, min(1.0, score))

    def rank(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        ranked = []
        for it in items:
            try:
                importance = self.compute_importance(it)
            except (ValueError, TypeError) as exc:
                logger.warning("Importance computation failed for %s: %s", it, exc)
                importance = 0.0
            enriched = dict(it)
            enriched["importance"] = importance
            # Backwards-compatible API expected by tests
            enriched["importance_score"] = importance
            ranked.append(enriched)
        ranked.sort(key=lambda d: d["importance"], reverse=True)
        # Assign ranks (1 = highest)
        for i, item in enumerate(ranked, start=1):
            item["rank"] = i
        return ranked

__all__ = ["ImportanceRanker"]
