from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, brier_score_loss
from sklearn.model_selection import train_test_split

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
WEAK_MAIN = Path('data/plausibility_training_v4_weak_labels.parquet')
WEAK_ALT = Path('data/plausibility_training_v4_weak_labels_alt.parquet')
CLUSTERS = Path('data/plausibility_training_v4_clusters.parquet')
OUT = Path('models/plausibility_v4_logreg.pkl')

FEATURE_COLS = [
    'title_len','abstract_len','citation_count','influential_citation_count',
    'influential_ratio','recency_years','fields_count','abstract_title_len_ratio'
]

def load_enriched():
    if not ENRICHED.exists():
        return pd.DataFrame([])
    rows = [json.loads(l) for l in ENRICHED.read_text(encoding='utf-8').splitlines() if l.strip()]
    return pd.DataFrame(rows)


def main():
    df = load_enriched()
    if df.empty:
        print('No enriched data.')
        return
    # Merge clusters
    if CLUSTERS.exists():
        df = df.merge(pd.read_parquet(CLUSTERS)[['paper_id','cluster_id']], on='paper_id', how='left')
    else:
        df['cluster_id'] = -1
    # Base weak labels
    if not WEAK_MAIN.exists():
        print('No weak labels base.')
        return
    df = df.merge(pd.read_parquet(WEAK_MAIN)[['paper_id','weak_label']], on='paper_id', how='left')
    # Alt weak labels (if available)
    alt_cols = []
    if WEAK_ALT.exists():
        alt_df = pd.read_parquet(WEAK_ALT)
        alt_cols = [c for c in alt_df.columns if c.startswith('weak_label_alt_')]
        df = df.merge(alt_df[['paper_id'] + alt_cols], on='paper_id', how='left')
    # Prepare features
    X_num = df[FEATURE_COLS].fillna(0)
    if df['cluster_id'].nunique() < 150:
        X_cl = pd.get_dummies(df['cluster_id'].fillna(-1).astype(int), prefix='cl')
        X = pd.concat([X_num, X_cl], axis=1)
    else:
        X = X_num
    y = df['weak_label'].fillna(0).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
    logreg = LogisticRegression(max_iter=2000, C=0.5, penalty='l2', class_weight='balanced', solver='lbfgs', n_jobs=-1)
    logreg.fit(X_train, y_train)
    proba = logreg.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, proba)
    # Threshold tuning simple
    best_thr, best_f1 = 0.5, -1
    for t in np.linspace(0.2,0.8,61):
        preds = (proba>=t).astype(int)
        f1 = f1_score(y_test, preds)
        if f1 > best_f1:
            best_f1 = f1
            best_thr = t
    brier = brier_score_loss(y_test, proba)
    import joblib
    OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'model': logreg, 'auc': auc, 'f1_opt': best_f1, 'thr_opt': best_thr, 'brier': brier, 'feature_columns': list(X.columns), 'alt_labels': alt_cols}, OUT)
    print(f'LogReg guardado {OUT} AUC={auc:.4f} F1_opt={best_f1:.4f}@{best_thr:.2f} Brier={brier:.4f}')

if __name__ == '__main__':
    main()
