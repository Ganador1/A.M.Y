from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
import numpy as np
import faiss

EMB_PATH = Path('data/plausibility_training_v4_embeddings.parquet')
INDEX_PATH = Path('data/faiss_index_v4.bin')
ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
OUT_CLEAN = Path('data/plausibility_training_v4_enriched_dedup.jsonl')
THRESHOLD = 0.95


def load_jsonl(p: Path):
    return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]


def write_jsonl(p: Path, rows):
    with p.open('w', encoding='utf-8') as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')


def main():
    if not EMB_PATH.exists() or not INDEX_PATH.exists() or not ENRICHED.exists():
        print('Faltan archivos necesarios.')
        return
    df_emb = pd.read_parquet(EMB_PATH)
    index = faiss.read_index(str(INDEX_PATH))
    mat = np.vstack(df_emb['embedding'].values).astype('float32')
    norms = np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12
    mat = mat / norms
    scores, idxs = index.search(mat, 5)
    to_remove = set()
    for i, (sc_row, id_row) in enumerate(zip(scores, idxs)):
        for s, j in zip(sc_row[1:], id_row[1:]):
            if j < 0:
                continue
            if s >= THRESHOLD:
                # remove higher index to keep deterministic
                to_remove.add(max(i, int(j)))
    enriched_rows = load_jsonl(ENRICHED)
    id_map = {r.get('paper_id') or r.get('doi'): r for r in enriched_rows}
    keep_ids = []
    for idx, rec in enumerate(df_emb.itertuples()):
        if idx in to_remove:
            continue
        keep_ids.append(rec.paper_id)
    cleaned = [id_map.get(pid) for pid in keep_ids if id_map.get(pid)]
    write_jsonl(OUT_CLEAN, cleaned)
    print(f'Duplicados eliminados: {len(to_remove)} -> dataset limpio {len(cleaned)} registros')

if __name__ == '__main__':
    main()
