#!/usr/bin/env python3
"""
Prueba Simple: Un Loop (Neuroscience) con Diferentes Modelos
Ejecuta el loop de neurociencia con 4 configuraciones de modelos diferentes
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add project root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.autonomous.pipelines.neuroscience_loop import NeuroscienceLoop

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuraciones de modelos a probar
MODEL_CONFIGS = {
    "baseline": {
        "name": "Baseline (Mixed)",
        "description": "deepseek-r1 + mistral + llama2"
    },
    "all_deepseek": {
        "name": "All DeepSeek",
        "description": "deepseek-r1:8b para todos los roles"
    },
    "all_llama": {
        "name": "All Llama3",
        "description": "llama3:8b para todos los roles"
    },
    "specialized": {
        "name": "Specialized",
        "description": "qwen (hypothesis) + codellama (coder)"
    }
}

# Hipótesis real de neurociencia
HYPOTHESIS = """
Deep learning models trained on fMRI data can predict individual cognitive 
task performance (working memory capacity) with >80% accuracy using 
resting-state functional connectivity patterns.

Expected Outcomes:
- Prediction accuracy >80% for working memory tasks
- Cross-validation R² >0.65
- Validated on HCP dataset (n=500+ subjects)
- Key networks: Default Mode, Executive Control, Attention
"""

async def run_single_iteration(config_name: str, iteration: int = 1):
    """Ejecuta una iteración del loop de neurociencia"""
    logger.info(f"\n{'='*60}")
    logger.info(f"🧠 NEUROSCIENCE LOOP - Config: {MODEL_CONFIGS[config_name]['name']}")
    logger.info(f"   {MODEL_CONFIGS[config_name]['description']}")
    logger.info(f"   Iteration: {iteration}")
    logger.info(f"{'='*60}\n")
    
    try:
        # Crear loop
        loop = NeuroscienceLoop()
        
        # Ejecutar con datos reales
        result = await loop.run_iteration(
            hypothesis_text=HYPOTHESIS,
            max_experiments=3,  # 3 experimentos por rapidez
            use_real_tools=True  # ✅ MODO PRODUCCIÓN
        )
        
        # Extraer métricas clave
        score = result.get('score', 0)
        discoveries = result.get('discoveries', [])
        evidence = result.get('evidence', {})
        
        logger.info(f"✅ COMPLETADO - Score: {score:.3f}, Discoveries: {len(discoveries)}")
        
        return {
            "config": config_name,
            "iteration": iteration,
            "score": score,
            "discoveries_count": len(discoveries),
            "evidence": evidence,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return {
            "config": config_name,
            "iteration": iteration,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

async def compare_models():
    """Compara todas las configuraciones de modelos"""
    logger.info("="*80)
    logger.info("🚀 AXIOM - COMPARACIÓN DE MODELOS EN NEUROSCIENCE LOOP")
    logger.info("="*80)
    
    all_results = []
    
    for config_name in MODEL_CONFIGS.keys():
        logger.info(f"\n\n🔄 Probando configuración: {MODEL_CONFIGS[config_name]['name']}")
        
        # 2 iteraciones por configuración
        for i in range(1, 3):
            result = await run_single_iteration(config_name, i)
            all_results.append(result)
            
            # Pausa breve entre iteraciones
            await asyncio.sleep(2)
    
    # Análisis
    logger.info("\n\n" + "="*80)
    logger.info("📊 RESULTADOS COMPARATIVOS")
    logger.info("="*80)
    
    # Agrupar por configuración
    by_config = {}
    for result in all_results:
        config = result['config']
        if config not in by_config:
            by_config[config] = []
        by_config[config].append(result)
    
    # Tabla de resultados
    print("\n" + "="*80)
    print(f"{'Configuración':<20} {'Iter':<6} {'Score':<10} {'Discoveries':<12} {'Status':<10}")
    print("="*80)
    
    config_averages = {}
    for config_name, results in by_config.items():
        scores = [r['score'] for r in results if r.get('success')]
        avg_score = sum(scores) / len(scores) if scores else 0
        config_averages[config_name] = avg_score
        
        for result in results:
            status = "✅ OK" if result.get('success') else "❌ ERROR"
            score = result.get('score', 0)
            disc = result.get('discoveries_count', 0)
            
            print(f"{MODEL_CONFIGS[config_name]['name']:<20} "
                  f"{result['iteration']:<6} "
                  f"{score:<10.3f} "
                  f"{disc:<12} "
                  f"{status:<10}")
        
        if scores:
            print(f"{'  └─ Promedio':<20} {'':6} {avg_score:<10.3f}")
        print("-"*80)
    
    # Mejor configuración
    if config_averages:
        best = max(config_averages.items(), key=lambda x: x[1])
        print(f"\n🏆 MEJOR CONFIGURACIÓN: {MODEL_CONFIGS[best[0]]['name']} (Score: {best[1]:.3f})")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"neuro_model_comparison_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "loop": "neuroscience",
            "hypothesis": HYPOTHESIS,
            "execution_date": datetime.now().isoformat(),
            "configs_tested": MODEL_CONFIGS,
            "results": all_results,
            "summary": {
                "averages": config_averages,
                "best_config": best[0] if config_averages else None,
                "best_score": best[1] if config_averages else 0
            }
        }, f, indent=2)
    
    logger.info(f"\n💾 Resultados guardados en: {output_file}\n")
    
    return all_results

if __name__ == "__main__":
    asyncio.run(compare_models())
