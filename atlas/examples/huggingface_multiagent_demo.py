"""
Demo: Sistema Multi-Agente con Modelos Cloud de Hugging Face

Este ejemplo demuestra cómo usar el sistema multi-agente de AXIOM Atlas
con modelos especializados de Hugging Face en lugar de modelos locales.

Características demostradas:
1. Configuración de agentes con modelos HF
2. Generación de hipótesis científica
3. Diseño experimental
4. Revisión crítica
5. Generación de reporte final
6. Comparación de rendimiento HF vs Ollama

Requisitos:
- API key de Hugging Face (opcional para modelos públicos)
- Configurar en .env: HUGGINGFACE_API_KEY=hf_...
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.llm_providers.huggingface_provider import huggingface_provider
from app.services.huggingface_agent_wrapper import (
    HuggingFaceAgentWrapper,
    HybridAgentWrapper,
    create_agent_wrapper
)


async def demo_basic_generation():
    """Demo 1: Generación básica con un solo agente"""
    print("\n" + "="*60)
    print("DEMO 1: Generación Básica con Bio Hypothesis Agent")
    print("="*60 + "\n")

    # Crear wrapper para agente de hipótesis biológicas
    bio_agent = HuggingFaceAgentWrapper(
        agent_role="bio_hypothesis",
        domain="biology"
    )

    # Prompt para generar hipótesis
    prompt = """
Generate a falsifiable biological hypothesis about the role of gut microbiome
in Alzheimer's disease. Include:
1. Specific hypothesis statement
2. Biological mechanism
3. Testable predictions
4. Experimental approach

Format as JSON with keys: hypothesis, mechanism, predictions, experiments
"""

    print("📝 Prompt enviado al agente...")
    print(f"Modelo usado: {bio_agent.model_id}\n")

    # Generar hipótesis
    result = await bio_agent.generate_async(
        prompt=prompt,
        max_new_tokens=800,
        temperature=0.65
    )

    print("📊 Hipótesis generada:\n")
    print(result)
    print("\n" + "-"*60 + "\n")


async def demo_multi_agent_workflow():
    """Demo 2: Workflow completo multi-agente"""
    print("\n" + "="*60)
    print("DEMO 2: Workflow Multi-Agente Completo")
    print("="*60 + "\n")

    research_goal = """
Investigate the potential of CRISPR-Cas9 gene editing for treating
sickle cell disease, focusing on efficiency and safety of editing
the HBB gene in hematopoietic stem cells.
"""

    print(f"🎯 Objetivo de investigación:\n{research_goal}\n")

    # Paso 1: Orchestrator - Planificación
    print("1️⃣ ORCHESTRATOR: Planificación estratégica...")
    orchestrator = create_agent_wrapper("orchestrator", provider="huggingface")

    plan_prompt = f"""
You are a research orchestrator. Given this research goal, create a detailed
research plan with 5 key steps. Format as JSON with key 'steps' containing a list.

Research goal: {research_goal}

JSON:"""

    plan = await orchestrator.generate_async(plan_prompt, max_new_tokens=512, temperature=0.3)
    print(f"📋 Plan generado:\n{plan[:500]}...\n")

    # Paso 2: Bio Hypothesis - Generación de hipótesis
    print("\n2️⃣ BIO HYPOTHESIS: Generación de hipótesis...")
    bio_hypothesis = create_agent_wrapper("bio_hypothesis", provider="huggingface", domain="biology")

    hyp_prompt = f"""
Based on this research goal, generate ONE specific, falsifiable, and testable
biological hypothesis. Format as JSON with keys: title, description,
variables, expected_outcome, assumptions.

Research goal: {research_goal}

JSON:"""

    hypothesis = await bio_hypothesis.generate_async(hyp_prompt, max_new_tokens=640, temperature=0.65)
    print(f"🧬 Hipótesis generada:\n{hypothesis[:500]}...\n")

    # Paso 3: PhysChem Coder - Diseño experimental
    print("\n3️⃣ PHYSCHEM CODER: Diseño experimental...")
    coder = create_agent_wrapper("physchem_coder", provider="huggingface")

    code_prompt = f"""
Design a computational experimental plan for this hypothesis. Include:
1. Data collection methods
2. Analysis pipeline (Python pseudo-code)
3. Statistical validation approach

Hypothesis: {hypothesis[:300]}

Provide structured Markdown with code blocks.

Plan:"""

    design = await coder.generate_async(code_prompt, max_new_tokens=700, temperature=0.4)
    print(f"🔬 Diseño experimental:\n{design[:500]}...\n")

    # Paso 4: Reviewer - Revisión crítica
    print("\n4️⃣ REVIEWER: Revisión crítica...")
    reviewer = create_agent_wrapper("reviewer", provider="huggingface")

    review_prompt = f"""
As a scientific reviewer, critically evaluate this hypothesis and experimental plan.
Provide JSON with keys: verdict (approve/revise/reject), strengths, weaknesses,
improvements, risk_level (low/medium/high).

Hypothesis: {hypothesis[:300]}
Plan: {design[:300]}

JSON:"""

    review = await reviewer.generate_async(review_prompt, max_new_tokens=480, temperature=0.35)
    print(f"✅ Revisión:\n{review[:500]}...\n")

    # Paso 5: Publisher - Reporte final
    print("\n5️⃣ PUBLISHER: Generación de reporte...")
    publisher = create_agent_wrapper("publisher", provider="huggingface")

    pub_prompt = f"""
Write a concise scientific report (300 words) with sections:
Abstract, Introduction, Methods, Expected Results, Conclusions.

Research: {research_goal[:200]}
Hypothesis: {hypothesis[:200]}
Plan: {design[:200]}
Review: {review[:200]}

