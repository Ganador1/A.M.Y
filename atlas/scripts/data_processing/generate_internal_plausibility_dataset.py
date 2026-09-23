"""Genera dataset interno de plausibility (v1 y v2) a partir de hipótesis persistidas.

v1 (legacy):
 - Percentiles globales de confianza para etiquetar (tercio inferior -> 0, tercio superior -> 1).
 - Incluye feature `confidence_score` (riesgo de leakage -> evitado en entrenamiento filtrando en servicio).

v2 (actual):
 - Percentiles por dominio (reduce sesgo inter-dominio y fuerza diversidad).
 - Elimina por completo `confidence_score` de los features para suprimir fuga de información.
 - Añade campo `domain` explícito (fallback 'unknown').
 - Balanceo simple intra-dominio (submuestreo de clase mayoritaria si ratio > 4:1) para evitar colapso.
 - Archivo de salida: data/plausibility_training_v2.jsonl (el servicio ahora prioriza este archivo).

Ambos datasets pueden regenerarse en la misma ejecución para reproducibilidad y auditoría.
"""
from __future__ import annotations
import json
from pathlib import Path
from typing import List, Dict, Any, cast, Tuple

from app.database import get_db_session, init_database
from app.models.hypothesis_models import HypothesisRecord
from app.services.plausibility_scoring_service import get_plausibility_service

OUT_PATH_V1 = Path("data/plausibility_training.jsonl")
OUT_PATH_V2 = Path("data/plausibility_training_v2.jsonl")
BALANCE_DOMAINS = True

# Palabras clave simples para mapear dominios interdisciplinarios (extensible)
DOMAIN_KEYWORDS = {
    "biology": ["cell", "genome", "protein", "bio", "enzyme", "dna", "rna"],
    "chemistry": ["molecule", "reaction", "synthesis", "catalyst", "compound", "ligand"],
    "materials": ["alloy", "crystal", "material", "polymer", "nanotube", "semiconductor"],
    "physics": ["quantum", "plasma", "thermo", "kinetic", "particle", "wave"],
    "medical": ["clinical", "patient", "cardiac", "diagnosis", "therapy", "trial"],
    "ai": ["model", "neural", "dataset", "learning", "transformer", "embedding"],
    "energy": ["battery", "solar", "photovoltaic", "fuel cell", "fusion", "energy"],
}

def infer_domain_free_text(title: str, desc: str, original: str) -> str:
    text = f"{title} {desc}".lower()
    # Si ya hay dominio explícito no 'unknown', lo preservamos
    if original and original != 'unknown':
        return original
    scores: Dict[str, int] = {}
    for dom, kws in DOMAIN_KEYWORDS.items():
        c = 0
        for kw in kws:
            if kw in text:
                c += 1
        if c:
            scores[dom] = c
    if not scores:
        return original or 'unknown'
    # dominio con mayor coincidencia
    return max(scores.items(), key=lambda x: x[1])[0]


def _token_count(txt: str) -> int:
    return len((txt or "").split())


def _compute_domain_percentiles(domain_conf_map: Dict[str, List[float]]) -> Dict[str, Tuple[float, float]]:
    """Devuelve (low_th, high_th) por dominio usando percentiles 33% y 66%.
    Si un dominio tiene <3 valores, se usa (0.0, 1.0) para evitar ruido.
    """
    import math
    out: Dict[str, Tuple[float, float]] = {}
    for dom, vals in domain_conf_map.items():
        if not vals or len(vals) < 3:
            out[dom] = (0.0, 1.0)
            continue
        vals_sorted = sorted(vals)
        def q(p: float) -> float:
            k = (len(vals_sorted)-1)*p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return vals_sorted[int(k)]
            return vals_sorted[f] + (k-f)*(vals_sorted[c]-vals_sorted[f])
        out[dom] = (q(0.33), q(0.66))
    return out


