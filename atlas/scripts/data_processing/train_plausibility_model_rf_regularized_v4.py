from __future__ import annotations
from pathlib import Path
import pandas as pd
import json
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
CLUSTERS = Path('data/plausibility_training_v4_clusters.parquet')
WEAK_ENSEMBLE = Path('data/plausibility_training_v4_weak_labels_ensemble.parquet')
OUT = Path('models/plausibility_v4_rf_regularized.pkl')

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
    if CLUSTERS.exists():
        df = df.merge(pd.read_parquet(CLUSTERS)[['paper_id','cluster_id']], on='paper_id', how='left')
    else:
        df['cluster_id'] = -1
    if not WEAK_ENSEMBLE.exists():
        print('No ensemble labels.')
        return
    df = df.merge(pd.read_parquet(WEAK_ENSEMBLE), on='paper_id', how='inner')
    X_num = df[FEATURE_COLS].fillna(0)
    if df['cluster_id'].nunique() < 150:
        X = pd.concat([X_num, pd.get_dummies(df['cluster_id'].fillna(-1).astype(int), prefix='cl')], axis=1)
    else:
        X = X_num
    y = df['ensemble_label'].astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, stratify=y, random_state=42)
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=6,
        min_samples_leaf=10,
        max_features='sqrt',
        class_weight='balanced_subsample',
        n_jobs=-1,
        random_state=42
    )
    rf.fit(X_train, y_train)
    proba = rf.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, proba)
    f1 = f1_score(y_test, (proba>=0.5).astype(int))
    import joblib
    OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'model': rf, 'auc': auc, 'f1': f1, 'feature_columns': list(X.columns)}, OUT)
    print(f'RF Regularizado guardado {OUT} AUC={auc:.4f} F1={f1:.4f}')

if __name__ == '__main__':
    main()
