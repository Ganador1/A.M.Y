import pytest

from app.services.orchestration.tool_evidence_orchestrator import CallSpec, ToolEvidenceOrchestratorService


class _UnavailableExternalAdapter:
    async def process_request(self, request_data):
        return {"success": False, "unavailable": True, "error": "endpoint not configured"}


class _ReturningService:
    def __init__(self, payload):
        self.payload = payload

    async def process_request(self, request_data):
        return dict(self.payload)


@pytest.mark.asyncio
async def test_execute_spec_marks_unavailable_adapter_as_not_available():
    service = ToolEvidenceOrchestratorService()
    spec = CallSpec(
        service_factory=lambda: _UnavailableExternalAdapter(),
        action="mattergen_generate_candidates",
        params={"chemical_system": "Li-Fe-P-O"},
        weight=0.7,
        description="test",
    )

    result = await service._execute_spec(
        spec,
        hypothesis={"title": "Test hypothesis", "description": "Test description", "domain": "materials_science"},
        domain="materials_science",
    )

    assert result["success"] is False
    assert result["_available"] is False


@pytest.mark.asyncio
async def test_execute_spec_marks_paperqa_fallback_as_non_real_evidence():
    service = ToolEvidenceOrchestratorService()
    spec = CallSpec(
        service_factory=lambda: _ReturningService(
            {
                "success": True,
                "backend": "atlas_fallback",
                "support_score": 0.7,
                "citations": [{"title": "Paper"}],
            }
        ),
        action="paperqa2_verify_claim",
        params={"claim": "test"},
        weight=0.7,
        description="test",
    )

    result = await service._execute_spec(
        spec,
        hypothesis={"title": "Test hypothesis", "description": "Test description", "domain": "quantum_computing"},
        domain="quantum_computing",
    )

    assert result["success"] is True
    assert result["evidence_tier"] == "fallback"
    assert result["counts_as_real_evidence"] is False
    assert result["realism_factor"] == pytest.approx(0.1)


@pytest.mark.asyncio
async def test_aggregate_support_uses_only_real_evidence():
    service = ToolEvidenceOrchestratorService()
    service.enable_early_stopping = False
    service.domain_routes["unit_test_domain"] = [
        CallSpec(
            service_factory=lambda: _ReturningService(
                {"success": True, "results": {"eigenvalue": -1.23}, "operation": "run_vqe"}
            ),
            action="run_vqe",
            params={},
            weight=1.0,
            description="real local computation",
        ),
        CallSpec(
            service_factory=lambda: _ReturningService(
                {"success": True, "conclusion": "Looks plausible"}
            ),
            action="scientific_reasoning",
            params={},
            weight=1.0,
            description="heuristic llm reasoning",
        ),
        CallSpec(
            service_factory=lambda: _ReturningService(
                {"success": True, "backend": "atlas_fallback", "support_score": 0.8}
            ),
            action="paperqa2_verify_claim",
            params={},
            weight=1.0,
            description="fallback citation synthesis",
        ),
    ]

    result = await service.process_request(
        {
            "action": "corroborate",
            "hypothesis": {
                "title": "Unit test hypothesis",
                "description": "Validate realism-aware support metrics",
                "domain": "unit_test_domain",
            },
        }
    )

    aggregate = result["aggregate"]
    assert aggregate["support_score"] < aggregate["nominal_support_score"]
    assert aggregate["real_success_count"] == 1
    assert aggregate["tier_counts"]["real_local"] == 1
    assert aggregate["tier_counts"]["heuristic"] == 1
    assert aggregate["tier_counts"]["fallback"] == 1
    assert 0 < aggregate["tool_realism_score"] < 1


def test_truncate_serializes_complex_numbers_without_failing():
    service = ToolEvidenceOrchestratorService()

    result = service._truncate(
        {
            "statevector": [1 + 2j, 0.5 - 0.25j],
            "probabilities": [0.75, 0.25],
        }
    )

    assert result["statevector"][0]["real"] == pytest.approx(1.0)
    assert result["statevector"][0]["imag"] == pytest.approx(2.0)
    assert result["probabilities"] == [0.75, 0.25]
