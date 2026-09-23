from __future__ import annotations
import pandas as pd
import numpy as np
import faiss
from pathlib import Path
import json

EMB_PATH = Path('data/plausibility_training_v4_embeddings.parquet')
INDEX_PATH = Path('data/faiss_index_v4.bin')
META_PATH = Path('data/faiss_index_v4_meta.json')


def main():
    if not EMB_PATH.exists():
        print('Archivo de embeddings no encontrado.')
        return
    df = pd.read_parquet(EMB_PATH)
    if 'embedding' not in df.columns:
        print('Columna embedding no encontrada.')
        return
    vectors = np.vstack(df['embedding'].values).astype('float32')
    dim = vectors.shape[1]
    index = faiss.IndexFlatIP(dim)
    # Asegurar normalización (IP ~ coseno si norm=1)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-12
    vectors = vectors / norms
    index.add(vectors)
    faiss.write_index(index, str(INDEX_PATH))
    META_PATH.write_text(json.dumps({
        'size': int(vectors.shape[0]),
        'dim': dim,
        'metric': 'cosine_via_IP',
        'embedding_method': df.get('embedding_method', ['unknown'])[0]
    }, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Índice FAISS guardado: {INDEX_PATH} (n={vectors.shape[0]}, dim={dim})')


if __name__ == '__main__':
    main()