def build_internal_records(v2: bool = True) -> List[Dict[str, Any]]:
    init_database()
    db = get_db_session()
    svc = get_plausibility_service()
    rows = db.query(HypothesisRecord).all()
    temp: List[Dict[str, Any]] = []
    confidences: List[float] = []  # global (solo v1)
    domain_conf: Dict[str, List[float]] = {}
    for r in rows:
        title = cast(str, getattr(r, 'title', '') or "")
        desc = cast(str, getattr(r, 'description', '') or "")
        domain_raw = getattr(r, 'domain', '') or 'unknown'
        inferred_domain = infer_domain_free_text(title, desc, domain_raw)
        base_score = svc.score_hypothesis({
            "title": title,
            "description": desc,
            "variables": getattr(r, 'variables', []) or [],
            "assumptions": getattr(r, 'assumptions', []) or [],
            "expected_outcome": getattr(r, 'expected_outcome', None),
            "domain": inferred_domain,
            "hypothesis_uuid": getattr(r, 'hypothesis_uuid', None)
        })
        confidence = float(getattr(r, 'confidence_score', 0.0) or 0.0)
        temp.append({
            "r": r,
            "title": title,
            "desc": desc,
            "base_score": base_score,
            "confidence": confidence,
            "evidence_count": int(getattr(r, 'evidence_count', 0) or 0),
            "refinement_count": int(getattr(r, 'refinement_count', 0) or 0),
            "domain": inferred_domain,
        })
        confidences.append(confidence)
        domain_conf.setdefault(inferred_domain, []).append(confidence)
    out: List[Dict[str, Any]] = []
    if not v2:
        # Lógica original (v1) con percentiles globales
        if confidences:
            confidences_sorted = sorted(confidences)
            import math
            def q(p: float) -> float:
                if not confidences_sorted:
                    return 0.0
                k = (len(confidences_sorted)-1)*p
                f = math.floor(k)
                c = math.ceil(k)
                if f == c:
                    return confidences_sorted[int(k)]
                return confidences_sorted[f] + (k-f)*(confidences_sorted[c]-confidences_sorted[f])
            low_th = q(0.33)
            high_th = q(0.66)
        else:
            low_th, high_th = 0.0, 1.0
        for d in temp:
            conf = d["confidence"]
            if conf <= low_th:
                label = 0
            elif conf >= high_th:
                label = 1
            else:
                continue
            r = d["r"]
            evidence_count = d["evidence_count"]
            refinement_count = d["refinement_count"]
            base_score = d["base_score"]
            desc = d["desc"]
            current_dom = d["domain"]
            feat = {
                **base_score.get("components", {}),
                "heuristic_composite": base_score.get("composite", 0.0),
                "evidence_count_norm": min(1.0, evidence_count/10.0),
                "refinement_count_norm": min(1.0, refinement_count/10.0),
                "confidence_score": conf,  # solo v1
                "has_expected_outcome": 1.0 if (getattr(r, 'expected_outcome', '') or "").strip() else 0.0,
                "text_length_ratio": min(1.0, _token_count(desc)/800.0),
                # one-hot dominio (solo para trazabilidad en v1; entrenamiento lo filtrará)
                **{f"domain_{dom_key}": 1.0 if dom_key == current_dom else 0.0 for dom_key in DOMAIN_KEYWORDS.keys()},
            }
            out.append({
                "paper_id": getattr(r, 'hypothesis_uuid', None),
                "title": d["title"],
                "abstract": desc,
                "label": label,
                "features": feat,
                "domain": d["domain"],
            })
        print(f"[INFO][v1] Low_th={low_th:.4f} High_th={high_th:.4f} -> dataset rows={len(out)}")
    else:
        # v2: percentiles por dominio
        domain_thresholds = _compute_domain_percentiles(domain_conf)
        domain_buckets: Dict[str, List[Dict[str, Any]]] = {}
        for d in temp:
            dom = d["domain"]
            low_th, high_th = domain_thresholds.get(dom, (0.0, 1.0))
            conf = d["confidence"]
            if conf <= low_th:
                label = 0
            elif conf >= high_th:
                label = 1
            else:
                continue
            r = d["r"]
            evidence_count = d["evidence_count"]
            refinement_count = d["refinement_count"]
            base_score = d["base_score"]
            desc = d["desc"]
            feat = {
                **base_score.get("components", {}),
                "heuristic_composite": base_score.get("composite", 0.0),
                "evidence_count_norm": min(1.0, evidence_count/10.0),
                "refinement_count_norm": min(1.0, refinement_count/10.0),
                # no confidence_score en v2
                "has_expected_outcome": 1.0 if (getattr(r, 'expected_outcome', '') or "").strip() else 0.0,
                "text_length_ratio": min(1.0, _token_count(desc)/800.0),
                **{f"domain_{d_key}": 1.0 if d_key == dom else 0.0 for d_key in DOMAIN_KEYWORDS.keys()},
            }
            rec = {
                "paper_id": getattr(r, 'hypothesis_uuid', None),
                "title": d["title"],
                "abstract": desc,
                "label": label,
                "features": feat,
                "domain": dom,
            }
            domain_buckets.setdefault(dom, []).append(rec)
        import random
        import math
        rng = random.Random(42)
        for dom, bucket in domain_buckets.items():
            if not bucket:
                continue
            labels = [b["label"] for b in bucket]
            p1 = sum(labels)
            p0 = len(labels) - p1
            maj = max(p0, p1)
            minc = min(p0, p1)
            if BALANCE_DOMAINS and minc > 0 and maj / max(1, minc) > 4:
                class_major = 1 if p1 > p0 else 0
                keep = [b for b in bucket if b["label"] != class_major]
                majority_samples = [b for b in bucket if b["label"] == class_major]
                rng.shuffle(majority_samples)
                keep.extend(majority_samples[: 4 * len(keep)])
                bucket = keep
            out.extend(bucket)
        dist = {dom: len(lst) for dom, lst in domain_buckets.items()}
        # Métricas diversidad: entropía de distribución de dominios
        total = sum(dist.values()) or 1
        probs = [c/total for c in dist.values() if c > 0]
        entropy = -sum(p * math.log(p + 1e-12) for p in probs)
        max_entropy = math.log(max(1, len(dist)))
        norm_entropy = entropy / max_entropy if max_entropy > 0 else 0.0
        print(f"[INFO][v2] dominios={len(dist)} filas={len(out)} dist={dist} H={entropy:.3f} H_norm={norm_entropy:.3f}")
    db.close()
    return out


def write_jsonl(recs: List[Dict[str, Any]], path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8') as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main():  # pragma: no cover
    recs_v2 = build_internal_records(v2=True)
    write_jsonl(recs_v2, OUT_PATH_V2)
    print(f"[OK] dataset v2 generado con {len(recs_v2)} filas en {OUT_PATH_V2}")
    try:
        recs_v1 = build_internal_records(v2=False)
        write_jsonl(recs_v1, OUT_PATH_V1)
        print(f"[OK] dataset v1 regenerado con {len(recs_v1)} filas en {OUT_PATH_V1}")
    except Exception as e:
        print(f"[WARN] Falló regeneración v1: {e}")

if __name__ == "__main__":  # pragma: no cover
    main()
