"""Procesa feedback empírico de experimentos / simulaciones para ajustar scores.

Entrada esperada (dict):
  {
    'metric_name': str,
    'value': float,
    'improved': bool,
    'confidence': float (0..1)
  }
Salida:
  {
    'adjustment': float (-1..1),
    'weight': float (0..1),
    'rationale': str
  }
"""
from __future__ import annotations

from typing import Dict, Any


def process_feedback(event: Dict[str, Any]) -> Dict[str, Any]:
    metric = event.get("metric_name", "metric")
    value = float(event.get("value", 0.0))
    improved = bool(event.get("improved", False))
    confidence = max(0.0, min(1.0, float(event.get("confidence", 0.5))))

    # Ajuste: si mejora y el valor se redujo (p.ej. loss) => positivo
    direction = 1.0 if improved else -0.5
    magnitude = min(1.0, abs(value) / 10.0)
    adjustment = direction * magnitude * confidence
    rationale = f"{metric}: {'mejora' if improved else 'empeora'} (valor={value:.3g}, conf={confidence:.2f})"

    return {
        "adjustment": max(-1.0, min(1.0, adjustment)),
        "weight": confidence,
        "rationale": rationale,
    }

__all__ = ["process_feedback"]
