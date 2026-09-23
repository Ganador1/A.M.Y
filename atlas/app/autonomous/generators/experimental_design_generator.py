"""Generator de diseño experimental para dominios físicos/químicos (placeholder).

Provee función principal generate_experimental_design que recibe un diccionario de parámetros base y produce
un plan con barridos (sweeps) y criterios de parada.
"""
from __future__ import annotations

from typing import Dict, Any, List
import itertools


def generate_experimental_design(config: Dict[str, Any]) -> Dict[str, Any]:
    """Genera un diseño experimental básico.

    Parámetros de entrada esperados (si presentes):
      - factors: Dict[str, List[Any]] factores discretos a barrer.
      - max_runs: int límite superior de combinaciones.
      - stop_metric: str métrica objetivo.
      - early_stop_threshold: float criterio de parada temprana.
    """
    factors = config.get("factors", {})
    max_runs = int(config.get("max_runs", 50))
    stop_metric = config.get("stop_metric", "loss")
    threshold = float(config.get("early_stop_threshold", 0.01))

    # Producto cartesiano limitado
    keys = list(factors.keys())
    raw_combos = list(itertools.product(*factors.values())) if factors else []
    combos = raw_combos[:max_runs]
    plan: List[Dict[str, Any]] = []
    for idx, combo in enumerate(combos):
        entry = {k: v for k, v in zip(keys, combo)}
        entry["run_id"] = idx
        plan.append(entry)

    return {
        "runs": plan,
        "stop_metric": stop_metric,
        "early_stop_threshold": threshold,
        "total_planned": len(plan),
    }

__all__ = ["generate_experimental_design"]
