#!/usr/bin/env python3
"""
Batch Tool Validation Runner
----------------------------
Ejecuta corroboración de herramientas para múltiples dominios e hipótesis generadas
(sintéticas si no existen) usando el ScientificHypothesisAgent + ToolEvidenceOrchestrator.

Salida:
  - JSONL en logs/mass_validation/mass_tool_validation_<fecha>.jsonl
  - Resumen agregado en stdout

Uso (desde raíz):
  python scripts/run_mass_tool_validation.py
"""
from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
import asyncio
from typing import List, Dict, Any

# Importaciones relativas dinámicas
from app.services.scientific_hypothesis_agent import ScientificHypothesisAgent

OUTPUT_DIR = Path("logs/mass_validation")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DOMAINS = [
    "materials_science", "mathematics", "physics", "chemistry", "biology", "plasma_physics", "medical_imaging"
]

# Preguntas base sintéticas por dominio
RESEARCH_QUESTIONS = {
    "materials_science": "How can dopant distribution affect thermal conductivity in layered materials?",
    "mathematics": "What transformation improves numerical stability in polynomial root finding?",
    "physics": "How does confinement modify energy distribution in quasi-2D systems?",
    "chemistry": "How do catalyst support interactions influence reaction selectivity?",
    "biology": "What factors modulate CRISPR editing efficiency in mammalian cells?",
    "plasma_physics": "How does magnetic field topology influence confinement stability?",
    "medical_imaging": "Can adaptive thresholding improve cardiac chamber segmentation consistency?",
}

async def generate_or_get_hypothesis(agent: ScientificHypothesisAgent, domain: str) -> str:
    rq = RESEARCH_QUESTIONS[domain]
    r = await agent.process_request({
        "action": "generate_hypothesis",
        "domain": domain if domain in agent.domain_knowledge else "materials_science",
        "research_question": rq,
        "context_data": {"auto": True}
    })
    if not r.get("success"):
        raise RuntimeError(f"No se pudo generar hipótesis para {domain}: {r}")
    return r["hypothesis_id"]

async def corroborate(agent: ScientificHypothesisAgent, hypothesis_id: str) -> Dict[str, Any]:
    return await agent.process_request({
        "action": "corroborate_with_tools",
        "hypothesis_id": hypothesis_id
    })

async def main():
    agent = ScientificHypothesisAgent()
    summary: List[Dict[str, Any]] = []
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = OUTPUT_DIR / f"mass_tool_validation_{ts_str}.jsonl"

    for domain in DOMAINS:
        try:
            hyp_id = await generate_or_get_hypothesis(agent, domain)
            corr = await corroborate(agent, hyp_id)
            record = {
                "timestamp": datetime.now().isoformat(),
                "domain": domain,
                "hypothesis_id": hyp_id,
                "support_score": corr.get("aggregate", {}).get("support_score"),
                "coverage": corr.get("aggregate", {}).get("coverage"),
                "mean_signal": corr.get("aggregate", {}).get("mean_signal"),
                "evidence_items": corr.get("evidence_items", []),
                "new_confidence": corr.get("new_confidence")
            }
            summary.append(record)
            with open(out_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            print(f"✅ {domain}: support={record['support_score']} coverage={record['coverage']} confidence={record['new_confidence']}")
        except Exception as e:
            err_record = {"timestamp": datetime.now().isoformat(), "domain": domain, "error": str(e)}
            with open(out_file, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(err_record, ensure_ascii=False) + "\n")
            print(f"❌ {domain}: {e}")

    # Resumen agregado
    ok = [s for s in summary if s.get("support_score") is not None]
    if ok:
        avg_support = sum(s["support_score"] for s in ok) / len(ok)
        avg_cov = sum(s["coverage"] for s in ok) / len(ok)
        print("\n=== RESUMEN GLOBAL ===")
        print(f"Dominios procesados: {len(DOMAINS)} exitosos: {len(ok)}")
        print(f"Promedio soporte: {avg_support:.3f}  | Promedio cobertura: {avg_cov:.3f}")

if __name__ == "__main__":
    asyncio.run(main())
