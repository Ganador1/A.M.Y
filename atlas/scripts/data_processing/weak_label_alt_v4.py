from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import json

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
OUT_ALT = Path('data/plausibility_training_v4_weak_labels_alt.parquet')

# Alternativa: eliminar influencia directa de citation_count.
# Enfatiza forma del abstract y recency templada para reducir fuga de señal de citas.
# Además construye una versión "low_cits" donde la cita tiene peso marginal.

def load_enriched() -> pd.DataFrame:
    if not ENRICHED.exists():
        return pd.DataFrame([])
    rows = [json.loads(l) for l in ENRICHED.read_text(encoding='utf-8').splitlines() if l.strip()]
    return pd.DataFrame(rows)


def mid_shape(series: pd.Series, p_high=0.9) -> pd.Series:
    s = series.fillna(0)
    cap = s.quantile(p_high) or 1.0
    n = (s / (cap + 1e-9)).clip(0,1)
    return 1 - (n - 0.5).abs() * 2


def recency_pref(years: pd.Series) -> pd.Series:
    r = years.fillna(10).clip(0, 15) / 15.0
    return np.exp(-((r - 0.25)**2)/0.025)


def build_scores(df: pd.DataFrame):
    a_mid = mid_shape(df['abstract_len'])
    rec = recency_pref(df['recency_years'])
    cits = df['citation_count'].fillna(0)
    cits_n = (cits / (cits.quantile(0.90) + 1e-9)).clip(0,1)
    # Variante sin citas
    score_no_cits = (0.65 * a_mid + 0.35 * rec).clip(0,1)
    # Variante citas minimizadas
    score_low_cits = (0.55 * a_mid + 0.30 * rec + 0.15 * cits_n).clip(0,1)
    return score_no_cits, score_low_cits


def to_labels(score: pd.Series):
    thr = score.median()
    return (score >= thr).astype(int), thr


def main():
    df = load_enriched()
    if df.empty:
        print('No enriched data para weak labels alternativas.')
        return
    s_no, s_low = build_scores(df)
    lab_no, thr_no = to_labels(s_no)
    lab_low, thr_low = to_labels(s_low)
    out = pd.DataFrame({
        'paper_id': df['paper_id'],
        'weak_label_score_no_cits': s_no,
        'weak_label_alt_no_cits': lab_no,
        'weak_label_score_low_cits': s_low,
        'weak_label_alt_low_cits': lab_low,
        'thr_no_cits': thr_no,
        'thr_low_cits': thr_low
    })
    OUT_ALT.parent.mkdir(parents=True, exist_ok=True)
    out.to_parquet(OUT_ALT, index=False)
    print(f'Weak labels alternativas guardadas en {OUT_ALT}')

if __name__ == '__main__':
    main()
