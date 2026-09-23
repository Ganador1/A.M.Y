#!/usr/bin/env python3
"""
Prueba Realista del Sistema Autónomo Multi-Modelo

Este script prueba la generación de hipótesis científicas reales usando:
1. Modelos pequeños (Ollama local)
2. Modelos grandes cloud (Groq, HuggingFace)
3. Modelos especializados (BioGPT, Galactica)

Compara calidad, tiempo de respuesta y consensus entre modelos.
"""

import asyncio
import json
import sys
import time
from pathlib import Path
from tabulate import tabulate

# Agregar directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.services.multi_model_hypothesis_service import (
    multi_model_service,
    HypothesisRequest,
    ModelTier,
)
from app.services.ollama_service import ollama_service


# Test cases por dominio científico
TEST_CASES = [
    {
        "domain": "quantum_computing",
        "question": "How can topological qubits improve quantum error correction rates beyond surface codes?",
        "context": {
            "current_error_rate": 0.001,
            "target_improvement": 2,
            "qubit_type": "Majorana fermions",
        },
    },
    {
        "domain": "materials_science",
        "question": "What novel 2D materials can achieve room-temperature superconductivity?",
        "context": {
            "temperature_target": 298,  # Kelvin
            "current_best": 203,  # K (H3S under pressure)
            "material_class": "van_der_waals",
        },
    },
    {
        "domain": "biology",
        "question": "How can CRISPR base editing be optimized to reduce off-target effects in therapeutic applications?",
        "context": {
            "editing_type": "C-to-T",
            "current_off_target_rate": 0.05,
            "target_reduction": 10,
        },
    },
    {
        "domain": "mathematics",
        "question": "Are there infinite twin prime pairs with a gap-closing property related to the Riemann zeta function?",
        "context": {
            "conjecture_type": "number_theory",
            "related_open_problems": ["Riemann Hypothesis", "Twin Prime Conjecture"],
        },
    },
    {
        "domain": "climate_science",
        "question": "Can atmospheric carbon sequestration via algae bioengineering offset industrial emissions?",
        "context": {
            "target_reduction": 1e9,  # tons CO2/year
            "algae_species": "Chlorella vulgaris",
            "growth_optimization": "photobioreactor",
        },
    },
]


async def test_single_model_baseline():
    """Prueba baseline con un solo modelo (Ollama local)"""
    print("\n" + "=" * 80)
    print("🔬 TEST 1: Baseline - Modelo Único (Ollama)")
    print("=" * 80)

    test_case = TEST_CASES[0]  # Quantum computing

    request = HypothesisRequest(
        research_question=test_case["question"],
        domain=test_case["domain"],
        context=test_case["context"],
    )

    print(f"\n📋 Dominio: {test_case['domain']}")
    print(f"❓ Pregunta: {test_case['question']}")

    start_time = time.time()

    try:
        result = await ollama_service.generate_hypothesis(request)
        elapsed = time.time() - start_time

        print(f"\n⏱️  Tiempo: {elapsed:.2f}s")
        print(f"📊 Confianza: {result.confidence:.2f}")
        print(f"\n💡 Hipótesis:\n{result.hypothesis_text}")
        print(f"\n🧠 Razonamiento:\n{result.reasoning[:200]}...")
        print(f"\n🔬 Predicciones ({len(result.testable_predictions)}):")
        for i, pred in enumerate(result.testable_predictions[:3], 1):
            print(f"  {i}. {pred}")

        return {
            "success": True,
            "time": elapsed,
            "confidence": result.confidence,
            "predictions": len(result.testable_predictions),
        }

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {"success": False, "error": str(e)}


async def test_multi_model_parallel():
    """Prueba con múltiples modelos en paralelo"""
    print("\n" + "=" * 80)
    print("🌐 TEST 2: Multi-Modelo Paralelo (3 modelos)")
    print("=" * 80)

    test_case = TEST_CASES[1]  # Materials science

    request = HypothesisRequest(
        research_question=test_case["question"],
        domain=test_case["domain"],
        context=test_case["context"],
    )

    print(f"\n📋 Dominio: {test_case['domain']}")
    print(f"❓ Pregunta: {test_case['question']}")

    start_time = time.time()

    try:
        candidates = await multi_model_service.generate_hypothesis_parallel(
            request=request,
            num_models=3,
            tier=ModelTier.BALANCED,
        )

        elapsed = time.time() - start_time

        print(f"\n⏱️  Tiempo Total: {elapsed:.2f}s")
        print(f"✅ Modelos exitosos: {len(candidates)}/3")

        # Mostrar resultados de cada modelo
        results_table = []
        for candidate in candidates:
            results_table.append([
                candidate.model_name[:30],
                f"{candidate.confidence:.2f}",
                f"{candidate.generation_time:.2f}s",
                len(candidate.testable_predictions),
            ])

        print("\n📊 Resultados por Modelo:")
        print(tabulate(
            results_table,
            headers=["Modelo", "Confianza", "Tiempo", "Predicciones"],
            tablefmt="grid",
        ))

        # Mostrar primera hipótesis como ejemplo
        if candidates:
            best = max(candidates, key=lambda c: c.confidence)
            print(f"\n💡 Mejor Hipótesis ({best.model_name}):")
            print(f"{best.hypothesis_text[:300]}...")

        return {
            "success": True,
            "time": elapsed,
            "num_models": len(candidates),
            "avg_confidence": sum(c.confidence for c in candidates) / len(candidates) if candidates else 0,
        }

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {"success": False, "error": str(e)}


