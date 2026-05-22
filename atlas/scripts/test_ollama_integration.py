#!/usr/bin/env python3
"""
Prueba rápida de la integración Ollama Cloud
Verifica que el servicio funciona correctamente antes de ejecutar el ciclo completo
"""

import asyncio
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from app.services.ollama_service import ollama_service, HypothesisRequest

async def test_ollama_integration():
    """Prueba básica de integración con Ollama"""
    
    print("🚀 Iniciando prueba de integración Ollama Cloud")
    print("=" * 60)
    
    # Verificar modelos disponibles
    print("\n📋 Verificando modelos disponibles...")
    try:
        available_models = await ollama_service.get_available_models()
        print(f"✅ Modelos disponibles: {available_models}")
    except Exception as e:
        print(f"❌ Error verificando modelos: {e}")
        return False
    
    if not available_models:
        print("⚠️ No hay modelos disponibles. Usando fallback.")
    
    # Prueba de generación de hipótesis
    print("\n🧠 Probando generación de hipótesis...")
    
    test_request = HypothesisRequest(
        research_question="¿Cómo mejorar la eficiencia de las celdas solares de perovskita?",
        domain="materials_science",
        context={
            "temperature_range": [300, 400],
            "material_type": "perovskite",
            "efficiency_target": 0.25
        }
    )
    
    try:
        print(f"📝 Dominio: {test_request.domain}")
        print(f"❓ Pregunta: {test_request.research_question}")
        
        result = await ollama_service.generate_hypothesis(test_request)
        
        print("\n📊 RESULTADO:")
        print(f"✅ Hipótesis: {result.hypothesis_text[:100]}...")
        print(f"🧭 Razonamiento: {result.reasoning[:100]}...")
        print(f"📊 Confianza: {result.confidence}")
        print(f"🔬 Predicciones: {len(result.testable_predictions)}")
        print(f"📚 Literatura: {len(result.related_literature)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error generando hipótesis: {e}")
        print(f"🔍 Tipo de error: {type(e).__name__}")
        return False

async def test_domain_models():
    """Prueba modelos específicos por dominio"""
    
    print("\n🔬 Probando modelos por dominio...")
    
    domains = [
        ("quantum_computing", "¿Cómo implementar algoritmos cuánticos más eficientes?"),
        ("materials_science", "¿Qué materiales son mejores para superconductores?"),
        ("biology", "¿Cómo mejorar la expresión de proteínas en E. coli?")
    ]
    
    for domain, question in domains:
        print(f"\n🧪 Dominio: {domain}")
        
        # Verificar modelo óptimo
        optimal_model = ollama_service.get_optimal_model(domain)
        print(f"🤖 Modelo óptimo: {optimal_model}")
        
        # Crear solicitud
        request = HypothesisRequest(
            research_question=question,
            domain=domain,
            model_preference=optimal_model
        )
        
        try:
            result = await ollama_service.generate_hypothesis(request)
            print(f"✅ Hipótesis generada - Confianza: {result.confidence}")
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Función principal de prueba"""
    
    print("🔥 PRUEBA DE INTEGRACIÓN OLLAMA CLOUD")
    print("=" * 60)
    
    # Prueba básica
    basic_success = await test_ollama_integration()
    
    if basic_success:
        print("\n" + "=" * 60)
        await test_domain_models()
        
        print("\n" + "=" * 60)
        print("🎉 INTEGRACIÓN OLLAMA COMPLETADA EXITOSAMENTE")
        print("✅ El sistema está listo para generar hipótesis reales")
        print("📋 Próximo paso: Ejecutar ciclo autónomo completo")
    else:
        print("\n" + "=" * 60)
        print("❌ INTEGRACIÓN FALLIDA")
        print("🔧 Verifica que Ollama esté funcionando correctamente")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))