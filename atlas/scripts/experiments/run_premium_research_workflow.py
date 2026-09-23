"""Script para ejecutar un workflow científico real PREMIUM con modelos especializados 7B-8B
Gestión dinámica de memoria: carga/descarga automática de modelos según el rol activo.
Dominios expandidos: materials_science, drug_discovery, energy_storage, quantum_computing, biophysics, genomics, biomedical_engineering, neuroscience
Modelos especializados por rol: llama3:8b (orchestrator), mistral:7b (bio_hypothesis), codellama:7b (physchem_coder), qwen:7b (reviewer)

Uso:
    source .venv/bin/activate && python run_premium_research_workflow.py \
        --goal "Desarrollo de biomaterial inteligente para regeneración de tejido neuronal mediante nanopartículas funcionalizadas con factores de crecimiento" \
        --domains biophysics genomics biomedical_engineering neuroscience \
        --compile-latex
"""
from __future__ import annotations
import argparse
import asyncio
import json
from typing import List
import time

from app.services.multi_agent_coordinator import MultiAgentCoordinator


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--goal', required=True, help='Objetivo/pregunta de investigación complejo interdisciplinario')
    p.add_argument('--domains', nargs='+', 
                   default=['materials_science', 'drug_discovery', 'energy_storage', 'quantum_computing'], 
                   choices=['materials_science', 'drug_discovery', 'energy_storage', 'quantum_computing', 
                           'biophysics', 'genomics', 'biomedical_engineering', 'neuroscience'],
                   help='Lista de dominios soportados expandidos')
    p.add_argument('--compile-latex', action='store_true', help='Compilar PDF LaTeX si pdflatex disponible')
    return p.parse_args()


