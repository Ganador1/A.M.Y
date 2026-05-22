"""Proof sketch generator (placeholder).

Generates structured skeletons for proof attempts using provided conjecture context.
Future integration: LLM calls + symbolic heuristic extraction.
"""
from __future__ import annotations

from typing import Dict, Any, List
import textwrap
from app.core.bootstrap_logging import logger

SKELETON_SECTIONS = [
    "Idea central",
    "Lemas candidatos",
    "Estrategia",
    "Riesgos",
]


def generate_proof_sketch(conjecture: Dict[str, Any], _attempts_history: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Return a lightweight proof sketch structure for a conjecture.

    Parameters
    ----------
    conjecture: dict with at least 'id' and 'statement'
    attempts_history: previous attempts for additional context (unused placeholder)
    """
    cid = conjecture.get("id", "unknown")
    statement = conjecture.get("statement", "")
    body_parts = [f"### {sec}\nTODO: completar {sec.lower()}\n" for sec in SKELETON_SECTIONS]
    body = "\n".join(body_parts)
    sketch_text = textwrap.dedent(
        f"""
        ## Bosquejo de Prueba (Conjetura {cid})
        **Enunciado:** {statement}

        {body}
        """.rstrip()
    )
    logger.debug("Generated proof sketch for %s", cid)
    return {"conjecture_id": cid, "sketch": sketch_text, "sections": SKELETON_SECTIONS}

__all__ = ["generate_proof_sketch"]
