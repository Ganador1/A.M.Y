#!/usr/bin/env python3
"""
Debug de estructura de respuesta de Ollama
"""

import ollama

def debug_ollama_response():
    """Debug de la respuesta de ollama.list()"""
    try:
        client = ollama.Client()
        response = client.list()
        
        print("🔍 Estructura completa de la respuesta:")
        print(f"Tipo: {type(response)}")
        print(f"Contenido: {response}")
        
        if isinstance(response, dict):
            print("\n🔑 Claves disponibles:")
            for key in response.keys():
                print(f"  - {key}: {type(response[key])}")
                
        return response
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    debug_ollama_response()