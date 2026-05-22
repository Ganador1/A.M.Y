#!/usr/bin/env python3
"""
Test súper simple para verificar modelos Ollama Cloud
"""

import ollama

def test_basic_connectivity():
    """Test básico sin dependencias del servicio"""
    print("🌩️ Probando conectividad básica con Ollama Cloud...")
    
    # Listar modelos disponibles
    try:
        models = ollama.list()
        print(f"📋 Modelos encontrados: {len(models['models'])}")
        for model in models['models']:
            print(f"  - {model['name']}")
        print()
    except Exception as e:
        print(f"❌ Error listando modelos: {e}")
        return False
    
    # Probar modelos cloud
    cloud_models = ["deepseek-v3.1:671b-cloud", "qwen3-coder:480b-cloud"]
    
    for model_name in cloud_models:
        print(f"🧪 Probando {model_name}...")
        try:
            response = ollama.generate(
                model=model_name,
                prompt="Write a brief scientific hypothesis about photosynthesis in 30 words.",
                options={"temperature": 0.7}
            )
            
            if 'response' in response:
                print(f"✅ {model_name}: OK")
                print(f"   📝 {response['response'][:80]}...")
            else:
                print(f"⚠️  {model_name}: Respuesta inesperada")
            print()
            
        except Exception as e:
            print(f"❌ {model_name}: Error - {e}")
            print()
    
    print("🎉 Test básico completado")
    return True

if __name__ == "__main__":
    test_basic_connectivity()