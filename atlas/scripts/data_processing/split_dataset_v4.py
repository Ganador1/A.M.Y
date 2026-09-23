from __future__ import annotations
import json, random
from pathlib import Path
from typing import List, Dict, Any
import hashlib

CANDIDATES = Path('data/plausibility_training_v4_enriched.jsonl')
SPLIT_DIR = Path('data/splits_v4')
RATIOS = (0.7, 0.15, 0.15)
SEED = 42


def load_rows() -> List[Dict[str, Any]]:
    if not CANDIDATES.exists():
        return []
    out = []
    for line in CANDIDATES.read_text(encoding='utf-8').splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def stable_key(title: str, year) -> int:
    base = (title or '') + str(year or '')
    h = hashlib.md5(base.encode('utf-8')).hexdigest()
    return int(h[:8], 16)


def main():
    rows = load_rows()
    if not rows:
        print('No hay datos para partir.')
        return
    random.seed(SEED)
    # Orden estable por hash para reproducibilidad sin sesgo por orden de archivo
    rows_sorted = sorted(rows, key=lambda r: stable_key(r.get('title',''), r.get('year')))
    n = len(rows_sorted)
    n_train = int(n * RATIOS[0])
    n_val = int(n * RATIOS[1])
    train = rows_sorted[:n_train]
    val = rows_sorted[n_train:n_train+n_val]
    holdout = rows_sorted[n_train+n_val:]
    SPLIT_DIR.mkdir(parents=True, exist_ok=True)
    def write(name: str, subset: List[Dict[str, Any]]):
        p = SPLIT_DIR / f'{name}.jsonl'
        with p.open('w', encoding='utf-8') as f:
            for r in subset:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    write('train', train)
    write('val', val)
    write('holdout', holdout)
    print(f'Splits guardados en {SPLIT_DIR} -> train={len(train)} val={len(val)} holdout={len(holdout)}')

if __name__ == '__main__':
    main()
