from __future__ import annotations

from typing import Dict, Any, Tuple
import math
import sympy as sp


class EvidenceRatioEngine:
    """Calcula evidence_ratio para conjeturas de teoría de números.

    Implementación inicial:
    - goldbach: proporción de n pares en [lower, upper] que se escriben como suma de dos primos.
    - sum_two_squares: proporción de n en [lower, upper] que cumplen el criterio de suma de dos cuadrados.
    """

    def __init__(self, lower: int = 4, upper: int = 1000) -> None:
        self.lower = int(lower)
        self.upper = int(upper)

    def compute(self, conjecture: Dict[str, Any]) -> Dict[str, Any]:
        ctype = conjecture.get("type")
        if ctype == "goldbach":
            return self._goldbach_ratio()
        if ctype == "sum_two_squares":
            return self._sum_two_squares_ratio()
        return {"evidence_ratio": None, "evaluated": 0}

    def _goldbach_ratio(self) -> Dict[str, Any]:
        total = 0
        holds = 0
        for n in range(max(4, self.lower) | 0, self.upper + 1):
            if n % 2 != 0:
                continue
            total += 1
            if self._has_goldbach_pair(n):
                holds += 1
        ratio = (holds / total) if total > 0 else None
        return {"conjecture": "goldbach", "evaluated": total, "supports": holds, "evidence_ratio": ratio}

    def _sum_two_squares_ratio(self) -> Dict[str, Any]:
        total = 0
        holds = 0
        for n in range(max(1, self.lower), self.upper + 1):
            total += 1
            if self._is_sum_two_squares(n):
                holds += 1
        ratio = (holds / total) if total > 0 else None
        return {"conjecture": "sum_two_squares", "evaluated": total, "supports": holds, "evidence_ratio": ratio}

    # ---------------- helpers ----------------
    def _has_goldbach_pair(self, n: int) -> bool:
        for p in range(2, n):
            if sp.isprime(p) and sp.isprime(n - p):
                return True
        return False

    def _is_sum_two_squares(self, n: int) -> bool:
        fac = sp.factorint(n)
        for p, e in fac.items():
            if p % 4 == 3 and e % 2 == 1:
                return False
        # quick witness try (optional)
        limit = int(math.isqrt(n))
        for x in range(0, limit + 1):
            y2 = n - x * x
            y = int(math.isqrt(y2))
            if y >= 0 and y * y == y2:
                return True
        return True


__all__ = ["EvidenceRatioEngine"]


