#!/usr/bin/env python3
"""
Test del endpoint Ollama en el servidor FastAPI
"""

import requests
import json
import time

def test_ollama_endpoint():
    """Test del endpoint /generate-hypothesis-ollama"""
    
    base_url = "http://localhost:8002"
    endpoint = f"{base_url}/api/scientific-hypothesis/generate-hypothesis-ollama"
    
    print("🔗 Probando endpoint Ollama en FastAPI...")
    
    # Esperar que el servidor esté listo
    print("⏳ Esperando que el servidor esté listo...")
    for i in range(10):
        try:
            health_response = requests.get(f"{base_url}/health", timeout=2)
            if health_response.status_code == 200:
                print("✅ Servidor FastAPI listo")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
        print(f"   Intento {i+1}/10...")
    
    # Test de generación de hipótesis
    test_request = {
        "research_question": "How can quantum computing improve drug discovery for cancer treatments?",
        "domain": "quantum_computing",
        "context": {
            "specific_focus": "molecular simulation",
            "target": "cancer therapeutics"
        }
    }
    
    print(f"🧪 Enviando request a {endpoint}...")
    try:
        response = requests.post(
            endpoint,
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=60  # Timeout generoso para modelos cloud
        )
        
        print(f"📡 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Respuesta exitosa del endpoint Ollama!")
            print(f"   📝 Hipótesis: {result.get('hypothesis_text', 'N/A')[:100]}...")
            print(f"   🤖 Razonamiento: {result.get('reasoning', 'N/A')[:100]}...")
            print(f"   📊 Confianza: {result.get('confidence', 'N/A')}")
            print(f"   🔬 Predicciones: {len(result.get('testable_predictions', []))}")
            print(f"   📚 Metodologías: {len(result.get('methodology_suggestions', []))}")
            return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("⏰ Timeout - El modelo cloud puede tardar más en responder")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def test_multiple_domains():
    """Test con múltiples dominios científicos"""
    
    base_url = "http://localhost:8002"
    endpoint = f"{base_url}/api/scientific-hypothesis/generate-hypothesis-ollama"
    
    test_cases = [
        {
            "domain": "materials_science",
            "research_question": "What novel materials could improve solar cell efficiency?"
        },
        {
            "domain": "chemistry", 
            "research_question": "How can catalysts be designed for CO2 reduction?"
        },
        {
            "domain": "biology",
            "research_question": "What mechanisms control cellular aging?"
        }
    ]
    
    print("\n🔬 Probando múltiples dominios científicos...")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test {i}/3 - Dominio: {test_case['domain']}")
        
        try:
            response = requests.post(
                endpoint,
                json=test_case,
                headers={"Content-Type": "application/json"},
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {test_case['domain']}: Exitoso")
                print(f"   📝 {result.get('hypothesis_text', 'N/A')[:80]}...")
            else:
                print(f"   ❌ {test_case['domain']}: Error {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ {test_case['domain']}: Error - {e}")
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando test del endpoint Ollama\n")
    
    # Test 1: Endpoint básico
    basic_ok = test_ollama_endpoint()
    
    # Test 2: Múltiples dominios
    if basic_ok:
        multi_ok = test_multiple_domains()
        
        if multi_ok:
            print("\n🎉 ¡Todos los tests del endpoint Ollama exitosos!")
            print("🌩️ Hipótesis reales generadas con modelos cloud")
        else:
            print("\n⚠️  Test básico OK, problemas con múltiples dominios")
    else:
        print("\n🔴 Problemas básicos con el endpoint Ollama")