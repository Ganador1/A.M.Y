from copy import deepcopy

import pytest

from app.autonomous.integration import EvidenceSummary
from app.autonomous.pipelines import biology_loop
from app.autonomous.pipelines.biology_loop import BiologyLoop
from app.monitoring.metrics import metrics


@pytest.fixture(autouse=True)
def reset_metrics():
    metrics.reset()
    yield
    metrics.reset()


def build_target(identifier: str) -> dict:
    base = {
        "id": identifier,
        "uniprot": f"P{identifier[-1:] or '0':>05}",
        "uncertainty": 0.6,
        "impact_potential": 0.4,
        "literature_frequency": 20,
        "dependency_count": 2,
        "proveability": 0.5,
        "novelty": 0.5,
        "information_gain": 0.5,
        "estimated_cost": 0.1,
    }
    return deepcopy(base)


@pytest.mark.asyncio
async def test_biology_loop_records_support(monkeypatch):
    class FakeBiologyService:
        networkx_available = True

        async def population_dynamics(self, _payload):
            return {"results": {"growth_rate": 0.2}}

        async def biodiversity_analysis(self, _payload):
            return {"indices": {"shannon": 1.4}}

        async def regulatory_network_analysis(self, _payload):
            return {"nodes": 5}

    class FakeAIService:
        def __init__(self, *args, **kwargs): pass
        async def process_request(self, data): return {"success": True}
        def initialize(self): pass

    monkeypatch.setattr(biology_loop, "ComputationalBiologyService", FakeBiologyService)
    monkeypatch.setattr(biology_loop, "DNABERT2GenomicsService", FakeAIService)
    monkeypatch.setattr(biology_loop, "ProtGPT2ProteinDesignService", FakeAIService)
    monkeypatch.setattr(biology_loop, "BioGPTService", FakeAIService)
    monkeypatch.setattr(biology_loop, "GenomicsService", FakeAIService)
    monkeypatch.setattr(biology_loop, "BiomedicalNLPService", FakeAIService)
    loop = BiologyLoop()

    async def fake_enrich(_target, _iteration_data=None):
        return {
            "population_dynamics": {"results": {"growth_rate": 0.2}},
            "biodiversity": {"indices": {"shannon": 1.4}},
            "regulatory_network": {"nodes": 5},
        }

    async def fake_corroborate(hypothesis, domain=None):
        assert domain == "biology"
        assert hypothesis["domain"] == "biology"
        return EvidenceSummary(
            success=True,
            support_score=0.9,
            weighted_coverage=0.7,
            mean_signal=0.65,
            diversity=0.5,
            evidence_items=[{"source": "literature"}],
        )

    monkeypatch.setattr(loop, "_seed_targets", lambda: [build_target("target_a"), build_target("target_b")])
    monkeypatch.setattr(loop, "_enrich_target_async", fake_enrich)
    monkeypatch.setattr(loop.novelty, "assess", lambda emb: {"novelty_score": 0.55})
    monkeypatch.setattr(loop.tool_evidence, "corroborate", fake_corroborate)

    result = await loop._run_iteration_impl(top_n=2)  # pylint: disable=protected-access

    assert result["avg_support_score"] == pytest.approx(0.9)
    assert metrics.gauges["autonomous_support_score_last"] == pytest.approx(0.9)

    for entry in result["selected"]:
        assert entry["impact_potential"] > 0.4
        outcome = result["outcomes"][entry["id"]]
        assert outcome["tool_evidence"]["success"] is True
        assert outcome["tool_evidence"]["support_score"] == pytest.approx(0.9)
        assert outcome["population_dynamics"]["results"]["growth_rate"] == 0.2


@pytest.mark.asyncio
async def test_biology_loop_handles_failed_support(monkeypatch):
    class FakeBiologyService:
        networkx_available = False

        async def population_dynamics(self, _payload):
            return {"results": {"growth_rate": 0.15}}

        async def biodiversity_analysis(self, _payload):
            return {"indices": {"shannon": 1.2}}

        async def regulatory_network_analysis(self, _payload):  # pragma: no cover - not called
            return None

    class FakeAIService:
        def __init__(self, *args, **kwargs): pass
        async def process_request(self, data): return {"success": True}
        def initialize(self): pass

    monkeypatch.setattr(biology_loop, "ComputationalBiologyService", FakeBiologyService)
    monkeypatch.setattr(biology_loop, "DNABERT2GenomicsService", FakeAIService)
    monkeypatch.setattr(biology_loop, "ProtGPT2ProteinDesignService", FakeAIService)
    monkeypatch.setattr(biology_loop, "BioGPTService", FakeAIService)
    monkeypatch.setattr(biology_loop, "GenomicsService", FakeAIService)
    monkeypatch.setattr(biology_loop, "BiomedicalNLPService", FakeAIService)
    loop = BiologyLoop()

    async def fake_enrich(_target, _iteration_data=None):
        return {
            "population_dynamics": {"results": {"growth_rate": 0.15}},
            "biodiversity": {"indices": {"shannon": 1.2}},
            "regulatory_network": None,
        }

    async def failing_corroborate(_hypothesis, domain=None):
        del domain
        return EvidenceSummary(success=False, support_score=0.0, error="timeout")

    monkeypatch.setattr(loop, "_seed_targets", lambda: [build_target("target_fail")])
    monkeypatch.setattr(loop, "_enrich_target_async", fake_enrich)
    monkeypatch.setattr(loop.novelty, "assess", lambda emb: {"novelty_score": 0.4})
    monkeypatch.setattr(loop.tool_evidence, "corroborate", failing_corroborate)

    result = await loop._run_iteration_impl(top_n=1)  # pylint: disable=protected-access

    assert result["avg_support_score"] == pytest.approx(0.0)
    assert metrics.gauges["autonomous_support_score_last"] == pytest.approx(0.0)

    selected = result["selected"][0]
    assert selected["impact_potential"] == pytest.approx(0.4)
    outcome = result["outcomes"][selected["id"]]
    assert outcome["tool_evidence"]["success"] is False
    assert outcome["tool_evidence"]["error"] == "timeout"
