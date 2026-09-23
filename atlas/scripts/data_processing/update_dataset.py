from __future__ import annotations
import argparse
from pathlib import Path
from typing import Dict, Any, List, Set
import json

from ingestion.crossref_fetcher import CrossrefFetcher
from ingestion.semantic_scholar_fetcher import SemanticScholarFetcher
from ingestion.utils import load_state, save_state, log_event, canonical_id

DATA_V3 = Path("data/plausibility_training_v3.jsonl")
OUT_V4 = Path("data/plausibility_training_v4_candidates.jsonl")


def read_jsonl(p: Path) -> List[Dict[str, Any]]:
    if not p.exists():
        return []
    return [json.loads(line) for line in p.read_text(encoding='utf-8').splitlines() if line.strip()]


def write_jsonl(p: Path, rows: List[Dict[str, Any]]):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def merge_dedup(base: List[Dict[str, Any]], new: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Set[str] = set()
    out: List[Dict[str, Any]] = []
    for r in base + new:
        pid = r.get('paper_id') or canonical_id(r.get('title', ''), r.get('year'))
        if pid in seen:
            continue
        seen.add(pid)
        out.append(r)
    return out


def main(cli_args):
    state = load_state()
    cursor_state = state.get('crossref')
    fetcher = CrossrefFetcher(rows=cli_args.rows, polite_delay=cli_args.delay)
    total_new_crossref = 0
    total_new_semantic = 0
    aggregated: List[Dict[str, Any]] = []
    for _ in range(cli_args.max_batches):
        batch = fetcher.fetch_batch(cursor_state)
        if not batch.items:
            break
        aggregated.extend(batch.items)
        total_new_crossref += len(batch.items)
        cursor_state = batch.next_state
        if not cursor_state:
            break
    # Semantic Scholar (opcional)
    if cli_args.semantic_limit > 0 and cli_args.semantic_batches > 0:
        ss_state = state.get('semantic_scholar')
        ss_fetcher = SemanticScholarFetcher(query=cli_args.semantic_query, limit=cli_args.semantic_limit, polite_delay=cli_args.delay)
        for _ in range(cli_args.semantic_batches):
            ss_batch = ss_fetcher.fetch_batch(ss_state)
            if not ss_batch.items:
                break
            aggregated.extend(ss_batch.items)
            ss_state = ss_batch.next_state
            if not ss_state:
                break
            total_new_semantic += len(ss_batch.items)
        state['semantic_scholar'] = ss_state

    base = read_jsonl(DATA_V3)
    merged = merge_dedup(base, aggregated)
    write_jsonl(OUT_V4, merged)
    state['crossref'] = cursor_state
    save_state(state)
    newly_added_effective = len(merged) - len(base)
    log_event('update_dataset', 'summary', new_crossref=total_new_crossref, new_semantic=total_new_semantic, effective_added=newly_added_effective, merged=len(merged), base=len(base))
    print(f"Nuevos registros (crudos) Crossref: {total_new_crossref} | SemanticScholar: {total_new_semantic}")
    print(f"Nuevos registros añadidos tras deduplicar: {newly_added_effective}")
    print(f"Total tras merge: {len(merged)} (base {len(base)})")
    if cursor_state:
        print("Cursor siguiente guardado para próxima ejecución.")
    else:
        print("No hay cursor siguiente (fin de resultados o límite alcanzado).")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--rows', type=int, default=200)
    parser.add_argument('--max-batches', type=int, default=5)
    parser.add_argument('--delay', type=float, default=1.0)
    parser.add_argument('--semantic-query', type=str, default='scientific')
    parser.add_argument('--semantic-limit', type=int, default=0, help='Límite por batch Semantic Scholar (0 = desactivado)')
    parser.add_argument('--semantic-batches', type=int, default=1, help='Número de batches Semantic Scholar a solicitar (paginación)')
    args = parser.parse_args()
    main(args)
