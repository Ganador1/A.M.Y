from app.services.literature_search import LiteratureSearchService


def test_offline_cache_upsert_and_search(tmp_path):
    cache_dir = tmp_path / "literature_cache"
    svc = LiteratureSearchService(cache_dir=str(cache_dir))

    papers = [
        {
            "paper_id": "p1",
            "title": "Quantum Computing Advances",
            "abstract": "We discuss advances in quantum algorithms.",
            "authors": ["Alice", "Bob"],
            "journal": "Quantum Journal",
            "year": 2024,
            "doi": "10.1000/qc.adv.2024",
            "citations": 12,
        },
        {
            "paper_id": "p2",
            "title": "Materials for Energy Storage",
            "abstract": "Lithium-ion batteries and beyond.",
            "authors": ["Carol"],
            "journal": "Energy Materials",
            "year": 2023,
            "citations": 5,
        },
    ]

    res_upsert = svc.cache_upsert({"papers": papers})
    assert res_upsert.get("success") is True
    assert res_upsert.get("added") == 2
    assert res_upsert.get("total") == 2

    # Should have persisted to sqlite-based cache
    assert (cache_dir / "cache.db").exists()

    res_search = svc.search_offline({"query": "quantum", "max_results": 10})
    assert res_search.get("success") is True
    assert res_search["summary"]["total_found"] == 1
    assert res_search["papers"][0]["paper_id"] == "p1"
