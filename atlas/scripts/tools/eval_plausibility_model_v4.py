from __future__ import annotations
from pathlib import Path
import json
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.calibration import calibration_curve
import matplotlib.pyplot as plt

MODEL_PATH = Path('models/plausibility_v4_rf.pkl')
WEAK = Path('data/plausibility_training_v4_weak_labels.parquet')
CLUSTERS = Path('data/plausibility_training_v4_clusters.parquet')
ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
REPORT_JSON = Path('reports/model_v4_eval.json')
PLOTS_DIR = Path('reports/plots_v4')

FEATURE_COLS = [
    'title_len','abstract_len','citation_count','influential_citation_count',
    'influential_ratio','recency_years','fields_count','abstract_title_len_ratio'
]

def load_enriched() -> pd.DataFrame:
    if not ENRICHED.exists():
        return pd.DataFrame([])
    rows = [json.loads(line) for line in ENRICHED.read_text(encoding='utf-8').splitlines() if line.strip()]
    return pd.DataFrame(rows)


def main():
    if not MODEL_PATH.exists():
        print('Modelo no encontrado')
        return
    model_bundle = joblib.load(MODEL_PATH)
    model = model_bundle['model']
    df_e = load_enriched()
    if df_e.empty:
        print('Dataset vacío')
        return
    if CLUSTERS.exists():
        df_c = pd.read_parquet(CLUSTERS)[['paper_id','cluster_id']]
        df_e = df_e.merge(df_c, on='paper_id', how='left')
    if WEAK.exists():
        df_w = pd.read_parquet(WEAK)
        df_e = df_e.merge(df_w, on='paper_id', how='left')
    df_e['cluster_id'] = df_e['cluster_id'].fillna(-1)
    X_num = df_e[FEATURE_COLS].fillna(0)
    if df_e['cluster_id'].nunique() < 200:
        X_cluster = pd.get_dummies(df_e['cluster_id'].astype(int), prefix='cl')
        X = pd.concat([X_num, X_cluster], axis=1)
    else:
        X = X_num
    y = df_e['weak_label'].fillna(0).astype(int)
    proba = model.predict_proba(X)[:,1]
    auc = roc_auc_score(y, proba)
    pr_auc = average_precision_score(y, proba)
    brier = brier_score_loss(y, proba)
    prob_true, prob_pred = calibration_curve(y, proba, n_bins=10, strategy='quantile')
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(4,4))
    plt.plot([0,1],[0,1],'--',color='gray')
    plt.plot(prob_pred, prob_true, marker='o')
    plt.xlabel('Predicted')
    plt.ylabel('Observed')
    plt.title('Calibration')
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / 'calibration.png')
    report = {
        'auc': auc,
        'pr_auc': pr_auc,
        'brier': brier,
        'n_samples': int(len(df_e))
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Reporte guardado: {REPORT_JSON}')

if __name__ == '__main__':
    main()
