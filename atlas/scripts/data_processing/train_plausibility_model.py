"""Entrena el modelo de plausibility v2 usando dataset jsonl (v2) y guarda artefactos.

Salida:
 - models/plausibility_model.joblib
 - models/plausibility_scaler.joblib
 - (opcional) models/plausibility_pca.joblib
 - metrics/plausibility_training_metrics.json

Estrategia:
 1. Cargar dataset v2 (data/plausibility_training_v2.jsonl)
 2. Construir matriz X a partir de features numéricos (excluyendo campos baneados)
 3. Escalar con StandardScaler
 4. (Opcional) PCA si dims > 24
 5. Entrenar LogisticRegression liblinear (balance='balanced')
 6. Calcular métricas (AUC, F1, accuracy, Brier, calibración simple)
 7. Guardar artefactos
"""
from __future__ import annotations
from pathlib import Path
import json
from typing import List, Dict, Any

from app.services.plausibility_scoring_service import get_plausibility_service

DATA_V2 = Path("data/plausibility_training_v2.jsonl")
METRICS_OUT = Path("metrics/plausibility_training_metrics.json")

# Campos que nunca deben usarse (fuga de señal)
BANNED = {"confidence_score"}


def load_dataset() -> List[Dict[str, Any]]:
    if not DATA_V2.exists():
        raise FileNotFoundError(f"No existe dataset v2 en {DATA_V2}")
    recs: List[Dict[str, Any]] = []
    for ln in DATA_V2.read_text(encoding='utf-8').splitlines():
        if not ln.strip():
            continue
        try:
            recs.append(json.loads(ln))
        except Exception:
            pass
    return recs


def build_matrix(recs: List[Dict[str, Any]]):
    import numpy as np
    # Recolectar todos los nombres de feature
    feature_names = set()
    for r in recs:
        feats = r.get("features", {})
        for k in feats.keys():
            if k in BANNED:
                continue
            feature_names.add(k)
    feature_names = sorted(feature_names)
    X = []
    y = []
    for r in recs:
        feats = r.get("features", {})
        row = []
        for name in feature_names:
            row.append(float(feats.get(name, 0.0)))
        X.append(row)
        y.append(int(r.get("label", 0)))
    return np.array(X, dtype=float), np.array(y, dtype=int), feature_names


def train():  # pragma: no cover
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, brier_score_loss
    from sklearn.model_selection import StratifiedKFold
    import joblib

    recs = load_dataset()
    if not recs:
        print("[WARN] dataset vacío")
        return
    X, y, feature_names = build_matrix(recs)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    pca = None
    if Xs.shape[1] > 24:
        pca = PCA(n_components= min(24, Xs.shape[1]))
        Xs_reduced = pca.fit_transform(Xs)
    else:
        Xs_reduced = Xs

    # Validación cruzada rápida para estimar desempeño
    cv = StratifiedKFold(n_splits=min(5, sum(y==0), sum(y==1), 5)) if len(y) >= 40 else None
    cv_metrics = []
    if cv:
        for train_idx, test_idx in cv.split(Xs_reduced, y):
            clf_cv = LogisticRegression(max_iter=1000, solver='liblinear', class_weight='balanced')
            clf_cv.fit(Xs_reduced[train_idx], y[train_idx])
            probs = clf_cv.predict_proba(Xs_reduced[test_idx])[:,1]
            preds = (probs >= 0.5).astype(int)
            try:
                fold_metrics = {
                    "auc": float(roc_auc_score(y[test_idx], probs)),
                    "accuracy": float(accuracy_score(y[test_idx], preds)),
                    "f1": float(f1_score(y[test_idx], preds)),
                    "brier": float(brier_score_loss(y[test_idx], probs)),
                }
            except Exception as e:
                fold_metrics = {"error": str(e)}
            cv_metrics.append(fold_metrics)
    # Entrenamiento final
    clf = LogisticRegression(max_iter=1000, solver='liblinear', class_weight='balanced')
    clf.fit(Xs_reduced, y)
    probs_full = clf.predict_proba(Xs_reduced)[:,1]
    preds_full = (probs_full >= 0.5).astype(int)
    try:
        train_metrics = {
            "auc": float(roc_auc_score(y, probs_full)),
            "accuracy": float(accuracy_score(y, preds_full)),
            "f1": float(f1_score(y, preds_full)),
            "brier": float(brier_score_loss(y, probs_full)),
        }
    except Exception as e:
        train_metrics = {"error": str(e)}

    # Guardar artefactos
    Path("models").mkdir(exist_ok=True)
    joblib.dump(clf, "models/plausibility_model.joblib")
    joblib.dump(scaler, "models/plausibility_scaler.joblib")
    if pca is not None:
        joblib.dump(pca, "models/plausibility_pca.joblib")

    METRICS_OUT.parent.mkdir(parents=True, exist_ok=True)
    METRICS_OUT.write_text(json.dumps({
        "train": train_metrics,
        "cv": cv_metrics,
        "n": int(len(y)),
        "features": feature_names,
    }, indent=2), encoding='utf-8')
    print("[OK] Entrenamiento completado. Métricas en", METRICS_OUT)

    # Actualizar servicio en memoria (hot-reload sencillo)
    svc = get_plausibility_service()
    svc._load_model_if_exists()
    svc._load_aux_artifacts()

if __name__ == "__main__":  # pragma: no cover
    train()
