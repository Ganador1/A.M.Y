"""
Experimento de Descubrimiento Causal - Dataset de Salud Pública
================================================================

Este experimento utiliza el servicio de descubrimiento causal de AXIOM
para analizar relaciones causales en datos de salud pública.

Dataset: Heart Disease UCI Dataset
Objetivo: Descubrir relaciones causales entre factores de riesgo y enfermedad cardíaca
"""

import requests
import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.preprocessing import StandardScaler
import json
import time
from typing import Dict, List, Any

class CausalDiscoveryExperiment:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {}
        
    def generate_heart_disease_data(self, n_samples: int = 500) -> pd.DataFrame:
        """
        Genera datos sintéticos de enfermedad cardíaca con relaciones causales conocidas
        """
        np.random.seed(42)
        
        # Variables causales conocidas
        age = np.random.normal(55, 15, n_samples)
        age = np.clip(age, 20, 80)
        
        # El colesterol está influenciado por la edad
        cholesterol = 150 + 2 * age + np.random.normal(0, 30, n_samples)
        cholesterol = np.clip(cholesterol, 100, 400)
        
        # La presión arterial está influenciada por edad y colesterol
        blood_pressure = 80 + 0.5 * age + 0.1 * cholesterol + np.random.normal(0, 15, n_samples)
        blood_pressure = np.clip(blood_pressure, 60, 200)
        
        # El ejercicio está inversamente relacionado con la edad
        exercise = np.random.binomial(1, 1 / (1 + np.exp((age - 50) / 10)), n_samples)
        
        # El tabaquismo es independiente pero afecta otros factores
        smoking = np.random.binomial(1, 0.3, n_samples)
        
        # La enfermedad cardíaca depende de múltiples factores
        heart_disease_prob = (
            0.1 +
            0.02 * (age - 40) +
            0.005 * (cholesterol - 200) +
            0.01 * (blood_pressure - 120) +
            0.3 * smoking -
            0.2 * exercise
        )
        heart_disease_prob = np.clip(heart_disease_prob, 0, 1)
        heart_disease = np.random.binomial(1, heart_disease_prob, n_samples)
        
        return pd.DataFrame({
            'age': age,
            'cholesterol': cholesterol,
            'blood_pressure': blood_pressure,
            'exercise': exercise,
            'smoking': smoking,
            'heart_disease': heart_disease
        })
    
    def test_causal_discovery(self) -> Dict[str, Any]:
        """
        Prueba el servicio de descubrimiento causal
        """
        print("🔬 Iniciando experimento de descubrimiento causal...")
        
        # Generar datos
        data = self.generate_heart_disease_data()
        print(f"📊 Datos generados: {len(data)} muestras, {len(data.columns)} variables")
        
        # Preparar datos para el API
        payload = {
            "data": data.to_dict('records'),
            "variables": list(data.columns),
            "target_variable": "heart_disease",
            "algorithm": "pc",
            "significance_level": 0.05
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                f"{self.base_url}/causal/discover",
                json=payload,
                timeout=60
            )
            
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Analizar resultados
                causal_graph = result.get('causal_graph', {})
                relationships = result.get('relationships', [])
                
                print("✅ Descubrimiento causal completado")
                print(f"⏱️  Tiempo de ejecución: {execution_time:.2f} segundos")
                print(f"🔗 Relaciones causales encontradas: {len(relationships)}")
                
                # Validar relaciones causales conocidas
                expected_relationships = [
                    ('age', 'cholesterol'),
                    ('age', 'blood_pressure'),
                    ('cholesterol', 'blood_pressure'),
                    ('smoking', 'heart_disease'),
                    ('exercise', 'heart_disease')
                ]
                
                found_relationships = [(rel['cause'], rel['effect']) for rel in relationships]
                
                validation_score = 0
                for expected in expected_relationships:
                    if expected in found_relationships or (expected[1], expected[0]) in found_relationships:
                        validation_score += 1
                
                validation_percentage = (validation_score / len(expected_relationships)) * 100
                
                return {
                    'status': 'success',
                    'execution_time': execution_time,
                    'relationships_found': len(relationships),
                    'causal_graph': causal_graph,
                    'relationships': relationships,
                    'validation_score': validation_percentage,
                    'data_samples': len(data),
                    'variables': len(data.columns)
                }
            else:
                print(f"❌ Error en el servicio: {response.status_code}")
                return {
                    'status': 'error',
                    'error_code': response.status_code,
                    'error_message': response.text
                }
                
        except Exception as e:
            print(f"❌ Error en la conexión: {str(e)}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def run_experiment(self) -> Dict[str, Any]:
        """
        Ejecuta el experimento completo
        """
        print("🧪 EXPERIMENTO DE DESCUBRIMIENTO CAUSAL")
        print("=" * 50)
        
        results = self.test_causal_discovery()
        
        if results['status'] == 'success':
            print("\n📈 RESULTADOS DEL EXPERIMENTO:")
            print(f"✅ Validación de relaciones causales: {results['validation_score']:.1f}%")
            print(f"⚡ Rendimiento: {results['execution_time']:.2f}s para {results['data_samples']} muestras")
            print(f"🔍 Relaciones descubiertas: {results['relationships_found']}")
            
            # Criterios de éxito científico
            success_criteria = {
                'validation_score': results['validation_score'] >= 60,  # Al menos 60% de relaciones correctas
                'performance': results['execution_time'] < 30,  # Menos de 30 segundos
                'completeness': results['relationships_found'] >= 3  # Al menos 3 relaciones
            }
            
            overall_success = all(success_criteria.values())
            
            print(f"\n🎯 CRITERIOS DE ÉXITO CIENTÍFICO:")
            for criterion, passed in success_criteria.items():
                status = "✅" if passed else "❌"
                print(f"{status} {criterion}: {passed}")
            
            print(f"\n🏆 RESULTADO GENERAL: {'EXITOSO' if overall_success else 'REQUIERE MEJORAS'}")
            
            results['scientific_validation'] = {
                'criteria': success_criteria,
                'overall_success': overall_success
            }
        
        return results

if __name__ == "__main__":
    experiment = CausalDiscoveryExperiment()
    results = experiment.run_experiment()
    
    # Guardar resultados
    with open('./experiments/causal_discovery_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Resultados guardados en: causal_discovery_results.json")