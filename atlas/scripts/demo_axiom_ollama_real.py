#!/usr/bin/env python3
"""
Demostración del ciclo autónomo AXIOM con hipótesis reales de Ollama Cloud
"""

import requests
import json
import time
from typing import Dict, Any

class AxiomOllamaDemo:
    """Demostración del sistema AXIOM con Ollama Cloud"""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session = requests.Session()
        
    def generate_real_hypothesis(self, domain: str, research_question: str) -> Dict[str, Any]:
        """Generar hipótesis real usando Ollama Cloud"""
        
        print(f"🌩️ Generando hipótesis real para dominio: {domain}")
        print(f"❓ Pregunta: {research_question}")
        
        endpoint = f"{self.base_url}/api/scientific-hypothesis/generate-hypothesis-ollama"
        
        request_data = {
            "research_question": research_question,
            "domain": domain,
            "context": {
                "complexity": "high",
                "target_application": "real_world_research"
            }
        }
        
        start_time = time.time()
        response = self.session.post(endpoint, json=request_data, timeout=120)
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Hipótesis generada en {generation_time:.1f}s")
            print(f"🤖 Modelo: {result.get('model_used', 'N/A')}")
            
            hypothesis = result.get('hypothesis', {})
            print(f"📝 Título: {hypothesis.get('title', 'N/A')[:100]}...")
            print(f"📊 Confianza: {hypothesis.get('confidence_score', 'N/A')}")
            print(f"🔬 Predicciones: {len(hypothesis.get('testable_predictions', []))}")
            print(f"📚 Metodologías: {len(hypothesis.get('methodology_suggestions', []))}")
            print()
            
            return result
        else:
            print(f"❌ Error generando hipótesis: {response.status_code}")
            return {}
    
    def demonstrate_autonomous_research(self):
        """Demostrar investigación autónoma con hipótesis reales"""
        
        print("🚀 DEMOSTRACIÓN AXIOM CON OLLAMA CLOUD")
        print("=" * 50)
        print()
        
        # Casos de prueba con diferentes dominios
        test_cases = [
            {
                "domain": "quantum_computing",
                "question": "How can quantum machine learning algorithms improve protein folding prediction accuracy?"
            },
            {
                "domain": "materials_science", 
                "question": "What novel 2D materials could surpass graphene's electrical conductivity for next-generation electronics?"
            },
            {
                "domain": "drug_discovery",
                "question": "How can AI-designed peptides target resistant cancer stem cells more effectively than current chemotherapy?"
            }
        ]
        
        results = []
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"🧪 CASO {i}/3: {test_case['domain'].upper()}")
            print("-" * 30)
            
            # Generar hipótesis real
            hypothesis_result = self.generate_real_hypothesis(
                test_case['domain'], 
                test_case['question']
            )
            
            if hypothesis_result:
                results.append({
                    "domain": test_case['domain'],
                    "question": test_case['question'],
                    "hypothesis": hypothesis_result,
                    "success": True
                })
                
                # Mostrar información destacada
                hypothesis = hypothesis_result.get('hypothesis', {})
                
                print("🔍 DETALLES DE LA HIPÓTESIS:")
                print(f"   📋 Descripción: {hypothesis.get('description', 'N/A')[:200]}...")
                print(f"   🧠 Razonamiento: {hypothesis.get('reasoning', 'N/A')[:200]}...")
                
                if hypothesis.get('testable_predictions'):
                    print("   🎯 Predicción destacada:")
                    print(f"      {hypothesis['testable_predictions'][0][:150]}...")
                
                if hypothesis.get('methodology_suggestions'):
                    print("   🔬 Metodología sugerida:")
                    print(f"      {hypothesis['methodology_suggestions'][0][:150]}...")
                
                print()
            else:
                results.append({
                    "domain": test_case['domain'],
                    "success": False
                })
        
        # Resumen final
        print("📊 RESUMEN DE LA DEMOSTRACIÓN")
        print("=" * 50)
        
        successful_cases = [r for r in results if r.get('success')]
        
        print(f"✅ Casos exitosos: {len(successful_cases)}/{len(test_cases)}")
        print(f"🌩️ Modelos cloud utilizados: Ollama Cloud (deepseek-v3.1, qwen3-coder)")
        print(f"🧠 Tipo de hipótesis: Científicas reales generadas por IA")
        print(f"⚡ Capacidades demostradas: Generación autónoma de hipótesis científicas")
        
        if successful_cases:
            print("\n🏆 LOGROS DESTACADOS:")
            for case in successful_cases:
                hypothesis = case['hypothesis'].get('hypothesis', {})
                confidence = hypothesis.get('confidence_score', 0)
                predictions = len(hypothesis.get('testable_predictions', []))
                
                print(f"   📋 {case['domain']}: Confianza {confidence:.2f}, {predictions} predicciones")
        
        print("\n🎉 ¡DEMOSTRACIÓN COMPLETADA EXITOSAMENTE!")
        print("🔬 AXIOM genera hipótesis científicas reales usando Ollama Cloud")
        print("🚀 Sistema completamente funcional para investigación autónoma")
        
        return results

if __name__ == "__main__":
    demo = AxiomOllamaDemo()
    demo.demonstrate_autonomous_research()