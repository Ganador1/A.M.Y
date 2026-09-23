from __future__ import annotations

from typing import Protocol, Dict, Any

from app.mathlab.core.object_models import MathematicalObject


class InvariantsComputer(Protocol):
    def compute(self, obj: MathematicalObject) -> Dict[str, Any]:
        ...