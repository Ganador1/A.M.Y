"""Base plugin interface for mathlab conjecture system.

Se define como archivo aislado para evitar conflictos con trabajos en
curso de otros agentes. Solo declara el `Protocol` mínimo y no fuerza
implementaciones concretas.
"""

from __future__ import annotations

from typing import Protocol, List, Dict, Any
from app.mathlab.core.object_models import MathematicalObject


class ConjecturePlugin(Protocol):
    """Interfaz mínima para plugins de generación/evaluación de conjeturas."""

    def generate(self, obj: MathematicalObject) -> List[Dict[str, Any]]:  # pragma: no cover - interface
        """Retorna lista de conjeturas (cada item: id, statement[, metadata])."""
        raise NotImplementedError

    def evaluate(self, obj: MathematicalObject, conjecture: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - interface
        """Evalúa una conjetura sobre un objeto.

        Debe retornar dict con al menos: status (str) y opcionalmente
        campos como supports (bool), refuted (bool), evidence (dict).
        """
        raise NotImplementedError


__all__ = ["ConjecturePlugin"]
