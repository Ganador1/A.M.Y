from copy import deepcopy

import pytest

from app.autonomous.integration import EvidenceSummary
from app.autonomous.pipelines.materials_loop import MaterialsLoop
from app.monitoring.metrics import metrics


@pytest.fixture(autouse=True)
def reset_metrics():
    """Ensure metrics gauges are clean for every test."""
    metrics.reset()
    yield
    metrics.reset()


def build_candidate(identifier: str) -> dict:
    base = {
        "id": identifier,
        "embedding": [1.0, 0.8, 0.7],
        "importance": 0.7,
        "proveability": 0.6,
        "novelty": 0.5,
        "information_gain": 0.6,
        "estimated_cost": 0.1,
        "impact_potential": 0.35,
        "suitability": 0.75,
        "materials_properties": {
            "band_gap": 1.2,
            "stability_score": 0.72,
        },
    }
    return deepcopy(base)


@pytest.mark.asyncio
async def test_materials_loop_records_support_score(monkeypatch):
    loop = MaterialsLoop(provider=lambda: [build_candidate("cand_a"), build_candidate("cand_b")])

    async def fake_analyze(composition: str):
        return {"composition": composition, "stability_score": 0.78}

    async def fake_predict(composition):
        return {"band_gap": 1.15, "stability_score": 0.78}

    monkeypatch.setattr(loop.materials_service, "analyze_stability", fake_analyze)
    monkeypatch.setattr(loop.materials_service, "predict_material_properties", fake_predict)

    async def fake_corroborate(hypothesis, domain=None):
        assert hypothesis["domain"] == "materials_science"
        assert "Validación" in hypothesis["title"]
        return EvidenceSummary(
            success=True,
            support_score=0.8,
            weighted_coverage=0.65,
            mean_signal=0.7,
            diversity=0.5,
            evidence_items=[{"source": "literature"}],
        )

    monkeypatch.setattr(loop.tool_evidence, "corroborate", fake_corroborate)

    result = await loop._run_iteration_impl(iteration=1)

    assert result["success"] is True
    summary = result["summary"]
    assert summary["avg_support_score"] == pytest.approx(0.8)
    assert metrics.gauges["autonomous_support_score_last"] == pytest.approx(0.8)

    for selected in result["selected"]:
        assert selected["impact_potential"] > 0.35
        evidence = selected["evaluation"]["tool_evidence"]
        assert evidence["success"] is True
        assert evidence["support_score"] == pytest.approx(0.8)


@pytest.mark.asyncio
async def test_materials_loop_handles_failed_evidence(monkeypatch):
    loop = MaterialsLoop(provider=lambda: [build_candidate("cand_x")])

    async def fake_analyze(composition: str):
        return {"composition": composition, "stability_score": 0.7}

    async def fake_predict(composition):
        return {"band_gap": 1.0, "stability_score": 0.7}

    monkeypatch.setattr(loop.materials_service, "analyze_stability", fake_analyze)
    monkeypatch.setattr(loop.materials_service, "predict_material_properties", fake_predict)

    async def failing_corroborate(hypothesis, domain=None):
        return EvidenceSummary(success=False, support_score=0.0, error="timeout")

    monkeypatch.setattr(loop.tool_evidence, "corroborate", failing_corroborate)

    result = await loop._run_iteration_impl(iteration=2)

    assert result["success"] is True
    summary = result["summary"]
    # Expect 0.05 because internal stability check passed, giving partial credit
    assert summary["avg_support_score"] == pytest.approx(0.05)
    assert metrics.gauges["autonomous_support_score_last"] == pytest.approx(0.05)

    selected = result["selected"][0]
    assert selected["evidence_support_score"] == pytest.approx(0.05)
    evidence = selected["evaluation"]["tool_evidence"]
    assert evidence["success"] is False
    assert evidence["support_score"] == pytest.approx(0.0)
    assert evidence["error"] == "timeout"
