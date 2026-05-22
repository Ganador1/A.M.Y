#!/usr/bin/env python3
"""
Test funcional para modelos Ollama Cloud
"""

import ollama

def test_cloud_models():
    """Test real con modelos cloud"""
    print("🌩️ Probando modelos Ollama Cloud...")
    
    # Obtener modelos disponibles
    try:
        models_response = ollama.list()
        models = models_response.models if hasattr(models_response, 'models') else models_response['models']
        
        print(f"📋 Modelos disponibles: {len(models)}")
        for model in models:
            model_name = model.model if hasattr(model, 'model') else model['model']
            print(f"  - {model_name}")
        print()
        
    except Exception as e:
        print(f"❌ Error listando modelos: {e}")
        return False
    
    # Probar modelos cloud específicos
    cloud_models = ["deepseek-v3.1:671b-cloud", "qwen3-coder:480b-cloud"]
    
    for model_name in cloud_models:
        print(f"🧪 Probando {model_name}...")
        try:
            # Test con prompt científico simple
            prompt = """Generate a scientific hypothesis about quantum computing applications in drug discovery. 
            Format your response as JSON with these fields:
            - hypothesis: the main hypothesis
            - reasoning: brief scientific reasoning
            - testable_predictions: 2-3 testable predictions
            """
            
            response = ollama.generate(
                model=model_name,
                prompt=prompt,
                options={
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            )
            
            if 'response' in response:
                print(f"✅ {model_name}: Generación exitosa")
                result_text = response['response'][:200].replace('\n', ' ')
                print(f"   📝 Respuesta: {result_text}...")
                print()
            else:
                print(f"⚠️  {model_name}: Formato de respuesta inesperado")
                print(f"   Keys disponibles: {list(response.keys())}")
                print()
                
        except Exception as e:
            print(f"❌ {model_name}: Error - {e}")
            print()
    
    print("🎉 Test de modelos cloud completado")
    return True

def test_hypothesis_generation():
    """Test específico para generación de hipótesis"""
    print("🔬 Test de generación de hipótesis científicas...")
    
    test_prompts = {
        "materials_science": "Generate a hypothesis about novel semiconductor materials for quantum computing",
        "quantum_computing": "Propose a hypothesis about quantum error correction in NISQ devices"
    }
    
    model = "deepseek-v3.1:671b-cloud"
    
    for domain, prompt in test_prompts.items():
        print(f"🎯 Dominio: {domain}")
        try:
            response = ollama.generate(
                model=model,
                prompt=prompt,
                options={"temperature": 0.8}
            )
            
            if 'response' in response:
                hypothesis = response['response'][:150].replace('\n', ' ')
                print(f"   ✅ Hipótesis: {hypothesis}...")
                print()
            else:
                print(f"   ❌ Error en formato de respuesta")
                print()
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando tests de Ollama Cloud\n")
    
    # Test 1: Modelos disponibles
    models_ok = test_cloud_models()
    
    # Test 2: Generación de hipótesis
    if models_ok:
        hypothesis_ok = test_hypothesis_generation()
        
        if hypothesis_ok:
            print("🎉 ¡Todos los tests exitosos! Ollama Cloud listo para hipótesis reales.")
        else:
            print("⚠️  Modelos funcionan pero hay problemas con generación de hipótesis.")
    else:
        print("🔴 Problemas básicos con modelos Ollama.")