from __future__ import annotations
"""Entrena variante del modelo de plausibilidad v4 SIN usar variables de citaciones.

Genera:
 - models/plausibility_v4_no_cits.pkl

Comparte gran parte de la lógica del script principal pero elimina:
   citation_count, influential_citation_count, influential_ratio
Mantiene resto de features estructurales.
"""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import roc_auc_score, f1_score, brier_score_loss
from sklearn.ensemble import RandomForestClassifier

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
CLUSTERS = Path('data/plausibility_training_v4_clusters.parquet')
WEAK = Path('data/plausibility_training_v4_weak_labels.parquet')
MODEL_OUT = Path('models/plausibility_v4_no_cits.pkl')

BASE_FEATURES = [
    'title_len','abstract_len','recency_years','fields_count','abstract_title_len_ratio'
]

def load_enriched_df():
    if not ENRICHED.exists():
        return pd.DataFrame([])
    rows = [json.loads(line) for line in ENRICHED.read_text(encoding='utf-8').splitlines() if line.strip()]
    return pd.DataFrame(rows)

def build_dataset():
    df_e = load_enriched_df()
    if df_e.empty:
        raise SystemExit('Enriched dataset vacío')
    if CLUSTERS.exists():
        df_c = pd.read_parquet(CLUSTERS)[['paper_id','cluster_id']]
        df_e = df_e.merge(df_c, on='paper_id', how='left')
    else:
        df_e['cluster_id'] = -1
    if WEAK.exists():
        df_w = pd.read_parquet(WEAK)
        df_e = df_e.merge(df_w, on='paper_id', how='left')
    else:
        raise SystemExit('Weak labels no encontrados')
    return df_e

def run_cv(X, y, n_splits=5, seed=42):
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    aucs, f1s = [], []
    for tr, te in skf.split(X, y):
        m = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=seed, class_weight='balanced')
        m.fit(X.iloc[tr], y.iloc[tr])
        p = m.predict_proba(X.iloc[te])[:,1]
        aucs.append(roc_auc_score(y.iloc[te], p))
        f1s.append(f1_score(y.iloc[te], (p>=0.5).astype(int)))
    return {'auc_mean': float(np.mean(aucs)), 'auc_std': float(np.std(aucs)), 'f1_mean': float(np.mean(f1s)), 'f1_std': float(np.std(f1s))}

def best_threshold(y_true, proba, grid=None):
    if grid is None:
        grid = np.linspace(0.2,0.8,61)
    best_t, best_f1 = 0.5, -1
    for t in grid:
        f1 = f1_score(y_true, (proba>=t).astype(int))
        if f1>best_f1:
            best_f1, best_t = f1, t
    return float(best_t), float(best_f1)

def expected_calibration_error(y_true, proba, n_bins: int = 15):
    bins = np.linspace(0.0,1.0,n_bins+1)
    ece=0.0
    for i in range(n_bins):
        mask = (proba>=bins[i]) & (proba < (bins[i+1] if i<n_bins-1 else bins[i+1]+1e-9))
        if not np.any(mask):
            continue
        ece += (mask.sum()/len(proba))*abs(y_true[mask].mean()-proba[mask].mean())
    return float(ece)

def main():
    df = build_dataset()
    df['cluster_id'] = df['cluster_id'].fillna(-1)
    X_num = df[BASE_FEATURES].fillna(0)
    if df['cluster_id'].nunique() < 200:
        X_cluster = pd.get_dummies(df['cluster_id'].astype(int), prefix='cl')
        X = pd.concat([X_num, X_cluster], axis=1)
    else:
        X = X_num
    y = df['weak_label'].fillna(0).astype(int)
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,stratify=y,random_state=42)
    clf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=42, class_weight='balanced')
    clf.fit(X_train,y_train)
    proba = clf.predict_proba(X_test)[:,1]
    thr_opt,f1_opt = best_threshold(y_test, proba)
    auc = roc_auc_score(y_test, proba)
    f1 = f1_score(y_test, (proba>=0.5).astype(int))
    brier = brier_score_loss(y_test, proba)
    ece = expected_calibration_error(y_test.values, proba)
    cv = run_cv(X,y)
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({
        'model': clf,
        'feature_columns': list(X.columns),
        'auc': auc,
        'f1': f1,
        'f1_opt': f1_opt,
        'threshold_opt': thr_opt,
        'brier': brier,
        'ece': ece,
        'cv': cv,
        'citation_features_removed': ['citation_count','influential_citation_count','influential_ratio']
    }, MODEL_OUT)
    print(f"NO-CITS modelo guardado: {MODEL_OUT} AUC={auc:.4f} F1={f1:.4f} F1_opt={f1_opt:.4f}@thr={thr_opt:.2f} Brier={brier:.4f} ECE={ece:.4f} | CV AUC={cv['auc_mean']:.4f}±{cv['auc_std']:.4f}")

if __name__ == '__main__':
    main()
