#!/usr/bin/env python3
"""
Investigación de estabilidad en MaterialsLoop
Ejecuta múltiples iteraciones para identificar variabilidad en support_score
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Añadir app al path
sys.path.insert(0, str(Path(__file__).parent))

from app.autonomous.pipelines.materials_loop import MaterialsLoop


async def run_materials_iteration(iteration: int):
    """Ejecuta una iteración de MaterialsLoop y extrae métricas"""
    print(f"\n{'='*60}")
    print(f"🔬 ITERACIÓN {iteration + 1}")
    print(f"{'='*60}")
    
    try:
        loop = MaterialsLoop()
        results = loop.run_iteration(iteration=iteration)
        
        # Extraer métricas clave
        metrics = {
            "iteration": iteration + 1,
            "timestamp": datetime.now().isoformat(),
            "num_candidates": len(results.get("candidates", [])),
            "support_scores": [],
            "execution_details": {}
        }
        
        # Analizar cada candidato
        for idx, candidate in enumerate(results.get("candidates", [])):
            score = candidate.get("support_score", 0.0)
            metrics["support_scores"].append(score)
            
            print(f"  Candidato {idx+1}:")
            print(f"    - Formula: {candidate.get('formula', 'N/A')}")
            print(f"    - Support Score: {score:.4f}")
            print(f"    - Evidence Sources: {len(candidate.get('evidence_summary', {}).get('sources', []))}")
        
        # Calcular estadísticas
        if metrics["support_scores"]:
            avg_score = sum(metrics["support_scores"]) / len(metrics["support_scores"])
            max_score = max(metrics["support_scores"])
            min_score = min(metrics["support_scores"])
            
            metrics["statistics"] = {
                "average": avg_score,
                "max": max_score,
                "min": min_score,
                "range": max_score - min_score
            }
            
            print(f"\n  📊 Estadísticas:")
            print(f"    - Promedio: {avg_score:.4f}")
            print(f"    - Máximo: {max_score:.4f}")
            print(f"    - Mínimo: {min_score:.4f}")
            print(f"    - Rango: {max_score - min_score:.4f}")
        
        # Guardar resultados completos
        metrics["full_results"] = results
        
        return metrics
        
    except Exception as e:
        print(f"  ❌ Error en iteración {iteration + 1}: {e}")
        import traceback
        traceback.print_exc()
        return {
            "iteration": iteration + 1,
            "error": str(e),
            "traceback": traceback.format_exc()
        }


async def main():
    """Ejecuta múltiples iteraciones y analiza variabilidad"""
    
    NUM_ITERATIONS = 5
    
    print("🚀 INICIANDO INVESTIGACIÓN DE ESTABILIDAD - MaterialsLoop")
    print(f"Iteraciones: {NUM_ITERATIONS}")
    
    all_metrics = []
    
    # Ejecutar iteraciones
    for i in range(NUM_ITERATIONS):
        metrics = await run_materials_iteration(i)
        all_metrics.append(metrics)
        
        # Pequeña pausa entre iteraciones
        if i < NUM_ITERATIONS - 1:
            await asyncio.sleep(2)
    
    # Análisis de variabilidad
    print(f"\n{'='*60}")
    print("📊 ANÁLISIS DE VARIABILIDAD")
    print(f"{'='*60}")
    
    # Extraer todos los scores promedio
    avg_scores = []
    for m in all_metrics:
        if "statistics" in m:
            avg_scores.append(m["statistics"]["average"])
    
    if avg_scores:
        global_avg = sum(avg_scores) / len(avg_scores)
        global_max = max(avg_scores)
        global_min = min(avg_scores)
        global_std = (sum((x - global_avg)**2 for x in avg_scores) / len(avg_scores)) ** 0.5
        
        print(f"\n🎯 Resultados globales ({len(avg_scores)} iteraciones exitosas):")
        print(f"  - Promedio global: {global_avg:.4f}")
        print(f"  - Máximo: {global_max:.4f}")
        print(f"  - Mínimo: {global_min:.4f}")
        print(f"  - Desviación estándar: {global_std:.4f}")
        print(f"  - Variabilidad (CV): {(global_std/global_avg)*100:.2f}%")
        
        # Clasificar estabilidad
        cv = (global_std/global_avg)*100
        if cv < 5:
            stability = "EXCELENTE ✅"
        elif cv < 10:
            stability = "BUENA ✅"
        elif cv < 20:
            stability = "MODERADA ⚠️"
        else:
            stability = "BAJA ❌"
        
        print(f"\n  🔍 Estabilidad: {stability}")
        
        # Guardar resultados
        summary = {
            "analysis_date": datetime.now().isoformat(),
            "num_iterations": NUM_ITERATIONS,
            "successful_iterations": len(avg_scores),
            "global_statistics": {
                "average": global_avg,
                "max": global_max,
                "min": global_min,
                "std_dev": global_std,
                "coefficient_variation": cv,
                "stability_rating": stability
            },
            "iteration_details": all_metrics
        }
        
        output_file = f"materials_stability_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Resultados guardados en: {output_file}")
        
        # Recomendaciones
        print(f"\n{'='*60}")
        print("💡 RECOMENDACIONES")
        print(f"{'='*60}")
        
        if cv < 10:
            print("✅ MaterialsLoop muestra estabilidad aceptable")
            print("   No se requieren cambios inmediatos")
        elif cv < 20:
            print("⚠️ MaterialsLoop tiene variabilidad moderada")
            print("   Recomendaciones:")
            print("   - Revisar servicios de evidencia para consistency")
            print("   - Verificar que la generación de candidatos sea determinista")
        else:
            print("❌ MaterialsLoop tiene alta variabilidad")
            print("   Acciones requeridas:")
            print("   - Investigar fuentes de aleatoriedad en scoring")
            print("   - Revisar configuración de servicios externos")
            print("   - Considerar semilla fija para generación de candidatos")
    
    else:
        print("❌ No se obtuvieron resultados válidos en ninguna iteración")
    
    print(f"\n{'='*60}")
    print("✅ INVESTIGACIÓN COMPLETADA")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
