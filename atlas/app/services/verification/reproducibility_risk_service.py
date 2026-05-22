"""Reproducibility Risk Service (Stub)
Calcula un score heurístico de riesgo de no-reproducibilidad basado en señales simples.
"""
from __future__ import annotations
from typing import Dict, Any
import math

class ReproducibilityRiskService:
    def __init__(self):
        self.version = "v0"

    def assess(self, *, evidence_strength: float | None, stability_score: float | None, data_sensitivity: str | None = None, dependency_count: int | None = None) -> Dict[str, Any]:
        e = evidence_strength if evidence_strength is not None else 0.5
        s = stability_score if stability_score is not None else 0.6
        dep = dependency_count if dependency_count is not None else 5
        sens_factor = 0.15 if (data_sensitivity or "none") in {"restricted", "sensitive"} else 0.0
        # Riesgo base: más bajo cuando evidencia y estabilidad altas
        base = 1.0 - math.sqrt(e * s)
        dep_factor = min(0.25, 0.02 * dep)
        risk = min(1.0, max(0.0, base + dep_factor + sens_factor))
        return {
            "risk_score": round(risk, 4),
            "components": {
                "base": round(base, 4),
                "dependency_factor": round(dep_factor, 4),
                "sensitivity_factor": sens_factor,
            },
            "version": self.version,
        }

reproducibility_risk_service = ReproducibilityRiskService()
