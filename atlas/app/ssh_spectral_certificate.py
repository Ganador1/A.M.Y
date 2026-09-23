"""Exact finite chiral-chain gap bounds from classical Perron inequalities.

This is an application of known linear algebra, not a claim of a new theorem.
For positive rational hoppings and zero onsite energies, the half-filling gap
is twice the smallest singular value of the bidiagonal sublattice block B.
The alternating-sign gauge turns B^{-1} into a nonnegative matrix C. Applying
C and C.T needs only two recurrences. For any strictly positive rational x,
min((C.T C x)/x) <= rho(C.T C) <= max((C.T C x)/x).

All reported bounds are rational bounds on the SQUARED gap. Floating-point
iteration only proposes a witness: the final bounds use Fraction arithmetic.
Arithmetic operation count is linear in chain length per sweep; exact integer
bit complexity is not claimed to be linear.
"""
from __future__ import annotations

from fractions import Fraction
import math
from typing import Sequence


_METHOD = "exact_rational_collatz_wielandt_inverse_bidiagonal"
_SCOPE = "finite_open_even_positive_hopping_zero_onsite_chain"


def _positive_rationals(values: Sequence, name: str) -> list[Fraction]:
    result = []
    for value in values:
        if isinstance(value, bool):
            raise ValueError(f"{name} must contain positive finite numbers")
        try:
            item = Fraction(value)
        except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
            raise ValueError(f"{name} must contain positive finite numbers") from exc
        if item <= 0:
            raise ValueError(f"{name} must contain positive finite numbers")
        result.append(item)
    return result


def inverse_gram_action(hoppings: Sequence, vector: Sequence) -> list[Fraction]:
    """Compute |B^-1|.T |B^-1| x exactly without forming either matrix."""
    t = _positive_rationals(hoppings, "hoppings")
    if len(t) < 3 or len(t) % 2 != 1:
        raise ValueError("hoppings must describe an even open chain of >=4 sites")
    x = _positive_rationals(vector, "vector")
    a, b = t[::2], t[1::2]
    if len(x) != len(a):
        raise ValueError("witness dimension must equal half the site count")
    y = [x[0] / a[0]]
    for i in range(1, len(a)):
        y.append((x[i] + b[i - 1] * y[-1]) / a[i])
    z = [Fraction(0)] * len(a)
    z[-1] = y[-1] / a[-1]
    for i in range(len(a) - 2, -1, -1):
        z[i] = (y[i] + b[i] * z[i + 1]) / a[i]
    return z


def positive_witness(hoppings: Sequence, iterations: int = 4) -> list[Fraction]:
    """Propose a witness with bounded floating iteration, then freeze its bits.

    Extreme overflow/underflow falls back to a valid all-ones witness. This
    can widen the interval but cannot create an invalid exact certificate.
    """
    t = _positive_rationals(hoppings, "hoppings")
    if len(t) < 3 or len(t) % 2 != 1:
        raise ValueError("hoppings must describe an even open chain of >=4 sites")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or not 0 <= iterations <= 100:
        raise ValueError("iterations must be an integer in [0, 100]")
    n = (len(t) + 1) // 2
    x = [1.0] * n
    try:
        scale = float(max(t))
        a = [float(v) / scale for v in t[::2]]
        b = [float(v) / scale for v in t[1::2]]
        for _ in range(iterations):
            y = [x[0] / a[0]]
            for i in range(1, n):
                y.append((x[i] + b[i - 1] * y[-1]) / a[i])
            ymax = max(y)
            y = [v / ymax for v in y]
            z = [0.0] * n
            z[-1] = y[-1] / a[-1]
            for i in range(n - 2, -1, -1):
                z[i] = (y[i] + b[i] * z[i + 1]) / a[i]
            zmax = max(z)
            candidate = [v / zmax for v in z]
            if any(not math.isfinite(v) or v <= 0 for v in candidate):
                break
            x = candidate
    except (OverflowError, ZeroDivisionError):
        pass
    return [Fraction(v) for v in x]


def certified_gap_squared(hoppings: Sequence, *, witness: Sequence | None = None,
                          iterations: int = 4) -> dict:
    """Certify the gap of the supplied exact rational, zero-onsite Hamiltonian.

    A float input means its exact binary value, not an intended decimal or
    uncertain physical measurement. Pass strings/Fraction for decimal input.
    This function does not certify hopping measurement uncertainty, diagonal
    disorder, a topological phase, or an infinite-system limit.
    """
    t = _positive_rationals(hoppings, "hoppings")
    x = positive_witness(t, iterations) if witness is None else _positive_rationals(witness, "witness")
    z = inverse_gram_action(t, x)
    ratios = [zi / xi for zi, xi in zip(z, x)]
    return {
        "gap_squared_lower": 4 / max(ratios),
        "gap_squared_upper": 4 / min(ratios),
        "witness": x,
        "hoppings": t,
        "method": _METHOD,
        "scope": _SCOPE,
    }


def verify_gap_certificate(certificate: dict) -> bool:
    """Recompute the exact witness inequalities; reject altered certificates.

    This verifies the recorded rational Hamiltonian, not its origin or identity
    against an external experiment. Consumers must bind ``hoppings`` to their
    intended Hamiltonian separately. Rational strings support lossless JSON
    storage; rounded floating bounds are rejected unless exactly equal.
    """
    if not isinstance(certificate, dict):
        return False
    if certificate.get("method") != _METHOD or certificate.get("scope") != _SCOPE:
        return False
    try:
        bounds = _positive_rationals(
            [certificate["gap_squared_lower"], certificate["gap_squared_upper"]],
            "gap bounds",
        )
        witness = _positive_rationals(certificate["witness"], "witness")
        recomputed = certified_gap_squared(
            certificate["hoppings"], witness=witness
        )
    except (KeyError, ValueError, TypeError, OverflowError, ZeroDivisionError):
        return False
    return (
        bounds[0] == recomputed["gap_squared_lower"]
        and bounds[1] == recomputed["gap_squared_upper"]
    )


def classify_gap_threshold(certificate: dict, threshold) -> str:
    """Verify first, then return a certified threshold verdict or inconclusive."""
    if isinstance(threshold, bool):
        raise ValueError("threshold must be a non-negative finite number")
    try:
        value = Fraction(threshold)
    except (ValueError, TypeError, OverflowError, ZeroDivisionError) as exc:
        raise ValueError("threshold must be a non-negative finite number") from exc
    if value < 0:
        raise ValueError("threshold must be a non-negative finite number")
    if not verify_gap_certificate(certificate):
        raise ValueError("invalid gap certificate")
    if Fraction(certificate["gap_squared_upper"]) <= value * value:
        return "proven_below_or_equal"
    if Fraction(certificate["gap_squared_lower"]) > value * value:
        return "proven_above"
    return "inconclusive"
