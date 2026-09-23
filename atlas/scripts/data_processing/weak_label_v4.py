from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import json

ENRICHED = Path('data/plausibility_training_v4_enriched.jsonl')
CLUSTERS = Path('data/plausibility_training_v4_clusters.parquet')
OUT_WEAK = Path('data/plausibility_training_v4_weak_labels.parquet')
HEURISTICS = Path('data/heuristics_tuned_v4.json')

# Heurísticas básicas: mayor plausibilidad si: citas altas, abstract más largo moderado, recency intermedia
# Score en [0,1]

def load_enriched() -> pd.DataFrame:
    if not ENRICHED.exists():
        return pd.DataFrame([])
    rows = [json.loads(line) for line in ENRICHED.read_text(encoding='utf-8').splitlines() if line.strip()]
    return pd.DataFrame(rows)


def load_weights():
    if HEURISTICS.exists():
        try:
            data = json.loads(HEURISTICS.read_text(encoding='utf-8'))
            bp = data.get('best_params') or {}
            wc = bp.get('w_cits')
            wa = bp.get('w_abstract')
            wr = bp.get('w_recency')
            if all(isinstance(x, (int,float)) for x in [wc,wa,wr]):
                wc_val = float(wc)
                wa_val = float(wa)
                wr_val = float(wr)
                wc_capped = min(wc_val, 0.25)
                s = wc_capped + wa_val + wr_val
                if s > 0:
                    return wc_capped / s, wa_val / s, wr_val / s
        except Exception:
            pass
    return 0.5, 0.3, 0.2


def compute_scores(df: pd.DataFrame) -> pd.Series:
    if df.empty:
        return pd.Series([], dtype=float)
    cits = df['citation_count'].fillna(0).clip(lower=0)
    abstract_len = df['abstract_len'].fillna(0)
    recency = df['recency_years'].fillna(10)  # si no hay año, asumir viejo

    # Normalizaciones robustas (percentil 95)
    def robust_norm(s: pd.Series) -> pd.Series:
        p95 = s.quantile(0.95) or 1.0
        return (s / (p95 + 1e-9)).clip(0, 1)

    cits_n = robust_norm(cits)
    # Abstract: preferible rango medio (ej: penalizar demasiado corto o demasiado largo)
    abstract_n = (abstract_len / (abstract_len.quantile(0.90) + 1e-9)).clip(0, 1)
    abstract_mid = 1 - (abstract_n - 0.5).abs() * 2  # pico en ~0.5
    # Recency: preferir artículos ni excesivamente antiguos ni totalmente nuevos (ej pico ~3 años)
    recency_n = recency.clip(0, 15) / 15.0
    recency_pref = np.exp(-((recency_n - 0.2) ** 2) / 0.02)  # campana centrada ~0.2 (~3 años si 15 ~ escala)

    w_cits, w_abstract, w_recency = load_weights()
    score = w_cits * cits_n + w_abstract * abstract_mid + w_recency * recency_pref
    return score.clip(0, 1)


def main():
    df_e = load_enriched()
    if df_e.empty:
        print('Datos enriquecidos no encontrados.')
        return
    if CLUSTERS.exists():
        df_c = pd.read_parquet(CLUSTERS)[['paper_id', 'cluster_id']]
        df = df_e.merge(df_c, on='paper_id', how='left')
    else:
        df = df_e.copy()
    df['weak_label_score'] = compute_scores(df)
    # Etiqueta binaria provisional (threshold mediana)
    thr = df['weak_label_score'].median()
    df['weak_label'] = (df['weak_label_score'] >= thr).astype(int)
    df[['paper_id','weak_label_score','weak_label']].to_parquet(OUT_WEAK, index=False)
    print(f'Weak labels guardados: {OUT_WEAK}')


if __name__ == '__main__':
    main()
