import re

import pytest


@pytest.mark.asyncio
async def test_registry_exposes_orchestrator_domains():
    from run_agent_with_tools import DynamicToolRegistry
    from app.services.tool_evidence_orchestrator import ToolEvidenceOrchestratorService

    registry = DynamicToolRegistry()
    orchestrator = ToolEvidenceOrchestratorService()

    for domain in orchestrator.domain_routes.keys():
        safe_dom = re.sub(r"[^a-zA-Z0-9_]+", "_", domain.strip().lower())
        evidence_tool = f"evidence_corroborate_{safe_dom}"
        tools = registry.list_tools_for_domain(domain)
        assert evidence_tool in tools, f"Missing evidence tool for domain={domain}"


@pytest.mark.asyncio
async def test_literature_search_tool_uses_service(monkeypatch):
    from run_agent_with_tools import DynamicToolRegistry

    # Patch LiteratureService.process_request to avoid network / external deps
    from app.services.literature.literature_service import LiteratureService

    async def fake_process_request(self, request_data):
        assert request_data.get("action") in {"search_papers", "search_arxiv", "search_patents"}
        return {
            "success": True,
            "results": [
                {"title": "Paper A", "year": 2020, "authors": "Doe et al."},
                {"title": "Paper B", "year": 2019, "authors": "Roe et al."},
            ],
        }

    monkeypatch.setattr(LiteratureService, "process_request", fake_process_request, raising=True)

    registry = DynamicToolRegistry()
    assert "literature_search" in registry.tools

    out = await registry.execute_tool("literature_search", "papers:goldbach conjecture")
    assert "Paper A" in out


@pytest.mark.asyncio
async def test_registry_domain_scoping_filters_cross_domain_tools():
    from run_agent_with_tools import DynamicToolRegistry

    registry = DynamicToolRegistry(scope_domain="chemistry")

    # Chemistry should be present
    assert "computational_chemistry" in registry.tools

    # Cross-domain math tools should not be registered
    assert "sympy_solve_equation" not in registry.tools
    assert "z3_prover" not in registry.tools

    # Research tools remain available under scoping
    assert "literature_search" in registry.tools
    assert "literature_verify_hypothesis_plus" in registry.tools


@pytest.mark.asyncio
async def test_literature_verify_hypothesis_plus_tool_uses_service(monkeypatch):
    from run_agent_with_tools import DynamicToolRegistry

    from app.services.literature.literature_service import LiteratureService

    async def fake_process_request(self, request_data):
        assert request_data.get("action") == "verify_hypothesis_plus"
        assert isinstance(request_data.get("hypothesis"), dict)
        assert request_data.get("topic")
        return {
            "success": True,
            "support_score": 0.77,
            "reasons": ["Evidence supports the claim"],
            "sources": [
                {
                    "source": "arxiv",
                    "title": "A Relevant Paper",
                    "url": "https://arxiv.org/abs/1234.5678",
                    "abstract": "We study a relevant phenomenon...",
                }
            ],
        }

    monkeypatch.setattr(LiteratureService, "process_request", fake_process_request, raising=True)

    registry = DynamicToolRegistry()
    assert "literature_verify_hypothesis_plus" in registry.tools

    out = await registry.execute_tool(
        "literature_verify_hypothesis_plus",
        "chemistry:photocatalytic water splitting via doped TiO2",
    )
    assert "support_score" in out
    assert "0.77" in out
    assert "A Relevant Paper" in out
