#!/usr/bin/env python3
"""
Test simple para conectividad con modelos Ollama Cloud
"""

import asyncio
import ollama
from app.services.ollama_service import OllamaHypothesisService

async def test_cloud_connectivity():
    """Prueba básica de conectividad con modelos cloud"""
    print("🌩️ Probando conectividad con modelos Ollama Cloud...")
    
    # Verificar modelos disponibles
    try:
        models = ollama.list()
        print(f"📋 Modelos disponibles: {len(models['models'])}")
        for model in models['models']:
            print(f"  - {model['name']}")
        print()
    except Exception as e:
        print(f"❌ Error listando modelos: {e}")
        return False
    
    # Probar modelos cloud específicos
    cloud_models = ["deepseek-v3.1:671b-cloud", "qwen3-coder:480b-cloud"]
    
    for model_name in cloud_models:
        print(f"🧪 Probando {model_name}...")
        try:
            response = ollama.generate(
                model=model_name,
                prompt="Generate a brief scientific hypothesis about quantum computing in 50 words.",
                options={
                    "temperature": 0.7,
                    "max_tokens": 100
                }
            )
            print(f"✅ {model_name}: Respuesta exitosa")
            print(f"   📝 {response['response'][:100]}...")
            print()
        except Exception as e:
            print(f"❌ {model_name}: Error - {e}")
            print()
    
    return True

async def test_ollama_service():
    """Prueba del servicio Ollama integrado"""
    print("🔧 Probando OllamaService integrado...")
    
    service = OllamaHypothesisService()
    
    test_request = {
        "domain": "quantum_computing",
        "description": "Test hypothesis generation with cloud models",
        "context": "Using Ollama cloud models for real hypothesis generation"
    }
    
    try:
        result = await service.generate_hypothesis(test_request)
        print("✅ OllamaService: Generación exitosa")
        print(f"   🎯 Dominio: {result.domain}")
        print(f"   🤖 Modelo: {result.model_used}")
        print(f"   📝 Hipótesis: {result.hypothesis[:150]}...")
        print(f"   🔬 Métodos: {len(result.experimental_methods)} métodos")
        print()
        return True
    except Exception as e:
        print(f"❌ OllamaService: Error - {e}")
        print()
        return False

async def main():
    """Función principal de test"""
    print("🚀 Iniciando tests de Ollama Cloud\n")
    
    # Test 1: Conectividad básica
    connectivity_ok = await test_cloud_connectivity()
    
    # Test 2: Servicio integrado
    if connectivity_ok:
        service_ok = await test_ollama_service()
        
        if service_ok:
            print("🎉 ¡Todos los tests pasaron! Ollama Cloud está listo para hipótesis reales.")
        else:
            print("⚠️  Conectividad OK, pero hay problemas con el servicio integrado.")
    else:
        print("🔴 Problemas de conectividad básica con Ollama.")

if __name__ == "__main__":
    asyncio.run(main())