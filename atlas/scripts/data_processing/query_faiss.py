from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import faiss

EMB_PATH = Path('data/plausibility_training_v4_embeddings.parquet')
INDEX_PATH = Path('data/faiss_index_v4.bin')


def load_embeddings():
    df = pd.read_parquet(EMB_PATH)
    mat = np.vstack(df['embedding'].values).astype('float32')
    norms = np.linalg.norm(mat, axis=1, keepdims=True) + 1e-12
    mat = mat / norms
    return df, mat


def load_index():
    return faiss.read_index(str(INDEX_PATH))


def search(index, query_vecs: np.ndarray, top_k: int):
    scores, idx = index.search(query_vecs, top_k)
    return scores, idx


def detect_duplicates(index, mat: np.ndarray, threshold: float = 0.92):
    # Self-similarity: buscar top 5 para cada vector y filtrar pares > threshold (excluyendo self)
    scores, idx = index.search(mat, 5)
    dup_pairs = []
    for i, (sc_row, id_row) in enumerate(zip(scores, idx)):
        for s, j in zip(sc_row[1:], id_row[1:]):  # saltar self en posición 0
            if j < 0:
                continue
            if s >= threshold:
                a, b = sorted((i, int(j)))
                dup_pairs.append((a, b, float(s)))
    # dedup pares repetidos
    seen = set()
    unique = []
    for a, b, s in dup_pairs:
        if (a, b) in seen:
            continue
        seen.add((a, b))
        unique.append({'i': a, 'j': b, 'score': s})
    return unique


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--query-text', type=str, default=None, help='Texto crudo para vectorizar (requiere TF-IDF guardado si embeddings TF-IDF).')
    ap.add_argument('--paper-id', type=str, default=None, help='Buscar similares a un paper_id existente.')
    ap.add_argument('--top-k', type=int, default=5)
    ap.add_argument('--show-json', action='store_true')
    ap.add_argument('--duplicates', action='store_true', help='Detectar duplicados por umbral.')
    ap.add_argument('--dup-threshold', type=float, default=0.92)
    args = ap.parse_args()

    df, mat = load_embeddings()
    index = load_index()

    results = {}

    if args.duplicates:
        dups = detect_duplicates(index, mat, args.dup_threshold)
        results['duplicates'] = dups

    if args.paper_id:
        row = df[df.paper_id == args.paper_id]
        if row.empty:
            print('paper_id no encontrado')
        else:
            vec = np.array([row.iloc[0].embedding], dtype='float32')
            vec /= (np.linalg.norm(vec, axis=1, keepdims=True) + 1e-12)
            scores, idxs = search(index, vec, args.top_k)
            items = []
            for s, j in zip(scores[0], idxs[0]):
                if j < 0:
                    continue
                rec = df.iloc[int(j)]
                items.append({'paper_id': rec.paper_id, 'score': float(s)})
            results['similar_to_paper_id'] = items

    if args.query_text:
        # Intentar cargar TF-IDF para vectorizar
        try:
            import joblib
            from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: F401
            tfidf = joblib.load('data/tfidf_v4.pkl')
            qv = tfidf.transform([args.query_text]).toarray().astype('float32')
            qv /= (np.linalg.norm(qv, axis=1, keepdims=True) + 1e-12)
            scores, idxs = search(index, qv, args.top_k)
            q_items = []
            for s, j in zip(scores[0], idxs[0]):
                if j < 0:
                    continue
                rec = df.iloc[int(j)]
                q_items.append({'paper_id': rec.paper_id, 'score': float(s)})
            results['query_text'] = q_items
        except Exception as e:  # pragma: no cover
            results['query_text_error'] = str(e)

    if args.show_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        if 'duplicates' in results:
            print(f"Duplicados detectados: {len(results['duplicates'])}")
        if 'similar_to_paper_id' in results:
            print('Similares a paper_id:')
            for r in results['similar_to_paper_id']:
                print(r)
        if 'query_text' in results:
            print('Resultados query_text:')
            for r in results['query_text']:
                print(r)


if __name__ == '__main__':
    main()
