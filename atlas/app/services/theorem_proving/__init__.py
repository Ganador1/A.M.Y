"""
Theorem Proving subpackage
- Z3SMTService: verificación SMT y optimización básica
- Lean4Service: integración (stub segura) con Lean 4
- ConjectureExplorer: exploración simple de conjeturas/patrones
"""

from __future__ import annotations

__all__ = [
    "Z3SMTService",
    "Lean4Service",
    "ConjectureExplorer",
]

try:  # pragma: no cover
    from .z3_smt_service import Z3SMTService  # type: ignore
except Exception:  # pragma: no cover
    Z3SMTService = None  # type: ignore

try:  # pragma: no cover
    from .lean4_integration import Lean4Service  # type: ignore
except Exception:  # pragma: no cover
    Lean4Service = None  # type: ignore

try:  # pragma: no cover
    from .conjecture_explorer import ConjectureExplorer  # type: ignore
except Exception:  # pragma: no cover
    ConjectureExplorer = None  # type: ignore
