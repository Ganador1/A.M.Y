"""
🧪 ATLAS - Análisis Rápido de Pseudociencia No Detectada  
========================================================

Identifiquemos qué pseudociencia está pasando el filtro
"""

from hybrid_confidence_filter import HybridConfidenceFilter
import json

def test_pseudoscience_detection():
    """Test específico de detección de pseudociencia"""
    
    print("🔍 ANÁLISIS DE PSEUDOCIENCIA NO DETECTADA")
    print("=" * 50)
    
    # Casos problemáticos de pseudociencia
    pseudoscience_cases = [
        "Perpetual Motion Engine Using Magnetic Field Amplification for Unlimited Energy",
        "Free Energy Generator Extracting Zero Point Vacuum Energy from Space", 
        "Over Unity Device Achieving 200% Efficiency Through Magnetic Resonance",
        "Anti-Gravity Propulsion System Using Electromagnetic Field Manipulation",
        "Time Travel Communication Device Based on Tachyon Wave Transmission",
        "Crystal Healing Therapy for Cancer Treatment Using Quartz Frequencies",
        "Homeopathic Cure for HIV Through Water Memory Activation",
        "Chakra Balancing Technique for Diabetes Reversal Through Energy Alignment",
        "Essential Oil Treatment for Autism via Aromatic Molecular Healing",
        "Magnetic Therapy Healing Cancer with Neodymium Magnet Arrays",
        "Quantum Consciousness Enhancement Through Meditation State Entanglement",
        "DNA Activation Using Quantum Field Manipulation for Evolution",
        "Suppressed Free Energy Technology Hidden by Government Agencies",
        "Big Pharma Conspiracy to Hide Natural Cancer Cures",
        "Reiki Energy Healing for Multiple Sclerosis Through Spiritual Channels",
        "Acupuncture Meridian Activation for COVID-19 Treatment"
    ]
    
    # Inicializar filtro
    filter_model = HybridConfidenceFilter('balanced_confidence_filter_20250916_195350.pkl')
    
    print("Evaluando casos de pseudociencia...")
    print("-" * 50)
    
    failed_cases = []
    passed_cases = []
    
    for i, case in enumerate(pseudoscience_cases, 1):
        result = filter_model.evaluate_hypothesis({'hypothesis_text': case})
        
        status = "✅" if result['decision'] == 'REJECT' else "❌"
        print(f"{status} [{i:2d}] {case[:50]}...")
        print(f"    Confianza: {result['confidence']:.3f}")
        print(f"    Decisión: {result['decision']}")
        print(f"    Pseudociencia Score: {result['pseudoscience_score']}")
        if result['detected_patterns']:
            patterns = [p[1] for p in result['detected_patterns']]
            print(f"    Patrones: {patterns}")
        print()
        
        if result['decision'] == 'REJECT':
            passed_cases.append({
                'text': case,
                'confidence': result['confidence'],
                'patterns': result['detected_patterns']
            })
        else:
            failed_cases.append({
                'text': case, 
                'confidence': result['confidence'],
                'ml_confidence': result['ml_confidence'],
                'pseudoscience_score': result['pseudoscience_score']
            })
    
    # Resumen
    total = len(pseudoscience_cases)
    detected = len(passed_cases) 
    missed = len(failed_cases)
    
    print("=" * 50)
    print("📊 RESUMEN DE DETECCIÓN:")
    print(f"   Total casos: {total}")
    print(f"   ✅ Detectados: {detected} ({detected/total*100:.1f}%)")
    print(f"   ❌ No detectados: {missed} ({missed/total*100:.1f}%)")
    
    if failed_cases:
        print(f"\n❌ PSEUDOCIENCIA NO DETECTADA:")
        for i, case in enumerate(failed_cases, 1):
            print(f"   {i}. {case['text'][:60]}...")
            print(f"      ML Conf: {case['ml_confidence']:.3f}, Pseudo Score: {case['pseudoscience_score']}")
    
    # Análisis de patrones faltantes
    if failed_cases:
        print(f"\n🔧 ANÁLISIS DE PATRONES FALTANTES:")
        missed_texts = [case['text'].lower() for case in failed_cases]
        
        # Palabras clave que deberían detectarse
        potential_patterns = [
            'energy generator', 'zero point', 'unlimited energy', 'tachyon', 
            'energy alignment', 'aromatic molecular', 'spiritual channels',
            'meridian activation', 'energy healing', 'big pharma'
        ]
        
        for pattern in potential_patterns:
            found_in = [text for text in missed_texts if pattern in text]
            if found_in:
                print(f"   • Agregar patrón: '{pattern}' (encontrado en {len(found_in)} casos)")
        
    return failed_cases, passed_cases

def suggest_pattern_improvements(failed_cases):
    """Sugiere mejoras a los patrones basado en casos fallidos"""
    
    print("\n💡 PATRONES SUGERIDOS PARA AGREGAR:")
    print("-" * 40)
    
    # Analizar textos fallidos para extraer patrones
    failed_texts = [case['text'].lower() for case in failed_cases]
    
    # Nuevos patrones identificados
    suggested_patterns = {
        'impossible_physics': [
            r'unlimited energy',
            r'zero.?point vacuum', 
            r'tachyon wave',
            r'energy generator'
        ],
        'healing_woo': [
            r'energy alignment',
            r'aromatic molecular',
            r'spiritual channels', 
            r'meridian activation',
            r'energy healing'
        ],
        'conspiracy_science': [
            r'big pharma'
        ]
    }
    
    for category, patterns in suggested_patterns.items():
        print(f"   {category.replace('_', ' ').title()}:")
        for pattern in patterns:
            # Ver cuántos casos fallidos contienen este patrón
            matches = sum(1 for text in failed_texts if 
                         __import__('re').search(pattern, text))
            if matches > 0:
                print(f"      • '{pattern}' -> detectaría {matches} casos adicionales")
    
    return suggested_patterns

if __name__ == "__main__":
    failed_cases, passed_cases = test_pseudoscience_detection()
    
    if failed_cases:
        suggest_pattern_improvements(failed_cases)
        
    print(f"\n🎯 CONCLUSIÓN:")
    detection_rate = len(passed_cases) / (len(passed_cases) + len(failed_cases)) * 100
    
    if detection_rate >= 90:
        print(f"   ✅ EXCELENTE detección de pseudociencia ({detection_rate:.1f}%)")
    elif detection_rate >= 80:
        print(f"   🟡 BUENA detección, mejora recomendada ({detection_rate:.1f}%)")  
    else:
        print(f"   ❌ NECESITA MEJORA urgente ({detection_rate:.1f}%)")
        print(f"   💡 Implementar patrones sugeridos arriba")