async def run_premium_workflow(goal: str, domains: List[str], compile_latex: bool):
    """Ejecuta workflow premium con gestión dinámica de modelos especializados"""
    print("\n🚀 AXIOM META 4 - Workflow Científico PREMIUM")
    print("=" * 80)
    print(f"📋 Objetivo: {goal}")
    print(f"🔬 Dominios: {', '.join(domains)}")
    print("🤖 Modelos especializados por rol:")
    print("   - Orchestrator: llama3:8b (planificación)")
    print("   - Bio Hypothesis: mistral:7b (hipótesis biológicas)")  
    print("   - PhysChem Coder: codellama:7b (código físico-químico)")
    print("   - Reviewer: qwen:7b (peer review)")
    print("   - Publisher: llama3:8b (redacción científica)")
    print("💾 Gestión dinámica de memoria: carga/descarga automática")
    print("🛠️ Herramientas expandidas: >20 servicios científicos")
    print("=" * 80)
    
    coord = MultiAgentCoordinator()
    results = []
    start_time = time.time()
    
    for i, domain in enumerate(domains):
        domain_start = time.time()
        print(f"\n{'🧪' * 3} DOMINIO {i+1}/{len(domains)}: {domain.upper()} {'🧪' * 3}")
        print("-" * 70)
        
        try:
            r = await coord.run_pipeline_integrated_async(goal, domain=domain, compile_latex=compile_latex)
            domain_time = time.time() - domain_start
            
            if not r.get('success'):
                print(f"❌ [ERROR dominio {domain}] {r.get('error')}")
                results.append({
                    "domain": domain, 
                    "success": False, 
                    "error": r.get('error'),
                    "duration_seconds": domain_time
                })
                continue
                
            art = r['artifact']
            paper = art.get('paper_paths', {})
            summary = art.get('evidence', {}).get('summary', {})
            
            # Mostrar métricas detalladas
            print("📊 MÉTRICAS DE EVIDENCIA CIENTÍFICA:")
            print(f"   🎯 Support Score: {summary.get('support_score', 'N/A'):.3f}")
            print(f"   📈 Coverage: {summary.get('coverage', 'N/A'):.3f}")
            print(f"   ⚖️ Weighted Coverage: {summary.get('weighted_coverage', 'N/A'):.3f}")
            print(f"   🌈 Diversity: {summary.get('diversity', 'N/A'):.3f}")
            print(f"   ❌ Failures: {summary.get('failures', 'N/A')}")
            
            # Mostrar revisión cuantitativa
            try:
                review = json.loads(art.get('review', '{}')) if isinstance(art.get('review'), str) else art.get('review', {})
                evidence_composite = review.get('evidence_composite', 'N/A')
                verdict_quant = review.get('verdict_quantitative', 'N/A')
                
                verdict_emoji = {"approve": "✅", "revise": "🔄", "reject": "❌"}.get(verdict_quant, "❓")
                print(f"   🏆 Evidence Composite: {evidence_composite:.3f}" if isinstance(evidence_composite, (int, float)) else f"   🏆 Evidence Composite: {evidence_composite}")
                print(f"   {verdict_emoji} Verdict: {verdict_quant.upper()}")
            except Exception:
                print("   📝 Review: (formato no estándar)")
            
            print(f"⏱️ Tiempo de procesamiento: {domain_time:.1f}s")
            print("📄 Artefactos generados:")
            print(f"   📝 Paper Markdown: {paper.get('markdown', 'N/A')}")
            print(f"   📊 Paper LaTeX: {paper.get('latex', 'N/A')}")
            
            results.append({
                "domain": domain, 
                "duration_seconds": domain_time,
                **r
            })
            
        except Exception as e:
            domain_time = time.time() - domain_start
            print(f"💥 [EXCEPCIÓN dominio {domain}] {str(e)}")
            results.append({
                "domain": domain, 
                "success": False, 
                "error": str(e),
                "duration_seconds": domain_time
            })
    
    total_time = time.time() - start_time
    
    # Agregación avanzada
    print(f"\n{'📈' * 3} ANÁLISIS GLOBAL AGREGADO {'📈' * 3}")
    print("=" * 80)
    
    agg = {
        "support_score": [], 
        "coverage": [], 
        "weighted_coverage": [], 
        "diversity": [], 
        "evidence_composite": [],
        "processing_times": []
    }
    successful_domains = []
    verdict_counts = {"approve": 0, "revise": 0, "reject": 0}
    
    for r in results:
        if not r.get('success'): 
            continue
        successful_domains.append(r['domain'])
        agg["processing_times"].append(r.get('duration_seconds', 0))
        
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
                    
                    verdict = parsed_review.get('verdict_quantitative')
                    if verdict in verdict_counts:
                        verdict_counts[verdict] += 1
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
                'std': round(statistics.stdev(vals) if len(vals) > 1 else 0.0, 4),
                'count': len(vals)
            }
    
    print(f"✅ Dominios exitosos: {len(successful_domains)}/{len(domains)}")
    print(f"⏱️ Tiempo total: {total_time:.1f}s")
    if successful_domains:
        print("📊 Métricas científicas agregadas:")
        for metric, stats in agg_stats.items():
            if metric != 'processing_times':
                print(f"   {metric}:")
                print(f"      📈 Mean: {stats['mean']} | 🔺 Max: {stats['max']} | 🔻 Min: {stats['min']} | 📊 Std: {stats['std']}")
        
        print("⏱️ Performance:")
        pstats = agg_stats.get('processing_times', {})
        if pstats:
            print(f"   Tiempo por dominio: {pstats['mean']:.1f}s promedio | {pstats['max']:.1f}s máximo | {pstats['min']:.1f}s mínimo")
        
        print("🏆 Veredictos peer review:")
        for verdict, count in verdict_counts.items():
            emoji = {"approve": "✅", "revise": "🔄", "reject": "❌"}[verdict]
            print(f"   {emoji} {verdict.capitalize()}: {count} papers")
    
    return {
        "results": results, 
        "aggregate": agg_stats, 
        "successful_domains": successful_domains,
        "total_processing_time": total_time,
        "verdict_distribution": verdict_counts
    }


def main():
    args = parse_args()
    result = asyncio.run(run_premium_workflow(args.goal, args.domains, args.compile_latex))
    
    print(f"\n{'🎯' * 3} RESUMEN EJECUTIVO {'🎯' * 3}")
    print("=" * 80)
    print(f"   🔬 Dominios procesados: {len(args.domains)}")
    print(f"   ✅ Dominios exitosos: {len(result['successful_domains'])}")
    print(f"   📄 Papers científicos generados: {len([r for r in result['results'] if r.get('success')])}")
    print(f"   ⏱️ Tiempo total de investigación: {result['total_processing_time']:.1f} segundos")
    print(f"   🧮 Métricas disponibles: {list(result['aggregate'].keys())}")
    print(f"   🏆 Distribución veredictos: {result['verdict_distribution']}")
    print("=" * 80)


if __name__ == '__main__':
    main()
