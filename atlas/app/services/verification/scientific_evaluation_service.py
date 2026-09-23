"""Scientific Evaluation Service

MVP: Proporciona un scoring unificado para hipótesis o ciclos de investigación combinando señales existentes
(novelty_score, evidence_strength, robustness/stability, benchmark placeholders) en un diccionario normalizado.

Diseño inicial (sin persistencia DB para velocidad):
- Entrada: dict con al menos hypothesis_id (opcional), y/o contenido textual.
- Recupera si es posible: novelty_score y evidence_strength (si están en la hipótesis almacenada o payload).
- Calcula sub-scores adicionales heurísticos (methodological_rigor, reproducibility_likelihood) con funciones simples.
- Agrega un composite_score ponderado configurable.
- Cache in-memory simple (LRU por id) para evitar recomputaciones frecuentes.

Futuro (no implementado aquí):
- Persistencia en tabla evaluation_records.
- Versionado de fórmula (stored formula_version).
- Ajuste dinámico de pesos vía configuración externa.
- Auditoría de explicaciones y trazabilidad completa.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Dict, Any, Optional
import math
import time
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import EvaluationRecord
from app.exceptions.domain.biology import BiologyError

# Pesos iniciales (pueden migrar a settings luego)
WEIGHTS = {
    "novelty": 0.25,
    "evidence": 0.30,
    "robustness": 0.20,
    "methodological_rigor": 0.15,
    "reproducibility": 0.10,
}

@dataclass(frozen=True)
class EvaluationInput:
    hypothesis_id: Optional[str] = None
    novelty_score: Optional[float] = None
    evidence_strength: Optional[float] = None
    stability_score: Optional[float] = None
    text: Optional[str] = None
    coverage_ratio: Optional[float] = None  # nueva señal opcional
    peer_review_consensus: Optional[float] = None  # nueva señal opcional

class ScientificEvaluationService:
    def __init__(self):
        self.weights = WEIGHTS.copy()
        self.formula_version = "v1"
        # Lazy import flag
        self._hypothesis_service: Optional[object] = None

    def _get_hypothesis_service(self):  # Lazy load para evitar ciclos
        if self._hypothesis_service is None:
            try:
                from app.services.hypothesis_persistence import HypothesisPersistenceService  # noqa
                self._hypothesis_service = HypothesisPersistenceService()
            except BiologyError:  # pragma: no cover
                self._hypothesis_service = None
        return self._hypothesis_service

    # --- Sub-score calculators ---
    def _score_methodological_rigor(self, text: Optional[str]) -> float:
        if not text:
            return 0.5
        # Heurística extremadamente simple: más términos metodológicos => mayor score
        keywords = ["control", "random", "statistical", "ablation", "sensitivity", "baseline"]
        hits = sum(1 for k in keywords if k in text.lower())
        return min(1.0, 0.3 + hits * 0.1)

    def _score_reproducibility_likelihood(self, evidence: Optional[float], stability: Optional[float]) -> float:
        e = evidence if evidence is not None else 0.5
        s = stability if stability is not None else 0.6
        # Simple mezcla geométrica suavizada
        return math.sqrt(e * s)

    def _normalize(self, value: Optional[float], default: float = 0.5) -> float:
        if value is None or math.isnan(value):
            return default
        return max(0.0, min(1.0, float(value)))

    def _composite(self, components: Dict[str, float]) -> float:
        total_w = sum(self.weights.values())
        agg = 0.0
        for k, w in self.weights.items():
            agg += components.get(k, 0.0) * (w / total_w)
        return round(agg, 4)

    @lru_cache(maxsize=256)
    def evaluate_cached(self, cache_key: str, payload_fingerprint: str) -> Dict[str, Any]:  # noqa: D401
        # Guardamos payload_fingerprint solo para invalidaciones futuras (no usada en MVP)
        return {"_fingerprint": payload_fingerprint, "_ts": time.time()}

    def evaluate(self, data: EvaluationInput) -> Dict[str, Any]:
        novelty = data.novelty_score
        evidence = data.evidence_strength
        robustness = data.stability_score

        # Si falta información y tenemos hypothesis_id intentar obtenerla
        if data.hypothesis_id and (novelty is None or evidence is None):
            svc = self._get_hypothesis_service()
            if svc is not None and hasattr(svc, "get_hypothesis"):
                try:
                    res = getattr(svc, "get_hypothesis")({"hypothesis_uuid": data.hypothesis_id})  # type: ignore[attr-defined]
                    if res.get("success"):
                        hyp = res.get("hypothesis", {})
                        # Heurística inicial: usar confidence_score como proxy evidence si falta
                        if evidence is None:
                            evidence = hyp.get("confidence_score")
                        # novelty_score todavía no está almacenado; placeholder derivado de dispersion de variables
                        if novelty is None:
                            vars_ = hyp.get("variables") or []
                            novelty = min(1.0, 0.3 + 0.05 * len(vars_))
                except BiologyError:
                    pass

        novelty = self._normalize(novelty)
        evidence = self._normalize(evidence)
        robustness = self._normalize(robustness)
        methodological_rigor = self._score_methodological_rigor(data.text)
        reproducibility = self._score_reproducibility_likelihood(evidence, robustness)

        components = {
            "novelty": novelty,
            "evidence": evidence,
            "robustness": robustness,
            "methodological_rigor": methodological_rigor,
            "reproducibility": reproducibility,
        }
        composite = self._composite(components)

        # --- Integración señales externas opcionales (coverage & peer review) ---
        coverage = self._normalize(data.coverage_ratio, default=0.0)
        consensus = self._normalize(data.peer_review_consensus, default=0.0)
        coverage_boost = 1.0 + 0.10 * coverage
        consensus_boost = 1.0 + 0.10 * consensus
        composite_adjusted = round(composite * coverage_boost * consensus_boost, 4)

        result = {
            "formula_version": self.formula_version,
            "components": components,
            "composite_score": composite_adjusted,
            "explanation": {
                "weights": self.weights,
                "aggregation": "weighted_average",
                "external_signals": {
                    "coverage_ratio": coverage,
                    "peer_review_consensus": consensus,
                    "coverage_boost": round(coverage_boost, 4),
                    "consensus_boost": round(consensus_boost, 4),
                    "pre_adjustment_score": composite,
                },
            },
        }

        # Persistencia (best-effort)
        try:
            db: Session = SessionLocal()
            rec = EvaluationRecord(
                hypothesis_id=data.hypothesis_id,
                inputs={
                    "hypothesis_id": data.hypothesis_id,
                    "coverage_ratio": coverage,
                    "peer_review_consensus": consensus,
                },
                normalized={k: float(v) for k, v in components.items()},
                components={"detail": "heuristic_v1"},
                weights=self.weights,
                composite_score=composite_adjusted,
                formula_version=self.formula_version,
                formula_hash=None,
            )
            db.add(rec)
            db.commit()
        except BiologyError:  # pragma: no cover
            try:
                db.rollback()  # type: ignore
            except BiologyError:
                pass
        finally:
            try:
                db.close()  # type: ignore
            except BiologyError:
                pass
        return result

# Instancia singleton simple
scientific_evaluation_service = ScientificEvaluationService()
