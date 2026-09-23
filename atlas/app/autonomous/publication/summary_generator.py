"""Resumen ejecutivo y secciones auxiliares para mini-papers.

Genera resúmenes concisos a partir de métricas y hallazgos clave.

API inicial:
    build_summary(insights: dict, max_len: int = 600) -> str
"""
from __future__ import annotations

from typing import Dict


def build_summary(insights: Dict[str, float | int | str], max_len: int = 600) -> str:
    parts = []
    for k, v in insights.items():
        parts.append(f"{k}: {v}")
    joined = "; ".join(parts)
    if len(joined) > max_len:
        return joined[: max_len - 3] + "..."
    return joined

__all__ = ["build_summary"]
