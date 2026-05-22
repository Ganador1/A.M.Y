#!/usr/bin/env python3
"""
Investigación simple de estabilidad en MaterialsLoop
Ejecuta run_loops_isolated múltiples veces y analiza variación del support_score
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def run_isolated_loops() -> Dict:
    """Ejecuta run_loops_isolated.py y retorna los resultados"""
    try:
        result = subprocess.run(
            [sys.executable, "run_loops_isolated.py"],
            capture_output=True,
            text=True,
            timeout=600,
            cwd=Path(__file__).parent
        )
        
        # Buscar el archivo de resultados más reciente
        result_files = list(Path(".").glob("isolated_loops_results_*.json"))
        if not result_files:
            return {"error": "No result file found"}
        
        latest_file = max(result_files, key=lambda p: p.stat().st_mtime)
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except subprocess.TimeoutExpired:
        return {"error": "Execution timeout"}
    except Exception as e:
        return {"error": str(e)}


def extract_materials_score(results: Dict) -> float:
    """Extrae el support score de MaterialsLoop"""
    for loop in results.get("loops", []):
        if loop.get("loop_name") == "MaterialsLoop":
            parsed = loop.get("parsed_summary", {})
            return parsed.get("support_score", 0.0)
    return 0.0


def main():
    """Ejecuta múltiples iteraciones y analiza variabilidad"""
    
    NUM_ITERATIONS = 5
    
    print("🚀 INVESTIGACIÓN DE ESTABILIDAD - MaterialsLoop (Enfoque Simple)")
    print(f"Iteraciones: {NUM_ITERATIONS}")
    print(f"{'='*60}\n")
    
    scores = []
    
    for i in range(NUM_ITERATIONS):
        print(f"🔬 Ejecutando iteración {i+1}/{NUM_ITERATIONS}...")
        
        results = run_isolated_loops()
        
        if "error" in results:
            print(f"  ❌ Error: {results['error']}")
            continue
        
        score = extract_materials_score(results)
        scores.append(score)
        
        print(f"  ✅ MaterialsLoop Support Score: {score:.4f}")
    
    # Análisis de variabilidad
    print(f"\n{'='*60}")
    print("📊 ANÁLISIS DE VARIABILIDAD")
    print(f"{'='*60}\n")
    
    if not scores:
        print("❌ No se obtuvieron scores válidos")
        return
    
    avg = sum(scores) / len(scores)
    max_score = max(scores)
    min_score = min(scores)
    std_dev = (sum((x - avg)**2 for x in scores) / len(scores)) ** 0.5 if len(scores) > 1 else 0.0
    cv = (std_dev / avg * 100) if avg > 0 else 0.0
    
    print(f"📈 Scores obtenidos: {scores}")
    print(f"\n🎯 Estadísticas ({len(scores)} iteraciones):")
    print(f"  - Promedio: {avg:.4f}")
    print(f"  - Máximo: {max_score:.4f}")
    print(f"  - Mínimo: {min_score:.4f}")
    print(f"  - Desviación estándar: {std_dev:.4f}")
    print(f"  - Coeficiente de variación: {cv:.2f}%")
    
    # Clasificar estabilidad
    if cv < 5:
        stability = "EXCELENTE ✅"
    elif cv < 10:
        stability = "BUENA ✅"
    elif cv < 20:
        stability = "MODERADA ⚠️"
    else:
        stability = "BAJA ❌"
    
    print(f"\n🔍 Estabilidad: {stability}")
    
    # Guardar resultados
    summary = {
        "analysis_date": datetime.now().isoformat(),
        "num_iterations": NUM_ITERATIONS,
        "successful_iterations": len(scores),
        "scores": scores,
        "statistics": {
            "average": avg,
            "max": max_score,
            "min": min_score,
            "std_dev": std_dev,
            "coefficient_variation": cv,
            "stability_rating": stability
        }
    }
    
    output_file = f"materials_stability_simple_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Resultados guardados en: {output_file}")
    
    # Recomendaciones
    print(f"\n{'='*60}")
    print("💡 RECOMENDACIONES")
    print(f"{'='*60}\n")
    
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
    
    print(f"\n{'='*60}")
    print("✅ INVESTIGACIÓN COMPLETADA")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
