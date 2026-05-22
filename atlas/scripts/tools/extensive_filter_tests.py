"""
🧪 ATLAS - Pruebas Extensas del Filtro Híbrido
=============================================

Test masivo del filtro híbrido con:
1. Más casos de pseudociencia
2. Papers científicos reales  
3. Casos límite y ambiguos
4. Estadísticas detalladas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hybrid_confidence_filter import HybridConfidenceFilter
import pandas as pd
import numpy as np
import json
from datetime import datetime

def create_extensive_test_dataset():
    """Crea dataset extenso de pruebas"""
    
    print("🧪 Creando dataset extenso de pruebas...")
    
    test_cases = []
    
    # 1. PSEUDOCIENCIA CLÁSICA (debería ser RECHAZADA)
    pseudoscience_cases = [
        # Física imposible
        "Perpetual Motion Engine Using Magnetic Field Amplification for Unlimited Energy",
        "Free Energy Generator Extracting Zero Point Vacuum Energy from Space",
        "Over Unity Device Achieving 200% Efficiency Through Magnetic Resonance",
        "Anti-Gravity Propulsion System Using Electromagnetic Field Manipulation",
        "Time Travel Communication Device Based on Tachyon Wave Transmission",
        "Faster Than Light Communication via Quantum Entanglement Tunneling",
        "Infinite Energy Machine Using Gyroscopic Momentum Conservation",
        
        # Medicina alternativa sin evidencia
        "Crystal Healing Therapy for Cancer Treatment Using Quartz Frequencies",
        "Homeopathic Cure for HIV Through Water Memory Activation",
        "Chakra Balancing Technique for Diabetes Reversal Through Energy Alignment",
        "Essential Oil Treatment for Autism via Aromatic Molecular Healing",
        "Magnetic Therapy Healing Cancer with Neodymium Magnet Arrays",
        "Reiki Energy Healing for Multiple Sclerosis Through Spiritual Channels",
        "Acupuncture Meridian Activation for COVID-19 Treatment",
        
        # Quantum woo
        "Quantum Consciousness Enhancement Through Meditation State Entanglement",  
        "DNA Activation Using Quantum Field Manipulation for Evolution",
        "Quantum Healing Frequencies for Cellular Regeneration Enhancement",
        "Consciousness-Based Quantum Computing Using Human Brain Waves",
        "Quantum Memory Storage in Water Molecules for Information Transfer",
        
        # Conspiracies
        "Suppressed Free Energy Technology Hidden by Government Agencies",
        "Big Pharma Conspiracy to Hide Natural Cancer Cures",
        "Mainstream Science Cover-up of Antigravity Technology Research"
    ]
    
    for text in pseudoscience_cases:
        test_cases.append({
            'hypothesis_text': text,
            'expected': 'REJECT',
            'category': 'pseudoscience',
            'subcategory': 'classic_woo'
        })
    
    # 2. CIENCIA LEGÍTIMA (debería ser APROBADA)
    legitimate_science = [
        # Medicina/Biología
        "CRISPR-Cas9 Gene Editing Approach for Treating Sickle Cell Disease",
        "Machine Learning Analysis of Protein Folding Patterns in Alzheimer Disease",
        "Immunotherapy Treatment Using CAR-T Cells for Lymphoma Patients",
        "Deep Learning Model for Early Cancer Detection from Medical Imaging",
        "Biomarker Discovery for Parkinson Disease Using Mass Spectrometry Analysis",
        "Gene Therapy Vector Development for Inherited Retinal Dystrophies",
        "Personalized Medicine Approach Using Pharmacogenomic Testing",
        
        # Física/Química
        "Quantum Computing Algorithm for Molecular Simulation Optimization",
        "Superconducting Materials Research for Energy Storage Applications",
        "Catalytic CO2 Conversion to Methanol Using Metal-Organic Frameworks",
        "Solar Cell Efficiency Enhancement Through Perovskite Layer Engineering",
        "Battery Technology Improvement Using Solid Electrolyte Materials",
        "Nuclear Fusion Plasma Confinement Using Magnetic Field Control",
        "Nanoparticle Drug Delivery System for Targeted Cancer Therapy",
        
        # Ingeniería/Tecnología
        "Artificial Intelligence Algorithm for Climate Change Modeling",
        "Renewable Energy Grid Optimization Using Smart Grid Technology",
        "Additive Manufacturing Process for Aerospace Component Production",
        "Autonomous Vehicle Safety System Using Computer Vision",
        "Robotics Application for Precision Agriculture Monitoring",
        "5G Network Optimization for Internet of Things Connectivity",
        "Blockchain Technology for Supply Chain Transparency"
    ]
    
    for text in legitimate_science:
        test_cases.append({
            'hypothesis_text': text,
            'expected': 'APPROVE',
            'category': 'legitimate_science',
            'subcategory': 'established_fields'
        })
    
    # 3. CASOS LÍMITE (pueden ir en cualquier dirección)
    edge_cases = [
        # Ciencia especulativa pero plausible
        {
            'hypothesis_text': 'Theoretical Framework for Dark Matter Detection Using Novel Detector Design',
            'expected': 'APPROVE',
            'category': 'edge_case',
            'subcategory': 'speculative_but_valid'
        },
        {
            'hypothesis_text': 'Extraterrestrial Life Detection Using Radio Signal Pattern Analysis',
            'expected': 'APPROVE', 
            'category': 'edge_case',
            'subcategory': 'speculative_but_valid'
        },
        # Tecnología emergente  
        {
            'hypothesis_text': 'Brain-Computer Interface for Paralyzed Patient Communication',
            'expected': 'APPROVE',
            'category': 'edge_case', 
            'subcategory': 'emerging_technology'
        },
        {
            'hypothesis_text': 'Artificial General Intelligence Development Using Neural Architecture Search',
            'expected': 'APPROVE',
            'category': 'edge_case',
            'subcategory': 'emerging_technology'  
        },
        # Medicina controversial pero científica
        {
            'hypothesis_text': 'Psychedelic Therapy for Treatment-Resistant Depression Clinical Trial',
            'expected': 'APPROVE',
            'category': 'edge_case',
            'subcategory': 'controversial_but_scientific'
        }
    ]
    
    test_cases.extend(edge_cases)
    
    # 4. CASOS AMBIGUOS (texto científico pero aplicación problemática)
    ambiguous_cases = [
        {
            'hypothesis_text': 'Quantum Effects in Biological Systems for Consciousness Research',
            'expected': 'APPROVE',  # Legítimo campo de investigación
            'category': 'ambiguous',
            'subcategory': 'quantum_biology'
        },
        {
            'hypothesis_text': 'Electromagnetic Field Effects on Cellular Biology in Medical Applications', 
            'expected': 'APPROVE',  # Campo legítimo de investigación
            'category': 'ambiguous',
            'subcategory': 'bioelectromagnetics'
        },
        {
            'hypothesis_text': 'Alternative Medicine Integration in Conventional Healthcare Systems',
            'expected': 'APPROVE',  # Investigación de políticas de salud
            'category': 'ambiguous', 
            'subcategory': 'healthcare_policy'
        }
    ]
    
    test_cases.extend(ambiguous_cases)
    
    print(f"✅ Dataset creado: {len(test_cases)} casos de prueba")
    print(f"   🔴 Pseudociencia: {len(pseudoscience_cases)}")
    print(f"   🟢 Ciencia legítima: {len(legitimate_science)}")
    print(f"   🟡 Casos límite: {len(edge_cases)}")
    print(f"   🟠 Casos ambiguos: {len(ambiguous_cases)}")
    
    return test_cases

def run_extensive_tests():
    """Ejecuta pruebas extensas del filtro híbrido"""
    
    print("🚀 ATLAS - Pruebas Extensas del Filtro Híbrido")
    print("=" * 55)
    
    # 1. Crear dataset de pruebas
    test_cases = create_extensive_test_dataset()
    
    # 2. Inicializar filtro
    print(f"\n🛡️ Inicializando filtro híbrido...")
    filter_model = HybridConfidenceFilter('balanced_confidence_filter_20250916_195350.pkl')
    
    if not filter_model.model:
        print("❌ No se pudo cargar el modelo. Continuando con reglas únicamente...")
    
    # 3. Ejecutar evaluaciones
    print(f"\n🔍 Evaluando {len(test_cases)} casos...")
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        result = filter_model.evaluate_hypothesis(test_case)
        
        # Agregar información del test
        result.update({
            'test_id': i,
            'expected': test_case['expected'],
            'category': test_case['category'],
            'subcategory': test_case['subcategory'],
            'correct': result['decision'] == test_case['expected']
        })
        
        results.append(result)
        
        if i % 10 == 0:
            print(f"   • Procesados: {i}/{len(test_cases)}")
    
    # 4. Análisis de resultados
    print(f"\n📊 ANÁLISIS DE RESULTADOS")
    print("-" * 40)
    
    # Estadísticas generales
    total = len(results)
    correct = sum(r['correct'] for r in results)
    accuracy = correct / total * 100
    
    print(f"Precisión General: {correct}/{total} ({accuracy:.1f}%)")
    
    # Por categorías
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'correct': 0, 'cases': []}
        categories[cat]['total'] += 1
        categories[cat]['correct'] += result['correct']
        categories[cat]['cases'].append(result)
    
    print(f"\nPor Categorías:")
    for cat, stats in categories.items():
        acc = stats['correct'] / stats['total'] * 100
        print(f"   • {cat}: {stats['correct']}/{stats['total']} ({acc:.1f}%)")
    
    # Casos incorrectos
    incorrect_cases = [r for r in results if not r['correct']]
    if incorrect_cases:
        print(f"\n❌ CASOS INCORRECTOS ({len(incorrect_cases)}):")
        for i, case in enumerate(incorrect_cases[:5]):  # Mostrar solo los primeros 5
            # Buscar el texto original en test_cases
            original_case = next((tc for tc in test_cases if tc['hypothesis_text'] in str(case)), None)
            if original_case:
                text = original_case['hypothesis_text']
            else:
                text = "Texto no encontrado"
            
            print(f"   {i+1}. {text[:60]}...")
            print(f"      Esperado: {case['expected']}, Obtenido: {case['decision']}")
            print(f"      Confianza: {case['confidence']:.3f}, Razón: {case['reason']}")
            print()
    
    # Estadísticas de pseudociencia
    pseudoscience_results = [r for r in results if r['category'] == 'pseudoscience']
    if pseudoscience_results:
        pseudo_correct = sum(r['correct'] for r in pseudoscience_results)
        pseudo_acc = pseudo_correct / len(pseudoscience_results) * 100
        print(f"🎯 DETECCIÓN DE PSEUDOCIENCIA:")
        print(f"   Precisión: {pseudo_correct}/{len(pseudoscience_results)} ({pseudo_acc:.1f}%)")
        
        # Casos de pseudociencia mal clasificados
        pseudo_errors = [r for r in pseudoscience_results if not r['correct']]
        if pseudo_errors:
            print(f"   ❌ Pseudociencia NO detectada:")
            for case in pseudo_errors:
                print(f"      • {case['hypothesis_text'][:50]}... (conf: {case['confidence']:.3f})")
    
    # Guardar resultados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"extensive_filter_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'test_summary': {
                'total_cases': total,
                'correct_predictions': correct,
                'accuracy_percentage': accuracy
            },
            'category_breakdown': {
                cat: {
                    'total': stats['total'],
                    'correct': stats['correct'], 
                    'accuracy': stats['correct'] / stats['total'] * 100
                }
                for cat, stats in categories.items()
            },
            'detailed_results': results
        }, f, indent=2)
    
    print(f"\n💾 Resultados guardados: {results_file}")
    
    # Conclusión
    print(f"\n" + "=" * 55)
    print(f"🎯 PRUEBAS EXTENSAS COMPLETADAS")
    
    if accuracy >= 90:
        print(f"✅ EXCELENTE: {accuracy:.1f}% precisión")
    elif accuracy >= 80:
        print(f"🟡 BUENO: {accuracy:.1f}% precisión")
    else:
        print(f"❌ NECESITA MEJORA: {accuracy:.1f}% precisión")
    
    # Recomendaciones
    if len(incorrect_cases) > 0:
        print(f"\n💡 RECOMENDACIONES:")
        if any(r['category'] == 'pseudoscience' and not r['correct'] for r in results):
            print(f"   • Añadir más patrones anti-pseudociencia")
        if any(r['category'] == 'legitimate_science' and not r['correct'] for r in results):
            print(f"   • Revisar reglas que rechazан ciencia legítima")
        if any(r['category'] == 'ambiguous' and not r['correct'] for r in results):
            print(f"   • Casos ambiguos requieren análisis manual")
    
    return results

if __name__ == "__main__":
    results = run_extensive_tests()
