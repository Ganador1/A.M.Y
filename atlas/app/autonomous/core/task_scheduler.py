"""Simple task scheduler for Agent 3.

Provides priority-based selection with optional diversity enforcement via domain quota.
Supports stochastic top-k selection to break ties and increase diversity.
This is a minimal initial implementation; future versions may integrate async queues.
"""
from __future__ import annotations

from typing import List, Dict, Any, Iterable
from collections import defaultdict
import random
from app.core.bootstrap_logging import logger


def softmax(scores: List[float], temperature: float = 1.0) -> List[float]:
    """Compute softmax probabilities from scores.
    
    Parameters
    ----------
    scores: list of numeric scores
    temperature: controls randomness (lower = more deterministic, higher = more random)
    
    Returns
    -------
    list of probabilities summing to 1.0
    """
    import math
    
    if not scores:
        return []
    
    # Avoid overflow by subtracting max
    max_score = max(scores)
    exp_scores = [math.exp((s - max_score) / temperature) for s in scores]
    total = sum(exp_scores)
    
    if total == 0:
        # All scores are -inf or similar edge case
        return [1.0 / len(scores)] * len(scores)
    
    return [e / total for e in exp_scores]


class TaskScheduler:
    def __init__(
        self,
        diversity_quota: int | None = None,
        stochastic_topk: bool = False,
        topk_size: int = 10,
        selection_temperature: float = 0.5,
    ):
        """Initialize scheduler.

        Parameters
        ----------
        diversity_quota: if set, limits consecutive selections per domain to enforce diversity.
        stochastic_topk: if True, enables probabilistic selection from top-k candidates
        topk_size: size of top-k pool for stochastic selection (default 10)
        selection_temperature: temperature for softmax probabilities (0.1-1.0 recommended)
                              Lower values = more deterministic, higher = more random
        """
        self.diversity_quota = diversity_quota
        self.stochastic_topk = stochastic_topk
        self.topk_size = topk_size
        self.selection_temperature = selection_temperature
        self._recent_domain_counts: Dict[str, int] = defaultdict(int)
        
        if stochastic_topk:
            logger.info(
                "TaskScheduler initialized with stochastic top-k selection "
                "(k=%d, temperature=%.2f)",
                topk_size,
                selection_temperature,
            )

    def reset_cycle(self):
        self._recent_domain_counts.clear()

    def select(self, ranked_items: Iterable[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Select items from ranked candidates with optional stochastic top-k sampling.
        
        If stochastic_topk is enabled, selects probabilistically from top-k pool.
        Otherwise, uses deterministic greedy selection.
        
        Parameters
        ----------
        ranked_items: candidates already ranked by score (descending)
        limit: maximum number of items to select
        
        Returns
        -------
        list of selected items (may be < limit if not enough candidates)
        """
        ranked_list = list(ranked_items)
        
        if not self.stochastic_topk:
            # Original deterministic selection
            return self._deterministic_select(ranked_list, limit)
        else:
            # New stochastic top-k selection
            return self._stochastic_select(ranked_list, limit)
    
    def _deterministic_select(self, ranked_items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Original greedy selection with diversity quota enforcement."""
        selected: List[Dict[str, Any]] = []
        for item in ranked_items:
            if len(selected) >= limit:
                break
            domain = str(item.get("domain", "default"))
            if self.diversity_quota is not None and self._recent_domain_counts[domain] >= self.diversity_quota:
                continue
            selected.append(item)
            self._recent_domain_counts[domain] += 1
        logger.debug("Scheduler selected %d items (limit=%d, mode=deterministic)", len(selected), limit)
        return selected
    
    def _stochastic_select(self, ranked_items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
        """Stochastic selection from top-k pool using softmax probabilities.
        
        This helps break ties and increase diversity by adding controlled randomness.
        """
        selected: List[Dict[str, Any]] = []
        available = ranked_items.copy()
        
        while len(selected) < limit and available:
            # Create top-k pool
            pool_size = min(self.topk_size, len(available))
            topk_pool = available[:pool_size]
            
            # Extract scores for softmax
            scores = [item.get("score", 0.0) for item in topk_pool]
            
            # Compute selection probabilities
            probabilities = softmax(scores, temperature=self.selection_temperature)
            
            # Sample one candidate
            chosen_idx = random.choices(range(len(topk_pool)), weights=probabilities, k=1)[0]
            chosen = topk_pool[chosen_idx]
            
            # Check diversity quota
            domain = str(chosen.get("domain", "default"))
            if self.diversity_quota is not None and self._recent_domain_counts[domain] >= self.diversity_quota:
                # Remove from available and try again
                available.remove(chosen)
                continue
            
            # Add to selection
            selected.append(chosen)
            self._recent_domain_counts[domain] += 1
            available.remove(chosen)
        
        logger.debug(
            "Scheduler selected %d items (limit=%d, mode=stochastic, k=%d, temp=%.2f)",
            len(selected),
            limit,
            self.topk_size,
            self.selection_temperature,
        )
        return selected

__all__ = ["TaskScheduler"]
