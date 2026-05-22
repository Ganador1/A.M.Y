"""Validación ligera de bosquejos de prueba (proof sketches).

Heurísticas:
  - Chequeo de secciones obligatorias (Idea central, Estrategia, Riesgos)
  - Longitud mínima de contenido
  - Palabras "TODO" o marcadores excesivos penalizan una señal de completitud

API:
    validate_sketch(text: str) -> dict {valid: bool, score: float, issues: [str]}
"""
from __future__ import annotations

from typing import Dict, List

REQUIRED_SECTIONS = ["Idea", "Estrategia", "Riesgos"]


def validate_sketch(text: str) -> Dict[str, object]:
    issues: List[str] = []
    norm = text.strip()
    if len(norm) < 40:
        issues.append("contenido_demasiado_corto")
    upper = norm.upper()
    todo_markers = upper.count("TODO")
    if todo_markers > 2:
        issues.append("exceso_todos")
    present_sections = sum(1 for s in REQUIRED_SECTIONS if s.lower() in norm.lower())
    if present_sections < len(REQUIRED_SECTIONS):
        issues.append("secciones_incompletas")
    # Score simple
    completeness = present_sections / len(REQUIRED_SECTIONS)
    length_component = min(1.0, len(norm) / 400)
    penalty = 0.1 * max(0, todo_markers - 2)
    raw = 0.6 * completeness + 0.4 * length_component - penalty
    score = max(0.0, min(1.0, raw))
    return {"valid": score >= 0.5 and not issues, "score": score, "issues": issues}

__all__ = ["validate_sketch"]
