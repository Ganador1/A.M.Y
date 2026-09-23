import pytest

from app.services.literature.literature_service import LiteratureService


class _FakeFacade:
    def unified_search(self, query, k):
        return {
            "results": [
                {
                    "id": "p1",
                    "title": "Symmetry-preserving ansatz for noisy Heisenberg VQE",
                    "authors": ["A. Author"],
                    "abstract": "A symmetry-preserving ansatz reduces error under depolarizing noise.",
                    "year": 2025,
                    "doi": "10.1000/p1",
                    "source": "openalex",
                }
            ]
        }

    class arxiv:
        @staticmethod
        def search(query, k):
            return {"results": []}

    def search_patents(self, query, k):
        return {"results": []}

    def search_materials(self, query, k):
        return {"results": []}

    def search_chembl(self, query, k):
        return {"results": []}

    def search_clinical_trials(self, query, k):
        return {"results": []}

    def search_pdb(self, query, k):
        return {"results": []}

    def search_proteins(self, query, k):
        return {"results": []}

    def search_exoplanets(self, query, k):
        return {"results": []}

    def search_open_targets(self, query, k):
        return {"results": []}

    def search_gwas(self, query, k):
        return {"results": []}


class _FakeExternalScienceService:
    async def process_request(self, request_data):
        return {
            "success": True,
            "support_score": 0.8,
            "reasons": ["PaperQA2 recovered relevant cited evidence."],
            "citations": [{"citation": "Example et al. (2025). Symmetry-preserving ansatz..."}],
        }


@pytest.mark.asyncio
async def test_verify_hypothesis_plus_includes_paperqa2(monkeypatch):
    service = LiteratureService()
    monkeypatch.setattr(service, "facade", _FakeFacade())
    monkeypatch.setattr(
        "app.services.literature.literature_service.external_science_service",
        _FakeExternalScienceService(),
    )

    result = await service.process_request(
        {
            "action": "verify_hypothesis_plus",
            "topic": "symmetry-preserving ansatz reduces noisy Heisenberg VQE error",
            "domain": "quantum_computing",
            "k": 6,
        }
    )

    assert result["success"] is True
    assert result["support_score"] >= 0.4
    assert "paperqa2" in result["sources"]
    assert any("PaperQA2" in reason or "cited evidence" in reason for reason in result["reasons"])
