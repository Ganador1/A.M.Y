#!/usr/bin/env python3
"""
Script para verificar qué modelos están realmente disponibles con tu token de HuggingFace
"""

import sys
sys.path.insert(0, '.')

from app.config.api_keys_manager import get_api_key
from huggingface_hub import InferenceClient
import asyncio

async def check_model_availability():
    print("="*80)
    print("🔍 VERIFICACIÓN DE MODELOS DISPONIBLES EN HUGGINGFACE INFERENCE API")
    print("="*80)

    api_key = get_api_key('HUGGINGFACE')
    print(f"\n✅ API Key: {api_key[:8]}...{api_key[-4:]}\n")

    # Modelos científicos especializados que queremos probar
    models_to_test = [
        # Modelos de biología
        ("microsoft/BioGPT-Large", "Biología especializada"),
        ("microsoft/BioGPT", "Biología base"),

        # Modelos de ciencia general
        ("facebook/galactica-30b", "Ciencia general 30B"),
        ("facebook/galactica-6.7b", "Ciencia general 6.7B"),
        ("facebook/galactica-1.3b", "Ciencia general 1.3B"),

        # Modelos matemáticos
        ("Qwen/Qwen2.5-Math-72B-Instruct", "Matemáticas 72B"),
        ("Qwen/Qwen2.5-Math-7B-Instruct", "Matemáticas 7B"),
        ("mistralai/Mathstral-7B-v0.1", "Matemáticas Mistral"),

        # Modelos de código
        ("Qwen/Qwen2.5-Coder-32B-Instruct", "Código 32B"),
        ("Qwen/Qwen2.5-Coder-7B-Instruct", "Código 7B"),
        ("deepseek-ai/deepseek-coder-33b-instruct", "DeepSeek Coder 33B"),
        ("deepseek-ai/deepseek-coder-6.7b-instruct", "DeepSeek Coder 6.7B"),

        # Modelos generales grandes
        ("meta-llama/Meta-Llama-3.1-70B-Instruct", "Llama 70B"),
        ("meta-llama/Llama-3.1-8B-Instruct", "Llama 8B"),
        ("mistralai/Mixtral-8x22B-Instruct-v0.1", "Mixtral 8x22B"),
        ("mistralai/Mixtral-8x7B-Instruct-v0.1", "Mixtral 8x7B"),

        # Modelos científicos alternativos
        ("google/flan-t5-xxl", "FLAN-T5 XXL científico"),
        ("EleutherAI/gpt-neox-20b", "GPT-NeoX 20B"),
    ]

    client = InferenceClient(token=api_key)

    available = []
    unavailable = []

    print(f"Probando {len(models_to_test)} modelos...\n")
    print("-"*80)

    for i, (model_id, description) in enumerate(models_to_test, 1):
        print(f"\n[{i}/{len(models_to_test)}] {model_id}")
        print(f"    Descripción: {description}")

        try:
            # Intentar una llamada simple
            response = client.chat_completion(
                messages=[{"role": "user", "content": "Hi"}],
                model=model_id,
                max_tokens=5
            )

            print(f"    ✅ DISPONIBLE - Respuesta: {response.choices[0].message.content[:50]}")
            available.append((model_id, description))

        except Exception as e:
            error_msg = str(e)

            # Analizar el tipo de error
            if "404" in error_msg or "not found" in error_msg.lower():
                status = "❌ NO EXISTE"
            elif "400" in error_msg or "bad request" in error_msg.lower():
                status = "⚠️ NO SOPORTADO (400)"
            elif "503" in error_msg:
                status = "⏳ CARGANDO (503)"
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                status = "🔒 REQUIERE PERMISOS"
            elif "402" in error_msg or "payment" in error_msg.lower():
                status = "💰 REQUIERE PAGO"
            else:
                status = f"❓ ERROR: {error_msg[:30]}"

            print(f"    {status}")
            unavailable.append((model_id, description, status))

        # Pequeña pausa para no saturar la API
        await asyncio.sleep(0.5)

    # Resumen
    print(f"\n\n{'='*80}")
    print("📊 RESUMEN DE DISPONIBILIDAD")
    print(f"{'='*80}\n")

    print(f"✅ MODELOS DISPONIBLES ({len(available)}/{len(models_to_test)}):")
    print("-"*80)
    if available:
        for model, desc in available:
            print(f"  ✓ {model:50s} | {desc}")
    else:
        print("  (ninguno)")

    print(f"\n❌ MODELOS NO DISPONIBLES ({len(unavailable)}/{len(models_to_test)}):")
    print("-"*80)
    if unavailable:
        for model, desc, status in unavailable:
            print(f"  ✗ {model:50s} | {status}")
    else:
        print("  (ninguno)")

    # Recomendaciones
    print(f"\n\n{'='*80}")
    print("💡 RECOMENDACIONES")
    print(f"{'='*80}\n")

    if len(available) < 3:
        print("⚠️ PROBLEMA DETECTADO: Muy pocos modelos disponibles.")
        print("\nPosibles causas:")
        print("  1. Tu token HuggingFace no tiene permisos 'Make calls to Inference Providers'")
        print("  2. Necesitas una cuenta PRO para acceder a modelos grandes")
        print("  3. Los modelos requieren providers específicos no incluidos en tu plan")
        print("\n✅ Solución:")
        print("  1. Verifica tu token en: https://huggingface.co/settings/tokens")
        print("  2. Asegúrate de tener permisos: 'Inference API (serverless)'")
        print("  3. Considera upgrade a PRO si necesitas modelos grandes especializados")
    else:
        print("✅ Tienes acceso a varios modelos. Configuración:")
        print("\nModelos recomendados para AXIOM ATLAS:")
        for model, desc in available[:6]:
            print(f"  • {model}")

if __name__ == "__main__":
    asyncio.run(check_model_availability())
