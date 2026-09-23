from __future__ import annotations
from typing import List, Dict, Any

"""Minimal ranking utilities for conjectures.

Diseño no intrusivo: se invoca solo cuando se necesita reordenar
una lista de conjeturas. No añade dependencias externas ni cambia
el flujo de otros agentes.
"""


def score_conjecture(c: Dict[str, Any]) -> float:
    """Compute a simple score using available lightweight signals.
    Prioritizes explicit novelty/evidence if present, else length heuristic.
    """
    novelty = float(c.get("novelty", 0.0))
    evidence = float(c.get("evidence_ratio", 0.0))
    complexity_penalty = 0.0
    stmt = c.get("statement") or c.get("text") or ""
    if stmt:
        # Penaliza longitud excesiva de forma suave
        complexity_penalty = min(0.3, max(0.0, (len(stmt) - 120) / 800))
    return novelty * 0.5 + evidence * 0.6 - complexity_penalty


def rank_conjectures(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    enriched = []
    for c in items:
        s = score_conjecture(c)
        c2 = dict(c)
        c2["_score"] = round(s, 4)
        enriched.append(c2)
    return sorted(enriched, key=lambda x: x["_score"], reverse=True)


__all__ = ["score_conjecture", "rank_conjectures"]
