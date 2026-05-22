import asyncio

import pytest

from app.services.literature.literature_service import LiteratureService


def test_verify_hypothesis_plus_includes_proteins(monkeypatch: pytest.MonkeyPatch) -> None:
    svc = LiteratureService()

    monkeypatch.setattr(svc.facade, "unified_search", lambda q, k=10: {"success": True, "results": []})
    monkeypatch.setattr(svc.facade.arxiv, "search", lambda q, k=10: {"success": True, "results": []})
    monkeypatch.setattr(svc.facade, "search_patents", lambda q, k=5: {"success": True, "results": []})
    monkeypatch.setattr(svc.facade, "search_materials", lambda f, k=5: {"success": True, "results": []})
    monkeypatch.setattr(svc.facade, "search_chembl", lambda q, k=5: {"success": True, "results": []})
    monkeypatch.setattr(svc.facade, "search_clinical_trials", lambda q, k=5: {"success": True, "results": []})
    monkeypatch.setattr(svc.facade, "search_pdb", lambda q, k=5: {"success": True, "results": []})
    monkeypatch.setattr(svc.facade, "search_exoplanets", lambda q, k=5: {"success": True, "results": []})

    monkeypatch.setattr(
        svc.facade,
        "search_proteins",
        lambda q, k=5: {
            "success": True,
            "results": [
                {
                    "id": "P12345",
                    "title": "Example protein",
                    "organism": "Homo sapiens",
                    "length": 123,
                    "reviewed": True,
                    "source": "uniprot",
                }
            ],
        },
    )

    payload = {
        "action": "verify_hypothesis_plus",
        "hypothesis": {"title": "Protein binding mutation impacts function"},
        "k": 8,
    }

    out = asyncio.run(svc.process_request(payload))
    assert out["success"] is True
    assert out["sources"]["proteins"]
    assert any("UniProt" in r for r in out.get("reasons", []))
