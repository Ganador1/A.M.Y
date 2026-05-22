#!/usr/bin/env python3
"""Test HuggingFace API 2025 con InferenceClient"""

import sys
import asyncio
sys.path.insert(0, '.')

from app.config.api_keys_manager import get_api_key
from app.services.llm_providers.huggingface_provider import (
    HuggingFaceProvider,
    HFInferenceRequest
)

async def test_new_api():
    print("="*70)
    print("🧪 Test HuggingFace API 2025")
    print("="*70)

    # Obtener API key
    api_key = get_api_key('HUGGINGFACE')
    print(f"\n✅ API Key: {api_key[:8]}...{api_key[-4:]}")

    # Inicializar provider
    provider = HuggingFaceProvider(api_key=api_key)
    print(f"✅ Provider inicializado")
    print(f"   - InferenceClient: {'✓' if provider.hf_client else '✗'}")
    print(f"   - API URL: {provider.api_url}")

    # Probar con modelo pequeño
    models_to_test = [
        ("microsoft/Phi-3.5-mini-instruct", "What is 2+2?"),
        ("meta-llama/Llama-3.2-1B-Instruct", "Explain photosynthesis in one sentence."),
    ]

    for model_id, prompt in models_to_test:
        print(f"\n{'='*70}")
        print(f"🤖 Modelo: {model_id}")
        print(f"📝 Prompt: {prompt}")
        print("-"*70)

        request = HFInferenceRequest(
            model_id=model_id,
            prompt=prompt,
            max_new_tokens=50,
            temperature=0.7
        )

        try:
            response = await provider.generate_text(request)

            if response.success:
                print(f"✅ SUCCESS!")
                print(f"   Texto generado: {response.generated_text[:200]}")
                print(f"   Tokens: {response.tokens_generated}")
                print(f"   Latencia: {response.latency_ms:.0f}ms")
                print(f"   Método: {response.metadata.get('method', 'httpx')}")
                break  # Si uno funciona, salimos
            else:
                print(f"❌ FAILED: {response.error}")

        except Exception as e:
            print(f"❌ EXCEPTION: {type(e).__name__}: {e}")

    # Mostrar métricas
    print(f"\n{'='*70}")
    print("📊 Métricas")
    print("-"*70)
    for key, value in provider.metrics.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_new_api())
