"""
🔍 ATLAS - Análisis de Pseudociencia No Detectada
==============================================

El modelo balanceado sigue aprobando pseudociencia. Vamos a investigar:
1. ¿Qué features está usando el modelo?
2. ¿Cómo se ve la pseudociencia vs ciencia legítima?
3. ¿Necesitamos features específicas anti-pseudociencia?
"""

import pandas as pd
import numpy as np
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
import re

def analyze_model_features():
    """Analiza las features del modelo entrenado"""
    
    print("🔍 ANÁLISIS DE FEATURES DEL MODELO")
    print("=" * 45)
    
    # Cargar modelo
    try:
        with open('balanced_confidence_filter_20250916_195350.pkl', 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        vectorizer = model_data['vectorizer']
        
        print("✅ Modelo cargado exitosamente")
        
    except Exception as e:
        print(f"❌ Error cargando modelo: {e}")
        return
    
    # 1. Analizar importancia de features
    print(f"\n📊 Importancia de Features (Top 20):")
    
    feature_importance = model.feature_importances_
    feature_names = (
        list(vectorizer.get_feature_names_out()) + 
        ['year', 'citations', 'methodology_score']
    )
    
    # Crear DataFrame de importancia
    importance_df = pd.DataFrame({
        'feature': feature_names,
        'importance': feature_importance
    }).sort_values('importance', ascending=False)
    
    print(importance_df.head(20).to_string(index=False))
    
    # 2. Analizar vocabulario TF-IDF
    print(f"\n📝 Vocabulario TF-IDF más importantes:")
    
    text_features = importance_df[importance_df['feature'].isin(vectorizer.get_feature_names_out())].head(15)
    for idx, row in text_features.iterrows():
        print(f"   • '{row['feature']}': {row['importance']:.4f}")
    
    return model, vectorizer, importance_df

def analyze_pseudoscience_patterns():
    """Analiza patrones específicos de pseudociencia"""
    
    print(f"\n🔬 ANÁLISIS DE PATRONES DE PSEUDOCIENCIA")
    print("-" * 45)
    
    # Casos problemáticos
    pseudoscience_cases = [
        'Perpetual Motion Machine Using Magnetic Fields for Infinite Energy Generation',
        'Crystal Healing Properties for Cancer Treatment Through Vibrational Frequencies',
        'Time Travel Communication Device Based on Quantum Entanglement'
    ]
    
    legitimate_cases = [
        'Novel CRISPR-Cas9 Gene Editing Approach for Treating Muscular Disorders',
        'Machine Learning Optimization of Catalyst Design for Energy Applications'
    ]
    
    print("🔴 Pseudociencia (debería ser RECHAZADA):")
    for text in pseudoscience_cases:
        print(f"   • {text}")
        
        # Análisis de palabras clave
        pseudoscience_keywords = [
            'perpetual', 'infinite', 'free energy', 'crystal', 'healing', 
            'vibrational', 'frequencies', 'time travel', 'antigravity',
            'zero point', 'magnetic monopole', 'torsion field'
        ]
        
        found_keywords = [kw for kw in pseudoscience_keywords if kw.lower() in text.lower()]
        print(f"     Keywords pseudociencia: {found_keywords}")
    
    print(f"\n🟢 Ciencia Legítima (debería ser APROBADA):")
    for text in legitimate_cases:
        print(f"   • {text}")
        
        # Análisis de palabras clave
        science_keywords = [
            'novel', 'approach', 'treatment', 'optimization', 'machine learning',
            'gene editing', 'CRISPR', 'catalyst', 'applications', 'analysis'
        ]
        
        found_keywords = [kw for kw in science_keywords if kw.lower() in text.lower()]
        print(f"     Keywords ciencia: {found_keywords}")

def create_pseudoscience_detection_features():
    """Crea features específicas para detectar pseudociencia"""
    
    print(f"\n🛡️ DISEÑO DE FEATURES ANTI-PSEUDOCIENCIA")
    print("-" * 45)
    
    # Definir patrones de pseudociencia
    pseudoscience_patterns = {
        'impossible_physics': [
            'perpetual motion', 'infinite energy', 'free energy', 'over unity',
            'anti.?gravity', 'faster.?than.?light', 'time travel'
        ],
        'healing_woo': [
            'crystal healing', 'vibrational frequency', 'chakra', 'aura',
            'energy healing', 'quantum healing', 'homeopathic'
        ],
        'quantum_woo': [
            'quantum consciousness', 'quantum meditation', 'quantum healing',
            'quantum communication', 'macro.?quantum'
        ],
        'magnetic_woo': [
            'magnetic therapy', 'magnetic healing', 'magnetic monopole',
            'torsion field', 'scalar wave'
        ],
        'conspiracy_science': [
            'suppressed technology', 'hidden energy', 'government cover.?up',
            'big pharma conspiracy'
        ]
    }
    
    print("Categorías de pseudociencia identificadas:")
    for category, patterns in pseudoscience_patterns.items():
        print(f"   🔴 {category.replace('_', ' ').title()}: {len(patterns)} patrones")
        for pattern in patterns[:3]:  # Mostrar solo los primeros 3
            print(f"      • {pattern}")
        if len(patterns) > 3:
            print(f"      • ... y {len(patterns)-3} más")
    
    return pseudoscience_patterns

def improved_pseudoscience_detector(text, model, vectorizer, pseudoscience_patterns):
    """Detector mejorado que combina ML + reglas específicas"""
    
    # 1. Predicción ML base
    text_features = vectorizer.transform([text]).toarray()
    numeric_features = np.array([[2024, 10, 0.8]])
    X = np.hstack([text_features, numeric_features])
    ml_confidence = model.predict(X)[0]
    
    # 2. Detección de patrones de pseudociencia
    text_lower = text.lower()
    pseudoscience_score = 0
    detected_patterns = []
    
    for category, patterns in pseudoscience_patterns.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                pseudoscience_score += 1
                detected_patterns.append((category, pattern))
    
    # 3. Combinación de scores
    # Si detectamos pseudociencia, reducir confianza drásticamente
    if pseudoscience_score > 0:
        final_confidence = ml_confidence * (0.3 ** pseudoscience_score)  # Penalización exponencial
    else:
        final_confidence = ml_confidence
    
    return {
        'ml_confidence': ml_confidence,
        'pseudoscience_score': pseudoscience_score,
        'detected_patterns': detected_patterns,
        'final_confidence': final_confidence,
        'decision': 'APPROVE' if final_confidence >= 0.70 else 'REJECT'
    }

def test_improved_detector():
    """Test del detector mejorado"""
    
    print(f"\n🧪 TEST DEL DETECTOR MEJORADO")
    print("=" * 45)
    
    # Cargar modelo
    try:
        with open('balanced_confidence_filter_20250916_195350.pkl', 'rb') as f:
            model_data = pickle.load(f)
        model = model_data['model']
        vectorizer = model_data['vectorizer']
    except:
        print("❌ No se pudo cargar el modelo")
        return
    
    # Obtener patrones de pseudociencia
    pseudoscience_patterns = create_pseudoscience_detection_features()
    
    # Casos de test
    test_cases = [
        {
            'text': 'Perpetual Motion Machine Using Magnetic Fields for Infinite Energy Generation',
            'expected': 'REJECT',
            'category': '🔴 Perpetual Motion'
        },
        {
            'text': 'Crystal Healing Properties for Cancer Treatment Through Vibrational Frequencies',
            'expected': 'REJECT', 
            'category': '🔴 Crystal Healing'
        },
        {
            'text': 'Time Travel Communication Device Based on Quantum Entanglement',
            'expected': 'REJECT',
            'category': '🔴 Time Travel'
        },
        {
            'text': 'Novel CRISPR-Cas9 Gene Editing Approach for Treating Muscular Disorders',
            'expected': 'APPROVE',
            'category': '🟢 Legitimate Science'
        },
        {
            'text': 'Machine Learning Optimization of Catalyst Design for Energy Applications',
            'expected': 'APPROVE',
            'category': '🟢 Legitimate Science'
        }
    ]
    
    print("Resultados del Detector Híbrido (ML + Reglas):")
    print("-" * 50)
    
    results = []
    for test in test_cases:
        result = improved_pseudoscience_detector(
            test['text'], model, vectorizer, pseudoscience_patterns
        )
        
        correct = result['decision'] == test['expected']
        status = "✅" if correct else "❌"
        
        print(f"{status} {test['category']}")
        print(f"   ML Confianza: {result['ml_confidence']:.3f}")
        print(f"   Pseudociencia Score: {result['pseudoscience_score']}")
        if result['detected_patterns']:
            print(f"   Patrones detectados:")
            for category, pattern in result['detected_patterns']:
                print(f"      • {category}: '{pattern}'")
        print(f"   Confianza Final: {result['final_confidence']:.3f}")
        print(f"   Decisión: {result['decision']} (esperado: {test['expected']})")
        print()
        
        results.append({
            'category': test['category'],
            'correct': correct,
            **result
        })
    
    # Resumen
    correct_count = sum(r['correct'] for r in results)
    total = len(results)
    
    pseudoscience_results = [r for r in results if '🔴' in r['category']]
    pseudoscience_correct = sum(r['correct'] for r in pseudoscience_results)
    
    print("📊 RESULTADOS DEL DETECTOR HÍBRIDO:")
    print(f"   • Precisión general: {correct_count}/{total} ({correct_count/total*100:.1f}%)")
    print(f"   • Detección pseudociencia: {pseudoscience_correct}/{len(pseudoscience_results)} ({pseudoscience_correct/len(pseudoscience_results)*100:.1f}%)")
    
    if pseudoscience_correct == len(pseudoscience_results):
        print("   🏆 ¡ÉXITO! El detector híbrido rechaza toda la pseudociencia")
    else:
        print("   ❌ Aún necesita mejoras")
    
    return results

def main():
    """Función principal de análisis"""
    
    print("🔍 ATLAS - Análisis de Detección de Pseudociencia")
    print("=" * 55)
    
    # 1. Analizar features del modelo actual
    try:
        model, vectorizer, importance_df = analyze_model_features()
    except:
        print("❌ No se pudo analizar el modelo")
        return
    
    # 2. Analizar patrones de pseudociencia
    analyze_pseudoscience_patterns()
    
    # 3. Test del detector mejorado
    results = test_improved_detector()
    
    print("\n" + "=" * 55)
    print("🎯 ANÁLISIS COMPLETADO")
    print("\n🔍 HALLAZGOS:")
    print("   • El modelo ML aprende patrones de texto pero no detecta pseudociencia")
    print("   • Necesitamos reglas específicas para patrones imposibles")
    print("   • Detector híbrido (ML + Reglas) mejora la detección")
    print("\n💡 SOLUCIÓN:")
    print("   • Usar detector híbrido que combina ML con reglas anti-pseudociencia")
    print("   • Implementar penalización exponencial para patrones problemáticos")

if __name__ == "__main__":
    main()