async def test_consensus_voting():
    """Prueba con consensus voting"""
    print("\n" + "=" * 80)
    print("🗳️  TEST 3: Consensus Voting (validación cruzada)")
    print("=" * 80)

    test_case = TEST_CASES[2]  # Biology

    request = HypothesisRequest(
        research_question=test_case["question"],
        domain=test_case["domain"],
        context=test_case["context"],
    )

    print(f"\n📋 Dominio: {test_case['domain']}")
    print(f"❓ Pregunta: {test_case['question']}")

    start_time = time.time()

    try:
        final_hypothesis, consensus = await multi_model_service.generate_hypothesis_with_consensus(
            request=request,
            num_models=3,
            tier=ModelTier.BALANCED,
        )

        elapsed = time.time() - start_time

        print(f"\n⏱️  Tiempo Total: {elapsed:.2f}s")
        print(f"📊 Confidence Score: {consensus.confidence_score:.2f}")
        print(f"🤝 Modelos participantes: {len(consensus.supporting_models)}")

        print("\n🎯 Métricas de Calidad:")
        for key, value in consensus.quality_metrics.items():
            if isinstance(value, float):
                print(f"  • {key}: {value:.3f}")
            else:
                print(f"  • {key}: {value}")

        print(f"\n💡 Hipótesis Final (Consensus):")
        print(f"{final_hypothesis.hypothesis_text}")

        print(f"\n🔬 Predicciones con Consensus ({len(consensus.common_predictions)}):")
        for i, pred in enumerate(consensus.common_predictions[:5], 1):
            print(f"  {i}. {pred}")

        print(f"\n💎 Insights Únicos ({len(consensus.unique_insights)}):")
        for i, insight in enumerate(consensus.unique_insights[:3], 1):
            print(f"  {i}. {insight}")

        return {
            "success": True,
            "time": elapsed,
            "confidence": consensus.confidence_score,
            "consensus_score": consensus.quality_metrics["consensus_score"],
        }

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return {"success": False, "error": str(e)}


async def test_domain_specialized_models():
    """Prueba con modelos especializados por dominio"""
    print("\n" + "=" * 80)
    print("🎓 TEST 4: Modelos Especializados por Dominio")
    print("=" * 80)

    results = []

    for test_case in TEST_CASES[:3]:  # Probar 3 dominios
        print(f"\n{'─' * 80}")
        print(f"📚 Dominio: {test_case['domain'].upper()}")
        print(f"{'─' * 80}")

        request = HypothesisRequest(
            research_question=test_case["question"],
            domain=test_case["domain"],
            context=test_case["context"],
        )

        # Mostrar modelos seleccionados
        selected_models = multi_model_service.get_models_for_domain(
            domain=test_case["domain"],
            max_models=2,
        )

        print(f"\n🤖 Modelos seleccionados:")
        for model in selected_models:
            specialty = f" (especializado en {model.domain_specialty})" if model.domain_specialty else ""
            print(f"  • {model.name}{specialty}")

        start_time = time.time()

        try:
            final_hypothesis, consensus = await multi_model_service.generate_hypothesis_with_consensus(
                request=request,
                num_models=2,
            )

            elapsed = time.time() - start_time

            results.append({
                "domain": test_case["domain"],
                "time": elapsed,
                "confidence": consensus.confidence_score,
                "models": len(consensus.supporting_models),
            })

            print(f"\n✅ Generación exitosa")
            print(f"  ⏱️  Tiempo: {elapsed:.2f}s")
            print(f"  📊 Confianza: {consensus.confidence_score:.2f}")
            print(f"  💡 Hipótesis: {final_hypothesis.hypothesis_text[:150]}...")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            results.append({
                "domain": test_case["domain"],
                "error": str(e),
            })

        await asyncio.sleep(1)  # Rate limiting

    # Resumen final
    print(f"\n{'=' * 80}")
    print("📊 RESUMEN DE RESULTADOS")
    print(f"{'=' * 80}")

    summary_table = []
    for result in results:
        if "error" not in result:
            summary_table.append([
                result["domain"],
                f"{result['time']:.2f}s",
                f"{result['confidence']:.2f}",
                result["models"],
            ])

    if summary_table:
        print(tabulate(
            summary_table,
            headers=["Dominio", "Tiempo", "Confianza", "Modelos"],
            tablefmt="grid",
        ))

    return results


