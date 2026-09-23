"""Resource budget allocation for Agent 3.

Distributes a global compute/iteration budget across candidate items based on their score
and estimated cost, attempting to maximize score gain under constraint.
Initial strategy: greedy ratio (score / (cost+epsilon)).
"""
from __future__ import annotations

from typing import List, Dict, Any
from app.core.bootstrap_logging import logger


class BudgetAllocator:
    def __init__(self, total_budget: float):
        self.total_budget = total_budget

    def allocate(self, items: List[Dict[str, Any]], cost_key: str = "estimated_cost") -> List[Dict[str, Any]]:
        """Greedy allocation maximizing score per unit cost until budget exhausted."""
        if self.total_budget <= 0:
            logger.warning("Total budget is non-positive; returning empty allocation")
            return []
        scored: List[tuple[float, float, float, Dict[str, Any]]] = []
        for it in items:
            score = float(it.get("score", 0.0))
            cost = max(float(it.get(cost_key, 1.0)), 1e-6)  # avoid div by zero
            ratio = score / cost
            scored.append((ratio, score, cost, it))
        scored.sort(key=lambda t: t[0], reverse=True)

        allocation: List[Dict[str, Any]] = []
        remaining = self.total_budget
        for ratio, score, cost, item in scored:
            if cost <= remaining:
                allocation.append(item)
                remaining -= cost
            if remaining <= 0:
                break
        logger.debug(
            "Allocated %d items consuming %.4f / %.4f budget",
            len(allocation),
            self.total_budget - remaining,
            self.total_budget,
        )
        return allocation

__all__ = ["BudgetAllocator"]
