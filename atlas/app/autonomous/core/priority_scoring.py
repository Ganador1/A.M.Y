"""Priority scoring component for Agent 3.

Implements a multi-factor scoring formula::

    S = w1*importance + w2*proveability + w3*novelty + w4*information_gain - w5*estimated_cost

Expected numeric factors in each input item:
    - importance
    - proveability
    - novelty (or alternatively ``novelty_score`` if produced by a prior evaluation stage)
    - information_gain
    - estimated_cost (will be subtracted)

Fallbacks / robustness:
    * If ``novelty`` is absent but ``novelty_score`` is present, that value is used.
    * Missing keys default to 0.0 (including cost) to keep the scorer tolerant of partial data.

Usage::

    scorer = PriorityScorer()
    score = scorer.compute_score(item_dict)

The scorer is stateless aside from its weight configuration; weights can be updated at runtime.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any
from app.core.bootstrap_logging import logger


@dataclass
class WeightConfig:
    importance: float = 1.0
    proveability: float = 1.0
    novelty: float = 1.0
    information_gain: float = 1.0
    estimated_cost: float = 1.0  # cost is subtracted
    diversity_bonus: float = 0.15  # bonus for unique candidates (0.0-0.3 recommended)

    def as_dict(self) -> Dict[str, float]:  # convenience
        return {
            "importance": self.importance,
            "proveability": self.proveability,
            "novelty": self.novelty,
            "information_gain": self.information_gain,
            "estimated_cost": self.estimated_cost,
            "diversity_bonus": self.diversity_bonus,
        }


class PriorityScorer:
    """Calculates priority scores for candidate scientific objects (e.g., conjectures)."""

    def __init__(self, weights: WeightConfig | None = None):
        self.weights = weights or WeightConfig()
        logger.debug("PriorityScorer initialized with weights %s", self.weights.as_dict())

    def update_weights(self, **kwargs: float) -> None:
        """Update weight configuration incrementally.
        Unknown keys are ignored to keep safety.
        """
        for k, v in kwargs.items():
            if hasattr(self.weights, k) and isinstance(v, (int, float)):
                setattr(self.weights, k, float(v))
        logger.info("PriorityScorer weights updated: %s", self.weights.as_dict())

    def compute_score(self, item: Dict[str, Any]) -> float:
        """Backward-compatible alias: keep compute_score as core method, but
        expose `score()` as the simple API expected by higher-level loops/tests."""        """Compute the composite score for an item.

        Parameters
        ----------
        item: dict containing numeric factors (0..1 recommended) and optionally domain metadata.

        Returns
        -------
        float: composite score; higher means higher priority.
        """
        w = self.weights
        # Extract factors with safe defaults
        importance = float(item.get("importance", 0.0))
        proveability = float(item.get("proveability", 0.0))
        # Accept alternate key 'novelty_score' if 'novelty' not directly provided
        novelty_raw = item.get("novelty", None)
        if novelty_raw is None:
            novelty_raw = item.get("novelty_score", 0.0)
        novelty = float(novelty_raw)
        info_gain = float(item.get("information_gain", 0.0))
        est_cost = float(item.get("estimated_cost", 0.0))

        score = (
            w.importance * importance
            + w.proveability * proveability
            + w.novelty * novelty
            + w.information_gain * info_gain
            - w.estimated_cost * est_cost
        )
        logger.debug(
            "Computed score %.4f (importance=%.3f, proveability=%.3f, novelty=%.3f, info_gain=%.3f, cost=%.3f)",
            score,
            importance,
            proveability,
            novelty,
            info_gain,
            est_cost,
        )
        return score

    def score(self, item: Dict[str, Any]) -> float:
        """Compatibility wrapper that returns a normalized score in [0,1]."""
        try:
            raw = self.compute_score(item)
            # Clamp to [0,1] for compatibility with callers/tests
            return max(0.0, min(1.0, float(raw)))
        except Exception:
            return 0.0

    def rank(self, items: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """Return a new list of items annotated with 'score' sorted descending.
        
        Applies diversity bonus based on uniqueness of candidate names/IDs.
        """
        ranked = []
        
        # Phase 1: Compute base scores
        for it in items:
            try:
                it_score = self.compute_score(it)
            except (ValueError, TypeError) as exc:  # expected numeric conversion issues
                logger.warning("Score computation failed for item %s: %s", it, exc)
                it_score = float("nan")
            enriched = dict(it)
            enriched["base_score"] = it_score
            ranked.append(enriched)
        
        # Phase 2: Apply diversity bonus
        if self.weights.diversity_bonus > 0.0:
            # Extract unique identifiers (prefer 'name', fallback to 'id' or 'title')
            seen_identifiers = set()
            for item in ranked:
                identifier = item.get("name") or item.get("id") or item.get("title") or ""
                seen_identifiers.add(str(identifier).strip().lower())
            
            # Calculate diversity ratio (0.0-1.0)
            total_candidates = len(ranked)
            unique_count = len(seen_identifiers)
            diversity_ratio = unique_count / total_candidates if total_candidates > 0 else 0.0
            
            # Apply bonus scaled by diversity ratio
            bonus_amount = self.weights.diversity_bonus * diversity_ratio
            
            logger.debug(
                "Diversity bonus: %.4f (unique=%d/%d, ratio=%.3f, weight=%.3f)",
                bonus_amount,
                unique_count,
                total_candidates,
                diversity_ratio,
                self.weights.diversity_bonus,
            )
            
            # Add bonus to each candidate's score
            for item in ranked:
                base = item.get("base_score", 0.0)
                item["diversity_bonus"] = bonus_amount
                item["score"] = base + bonus_amount
        else:
            # No diversity bonus - just copy base_score to score
            for item in ranked:
                item["score"] = item.get("base_score", 0.0)
                item["diversity_bonus"] = 0.0
        
        # Phase 3: Sort by final score
        ranked.sort(key=lambda d: (d.get("score") if d.get("score") is not None else float("nan")), reverse=True)
        return ranked

__all__ = ["WeightConfig", "PriorityScorer"]
