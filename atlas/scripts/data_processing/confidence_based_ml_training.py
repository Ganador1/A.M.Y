#!/usr/bin/env python3
"""
🚀 CONFIDENCE-BASED ML TRAINING
Entrena modelos ML usando los confidence scores generados por LLM
"""

import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_llm_classifications():
    """Cargar las clasificaciones LLM con confidence scores"""
    print("📊 Cargando clasificaciones LLM...")
    
    data = []
    with open('data/final_llm_classifications.jsonl', 'r', encoding='utf-8') as f:
        for line in f:
            try:
                item = json.loads(line.strip())
                # Solo incluir papers con clasificación exitosa
                if item.get('confidence') is not None and item.get('plausible') is not None:
                    data.append(item)
            except json.JSONDecodeError:
                continue
    
    df = pd.DataFrame(data)
    print(f"✅ Cargados {len(df)} papers con clasificación exitosa")
    
    # Estadísticas básicas
    print(f"📈 Distribución plausible: {df['plausible'].value_counts().to_dict()}")
    print(f"📈 Confianza promedio: {df['confidence'].mean():.3f}")
    print(f"📈 Domains: {df['domain'].value_counts().to_dict()}")
    
    return df

def extract_features(df):
    """Extraer features para entrenamiento ML"""
    print("🔧 Extrayendo features...")
    
    # Text features (TF-IDF)
    # Combinar título y abstract para features de texto
    df['combined_text'] = df['title'].fillna('') + ' ' + df['abstract'].fillna('')
    
    # TF-IDF para texto
    tfidf = TfidfVectorizer(
        max_features=1000,
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    
    text_features = tfidf.fit_transform(df['combined_text']).toarray()
    text_feature_names = [f'tfidf_{i}' for i in range(text_features.shape[1])]
    
    # Numerical features
    numerical_features = []
    numerical_names = []
    
    # Scores LLM como features
    for score_name in ['validity_score', 'feasibility_score', 'novelty_score']:
        if score_name in df.columns:
            scores = df[score_name].fillna(0).values
            numerical_features.append(scores)
            numerical_names.append(score_name)
    
    # Length features
    df['title_len'] = df['title'].fillna('').str.len()
    df['abstract_len'] = df['abstract'].fillna('').str.len()
    df['combined_len'] = df['combined_text'].str.len()
    
    for len_feature in ['title_len', 'abstract_len', 'combined_len']:
        numerical_features.append(df[len_feature].values)
        numerical_names.append(len_feature)
    
    # Domain encoding (one-hot)
    domain_dummies = pd.get_dummies(df['domain'], prefix='domain')
    domain_features = domain_dummies.values
    domain_names = list(domain_dummies.columns)
    
    # Year feature (si está disponible)
    if 'year' in df.columns:
        years = pd.to_numeric(df['year'], errors='coerce').fillna(2020).values
        numerical_features.append(years)
        numerical_names.append('year')
    
    # Red flags count
    df['red_flags_count'] = df['red_flags'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    numerical_features.append(df['red_flags_count'].values)
    numerical_names.append('red_flags_count')
    
    # Strengths count
    df['strengths_count'] = df['strengths'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    numerical_features.append(df['strengths_count'].values)
    numerical_names.append('strengths_count')
    
    # Combine all features
    if numerical_features:
        numerical_array = np.column_stack(numerical_features)
        all_features = np.hstack([text_features, numerical_array, domain_features])
        feature_names = text_feature_names + numerical_names + domain_names
    else:
        all_features = np.hstack([text_features, domain_features])
        feature_names = text_feature_names + domain_names
    
    print(f"✅ Features extraídos: {all_features.shape[1]} features para {all_features.shape[0]} papers")
    print(f"📝 Tipos de features: {len(text_feature_names)} TF-IDF, {len(numerical_names)} numéricos, {len(domain_names)} domain")
    
    return all_features, feature_names, tfidf

def train_confidence_weighted_models(X, y, confidence_weights):
    """Entrenar múltiples modelos con confidence weighting"""
    print("🤖 Entrenando modelos con confidence weighting...")
    
    # Check class distribution
    unique_classes, class_counts = np.unique(y, return_counts=True)
    min_class_count = min(class_counts)
    
    print(f"📊 Class distribution: {dict(zip(unique_classes, class_counts))}")
    
    # Split data - no stratify si hay muy pocos ejemplos de alguna clase
    if min_class_count < 2:
        print("⚠️ Clase minoritaria con <2 ejemplos, usando split sin stratify")
        X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
            X, y, confidence_weights, test_size=0.2, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test, weights_train, weights_test = train_test_split(
            X, y, confidence_weights, test_size=0.2, random_state=42, stratify=y
        )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Class weights para handling imbalance
    class_weights = compute_class_weight('balanced', classes=np.unique(y), y=y)
    class_weight_dict = dict(zip(np.unique(y), class_weights))
    
    print(f"📊 Train set: {X_train.shape[0]} samples")
    print(f"📊 Test set: {X_test.shape[0]} samples")
    print(f"📊 Class weights: {class_weight_dict}")
    
    # Modelos a entrenar
    models = {
        'Random Forest': RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            class_weight='balanced',
            random_state=42
        ),
        'Gradient Boosting': GradientBoostingClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ),
        'Logistic Regression': LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=42
        ),
        'SVM': SVC(
            class_weight='balanced',
            probability=True,
            random_state=42
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n🔥 Entrenando {name}...")
        
        # Entrenar con sample weights (confidence) - solo para modelos que lo soporten bien
        if name == 'Random Forest':
            model.fit(X_train_scaled, y_train, sample_weight=weights_train)
        elif name == 'Gradient Boosting':
            # GradientBoosting tiene problemas con clases muy desbalanceadas y weights
            # Usar sin weights pero con class_weight en su lugar
            try:
                model.fit(X_train_scaled, y_train, sample_weight=weights_train)
            except ValueError:
                print(f"   ⚠️ {name}: usando sin sample_weight debido a clases desbalanceadas")
                model.fit(X_train_scaled, y_train)
        else:
            model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)
        
        # Handle case where only one class is present
        if y_pred_proba.shape[1] == 1:
            # Solo hay una clase, usar esa probabilidad
            y_pred_proba_positive = y_pred_proba[:, 0] if np.unique(y_test)[0] == 1 else 1 - y_pred_proba[:, 0]
        else:
            y_pred_proba_positive = y_pred_proba[:, 1]
        
        # Metrics
        try:
            auc = roc_auc_score(y_test, y_pred_proba_positive)
        except Exception:
            auc = 0.5  # Si solo hay una clase en test
        
        # Cross validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                   cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
                                   scoring='accuracy')
        
        results[name] = {
            'model': model,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba_positive,
            'auc': auc,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'accuracy': (y_pred == y_test).mean()
        }
        
        print(f"✅ {name} - Accuracy: {results[name]['accuracy']:.3f}, AUC: {auc:.3f}")
        print(f"   CV: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    
    return results, X_test, y_test, scaler

def analyze_confidence_patterns(df):
    """Analizar patrones en los confidence scores"""
    print("\n📊 ANÁLISIS DE PATRONES DE CONFIANZA")
    
    # Confidence por domain
    confidence_by_domain = df.groupby('domain')['confidence'].agg(['mean', 'std', 'count']).round(3)
    print("\n🏷️ Confianza por dominio:")
    print(confidence_by_domain)
    
    # Confidence por plausibilidad
    confidence_by_plausible = df.groupby('plausible')['confidence'].agg(['mean', 'std', 'count']).round(3)
    print("\n✅ Confianza por plausibilidad:")
    print(confidence_by_plausible)
    
    # Correlation entre scores
    score_cols = ['confidence', 'validity_score', 'feasibility_score', 'novelty_score']
    available_scores = [col for col in score_cols if col in df.columns]
    
    if len(available_scores) > 1:
        correlation_matrix = df[available_scores].corr()
        print(f"\n📈 Correlaciones entre scores:")
        print(correlation_matrix.round(3))
    
    # Casos de baja confianza
    low_confidence = df[df['confidence'] <= 0.6]
    if len(low_confidence) > 0:
        print(f"\n⚠️ Papers con baja confianza (≤0.6): {len(low_confidence)}")
        for _, paper in low_confidence.head(3).iterrows():
            print(f"   - {paper['title'][:50]}... (confianza: {paper['confidence']})")
    
    return confidence_by_domain

def generate_training_report(results, df, feature_names):
    """Generar reporte completo del entrenamiento"""
    print("\n📝 Generando reporte de entrenamiento...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"confidence_ml_training_report_{timestamp}.json"
    
    # Best model
    best_model_name = max(results.keys(), key=lambda x: results[x]['accuracy'])
    best_model = results[best_model_name]
    
    report = {
        "timestamp": timestamp,
        "dataset_summary": {
            "total_papers": len(df),
            "plausible_papers": len(df[df['plausible'] == True]),
            "implausible_papers": len(df[df['plausible'] == False]),
            "avg_confidence": df['confidence'].mean(),
            "confidence_std": df['confidence'].std(),
            "domains": df['domain'].value_counts().to_dict()
        },
        "feature_engineering": {
            "total_features": len(feature_names),
            "text_features": len([f for f in feature_names if f.startswith('tfidf_')]),
            "numerical_features": len([f for f in feature_names if not f.startswith(('tfidf_', 'domain_'))]),
            "domain_features": len([f for f in feature_names if f.startswith('domain_')])
        },
        "model_performance": {},
        "best_model": {
            "name": best_model_name,
            "accuracy": best_model['accuracy'],
            "auc": best_model['auc'],
            "cv_score": f"{best_model['cv_mean']:.3f} ± {best_model['cv_std']:.3f}"
        },
        "confidence_analysis": analyze_confidence_patterns(df).to_dict()
    }
    
    # Add all model results
    for name, result in results.items():
        report["model_performance"][name] = {
            "accuracy": result['accuracy'],
            "auc": result['auc'],
            "cv_mean": result['cv_mean'],
            "cv_std": result['cv_std']
        }
    
    # Save report
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Reporte guardado en: {report_file}")
    
    # Print summary
    print(f"\n🏆 MEJOR MODELO: {best_model_name}")
    print(f"   📊 Accuracy: {best_model['accuracy']:.3f}")
    print(f"   📈 AUC: {best_model['auc']:.3f}")
    print(f"   🔄 CV Score: {best_model['cv_mean']:.3f} ± {best_model['cv_std']:.3f}")
    
    return report_file, best_model_name

def main():
    """Main training pipeline"""
    print("🚀 INICIANDO CONFIDENCE-BASED ML TRAINING")
    print("=" * 50)
    
    # 1. Load data
    df = load_llm_classifications()
    
    if len(df) == 0:
        print("❌ No hay datos para entrenar")
        return
    
    # 2. Extract features
    X, feature_names, tfidf = extract_features(df)
    
    # 3. Prepare targets and weights  
    y = df['plausible'].astype(int).values
    confidence_weights = df['confidence'].values
    
    print(f"🎯 Target distribution: {df['plausible'].value_counts().to_dict()}")
    print(f"⚖️ Confidence weights: min={df['confidence'].min():.3f}, max={df['confidence'].max():.3f}, mean={df['confidence'].mean():.3f}")
    
    # 4. Train models
    results, X_test, y_test, scaler = train_confidence_weighted_models(X, y, confidence_weights)
    
    # 5. Analyze confidence patterns
    analyze_confidence_patterns(df)
    
    # 6. Generate report
    report_file, best_model_name = generate_training_report(results, df, feature_names)
    
    print(f"\n🎉 ENTRENAMIENTO COMPLETADO!")
    print(f"📄 Reporte: {report_file}")
    print(f"🏆 Mejor modelo: {best_model_name}")
    
    return results, df, feature_names

if __name__ == "__main__":
    results, df, feature_names = main()
