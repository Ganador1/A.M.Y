import pytest

from app.integrations.literature_clients import ClinicalTrialsClient, NasaExoplanetArchiveClient, RcsbPdbClient

CTG_YEAR = 2020
PDB_YEAR = 2021
EXO_YEAR = 2011


def test_clinicaltrials_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AXIOM_DISABLE_NET", raising=False)
    client = ClinicalTrialsClient()

    def fake_get(url: str, params=None):  # type: ignore[no-untyped-def]
        assert url.endswith("/studies")
        assert params and "query.term" in params
        return {
            "studies": [
                {
                    "protocolSection": {
                        "identificationModule": {"nctId": "NCT00000001", "briefTitle": "Test Trial"},
                        "descriptionModule": {"briefSummary": "A brief summary"},
                        "statusModule": {"studyFirstPostDateStruct": {"date": f"{CTG_YEAR}-01-15"}},
                    }
                }
            ]
        }

    monkeypatch.setattr(client, "get", fake_get)
    out = client.search("cancer", page_size=3)
    assert out["success"] is True
    assert len(out["results"]) == 1
    r = out["results"][0]
    assert r["id"] == "NCT00000001"
    assert r["title"] == "Test Trial"
    assert r["abstract"] == "A brief summary"
    assert r["year"] == CTG_YEAR
    assert r["source"] == "clinicaltrials"
    assert r["url"] == "https://clinicaltrials.gov/study/NCT00000001"


def test_clinicaltrials_offline_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AXIOM_DISABLE_NET", "1")
    client = ClinicalTrialsClient()
    out = client.search("anything", page_size=5)
    assert out["success"] is True
    assert out["results"] == []
    assert isinstance(out.get("raw"), dict)
    assert out["raw"].get("error") == "network_disabled"


def test_rcsb_pdb_mapping(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AXIOM_DISABLE_NET", raising=False)
    client = RcsbPdbClient()

    def fake_post(url: str, json_body=None):  # type: ignore[no-untyped-def]
        assert "rcsbsearch" in url
        _ = json_body
        return {"result_set": [{"identifier": "1ABC"}, {"identifier": "2XYZ"}]}

    def fake_get(url: str, params=None):  # type: ignore[no-untyped-def]
        _ = params
        if url.endswith("/1ABC"):
            return {
                "struct": {"title": "Structure One"},
                "rcsb_primary_citation": {
                    "rcsb_authors": ["A. Author", "B. Author"],
                    "year": 2019,
                    "pdbx_database_id_doi": "10.1234/example",
                },
            }
        if url.endswith("/2XYZ"):
            return {"struct": {"title": "Structure Two"}, "rcsb_primary_citation": {"year": str(PDB_YEAR)}}
        raise AssertionError(f"unexpected url: {url}")

    monkeypatch.setattr(client, "post", fake_post)
    monkeypatch.setattr(client, "get", fake_get)

    out = client.search("kinase", rows=2)
    assert out["success"] is True
    assert [r["id"] for r in out["results"]] == ["1ABC", "2XYZ"]
    assert out["results"][0]["title"] == "Structure One"
    assert out["results"][0]["doi"] == "10.1234/example"
    assert out["results"][0]["authors"] == ["A. Author", "B. Author"]
    assert out["results"][0]["source"] == "rcsb_pdb"
    assert out["results"][0]["url"] == "https://www.rcsb.org/structure/1ABC"
    assert out["results"][1]["year"] == PDB_YEAR


def test_rcsb_pdb_offline_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AXIOM_DISABLE_NET", "true")
    client = RcsbPdbClient()
    out = client.search("protein", rows=3)
    assert out["success"] is True
    assert out["results"] == []


def test_exoplanet_archive_parses_raw_json(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AXIOM_DISABLE_NET", raising=False)
    client = NasaExoplanetArchiveClient()

    def fake_get(url: str, params=None):  # type: ignore[no-untyped-def]
        assert "nph-nstedAPI" in url
        _ = params
        # The HttpClient may return text under {"raw": ...}; ensure we parse it.
        return {
            "raw": f"[{{\"pl_name\": \"Kepler-22 b\", \"hostname\": \"Kepler-22\", \"disc_year\": {EXO_YEAR}, \"discoverymethod\": \"Transit\"}}]"
        }

    monkeypatch.setattr(client, "get", fake_get)

    out = client.search("Kepler-22", k=5)
    assert out["success"] is True
    assert len(out["results"]) == 1
    r = out["results"][0]
    assert r["id"] == "Kepler-22 b"
    assert "Exoplanet Archive" in (r["title"] or "")
    assert r["year"] == EXO_YEAR
    assert r["source"] == "nasa_exoplanet_archive"


def test_exoplanet_archive_offline_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("AXIOM_DISABLE_NET", "yes")
    client = NasaExoplanetArchiveClient()
    out = client.search("Kepler", k=3)
    assert out["success"] is True
    assert out["results"] == []
