import os


def test_europepmc_client_maps_results(monkeypatch):
    from app.integrations import literature_clients

    sample = {
        "hitCount": 1,
        "resultList": {
            "result": [
                {
                    "id": "123",
                    "source": "MED",
                    "title": "Example paper about p53",
                    "authorString": "Smith J, Doe A",
                    "abstractText": "We study p53 in cancer.",
                    "pubYear": "2020",
                    "doi": "10.1000/example",
                }
            ]
        },
    }

    def fake_get(self, url, params=None):
        return sample

    monkeypatch.setattr(literature_clients.EuropePMCClient, "get", fake_get)

    client = literature_clients.EuropePMCClient()
    res = client.search("p53", page_size=1)

    assert res["success"] is True
    assert len(res["results"]) == 1
    paper = res["results"][0]
    assert paper["source"] == "europepmc"
    assert paper["title"] == "Example paper about p53"
    assert paper["doi"] == "10.1000/example"
    assert "Smith" in " ".join(paper.get("authors") or [])


def test_literature_facade_unified_search_includes_europepmc(monkeypatch):
    from app.integrations import literature_clients

    def fake_search(self, query, page_size=10, result_type="lite"):
        return {
            "success": True,
            "results": [
                {
                    "id": "X",
                    "title": "Only EuropePMC result",
                    "authors": ["A"],
                    "abstract": None,
                    "year": "2021",
                    "doi": None,
                    "source": "europepmc",
                }
            ],
        }

    monkeypatch.setattr(literature_clients.EuropePMCClient, "search", fake_search)
    # Make other sources quiet to keep deterministic.
    monkeypatch.setattr(literature_clients.OpenAlexClient, "search", lambda self, query, per_page=10: {"success": True, "results": []})
    monkeypatch.setattr(literature_clients.SemanticScholarClient, "search", lambda self, query, limit=10, fields=None: {"success": True, "results": []})
    monkeypatch.setattr(literature_clients.CrossrefClient, "search", lambda self, query, rows=10: {"success": True, "results": []})
    monkeypatch.setattr(literature_clients.PubMedClient, "search", lambda self, query, db="pubmed", retmax=10: {"success": True, "results": []})
    monkeypatch.setattr(literature_clients.ArxivClient, "search", lambda self, query, max_results=10: {"success": True, "results": []})

    facade = literature_clients.LiteratureFacade()
    out = facade.unified_search("anything", k=5)

    assert out["success"] is True
    assert len(out["results"]) == 1
    assert out["results"][0]["source"] == "europepmc"


def test_europepmc_offline_mode_returns_success(monkeypatch):
    os.environ["AXIOM_DISABLE_NET"] = "1"
    try:
        from app.integrations.literature_clients import EuropePMCClient

        client = EuropePMCClient()
        res = client.search("p53", page_size=3)
        assert res["success"] is True
        assert isinstance(res.get("results"), list)
    finally:
        os.environ.pop("AXIOM_DISABLE_NET", None)
