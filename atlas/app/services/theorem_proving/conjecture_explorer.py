"""
Conjecture Explorer (ligero)
- Heurísticas para detectar patrones simples en secuencias
- Búsqueda OEIS-like (mock) y regresión polinómica básica
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import numpy as np

try:  # opcional
    from numpy.polynomial import Polynomial
except Exception:  # pragma: no cover
    Polynomial = None  # type: ignore


class ConjectureExplorer:
    def __init__(self) -> None:
        self._max_degree = 4

    async def explore_sequence(self, sequence: List[int]) -> List[Dict[str, Any]]:
        sequence = [int(x) for x in sequence if x is not None]
        tasks = [
            self._known_patterns(sequence),
            self._poly_fit(sequence),
            self._recurrence(sequence),
            self._number_theory_props(sequence),
        ]
        results = await asyncio.gather(*tasks)
        flat: List[Dict[str, Any]] = []
        for r in results:
            flat.extend(r)
        flat.sort(key=lambda x: x.get("confidence", 0.0), reverse=True)
        return flat[:10]

    async def _known_patterns(self, seq: List[int]) -> List[Dict[str, Any]]:
        # Heurística mínima: detecta aritmética y geométrica
        if len(seq) < 3:
            return []
        diffs = [seq[i+1] - seq[i] for i in range(len(seq)-1)]
        if len(set(diffs)) == 1:
            d = diffs[0]
            next_terms = [seq[-1] + d]
            return [{
                "type": "arithmetic_progression",
                "formula": f"a_n = a_0 + {d} * n",
                "confidence": 0.9,
                "next_terms": next_terms,
            }]
        ratios = []
        ok = True
        for i in range(len(seq)-1):
            if seq[i] == 0:
                ok = False
                break
            ratios.append(seq[i+1] / seq[i])
        if ok and len(ratios) > 0 and max(ratios) - min(ratios) < 1e-9:
            r = ratios[0]
            next_terms = [seq[-1] * r]
            return [{
                "type": "geometric_progression",
                "formula": f"a_n = a_0 * {r}^n",
                "confidence": 0.85,
                "next_terms": next_terms,
            }]
        return []

    async def _poly_fit(self, seq: List[int]) -> List[Dict[str, Any]]:
        if Polynomial is None or len(seq) < 4:
            return []
        try:
            x = np.arange(len(seq))
            y = np.array(seq, dtype=float)
            best = None
            for deg in range(1, min(self._max_degree, len(seq)-1) + 1):
                coeffs = np.polyfit(x, y, deg)
                p = np.poly1d(coeffs)
                preds = p(x)
                rmse = float(np.sqrt(np.mean((preds - y) ** 2)))
                score = 1.0 / (1.0 + rmse)
                if not best or score > best[0]:
                    best = (score, deg, p)
            if best:
                score, deg, p = best
                next_val = float(p(len(seq)))
                return [{
                    "type": "algebraic",
                    "formula": f"poly_degree_{deg}",
                    "confidence": round(min(0.99, score), 4),
                    "next_terms": [next_val],
                }]
        except Exception:
            return []
        return []

    async def _recurrence(self, seq: List[int]) -> List[Dict[str, Any]]:
        # Recurrencia lineal de orden 1 o 2 simple
        if len(seq) < 5:
            return []
        # Orden 1: a_{n} = c * a_{n-1} + b
        try:
            a = np.array(seq[1:], dtype=float)
            b = np.array(seq[:-1], dtype=float)
            A = np.vstack([b, np.ones_like(b)]).T
            c1, c0 = np.linalg.lstsq(A, a, rcond=None)[0]
            pred = c1 * b + c0
            rmse = float(np.sqrt(np.mean((pred - a) ** 2)))
            score = 1.0 / (1.0 + rmse)
            if score > 0.6:
                next_val = float(c1 * seq[-1] + c0)
                return [{
                    "type": "recurrence_order_1",
                    "relation": f"a_n = {c1:.4f} * a_(n-1) + {c0:.4f}",
                    "confidence": round(score, 4),
                    "next_terms": [next_val],
                }]
        except Exception:
            pass
        return []

    async def _number_theory_props(self, seq: List[int]) -> List[Dict[str, Any]]:
        if len(seq) == 0:
            return []
        evens = sum(1 for x in seq if x % 2 == 0)
        odds = len(seq) - evens
        props = []
        if evens == len(seq) or odds == len(seq):
            props.append({
                "type": "parity_pattern",
                "formula": "even_only" if evens == len(seq) else "odd_only",
                "confidence": 0.7,
            })
        return props