REPORT:"""

    report = await publisher.generate_async(pub_prompt, max_new_tokens=700, temperature=0.65)
    print(f"📄 Reporte final:\n{report}\n")

    print("\n" + "="*60)
    print("✅ Workflow multi-agente completado!")
    print("="*60 + "\n")


async def demo_hybrid_fallback():
    """Demo 3: Sistema híbrido con fallback automático"""
    print("\n" + "="*60)
    print("DEMO 3: Sistema Híbrido HF + Ollama Fallback")
    print("="*60 + "\n")

    # Crear wrapper híbrido
    hybrid_agent = HybridAgentWrapper(
        agent_role="scientific_reasoner",
        hf_model_id="facebook/galactica-30b",
        ollama_model="mistral:7b",
        domain="physics",
        prefer_cloud=True
    )

    prompt = """
Explain the physical principles behind quantum entanglement and its potential
applications in quantum computing. Be concise (200 words).
"""

    print("🔀 Intentando con Hugging Face primero, fallback a Ollama si falla...\n")

    result = hybrid_agent.generate(
        prompt=prompt,
        max_new_tokens=400,
        temperature=0.6
    )

    print(f"📊 Resultado:\n{result}\n")


async def demo_performance_comparison():
    """Demo 4: Comparación de rendimiento"""
    print("\n" + "="*60)
    print("DEMO 4: Comparación de Rendimiento HF vs Ollama")
    print("="*60 + "\n")

    prompt = "Generate a hypothesis about dark matter detection methods."

    # Test HF
    print("⏱️ Testing Hugging Face (cloud)...")
    import time

    hf_agent = create_agent_wrapper("orchestrator", provider="huggingface")
    start = time.time()
    hf_result = await hf_agent.generate_async(prompt, max_new_tokens=300)
    hf_time = time.time() - start

    print(f"  ✅ HF completado en {hf_time:.2f}s")
    print(f"  📝 Longitud: {len(hf_result)} caracteres\n")

    # Test Ollama (si está disponible)
    try:
        print("⏱️ Testing Ollama (local)...")
        ollama_agent = create_agent_wrapper(
            "orchestrator",
            provider="ollama",
            ollama_model="llama3:8b"
        )
        start = time.time()
        ollama_result = ollama_agent.generate(prompt, max_new_tokens=300)
        ollama_time = time.time() - start

        print(f"  ✅ Ollama completado en {ollama_time:.2f}s")
        print(f"  📝 Longitud: {len(ollama_result)} caracteres\n")

        # Comparación
        speedup = ollama_time / hf_time if hf_time > 0 else 0
        print(f"📊 Comparación:")
        print(f"  • Hugging Face: {hf_time:.2f}s")
        print(f"  • Ollama: {ollama_time:.2f}s")
        print(f"  • Speedup HF: {speedup:.2f}x {'(faster)' if speedup > 1 else '(slower)'}\n")

    except Exception as e:
        print(f"  ⚠️ Ollama no disponible: {e}\n")


async def demo_domain_specialization():
    """Demo 5: Especialización por dominio"""
    print("\n" + "="*60)
    print("DEMO 5: Especialización por Dominio Científico")
    print("="*60 + "\n")

    domains = [
        ("biology", "Generate a hypothesis about protein folding mechanisms"),
        ("chemistry", "Propose a novel synthesis pathway for aspirin derivatives"),
        ("physics", "Explain quantum tunneling in semiconductor devices"),
        ("mathematics", "Conjecture about prime number distribution")
    ]

    for domain, prompt in domains:
        print(f"🔬 Dominio: {domain}")

        agent = create_agent_wrapper(
            agent_role="scientific_reasoner",
            provider="huggingface",
            domain=domain
        )

        print(f"   Modelo seleccionado: {agent.model_id}")

        result = await agent.generate_async(
            prompt=prompt,
            max_new_tokens=200,
            temperature=0.7
        )

        print(f"   📝 Resultado: {result[:150]}...")
        print()


async def demo_metrics():
    """Demo 6: Métricas de uso"""
    print("\n" + "="*60)
    print("DEMO 6: Métricas de Uso del Servicio")
    print("="*60 + "\n")

    # Obtener métricas actuales
    metrics = huggingface_provider.get_metrics()

    print("📊 Estadísticas del servicio Hugging Face:\n")
    print(f"  • Total de solicitudes: {metrics['total_requests']}")
    print(f"  • Solicitudes exitosas: {metrics['successful_requests']}")
    print(f"  • Solicitudes fallidas: {metrics['failed_requests']}")
    print(f"  • Tasa de éxito: {metrics['success_rate']:.1f}%")
    print(f"  • Cache hits: {metrics['cache_hits']}")
    print(f"  • Tasa de cache: {metrics['cache_hit_rate']:.1f}%")
    print(f"  • Total tokens generados: {metrics['total_tokens']}")
    print(f"  • Latencia promedio: {metrics['average_latency_ms']:.0f}ms\n")


async def main():
    """Ejecutar todas las demos"""
    print("\n🚀 AXIOM ATLAS - Demo Sistema Multi-Agente con Hugging Face")
    print("="*60 + "\n")

    # Verificar API key
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if api_key:
        print(f"✅ API Key de Hugging Face configurada: {api_key[:10]}...")
    else:
        print("⚠️ API Key no configurada. Usando modelos públicos con límites de tasa.")

    print("\nEjecutando demos...\n")

    # Ejecutar demos
    try:
        await demo_basic_generation()
        await demo_multi_agent_workflow()
        await demo_hybrid_fallback()
        await demo_performance_comparison()
        await demo_domain_specialization()
        await demo_metrics()

        print("\n✅ Todas las demos completadas exitosamente!\n")

    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrumpida por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error en demo: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
