"""A/B test para comparar prompt estático vs PromptRegistry en generación de hipótesis.
Estrategia:
- Ejecutar N escenarios (dominio + pregunta) con y sin registry.
- Métricas colectadas: longitud descripción, nº variables, confianza, tiempo de respuesta.
- Reporte simple en consola.

Requiere: ScientificHypothesisAgent y (opcional) local LLM; si no hay LLM usará lógica heurística, útil para validar flujo.
"""
from __future__ import annotations
import os
import sys
import asyncio
import time
from statistics import mean
from typing import List, Dict, Any, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent
from app.logging_config import log_decision_event
from app.middleware.trace_id_middleware import get_current_trace_id

SCENARIOS = [
    {"domain": "materials_science", "research_question": "How does nano-structuring affect thermal conductivity of the alloy?", "context_data": {"material": "Fe-Cu", "scale": "nano"}},
    {"domain": "drug_discovery", "research_question": "Can modifying the side chain improve binding affinity to the target receptor?", "context_data": {"receptor": "GPCR", "modification": "alkyl chain"}},
    {"domain": "energy_storage", "research_question": "Does electrolyte additive X extend cycle life in Li-ion cells?", "context_data": {"additive": "X", "cell_type": "NMC"}},
]

RUNS_PER_SCENARIO = 6  # aumentar para señal estadística (ajustar según coste)

V2_TEMPLATE = (
    "Generate ONE testable scientific hypothesis. List 3-5 DISTINCT, specific experimental variables."
    "\nDomain: {{ domain }}"
    "\nQuestion: {{ research_question }}"
    "\nContext: {{ context_data }}"
    "\nReturn JSON keys: title, description, variables (3-5), assumptions, expected_outcome, confidence_score (0-1)."
)


def summarize(hyp: Dict[str, Any]) -> Dict[str, Any]:
    """Extrae métricas base de la hipótesis."""
    raw_vars = hyp.get("variables", []) or []
    if not isinstance(raw_vars, list):
        raw_vars = [raw_vars]
    # Sanitizar: convertir todo a string hashable
    clean_vars = []
    for v in raw_vars:
        if isinstance(v, str):
            clean_vars.append(v.strip())
        elif isinstance(v, (int, float)):
            clean_vars.append(str(v))
        elif isinstance(v, dict):
            # usar claves principales concatenadas
            clean_vars.append("dict:" + ",".join(sorted(map(str, v.keys()))))
        else:
            clean_vars.append(repr(v))
    return {
        "title": hyp.get("title", ""),
        "description": hyp.get("description", ""),
        "variables": clean_vars,
        "title_len": len(hyp.get("title", "")),
        "desc_len": len(hyp.get("description", "")),
        "n_vars": len(clean_vars),
        "confidence": hyp.get("confidence_score", 0.0),
    }


async def run_variant(agent: ScientificHypothesisAgent, scenario: Dict[str, Any], use_registry: bool, prompt_version: str | None = None) -> Dict[str, Any]:
    start = time.time()
    payload = {
        "domain": scenario["domain"],
        "research_question": scenario["research_question"],
        "context_data": scenario.get("context_data", {}),
        "use_prompt_registry": use_registry,
    }
    if prompt_version:
        payload["prompt_version"] = prompt_version
    res = await agent.generate_hypothesis(payload)
    elapsed = time.time() - start
    if not res.get("success"):
        return {"error": res.get("error", "unknown"), "elapsed": elapsed}
    hyp = res.get("hypothesis", {})
    metrics = summarize(hyp)
    metrics["elapsed"] = elapsed
    return metrics


def jaccard(a: List[str], b: List[str]) -> float:
    if not a and not b:
        return 1.0
    sa, sb = set(a), set(b)
    inter = len(sa & sb)
    union = len(sa | sb) or 1
    return inter / union


async def ensure_v2_prompt(agent: ScientificHypothesisAgent):
    try:
        reg = agent.prompt_registry.get(name="hypothesis_generation", version="v2")
        if reg.get("success"):
            return
    except Exception:
        pass
    agent.prompt_registry.register(
        name="hypothesis_generation",
        version="v2",
        template=V2_TEMPLATE,
        variables=["domain", "research_question", "context_data"],
        metadata={"description": "Hypothesis generation v2 - enforces 3-5 variables"}
    )


def normalize_title(title: str) -> str:
    t = title.strip()
    if t.endswith('.'):
        t = t[:-1].strip()
    if t:
        t = t[0].upper() + t[1:]
    return t


def pairwise_jaccard(sets: List[List[str]]) -> Tuple[float, float]:
    """Devuelve (mean_jaccard_similarity, diversity=1-mean_similarity)."""
    if len(sets) < 2:
        return 1.0, 0.0
    sims = []
    for i in range(len(sets)):
        for j in range(i + 1, len(sets)):
            sims.append(jaccard(sets[i], sets[j]))
    if not sims:
        return 1.0, 0.0
    m = sum(sims) / len(sims)
    return m, 1 - m


