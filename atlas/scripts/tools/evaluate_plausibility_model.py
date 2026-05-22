"""Evalúa el modelo de plausibility.

Mejoras v2:
 - Acepta dataset por argumento CLI (default v2 si existe).
 - Soporta claves `model_probability` o `model_score` del servicio.
 - Calcula métricas clásicas (AUC, Accuracy, F1, Brier) y estadísticas de diversidad de dominio
     (distribución y entropía normalizada si está presente la columna de one-hot o el campo `domain`).
 - Permite filtrar features prohibidas solo para reconstrucción (no usado ahora pero preparado).
 - Escribe resultado en `metrics/plausibility_eval_v2.json` si se usa dataset v2.
"""
from __future__ import annotations
from pathlib import Path
import json
import argparse
from typing import List, Dict, Any, Tuple
import math

from app.services.plausibility_scoring_service import get_plausibility_service

DEFAULT_DATASET_V1 = Path("data/plausibility_training.jsonl")
DEFAULT_DATASET_V2 = Path("data/plausibility_training_v2.jsonl")


def resolve_paths(dataset_arg: str | None) -> Tuple[Path, Path]:
    if dataset_arg:
        ds = Path(dataset_arg)
    else:
        ds = DEFAULT_DATASET_V2 if DEFAULT_DATASET_V2.exists() else DEFAULT_DATASET_V1
    out_name = "plausibility_eval_v2.json" if ds.name.endswith("_v2.jsonl") else "plausibility_eval.json"
    return ds, Path("metrics") / out_name


def load_dataset(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    lines = path.read_text(encoding='utf-8').strip().splitlines()
    out = []
    import json as _json
    for ln in lines:
        try:
            out.append(_json.loads(ln))
        except Exception:
            pass
    return out


def domain_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    total = 0
    for r in records:
        d = r.get("domain") or r.get("domain_raw") or ""  # fallback
        if d:
            counts[d] = counts.get(d, 0) + 1
            total += 1
    if not counts:
        return {"domain_counts": {}, "domain_entropy_norm": None}
    # Shannon entropy
    probs = [c / total for c in counts.values()]
    entropy = -sum(p * math.log(p + 1e-12, 2) for p in probs)
    max_entropy = math.log(len(counts) + 1e-12, 2)
    entropy_norm = entropy / max_entropy if max_entropy > 0 else None
    return {
        "domain_counts": counts,
        "domain_entropy_norm": entropy_norm,
        "domain_unique": len(counts),
        "domain_total_labeled": total,
    }


def evaluate(dataset_path: Path):  # pragma: no cover
    svc = get_plausibility_service()
    recs = load_dataset(dataset_path)
    if not recs:
        print("[WARN] Dataset vacío")
        return
    y_true: List[int] = []
    y_prob: List[float] = []
    for r in recs:
        y_true.append(int(r.get("label", 0)))
        # reconstruir score usando servicio (aplica scaler/pca + temperatura si procede)
        dummy = {
            "title": r.get("title", ""),
            "description": r.get("abstract", r.get("description", "")),
            "variables": [],
            "assumptions": [],
            "expected_outcome": r.get("expected_outcome", ""),
            "domain": r.get("domain", ""),
            "hypothesis_uuid": None,
        }
        scored = svc.score_hypothesis(dummy)
        prob = (
            scored.get("model_probability")
            or scored.get("model_score")
            or scored.get("composite")
            or 0.0
        )
        y_prob.append(float(prob))
    try:
        from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, brier_score_loss
        import numpy as np
        preds = (np.array(y_prob) >= 0.5).astype(int)
        metrics = {
            "auc": float(roc_auc_score(y_true, y_prob)),
            "accuracy": float(accuracy_score(y_true, preds)),
            "f1": float(f1_score(y_true, preds)),
            "brier": float(brier_score_loss(y_true, y_prob)),
            "n": len(y_true)
        }
    except Exception as e:
        metrics = {"error": str(e), "n": len(y_true)}
    metrics.update(domain_stats(recs))
    out_path = resolve_paths(str(dataset_path))[1]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[OK] Métricas guardadas en", out_path, metrics)


def main():  # pragma: no cover
    parser = argparse.ArgumentParser(description="Evaluar modelo plausibility")
    parser.add_argument("--dataset", help="Ruta dataset jsonl (default: v2 si existe)", default=None)
    args = parser.parse_args()
    ds, _ = resolve_paths(args.dataset)
    evaluate(ds)

if __name__ == "__main__":  # pragma: no cover
    main()
