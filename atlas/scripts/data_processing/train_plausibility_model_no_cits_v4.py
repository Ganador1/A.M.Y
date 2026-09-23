from __future__ import annotations
from pathlib import Path
import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.ensemble import RandomForestClassifier

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
CLUSTERS = Path('data/plausibility_training_v4_clusters.parquet')
WEAK = Path('data/plausibility_training_v4_weak_labels.parquet')
OUT = Path('models/plausibility_v4_rf_no_cits.pkl')

FEATURE_COLS_BASE = [
    'title_len','abstract_len',
    # 'citation_count','influential_citation_count',  # excluidas para evaluar leakage
    'influential_ratio',  # se mantiene para ver impacto residual
    'recency_years','fields_count','abstract_title_len_ratio'
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
    if not WEAK.exists():
        print('No weak labels.')
        return
    df = df.merge(pd.read_parquet(WEAK)[['paper_id','weak_label']], on='paper_id', how='left')
    X_num = df[FEATURE_COLS_BASE].fillna(0)
    if df['cluster_id'].nunique() < 150:
        X = pd.concat([X_num, pd.get_dummies(df['cluster_id'].fillna(-1).astype(int), prefix='cl')], axis=1)
    else:
        X = X_num
    y = df['weak_label'].fillna(0).astype(int)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    rf = RandomForestClassifier(n_estimators=300, max_depth=None, n_jobs=-1, random_state=42, class_weight='balanced')
    rf.fit(X_train, y_train)
    proba = rf.predict_proba(X_test)[:,1]
    auc = roc_auc_score(y_test, proba)
    f1 = f1_score(y_test, (proba>=0.5).astype(int))
    import joblib
    OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({'model': rf, 'auc': auc, 'f1': f1, 'feature_columns': list(X.columns)}, OUT)
    print(f'RF sin citas guardado {OUT} AUC={auc:.4f} F1={f1:.4f}')

if __name__ == '__main__':
    main()
