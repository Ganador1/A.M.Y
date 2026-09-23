#!/usr/bin/env python3
"""
Test específico del modelo Mathstral-7B para razonamiento científico
"""

import sys
import asyncio
sys.path.insert(0, '.')

from app.config.api_keys_manager import get_api_key
from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest
)

async def test_mathstral():
    print("="*80)
    print("🧪 TEST: Mathstral-7B para Razonamiento Científico")
    print("="*80)

    # Obtener API key
    api_key = get_api_key('HUGGINGFACE')
    print(f"\n✅ API Key: {api_key[:8]}...{api_key[-4:]}")

    # Inicializar provider
    provider = HuggingFaceProvider(api_key=api_key)
    print(f"✅ Provider inicializado\n")

    # Modelo a probar
    model_id = "mistralai/Mathstral-7B-v0.1"

    # Tests científicos variados
    test_prompts = [
        {
            "prompt": "Explain the mathematical relationship between entropy and information theory in Shannon's framework.",
            "description": "Teoría de la información (Shannon)"
        },
        {
            "prompt": "Derive the Schrödinger equation from first principles of quantum mechanics.",
            "description": "Física cuántica fundamental"
        },
        {
            "prompt": "Calculate the gravitational time dilation factor at Earth's surface relative to infinity.",
            "description": "Relatividad general"
        },
        {
            "prompt": "Prove that the sum of angles in a hyperbolic triangle is less than 180 degrees.",
            "description": "Geometría no euclidiana"
        },
        {
            "prompt": "Explain how the Navier-Stokes equations describe fluid dynamics and why they're computationally challenging.",
            "description": "Dinámica de fluidos"
        }
    ]

    results = []

    for i, test in enumerate(test_prompts, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_prompts)}: {test['description']}")
        print(f"{'='*80}")
        print(f"📝 Prompt: {test['prompt'][:70]}...")
        print("-"*80)

        request = HFInferenceRequest(
            model_id=model_id,
            prompt=test['prompt'],
            max_new_tokens=200,  # Más tokens para explicaciones matemáticas
            temperature=0.7
        )

        try:
            response = await provider.generate_text(request)

            if response.success:
                print(f"✅ SUCCESS!")
                print(f"\n📤 Respuesta:")
                print(f"{response.generated_text}")
                print(f"\n📊 Métricas:")
                print(f"   - Tokens: {response.tokens_generated}")
                print(f"   - Latencia: {response.latency_ms:.0f}ms")
                print(f"   - Método: {response.metadata.get('method', 'httpx')}")

                results.append({
                    "test": test['description'],
                    "success": True,
                    "tokens": response.tokens_generated,
                    "latency": response.latency_ms
                })
            else:
                print(f"❌ FAILED: {response.error}")
                results.append({
                    "test": test['description'],
                    "success": False,
                    "error": response.error
                })

        except Exception as e:
            print(f"❌ EXCEPTION: {type(e).__name__}: {str(e)[:150]}")
            results.append({
                "test": test['description'],
                "success": False,
                "error": str(e)
            })

        # Pausa entre requests
        await asyncio.sleep(2)

    # Resumen
    print(f"\n\n{'='*80}")
    print("📊 RESUMEN")
    print(f"{'='*80}")

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\n✅ Tests exitosos: {successful}/{total} ({successful*100//total if total > 0 else 0}%)")
    print(f"\nDetalle:")
    print("-"*80)

    for result in results:
        status = "✅" if result['success'] else "❌"
        if result['success']:
            print(f"{status} {result['test']:40s} | {result['tokens']:3d} tokens | {result['latency']:6.0f}ms")
        else:
            error_msg = result.get('error', 'Unknown')[:35]
            print(f"{status} {result['test']:40s} | ERROR: {error_msg}")

    # Métricas del provider
    print(f"\n{'='*80}")
    print("📈 MÉTRICAS DEL PROVIDER")
    print(f"{'='*80}")
    for key, value in provider.metrics.items():
        print(f"   {key:25s}: {value}")

    return results

if __name__ == "__main__":
    results = asyncio.run(test_mathstral())

    successful = sum(1 for r in results if r['success'])
    if successful == len(results):
        print(f"\n\n🎉 ¡Todos los tests pasaron! Mathstral-7B está funcionando perfectamente.")
    else:
        print(f"\n\n⚠️ {successful}/{len(results)} tests pasaron. Revisar errores arriba.")
