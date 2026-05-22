"""
Unified literature and knowledge API clients
- Papers: OpenAlex, Europe PMC, Semantic Scholar, Crossref, PubMed, arXiv
- Patents: PatentsView
- Materials: Materials Project v2 (POST /materials/summary)
- Chemistry: ChEMBL
- Proteins: UniProt search + AlphaFold predictions
- Clinical trials: ClinicalTrials.gov v2
- Structures: RCSB PDB Search API + Data API
- Astronomy: NASA Exoplanet Archive (legacy nstedAPI)
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional
import os
import time
import json
import datetime as _dt
import xml.etree.ElementTree as ET

import httpx
from app.middleware.trace_id_middleware import (
    TRACE_HEADER,
    get_current_trace_id,
    ensure_trace_id,
)

DEFAULT_TIMEOUT = float(os.getenv("LIT_HTTP_TIMEOUT", "10"))
DEFAULT_MAX_RETRIES = int(os.getenv("LIT_HTTP_MAX_RETRIES", "2"))
DEFAULT_BACKOFF = float(os.getenv("LIT_HTTP_BACKOFF", "0.5"))

UserAgent = os.getenv("LIT_HTTP_UA", "AXIOM-Atlas/1.0 (+https://example.org)")
OpenAlexMailto = os.getenv("OPENALEX_MAILTO", "you@example.com")
NCBI_TOOL = os.getenv("NCBI_TOOL")
NCBI_EMAIL = os.getenv("NCBI_EMAIL")
NCBI_API_KEY = os.getenv("NCBI_API_KEY")


class HttpClient:
    """
    Synchronous HTTP client with retry logic.
    
    NOTE: This client uses time.sleep() for retry backoff in synchronous context.
    This is acceptable since all methods are synchronous (def, not async def).
    For async code, consider creating AsyncHttpClient in the future.
    
    TODO (ROADMAP 5): Migrate to AsyncHttpClient with asyncio.sleep()
    """
    def __init__(self):
        self.headers = {"User-Agent": UserAgent}
        self.client = httpx.Client(
            headers=self.headers,
            timeout=DEFAULT_TIMEOUT,
            event_hooks={
                "request": [self._inject_trace_id]
            },
        )
        self.offline = os.getenv("AXIOM_DISABLE_NET", "0").lower() in {"1", "true", "yes"}

    def _inject_trace_id(self, request: httpx.Request) -> None:
        tid = get_current_trace_id() or ensure_trace_id()
        if tid and TRACE_HEADER not in request.headers:
            request.headers[TRACE_HEADER] = tid

    def get(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if self.offline:
            return {"error": "network_disabled", "url": url, "params": params or {}}
        params = params or {}
        last_exc: Optional[Exception] = None
        for attempt in range(1, DEFAULT_MAX_RETRIES + 2):
            try:
                resp = self.client.get(url, params=params)
                if resp.status_code == 200:
                    ct = resp.headers.get("content-type", "")
                    if "application/json" in ct:
                        return resp.json()
                    return {"raw": resp.text}
                if resp.status_code in (429, 500, 502, 503, 504):
                    time.sleep(DEFAULT_BACKOFF * attempt)
                    continue
                return {"error": f"HTTP {resp.status_code}", "body": resp.text}
            except Exception as e:
                last_exc = e
                time.sleep(DEFAULT_BACKOFF * attempt)
        return {"error": str(last_exc) if last_exc else "request_failed"}

    def post(self, url: str, json_body: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        if self.offline:
            return {"error": "network_disabled", "url": url, "payload": json_body or {}}
        json_body = json_body or {}
        last_exc: Optional[Exception] = None
        for attempt in range(1, DEFAULT_MAX_RETRIES + 2):
            try:
                resp = self.client.post(url, json=json_body)
                if resp.status_code == 200:
                    ct = resp.headers.get("content-type", "")
                    if "application/json" in ct:
                        return resp.json()
                    return {"raw": resp.text}
                if resp.status_code in (429, 500, 502, 503, 504):
                    time.sleep(DEFAULT_BACKOFF * attempt)
                    continue
                return {"error": f"HTTP {resp.status_code}", "body": resp.text}
            except Exception as e:
                last_exc = e
                time.sleep(DEFAULT_BACKOFF * attempt)
        return {"error": str(last_exc) if last_exc else "request_failed"}


# Unified mapping helpers

def map_paper(source: str, item: Dict[str, Any]) -> Dict[str, Any]:
    if source == "openalex":
        id_ = item.get("id")
        title = item.get("title")
        authors = [a.get("author", {}).get("display_name") if isinstance(a, dict) else None for a in item.get("authorships", [])]
        abstract = item.get("abstract_inverted_index")
        if isinstance(abstract, dict):
            tokens = sorted(((pos, word) for word, poss in abstract.items() for pos in poss))
            abstract_text = " ".join(w for _, w in tokens)
        else:
            abstract_text = None
        year = item.get("publication_year")
        doi = item.get("doi")
        return {"id": id_, "title": title, "authors": [a for a in authors if a], "abstract": abstract_text, "year": year, "doi": doi, "source": source}
    if source == "europepmc":
        # Europe PMC uses keys like: title, authorString, abstractText, pubYear, doi
        title = item.get("title")
        authors = []
        author_string = item.get("authorString")
        if isinstance(author_string, str) and author_string.strip():
            # Keep it simple: split by comma; avoid heavy parsing.
            authors = [a.strip() for a in author_string.split(",") if a.strip()]
        abstract_text = item.get("abstractText") or item.get("abstract")
        year = item.get("pubYear") or item.get("year")
        doi = item.get("doi")
        source_id = item.get("id") or item.get("pmid") or item.get("pmcid")
        return {
            "id": source_id,
            "title": title,
            "authors": authors,
            "abstract": abstract_text,
            "year": year,
            "doi": doi,
            "source": source,
        }
    if source == "arxiv":
        return {"id": item.get("id"), "title": item.get("title"), "authors": item.get("authors"), "abstract": item.get("summary"), "year": item.get("year"), "doi": item.get("doi"), "source": source}
    if source == "pubmed":
        return {"id": item.get("uid") or item.get("Id"), "title": item.get("title") or item.get("Title"), "authors": item.get("authors"), "abstract": item.get("abstract"), "year": item.get("pubdate") or item.get("Year"), "doi": item.get("elocationid") or item.get("DOI"), "source": source}
    if source == "semanticscholar":
        return {"id": item.get("paperId"), "title": item.get("title"), "authors": [a.get("name") for a in item.get("authors", [])], "abstract": item.get("abstract"), "year": item.get("year"), "doi": item.get("doi"), "source": source}
    if source == "crossref":
        author_names = []
        for a in item.get("author", []) or []:
            given = a.get("given")
            family = a.get("family")
            if given or family:
                author_names.append(" ".join([p for p in [given, family] if p]))
        return {"id": item.get("DOI"), "title": (item.get("title") or [None])[0], "authors": author_names, "abstract": item.get("abstract"), "year": (item.get("issued", {}).get("date-parts", [[None]])[0] or [None])[0], "doi": item.get("DOI"), "source": source}
    return {"id": item.get("id"), "title": item.get("title"), "source": source}


# Papers
class OpenAlexClient(HttpClient):
    BASE = "https://api.openalex.org"
    def search(self, query: str, per_page: int = 10) -> Dict[str, Any]:
        params = {"search": query, "per-page": per_page, "mailto": OpenAlexMailto}
        data = self.get(f"{self.BASE}/works", params)
        results = [map_paper("openalex", it) for it in (data or {}).get("results", [])]
        return {"success": True, "results": results, "raw": data}

class SemanticScholarClient(HttpClient):
    BASE = "https://api.semanticscholar.org/graph/v1"
    def search(self, query: str, limit: int = 10, fields: str = "title,authors,year,abstract,doi") -> Dict[str, Any]:
        params = {"query": query, "limit": limit, "fields": fields}
        data = self.get(f"{self.BASE}/paper/search", params)
        results = [map_paper("semanticscholar", it) for it in (data or {}).get("data", [])]
        return {"success": True, "results": results, "raw": data}

class CrossrefClient(HttpClient):
    BASE = "https://api.crossref.org"
    def search(self, query: str, rows: int = 10) -> Dict[str, Any]:
        params = {"query": query, "rows": rows}
        data = self.get(f"{self.BASE}/works", params)
        results = [map_paper("crossref", it) for it in (data or {}).get("message", {}).get("items", [])]
        return {"success": True, "results": results, "raw": data}

class PubMedClient(HttpClient):
    ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    def search(self, query: str, db: str = "pubmed", retmax: int = 10) -> Dict[str, Any]:
        params: Dict[str, Any] = {"db": db, "term": query, "retmode": "json", "retmax": retmax}
        # NCBI usage guidelines: include tool/email when possible; api_key for higher throughput.
        if NCBI_TOOL:
            params["tool"] = NCBI_TOOL
        if NCBI_EMAIL:
            params["email"] = NCBI_EMAIL
        if NCBI_API_KEY:
            params["api_key"] = NCBI_API_KEY
        data = self.get(self.ESEARCH, params)
        ids = (data or {}).get("esearchresult", {}).get("idlist", [])
        if not ids:
            return {"success": True, "results": [], "raw": data}
        sparams: Dict[str, Any] = {"db": db, "id": ",".join(ids), "retmode": "json"}
        if NCBI_TOOL:
            sparams["tool"] = NCBI_TOOL
        if NCBI_EMAIL:
            sparams["email"] = NCBI_EMAIL
        if NCBI_API_KEY:
            sparams["api_key"] = NCBI_API_KEY
        sdata = self.get(self.ESUMMARY, sparams)
        summaries = (sdata or {}).get("result", {})
        results: List[Dict[str, Any]] = []
        for id_ in ids:
            rec = summaries.get(id_, {})
            if rec:
                results.append(map_paper("pubmed", rec))
        return {"success": True, "results": results, "raw": {"search": data, "summary": sdata}}

class EuropePMCClient(HttpClient):
    BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"

    def search(self, query: str, page_size: int = 10, result_type: str = "lite") -> Dict[str, Any]:
        # Docs: GET /search?query=...&format=json&pageSize=...&resultType=lite|core
        params = {
            "query": query,
            "format": "json",
            "pageSize": page_size,
            "resultType": result_type,
        }
        data = self.get(f"{self.BASE}/search", params)
        results_raw = (data or {}).get("resultList", {}).get("result", [])
        if not isinstance(results_raw, list):
            results_raw = []
        results = [map_paper("europepmc", it) for it in results_raw if isinstance(it, dict)]
        return {"success": True, "results": results, "raw": data}

class ArxivClient(HttpClient):
    BASE = "https://export.arxiv.org/api/query"
    def search(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        params = {"search_query": query, "start": 0, "max_results": max_results}
        raw = self.get(self.BASE, params)
        text = (raw or {}).get("raw") if isinstance(raw, dict) else None
        items: List[Dict[str, Any]] = []
        if text:
            try:
                root = ET.fromstring(text)
                ns = {"atom": "http://www.w3.org/2005/Atom"}
                for entry in root.findall("atom:entry", ns):
                    title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
                    summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
                    id_ = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
                    authors = [a.findtext("atom:name", default="", namespaces=ns) for a in entry.findall("atom:author", ns)]
                    published = entry.findtext("atom:published", default="", namespaces=ns)
                    year = None
                    if published:
                        try:
                            year = _dt.datetime.fromisoformat(published.replace("Z", "+00:00")).year
                        except Exception:
                            year = None
                    items.append({
                        "id": id_, "title": title, "authors": [a for a in authors if a],
                        "abstract": summary, "year": year, "doi": None, "source": "arxiv"
                    })
            except Exception:
                pass
        return {"success": True, "results": items, "raw": raw}


# Patents
class PatentsViewClient(HttpClient):
    BASE = "https://api.patentsview.org/patents/query"
    def search(self, query: str, per_page: int = 5) -> Dict[str, Any]:
        q = {"_text_any": {"patent_title": query}}
        params = {
            "q": json.dumps(q),
            "f": "patent_number,patent_title,patent_date,patent_abstract",
            "o": json.dumps({"per_page": per_page})
        }
        data = self.get(self.BASE, params)
        results = []
        for p in ((data or {}).get("patents") or []):
            results.append({
                "id": p.get("patent_number"),
                "title": p.get("patent_title"),
                "abstract": p.get("patent_abstract"),
                "year": (p.get("patent_date") or "")[:4] or None,
                "authors": [],
                "doi": None,
                "source": "patentsview"
            })
        return {"success": True, "results": results, "raw": data}


# Clinical trials
class ClinicalTrialsClient(HttpClient):
    BASE = "https://clinicaltrials.gov/api/v2"

    def search(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        # Docs: GET /api/v2/studies with query.term parameter
        params: Dict[str, Any] = {
            "query.term": query,
            "pageSize": max(1, min(int(page_size), 1000)),
        }
        data = self.get(f"{self.BASE}/studies", params)
        if not isinstance(data, dict) or data.get("error"):
            return {"success": True, "results": [], "raw": data}

        studies = data.get("studies")
        if not isinstance(studies, list):
            studies = []

        results: List[Dict[str, Any]] = []
        for s in studies:
            if not isinstance(s, dict):
                continue
            protocol = s.get("protocolSection") or {}
            ident = (protocol.get("identificationModule") or {}) if isinstance(protocol, dict) else {}
            desc = (protocol.get("descriptionModule") or {}) if isinstance(protocol, dict) else {}
            status = (protocol.get("statusModule") or {}) if isinstance(protocol, dict) else {}

            nct_id = ident.get("nctId") or s.get("nctId")
            title = ident.get("briefTitle") or ident.get("officialTitle") or s.get("briefTitle")
            summary = desc.get("briefSummary") or desc.get("detailedDescription")

            year = None
            date_struct = status.get("studyFirstPostDateStruct")
            if isinstance(date_struct, dict):
                date_val = date_struct.get("date")
                if isinstance(date_val, str) and len(date_val) >= 4:
                    try:
                        year = int(date_val[:4])
                    except Exception:
                        year = None

            url = None
            if isinstance(nct_id, str) and nct_id:
                url = f"https://clinicaltrials.gov/study/{nct_id}"

            results.append(
                {
                    "id": nct_id,
                    "title": title,
                    "authors": [],
                    "abstract": summary,
                    "year": year,
                    "doi": None,
                    "source": "clinicaltrials",
                    "url": url,
                }
            )

        return {"success": True, "results": results, "raw": data}


# Structural biology / macromolecular structures
class RcsbPdbClient(HttpClient):
    SEARCH = "https://search.rcsb.org/rcsbsearch/v2/query"
    DATA = "https://data.rcsb.org/rest/v1/core/entry/"

    def search(self, query: str, rows: int = 5) -> Dict[str, Any]:
        rows_i = max(1, min(int(rows), 100))
        payload = {
            "query": {
                "type": "terminal",
                "service": "full_text",
                "parameters": {"value": query},
            },
            "return_type": "entry",
            "request_options": {
                "paginate": {"start": 0, "rows": rows_i},
            },
        }
        data = self.post(self.SEARCH, payload)
        if not isinstance(data, dict) or data.get("error"):
            return {"success": True, "results": [], "raw": data}

        result_set = data.get("result_set")
        if not isinstance(result_set, list):
            result_set = []

        ids: List[str] = []
        for r in result_set:
            if isinstance(r, dict) and isinstance(r.get("identifier"), str):
                ids.append(r["identifier"])

        results: List[Dict[str, Any]] = []
        for pdb_id in ids[:rows_i]:
            entry = self.get(self.DATA + pdb_id)
            if not isinstance(entry, dict) or entry.get("error"):
                results.append(
                    {
                        "id": pdb_id,
                        "title": pdb_id,
                        "authors": [],
                        "abstract": None,
                        "year": None,
                        "doi": None,
                        "source": "rcsb_pdb",
                        "url": f"https://www.rcsb.org/structure/{pdb_id}",
                    }
                )
                continue

            title = None
            struct = entry.get("struct")
            if isinstance(struct, dict):
                title = struct.get("title")

            citation = entry.get("rcsb_primary_citation")
            authors: List[str] = []
            year = None
            doi = None
            if isinstance(citation, dict):
                ra = citation.get("rcsb_authors")
                if isinstance(ra, list):
                    authors = [a for a in ra if isinstance(a, str) and a]
                yv = citation.get("year")
                if isinstance(yv, int):
                    year = yv
                elif isinstance(yv, str) and yv.isdigit():
                    year = int(yv)
                doi_v = citation.get("pdbx_database_id_doi") or citation.get("doi")
                if isinstance(doi_v, str) and doi_v:
                    doi = doi_v

            results.append(
                {
                    "id": pdb_id,
                    "title": title or pdb_id,
                    "authors": authors,
                    "abstract": None,
                    "year": year,
                    "doi": doi,
                    "source": "rcsb_pdb",
                    "url": f"https://www.rcsb.org/structure/{pdb_id}",
                }
            )

        return {"success": True, "results": results, "raw": {"search": data, "entries": ids[:rows_i]}}


# Astronomy / exoplanets
class NasaExoplanetArchiveClient(HttpClient):
    BASE = "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/nstedAPI/nph-nstedAPI"

    def search(self, query: str, k: int = 5) -> Dict[str, Any]:
        # Legacy API supports SQL-like where/select; many tables moved to TAP.
        # We keep a minimal, best-effort query against the "ps" table.
        q = (query or "").strip()
        if not q:
            return {"success": True, "results": [], "raw": None}

        q_esc = q.replace("'", "''")
        where = f"pl_name like '%{q_esc}%' or hostname like '%{q_esc}%'"
        select = "pl_name,hostname,disc_year,discoverymethod,pl_orbper,pl_rade,pl_bmasse"
        params: Dict[str, Any] = {
            "table": "ps",
            "select": select,
            "where": where,
            "format": "json",
        }
        data = self.get(self.BASE, params)
        if not isinstance(data, (dict, list)):
            return {"success": True, "results": [], "raw": data}
        if isinstance(data, dict) and data.get("error"):
            return {"success": True, "results": [], "raw": data}

        rows = data
        if isinstance(data, dict) and "raw" in data and isinstance(data.get("raw"), str):
            try:
                rows = json.loads(data["raw"])
            except Exception:
                rows = []

        if not isinstance(rows, list):
            rows = []

        results: List[Dict[str, Any]] = []
        for r in rows[: max(1, min(int(k), 50))]:
            if not isinstance(r, dict):
                continue
            pl = r.get("pl_name")
            host = r.get("hostname")
            year = r.get("disc_year")
            abstract_parts = []
            if host:
                abstract_parts.append(f"Host: {host}")
            if r.get("discoverymethod"):
                abstract_parts.append(f"Method: {r.get('discoverymethod')}")
            if r.get("pl_orbper") is not None:
                abstract_parts.append(f"Period(d): {r.get('pl_orbper')}")
            if r.get("pl_rade") is not None:
                abstract_parts.append(f"Radius(Re): {r.get('pl_rade')}")
            if r.get("pl_bmasse") is not None:
                abstract_parts.append(f"Mass(Me): {r.get('pl_bmasse')}")

            results.append(
                {
                    "id": pl or host,
                    "title": f"Exoplanet Archive: {pl or host}",
                    "authors": [],
                    "abstract": "; ".join(abstract_parts) if abstract_parts else None,
                    "year": year,
                    "doi": None,
                    "source": "nasa_exoplanet_archive",
                    "url": "https://exoplanetarchive.ipac.caltech.edu/",
                }
            )

        return {"success": True, "results": results, "raw": data}


# Materials (v2)
class MaterialsProjectClient(HttpClient):
    BASE = "https://api.materialsproject.org/v2/materials/summary"
    def __init__(self):
        super().__init__()
        # Try load from environment and .env
        self.api_key = os.getenv("MATERIALS_PROJECT_API_KEY")
        if not self.api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                self.api_key = os.getenv("MATERIALS_PROJECT_API_KEY")
            except Exception:
                pass
        # Manual fallback: parse .env if still missing
        if not self.api_key:
            try:
                env_path = os.path.join(os.getcwd(), ".env")
                if os.path.exists(env_path):
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            s = line.strip()
                            if not s or s.startswith("#"):
                                continue
                            if s.startswith("MATERIALS_PROJECT_API_KEY"):
                                # Support formats KEY=VALUE or KEY: VALUE
                                import re
                                parts = re.split(r"[:=]", s, maxsplit=1)
                                if len(parts) == 2:
                                    val = parts[1].strip()
                                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                        val = val[1:-1]
                                    if val:
                                        self.api_key = val
                                        os.environ["MATERIALS_PROJECT_API_KEY"] = val
                                break
            except Exception:
                pass
        if self.api_key:
            self.client.headers.update({"X-API-KEY": self.api_key, "Content-Type": "application/json"})
        # Endpoints candidatos (por cambios de rutas)
        self._candidates = [
            # v2 documented endpoint(s)
            "https://api.materialsproject.org/v2/materials/summary/",
            "https://api.materialsproject.org/v2/materials/summary",
            # some deployments expose an explicit search subroute
            "https://api.materialsproject.org/v2/materials/summary/search",
            "https://api.materialsproject.org/v2/materials/summary/search/",
            # fallback to non-v2 routes (observed in some deployments)
            "https://api.materialsproject.org/materials/summary/",
            "https://api.materialsproject.org/materials/summary",
        ]

    def _post_mp(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        traces = {}
        d: Dict[str, Any] = {"error": "no_attempt"}
        for url in self._candidates:
            resp = self.post(url, payload)
            d = resp or {}
            traces[url] = d
            if isinstance(d, dict) and not d.get("error"):
                return {"data": d, "used": url, "traces": traces}
        # devuelve el último intento
        return {"data": d, "used": self._candidates[-1], "traces": traces}

    def _get_mp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        traces = {}
        d: Dict[str, Any] = {"error": "no_attempt"}
        for url in self._candidates:
            resp = self.get(url, params)
            d = resp or {}
            traces[url] = d
            if isinstance(d, dict) and not d.get("error"):
                return {"data": d, "used": url, "traces": traces}
        return {"data": d, "used": self._candidates[-1], "traces": traces}

    def _collect(self, d: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for r in ((d or {}).get("data") or []):
            props = r.get("properties", {}) or r
            items.append({
                "id": r.get("material_id") or props.get("material_id"),
                "title": props.get("formula_pretty") or props.get("material_name") or r.get("formula_pretty"),
                "abstract": None,
                "year": None,
                "authors": [],
                "doi": None,
                "source": "materials_project",
                "properties": {
                    "band_gap": props.get("band_gap"),
                    "formation_energy_per_atom": props.get("formation_energy_per_atom"),
                    "e_above_hull": props.get("e_above_hull"),
                }
            })
        return items

    def _search_with_mp_api(self, formula: Optional[str] = None, chemsys: Optional[str] = None, limit: int = 5, e_above_hull_max: Optional[float] = None, band_gap_min: Optional[float] = None) -> List[Dict[str, Any]]:
        """Fallback search using official mp-api library"""
        if not self.api_key:
            return []
        
        try:
            from app.core.real_matplotlib import ensure_real_matplotlib, get_real_pyplot

            ensure_real_matplotlib()
            get_real_pyplot()
            from mp_api.client import MPRester
            
            with MPRester(api_key=self.api_key) as mpr:
                # Simple search approach - just use formula or chemsys
                docs = []
                if formula:
                    docs = mpr.summary.search(
                        formula=formula,
                        fields=["material_id", "formula_pretty", "band_gap", "energy_above_hull", "formation_energy_per_atom"],
                        num_chunks=1,
                        chunk_size=limit
                    )
                elif chemsys:
                    docs = mpr.summary.search(
                        chemsys=chemsys,
                        fields=["material_id", "formula_pretty", "band_gap", "energy_above_hull", "formation_energy_per_atom"],
                        num_chunks=1,
                        chunk_size=limit
                    )
                
                # Convert to our format
                items: List[Dict[str, Any]] = []
                for doc in docs:
                    # Helper function to safely get attributes/keys
                    def safe_get(obj, key, default=None):
                        if hasattr(obj, key):
                            return getattr(obj, key, default)
                        elif hasattr(obj, 'get'):
                            return obj.get(key, default)
                        else:
                            return default
                    
                    items.append({
                        "id": str(safe_get(doc, "material_id", "")),
                        "title": safe_get(doc, "formula_pretty", ""),
                        "abstract": None,
                        "year": None,
                        "authors": [],
                        "doi": None,
                        "source": "materials_project",
                        "properties": {
                            "band_gap": safe_get(doc, "band_gap"),
                            "formation_energy_per_atom": safe_get(doc, "formation_energy_per_atom"),
                            "e_above_hull": safe_get(doc, "energy_above_hull"),
                        }
                    })
                
                return items[:limit]
                
        except Exception as e:
            # Log error but don't fail completely
            print(f"MP-API fallback failed: {e}")
            return []

    def search(self, formula: str, limit: int = 5, e_above_hull_max: Optional[float] = None, band_gap_min: Optional[float] = None) -> Dict[str, Any]:
        if not self.api_key or not str(self.api_key).strip():
            return {"success": False, "error": "MATERIALS_PROJECT_API_KEY not set"}
        fields = ["material_id", "formula_pretty", "band_gap", "e_above_hull", "formation_energy_per_atom"]
        # MP v2 Summary expects 'criteria' and uses page/page_size for pagination
        base_variant: Dict[str, Any] = {"page_size": limit, "page": 1}
        variants: List[Dict[str, Any]] = [
            {**base_variant, "criteria": {"formula_pretty": formula}, "properties": fields},
            {**base_variant, "criteria": {"formula": formula}, "properties": fields},
            {**base_variant, "criteria": {"formula_pretty": formula}, "fields": fields},
            {**base_variant, "criteria": {"formula": formula}, "fields": fields},
            # very old shape fallback
            {**base_variant, "formula": formula, "fields": fields},
        ]
        items: List[Dict[str, Any]] = []
        post1: Dict[str, Any] = {}
        post2: Dict[str, Any] = {}  # Initialize post2
        if e_above_hull_max is not None or band_gap_min is not None:
            for v in variants:
                filt: Dict[str, Any] = {}
                if e_above_hull_max is not None:
                    filt["e_above_hull"] = {"$lte": float(e_above_hull_max)}
                if band_gap_min is not None:
                    filt["band_gap"] = {"$gte": float(band_gap_min)}
                if filt:
                    # accept both keys
                    if "filter" in v or True:
                        v["filter"] = filt
        # try post variants until we get items
        for v in variants:
            post_try = self._post_mp(v)
            data = post_try.get("data")
            cand = self._collect(data)
            post1 = post_try
            if cand:
                items = cand
                break
        
        # If no items from POST variants, try mp-api fallback immediately
        if not items:
            mp_items = self._search_with_mp_api(formula=formula, limit=limit, e_above_hull_max=e_above_hull_max, band_gap_min=band_gap_min)
            if mp_items:
                return {"success": True, "results": mp_items, "raw": {"mp_api_fallback": True}}
            # Continue with other HTTP attempts if mp-api also fails
        if not items and formula:
            import re
            # small GET attempt against formula_pretty with fields/properties
            data_g1 = self._get_mp({
                "formula_pretty": formula,
                "page_size": limit,
                "page": 1,
                "fields": ",".join(fields)
            }).get("data")
            items = self._collect(data_g1)
            if not items:
                data_g1b = self._get_mp({
                    "formula_pretty": formula,
                    "page_size": limit,
                    "page": 1,
                    "properties": ",".join(fields)
                }).get("data")
                items = self._collect(data_g1b)
            # derive chemsys for broader search
            elems = re.findall(r"[A-Z][a-z]?", formula)
            chemsys = "-".join(sorted(set(elems))) if elems else None
            if chemsys:
                base2 = {"page_size": limit, "page": 1}
                variants2: List[Dict[str, Any]] = [
                    {**base2, "criteria": {"chemsys": chemsys}, "properties": fields},
                    {**base2, "criteria": {"chemsys": chemsys}, "fields": fields},
                ]
                if e_above_hull_max is not None or band_gap_min is not None:
                    for v2 in variants2:
                        filt2: Dict[str, Any] = {}
                        if e_above_hull_max is not None:
                            filt2["e_above_hull"] = {"$lte": float(e_above_hull_max)}
                        if band_gap_min is not None:
                            filt2["band_gap"] = {"$gte": float(band_gap_min)}
                        if filt2:
                            v2["filter"] = filt2
                post2 = {}
                for v2 in variants2:
                    post2_try = self._post_mp(v2)
                    data2_t = post2_try.get("data")
                    cand2 = self._collect(data2_t)
                    post2 = post2_try
                    if cand2:
                        items = cand2
                        break
                # no need to force data2 parse if we already have items

                # Intento GET con page_size/page probando 'fields' y 'properties'
                if not items:
                    get_params1 = {
                        "formula_pretty": formula,
                        "page_size": limit,
                        "page": 1,
                    }
                    gp = dict(get_params1)
                    gp["fields"] = ",".join(fields)
                    data_g1 = self._get_mp(gp).get("data")
                    items = self._collect(data_g1)
                    if not items:
                        gp2 = {
                            "chemsys": chemsys,
                            "page_size": limit,
                            "page": 1,
                        }
                        gp2a = dict(gp2)
                        gp2a["fields"] = ",".join(fields)
                        data_g2 = self._get_mp(gp2a).get("data")
                        items = self._collect(data_g2)
                        if not items:
                            gp2b = dict(gp2)
                            gp2b["properties"] = ",".join(fields)
                            data_g2b = self._get_mp(gp2b).get("data")
                            items = self._collect(data_g2b)
                return {"success": True, "results": items, "raw": {"post_formula": post1, "post_chemsys": post2}}

        # Final fallback: try mp-api if no items found
        if not items:
            print(f"Materials Project: No results from HTTP endpoints, trying mp-api fallback for formula '{formula}'")
            mp_items = self._search_with_mp_api(formula=formula, limit=limit, e_above_hull_max=e_above_hull_max, band_gap_min=band_gap_min)
            if mp_items:
                print(f"Materials Project: mp-api fallback returned {len(mp_items)} items")
                return {"success": True, "results": mp_items, "raw": {"mp_api_fallback": True}}
            else:
                print("Materials Project: mp-api fallback also returned no results")

        if items:
            print(f"Materials Project: HTTP endpoints returned {len(items)} items")
        else:
            print("Materials Project: No results found via any method")

        return {"success": True, "results": items, "raw": {"post_formula": post1, "post_chemsys": post2}}

    def search_by_chemsys(self, chemsys: str, limit: int = 5, e_above_hull_max: Optional[float] = None, band_gap_min: Optional[float] = None, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        if not self.api_key or not str(self.api_key).strip():
            return {"success": False, "error": "MATERIALS_PROJECT_API_KEY not set"}
        fields = fields or ["material_id", "formula_pretty", "band_gap", "e_above_hull", "formation_energy_per_atom"]
        base = {"page_size": limit, "page": 1}
        variants = [
            {**base, "criteria": {"chemsys": chemsys}, "properties": fields},
            {**base, "criteria": {"chemsys": chemsys}, "fields": fields},
        ]
        if e_above_hull_max is not None or band_gap_min is not None:
            for v in variants:
                filt: Dict[str, Any] = {}
                if e_above_hull_max is not None:
                    filt["e_above_hull"] = {"$lte": float(e_above_hull_max)}
                if band_gap_min is not None:
                    filt["band_gap"] = {"$gte": float(band_gap_min)}
                if filt:
                    v["filter"] = filt
        items: List[Dict[str, Any]] = []
        post = {}
        for v in variants:
            post_try = self._post_mp(v)
            data = post_try.get("data")
            cand = self._collect(data)
            post = post_try
            if cand:
                items = cand
                break
        
        # Try mp-api fallback if no results from POST
        if not items:
            mp_items = self._search_with_mp_api(chemsys=chemsys, limit=limit, e_above_hull_max=e_above_hull_max, band_gap_min=band_gap_min)
            if mp_items:
                return {"success": True, "results": mp_items, "raw": {"mp_api_fallback": True}}
        
        return {"success": True, "results": items, "raw": post}


# Chemistry
class ChemblClient(HttpClient):
    BASE = "https://www.ebi.ac.uk/chembl/api/data/molecule.json"
    def search(self, query: str, limit: int = 5) -> Dict[str, Any]:
        params = {"pref_name__icontains": query, "limit": limit}
        data = self.get(self.BASE, params)
        molecules = ((data or {}).get("molecules") or [])
        if not molecules:
            alt_params = {"molecule_synonyms__synonyms__icontains": query, "limit": limit}
            data_alt = self.get(self.BASE, alt_params)
            molecules = ((data_alt or {}).get("molecules") or [])
            raw = {"primary": data, "fallback": data_alt}
        else:
            raw = data
        results = []
        for m in molecules:
            results.append({
                "id": m.get("molecule_chembl_id"),
                "title": m.get("pref_name") or m.get("molecule_chembl_id"),
                "abstract": None,
                "year": None,
                "authors": [],
                "doi": None,
                "source": "chembl",
                "properties": {"max_phase": m.get("max_phase")}
            })
        return {"success": True, "results": results, "raw": raw}


# Proteins
class UniProtClient(HttpClient):
    BASE = "https://rest.uniprot.org/uniprotkb/search"
    def search(self, query: str, size: int = 10) -> Dict[str, Any]:
        params = {
            "query": query,
            "format": "json",
            "size": size,
            "fields": "accession,id,protein_name,organism_name,length,reviewed"
        }
        data = self.get(self.BASE, params)
        results = []
        for r in ((data or {}).get("results") or []):
            acc = r.get("primaryAccession") or r.get("accession") or r.get("uniProtkbId")
            name = None
            pd = r.get("proteinDescription") or {}
            if pd:
                rec = (pd.get("recommendedName") or {}).get("fullName") or {}
                name = rec.get("value") if isinstance(rec, dict) else rec
            if not name:
                name = r.get("uniProtkbId")
            org = (r.get("organism") or {}).get("scientificName") or r.get("organismName")
            results.append({
                "id": acc,
                "title": name,
                "organism": org,
                "length": (r.get("sequence") or {}).get("length") or r.get("length"),
                "reviewed": r.get("reviewed"),
                "source": "uniprot"
            })
        return {"success": True, "results": results, "raw": data}

class AlphaFoldClient(HttpClient):
    BASE = "https://alphafold.ebi.ac.uk/api/prediction/"
    def get_prediction(self, accession: str) -> Dict[str, Any]:
        data = self.get(self.BASE + accession)
        entries = data if isinstance(data, list) else (data or {}).get("results") or []
        results = []
        for e in entries:
            if isinstance(e, dict):
                results.append({
                    "id": e.get("uniprotAccession") or accession,
                    "title": e.get("uniprotId") or accession,
                    "organism": e.get("organismScientificName"),
                    "model_url": e.get("cifUrl") or e.get("pdbUrl") or e.get("url"),
                    "source": "alphafold",
                    "raw": e,
                })
        return {"success": True, "results": results, "raw": data}


class OpenTargetsClient(HttpClient):
    BASE = "https://api.platform.opentargets.org/api/v4/graphql"

    def search(self, query_text: str, k: int = 5) -> Dict[str, Any]:
        q = """
        query Search($queryString: String!) {
          search(queryString: $queryString) {
            hits {
              id
              name
              entity
              description
            }
          }
        }
        """
        try:
            resp = self.post(self.BASE, json_body={"query": q, "variables": {"queryString": query_text}})
            if not resp or "error" in resp:
                return {"success": False, "error": resp.get("error") if resp else "unknown", "results": []}
            
            data = resp.get("data", {}).get("search", {}).get("hits", [])
            results = []
            for item in data[:k]:
                results.append({
                    "id": item.get("id"),
                    "title": item.get("name"),
                    "type": item.get("entity"),
                    "description": item.get("description"),
                    "source": "open_targets"
                })
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def get_associated_diseases(self, ensembl_id: str, k: int = 5) -> Dict[str, Any]:
        q = """
        query TargetDiseases($ensemblId: String!) {
          target(ensemblId: $ensemblId) {
            associatedDiseases {
              rows {
                disease {
                  id
                  name
                }
                score
              }
            }
          }
        }
        """
        try:
            resp = self.post(self.BASE, json_body={"query": q, "variables": {"ensemblId": ensembl_id}})
            if not resp or "error" in resp:
                return {"success": False, "error": resp.get("error") if resp else "unknown", "results": []}

            rows = resp.get("data", {}).get("target", {}).get("associatedDiseases", {}).get("rows", [])
            results = []
            for row in rows[:k]:
                d = row.get("disease", {})
                results.append({
                    "id": d.get("id"),
                    "title": d.get("name"),
                    "score": row.get("score"),
                    "source": "open_targets"
                })
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}


class GwasCatalogClient(HttpClient):
    BASE = "https://www.ebi.ac.uk/gwas/rest/api"

    def search_studies(self, query: str, k: int = 5) -> Dict[str, Any]:
        # Basic search using the studies endpoint
        # Ideally we would use the search endpoints but they are HATEOAS driven
        try:
            # Fallback to listing studies if query is empty, or try to filter?
            # The API doesn't seem to support simple q= param on /studies.
            # But let's try to just get recent studies as a proxy for "search" if query is generic,
            # or if query is specific, we might need to use the /search/findBy... endpoints.
            # For now, we'll just fetch studies and filter client side if needed, or just return top K.
            # A real implementation would need to traverse the HATEOAS links.
            res = self.get(f"{self.BASE}/studies", params={"size": k})
            if not res or "error" in res:
                 return {"success": False, "error": res.get("error") if res else "unknown", "results": []}

            embedded = res.get("_embedded", {}).get("studies", [])
            results = []
            for s in embedded:
                results.append({
                    "id": s.get("accessionId"),
                    "title": s.get("title") or (s.get("publicationInfo") or {}).get("title"),
                    "trait": (s.get("diseaseTrait") or {}).get("trait"),
                    "source": "gwas_catalog",
                    "raw": s
                })
            return {"success": True, "results": results}
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}


# Facade
class LiteratureFacade:
    def __init__(self):
        self.openalex = OpenAlexClient()
        self.europepmc = EuropePMCClient()
        self.semsch = SemanticScholarClient()
        self.crossref = CrossrefClient()
        self.pubmed = PubMedClient()
        self.arxiv = ArxivClient()
        self.patents = PatentsViewClient()
        self.materials = MaterialsProjectClient()
        self.chembl = ChemblClient()
        self.uniprot = UniProtClient()
        self.alphafold = AlphaFoldClient()
        self.clinicaltrials = ClinicalTrialsClient()
        self.rcsb_pdb = RcsbPdbClient()
        self.exoplanets = NasaExoplanetArchiveClient()
        self.opentargets = OpenTargetsClient()
        self.gwas = GwasCatalogClient()

    def unified_search(self, query: str, k: int = 10) -> Dict[str, Any]:
        agg: List[Dict[str, Any]] = []
        for fn in [
            self.openalex.search,
            self.europepmc.search,
            self.semsch.search,
            self.crossref.search,
            self.pubmed.search,
            self.arxiv.search,
        ]:
            try:
                if fn is self.pubmed.search:
                    res = fn(query, retmax=k)  # type: ignore
                elif fn is self.europepmc.search:
                    res = fn(query, page_size=k)  # type: ignore
                else:
                    res = fn(query, k)  # type: ignore
                agg.extend(res.get("results", []))
            except Exception:
                continue
        seen = set()
        dedup: List[Dict[str, Any]] = []
        for p in agg:
            key = (p.get("doi") or p.get("title") or p.get("id"))
            if key and key not in seen:
                seen.add(key)
                dedup.append(p)
        return {"success": True, "results": dedup[:k]}

    # Domain-specific helpers
    def search_patents(self, query: str, k: int = 5) -> Dict[str, Any]:
        try:
            return self.patents.search(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_materials(self, formula: str, k: int = 5, e_above_hull_max: Optional[float] = None, band_gap_min: Optional[float] = None) -> Dict[str, Any]:
        try:
            return self.materials.search(formula, k, e_above_hull_max, band_gap_min)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_materials_by_chemsys(self, chemsys: str, k: int = 5, e_above_hull_max: Optional[float] = None, band_gap_min: Optional[float] = None, fields: Optional[List[str]] = None) -> Dict[str, Any]:
        try:
            return self.materials.search_by_chemsys(chemsys, k, e_above_hull_max, band_gap_min, fields)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_chembl(self, query: str, k: int = 5) -> Dict[str, Any]:
        try:
            return self.chembl.search(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_proteins(self, query: str, k: int = 10) -> Dict[str, Any]:
        try:
            return self.uniprot.search(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def get_alphafold(self, accession: str) -> Dict[str, Any]:
        try:
            return self.alphafold.get_prediction(accession)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_clinical_trials(self, query: str, k: int = 5) -> Dict[str, Any]:
        try:
            return self.clinicaltrials.search(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_pdb(self, query: str, k: int = 5) -> Dict[str, Any]:
        try:
            return self.rcsb_pdb.search(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_exoplanets(self, query: str, k: int = 5) -> Dict[str, Any]:
        try:
            return self.exoplanets.search(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_open_targets(self, query: str, k: int = 5) -> Dict[str, Any]:
        try:
            return self.opentargets.search(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}

    def search_gwas(self, query: str, k: int = 5) -> Dict[str, Any]:
        try:
            return self.gwas.search_studies(query, k)
        except Exception as e:
            return {"success": False, "error": str(e), "results": []}
