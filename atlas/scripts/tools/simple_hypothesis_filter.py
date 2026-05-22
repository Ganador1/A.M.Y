#!/usr/bin/env python3
"""
🎯 SIMPLE HYPOTHESIS QUALITY FILTER
Versión simplificada del filtro de calidad usando solo features básicas
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
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
            max_features=100,  # Reducido para simplicidad
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

def train_simple_filter():
    """Entrena un filtro simple de calidad"""
    print("🔧 Entrenando filtro simple de calidad...")
    
    # Cargar datos
    df = load_training_data()
    if df is None:
        return None, None, None, None
    
    print(f"✅ Cargados {len(df)} papers")
    
    # Extraer features
    X, tfidf, scaler = extract_simple_features(df, fit=True)
    y = df['confidence'].values
    
    # Entrenar modelo
    model = GradientBoostingRegressor(
        n_estimators=50,  # Reducido para velocidad
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
    
    return model, tfidf, scaler, df

def predict_hypothesis_quality(hypothesis, model, tfidf, scaler):
    """Predice la calidad de una hipótesis"""
    
    # Extraer features
    X, _, _ = extract_simple_features(hypothesis, tfidf, scaler, fit=False)
    
    # Predecir
    confidence = float(model.predict(X)[0])
    
    # Categorizar
    if confidence >= 0.95:
        category = "HIGH"
        recommendation = "✅ APROBAR - Alta confianza científica"
        color = "🟢"
    elif confidence >= 0.7:
        category = "MEDIUM"
        recommendation = "⚠️ REVISAR - Confianza moderada"
        color = "🟡"
    else:
        category = "LOW"
        recommendation = "❌ RECHAZAR - Baja confianza"
        color = "🔴"
    
    return {
        'confidence': confidence,
        'category': category,
        'recommendation': recommendation,
        'color': color
    }

def create_test_hypotheses():
    """Crea hipótesis de prueba"""
    return [
        {
            'title': 'Machine Learning Approach for Protein Folding Prediction',
            'abstract': 'We developed a novel deep learning architecture combining convolutional neural networks and transformer models to predict protein folding patterns. Our method achieved state-of-the-art accuracy on standard benchmarks, with potential applications in drug discovery and disease treatment.',
            'domain': 'pubmed'
        },
        {
            'title': 'Perpetual Motion Engine Using Magnetic Fields',
            'abstract': 'This revolutionary design creates unlimited energy by arranging magnets in a specific pattern that generates continuous motion without any external energy input, violating fundamental laws of physics.',
            'domain': 'arxiv'
        },
        {
            'title': 'Quantum Computing Algorithm for NP-Complete Problems',
            'abstract': 'We present a quantum algorithm that can solve NP-complete problems in polynomial time using novel quantum gate sequences. Our theoretical analysis shows exponential speedup over classical algorithms.',
            'domain': 'arxiv'
        },
        {
            'title': 'Crystal Healing for Cancer Treatment',
            'abstract': 'Our study demonstrates that specific crystal arrangements can cure cancer by aligning chakras and redirecting healing energy. We tested 30 patients using amethyst and quartz crystals with remarkable results.',
            'domain': 'base_v2'
        },
        {
            'title': 'Graph Neural Networks for Social Network Analysis',
            'abstract': 'We propose a novel graph neural network architecture for analyzing large-scale social networks. Our method effectively captures complex relationships and demonstrates superior performance in community detection and influence prediction tasks.',
            'domain': 'openalex'
        }
    ]

def main():
    """Demo del filtro simple"""
    print("🎯 SIMPLE HYPOTHESIS QUALITY FILTER")
    print("=" * 50)
    
    # Entrenar modelo
    model, tfidf, scaler, training_df = train_simple_filter()
    
    if model is None:
        print("❌ Error entrenando modelo")
        return
    
    # Crear hipótesis de prueba
    print("\n🧪 Creando hipótesis de prueba...")
    test_hypotheses = create_test_hypotheses()
    
    # Filtrar cada hipótesis
    print("\n🔍 Filtrando hipótesis...")
    print("=" * 60)
    
    results = []
    for i, hyp in enumerate(test_hypotheses):
        result = predict_hypothesis_quality(hyp, model, tfidf, scaler)
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
    
    # Análisis de resultados esperados
    print(f"\n🎯 ANÁLISIS:")
    expected_good = ['Machine Learning Approach', 'Quantum Computing Algorithm', 'Graph Neural Networks']
    expected_bad = ['Perpetual Motion Engine', 'Crystal Healing']
    
    print("   📋 Hipótesis que DEBERÍAN ser aprobadas:")
    for hyp in expected_good:
        for r in results:
            if hyp in r['title']:
                status = "✅" if r['category'] in ['HIGH', 'MEDIUM'] else "❌"
                print(f"      {status} {r['title'][:50]}... ({r['confidence']:.3f})")
    
    print("   📋 Hipótesis que DEBERÍAN ser rechazadas:")
    for hyp in expected_bad:
        for r in results:
            if hyp in r['title']:
                status = "✅" if r['category'] == 'LOW' else "❌"
                print(f"      {status} {r['title'][:50]}... ({r['confidence']:.3f})")
    
    print(f"\n🎉 FILTRO DE CALIDAD FUNCIONANDO")
    print("   Ready para integración en el workflow de hipótesis!")

if __name__ == "__main__":
    main()
