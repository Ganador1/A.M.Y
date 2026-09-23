import pytest

from app.services.external_science.external_science_service import ExternalScienceService
from app.services.external_science.paperqa2_adapter import PaperQA2Adapter


class _FakeFacade:
    def unified_search(self, query, k):
        return {
            "results": [
                {
                    "id": "oa:1",
                    "title": "Symmetry-preserving ansatz improves noisy VQE for Heisenberg systems",
                    "authors": ["Alice Example", "Bob Example"],
                    "abstract": "A symmetry-preserving ansatz reduces error under depolarizing noise in VQE.",
                    "year": 2025,
                    "doi": "10.1000/example1",
                    "source": "openalex",
                },
                {
                    "id": "oa:2",
                    "title": "Noise-aware variational algorithms for 2-qubit Hamiltonians",
                    "authors": ["Carol Example"],
                    "abstract": "Variational ansatz design affects energy estimation error in noisy settings.",
                    "year": 2024,
                    "doi": "10.1000/example2",
                    "source": "openalex",
                },
            ]
        }

    class arxiv:
        @staticmethod
        def search(query, k):
            return {
                "results": [
                    {
                        "id": "arxiv:1",
                        "title": "Heisenberg Hamiltonian error mitigation with structured ansatze",
                        "authors": ["Dana Example"],
                        "abstract": "Structured ansatze improve robustness for small Heisenberg systems.",
                        "year": 2025,
                        "doi": None,
                        "source": "arxiv",
                    }
                ]
            }


@pytest.mark.asyncio
async def test_paperqa2_fallback_produces_citations(monkeypatch):
    adapter = PaperQA2Adapter({"enabled": True, "max_results": 5})
    monkeypatch.setattr(adapter, "facade", _FakeFacade())

    result = await adapter.process_request(
        {
            "action": "verify_claim",
            "claim": "symmetry-preserving ansatz reduces noisy Heisenberg Hamiltonian VQE error",
            "domain": "quantum_computing",
            "max_results": 5,
        }
    )

    assert result["success"] is True
    assert result["backend"] == "atlas_fallback"
    assert result["support_score"] > 0.3
    assert len(result["citations"]) >= 2
    assert "PaperQA2-style synthesis" in result["answer"]


@pytest.mark.asyncio
async def test_external_science_service_lists_adapter_status():
    service = ExternalScienceService()

    result = await service.process_request({"action": "list_adapters"})

    assert result["success"] is True
    assert "paperqa2" in result["adapters"]
    assert "mattergen" in result["adapters"]


@pytest.mark.asyncio
async def test_external_science_service_routes_paperqa_action(monkeypatch):
    service = ExternalScienceService()
    monkeypatch.setattr(service.adapters["paperqa2"], "facade", _FakeFacade())

    result = await service.process_request(
        {
            "action": "paperqa2_verify_claim",
            "claim": "symmetry-preserving ansatz reduces noisy Heisenberg Hamiltonian VQE error",
            "domain": "quantum_computing",
        }
    )

    assert result["success"] is True
    assert result["adapter"] == "paperqa2"
