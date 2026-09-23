"""Hypothesis mutation operators for mathematical conjectures and scientific hypotheses.

Each hypothesis is represented as a dict with at minimum:
    id: str
    statement: str
    metadata: dict (optional)

Mutations return new hypothesis dicts with a parent_id reference for traceability.
This is a minimal initial implementation with simple text-level heuristics.
"""
from __future__ import annotations

from typing import Dict, Any, List, Callable
import re
import uuid
import random
from app.core.bootstrap_logging import logger

Mutation = Callable[[Dict[str, Any]], Dict[str, Any] | None]


class HypothesisMutator:
    def __init__(self) -> None:
        self._mutators: List[Mutation] = [
            self._scale_numeric_constants,
            self._add_missing_condition_stub,
            self._relax_inequality,
            self._semantic_synonym_injection,
        ]

    def mutate_batch(self, hypotheses: List[Dict[str, Any]], max_mutations: int = 3) -> List[Dict[str, Any]]:
        """Apply mutators sequentially until max_mutations reached."""
        results: List[Dict[str, Any]] = []
        for hyp in hypotheses:
            for mut in self._mutators:
                if len(results) >= max_mutations:
                    return results
                try:
                    new_h = mut(hyp)
                except (ValueError, TypeError) as exc:
                    logger.debug("Mutation %s failed for %s: %s", mut.__name__, hyp.get("id"), exc)
                    new_h = None
                if new_h:
                    results.append(new_h)
        return results

    # --- Individual mutators -------------------------------------------------
    def _scale_numeric_constants(self, hyp: Dict[str, Any]) -> Dict[str, Any] | None:
        stmt = hyp.get("statement", "")
        numbers = re.findall(r"(?<![A-Za-z])([0-9]{1,3})", stmt)
        if not numbers:
            return None
        original = numbers[0]
        try:
            val = int(original)
        except ValueError:
            return None
        scaled = val * 2 + 1  # simple heuristic
        mutated_stmt = stmt.replace(original, str(scaled), 1)
        return self._build_child(hyp, mutated_stmt, op="scale_constant")

    def _add_missing_condition_stub(self, hyp: Dict[str, Any]) -> Dict[str, Any] | None:
        stmt = hyp.get("statement", "")
        if " such that " in stmt:
            return None
        mutated_stmt = f"{stmt} such that (additional regularity conditions hold)"
        return self._build_child(hyp, mutated_stmt, op="add_condition_stub")

    def _relax_inequality(self, hyp: Dict[str, Any]) -> Dict[str, Any] | None:
        stmt = hyp.get("statement", "")
        if "≤" not in stmt and "<=" not in stmt:
            return None
        mutated_stmt = stmt.replace("≤", "<").replace("<=", "<")
        if mutated_stmt == stmt:
            return None
        return self._build_child(hyp, mutated_stmt, op="relax_inequality")

    def _semantic_synonym_injection(self, hyp: Dict[str, Any]) -> Dict[str, Any] | None:
        stmt = hyp.get("statement", "")
        if not stmt:
            return None
        synonym_map = {
            "increase": ["enhance", "boost", "amplify"],
            "decrease": ["reduce", "diminish", "lower"],
            "improves": ["enhances", "boosts"],
            "stability": ["robustness", "resilience"],
            "interaction": ["association", "coupling"],
            "efficiency": ["performance", "throughput"],
        }
        tokens = stmt.split()
        random.shuffle(tokens)
        # Work on a shuffled copy but apply to original order: pick first synonym candidate
        for tok in tokens:
            key = tok.lower().strip(",.;:")
            if key in synonym_map:
                replacement = random.choice(synonym_map[key])
                mutated_stmt = stmt.replace(tok, replacement, 1)
                if mutated_stmt != stmt:
                    return self._build_child(hyp, mutated_stmt, op="semantic_synonym")
        return None

    # --- Helpers --------------------------------------------------------------
    def _build_child(self, parent: Dict[str, Any], new_statement: str, op: str) -> Dict[str, Any]:
        child = {
            "id": str(uuid.uuid4()),
            "parent_id": parent.get("id"),
            "statement": new_statement,
            "mutation_op": op,
            "metadata": {
                **(parent.get("metadata") or {}),
                "mutation_parent": parent.get("id"),
            },
        }
        logger.debug("Generated mutation %s from %s", child["id"], parent.get("id"))
        return child

__all__ = ["HypothesisMutator"]
