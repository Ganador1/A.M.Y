#!/usr/bin/env python3
"""Test HuggingFace Hub API"""

import sys
sys.path.insert(0, '.')

from app.config.api_keys_manager import get_api_key
from huggingface_hub import InferenceClient

def test_hf_hub():
    api_key = get_api_key('HUGGINGFACE')
    print(f"✅ API Key: {api_key[:8]}...{api_key[-4:]}\n")

    # Initialize client
    client = InferenceClient(token=api_key)

    # Test with a small public model
    models_to_test = [
        "gpt2",
        "distilgpt2",
        "microsoft/DialoGPT-small"
    ]

    for model in models_to_test:
        try:
            print(f"🧪 Testing model: {model}")
            response = client.text_generation(
                "The answer to 2+2 is",
                model=model,
                max_new_tokens=20
            )
            print(f"✅ Success! Response: {response[:100]}")
            print()
            break  # Si uno funciona, salimos
        except Exception as e:
            print(f"❌ Error with {model}: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            print()
            continue

if __name__ == "__main__":
    test_hf_hub()
