import asyncio
import pytest

from app.services.theorem_proving.z3_smt_service import Z3SMTService, Z3_AVAILABLE
from app.services.theorem_proving.conjecture_explorer import ConjectureExplorer


@pytest.mark.asyncio
async def test_conjecture_explorer_basic():
    cx = ConjectureExplorer()
    seq = [2, 4, 6, 8, 10]
    res = await cx.explore_sequence(seq)
    assert isinstance(res, list)
    assert any(r.get("type") == "arithmetic_progression" for r in res)


def test_z3_verify_impl():
    svc = Z3SMTService()
    if not Z3_AVAILABLE:
        out = svc.verify(None)
        assert out["status"] in ("UNKNOWN", "ERROR")
        return
    import z3
    x = z3.Real('x')
    formula = z3.Implies(x > 0, x * x > 0)
    out = svc.verify(formula)
    assert out["status"] in ("PROVEN", "REFUTED", "UNKNOWN")

