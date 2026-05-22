#!/usr/bin/env python3
"""
Test simple de conectividad con Ollama
Usa modelos que sabemos que están disponibles
"""

import asyncio
import ollama
import json
from datetime import datetime

async def test_ollama_basic():
    """Prueba básica de conectividad con Ollama"""
    print("🔬 Test básico de Ollama Cloud")
    print("=" * 50)
    
    try:
        # Crear cliente
        client = ollama.Client()
        
        # Listar modelos disponibles
        print("📋 Modelos disponibles:")
        models_response = client.list()
        models = models_response.models  # Acceso correcto a la lista de modelos
        
        for model in models:
            print(f"  ✅ {model.model} (Tamaño: {model.size} bytes)")
        
        if not models:
            print("❌ No hay modelos disponibles")
            return False
            
        # Seleccionar primer modelo disponible
        test_model = models[0].model
        print(f"\n🧪 Probando con modelo: {test_model}")
        
        # Prompt científico simple
        prompt = """
        Generate a brief scientific hypothesis about quantum entanglement applications in computing.
        Format your response as JSON with these fields:
        {
            "hypothesis": "Your hypothesis here",
            "domain": "quantum_computing", 
            "reasoning": "Brief explanation",
            "experiments": ["experiment 1", "experiment 2"]
        }
        """
        
        print("📤 Enviando solicitud...")
        start_time = datetime.now()
        
        response = client.generate(
            model=test_model,
            prompt=prompt
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print(f"✅ Respuesta recibida en {duration:.2f} segundos")
        print("\n📋 Respuesta:")
        print("-" * 30)
        
        # Intentar parsear como JSON
        try:
            response_json = json.loads(response.response)
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print("⚠️  Respuesta no es JSON válido:")
            print(response.response)
        
        return True
        
    except Exception as e:
        print(f"❌ Error en test básico: {e}")
        return False

async def test_all_available_models():
    """Prueba todos los modelos disponibles"""
    print("\n🔬 Test de todos los modelos disponibles")
    print("=" * 50)
    
    try:
        client = ollama.Client()
        models_response = client.list()
        models = models_response.models
        
        for model in models:
            model_name = model.model
            print(f"\n🧪 Probando modelo: {model_name}")
            
            try:
                response = client.generate(
                    model=model_name,
                    prompt="What is quantum computing? (brief answer)"
                )
                
                print(f"  ✅ {model_name}: OK")
                print(f"     Respuesta: {response.response[:100]}...")
                
            except Exception as e:
                print(f"  ❌ {model_name}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error probando modelos: {e}")
        return False

async def main():
    """Función principal"""
    print("🚀 Iniciando tests de Ollama Cloud")
    print(f"⏰ Timestamp: {datetime.now()}")
    
    # Test básico
    basic_ok = await test_ollama_basic()
    
    if basic_ok:
        # Test de todos los modelos
        await test_all_available_models()
    
    print("\n✅ Tests completados")

if __name__ == "__main__":
    asyncio.run(main())