#!/usr/bin/env python3
"""
Test detallado del endpoint Ollama para ver la respuesta completa
"""

import requests
import json

def test_detailed_ollama():
    """Test detallado para ver la respuesta completa"""
    
    base_url = "http://localhost:8002"
    endpoint = f"{base_url}/api/scientific-hypothesis/generate-hypothesis-ollama"
    
    test_request = {
        "research_question": "What quantum algorithms could accelerate drug discovery?",
        "domain": "quantum_computing",
        "context": {
            "specific_focus": "quantum simulation",
            "target": "pharmaceutical compounds"
        }
    }
    
    print("🧪 Enviando request detallado...")
    print(f"📝 Request: {json.dumps(test_request, indent=2)}")
    print()
    
    try:
        response = requests.post(
            endpoint,
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta completa:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"❌ Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_detailed_ollama()