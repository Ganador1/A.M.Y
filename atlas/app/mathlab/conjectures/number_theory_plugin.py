from __future__ import annotations

from typing import Dict, Any, List
import math

import sympy as sp

from app.mathlab.core.object_models import MathematicalObject
from app.mathlab.conjectures.base_plugin import ConjecturePlugin


class NumberTheoryConjecturePlugin(ConjecturePlugin):
    """Plugin de teoría de números (enteros n).

    Genera y evalúa conjeturas clásicas sobre un entero n:
    - Goldbach (para n par ≥ 4): n = p + q con p,q primos.
    - Suma de dos cuadrados (Fermat): n = x^2 + y^2 si y sólo si para todo primo p ≡ 3 (mod 4), su exponente en la factorización de n es par.
    """

    def generate(self, obj: MathematicalObject) -> List[Dict[str, Any]]:
        payload = obj.payload_json
        if payload.get("type") != "integer" or "value" not in payload:
            return []
        n = int(payload["value"])  # puede venir como str/float
        out: List[Dict[str, Any]] = []
        if n >= 4 and n % 2 == 0:
            out.append({
                "id": f"goldbach_{n}",
                "statement": f"Para n par, existen primos p,q con p+q=n (n={n}).",
                "type": "goldbach",
                "n": n,
            })
        if n > 0:
            out.append({
                "id": f"sum_two_squares_{n}",
                "statement": f"n es suma de dos cuadrados (n={n}).",
                "type": "sum_two_squares",
                "n": n,
            })
        return out

    def evaluate(self, obj: MathematicalObject, conjecture: Dict[str, Any]) -> Dict[str, Any]:
        payload = obj.payload_json
        if payload.get("type") != "integer" or "value" not in payload:
            return {"status": "ERROR", "error": "Objeto no es entero"}
        n = int(payload["value"])  # robustez
        ctype = conjecture.get("type")

        if ctype == "goldbach":
            if n < 4 or n % 2 != 0:
                return {"status": "SKIP", "reason": "No aplica (n par ≥ 4)"}
            p, q = self._find_goldbach_pair(n)
            if p is not None:
                return {"status": "SUPPORTS", "supports": True, "evidence": {"p": p, "q": q}}
            return {"status": "INCONCLUSIVE", "supports": False}

        if ctype == "sum_two_squares":
            ok, witness = self._is_sum_two_squares(n)
            if ok:
                return {"status": "SUPPORTS", "supports": True, "evidence": witness}
            return {"status": "REFUTES", "supports": False}

        return {"status": "UNKNOWN"}

    # ---------------- helpers ----------------
    def _find_goldbach_pair(self, n: int) -> tuple[int | None, int | None]:
        for p in range(2, n):
            if sp.isprime(p) and sp.isprime(n - p):
                return p, n - p
        return None, None

    def _is_sum_two_squares(self, n: int) -> tuple[bool, Dict[str, Any] | None]:
        fac = sp.factorint(n)
        for p, e in fac.items():
            if p % 4 == 3 and e % 2 == 1:
                return False, None
        # Buscar testigo pequeño por si acaso
        limit = int(math.sqrt(n))
        for x in range(0, limit + 1):
            y2 = n - x * x
            y = int(math.isqrt(y2))
            if y >= 0 and y * y == y2:
                return True, {"x": x, "y": y}
        return True, None


__all__ = ["NumberTheoryConjecturePlugin"]


