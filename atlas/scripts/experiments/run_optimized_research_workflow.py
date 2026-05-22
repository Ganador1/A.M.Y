"""Script para ejecutar workflow científico OPTIMIZADO con manejo de errores y rate limiting
Focalizado en calidad sobre cantidad de herramientas, con gestión de errores robusta.
"""
from __future__ import annotations
import argparse
import asyncio
import json
import time
import random

from app.services.multi_agent_coordinator import MultiAgentCoordinator


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--goal', required=True, help='Objetivo de investigación')
    p.add_argument('--domain', 
                   default='biomedical_engineering', 
                   choices=['materials_science', 'drug_discovery', 'energy_storage', 'quantum_computing', 
                           'biophysics', 'genomics', 'biomedical_engineering', 'neuroscience'],
                   help='Dominio científico individual')
    p.add_argument('--tools-limit', type=int, default=5, help='Límite de herramientas por ejecución')
    p.add_argument('--retry-delay', type=float, default=2.0, help='Delay entre reintentos en segundos')
    p.add_argument('--compile-latex', action='store_true', help='Compilar PDF LaTeX')
    return p.parse_args()


async def run_optimized_workflow(goal: str, domain: str, tools_limit: int, retry_delay: float, compile_latex: bool):
    """Ejecuta workflow optimizado con un solo dominio pero máxima calidad"""
    print("\n🎯 AXIOM META 4 - Workflow Científico OPTIMIZADO")
    print("=" * 80)
    print(f"📋 Objetivo: {goal}")
    print(f"🔬 Dominio enfocado: {domain}")
    print(f"⚙️ Límite de herramientas: {tools_limit}")
    print(f"⏰ Delay entre reintentos: {retry_delay}s")
    print("🤖 Modelos especializados por rol:")
    print("   - Orchestrator: llama3:8b")
    print("   - Bio Hypothesis: mistral:7b") 
    print("   - PhysChem Coder: codellama:7b")
    print("   - Reviewer: qwen:7b")
    print("   - Publisher: llama3:8b")
    print("💾 Gestión dinámica de memoria activada")
    print("🛠️ Herramientas: optimizadas con rate limiting")
    print("=" * 80)
    
    coord = MultiAgentCoordinator()
    start_time = time.time()
    
    # Agregar delay aleatorio inicial para evitar race conditions
    delay = random.uniform(0.5, 2.0)
    print(f"⏳ Delay inicial aleatorio: {delay:.1f}s")
    await asyncio.sleep(delay)
    
    print(f"\n🚀 EJECUTANDO DOMINIO: {domain.upper()}")
    print("-" * 50)
    
    try:
        result = await coord.run_pipeline_integrated_async(
            goal, 
            domain=domain, 
            compile_latex=compile_latex
        )
        
        duration = time.time() - start_time
        
        if not result.get('success'):
            print(f"❌ [ERROR] {result.get('error')}")
            return {"success": False, "error": result.get('error'), "duration": duration}
        
        art = result['artifact']
        paper = art.get('paper_paths', {})
        summary = art.get('evidence', {}).get('summary', {})
        
        print("\n📊 ANÁLISIS DE CALIDAD CIENTÍFICA:")
        print("-" * 40)
        
        # Mostrar métricas con mejor formato
        metrics = {
            '🎯 Support Score': summary.get('support_score', 'N/A'),
            '📈 Coverage': summary.get('coverage', 'N/A'),
            '⚖️ Weighted Coverage': summary.get('weighted_coverage', 'N/A'),
            '🌈 Diversity': summary.get('diversity', 'N/A'),
            '❌ Failures': summary.get('failures', 'N/A')
        }
        
        for name, value in metrics.items():
            if isinstance(value, (int, float)):
                color = "🟢" if value > 0.7 else "🟡" if value > 0.3 else "🔴"
                print(f"   {name}: {color} {value:.3f}")
            else:
                print(f"   {name}: ⚪ {value}")
        
        # Análisis del review
        evidence_composite = 'N/A'
        verdict_quant = 'N/A'
        try:
            review = json.loads(art.get('review', '{}')) if isinstance(art.get('review'), str) else art.get('review', {})
            evidence_composite = review.get('evidence_composite', 'N/A')
            verdict_quant = review.get('verdict_quantitative', 'N/A')
            
            verdict_colors = {"approve": "🟢", "revise": "🟡", "reject": "🔴"}
            verdict_emoji = {"approve": "✅", "revise": "🔄", "reject": "❌"}
            
            color = verdict_colors.get(verdict_quant, "⚪")
            emoji = verdict_emoji.get(verdict_quant, "❓")
            
            print("\n🏆 PEER REVIEW QUANTITATIVO:")
            if isinstance(evidence_composite, (int, float)):
                comp_color = "🟢" if evidence_composite > 0.7 else "🟡" if evidence_composite > 0.3 else "🔴"
                print(f"   Evidence Composite: {comp_color} {evidence_composite:.3f}")
            else:
                print(f"   Evidence Composite: ⚪ {evidence_composite}")
            print(f"   Verdict Final: {color} {emoji} {verdict_quant.upper()}")
            
        except Exception:
            print("   📝 Review: ⚠️ (formato no procesable)")
        
        # Métricas de herramientas
        tool_calls = art.get('evidence', {}).get('tool_calls', [])
        successful_tools = len([tc for tc in tool_calls if tc.get('success', False)])
        total_tools = len(tool_calls)
        
        print("\n🛠️ ANÁLISIS DE HERRAMIENTAS:")
        if total_tools > 0:
            success_rate = successful_tools / total_tools
            rate_color = "🟢" if success_rate > 0.8 else "🟡" if success_rate > 0.5 else "🔴"
            print(f"   Herramientas ejecutadas: {rate_color} {successful_tools}/{total_tools} ({success_rate:.1%} éxito)")
            
            # Mostrar herramientas más exitosas
            if tool_calls:
                successful_names = [tc.get('tool_name', 'unknown') for tc in tool_calls if tc.get('success', False)]
                if successful_names:
                    print(f"   Herramientas exitosas: {', '.join(set(successful_names))}")
        else:
            print("   Herramientas ejecutadas: 🔴 0/0 (sin herramientas)")
        
        print("\n📄 ARTEFACTOS GENERADOS:")
        print(f"   📝 Paper Markdown: {paper.get('markdown', 'N/A')}")
        print(f"   📊 Paper LaTeX: {paper.get('latex', 'N/A')}")
        print(f"   ⏱️ Tiempo total: {duration:.1f}s")
        
        return {
            "success": True,
            "domain": domain,
            "duration": duration,
            "metrics": metrics,
            "evidence_composite": evidence_composite,
            "verdict": verdict_quant,
            "tools_success_rate": successful_tools / total_tools if total_tools > 0 else 0,
            "tools_executed": total_tools,
            "paper_paths": paper
        }
        
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 [EXCEPCIÓN] {str(e)}")
        return {"success": False, "error": str(e), "duration": duration}


def main():
    args = parse_args()
    result = asyncio.run(run_optimized_workflow(
        args.goal, 
        args.domain, 
        args.tools_limit,
        args.retry_delay,
        args.compile_latex
    ))
    
    print("\n🎯 RESUMEN EJECUTIVO OPTIMIZADO")
    print("=" * 50)
    
    if result.get('success'):
        print(f"   ✅ Dominio: {result['domain']}")
        print(f"   ⏱️ Duración: {result['duration']:.1f}s")
        print(f"   🛠️ Herramientas: {result.get('tools_executed', 0)} ejecutadas")
        print(f"   📊 Tasa de éxito herramientas: {result.get('tools_success_rate', 0):.1%}")
        print(f"   🏆 Verdict: {result.get('verdict', 'N/A').upper()}")
        print(f"   📄 Papers generados: {'✅' if result.get('paper_paths') else '❌'}")
    else:
        print(f"   ❌ Error: {result.get('error', 'Unknown')}")
        print(f"   ⏱️ Duración: {result.get('duration', 0):.1f}s")
    
    print("=" * 50)


if __name__ == '__main__':
    main()
