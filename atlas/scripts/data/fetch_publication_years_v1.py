"""Fetch publication years for candidate records using external APIs.

Strategy:
1. Read `data/plausibility_training_v4_candidates.jsonl`.
2. For each record (title required), query Crossref first, then fallback to Semantic Scholar.
3. Extract best candidate year with simple fuzzy similarity on title (ratio >= MIN_SIM).
4. Cache results incrementally in JSON (`data/publication_years_cache_v1.json`) so the script is resumable.
5. Write a mapping file `data/publication_years_v1.json` (paper_id -> year) and an updated enriched file
   `data/plausibility_training_v4_enriched_with_year.jsonl` merging years if available.

Environment / Rate limiting:
- Default sleep between requests: 0.3s (configurable via --sleep)
- Limit number of records processed via --limit for testing.

Requires: requests, rapidfuzz (optional; falls back to simple normalization if absent).
If rapidfuzz not installed, installs a lightweight internal similarity (Jaccard of tokens).

Usage (after activating venv):
  python fetch_publication_years_v1.py --limit 100 --sleep 0.4

You can safely stop and re-run; cache preserves prior lookups.
"""
from __future__ import annotations
import json
import time
import argparse
import html
import re
from pathlib import Path
from typing import Dict, Any, Optional
import logging

try:
    import requests
except ImportError as exc:  # pragma: no cover
    raise SystemExit('Install requests first: pip install requests') from exc

try:
    from rapidfuzz import fuzz  # type: ignore
except ImportError:  # pragma: no cover
    fuzz = None  # type: ignore

def similarity(a: str, b: str) -> float:
    if fuzz is not None:  # pragma: no cover - simple pass-through
        return fuzz.token_set_ratio(a, b) / 100.0
    tokens_a = set(re.findall(r'[a-z0-9]+', a.lower()))
    tokens_b = set(re.findall(r'[a-z0-9]+', b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / len(tokens_a | tokens_b)

IN_CANDIDATES = Path('data/plausibility_training_v4_candidates.jsonl')
IN_ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')  # optional merge source
OUT_MAP = Path('data/publication_years_v1.json')
OUT_CACHE = Path('data/publication_years_cache_v1.json')
OUT_ENRICHED_MERGED = Path('data/plausibility_training_v4_enriched_with_year.jsonl')

CROSSREF_ENDPOINT = "https://api.crossref.org/works"
SEMANTIC_SCHOLAR_ENDPOINT = "https://api.semanticscholar.org/graph/v1/paper/search"

MIN_SIM = 0.82  # Accept candidate only if similarity >= MIN_SIM
TIMEOUT = 15

log = logging.getLogger("year_fetch")
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def load_jsonl(path: Path) -> list[Dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8').splitlines()
    return [json.loads(line) for line in lines if line.strip()]

def save_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')

def load_cache() -> Dict[str, Any]:
    if not OUT_CACHE.exists():
        return {}
    try:
        return json.loads(OUT_CACHE.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):  # pragma: no cover
        return {}

def save_cache(cache: Dict[str, Any]):
    OUT_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')

def query_crossref(title: str) -> Optional[Dict[str, Any]]:
    params = {
        'query.title': title,
        'rows': 1,
        'select': 'title,created,issued,published-print,published-online'
    }
    try:
        resp = requests.get(CROSSREF_ENDPOINT, params=params, timeout=TIMEOUT)
        if resp.status_code != 200:
            return None
        data = resp.json()
        items = data.get('message', {}).get('items', [])
        return items[0] if items else None
    except (requests.RequestException, ValueError):  # pragma: no cover
        return None

def extract_year_crossref(item: Dict[str, Any]) -> Optional[int]:
    for key in ('published-print', 'published-online', 'issued', 'created'):
        obj = item.get(key)
        if isinstance(obj, dict):
            dp = obj.get('date-parts') or obj.get('date_parts')
            if isinstance(dp, list) and dp and isinstance(dp[0], list) and dp[0]:
                y = dp[0][0]
                if isinstance(y, int) and 1900 <= y <= 2100:
                    return y
    return None

def query_semantic_scholar(title: str) -> Optional[Dict[str, Any]]:
    # Use paper/search endpoint (Graph API v1) limited fields
    params = {
        'query': title,
        'limit': 1,
        'fields': 'title,year'
    }
    try:
        resp = requests.get(SEMANTIC_SCHOLAR_ENDPOINT, params=params, timeout=TIMEOUT)
        if resp.status_code != 200:
            return None
        data = resp.json()
        papers = data.get('data') or []
        return papers[0] if papers else None
    except (requests.RequestException, ValueError):  # pragma: no cover
        return None

def clean_text(s: str) -> str:
    s = html.unescape(s or '')
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def resolve_year(title: str) -> Optional[int]:
    base = clean_text(title)
    cr_item = query_crossref(title)
    if cr_item:
        cr_title_list = cr_item.get('title') or []
        cr_title = cr_title_list[0] if cr_title_list else ''
        if similarity(base, clean_text(cr_title)) >= MIN_SIM:
            year_val = extract_year_crossref(cr_item)
            if year_val:
                return year_val
    ss_item = query_semantic_scholar(title)
    if ss_item:
        ss_title = ss_item.get('title') or ''
        if similarity(base, clean_text(ss_title)) >= MIN_SIM:
            ss_year = ss_item.get('year')
            if isinstance(ss_year, int) and 1900 <= ss_year <= 2100:
                return ss_year
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=None, help='Procesar máximo N registros')
    ap.add_argument('--sleep', type=float, default=0.3, help='Segundos entre requests')
    ap.add_argument('--force', action='store_true', help='Forzar re-fetch incluso si está en cache')
    args = ap.parse_args()

    rows = load_jsonl(IN_CANDIDATES)
    if not rows:
        log.error('No candidate data found.')
        return
    cache = load_cache()
    mapping: Dict[str, int] = {}
    processed = 0
    for r in rows:
        if args.limit and processed >= args.limit:
            break
        pid = r.get('paper_id')
        title = r.get('title') or ''
        if not pid or not title:
            continue
        if not args.force and pid in cache:
            yr = cache[pid]
            if isinstance(yr, int):
                mapping[pid] = yr
            processed += 1
            continue
        yr = resolve_year(title)
        cache[pid] = yr
        if isinstance(yr, int):
            mapping[pid] = yr
            log.info("%s -> %s", pid, yr)
        else:
            log.info("%s -> (no year)", pid)
        processed += 1
        save_cache(cache)
        time.sleep(args.sleep)

    # Persist mappings
    save_json(OUT_MAP, mapping)
    log.info("Years mapped: %d (cache size=%d) -> %s", len(mapping), len(cache), OUT_MAP)

    # Merge into enriched if exists
    enriched_rows = load_jsonl(IN_ENRICHED)
    if enriched_rows:
        for rec in enriched_rows:
            pid = rec.get('paper_id')
            if pid in mapping:
                rec['year'] = mapping[pid]
        out_lines = [json.dumps(rec, ensure_ascii=False) for rec in enriched_rows]
        OUT_ENRICHED_MERGED.write_text('\n'.join(out_lines) + '\n', encoding='utf-8')
        log.info("Merged enriched with years -> %s", OUT_ENRICHED_MERGED)
    else:
        log.warning('No enriched file to merge years into.')

if __name__ == '__main__':  # pragma: no cover
    main()
