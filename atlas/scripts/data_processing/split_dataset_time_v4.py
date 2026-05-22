from __future__ import annotations
from pathlib import Path
import json
import pandas as pd

ENRICHED_PRIMARY = Path('data/plausibility_training_v4_enriched_with_year.jsonl')
ENRICHED_FALLBACK = Path('data/plausibility_training_v4_enriched.jsonl')
OUT_DIR = Path('data/time_splits_v4')
RATIOS = (0.6, 0.2, 0.2)  # train, val, test


def pick_enriched_path() -> Path | None:
    if ENRICHED_PRIMARY.exists():
        return ENRICHED_PRIMARY
    if ENRICHED_FALLBACK.exists():
        return ENRICHED_FALLBACK
    return None

def load_enriched(path: Path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def main():
    enriched_path = pick_enriched_path()
    if enriched_path is None:
        print('No enriched file encontrado.')
        return
    rows = load_enriched(enriched_path)
    if not rows:
        print('Archivo enriched vacío.')
        return
    df = pd.DataFrame(rows)
    if 'year' not in df.columns:
        print('No year column encontrada en dataset (intenta primero fetch_publication_years_v1).')
        return
    df = df[df['year'].notna()].copy()
    coverage = len(df) / len(rows) if rows else 0.0
    df['year'] = df['year'].astype(int)
    df = df.sort_values('year')
    n = len(df)
    n_train = int(n * RATIOS[0])
    n_val = int(n * RATIOS[1])
    train_df = df.iloc[:n_train]
    val_df = df.iloc[n_train:n_train+n_val]
    test_df = df.iloc[n_train+n_val:]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, part in [('train', train_df), ('val', val_df), ('test', test_df)]:
        out_p = OUT_DIR / f'{name}.jsonl'
        with out_p.open('w', encoding='utf-8') as f:
            for _, r in part.iterrows():
                f.write(json.dumps(r.to_dict(), ensure_ascii=False) + '\n')
    print(f'Splits temporales guardados en {OUT_DIR} (train={len(train_df)}, val={len(val_df)}, test={len(test_df)})')
    print(f'Cobertura year utilizada: {coverage:.1%} ({len(df)}/{len(rows)}) - fuente: {enriched_path.name}')

if __name__ == '__main__':
    main()
