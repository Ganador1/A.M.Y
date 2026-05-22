"""
Demo Real: Sistema Multi-Agente con Hugging Face
Usa modelos públicos pequeños SIN necesidad de API key
"""

import asyncio
import sys
import os

# Agregar path del proyecto
sys.path.insert(0, os.path.dirname(__file__))

from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest
)


async def test_modelo_publico():
    """Test con modelo público pequeño (sin API key)"""
    print("\n" + "="*70)
    print("DEMO: Hugging Face con Modelo Público (SIN API KEY)")
    print("="*70 + "\n")

    # Crear provider SIN API key (usa modelos públicos)
    provider = HuggingFaceProvider(
        api_key=None,  # No API key = modelos públicos
        cache_enabled=True,
        max_retries=2
    )

    # Usar modelo público pequeño y rápido
    test_cases = [
        {
            "model": "gpt2",
            "prompt": "Scientific hypothesis about",
            "description": "GPT-2 (modelo base público)"
        },
        {
            "model": "distilgpt2",
            "prompt": "The theory of protein folding suggests that",
            "description": "DistilGPT-2 (más rápido)"
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Probando: {case['description']}")
        print(f"   Modelo: {case['model']}")
        print(f"   Prompt: '{case['prompt']}'")

        request = HFInferenceRequest(
            model_id=case['model'],
            prompt=case['prompt'],
            max_new_tokens=50,
            temperature=0.7,
            return_full_text=False
        )

        try:
            response = await provider.generate_text(request)

            if response.success:
                print(f"\n   ✅ Generación exitosa!")
                print(f"   📝 Texto generado: {response.generated_text[:200]}")
                print(f"   ⏱️  Latencia: {response.latency_ms:.0f}ms")
                print(f"   🔢 Tokens: {response.tokens_generated}")
            else:
                print(f"\n   ❌ Error: {response.error}")

        except Exception as e:
            print(f"\n   ❌ Excepción: {e}")

        print(f"\n   {'-'*60}")

    # Mostrar métricas
    print(f"\n📊 MÉTRICAS FINALES:")
    metrics = provider.get_metrics()
    for key, value in metrics.items():
        print(f"   • {key}: {value}")


async def test_agentes_con_modelos_publicos():
    """Test de agentes usando solo modelos públicos"""
    print("\n" + "="*70)
    print("DEMO: Agentes Multi-Modelo con Modelos Públicos")
    print("="*70 + "\n")

    from app.services.huggingface_agent_wrapper import create_agent_wrapper

    # Configurar modelos públicos por agente
    agent_configs = [
        {
            "role": "orchestrator",
            "model": "gpt2",
            "prompt": "Create a research plan for studying",
            "tokens": 100
        },
        {
            "role": "bio_hypothesis",
            "model": "distilgpt2",
            "prompt": "Biological hypothesis: The mechanism of",
            "tokens": 80
        },
        {
            "role": "reviewer",
            "model": "gpt2",
            "prompt": "Critical review: The main weakness of this approach is",
            "tokens": 60
        }
    ]

    for config in agent_configs:
        print(f"\n🎭 Agente: {config['role']}")
        print(f"   Modelo: {config['model']}")
        print(f"   Prompt: '{config['prompt']}'")

        try:
            agent = create_agent_wrapper(
                agent_role=config['role'],
                provider="huggingface",
                model_override=config['model']
            )

            # Generar respuesta
            result = await agent.generate_async(
                prompt=config['prompt'],
                max_new_tokens=config['tokens'],
                temperature=0.7
            )

            if not result.startswith("[ERROR"):
                print(f"\n   ✅ Respuesta generada:")
                print(f"   {result[:150]}...")
            else:
                print(f"\n   ❌ Error: {result}")

        except Exception as e:
            print(f"\n   ❌ Excepción: {e}")

        print(f"\n   {'-'*60}")


async def test_comparacion_modelos():
    """Comparar diferentes modelos públicos para misma tarea"""
    print("\n" + "="*70)
    print("DEMO: Comparación de Modelos Públicos")
    print("="*70 + "\n")

    provider = HuggingFaceProvider(api_key=None)

    prompt = "The scientific method involves"
    modelos = ["gpt2", "distilgpt2"]

    resultados = []

    for modelo in modelos:
        print(f"\n🔬 Probando modelo: {modelo}")

        request = HFInferenceRequest(
            model_id=modelo,
            prompt=prompt,
            max_new_tokens=50,
            temperature=0.7
        )

        try:
            response = await provider.generate_text(request)

            if response.success:
                resultados.append({
                    "modelo": modelo,
                    "texto": response.generated_text,
                    "latencia": response.latency_ms,
                    "tokens": response.tokens_generated,
                    "success": True
                })
                print(f"   ✅ Exitoso ({response.latency_ms:.0f}ms)")
            else:
                resultados.append({
                    "modelo": modelo,
                    "error": response.error,
                    "success": False
                })
                print(f"   ❌ Falló: {response.error}")

        except Exception as e:
            resultados.append({
                "modelo": modelo,
                "error": str(e),
                "success": False
            })
            print(f"   ❌ Excepción: {e}")

    # Comparación
    print(f"\n📊 COMPARACIÓN:")
    print(f"\n{'Modelo':<15} {'Status':<10} {'Latencia':<12} {'Tokens':<10}")
    print("-" * 50)

    for r in resultados:
        if r.get("success"):
            print(f"{r['modelo']:<15} {'✅ OK':<10} {r['latencia']:.0f}ms{'':<7} {r['tokens']}")
        else:
            print(f"{r['modelo']:<15} {'❌ Error':<10} {'-':<12} {'-':<10}")


async def test_workflow_simplificado():
    """Workflow multi-agente simplificado con modelos públicos"""
    print("\n" + "="*70)
    print("DEMO: Workflow Multi-Agente Simplificado")
    print("="*70 + "\n")

    from app.services.huggingface_agent_wrapper import HuggingFaceAgentWrapper

    research_goal = "cancer immunotherapy"

    print(f"🎯 Objetivo: {research_goal}\n")

    # Paso 1: Planificación (orchestrator)
    print("1️⃣ ORCHESTRATOR: Planificación...")
    orchestrator = HuggingFaceAgentWrapper(
        agent_role="orchestrator",
        model_id="gpt2"
    )

    plan_prompt = f"Research plan for {research_goal}: 1."
    plan = await orchestrator.generate_async(plan_prompt, max_new_tokens=80)

    if not plan.startswith("[ERROR"):
        print(f"   ✅ Plan: {plan[:120]}...")
    else:
        print(f"   ❌ Error: {plan}")

    # Paso 2: Hipótesis (bio_hypothesis)
    print("\n2️⃣ BIO HYPOTHESIS: Generación...")
    bio = HuggingFaceAgentWrapper(
        agent_role="bio_hypothesis",
        model_id="distilgpt2"
    )

    hyp_prompt = f"Hypothesis about {research_goal}:"
    hypothesis = await bio.generate_async(hyp_prompt, max_new_tokens=60)

    if not hypothesis.startswith("[ERROR"):
        print(f"   ✅ Hipótesis: {hypothesis[:120]}...")
    else:
        print(f"   ❌ Error: {hypothesis}")

    # Paso 3: Revisión (reviewer)
    print("\n3️⃣ REVIEWER: Revisión crítica...")
    reviewer = HuggingFaceAgentWrapper(
        agent_role="reviewer",
        model_id="gpt2"
    )

    review_prompt = "Critical analysis: The weakness is"
    review = await reviewer.generate_async(review_prompt, max_new_tokens=50)

    if not review.startswith("[ERROR"):
        print(f"   ✅ Revisión: {review[:120]}...")
    else:
        print(f"   ❌ Error: {review}")

    print("\n✅ Workflow completado!\n")


async def main():
    """Ejecutar todas las demos"""
    print("\n🚀 AXIOM ATLAS - Demo Real Hugging Face (Modelos Públicos)")
    print("="*70)
    print("\n⚠️  IMPORTANTE: Estos son modelos públicos pequeños para demostración")
    print("   Para mejor calidad, usa modelos especializados con API key")
    print("="*70 + "\n")

    try:
        # Demo 1: Modelos públicos básicos
        await test_modelo_publico()

        # Demo 2: Agentes con modelos públicos
        await test_agentes_con_modelos_publicos()

        # Demo 3: Comparación
        await test_comparacion_modelos()

        # Demo 4: Workflow simplificado
        await test_workflow_simplificado()

        print("\n" + "="*70)
        print("✅ TODAS LAS DEMOS COMPLETADAS!")
        print("="*70 + "\n")

        print("📝 NOTAS:")
        print("   1. Estos son modelos públicos pequeños (GPT-2, DistilGPT-2)")
        print("   2. Para mejor calidad, configura API key y usa modelos especializados:")
        print("      - microsoft/biogpt (biología)")
        print("      - facebook/galactica-30b (ciencia general)")
        print("      - meta-llama/Meta-Llama-3.1-70B-Instruct (razonamiento)")
        print("   3. Configura: export HUGGINGFACE_API_KEY=hf_...")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrumpida\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
