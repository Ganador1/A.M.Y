from __future__ import annotations
from pathlib import Path
import pandas as pd
import numpy as np
import json
from typing import Dict, Tuple, Optional

import mlflow

BASE = Path('data/plausibility_training_v4_weak_labels.parquet')
ALT = Path('data/plausibility_training_v4_weak_labels_alt.parquet')
OUT = Path('data/plausibility_training_v4_weak_labels_ensemble.parquet')
MANUAL = Path('data/manual_labels_v4.json')
MANUAL_LLM = Path('data/manual_labels_v4_ollama.json')
from pipeline_metadata_v4 import ARTIFACT_MAP, file_hash, git_commit

# Estrategia: grid search sobre pesos de combinación entre score base y score_no_cits.
# Si no hay labels manuales, se usa promedio 0.5/0.5 como fallback.


def _load_manual_labels(path: Path) -> Dict[str, int]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        labels = data.get('manual_labels') or {}
        # Normalizar a int 0/1
        return {str(k): int(v) for k, v in labels.items() if v in (0, 1, '0', '1')}
    except Exception as e:
        print(f"Warning: no se pudieron cargar labels desde {path}: {e}")
        return {}


def _ece(y_true: np.ndarray, y_prob: np.ndarray, n_bins: int = 10) -> float:
    # Expected Calibration Error
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    inds = np.digitize(y_prob, bins) - 1
    ece = 0.0
    n = len(y_true)
    for b in range(n_bins):
        mask = inds == b
        if not np.any(mask):
            continue
        conf = y_prob[mask].mean()
        acc = y_true[mask].mean()
        ece += (np.sum(mask) / n) * abs(acc - conf)
    return float(ece)


def _brier(y_true: np.ndarray, y_prob: np.ndarray) -> float:
    return float(np.mean((y_prob - y_true) ** 2))


def _f1_at_threshold(y_true: np.ndarray, y_prob: np.ndarray, thr: float) -> float:
    y_pred = (y_prob >= thr).astype(int)
    tp = np.sum((y_pred == 1) & (y_true == 1))
    fp = np.sum((y_pred == 1) & (y_true == 0))
    fn = np.sum((y_pred == 0) & (y_true == 1))
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    return float(f1)


def _evaluate_weights(y_true: np.ndarray, base: np.ndarray, no_cits: np.ndarray, w_base: float) -> Dict[str, float]:
    w_nc = 1.0 - w_base
    p = (w_base * base + w_nc * no_cits).clip(0, 1)
    thr = float(np.median(p))
    return {
        'w_base': w_base,
        'w_no_cits': w_nc,
        'brier': _brier(y_true, p),
        'ece': _ece(y_true, p, n_bins=10),
        'f1': _f1_at_threshold(y_true, p, thr),
        'thr_eval': thr,
        'n_eval': int(y_true.shape[0])
    }


def _pick_best(results: list[Dict[str, float]]) -> Dict[str, float]:
    # Orden: menor Brier, mayor F1, menor ECE
    return sorted(results, key=lambda r: (r['brier'], -r['f1'], r['ece']))[0]


def _update_artifact_map(artifact_name: str, path: Path, params: Dict[str, float] | None = None) -> None:
    try:
        if ARTIFACT_MAP.exists():
            data = json.loads(ARTIFACT_MAP.read_text(encoding='utf-8'))
        else:
            data = {'artifacts': []}
        artifacts = data.get('artifacts') or []
        # eliminar entradas previas con el mismo nombre
        artifacts = [a for a in artifacts if a.get('name') != artifact_name]
        rec = {
            'name': artifact_name,
            'path': str(path),
            'exists': path.exists(),
            'hash': file_hash(path) if path.exists() else None,
            'producer': 'weak_label_ensemble_v4',
            'git_commit': git_commit(),
            'params': params or {}
        }
        artifacts.append(rec)
        data['artifacts'] = artifacts
        ARTIFACT_MAP.parent.mkdir(parents=True, exist_ok=True)
        ARTIFACT_MAP.write_text(json.dumps({'artifacts': artifacts}, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"🗺️  Artifact map actualizado en {ARTIFACT_MAP}")
    except Exception as e:
        print(f"Warning: no se pudo actualizar artifact_map: {e}")


def main():
    if not BASE.exists() or not ALT.exists():
        print('Faltan archivos base o alterno para ensemble.')
        return

    b = pd.read_parquet(BASE)
    a = pd.read_parquet(ALT)
    if 'weak_label_score' not in b.columns:
        print('Columna weak_label_score faltante en base.')
        return
    if 'weak_label_score_no_cits' not in a.columns:
        print('Columna weak_label_score_no_cits faltante en alt.')
        return

    merged = b.merge(a[['paper_id', 'weak_label_score_no_cits']], on='paper_id', how='inner')

    # Cargar labels manuales (preferir humanas sobre LLM)
    lbl_h = _load_manual_labels(MANUAL)
    lbl_llm = _load_manual_labels(MANUAL_LLM)
    labels: Dict[str, int] = {**lbl_llm, **lbl_h}  # las humanas sobreescriben

    best = None
    mlflow_logged = False

    if labels:
        eval_df = merged[merged['paper_id'].astype(str).isin(labels.keys())].copy()
        if not eval_df.empty:
            y_true = eval_df['paper_id'].astype(str).map(labels).astype(int).to_numpy()
            base_p = eval_df['weak_label_score'].to_numpy()
            no_cits_p = eval_df['weak_label_score_no_cits'].to_numpy()

            grid = [0.0, 0.25, 0.5, 0.75, 1.0]
            results = [_evaluate_weights(y_true, base_p, no_cits_p, w) for w in grid]
            best = _pick_best(results)

            # MLflow logging
            try:
                mlflow.set_experiment('plausibility_v4')
                with mlflow.start_run(run_name='weak_label_ensemble_v4'):
                    mlflow.log_params({'w_base': best['w_base'], 'w_no_cits': best['w_no_cits']})
                    mlflow.log_metrics({k: float(best[k]) for k in ['brier', 'ece', 'f1', 'thr_eval']})
                    mlflow.log_metric('n_eval', int(best['n_eval']))
                mlflow_logged = True
            except Exception as e:
                print(f"Warning: fallo al loggear en MLflow: {e}")
        else:
            print('No hay intersección entre labels manuales y dataset; se usará promedio 0.5/0.5')
    else:
        print('No se encontraron labels manuales; se usará promedio 0.5/0.5')

    # Aplicar pesos a todo el dataset
    if best is None:
        w_base = 0.5
        w_nc = 0.5
    else:
        w_base = float(best['w_base'])
        w_nc = float(best['w_no_cits'])

    merged['ensemble_score'] = (w_base * merged['weak_label_score'] + w_nc * merged['weak_label_score_no_cits']).clip(0, 1)
    thr_full = float(merged['ensemble_score'].median())
    merged['ensemble_label'] = (merged['ensemble_score'] >= thr_full).astype(int)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    merged[['paper_id', 'ensemble_score', 'ensemble_label']].to_parquet(OUT, index=False)

    msg = f"Ensemble guardado en {OUT} w_base={w_base:.2f} w_no_cits={w_nc:.2f} thr_full={thr_full:.4f}"
    if mlflow_logged:
        msg += " (metrics at MLflow)"
    print(msg)

    # Actualizar artifact_map con los parámetros del ensemble
    _update_artifact_map(
        'weak_labels_ensemble',
        OUT,
        params={
            'w_base': w_base,
            'w_no_cits': w_nc,
            'thr_full': thr_full
        }
    )


if __name__ == '__main__':
    main()
