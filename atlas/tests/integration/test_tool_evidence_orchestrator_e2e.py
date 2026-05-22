import pytest
from dataclasses import replace

from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService


@pytest.mark.asyncio
async def test_materials_science_route_invokes_new_tools_end_to_end():
    orchestrator = ToolEvidenceOrchestratorService()
    orchestrator.enable_early_stopping = False
    domain = "materials_science"

    expected_actions = {
        "verify_hypothesis_plus",
        "scientific_reasoning",
        "material_properties",
        "power_analysis",
    }

    available_actions = [spec.action for spec in orchestrator.domain_routes[domain]]
    for action in expected_actions:
        assert action in available_actions, f"{action} no está configurada en rutas de {domain}"

    stub_names = {
        "verify_hypothesis_plus": "LiteratureService",
        "scientific_reasoning": "ScientificAIService",
        "material_properties": "MolecularDynamicsService",
        "power_analysis": "StatisticalValidationService",
    }

    call_records = []
    new_route = []

    def _make_stub_factory(action_name: str, service_label: str):
        async def process_request(_self, payload):
            call_records.append({"action": action_name, "payload": payload})
            return {
                "success": True,
                "stub_action": action_name,
                "received_params": payload,
                "support_score": 0.8,
            }

        StubClass = type(f"{service_label}Stub", (), {"process_request": process_request})
        return lambda StubClass=StubClass: StubClass()

    for spec in orchestrator.domain_routes[domain]:
        if spec.action not in expected_actions:
            continue

        service_factory = _make_stub_factory(spec.action, stub_names[spec.action])
        new_route.append(replace(spec, service_factory=service_factory))

    orchestrator.domain_routes[domain] = new_route

    hypothesis = {
        "title": "High-Conductivity Metamaterial for Thermal Regulation",
        "description": "Evaluate whether nano-layered composites can maintain stable thermal conductivity under rapid cycling.",
        "domain": domain,
        "variables": {
            "layer_thickness": "50nm",
            "matrix_material": "Graphene",
            "operating_temperature": "350K",
        },
        "assumptions": ["Controlled atmosphere", "Stable thermal gradients"],
    }

    result = await orchestrator.process_request({
        "action": "corroborate",
        "hypothesis": hypothesis,
    })

    assert result["success"] is True
    assert len(result["evidence_items"]) == len(expected_actions)

    called_actions = {record["action"] for record in call_records}
    assert called_actions == expected_actions

    evidence_operations = {item["operation"] for item in result["evidence_items"]}
    assert expected_actions <= evidence_operations

    for record in call_records:
        payload = record["payload"]
        action = record["action"]
        assert payload["action"] == action

        if action == "verify_hypothesis_plus":
            assert payload["hypothesis"]["title"] == hypothesis["title"]
        elif action == "scientific_reasoning":
            assert payload["problem"] == hypothesis["title"]
            assert payload["context"] == hypothesis["description"]
        elif action == "material_properties":
            assert payload["material_structure"] == hypothesis["title"]
        elif action == "power_analysis":
            assert payload["operation"] == "power_analysis"

    aggregate = result.get("aggregate", {})
    assert aggregate.get("coverage") == 1.0
    assert aggregate.get("weighted_coverage") == 1.0
    assert aggregate.get("support_score", 0) > 0
