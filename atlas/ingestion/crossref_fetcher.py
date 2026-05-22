from __future__ import annotations
import time
from typing import Any, Dict, List, Optional
import requests
from .base_fetcher import BaseFetcher, FetchBatch
from .utils import normalize_text, canonical_id, write_cache, log_event

CROSSREF_ENDPOINT = "https://api.crossref.org/works"
USER_AGENT = "atlas-plausibility/0.1 (mailto:example@example.com)"

class CrossrefFetcher(BaseFetcher):
    source_name = "crossref"

    def __init__(self, rows: int = 200, polite_delay: float = 1.0):
        self.rows = min(rows, 1000)  # Crossref permite hasta 1000
        self.delay = polite_delay

    def fetch_batch(self, state: Optional[Dict[str, Any]] = None) -> FetchBatch:
        cursor = state.get("cursor") if state else "*"
        params = {
            "rows": self.rows,
            "cursor": cursor,
            "select": "DOI,title,issued,abstract,reference-count,author",
            "filter": "has-abstract:true"
        }
        headers = {"User-Agent": USER_AGENT}
        attempt = 0
        while True:
            t0 = time.time()
            r = requests.get(CROSSREF_ENDPOINT, params=params, headers=headers, timeout=60)
            elapsed = time.time() - t0
            if r.status_code == 200:
                break
            attempt += 1
            if attempt >= 4:
                log_event(self.source_name, "error", status=r.status_code, cursor=cursor, attempts=attempt)
                return FetchBatch([], None, 0)
            backoff = 2 ** (attempt - 1)
            log_event(self.source_name, "retry", status=r.status_code, attempt=attempt, backoff=backoff)
            time.sleep(backoff)
        data = r.json()
        cursor_tag = cursor if cursor and cursor != '*' else 'start'
        write_cache(self.source_name, f"cursor_{cursor_tag}", data)
        items = data.get("message", {}).get("items", [])
        normalized: List[Dict[str, Any]] = []
        for it in items:
            title_list = it.get("title") or []
            title = normalize_text(title_list[0]) if title_list else ""
            abstract_raw = it.get("abstract") or ""
            abstract = abstract_raw.replace('<jats:p>', ' ').replace('</jats:p>', ' ')
            abstract = normalize_text(abstract)
            issued = it.get("issued", {}).get("date-parts", [[]])
            year = issued[0][0] if issued and issued[0] else None
            doi = it.get("DOI")
            if not title or not abstract or len(abstract) < 50:
                continue
            normalized.append({
                "paper_id": doi or canonical_id(title, year),
                "title": title,
                "abstract": abstract,
                "year": year,
                "source": self.source_name,
                "raw_source": "crossref_api",
                "reference_count": it.get("reference-count"),
            })
        next_cursor = data.get("message", {}).get("next-cursor")
        time.sleep(self.delay)
        log_event(self.source_name, "batch", fetched=len(items), kept=len(normalized), cursor=cursor, elapsed=elapsed)
        next_state = {"cursor": next_cursor} if next_cursor else None
        return FetchBatch(normalized, next_state, len(items))
