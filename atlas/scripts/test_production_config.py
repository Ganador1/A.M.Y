#!/usr/bin/env python3
"""
Test de configuración de producción: hf_frontier_reflect
Ejecuta un ciclo completo de investigación y analiza los resultados
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.research_cycle_manager import ResearchCycleManager


async def main():
    print("🚀 TESTING PRODUCTION CONFIG: hf_frontier_reflect")
    print("=" * 80)
    print("Modelos configurados:")
    print("  orchestrator:   meta-llama/Meta-Llama-3.1-405B-Instruct (405B)")
    print("  bio_hypothesis: Qwen/Qwen2.5-72B-Instruct (72B)")
    print("  physchem_coder: Qwen/Qwen2.5-Coder-32B-Instruct (32B)")
    print("  reviewer:       DeepSeek-R1-Distill-Qwen-32B (32B)")
    print("  publisher:      meta-llama/Meta-Llama-3.1-405B-Instruct (405B)")
    print("=" * 80)
    print()
    
    # Inicializar manager
    manager = ResearchCycleManager()
    
    # Objetivo de investigación
    user_goal = "Investigar aplicaciones de entrelazamiento cuántico en computación distribuida para mejorar protocolos de consenso bizantino"
    
    print(f"🎯 Objetivo: {user_goal}")
    print("\n📝 Ejecutando ciclo completo de investigación autónoma...")
    print("-" * 80)
    
    # Ejecutar ciclo
    try:
        request_data = {
            "user_goal": user_goal,
            "research_domain": "quantum_physics",
            "max_iterations": 3
        }
        result = await manager.start_research_cycle(request_data)
        
        print("\n" + "=" * 80)
        print("✅ CICLO COMPLETADO EXITOSAMENTE")
        print("=" * 80)
        
        # Guardar resultado completo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"production_cycle_{timestamp}.json"
        
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Resultado completo guardado en: {output_file}")
        
        # Extraer y mostrar información clave
        print("\n" + "=" * 80)
        print("📊 ANÁLISIS DE RESULTADOS")
        print("=" * 80)
        
        # Hipótesis generada
        if "hypothesis" in result:
            print("\n🔬 HIPÓTESIS GENERADA:")
            print("-" * 80)
            hypothesis = result["hypothesis"]
            if isinstance(hypothesis, dict):
                print(f"Título: {hypothesis.get('title', 'N/A')}")
                print(f"Descripción: {hypothesis.get('description', 'N/A')[:500]}...")
            else:
                print(f"{hypothesis[:500]}...")
            
            # Guardar hipótesis en archivo separado
            hypothesis_file = f"hypothesis_{timestamp}.json"
            with open(hypothesis_file, "w", encoding="utf-8") as f:
                json.dump(hypothesis, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Hipótesis guardada en: {hypothesis_file}")
        
        # Paper final
        if "final_report" in result or "paper" in result:
            print("\n📄 PAPER FINAL GENERADO:")
            print("-" * 80)
            paper = result.get("final_report") or result.get("paper")
            if isinstance(paper, dict):
                print(f"Título: {paper.get('title', 'N/A')}")
                print(f"Abstract: {paper.get('abstract', 'N/A')[:500]}...")
            else:
                print(f"{str(paper)[:500]}...")
            
            # Guardar paper en archivo separado
            paper_file = f"paper_{timestamp}.json"
            with open(paper_file, "w", encoding="utf-8") as f:
                json.dump(paper, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Paper guardado en: {paper_file}")
        
        # Estadísticas del ciclo
        print("\n📈 ESTADÍSTICAS DEL CICLO:")
        print("-" * 80)
        if "metadata" in result:
            metadata = result["metadata"]
            print(f"Duración total: {metadata.get('duration', 'N/A')}s")
            print(f"Agentes ejecutados: {metadata.get('agents_executed', 'N/A')}")
            print(f"Iteraciones: {metadata.get('iterations', 'N/A')}")
        
        if "scores" in result:
            scores = result["scores"]
            print(f"\n🎯 Scores:")
            for key, value in scores.items():
                print(f"  {key}: {value}")
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISIS COMPLETADO")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR durante la ejecución: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n🎉 Test de producción completado exitosamente!")
        sys.exit(0)
    else:
        print("\n⚠️ Test de producción falló")
        sys.exit(1)
