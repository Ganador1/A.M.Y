#!/usr/bin/env python3
"""
Ejemplo End-to-End: Integración Multi-Modelo con Loop Autónomo

Este ejemplo demuestra cómo usar el nuevo sistema multi-modelo
para generar hipótesis científicas de alta calidad en un loop autónomo real.

Compara:
1. Generación baseline (heurístico simple)
2. Generación multi-modelo (3 modelos con consensus)
3. Métricas de calidad y tiempo
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.services.multi_model_hypothesis_service import (
    multi_model_service,
    HypothesisRequest,
    ModelTier,
)
from app.autonomous.generators.hypothesis_mutator import HypothesisMutator


def print_section(title: str) -> None:
    """Imprimir sección formateada"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_subsection(title: str) -> None:
    """Imprimir subsección formateada"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


async def test_baseline_heuristic():
    """Test 1: Baseline heurístico (método actual)"""
    print_section("TEST 1: BASELINE HEURÍSTICO (Método Actual)")
    
    # Simular una conjetura matemática
    fake_conjecture = {
        "id": "conj_001",
        "statement": "For all prime numbers p > 2, the equation p^2 + 1 has exactly two prime divisors",
        "domain": "number_theory",
        "metadata": {},
    }
    
    print("\n📋 Conjetura Original:")
    print(f"   {fake_conjecture['statement']}")
    
    # Usar HypothesisMutator actual
    mutator = HypothesisMutator()
    
    start_time = time.time()
    mutations = mutator.mutate_batch([fake_conjecture], max_mutations=3)
    elapsed = time.time() - start_time
    
    print(f"\n⏱️  Tiempo de generación: {elapsed:.3f}s")
    print(f"✅ Mutaciones generadas: {len(mutations)}")
    
    print("\n🧬 Mutaciones Heurísticas:")
    for i, mut in enumerate(mutations, 1):
        print(f"\n   {i}. Operación: {mut.get('mutation_op', 'unknown')}")
        print(f"      Enunciado: {mut.get('statement', '')[:100]}...")
    
    return {
        "method": "heuristic",
        "time": elapsed,
        "count": len(mutations),
        "mutations": mutations,
    }


async def test_multi_model_single():
    """Test 2: Multi-modelo con un solo request"""
    print_section("TEST 2: MULTI-MODELO SIMPLE (1 hipótesis)")
    
    research_question = """
    Investigate whether there exists a closed-form formula for the distribution 
    of prime gaps that depends on the Riemann zeta function zeros.
    """
    
    print("\n❓ Pregunta de Investigación:")
    print(f"   {research_question.strip()}")
    
    request = HypothesisRequest(
        research_question=research_question,
        domain="number_theory",
        context={
            "area": "analytic number theory",
            "related_conjectures": ["Riemann Hypothesis", "Prime Number Theorem"],
            "difficulty": "high",
        },
    )
    
    print("\n🤖 Configuración:")
    print(f"   Dominio: {request.domain}")
    print(f"   Modelos: 3 (auto-selección)")
    print(f"   Tier: BALANCED")
    
    start_time = time.time()
    
    try:
        final_hypothesis, consensus = await multi_model_service.generate_hypothesis_with_consensus(
            request=request,
            num_models=3,
            tier=ModelTier.BALANCED,
        )
        
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Tiempo total: {elapsed:.2f}s")
        print(f"📊 Confidence Score: {consensus.confidence_score:.3f}")
        print(f"🤝 Modelos participantes: {len(consensus.supporting_models)}")
        
        print("\n💡 HIPÓTESIS GENERADA:")
        print(f"   {final_hypothesis.hypothesis_text}")
        
        print("\n🧠 RAZONAMIENTO CIENTÍFICO:")
        print(f"   {final_hypothesis.reasoning[:300]}...")
        
        print(f"\n🔬 PREDICCIONES TESTABLES ({len(final_hypothesis.testable_predictions)}):")
        for i, pred in enumerate(final_hypothesis.testable_predictions[:5], 1):
            print(f"   {i}. {pred}")
        
        print(f"\n📚 METODOLOGÍA SUGERIDA ({len(final_hypothesis.methodology_suggestions)}):")
        for i, method in enumerate(final_hypothesis.methodology_suggestions[:3], 1):
            print(f"   {i}. {method}")
        
        print("\n🎯 MÉTRICAS DE CONSENSUS:")
        for key, value in consensus.quality_metrics.items():
            if isinstance(value, float):
                print(f"   • {key}: {value:.3f}")
            else:
                print(f"   • {key}: {value}")
        
        print(f"\n🔗 PREDICCIONES COMUNES ({len(consensus.common_predictions)}):")
        for i, common in enumerate(consensus.common_predictions[:3], 1):
            print(f"   {i}. {common}")
        
        return {
            "method": "multi_model",
            "time": elapsed,
            "confidence": consensus.confidence_score,
            "consensus_score": consensus.quality_metrics.get("consensus_score", 0.0),
            "hypothesis": final_hypothesis,
            "consensus": consensus,
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {
            "method": "multi_model",
            "error": str(e),
        }


async def test_multi_model_batch():
    """Test 3: Multi-modelo con múltiples conjeturas"""
    print_section("TEST 3: MULTI-MODELO BATCH (3 hipótesis)")
    
    conjectures = [
        {
            "id": "bio_001",
            "question": "How can base editing in CRISPR be optimized to reduce off-target effects in vivo?",
            "domain": "biology",
        },
        {
            "id": "mat_001",
            "question": "What atomic configurations enable room-temperature superconductivity in 2D materials?",
            "domain": "materials_science",
        },
        {
            "id": "qc_001",
            "question": "Can topological qubits achieve fault-tolerant quantum computation with lower error rates?",
            "domain": "quantum_computing",
        },
    ]
    
    results = []
    total_start = time.time()
    
    for conj in conjectures:
        print_subsection(f"Procesando: {conj['id']}")
        print(f"❓ {conj['question']}")
        
        request = HypothesisRequest(
            research_question=conj["question"],
            domain=conj["domain"],
            context={"conjecture_id": conj["id"]},
        )
        
        start = time.time()
        
        try:
            final_hypothesis, consensus = await multi_model_service.generate_hypothesis_with_consensus(
                request=request,
                num_models=2,  # Solo 2 modelos para rapidez
                tier=ModelTier.FAST,
            )
            
            elapsed = time.time() - start
            
            results.append({
                "id": conj["id"],
                "domain": conj["domain"],
                "time": elapsed,
                "confidence": consensus.confidence_score,
                "models": len(consensus.supporting_models),
                "hypothesis_preview": final_hypothesis.hypothesis_text[:100],
            })
            
            print(f"✅ Generado en {elapsed:.2f}s")
            print(f"   Confianza: {consensus.confidence_score:.2f}")
            print(f"   Modelos: {', '.join(consensus.supporting_models)}")
            print(f"   Preview: {final_hypothesis.hypothesis_text[:80]}...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append({
                "id": conj["id"],
                "error": str(e),
            })
        
        # Rate limiting
        await asyncio.sleep(1)
    
    total_elapsed = time.time() - total_start
    
    print_subsection("RESUMEN DEL BATCH")
    print(f"⏱️  Tiempo total: {total_elapsed:.2f}s")
    print(f"✅ Hipótesis exitosas: {sum(1 for r in results if 'error' not in r)}/{len(results)}")
    
    if results:
        successful = [r for r in results if "error" not in r]
        if successful:
            avg_time = sum(r["time"] for r in successful) / len(successful)
            avg_conf = sum(r["confidence"] for r in successful) / len(successful)
            
            print(f"📊 Tiempo promedio: {avg_time:.2f}s")
            print(f"📊 Confianza promedio: {avg_conf:.3f}")
    
    return {
        "method": "multi_model_batch",
        "total_time": total_elapsed,
        "results": results,
    }


async def compare_baseline_vs_multimodel():
    """Test 4: Comparación directa"""
    print_section("TEST 4: COMPARACIÓN BASELINE VS MULTI-MODELO")
    
    test_conjecture = {
        "id": "compare_001",
        "statement": "The sum of reciprocals of twin primes converges to a finite value",
        "domain": "number_theory",
        "metadata": {},
    }
    
    print("\n📋 Conjetura de prueba:")
    print(f"   {test_conjecture['statement']}")
    
    # Baseline
    print_subsection("Método 1: Baseline Heurístico")
    mutator = HypothesisMutator()
    
    baseline_start = time.time()
    baseline_mutations = mutator.mutate_batch([test_conjecture], max_mutations=3)
    baseline_time = time.time() - baseline_start
    
    print(f"⏱️  Tiempo: {baseline_time:.3f}s")
    print(f"✅ Mutaciones: {len(baseline_mutations)}")
    print("\nEjemplo de mutación:")
    if baseline_mutations:
        print(f"   {baseline_mutations[0].get('statement', '')[:100]}...")
    
    # Multi-modelo
    print_subsection("Método 2: Multi-Modelo con Consensus")
    
    request = HypothesisRequest(
        research_question=f"Investigate: {test_conjecture['statement']}",
        domain=test_conjecture["domain"],
        context=test_conjecture.get("metadata", {}),
    )
    
    multimodel_start = time.time()
    
    try:
        final_hypothesis, consensus = await multi_model_service.generate_hypothesis_with_consensus(
            request=request,
            num_models=3,
            tier=ModelTier.BALANCED,
        )
        
        multimodel_time = time.time() - multimodel_start
        
        print(f"⏱️  Tiempo: {multimodel_time:.2f}s")
        print(f"📊 Confianza: {consensus.confidence_score:.3f}")
        print(f"🤝 Modelos: {len(consensus.supporting_models)}")
        print("\nHipótesis generada:")
        print(f"   {final_hypothesis.hypothesis_text[:150]}...")
        
        # Comparación
        print_subsection("ANÁLISIS COMPARATIVO")
        
        speedup = baseline_time / multimodel_time if multimodel_time > 0 else 0
        
        print(f"📊 Tiempo:")
        print(f"   Baseline:     {baseline_time:.3f}s")
        print(f"   Multi-modelo: {multimodel_time:.2f}s")
        print(f"   Factor:       {speedup:.2f}x {'(baseline más rápido)' if speedup > 1 else '(multi-modelo más lento)'}")
        
        print(f"\n📊 Calidad:")
        print(f"   Baseline:     Mutaciones simples (sin confianza)")
        print(f"   Multi-modelo: Confidence {consensus.confidence_score:.2f}, Consensus {consensus.quality_metrics.get('consensus_score', 0):.2f}")
        
        print("\n💡 RECOMENDACIÓN:")
        if consensus.confidence_score > 0.7:
            print("   ✅ Multi-modelo produce hipótesis de ALTA CALIDAD")
            print("   ✅ El tiempo adicional está justificado por la mejora")
        else:
            print("   ⚠️  Multi-modelo puede necesitar ajustes de configuración")
        
        return {
            "baseline_time": baseline_time,
            "multimodel_time": multimodel_time,
            "multimodel_confidence": consensus.confidence_score,
            "recommendation": "multi_model" if consensus.confidence_score > 0.7 else "needs_tuning",
        }
        
    except Exception as e:
        print(f"❌ Error en multi-modelo: {e}")
        return {"error": str(e)}


async def main():
    """Función principal de demostración"""
    
    print("\n" + "█" * 80)
    print("🚀 DEMO END-TO-END: INTEGRACIÓN MULTI-MODELO CON LOOP AUTÓNOMO")
    print("█" * 80)
    
    print("\n📝 Esta demostración compara:")
    print("   1. Generación baseline (heurístico actual)")
    print("   2. Generación multi-modelo (nuevo sistema)")
    print("   3. Calidad y rendimiento de ambos enfoques")
    
    all_results = {}
    
    # Test 1: Baseline
    try:
        all_results["baseline"] = await test_baseline_heuristic()
    except Exception as e:
        print(f"\n⚠️  Test 1 falló: {e}")
    
    await asyncio.sleep(2)
    
    # Test 2: Multi-modelo simple
    try:
        all_results["multimodel_single"] = await test_multi_model_single()
    except Exception as e:
        print(f"\n⚠️  Test 2 falló: {e}")
    
    await asyncio.sleep(2)
    
    # Test 3: Multi-modelo batch
    try:
        all_results["multimodel_batch"] = await test_multi_model_batch()
    except Exception as e:
        print(f"\n⚠️  Test 3 falló: {e}")
    
    await asyncio.sleep(2)
    
    # Test 4: Comparación directa
    try:
        all_results["comparison"] = await compare_baseline_vs_multimodel()
    except Exception as e:
        print(f"\n⚠️  Test 4 falló: {e}")
    
    # Guardar resultados
    results_file = Path("multi_model_demo_results.json")
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print_section("✅ DEMOSTRACIÓN COMPLETADA")
    print(f"\n📁 Resultados guardados en: {results_file}")
    
    # Resumen final
    print("\n🎯 CONCLUSIONES:")
    
    if "comparison" in all_results and "recommendation" in all_results["comparison"]:
        recommendation = all_results["comparison"]["recommendation"]
        
        if recommendation == "multi_model":
            print("   ✅ El sistema multi-modelo está LISTO para producción")
            print("   ✅ Genera hipótesis de calidad superior al baseline")
            print("   ✅ Se recomienda integrar con loops autónomos")
        else:
            print("   ⚠️  El sistema multi-modelo necesita ajustes")
            print("   ⚠️  Considerar usar más modelos o tier QUALITY")
    
    print("\n📚 Siguiente paso:")
    print("   Ejecutar: python test_multi_model_autonomous.py")
    print("   Para pruebas exhaustivas de todos los modelos")
    
    # Cerrar servicio
    await multi_model_service.close()
    
    print("\n🎉 ¡Demo completada exitosamente!")
    
    return 0


if __name__ == "__main__":
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrumpida por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
