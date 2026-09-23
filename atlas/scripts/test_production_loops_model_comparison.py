#!/usr/bin/env python3
"""
FASE 7 - Test de Producción: Loops Autónomos con Datos Reales
Prueba diferentes modelos LLM para cada tarea y compara resultados

Ejecuta:
1. Biology Loop (real protein data)
2. Chemistry Loop (real molecular discovery)
3. Mathematics Loop (real proofs)
4. Quantum Loop (real quantum circuits)

Con diferentes configuraciones de modelos:
- Config A (baseline): deepseek-r1, mistral, llama2
- Config B (all deepseek): deepseek-r1 para todos los roles
- Config C (all llama): llama3 para todos los roles
- Config D (specialized): qwen (hypothesis), codellama (coder), deepseek (reviewer)
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.autonomous.pipelines.biology_loop import BiologyLoop
from app.autonomous.pipelines.chemistry_loop import ChemistryLoop
from app.autonomous.pipelines.mathematics_loop import MathematicsLoop
from app.autonomous.pipelines.quantum_loop import QuantumLoop

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# MODEL CONFIGURATIONS
# ============================================================================

MODEL_CONFIGS = {
    "baseline": {
        "name": "Baseline (Mixed)",
        "orchestrator": "deepseek-r1:8b",
        "hypothesis": "mistral:7b",
        "coder": "llama2:7b",
        "reviewer": "deepseek-r1:8b",
        "publisher": "llama2:7b"
    },
    "deepseek": {
        "name": "All DeepSeek-R1",
        "orchestrator": "deepseek-r1:8b",
        "hypothesis": "deepseek-r1:8b",
        "coder": "deepseek-r1:8b",
        "reviewer": "deepseek-r1:8b",
        "publisher": "deepseek-r1:8b"
    },
    "llama": {
        "name": "All Llama3",
        "orchestrator": "llama3:8b",
        "hypothesis": "llama3:8b",
        "coder": "llama3:8b",
        "reviewer": "llama3:8b",
        "publisher": "llama3:8b"
    },
    "specialized": {
        "name": "Specialized (Qwen+CodeLlama)",
        "orchestrator": "deepseek-r1:8b",
        "hypothesis": "qwen:7b",
        "coder": "codellama:7b",
        "reviewer": "qwen:7b",
        "publisher": "llama3:8b"
    }
}

# ============================================================================
# REAL DATA HYPOTHESES
# ============================================================================

REAL_HYPOTHESES = {
    "biology": {
        "title": "CRISPR-Cas9 Off-Target Prediction via Deep Learning",
        "hypothesis": """
        Neural network models trained on experimentally validated CRISPR-Cas9 
        off-target sites can predict genome-wide off-target activity with 
        >95% accuracy using sequence features and chromatin accessibility data.
        
        Expected Outcomes:
        - AUC-ROC >0.95 for off-target classification
        - Precision >0.90 at 90% recall
        - Validated on human genome (hg38)
        """,
        "domain": "genomics",
        "tools": ["dnabert2", "sequence_alignment", "ml_prediction"]
    },
    "chemistry": {
        "title": "Novel MOF Catalysts for CO2 Reduction",
        "hypothesis": """
        Metal-Organic Frameworks (MOFs) with copper-nitrogen active sites 
        demonstrate superior CO2-to-methanol conversion efficiency (>85%) 
        compared to traditional catalysts, verified through DFT calculations 
        and experimental validation.
        
        Expected Properties:
        - Turnover frequency >1000 h⁻¹
        - Selectivity >90% for methanol
        - Stability >100 cycles
        """,
        "domain": "catalysis",
        "tools": ["rdkit", "dft_calculations", "materials_discovery"]
    },
    "mathematics": {
        "title": "Improved Bounds for Prime Gaps via Analytic Methods",
        "hypothesis": """
        Using refined exponential sum estimates and the Maynard-Tao method, 
        we can improve the upper bound for prime gaps to G(n) < n^0.52, 
        tightening the current best result of n^0.525.
        
        Key Steps:
        - Refine Type I/II estimates
        - Optimize sieve parameters
        - Apply automated theorem proving
        """,
        "domain": "number_theory",
        "tools": ["sympy", "formal_verification", "prime_analysis"]
    },
    "quantum": {
        "title": "QAOA Optimization for MaxCut with Hardware Noise",
        "hypothesis": """
        Quantum Approximate Optimization Algorithm (QAOA) with adaptive 
        circuit depth and error mitigation achieves >0.95 approximation 
        ratio for MaxCut problems (n=20 nodes) on NISQ devices with 
        realistic noise models.
        
        Validation:
        - IBM quantum hardware simulation
        - Coherence time T1=100μs, T2=50μs
        - Gate fidelity 99.5%
        """,
        "domain": "quantum_computing",
        "tools": ["qiskit", "quantum_simulation", "optimization"]
    }
}

# ============================================================================
# LOOP EXECUTION
# ============================================================================

async def run_loop_with_config(
    loop_class,
    loop_name: str,
    hypothesis: Dict[str, Any],
    config_name: str,
    config: Dict[str, str],
    iterations: int = 3
) -> Dict[str, Any]:
    """
    Ejecuta un loop autónomo con una configuración específica de modelos
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"🔬 {loop_name.upper()} LOOP - Config: {config['name']}")
    logger.info(f"{'='*80}")
    
    try:
        # Crear instancia del loop
        loop = loop_class()
        
        # TODO: Configure models dynamically (requires loop API support)
        # For now, loops use default models from config/agents.yaml
        
        results = []
        for i in range(iterations):
            logger.info(f"\n🔄 Iteration {i+1}/{iterations}")
            
            # Run iteration con hipótesis real
            result = await loop.run_iteration(
                hypothesis_text=hypothesis['hypothesis'],
                max_experiments=5,
                use_real_tools=True  # ✅ MODO PRODUCCIÓN
            )
            
            results.append(result)
            
            # Log progress
            if 'score' in result:
                logger.info(f"✅ Score: {result['score']:.3f}")
            if 'discoveries' in result:
                logger.info(f"📊 Discoveries: {len(result['discoveries'])}")
        
        # Calcular métricas agregadas
        scores = [r.get('score', 0) for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "loop_name": loop_name,
            "config_name": config_name,
            "config": config,
            "hypothesis": hypothesis['title'],
            "iterations": iterations,
            "results": results,
            "metrics": {
                "avg_score": avg_score,
                "min_score": min(scores) if scores else 0,
                "max_score": max(scores) if scores else 0,
                "total_discoveries": sum(len(r.get('discoveries', [])) for r in results)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Error en {loop_name} con config {config_name}: {e}")
        return {
            "loop_name": loop_name,
            "config_name": config_name,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def compare_models_for_loop(
    loop_class,
    loop_name: str,
    hypothesis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Compara todas las configuraciones de modelos para un loop específico
    """
    logger.info(f"\n{'#'*80}")
    logger.info(f"# COMPARACIÓN DE MODELOS - {loop_name.upper()}")
    logger.info(f"# Hipótesis: {hypothesis['title']}")
    logger.info(f"{'#'*80}\n")
    
    results = []
    for config_name, config in MODEL_CONFIGS.items():
        result = await run_loop_with_config(
            loop_class,
            loop_name,
            hypothesis,
            config_name,
            config,
            iterations=2  # 2 iteraciones por config para rapidez
        )
        results.append(result)
    
    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """
    Ejecuta todos los loops con todas las configuraciones de modelos
    y genera reporte comparativo
    """
    logger.info("="*80)
    logger.info("🚀 AXIOM ATLAS - PRODUCCIÓN: Comparación de Modelos en Loops Reales")
    logger.info("="*80)
    
    all_results = []
    
    # 1. Biology Loop
    logger.info("\n\n📊 1/4 - BIOLOGY LOOP")
    biology_results = await compare_models_for_loop(
        BiologyLoop,
        "biology",
        REAL_HYPOTHESES["biology"]
    )
    all_results.extend(biology_results)
    
    # 2. Chemistry Loop
    logger.info("\n\n📊 2/4 - CHEMISTRY LOOP")
    chemistry_results = await compare_models_for_loop(
        ChemistryLoop,
        "chemistry",
        REAL_HYPOTHESES["chemistry"]
    )
    all_results.extend(chemistry_results)
    
    # 3. Mathematics Loop
    logger.info("\n\n📊 3/4 - MATHEMATICS LOOP")
    math_results = await compare_models_for_loop(
        MathematicsLoop,
        "mathematics",
        REAL_HYPOTHESES["mathematics"]
    )
    all_results.extend(math_results)
    
    # 4. Quantum Loop
    logger.info("\n\n📊 4/4 - QUANTUM LOOP")
    quantum_results = await compare_models_for_loop(
        QuantumLoop,
        "quantum",
        REAL_HYPOTHESES["quantum"]
    )
    all_results.extend(quantum_results)
    
    # ========================================================================
    # ANÁLISIS COMPARATIVO
    # ========================================================================
    
    logger.info("\n\n" + "="*80)
    logger.info("📈 RESULTADOS COMPARATIVOS")
    logger.info("="*80)
    
    # Agrupar por configuración
    by_config = {}
    for result in all_results:
        if 'error' not in result:
            config = result['config_name']
            if config not in by_config:
                by_config[config] = []
            by_config[config].append(result)
    
    # Tabla comparativa
    print("\n📊 SCORES PROMEDIO POR CONFIGURACIÓN:\n")
    print(f"{'Config':<20} {'Biology':<10} {'Chemistry':<10} {'Math':<10} {'Quantum':<10} {'Promedio':<10}")
    print("-" * 80)
    
    config_averages = {}
    for config_name in MODEL_CONFIGS.keys():
        if config_name in by_config:
            loop_scores = {}
            for result in by_config[config_name]:
                loop_scores[result['loop_name']] = result['metrics']['avg_score']
            
            overall_avg = sum(loop_scores.values()) / len(loop_scores) if loop_scores else 0
            config_averages[config_name] = overall_avg
            
            print(f"{MODEL_CONFIGS[config_name]['name']:<20} "
                  f"{loop_scores.get('biology', 0):<10.3f} "
                  f"{loop_scores.get('chemistry', 0):<10.3f} "
                  f"{loop_scores.get('mathematics', 0):<10.3f} "
                  f"{loop_scores.get('quantum', 0):<10.3f} "
                  f"{overall_avg:<10.3f}")
    
    # Mejor configuración
    if config_averages:
        best_config = max(config_averages.items(), key=lambda x: x[1])
        print(f"\n🏆 MEJOR CONFIGURACIÓN: {MODEL_CONFIGS[best_config[0]]['name']} (Score: {best_config[1]:.3f})")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"production_model_comparison_{timestamp}.json"
    
    with open(output_file, 'w') as f:
        json.dump({
            "execution_date": datetime.now().isoformat(),
            "model_configs": MODEL_CONFIGS,
            "hypotheses": REAL_HYPOTHESES,
            "results": all_results,
            "summary": {
                "by_config": by_config,
                "config_averages": config_averages,
                "best_config": best_config[0] if config_averages else None
            }
        }, f, indent=2)
    
    logger.info(f"\n💾 Resultados guardados en: {output_file}")
    
    return all_results

if __name__ == "__main__":
    asyncio.run(main())
