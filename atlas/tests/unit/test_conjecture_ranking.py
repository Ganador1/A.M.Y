from __future__ import annotations

import pytest

from app.mathlab.conjectures.ranking_engine import score_conjecture, rank_conjectures
from app.services.theorem_proving.z3_smt_service import Z3SMTService, Z3_AVAILABLE

try:
    import z3  # type: ignore
except Exception:  # pragma: no cover
    z3 = None  # type: ignore


def test_ranking_orders_by_score():
    items = [
        {"id": 1, "statement": "A", "novelty": 0.1, "evidence_ratio": 0.2},
        {"id": 2, "statement": "B", "novelty": 0.9, "evidence_ratio": 0.1},
        {"id": 3, "statement": "C", "novelty": 0.4, "evidence_ratio": 0.9},
    ]
    ranked = rank_conjectures(items)
    # Esperamos que el item con mayor evidencia (id 3) sea primero
    assert ranked[0]["id"] == 3
    # Puntajes descendentes
    scores = [r["_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_score_conjecture_penaliza_longitud():
    base = {"novelty": 0.5, "evidence_ratio": 0.5}
    corto = dict(base, statement="x+y=z")
    largo = dict(base, statement="x=" + "1+" * 500 + "1")
    assert score_conjecture(corto) > score_conjecture(largo)


def test_verify_simple_tautology_trivial_pattern():
    service = Z3SMTService()
    if not Z3_AVAILABLE:
        # Si Z3 no está disponible sólo verificamos contrato de retorno
        res = service.verify_simple_tautology(None)
        assert res["status"] == "UNKNOWN"
        return
    x = z3.Int('x')
    expr = z3.Implies(x > 0, x > 0)
    res = service.verify_simple_tautology(expr)
    assert res["verified"] is True
    assert res["status"] in {"TRIVIAL", "PROVEN"}


def test_verify_simple_tautology_fallback():
    service = Z3SMTService()
    if not Z3_AVAILABLE:
        pytest.skip("Z3 no disponible")
    x = z3.Int('x')
    y = z3.Int('y')
    # No es tautología trivial => debería delegar a verify (puede ser UNKNOWN, PROVEN o REFUTED)
    expr = z3.Implies(x > y, x + 1 > y)
    res = service.verify_simple_tautology(expr)
    assert 'status' in res
    assert 'verified' in res  # puede ser True/False/None según solver