async def compare_model_tiers():
    """Comparar diferentes tiers de modelos (Fast vs Quality)"""
    print("\n" + "=" * 80)
    print("⚡ TEST 5: Comparación de Tiers (Fast vs Balanced vs Quality)")
    print("=" * 80)

    test_case = TEST_CASES[3]  # Mathematics

    request = HypothesisRequest(
        research_question=test_case["question"],
        domain=test_case["domain"],
        context=test_case["context"],
    )

    comparison_results = []

    for tier in [ModelTier.FAST, ModelTier.BALANCED, ModelTier.QUALITY]:
        print(f"\n{'─' * 80}")
        print(f"🏃 Tier: {tier.value.upper()}")
        print(f"{'─' * 80}")

        start_time = time.time()

        try:
            candidates = await multi_model_service.generate_hypothesis_parallel(
                request=request,
                num_models=2,
                tier=tier,
            )

            elapsed = time.time() - start_time

            if candidates:
                avg_conf = sum(c.confidence for c in candidates) / len(candidates)
                avg_time = sum(c.generation_time for c in candidates) / len(candidates)

                comparison_results.append({
                    "tier": tier.value,
                    "total_time": elapsed,
                    "avg_time": avg_time,
                    "avg_confidence": avg_conf,
                    "num_models": len(candidates),
                })

                print(f"  ⏱️  Tiempo total: {elapsed:.2f}s")
                print(f"  📊 Confianza promedio: {avg_conf:.2f}")
                print(f"  ✅ Modelos: {len(candidates)}")

        except Exception as e:
            print(f"  ❌ Error: {e}")

        await asyncio.sleep(1)

    # Mostrar comparación
    if comparison_results:
        print(f"\n{'=' * 80}")
        print("📊 COMPARACIÓN DE TIERS")
        print(f"{'=' * 80}")

        comparison_table = [
            [r["tier"], f"{r['total_time']:.2f}s", f"{r['avg_confidence']:.2f}", r["num_models"]]
            for r in comparison_results
        ]

        print(tabulate(
            comparison_table,
            headers=["Tier", "Tiempo Total", "Confianza", "Modelos"],
            tablefmt="grid",
        ))

    return comparison_results


async def main():
    """Función principal de pruebas"""
    print("\n" + "█" * 80)
    print("🚀 PRUEBA REALISTA DEL SISTEMA AUTÓNOMO MULTI-MODELO")
    print("█" * 80)

    print("\n📝 Descripción:")
    print("  Este test compara la calidad de hipótesis científicas generadas por:")
    print("  • Modelos pequeños locales (Ollama)")
    print("  • Modelos grandes en la nube (Groq, HuggingFace)")
    print("  • Modelos especializados (BioGPT, Galactica)")
    print("  • Sistema de consensus voting")

    all_results = {}

    # Test 1: Baseline single model
    try:
        all_results["baseline"] = await test_single_model_baseline()
    except Exception as e:
        print(f"\n⚠️  Test 1 skipped: {e}")

    await asyncio.sleep(2)

    # Test 2: Multi-model parallel
    try:
        all_results["parallel"] = await test_multi_model_parallel()
    except Exception as e:
        print(f"\n⚠️  Test 2 skipped: {e}")

    await asyncio.sleep(2)

    # Test 3: Consensus voting
    try:
        all_results["consensus"] = await test_consensus_voting()
    except Exception as e:
        print(f"\n⚠️  Test 3 skipped: {e}")

    await asyncio.sleep(2)

    # Test 4: Domain-specialized models
    try:
        all_results["specialized"] = await test_domain_specialized_models()
    except Exception as e:
        print(f"\n⚠️  Test 4 skipped: {e}")

    await asyncio.sleep(2)

    # Test 5: Tier comparison
    try:
        all_results["tiers"] = await compare_model_tiers()
    except Exception as e:
        print(f"\n⚠️  Test 5 skipped: {e}")

    # Guardar resultados
    results_file = Path("multi_model_test_results.json")
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n{'=' * 80}")
    print("✅ PRUEBAS COMPLETADAS")
    print(f"{'=' * 80}")
    print(f"\n📁 Resultados guardados en: {results_file}")

    # Cerrar servicio
    await multi_model_service.close()

    print("\n🎉 Sistema multi-modelo listo para integración con loops autónomos!")

    return 0


if __name__ == "__main__":
    try:
        exit(asyncio.run(main()))
    except KeyboardInterrupt:
        print("\n\n⚠️  Prueba interrumpida por el usuario")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
