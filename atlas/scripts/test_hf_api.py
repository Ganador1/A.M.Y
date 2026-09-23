#!/usr/bin/env python3
"""Script simple para probar la API de HuggingFace"""

import sys
sys.path.insert(0, '.')

from app.config.api_keys_manager import get_api_key
import httpx
import asyncio

async def test_hf_api():
    api_key = get_api_key('HUGGINGFACE')
    print(f"✅ API Key obtenido: {api_key[:8]}...{api_key[-4:]}")
    print(f"Longitud: {len(api_key)}")

    # Test con gpt2 (modelo público)
    url = "https://api-inference.huggingface.co/models/gpt2"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "inputs": "The answer to 2+2 is",
        "parameters": {"max_new_tokens": 20}
    }

    print(f"\n🔍 Probando URL: {url}")
    print(f"Headers: Authorization: Bearer {api_key[:8]}...{api_key[-4:]}")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            print(f"\n📊 Status Code: {response.status_code}")
            print(f"Response: {response.text[:500]}")

            if response.status_code == 200:
                print("\n✅ API funcionando correctamente!")
                result = response.json()
                if isinstance(result, list):
                    print(f"Texto generado: {result[0].get('generated_text', '')}")
            else:
                print(f"\n❌ Error {response.status_code}")
                print(f"Response body: {response.text}")

        except Exception as e:
            print(f"\n❌ Excepción: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hf_api())