async def main():
    agent = ScientificHypothesisAgent()
    await ensure_v2_prompt(agent)
    results: List[Dict[str, Any]] = []
    for sc in SCENARIOS:
        for _ in range(RUNS_PER_SCENARIO):
            # static
            static_res = await run_variant(agent, sc, use_registry=False)
            static_res["normalized_title"] = normalize_title(static_res.get("title", "")) if not static_res.get("error") else ""
            results.append({"scenario": sc["domain"], "variant": "static", **static_res})
            # registry v1 (implicit default)
            v1_res = await run_variant(agent, sc, use_registry=True, prompt_version="v1")
            if not v1_res.get("error") and v1_res.get("n_vars", 0) < 3:
                # penalización suave
                v1_res["confidence"] = max(0.0, v1_res.get("confidence", 0.0) - 0.10)
                v1_res["penalty_applied"] = True
            else:
                v1_res["penalty_applied"] = False
            v1_res["normalized_title"] = normalize_title(v1_res.get("title", "")) if not v1_res.get("error") else ""
            results.append({"scenario": sc["domain"], "variant": "registry_v1", **v1_res})
            # registry v2
            v2_res = await run_variant(agent, sc, use_registry=True, prompt_version="v2")
            v2_res["normalized_title"] = normalize_title(v2_res.get("title", "")) if not v2_res.get("error") else ""
            results.append({"scenario": sc["domain"], "variant": "registry_v2", **v2_res})

    # Agregación
    grouped: Dict[str, Dict[str, List[float]]] = {}
    variable_sets: Dict[str, List[List[str]]] = {}
    title_consistency: Dict[str, List[int]] = {}
    penalty_counts: Dict[str, int] = {}
    for r in results:
        if r.get("error"):
            continue
        key = r["variant"]
        grouped.setdefault(key, {k: [] for k in ["title_len", "desc_len", "n_vars", "confidence", "elapsed"]})
        for m in grouped[key].keys():
            grouped[key][m].append(r[m])
        # variables para diversidad
        variable_sets.setdefault(key, []).append(list(r.get("variables", [])))
        # consistencia títulos (ya normalizados)
        title_consistency.setdefault(key, []).append(1 if r.get("title") == r.get("normalized_title") else 0)
        if r.get("penalty_applied"):
            penalty_counts[key] = penalty_counts.get(key, 0) + 1

    diversity_metrics: Dict[str, Dict[str, float]] = {}
    for variant, sets in variable_sets.items():
        mean_j, diversity = pairwise_jaccard(sets)
        diversity_metrics[variant] = {"mean_jaccard": mean_j, "diversity": diversity}

    title_consistency_ratio = {v: (sum(vals) / len(vals) if vals else 0.0) for v, vals in title_consistency.items()}

    print("\n=== A/B Hypothesis Generation Results (Extended) ===")
    
    # Log A/B test completion with trace correlation
    current_trace_id = get_current_trace_id()
    log_decision_event(
        event_type="ab_test_variant_completed",
        phase="hypothesis_generation",
        details={
            "variants_tested": list(grouped.keys()),
            "scenarios_count": len(SCENARIOS),
            "runs_per_scenario": RUNS_PER_SCENARIO,
            "total_results": len([r for r in results if not r.get("error")])
        },
        outcome="analysis_ready",
        trace_id=current_trace_id
    )
    
    for variant, metrics in grouped.items():
        print(f"\nVariant: {variant}")
        for metric, vals in metrics.items():
            if vals:
                print(f"  {metric}: mean={mean(vals):.3f} (n={len(vals)})")
        if variant in diversity_metrics:
            dm = diversity_metrics[variant]
            print(f"  mean_jaccard: {dm['mean_jaccard']:.3f} | diversity: {dm['diversity']:.3f}")
        if variant in title_consistency_ratio:
            print(f"  title_consistency: {title_consistency_ratio[variant]:.3f}")
        if penalty_counts.get(variant):
            print(f"  penalties_applied: {penalty_counts[variant]}")

    # Diferencias
    # Comparaciones clave
    def rel(a: float, b: float) -> float:
        if b == 0:
            return 0.0
        return (a - b) / b * 100.0

    comparisons = [
        ("registry_v1", "static"),
        ("registry_v2", "static"),
        ("registry_v2", "registry_v1"),
    ]
    print("\n--- Relative Improvements ---")
    for A, B in comparisons:
        if A not in grouped or B not in grouped:
            continue
        print(f"\n{A} vs {B}")
        for metric in ["title_len", "desc_len", "n_vars", "confidence", "elapsed"]:
            av = mean(grouped[A][metric]) if grouped[A][metric] else None
            bv = mean(grouped[B][metric]) if grouped[B][metric] else None
            if av is not None and bv is not None:
                delta = rel(av, bv)
                direction = "↑" if delta > 0 else "↓"
                print(f"  {metric}: {av:.3f} vs {bv:.3f} => {delta:+.2f}% {direction}")

    # Guardar JSON
    import json
    import datetime
    report = {
        "runs_per_scenario": RUNS_PER_SCENARIO,
        "scenarios": len(SCENARIOS),
        "metrics": {k: {m: (mean(v) if v else None) for m, v in val.items()} for k, val in grouped.items()},
        "diversity": diversity_metrics,
        "title_consistency": title_consistency_ratio,
        "penalties": penalty_counts,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "raw": results,
    }
    out_path = f"ab_hypothesis_report_{int(time.time())}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReporte guardado en {out_path}")

if __name__ == "__main__":
    asyncio.run(main())
