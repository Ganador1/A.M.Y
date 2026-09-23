"""Unified Policy Engine
Aplica pesos configurables y reglas para decidir: halt | approve | refine | reject.
Config principal: `config/policy_engine_config.yaml`.
Soporta:
- Pesos con signo (riesgos negativos)
- Umbrales multi-regla (halt, approve, refine)
- Normalización ignorando scores ausentes (neutral)
- Caps de valores intermedios
- Logging JSONL con deltas de contribución
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import datetime
import aiofiles
import asyncio

from app.config.config_loader import load_config_section, reload_section, get_config
from app.core.bootstrap_logging import logger
from app.exceptions.infrastructure.cache import CacheError

# decisions log path will be resolved from configuration (see _load_config())

@dataclass
class PolicyDecision:
    status: str
    composite: float
    reasons: List[str]
    raw_scores: Dict[str, Any]
    contributions: Dict[str, float]
    ordered_factors: List[str]
    timestamp: str
    config_version: Optional[int] = None

class PolicyEngineService:
    def __init__(self) -> None:
        self.config = self._load_config()
        logger.info("✅ Unified PolicyEngineService inicializado")

    def _load_config(self) -> Dict[str, Any]:
        # Carga sección desde archivo `config/policy_engine_config.yaml` (y overrides por ATLAS_ENV)
        default_log_path = str(get_config('policy_engine_config.logging.decisions_path', 'data/policy_decisions.jsonl'))
        data = load_config_section('policy_engine_config')
        if not data:  # fallback interno mínimo
            data = {
                "version": 1,
                "weights": {
                    "novelty": 0.15,
                    "evidence_strength": 0.20,
                    "reproducibility_risk": -0.20,
                    "coverage": 0.10,
                    "diversity": 0.05,
                    "consistency": 0.10,
                    "peer_review": 0.15,
                    "methodological_rigor": 0.10,
                    "safety": 0.05,
                },
                "thresholds": {
                    "approve": {"composite_min": 0.62, "max_reproducibility_risk": 0.50},
                    "refine": {"composite_min": 0.45, "composite_max": 0.65},
                    "halt": {"composite_max": 0.30, "min_reproducibility_risk": 0.80},
                },
                "normalization": {"missing_score_policy": "treat_as_neutral"},
                "caps": {"max_positive": 1.0, "min_negative": -1.0},
                "logging": {"decisions_path": default_log_path, "include_deltas": True},
            }
        # Asegurar claves básicas
        data.setdefault("weights", {})
        data.setdefault("thresholds", {})
        data.setdefault("normalization", {"missing_score_policy": "treat_as_neutral"})
        data.setdefault("caps", {"max_positive": 1.0, "min_negative": -1.0})
        logging_cfg = data.setdefault("logging", {})
        logging_cfg.setdefault("decisions_path", default_log_path)
        logging_cfg.setdefault("include_deltas", True)
        return data

    def reload(self) -> Dict[str, Any]:
        # Recarga desde disco invalidando cache
        new_cfg = reload_section('policy_engine_config')
        if not new_cfg:
            self.config = self._load_config()
        else:
            default_log_path = str(get_config('policy_engine_config.logging.decisions_path', 'data/policy_decisions.jsonl'))
            new_cfg.setdefault("weights", {})
            new_cfg.setdefault("thresholds", {})
            new_cfg.setdefault("normalization", {"missing_score_policy": "treat_as_neutral"})
            new_cfg.setdefault("caps", {"max_positive": 1.0, "min_negative": -1.0})
            logging_cfg = new_cfg.setdefault("logging", {})
            logging_cfg.setdefault("decisions_path", default_log_path)
            logging_cfg.setdefault("include_deltas", True)
            self.config = new_cfg
        return {"success": True, "config": self.config}

    def _apply_caps(self, value: float) -> float:
        caps = self.config.get("caps", {})
        return max(caps.get("min_negative", -1.0), min(caps.get("max_positive", 1.0), value))

    def decide(self, scores: Dict[str, Any], *, hypothesis_id: Optional[str] = None) -> Dict[str, Any]:
        cfg = self.config
        weights: Dict[str, float] = cfg.get("weights", {})
        norms = cfg.get("normalization", {})
        thresholds = cfg.get("thresholds", {})
        missing_policy = norms.get("missing_score_policy", "treat_as_neutral")
        contributions: Dict[str, float] = {}
        composite = 0.0
        abs_weight_sum = 0.0
        used_scores: Dict[str, Any] = {}

        for metric, weight in weights.items():
            raw = scores.get(metric)
            if raw is None:
                if missing_policy == "zero":
                    raw_val = 0.0
                else:  # neutral -> ignora la contribución (no suma peso)
                    continue
            else:
                try:
                    raw_val = float(raw)
                except CacheError:
                    raw_val = 0.0
            capped = self._apply_caps(raw_val)
            contrib = weight * capped
            composite += contrib
            contributions[metric] = contrib
            abs_weight_sum += abs(weight)
            used_scores[metric] = raw_val

        normalized = composite / abs_weight_sum if abs_weight_sum > 0 else 0.0

        # Reglas
        reasons: List[str] = []
        status = "reject"
        halt_cfg = thresholds.get("halt", {})
        approve_cfg = thresholds.get("approve", {})
        refine_cfg = thresholds.get("refine", {})

        repro_risk = scores.get("reproducibility_risk") or scores.get("reproducibility_likelihood")
        try:
            repro_risk = float(repro_risk) if repro_risk is not None else None
        except CacheError:
            repro_risk = None

        # HALT
        halt_hit = False
        if halt_cfg:
            comp_max = halt_cfg.get("composite_max")
            min_repro = halt_cfg.get("min_reproducibility_risk")
            if (comp_max is not None and normalized < comp_max) or (min_repro is not None and repro_risk is not None and repro_risk > min_repro):
                status = "halt"
                if comp_max is not None and normalized < comp_max:
                    reasons.append(f"low_composite:{normalized:.3f}<={comp_max}")
                if min_repro is not None and repro_risk is not None and repro_risk > min_repro:
                    reasons.append(f"high_repro_risk:{repro_risk:.3f}>{min_repro}")
                halt_hit = True

        if not halt_hit:
            # APPROVE
            approve_min = approve_cfg.get("composite_min")
            max_repro = approve_cfg.get("max_reproducibility_risk")
            if approve_min is not None and normalized >= approve_min and (max_repro is None or repro_risk is None or repro_risk <= max_repro):
                status = "approve"
                reasons.append(f"composite_ok:{normalized:.3f}>={approve_min}")
                if max_repro is not None and repro_risk is not None:
                    reasons.append(f"repro_risk_ok:{repro_risk:.3f}<={max_repro}")
            else:
                # REFINE
                refine_min = refine_cfg.get("composite_min")
                refine_max = refine_cfg.get("composite_max")
                if refine_min is not None and normalized >= refine_min and (refine_max is None or normalized < refine_max):
                    status = "refine"
                    reasons.append(f"composite_mid:{normalized:.3f}")
                else:
                    status = "reject"
                    reasons.append(f"composite_low:{normalized:.3f}")

        # Ordenar factores por |contrib|
        ordered_factors = [k for k, _ in sorted(contributions.items(), key=lambda kv: abs(kv[1]), reverse=True)]
        decision = PolicyDecision(
            status=status,
            composite=round(float(normalized), 4),
            reasons=reasons,
            raw_scores=used_scores,
            contributions={k: round(v, 4) for k, v in contributions.items()},
            ordered_factors=ordered_factors,
            timestamp=datetime.datetime.utcnow().isoformat(),
            config_version=cfg.get("version")
        )

        # Logging
        # Eliminado DECISIONS_LOG; se resolverá en tiempo de ejecución desde config
        log_path = Path(cfg.get("logging", {}).get("decisions_path", "data/policy_decisions.jsonl"))
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a", encoding="utf-8") as f:
            record = decision.__dict__ | ({"hypothesis_id": hypothesis_id} if hypothesis_id else {})
            f.write(json.dumps(record) + "\n")
        return {"success": True, "decision": decision.__dict__}

policy_engine_service = PolicyEngineService()
