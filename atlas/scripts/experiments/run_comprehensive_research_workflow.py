"""Script para ejecutar un workflow científico real multi-dominio COMPLETO
Usa todos los modelos especializados correctos y todas las herramientas disponibles.
Dominios soportados: materials_science, drug_discovery, energy_storage, quantum_computing
Uso:
    source .venv/bin/activate && python run_comprehensive_research_workflow.py \
        --goal "Optimizar eficiencia de conversión fotocatalítica en nanomaterial TiO2 dopado con dopantes metálicos para aplicaciones de energía limpia" \
        --domains materials_science energy_storage quantum_computing \
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
    p.add_argument('--goal', required=True, help='Objetivo/ pregunta de investigación complejo')
    p.add_argument('--domains', nargs='+', 
                   default=['materials_science', 'drug_discovery', 'energy_storage', 'quantum_computing'], 
                   choices=['materials_science', 'drug_discovery', 'energy_storage', 'quantum_computing'],
                   help='Lista de dominios soportados a ejecutar')
    p.add_argument('--compile-latex', action='store_true', help='Compilar PDF LaTeX si pdflatex disponible')
    return p.parse_args()


async def run_comprehensive(goal: str, domains: List[str], compile_latex: bool):
    """Ejecuta workflow completo con todos los modelos especializados y herramientas expandidas"""
    print("\n🚀 AXIOM META 4 - Workflow Científico Completo")
    print(f"📋 Objetivo: {goal}")
    print(f"🔬 Dominios: {', '.join(domains)}")
    print("🤖 Modelos activos: falcon3:3b, qwen2.5:1.5b, deepseek-r1:1.5b")
    print("🛠️ Herramientas: GNOME Materials, DNABERT2, PyTorch, SciPy, LangChain, Biomecánica, etc.")
    
    coord = MultiAgentCoordinator()
    results = []
    
    for i, domain in enumerate(domains):
        print(f"\n{'='*60}")
        print(f"🧪 Ejecutando dominio {i+1}/{len(domains)}: {domain}")
        print(f"{'='*60}")
        
        try:
            r = await coord.run_pipeline_integrated_async(goal, domain=domain, compile_latex=compile_latex)
            if not r.get('success'):
                print(f"❌ [ERROR dominio {domain}] {r.get('error')}")
                results.append({"domain": domain, "success": False, "error": r.get('error')})
                continue
                
            art = r['artifact']
            paper = art.get('paper_paths', {})
            summary = art.get('evidence', {}).get('summary', {})
            
            # Mostrar métricas de evidencia
            print(f"📊 Métricas de evidencia para {domain}:")
            print(f"   - support_score: {summary.get('support_score', 'N/A')}")
            print(f"   - coverage: {summary.get('coverage', 'N/A')}")
            print(f"   - weighted_coverage: {summary.get('weighted_coverage', 'N/A')}")
            print(f"   - diversity: {summary.get('diversity', 'N/A')}")
            print(f"   - failures: {summary.get('failures', 'N/A')}")
            
            # Mostrar revisión cuantitativa
            try:
                review = json.loads(art.get('review', '{}')) if isinstance(art.get('review'), str) else art.get('review', {})
                evidence_composite = review.get('evidence_composite', 'N/A')
                verdict_quant = review.get('verdict_quantitative', 'N/A')
                print(f"   - evidence_composite: {evidence_composite}")
                print(f"   - verdict_quantitative: {verdict_quant}")
            except Exception:
                print("   - review: (formato no JSON)")
            
            print("📄 Artefactos generados:")
            print(f"   - Paper Markdown: {paper.get('markdown', 'N/A')}")
            print(f"   - Paper LaTeX: {paper.get('latex', 'N/A')}")
            
            results.append({"domain": domain, **r})
            
        except Exception as e:
            print(f"❌ [EXCEPCIÓN dominio {domain}] {str(e)}")
            results.append({"domain": domain, "success": False, "error": str(e)})
    
    # Agregación final mejorada
    print(f"\n{'='*60}")
    print("📈 AGREGACIÓN GLOBAL DE MÉTRICAS")
    print(f"{'='*60}")
    
    agg = {"support_score": [], "coverage": [], "weighted_coverage": [], "diversity": [], "evidence_composite": []}
    successful_domains = []
    
    for r in results:
        if not r.get('success'): 
            continue
        successful_domains.append(r['domain'])
        
        try:
            summ = r.get('artifact', {}).get('evidence', {}).get('summary', {})
            for k in ['support_score', 'coverage', 'weighted_coverage', 'diversity']:
                v = summ.get(k)
                if isinstance(v, (int, float)):
                    agg[k].append(v)
            
            # Agregar evidence_composite del review
            review = r.get('artifact', {}).get('review', '{}')
            if isinstance(review, str):
                try:
                    parsed_review = json.loads(review)
                    ec = parsed_review.get('evidence_composite')
                    if isinstance(ec, (int, float)):
                        agg['evidence_composite'].append(ec)
                except Exception:
                    pass
        except Exception:
            pass
    
    import statistics
    agg_stats = {}
    for k, vals in agg.items():
        if vals:
            agg_stats[k] = {
                'mean': round(statistics.mean(vals), 4),
                'max': round(max(vals), 4),
                'min': round(min(vals), 4),
                'count': len(vals)
            }
    
    print(f"✅ Dominios exitosos: {len(successful_domains)}/{len(domains)}")
    print("📊 Métricas agregadas:")
    for metric, stats in agg_stats.items():
        print(f"   {metric}:")
        print(f"      - mean: {stats['mean']} | max: {stats['max']} | min: {stats['min']} | count: {stats['count']}")
    
    return {"results": results, "aggregate": agg_stats, "successful_domains": successful_domains}


def main():
    args = parse_args()
    result = asyncio.run(run_comprehensive(args.goal, args.domains, args.compile_latex))
    
    print("\n🎯 RESUMEN FINAL:")
    print(f"   - Dominios procesados: {len(args.domains)}")
    print(f"   - Dominios exitosos: {len(result['successful_domains'])}")
    print(f"   - Papers generados: {len([r for r in result['results'] if r.get('success')])}")
    print(f"   - Aggregate metrics keys: {list(result['aggregate'].keys())}")


if __name__ == '__main__':
    main()
