from __future__ import annotations

from typing import Dict, Any, List
import sympy as sp


def compute_polynomial_invariants(coeffs: List[float]) -> Dict[str, Any]:
    """Compute simple invariants for a univariate polynomial with given coefficients.

    coeffs: list of coefficients [a_n, a_{n-1}, ..., a_0]
    """
    if not coeffs:
        raise ValueError("Empty coefficients")
    # Build polynomial
    x = sp.Symbol('x')
    poly = sp.Poly(sum(sp.Rational(c) * x ** i for i, c in enumerate(reversed(coeffs))), x)
    deg = int(poly.degree())
    lc = sp.together(poly.LC())
    cont = sp.content(poly)
    prim = sp.primitive(poly)[1]
    disc = sp.discriminant(poly.as_expr(), x)
    sqf = sp.squarefree_part(poly.as_expr())
    try:
        roots = sp.nroots(poly.as_expr())
        real_roots = sum(1 for r in roots if abs(sp.im(r)) < 1e-12)
    except Exception:
        real_roots = None
    try:
        irr_q = sp.numer(poly.as_expr()).is_irreducible
    except Exception:
        irr_q = None
    fac = sp.factor_list(poly.as_expr())
    return {
        "degree": deg,
        "leading_coefficient": sp.simplify(lc),
        "content": sp.simplify(cont),
        "discriminant": sp.simplify(disc),
        "squarefree_part": sp.simplify(sqf),
        "real_roots_count": real_roots,
        "factorization": fac,
        "is_irreducible_over_Q": irr_q,
        "primitive_part": sp.simplify(prim),
    }


__all__ = ["compute_polynomial_invariants"]


