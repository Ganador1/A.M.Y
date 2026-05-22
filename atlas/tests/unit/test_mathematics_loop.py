from copy import deepcopy

import pytest

from app.autonomous.integration import EvidenceSummary
from app.autonomous.pipelines import mathematics_loop
from app.autonomous.pipelines.mathematics_loop import MathematicsLoop
from app.domains.mathematics.services.mathematical_discovery_engine import Conjecture
from app.monitoring.metrics import metrics


@pytest.fixture(autouse=True)
def reset_metrics():
    metrics.reset()
    yield
    metrics.reset()


def build_candidate(identifier: str) -> dict:
    conjecture = Conjecture(id=identifier, statement=f"Conjecture {identifier}", domain="number_theory")
    base = {
        "id": identifier,
        "statement": conjecture.statement,
        "domain": conjecture.domain,
        "conjecture": conjecture,
        "importance": 0.6,
        "novelty": 0.5,
        "information_gain": 0.55,
        "impact_potential": 0.4,
        "estimated_cost": 0.1,
        "literature_frequency": 10,
        "dependency_count": 1,
    }
    return deepcopy(base)


@pytest.mark.asyncio
async def test_mathematics_loop_records_support(monkeypatch):
    loop = MathematicsLoop()

    def fake_prepare(limit, domain=None):
        return [build_candidate("math_a"), build_candidate("math_b"), build_candidate("math_c")][:limit]

    async def fake_evaluate(candidate, include_literature=False):
        return {
            "status": "open",
            "importance": 0.65,
            "proof": None,
            "counterexample": None,
            "notes": "stub",
            "time_seconds": 0.1,
            "literature": [{"title": "Example"}] if include_literature else None,
        }

    async def fake_corroborate(hypothesis, domain=None):
        assert domain == "number_theory"
        assert hypothesis["domain"] == "number_theory"
        return EvidenceSummary(
            success=True,
            support_score=0.85,
            weighted_coverage=0.7,
            mean_signal=0.6,
            diversity=0.5,
            evidence_items=[{"source": "formal"}],
        )

    monkeypatch.setattr(loop, "_prepare_candidates", fake_prepare)
    monkeypatch.setattr(loop, "_evaluate_candidate_async", fake_evaluate)
    monkeypatch.setattr(loop.novelty, "assess", lambda embed: {"novelty_score": 0.45})
    monkeypatch.setattr(loop.tool_evidence, "corroborate", fake_corroborate)
    monkeypatch.setattr(mathematics_loop, "generate_proof_sketch", lambda candidate: {"content": "sketch"})
    monkeypatch.setattr(mathematics_loop, "validate_sketch", lambda content: {"valid": True})

    result = await loop._run_iteration_impl(iteration=1, limit=2)

    summary = result["summary"]
    assert summary["avg_support_score"] == pytest.approx(0.85)
    assert metrics.gauges["autonomous_support_score_last"] == pytest.approx(0.85)

    for entry in result["selected"]:
        assert entry["impact_potential"] > 0.4
        evidence = entry["tool_evidence"]
        assert evidence["success"] is True
        assert evidence["support_score"] == pytest.approx(0.85)


@pytest.mark.asyncio
async def test_mathematics_loop_handles_failed_support(monkeypatch):
    loop = MathematicsLoop()

    def fake_prepare(limit, domain=None):
        return [build_candidate("math_fail")] * limit

    async def fake_evaluate(candidate, include_literature=False):
        return {
            "status": "open",
            "importance": 0.6,
            "proof": None,
            "counterexample": None,
            "notes": "stub",
            "time_seconds": 0.1,
            "literature": None,
        }

    async def failing_corroborate(hypothesis, domain=None):
        assert domain == "number_theory"
        return EvidenceSummary(success=False, support_score=0.0, error="timeout")

    monkeypatch.setattr(loop, "_prepare_candidates", fake_prepare)
    monkeypatch.setattr(loop, "_evaluate_candidate_async", fake_evaluate)
    monkeypatch.setattr(loop.novelty, "assess", lambda embed: {"novelty_score": 0.3})
    monkeypatch.setattr(loop.tool_evidence, "corroborate", failing_corroborate)
    monkeypatch.setattr(mathematics_loop, "generate_proof_sketch", lambda candidate: {"content": "sketch"})
    monkeypatch.setattr(mathematics_loop, "validate_sketch", lambda content: {"valid": True})

    result = await loop._run_iteration_impl(iteration=2, limit=1)

    summary = result["summary"]
    assert summary["avg_support_score"] == pytest.approx(0.0)
    assert metrics.gauges["autonomous_support_score_last"] == pytest.approx(0.0)

    selected = result["selected"][0]
    assert selected["impact_potential"] == pytest.approx(0.4)
    evidence = selected["tool_evidence"]
    assert evidence is None or evidence["success"] is False