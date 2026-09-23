from __future__ import annotations
import json, math, random
from pathlib import Path
from typing import List, Dict, Any
import optuna
import numpy as np
import pandas as pd

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
SPLITS_DIR = Path('data/splits_v4')
OUT_PATH = Path('data/heuristics_tuned_v4.json')
SEED = 42
random.seed(SEED)

FEATURES = {
    'citation_count': {'clip_p95': True},
    'abstract_len': {'clip_p90': True},
    'recency_years': {'gauss_center': 3.0, 'gauss_scale': 4.0},
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines() if l.strip()]


def load_split(name: str) -> pd.DataFrame:
    p = SPLITS_DIR / f'{name}.jsonl'
    rows = load_jsonl(p)
    return pd.DataFrame(rows)


def robust_norm(series: pd.Series, p=0.95):
    cap = series.quantile(p) or 1.0
    return (series / (cap + 1e-9)).clip(0, 1)


def score_rows(df: pd.DataFrame, w_cits: float, w_abstract: float, w_recency: float) -> pd.Series:
    cits_n = robust_norm(df['citation_count'].fillna(0))
    abstract_raw = df['abstract_len'].fillna(0)
    abstract_n = (abstract_raw / (abstract_raw.quantile(0.90) + 1e-9)).clip(0, 1)
    abstract_mid = 1 - (abstract_n - 0.5).abs() * 2
    rec = df['recency_years'].fillna(10)
    rec_n = (rec / 15.0).clip(0, 1)
    rec_pref = np.exp(-((rec_n - 0.2) ** 2) / 0.02)
    return (w_cits * cits_n + w_abstract * abstract_mid + w_recency * rec_pref).clip(0, 1)


def objective(trial: optuna.Trial):
    w_cits = trial.suggest_float('w_cits', 0.1, 0.8)
    w_abstract = trial.suggest_float('w_abstract', 0.1, 0.8)
    w_recency = trial.suggest_float('w_recency', 0.05, 0.5)
    # Normalizar pesos
    s = w_cits + w_abstract + w_recency
    w_cits, w_abstract, w_recency = w_cits/s, w_abstract/s, w_recency/s
    train_df = load_split('train')
    val_df = load_split('val')
    if train_df.empty or val_df.empty:
        raise optuna.TrialPruned()
    # Generar pseudo etiquetas base usando mediana train
    train_scores = score_rows(train_df, w_cits, w_abstract, w_recency)
    thr = train_scores.median()
    train_labels = (train_scores >= thr).astype(int)
    val_scores = score_rows(val_df, w_cits, w_abstract, w_recency)
    val_labels = (val_scores >= thr).astype(int)
    # Métrica simple: separación media entre clases en val
    sep = val_scores[val_labels==1].mean() - val_scores[val_labels==0].mean()
    return float(sep)


def main():
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=40, show_progress_bar=False)
    best = study.best_params
    with OUT_PATH.open('w', encoding='utf-8') as f:
        json.dump({'best_params': best}, f, ensure_ascii=False, indent=2)
    print(f'Heurísticas optimizadas guardadas en {OUT_PATH}: {best}')


if __name__ == '__main__':
    main()
