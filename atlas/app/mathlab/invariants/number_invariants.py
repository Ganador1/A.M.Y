from __future__ import annotations

from typing import Dict, Any

import sympy as sp

from app.mathlab.core.invariants_interface import InvariantsComputer
from app.mathlab.core.object_models import MathematicalObject


class NumberInvariants(InvariantsComputer):
    """Invariantes básicos de teoría de números para enteros usando SymPy."""

    def compute(self, obj: MathematicalObject) -> Dict[str, Any]:
        payload = obj.payload_json
        if "value" not in payload:
            raise ValueError("Missing 'value' in integer object payload")
        n = int(payload["value"])  # puede venir como str/float compatible

        inv: Dict[str, Any] = {}
        try:
            inv["abs"] = int(abs(n))
            inv["sign"] = -1 if n < 0 else (0 if n == 0 else 1)
            inv["is_prime"] = bool(sp.isprime(n))
        except Exception:
            inv["is_prime"] = None

        try:
            fac = sp.factorint(n)
            inv["prime_factorization"] = {int(p): int(e) for p, e in fac.items()}
            # Estándares: ω(n) = número de primos distintos; Ω(n) = total con multiplicidad
            inv["omega"] = int(len(fac))
            inv["Omega"] = int(sum(fac.values()))
            # radical(n) = producto de primos distintos
            radical = 1
            for p in fac.keys():
                radical *= int(p)
            inv["radical"] = int(radical)
        except Exception:
            inv["prime_factorization"] = None
            inv["omega"] = None
            inv["Omega"] = None
            inv["radical"] = None

        try:
            inv["totient"] = int(sp.totient(n))
        except Exception:
            inv["totient"] = None

        try:
            inv["mobius"] = int(sp.mobius(n))
        except Exception:
            inv["mobius"] = None

        try:
            inv["divisor_count"] = int(sp.divisor_count(n))
            inv["divisor_sigma"] = int(sp.divisor_sigma(n))
        except Exception:
            inv["divisor_count"] = None
            inv["divisor_sigma"] = None

        return inv