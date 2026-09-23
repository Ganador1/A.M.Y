#!/usr/bin/env python3
"""
🎯 CONFIDENCE REGRESSION TRAINING
Como tenemos solo 1 paper implausible, entrenaremos modelos de REGRESIÓN 
para predecir el CONFIDENCE SCORE directamente (0.5-0.98)
"""

import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
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
                if item.get('confidence') is not None:
                    data.append(item)
            except json.JSONDecodeError:
                continue
    
    df = pd.DataFrame(data)
    print(f"✅ Cargados {len(df)} papers con classificación exitosa")
    
    # Estadísticas básicas
    print(f"📈 Confianza: min={df['confidence'].min():.3f}, max={df['confidence'].max():.3f}, mean={df['confidence'].mean():.3f}")
    print(f"📈 Domains: {df['domain'].value_counts().to_dict()}")
    
    return df

def extract_regression_features(df):
    """Extraer features para regresión de confidence score"""
    print("🔧 Extrayendo features para regresión...")
    
    # Text features (TF-IDF)
    df['combined_text'] = df['title'].fillna('') + ' ' + df['abstract'].fillna('')
    
    # TF-IDF para texto
    tfidf = TfidfVectorizer(
        max_features=500,  # Menos features para regresión
        stop_words='english',
        ngram_range=(1, 2),
        min_df=2
    )
    
    text_features = tfidf.fit_transform(df['combined_text']).toarray()
    text_feature_names = [f'tfidf_{i}' for i in range(text_features.shape[1])]
    
    # Numerical features
    numerical_features = []
    numerical_names = []
    
    # Scores LLM como features (si están disponibles)
    for score_name in ['validity_score', 'feasibility_score', 'novelty_score']:
        if score_name in df.columns:
            scores = df[score_name].fillna(df[score_name].mean()).values
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
    
    # Red flags y strengths counts
    df['red_flags_count'] = df['red_flags'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df['strengths_count'] = df['strengths'].apply(lambda x: len(x) if isinstance(x, list) else 0)
    
    numerical_features.extend([df['red_flags_count'].values, df['strengths_count'].values])
    numerical_names.extend(['red_flags_count', 'strengths_count'])
    
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

def train_confidence_regression_models(X, y):
    """Entrenar modelos de regresión para predecir confidence score"""
    print("🤖 Entrenando modelos de regresión de confidence...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"📊 Train set: {X_train.shape[0]} samples")
    print(f"📊 Test set: {X_test.shape[0]} samples")
    print(f"📊 Target range: {y.min():.3f} - {y.max():.3f}")
    
    # Modelos a entrenar
    models = {
        'Random Forest': RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        ),
        'Gradient Boosting': GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ),
        'Ridge Regression': Ridge(
            alpha=1.0
        ),
        'Lasso Regression': Lasso(
            alpha=0.1,
            max_iter=1000
        ),
        'SVR': SVR(
            C=1.0,
            epsilon=0.01
        )
    }
    
    results = {}
    
    for name, model in models.items():
        print(f"\n🔥 Entrenando {name}...")
        
        # Entrenar modelo
        model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        
        # Metrics
        train_mse = mean_squared_error(y_train, y_pred_train)
        test_mse = mean_squared_error(y_test, y_pred_test)
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        # Cross validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                   cv=KFold(n_splits=5, shuffle=True, random_state=42),
                                   scoring='r2')
        
        results[name] = {
            'model': model,
            'y_pred_train': y_pred_train,
            'y_pred_test': y_pred_test,
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'test_mae': test_mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }
        
        print(f"✅ {name}:")
        print(f"   📊 Test R²: {test_r2:.3f}")
        print(f"   📊 Test MAE: {test_mae:.3f}")
        print(f"   📊 CV R²: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
    
    return results, X_test, y_test, scaler

def analyze_confidence_predictions(results, df):
    """Analizar las predicciones de confidence"""
    print("\n📊 ANÁLISIS DE PREDICCIONES DE CONFIDENCE")
    
    # Mejor modelo por R²
    best_model_name = max(results.keys(), key=lambda x: results[x]['test_r2'])
    best_result = results[best_model_name]
    
    print(f"\n🏆 Mejor modelo: {best_model_name}")
    print(f"   📈 Test R²: {best_result['test_r2']:.3f}")
    print(f"   📈 Test MAE: {best_result['test_mae']:.3f}")
    
    # Distribución de confidence por dominio
    confidence_by_domain = df.groupby('domain')['confidence'].agg(['mean', 'std', 'count', 'min', 'max']).round(3)
    print("\n🏷️ Confianza por dominio:")
    print(confidence_by_domain)
    
    # Casos con confidence extrema
    high_conf = df[df['confidence'] >= 0.95]
    medium_conf = df[(df['confidence'] >= 0.7) & (df['confidence'] < 0.95)]  
    low_conf = df[df['confidence'] < 0.7]
    
    print("\n📈 Distribución de confidence:")
    print(f"   🟢 Alta (≥0.95): {len(high_conf)} papers ({len(high_conf)/len(df)*100:.1f}%)")
    print(f"   🟡 Media (0.7-0.95): {len(medium_conf)} papers ({len(medium_conf)/len(df)*100:.1f}%)")
    print(f"   🔴 Baja (<0.7): {len(low_conf)} papers ({len(low_conf)/len(df)*100:.1f}%)")
    
    if len(low_conf) > 0:
        print("\n⚠️ Papers con baja confianza:")
        for _, paper in low_conf.head(5).iterrows():
            print(f"   - {paper['title'][:50]}... (conf: {paper['confidence']:.3f})")
    
    return confidence_by_domain

def generate_regression_report(results, df, feature_names):
    """Generar reporte completo del entrenamiento de regresión"""
    print("\n📝 Generando reporte de regresión...")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"confidence_regression_report_{timestamp}.json"
    
    # Best model
    best_model_name = max(results.keys(), key=lambda x: results[x]['test_r2'])
    best_model = results[best_model_name]
    
    report = {
        "timestamp": timestamp,
        "task_type": "confidence_regression",
        "dataset_summary": {
            "total_papers": len(df),
            "confidence_range": [df['confidence'].min(), df['confidence'].max()],
            "confidence_mean": df['confidence'].mean(),
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
            "test_r2": best_model['test_r2'],
            "test_mae": best_model['test_mae'],
            "cv_score": f"{best_model['cv_mean']:.3f} ± {best_model['cv_std']:.3f}"
        },
        "confidence_analysis": analyze_confidence_predictions(results, df).to_dict()
    }
    
    # Add all model results
    for name, result in results.items():
        report["model_performance"][name] = {
            "test_r2": result['test_r2'],
            "test_mae": result['test_mae'],
            "cv_mean": result['cv_mean'],
            "cv_std": result['cv_std']
        }
    
    # Save report
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📋 Reporte guardado en: {report_file}")
    
    # Print summary
    print(f"\n🏆 MEJOR MODELO: {best_model_name}")
    print(f"   📊 Test R²: {best_model['test_r2']:.3f}")
    print(f"   📊 Test MAE: {best_model['test_mae']:.3f}")
    print(f"   🔄 CV Score: {best_model['cv_mean']:.3f} ± {best_model['cv_std']:.3f}")
    
    return report_file, best_model_name

def main():
    """Main regression training pipeline"""
    print("🎯 INICIANDO CONFIDENCE REGRESSION TRAINING")
    print("=" * 50)
    
    # 1. Load data
    df = load_llm_classifications()
    
    if len(df) == 0:
        print("❌ No hay datos para entrenar")
        return
    
    # 2. Extract features
    X, feature_names, tfidf = extract_regression_features(df)
    
    # 3. Target: confidence score
    y = df['confidence'].values
    
    print(f"🎯 Target (confidence): min={df['confidence'].min():.3f}, max={df['confidence'].max():.3f}, mean={df['confidence'].mean():.3f}")
    
    # 4. Train regression models
    results, X_test, y_test, scaler = train_confidence_regression_models(X, y)
    
    # 5. Generate report
    report_file, best_model_name = generate_regression_report(results, df, feature_names)
    
    print(f"\n🎉 ENTRENAMIENTO DE REGRESIÓN COMPLETADO!")
    print(f"📄 Reporte: {report_file}")
    print(f"🏆 Mejor modelo: {best_model_name}")
    
    return results, df, feature_names

if __name__ == "__main__":
    results, df, feature_names = main()
