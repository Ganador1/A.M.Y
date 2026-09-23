from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
import requests
from .base_fetcher import BaseFetcher, FetchBatch
from .utils import normalize_text, canonical_id, write_cache, log_event

SEMANTIC_SCHOLAR_SEARCH = "https://api.semanticscholar.org/graph/v1/paper/search"
USER_AGENT = "atlas-plausibility/0.1 (mailto:example@example.com)"

# Campos disponibles: https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_v1_paper_search
FIELDS = "title,abstract,year,citationCount,influentialCitationCount,fieldsOfStudy"

class SemanticScholarFetcher(BaseFetcher):
    source_name = "semantic_scholar"

    def __init__(self, query: str = "scientific", limit: int = 100, polite_delay: float = 1.0):
        self.query = query
        self.limit = min(limit, 100)  # API search page size
        self.delay = polite_delay

    def fetch_batch(self, state: Optional[Dict[str, Any]] = None) -> FetchBatch:
        raw_offset = state.get("offset") if state else 0
        try:
            offset = int(raw_offset)
        except (TypeError, ValueError):  # fallback
            offset = 0
        params = {
            "query": self.query,
            "limit": self.limit,
            "offset": offset,
            "fields": FIELDS
        }
        headers = {"User-Agent": USER_AGENT}
        t0 = time.time()
        r = requests.get(SEMANTIC_SCHOLAR_SEARCH, params=params, headers=headers, timeout=60)
        elapsed = time.time() - t0
        if r.status_code != 200:
            log_event(self.source_name, "error", status=r.status_code, offset=offset)
            return FetchBatch([], None, 0)
        data = r.json()
        write_cache(self.source_name, f"offset_{offset}", data)
        items = data.get("data", [])
        normalized: List[Dict[str, Any]] = []
        for it in items:
            title = normalize_text(it.get("title") or "")
            abstract = normalize_text(it.get("abstract") or "")
            if not title or not abstract or len(abstract) < 50:
                continue
            year = it.get("year")
            paper_id = it.get("paperId") or canonical_id(title, year)
            normalized.append({
                "paper_id": paper_id,
                "title": title,
                "abstract": abstract,
                "year": year,
                "source": self.source_name,
                "raw_source": "semantic_scholar_api",
                "citation_count": it.get("citationCount"),
                "influential_citation_count": it.get("influentialCitationCount"),
                "fields_of_study": it.get("fieldsOfStudy"),
            })
        next_offset = (offset + self.limit) if items else None
        time.sleep(self.delay)
        log_event(self.source_name, "batch", fetched=len(items), kept=len(normalized), offset=offset, elapsed=elapsed)
        next_state = {"offset": next_offset} if next_offset is not None else None
        return FetchBatch(normalized, next_state, len(items))
