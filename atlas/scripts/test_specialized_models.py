#!/usr/bin/env python3
"""
Test de modelos especializados grandes para el sistema multi-agente
"""

import sys
import asyncio
sys.path.insert(0, '.')

from app.config.api_keys_manager import get_api_key
from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest
)

async def test_specialized_models():
    print("="*80)
    print("🧪 TEST: Modelos Especializados Grandes para Multi-Agente AXIOM ATLAS")
    print("="*80)

    # Obtener API key
    api_key = get_api_key('HUGGINGFACE')
    print(f"\n✅ API Key configurado: {api_key[:8]}...{api_key[-4:]}")

    # Inicializar provider
    provider = HuggingFaceProvider(api_key=api_key)
    print(f"✅ HuggingFaceProvider inicializado")
    print(f"   - InferenceClient: {'✓' if provider.hf_client else '✗'}")
    print(f"   - API URL: {provider.api_url}\n")

    # Test de modelos especializados por rol de agente
    test_cases = [
        {
            "role": "orchestrator",
            "model": provider.AGENT_MODEL_MAP["orchestrator"],
            "prompt": "Create a research plan to study the effects of CRISPR gene editing on cancer cells.",
            "description": "Coordinación de investigación científica"
        },
        {
            "role": "bio_hypothesis",
            "model": provider.AGENT_MODEL_MAP["bio_hypothesis"],
            "prompt": "Generate a hypothesis about the role of mitochondria in cellular aging.",
            "description": "Generación de hipótesis biológicas"
        },
        {
            "role": "physchem_coder",
            "model": provider.AGENT_MODEL_MAP["physchem_coder"],
            "prompt": "Write a Python function to calculate molecular orbital energies using Hartree-Fock method.",
            "description": "Generación de código científico"
        },
        {
            "role": "reviewer",
            "model": provider.AGENT_MODEL_MAP["reviewer"],
            "prompt": "Critically evaluate this claim: Quantum entanglement can be used for faster-than-light communication.",
            "description": "Revisión crítica científica"
        },
        {
            "role": "publisher",
            "model": provider.AGENT_MODEL_MAP["publisher"],
            "prompt": "Write an abstract for a paper about machine learning applications in protein folding prediction.",
            "description": "Generación de documentación científica"
        },
        {
            "role": "scientific_reasoner",
            "model": provider.AGENT_MODEL_MAP["scientific_reasoner"],
            "prompt": "Explain the mathematical relationship between entropy and information theory.",
            "description": "Razonamiento científico avanzado"
        }
    ]

    results = []

    for i, test in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_cases)}: {test['role'].upper()}")
        print(f"{'='*80}")
        print(f"📋 Descripción: {test['description']}")
        print(f"🤖 Modelo: {test['model']}")
        print(f"📝 Prompt: {test['prompt'][:80]}...")
        print("-"*80)

        request = HFInferenceRequest(
            model_id=test['model'],
            prompt=test['prompt'],
            max_new_tokens=150,  # Más tokens para respuestas detalladas
            temperature=0.7
        )

        try:
            response = await provider.generate_text(request)

            if response.success:
                print(f"✅ SUCCESS!")
                print(f"\n📤 Respuesta generada:")
                print(f"   {response.generated_text[:300]}...")
                print(f"\n📊 Métricas:")
                print(f"   - Tokens generados: {response.tokens_generated}")
                print(f"   - Latencia: {response.latency_ms:.0f}ms")
                print(f"   - Método: {response.metadata.get('method', 'httpx')}")

                results.append({
                    "role": test['role'],
                    "model": test['model'],
                    "success": True,
                    "tokens": response.tokens_generated,
                    "latency": response.latency_ms
                })
            else:
                print(f"❌ FAILED: {response.error}")
                results.append({
                    "role": test['role'],
                    "model": test['model'],
                    "success": False,
                    "error": response.error
                })

        except Exception as e:
            print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)[:200]}")
            results.append({
                "role": test['role'],
                "model": test['model'],
                "success": False,
                "error": str(e)
            })

        # Pequeña pausa entre requests para no saturar la API
        await asyncio.sleep(2)

    # Resumen final
    print(f"\n\n{'='*80}")
    print("📊 RESUMEN DE RESULTADOS")
    print(f"{'='*80}")

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\n✅ Tests exitosos: {successful}/{total} ({successful*100//total}%)")
    print(f"\nDetalle por agente:")
    print("-"*80)

    for result in results:
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"{status} {result['role']:20s} | {result['tokens']:3d} tokens | {result['latency']:6.0f}ms")
        else:
            error_msg = result.get('error', 'Unknown')[:40]
            print(f"{status} {result['role']:20s} | ERROR: {error_msg}")

    # Métricas globales del provider
    print(f"\n{'='*80}")
    print("📈 MÉTRICAS GLOBALES DEL PROVIDER")
    print(f"{'='*80}")
    for key, value in provider.metrics.items():
        print(f"   {key:25s}: {value}")

    return results

if __name__ == "__main__":
    results = asyncio.run(test_specialized_models())
    print(f"\n\n🎉 Test completado!")
