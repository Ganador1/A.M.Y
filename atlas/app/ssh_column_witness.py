"""Exact column witnesses for the finite positive SSH inverse Gram matrix.

These apply classical Green-kernel bounds: Mu-Fa Chen (2010), ``Speed of
stability for birth--death processes``, arXiv:1004.4407v4, Corollary 3.3,
Eq. (3.5), and proof (d), Eqs. (3.9)--(3.10).
https://arxiv.org/abs/1004.4407v4
Under mu_i=v_i**2, nu_i=u_i**2 and phi_i=S_i, the Green operator is diagonally
similar to M=C.T*C. This implementation makes no new-theorem claim.

Scanning all columns uses O(n) rational operations, not O(n) bit complexity.
Returned vectors are proposals: the existing exact certificate routine must
recompute every quotient. No bounds from different witnesses are combined.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Sequence


def scan_columns(hoppings: Sequence[int | Fraction]) -> dict:
    """Scan columns for 3..511 positive, odd-count, 128-bit rational hoppings.

    Text/decimal parsing belongs to the JSON adapter. This arithmetic helper
    accepts only integers and Fraction values, excluding bool and float.
    """
    if not 3 <= len(hoppings) <= 511 or len(hoppings) % 2 != 1:
        raise ValueError("hoppings must be an odd-length sequence with 3 to 511 entries")
    if any(isinstance(t, bool) or not isinstance(t, (int, Fraction)) for t in hoppings):
        raise ValueError("hoppings must contain positive exact integers or Fractions")
    values = [Fraction(t) for t in hoppings]
    if any(t <= 0 or max(t.numerator.bit_length(), t.denominator.bit_length()) > 128 for t in values):
        raise ValueError("hoppings must be positive with 128-bit rational components")
    diagonal, subdiagonal = values[::2], values[1::2]
    n = len(diagonal)
    u = [Fraction(1)]
    for i in range(1, n):
        u.append(u[-1] * subdiagonal[i - 1] / diagonal[i])
    v = [1 / (diagonal[i] * u[i]) for i in range(n)]
    tails = [Fraction(0)] * (n + 1)
    for i in range(n - 1, -1, -1):
        tails[i] = tails[i + 1] + u[i] ** 2
    prefix_v2, prefix_diagonal = [], []
    running_v2 = running_diagonal = Fraction(0)
    for i in range(n):
        running_v2 += v[i] ** 2
        running_diagonal += v[i] ** 2 * tails[i]
        prefix_v2.append(running_v2)
        prefix_diagonal.append(running_diagonal)
    squared_tail = [Fraction(0)] * (n + 1)
    for i in range(n - 1, -1, -1):
        squared_tail[i] = squared_tail[i + 1] + v[i] ** 2 * tails[i] ** 2
    columns = []
    for k in range(n):
        remainder = squared_tail[k + 1] / tails[k]
        qk = tails[k] * prefix_v2[k] + remainder
        qfirst = prefix_diagonal[k] + remainder
        qlast = tails[k] * prefix_v2[k] + running_diagonal - prefix_diagonal[k]
        columns.append({"rho_lower": qk, "rho_upper": max(qfirst, qlast),
                        "qfirst": qfirst, "qlast": qlast})
    best = min(range(n), key=lambda k: columns[k]["rho_upper"] / columns[k]["rho_lower"])
    return {"v": v, "tails": tails[:-1], "columns": columns, "best_index": best}


def column_witness(scan: dict, index: int) -> list[Fraction]:
    """Return a normalized positive column of M; its first entry is one."""
    v, tails = scan["v"], scan["tails"]
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(v):
        raise ValueError("invalid column index")
    vector = [v[i] * tails[max(i, index)] for i in range(len(v))]
    return [value / vector[0] for value in vector]


def balanced_witness(scan: dict) -> list[Fraction]:
    """Balance adjacent columns with 128 rational bisections, retaining ends.

    This reduces the maximum quotient over that segment. It need not minimize
    the full interval width, so callers must compare complete certificates.
    The endpoint-maximum property does not extend to nonadjacent mixtures.
    """
    columns = scan["columns"]
    right = next(k for k, column in enumerate(columns) if column["qfirst"] >= column["qlast"])
    if right == 0 or columns[right]["qfirst"] == columns[right]["qlast"]:
        return column_witness(scan, right)
    left = right - 1
    first, second = columns[left], columns[right]
    ratio = scan["tails"][left] / scan["tails"][right]

    def endpoints(weight):
        qfirst = (1 - weight) * first["qfirst"] + weight * second["qfirst"]
        qlast = ((1 - weight) * first["qlast"] + weight * ratio * second["qlast"]) / (1 - weight + weight * ratio)
        return qfirst, qlast

    lower, upper = Fraction(0), Fraction(1)
    for _ in range(128):
        middle = (lower + upper) / 2
        qfirst, qlast = endpoints(middle)
        if qfirst < qlast:
            lower = middle
        else:
            upper = middle
    weight = min((Fraction(0), lower, upper, Fraction(1)), key=lambda t: max(endpoints(t)))
    first_vector, second_vector = column_witness(scan, left), column_witness(scan, right)
    return [(1 - weight) * a + weight * b for a, b in zip(first_vector, second_vector)]


def column_witness_candidates(hoppings: Sequence[int | Fraction]):
    """Yield the best individual column and one balanced adjacent proposal."""
    scan = scan_columns(hoppings)
    yield "column", column_witness(scan, scan["best_index"])
    yield "balanced_columns", balanced_witness(scan)
