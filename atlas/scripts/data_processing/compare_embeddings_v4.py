from __future__ import annotations
import pandas as pd
import numpy as np
from pathlib import Path
import time

TFIDF_EMB = Path('data/plausibility_training_v4_embeddings.parquet')
TRANS_EMB = Path('data/plausibility_training_v4_embeddings_transformer.parquet')
REPORT = Path('data/embedding_comparison_v4.json')

# Placeholder: si no existe TRANS_EMB, reporta solo TF-IDF

def stat(vecs):
    arr = np.vstack(vecs)
    return {
        'dim': int(arr.shape[1]),
        'mean_norm': float(np.linalg.norm(arr, axis=1).mean()),
        'var_norm': float(np.var(np.linalg.norm(arr, axis=1)))
    }


def main():
    import json
    report = {'timestamp': time.time()}
    if TFIDF_EMB.exists():
        df_tfidf = pd.read_parquet(TFIDF_EMB)
        report['tfidf'] = stat(df_tfidf['embedding'].values)
    if TRANS_EMB.exists():
        df_tr = pd.read_parquet(TRANS_EMB)
        report['transformer'] = stat(df_tr['embedding'].values)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Reporte guardado: {REPORT}')

if __name__ == '__main__':
    main()
