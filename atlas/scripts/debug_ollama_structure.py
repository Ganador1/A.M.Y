#!/usr/bin/env python3
"""
Debug de estructura de modelos Ollama
"""

import ollama
import json

def debug_models():
    """Ver estructura real de modelos"""
    print("🔍 Inspeccionando estructura de modelos...")
    
    try:
        models_response = ollama.list()
        print("📋 Respuesta completa:")
        print(json.dumps(models_response, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_models()