#!/usr/bin/env python3
"""
COMPARACIÓN SIMPLE DE MODELOS - NEUROSCIENCE LOOP
Ejecuta el loop de neurociencia 2 veces con la configuración actual
para validar funcionamiento antes de la comparación completa de modelos
"""

import sys
import json
import importlib
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Colores
class C:
    OK = '\033[92m'
    FAIL = '\033[91m'
    INFO = '\033[96m'
    WARN = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(msg):
    print(f"\n{C.BOLD}{'='*70}{C.END}")
    print(f"{C.BOLD}{msg:^70}{C.END}")
    print(f"{C.BOLD}{'='*70}{C.END}\n")

def print_ok(msg):
    print(f"{C.OK}✅ {msg}{C.END}")

def print_fail(msg):
    print(f"{C.FAIL}❌ {msg}{C.END}")

def print_info(msg):
    print(f"{C.INFO}ℹ️  {msg}{C.END}")

def run_neuroscience_iteration(iteration_num):
    """Ejecuta una iteración del loop de neurociencia"""
    print_info(f"Ejecutando iteración {iteration_num}/2...")
    
    try:
        # Importar loop
        module = importlib.import_module("app.autonomous.pipelines.neuroscience_loop")
        NeuroscienceLoop = getattr(module, "NeuroscienceLoop")
        
        # Crear instancia
        loop = NeuroscienceLoop()
        
        # Ejecutar iteración (API real: run_iteration(top_n=3))
        result = loop.run_iteration(top_n=5)  # 5 candidatos
        
        # Extraer métricas
        score = result.get('final_score', result.get('score', 0))
        candidates = result.get('scored_candidates', [])
        hypotheses = result.get('hypotheses', [])
        
        print_ok(f"Iteración {iteration_num} completada")
        print_info(f"  Score: {score:.3f}")
        print_info(f"  Candidatos: {len(candidates)}")
        print_info(f"  Hipótesis generadas: {len(hypotheses)}")
        
        return {
            "iteration": iteration_num,
            "success": True,
            "score": score,
            "candidates_count": len(candidates),
            "hypotheses_count": len(hypotheses),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print_fail(f"Error en iteración {iteration_num}: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            "iteration": iteration_num,
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    print_header("NEUROSCIENCE LOOP - TEST DE PRODUCCIÓN")
    print_info("Configuración actual de modelos (config/agents.yaml):")
    print_info("  - orchestrator: deepseek-r1:8b")
    print_info("  - bio_hypothesis: mistral:7b")
    print_info("  - reviewer: deepseek-r1:8b")
    print_info("  - publisher: llama2:7b\n")
    
    results = []
    
    # Ejecutar 2 iteraciones
    for i in range(1, 3):
        result = run_neuroscience_iteration(i)
        results.append(result)
        print("")
    
    # Análisis
    print_header("RESULTADOS")
    
    successful = [r for r in results if r.get('success')]
    scores = [r['score'] for r in successful]
    
    if scores:
        avg_score = sum(scores) / len(scores)
        print_ok(f"Ejecuciones exitosas: {len(successful)}/2")
        print_info(f"Score promedio: {avg_score:.3f}")
        print_info(f"Scores individuales: {', '.join(f'{s:.3f}' for s in scores)}")
    else:
        print_fail("No hubo ejecuciones exitosas")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"neuro_baseline_test_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "test_type": "baseline",
            "loop": "neuroscience",
            "execution_date": datetime.now().isoformat(),
            "results": results,
            "summary": {
                "successful": len(successful),
                "total": len(results),
                "avg_score": avg_score if scores else 0,
                "scores": scores
            }
        }, f, indent=2)
    
    print_info(f"\n💾 Resultados guardados en: {output_file}\n")

if __name__ == "__main__":
    main()
