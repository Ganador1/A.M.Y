from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import joblib

EMB_PATH = Path('data/plausibility_training_v4_embeddings.parquet')
CLUSTERS_PATH = Path('data/plausibility_training_v4_clusters.parquet')
CENTROIDS_PATH = Path('data/plausibility_training_v4_centroids.npy')
MODEL_PATH = Path('data/kmeans_v4.pkl')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--k', type=int, default=20)
    ap.add_argument('--random-state', type=int, default=42)
    args = ap.parse_args()
    if not EMB_PATH.exists():
        print('Embeddings no encontrados.')
        return
    df = pd.read_parquet(EMB_PATH)
    X = np.vstack(df['embedding'].values).astype('float32')
    km = KMeans(n_clusters=args.k, random_state=args.random_state, n_init='auto')
    labels = km.fit_predict(X)
    df_out = df.copy()
    df_out['cluster_id'] = labels
    df_out.to_parquet(CLUSTERS_PATH, index=False)
    np.save(CENTROIDS_PATH, km.cluster_centers_)
    joblib.dump(km, MODEL_PATH)
    print(f'Clustering completado: k={args.k} -> {CLUSTERS_PATH}')


if __name__ == '__main__':
    main()
