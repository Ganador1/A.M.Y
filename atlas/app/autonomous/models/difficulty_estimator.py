"""DifficultyEstimator: heurística simple para estimar dificultad de prueba / simulación.

Futuro: reemplazar por modelo entrenado (gradient boosting / small transformer) sobre features estructurales.
"""
from __future__ import annotations

from typing import Dict
import math


class DifficultyEstimator:
    def __init__(self, scale: float = 1.0):
        self.scale = scale

    def estimate(self, item: Dict) -> float:
        """Devuelve dificultad normalizada [0,1].
        Heurística: combina longitud statement y coste estimado si presente.
        """
        text = str(item.get("statement", ""))
        cost = float(item.get("estimated_cost", 1.0))
        # longitud suavizada
        length_component = math.tanh(len(text) / 120)
        cost_component = math.tanh(cost / 10)
        score = 0.6 * length_component + 0.4 * cost_component
        return max(0.0, min(1.0, score * self.scale))

__all__ = ["DifficultyEstimator"]
