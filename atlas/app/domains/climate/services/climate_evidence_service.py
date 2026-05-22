"""Servicio de evidencia climática basado en el dataset GISTEMP."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional

from app.domains.climate.data_utils import load_gistemp_dataset, resolve_gistemp_path
from app.services.base_service import BaseService


@dataclass
class ClimateEvidenceResult:
    support_score: float
    coverage: float
    mean_signal: float
    context: Dict[str, Any]


class ClimateEvidenceService(BaseService):
    def __init__(self, gistemp_path: Optional[str | Path] = None) -> None:
        super().__init__("ClimateEvidenceService")
        self._gistemp_path = resolve_gistemp_path(gistemp_path)
        self._cache: Optional[List[Dict[str, Any]]] = None

    def _entries(self) -> List[Dict[str, Any]]:
        if self._cache is None:
            self._cache = load_gistemp_dataset(self._gistemp_path)
        return self._cache

    @staticmethod
    def _compute_support(anomalies: List[float]) -> ClimateEvidenceResult:
        if not anomalies:
            return ClimateEvidenceResult(0.0, 0.0, 0.0, {})
        window = anomalies[-30:] if len(anomalies) >= 30 else anomalies
        baseline = anomalies[:30] if len(anomalies) >= 30 else anomalies
        avg_recent = mean(window)
        avg_baseline = mean(baseline)
        delta = avg_recent - avg_baseline
        support = max(0.0, min(1.0, (delta + 1.5) / 3.0))
        coverage = min(1.0, len(window) / 30.0)
        mean_signal = min(1.0, abs(delta))
        context = {
            "avg_recent": round(avg_recent, 3),
            "avg_baseline": round(avg_baseline, 3),
            "delta": round(delta, 3),
            "window_years": len(window),
        }
        return ClimateEvidenceResult(support, coverage, mean_signal, context)

    async def process_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        action = payload.get("action")
        if action != "climate_evidence":
            return {"success": False, "error": f"Acción no soportada: {action}"}

        entries = self._entries()
        anomalies = [
            float(entry["J-D"])
            for entry in entries
            if isinstance(entry.get("J-D"), (int, float))
        ]
        result = self._compute_support(anomalies)

        return {
            "success": True,
            "support_score": round(result.support_score, 3),
            "coverage": round(result.coverage, 3),
            "mean_signal": round(result.mean_signal, 3),
            "analysis": result.context,
        }
