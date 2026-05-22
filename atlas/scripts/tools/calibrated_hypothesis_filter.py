#!/usr/bin/env python3
"""
🎯 CALIBRATED HYPOTHESIS FILTER
Filtro calibrado usando el paper implausible como referencia
"""

import json
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

def load_training_data():
    """Carga los datos de entrenamiento"""
    data = []
    try:
        with open('data/final_llm_classifications.jsonl', 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    item = json.loads(line.strip())
                    if item.get('confidence') is not None:
                        data.append(item)
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print("❌ No se encontraron datos de entrenamiento")
        return None
    
    return pd.DataFrame(data) if data else None

def extract_simple_features(df_or_dict, tfidf=None, scaler=None, fit=False):
    """Extrae features simples para el modelo"""
    
    # Convertir input a DataFrame
    if isinstance(df_or_dict, dict):
        df = pd.DataFrame([df_or_dict])
    elif isinstance(df_or_dict, list):
        df = pd.DataFrame(df_or_dict)
    else:
        df = df_or_dict.copy()
    
    # Texto combinado
    df['combined_text'] = df['title'].fillna('') + ' ' + df['abstract'].fillna('')
    
    # TF-IDF features (reducido)
    if fit or tfidf is None:
        tfidf = TfidfVectorizer(
            max_features=100,
            stop_words='english',
            ngram_range=(1, 1)
        )
        text_features = tfidf.fit_transform(df['combined_text']).toarray()
    else:
        text_features = tfidf.transform(df['combined_text']).toarray()
    
    # Features básicas
    features = []
    
    # Length features
    title_len = df['title'].fillna('').str.len().values
    abstract_len = df['abstract'].fillna('').str.len().values
    combined_len = df['combined_text'].str.len().values
    
    features.extend([title_len, abstract_len, combined_len])
    
    # Domain encoding (simplificado)
    domain_openalex = (df['domain'] == 'openalex').astype(int).values
    domain_arxiv = (df['domain'] == 'arxiv').astype(int).values
    domain_pubmed = (df['domain'] == 'pubmed').astype(int).values
    
    features.extend([domain_openalex, domain_arxiv, domain_pubmed])
    
    # Combinar features
    numerical_features = np.column_stack(features)
    all_features = np.hstack([text_features, numerical_features])
    
    # Escalar
    if fit or scaler is None:
        scaler = StandardScaler()
        all_features = scaler.fit_transform(all_features)
    else:
        all_features = scaler.transform(all_features)
    
    return all_features, tfidf, scaler

def train_calibrated_filter():
    """Entrena un filtro calibrado de calidad"""
    print("🔧 Entrenando filtro calibrado...")
    
    # Cargar datos
    df = load_training_data()
    if df is None:
        return None, None, None, None, None
    
    print(f"✅ Cargados {len(df)} papers")
    
    # Encontrar el paper implausible para calibración
    implausible_papers = df[df['plausible'] == False]
    if len(implausible_papers) > 0:
        implausible_confidence = implausible_papers['confidence'].iloc[0]
        print(f"🎯 Paper implausible encontrado: confianza = {implausible_confidence}")
    else:
        implausible_confidence = 0.65  # Default
        print(f"⚠️ No hay papers implausibles, usando threshold default: {implausible_confidence}")
    
    # Extraer features
    X, tfidf, scaler = extract_simple_features(df, fit=True)
    y = df['confidence'].values
    
    # Entrenar modelo
    model = GradientBoostingRegressor(
        n_estimators=50,
        max_depth=4,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X, y)
    
    # Evaluar
    predictions = model.predict(X)
    mae = np.mean(np.abs(predictions - y))
    r2 = model.score(X, y)
    
    print(f"✅ Filtro entrenado:")
    print(f"   📊 R² Score: {r2:.3f}")
    print(f"   📊 MAE: {mae:.3f}")
    print(f"   📊 Features: {X.shape[1]}")
    
    return model, tfidf, scaler, df, implausible_confidence

def predict_calibrated_quality(hypothesis, model, tfidf, scaler, implausible_threshold):
    """Predice la calidad con thresholds calibrados"""
    
    # Extraer features
    X, _, _ = extract_simple_features(hypothesis, tfidf, scaler, fit=False)
    
    # Predecir
    confidence = float(model.predict(X)[0])
    
    # Thresholds calibrados basados en el paper implausible
    threshold_reject = implausible_threshold + 0.05  # 0.70 (un poco más que el implausible)
    threshold_approve = 0.85  # Threshold más conservador
    
    # Categorizar con thresholds calibrados
    if confidence >= threshold_approve:
        category = "HIGH"
        recommendation = f"✅ APROBAR - Alta confianza científica (≥{threshold_approve})"
        color = "🟢"
    elif confidence >= threshold_reject:
        category = "MEDIUM"
        recommendation = f"⚠️ REVISAR - Confianza moderada ({threshold_reject:.2f}-{threshold_approve})"
        color = "🟡"
    else:
        category = "LOW"
        recommendation = f"❌ RECHAZAR - Baja confianza científica (<{threshold_reject:.2f})"
        color = "🔴"
    
    return {
        'confidence': confidence,
        'category': category,
        'recommendation': recommendation,
        'color': color,
        'threshold_reject': threshold_reject,
        'threshold_approve': threshold_approve
    }

def create_diverse_test_hypotheses():
    """Crea hipótesis de prueba más diversas"""
    return [
        {
            'title': 'Machine Learning for Protein Structure Prediction Using Deep Neural Networks',
            'abstract': 'We developed a state-of-the-art deep learning model combining convolutional neural networks and attention mechanisms to predict protein secondary and tertiary structures. Our method achieved 92% accuracy on the CASP14 benchmark, outperforming existing methods by 15%. The model uses multiple sequence alignments and evolutionary information to capture structural patterns.',
            'domain': 'pubmed'
        },
        {
            'title': 'Perpetual Motion Machine Using Magnetism Violates Thermodynamics Laws',
            'abstract': 'This revolutionary design creates unlimited free energy by arranging permanent magnets in a specific geometric pattern that generates continuous rotational motion without any external energy input, completely violating the first and second laws of thermodynamics.',
            'domain': 'arxiv'
        },
        {
            'title': 'Quantum Error Correction for Fault-Tolerant Computing',
            'abstract': 'We present a novel quantum error correction scheme using surface codes with improved error thresholds. Our theoretical analysis and simulation results demonstrate a 40% reduction in logical error rates compared to standard surface codes. The method is compatible with current superconducting qubit architectures.',
            'domain': 'arxiv'
        },
        {
            'title': 'Healing Cancer with Crystal Energy and Chakra Alignment',
            'abstract': 'Our groundbreaking research proves that specific crystal arrangements can cure all types of cancer by realigning the patient\'s chakras and redirecting healing energy flows. We tested this method on 100 patients with 100% success rate using only amethyst and rose quartz.',
            'domain': 'base_v2'
        },
        {
            'title': 'Graph Convolutional Networks for Large-Scale Social Network Analysis',
            'abstract': 'We propose a scalable graph convolutional network architecture for analyzing social networks with millions of nodes. Our method efficiently processes large graphs using mini-batch sampling and demonstrates superior performance on community detection, link prediction, and influence propagation tasks.',
            'domain': 'openalex'
        },
        {
            'title': 'Time Travel Communication Using Quantum Entanglement',
            'abstract': 'We demonstrate backwards time communication by exploiting quantum entanglement between particles in different temporal states. Our experiment successfully transmitted information 5 minutes into the past, opening possibilities for paradox-free time travel.',
            'domain': 'arxiv'
        },
        {
            'title': 'BERT-Based Sentiment Analysis for Financial Market Prediction',
            'abstract': 'We fine-tuned BERT on financial news and social media data to predict stock market movements. Our model analyzes sentiment patterns and achieves 68% accuracy in predicting next-day price direction, with careful validation to avoid data leakage and overfitting.',
            'domain': 'openalex'
        }
    ]

def main():
    """Demo del filtro calibrado"""
    print("🎯 CALIBRATED HYPOTHESIS QUALITY FILTER")
    print("=" * 50)
    
    # Entrenar modelo calibrado
    model, tfidf, scaler, training_df, implausible_threshold = train_calibrated_filter()
    
    if model is None:
        print("❌ Error entrenando modelo")
        return
    
    print(f"🎯 Usando threshold de rechazo calibrado: {implausible_threshold + 0.05:.2f}")
    
    # Crear hipótesis de prueba más diversas
    print("\n🧪 Creando hipótesis de prueba diversas...")
    test_hypotheses = create_diverse_test_hypotheses()
    
    # Filtrar cada hipótesis
    print("\n🔍 Filtrando hipótesis con thresholds calibrados...")
    print("=" * 70)
    
    results = []
    for i, hyp in enumerate(test_hypotheses):
        result = predict_calibrated_quality(hyp, model, tfidf, scaler, implausible_threshold)
        result['title'] = hyp['title']
        result['index'] = i
        results.append(result)
        
        print(f"\n{result['color']} **{result['category']}** (Confianza: {result['confidence']:.3f})")
        print(f"   📝 {hyp['title']}")
        print(f"   💡 {result['recommendation']}")
    
    # Estadísticas finales
    approved = sum(1 for r in results if r['category'] == 'HIGH')
    review = sum(1 for r in results if r['category'] == 'MEDIUM') 
    rejected = sum(1 for r in results if r['category'] == 'LOW')
    
    print(f"\n📊 RESUMEN FINAL:")
    print(f"   🟢 Aprobadas: {approved}")
    print(f"   🟡 Para revisar: {review}")
    print(f"   🔴 Rechazadas: {rejected}")
    print(f"   📈 Total: {len(results)}")
    
    # Análisis de efectividad
    print(f"\n🎯 VALIDACIÓN DEL FILTRO:")
    expected_reject = ['Perpetual Motion', 'Crystal Energy', 'Time Travel']
    expected_approve = ['Machine Learning for Protein', 'Quantum Error Correction', 'Graph Convolutional', 'BERT-Based']
    
    print("   ✅ DEBERÍA RECHAZAR (pseudociencia):")
    correct_rejects = 0
    for keyword in expected_reject:
        for r in results:
            if keyword.lower() in r['title'].lower():
                status = "✅ CORRECTO" if r['category'] == 'LOW' else f"❌ ERROR ({r['category']})"
                print(f"      {status}: {r['title'][:50]}... ({r['confidence']:.3f})")
                if r['category'] == 'LOW':
                    correct_rejects += 1
    
    print("   ✅ DEBERÍA APROBAR (ciencia legítima):")
    correct_approvals = 0
    for keyword in expected_approve:
        for r in results:
            if keyword.lower() in r['title'].lower():
                status = "✅ CORRECTO" if r['category'] in ['HIGH', 'MEDIUM'] else f"❌ ERROR ({r['category']})"
                print(f"      {status}: {r['title'][:50]}... ({r['confidence']:.3f})")
                if r['category'] in ['HIGH', 'MEDIUM']:
                    correct_approvals += 1
    
    total_expected_rejects = len([r for r in results for k in expected_reject if k.lower() in r['title'].lower()])
    total_expected_approvals = len([r for r in results for k in expected_approve if k.lower() in r['title'].lower()])
    
    reject_accuracy = correct_rejects / total_expected_rejects if total_expected_rejects > 0 else 0
    approve_accuracy = correct_approvals / total_expected_approvals if total_expected_approvals > 0 else 0
    
    print(f"\n📈 MÉTRICAS DE EFECTIVIDAD:")
    print(f"   🔴 Precisión rechazo pseudociencia: {reject_accuracy:.1%}")
    print(f"   🟢 Precisión aprobación ciencia: {approve_accuracy:.1%}")
    print(f"   🎯 Efectividad general: {(correct_rejects + correct_approvals)/(total_expected_rejects + total_expected_approvals):.1%}")
    
    print(f"\n🎉 FILTRO CALIBRADO LISTO PARA PRODUCCIÓN!")

if __name__ == "__main__":
    main()
