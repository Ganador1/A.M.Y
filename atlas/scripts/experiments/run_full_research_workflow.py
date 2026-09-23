"""Script para ejecutar un workflow científico real multi-dominio
Genera artefactos y papers Markdown/LaTeX por dominio.
Uso rápido:
    source .venv/bin/activate && python run_full_research_workflow.py \
        --goal "Optimizar eficiencia de conversión fotocatalítica en nanomaterial TiO2 dopado" \
        --domains materials_science biophysics genomics \
        --compile-latex
"""
from __future__ import annotations
import argparse
import asyncio
import json
from typing import List

from app.services.multi_agent_coordinator import MultiAgentCoordinator


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--goal', required=True, help='Objetivo/ pregunta de investigación')
    p.add_argument('--domains', nargs='+', default=['materials_science'], help='Lista de dominios a ejecutar')
    p.add_argument('--compile-latex', action='store_true', help='Compilar PDF LaTeX si pdflatex disponible')
    return p.parse_args()


async def run(goal: str, domains: List[str], compile_latex: bool):
    coord = MultiAgentCoordinator()
    results = []
    for d in domains:
        print(f"\n=== Ejecutando dominio: {d} ===")
        r = await coord.run_pipeline_integrated_async(goal, domain=d, compile_latex=compile_latex)
        if not r.get('success'):
            print(f"[ERROR dominio {d}] {r.get('error')}")
        else:
            art = r['artifact']
            paper = art.get('paper_paths', {})
            summary = art.get('evidence', {}).get('summary', {})
            print(f"Dominio {d} métricas: {json.dumps(summary, ensure_ascii=False)}")
            print(f"Paper MD: {paper.get('markdown')} | LaTeX: {paper.get('latex')}")
        results.append({"domain": d, **r})
    # Agregación simple
    agg = {"support_score": [], "weighted_coverage": [], "diversity": []}
    for r in results:
        if not r.get('success'):
            continue
        summ = r.get('artifact', {}).get('evidence', {}).get('summary', {})
        for k in agg:
            v = summ.get(k)
            if isinstance(v, (int, float)):
                agg[k].append(v)
    import statistics
    agg_stats = {}
    for k, vals in agg.items():
        if vals:
            agg_stats[k] = {
                'mean': statistics.mean(vals),
                'max': max(vals),
                'min': min(vals)
            }
    print("\n=== Agregación Global ===")
    print(json.dumps(agg_stats, indent=2, ensure_ascii=False))
    return {"results": results, "aggregate": agg_stats}


def main():
    args = parse_args()
    asyncio.run(run(args.goal, args.domains, args.compile_latex))


if __name__ == '__main__':
    main()
