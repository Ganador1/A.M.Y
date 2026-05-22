#!/usr/bin/env python3
"""
🎯 HYPOTHESIS QUALITY FILTER
Integra el modelo Gradient Boosting entrenado como filtro de calidad
para hipótesis generadas automáticamente
"""

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class HypothesisQualityFilter:
    """
    Filtro de calidad para hipótesis científicas usando el modelo entrenado
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.tfidf = None
        self.feature_names = None
        self.is_trained = False
        self.confidence_threshold_low = 0.7
        self.confidence_threshold_high = 0.95
    
    def train_from_existing_data(self):
        """Entrena el modelo usando los datos ya clasificados"""
        print("🔧 Entrenando modelo de calidad desde datos existentes...")
        
        # Cargar datos clasificados
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
            return False
        
        if len(data) == 0:
            print("❌ No hay datos válidos para entrenar")
            return False
        
        df = pd.DataFrame(data)
        print(f"✅ Cargados {len(df)} papers para entrenamiento")
        
        # Extraer features
        X, feature_names = self._extract_features(df, fit_transform=True)
        y = df['confidence'].values
        
        # Entrenar modelo Gradient Boosting
        from sklearn.ensemble import GradientBoostingRegressor
        
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        )
        
        # Entrenar modelo
        self.model.fit(X, y)
        self.feature_names = feature_names
        self.is_trained = True
        
        # Evaluar en datos de entrenamiento
        predictions = self.model.predict(X)
        mae = np.mean(np.abs(predictions - y))
        r2 = self.model.score(X, y)
        
        print(f"✅ Modelo entrenado:")
        print(f"   📊 R² Score: {r2:.3f}")
        print(f"   📊 MAE: {mae:.3f}")
        print(f"   📊 Features: {len(feature_names)}")
        
        return True
    
    def _extract_features(self, data_input, fit_transform=False):
        """Extrae features de los datos"""
        
        # Si es un DataFrame
        if isinstance(data_input, pd.DataFrame):
            df = data_input.copy()
        # Si es una lista de diccionarios
        elif isinstance(data_input, list):
            df = pd.DataFrame(data_input)
        # Si es un solo diccionario
        elif isinstance(data_input, dict):
            df = pd.DataFrame([data_input])
        else:
            raise ValueError("Input debe ser DataFrame, lista de dicts, o dict")
        
        # Preparar texto combinado
        df['combined_text'] = df['title'].fillna('') + ' ' + df['abstract'].fillna('')
        
        # TF-IDF features
        if fit_transform or self.tfidf is None:
            self.tfidf = TfidfVectorizer(
                max_features=500,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=1  # Menos restrictivo para casos individuales
            )
            text_features = self.tfidf.fit_transform(df['combined_text']).toarray()
        else:
            text_features = self.tfidf.transform(df['combined_text']).toarray()
        
        text_feature_names = [f'tfidf_{i}' for i in range(text_features.shape[1])]
        
        # Features numéricas
        numerical_features = []
        numerical_names = []
        
        # Scores LLM (si están disponibles)
        for score_name in ['validity_score', 'feasibility_score', 'novelty_score']:
            if score_name in df.columns:
                scores = df[score_name].fillna(0.5).values  # Default neutro
                numerical_features.append(scores)
                numerical_names.append(score_name)
            else:
                # Si no están disponibles, usar valores por defecto
                numerical_features.append(np.full(len(df), 0.75))
                numerical_names.append(score_name)
        
        # Length features
        df['title_len'] = df['title'].fillna('').str.len()
        df['abstract_len'] = df['abstract'].fillna('').str.len()
        df['combined_len'] = df['combined_text'].str.len()
        
        for len_feature in ['title_len', 'abstract_len', 'combined_len']:
            numerical_features.append(df[len_feature].values)
            numerical_names.append(len_feature)
        
        # Domain features (one-hot)
        # Usar domains conocidos del entrenamiento
        known_domains = ['openalex', 'base_v2', 'arxiv', 'pubmed']
        domain_features = []
        domain_names = []
        
        for domain in known_domains:
            domain_col = (df['domain'] == domain).astype(int).values
            domain_features.append(domain_col)
            domain_names.append(f'domain_{domain}')
        
        # Red flags y strengths counts
        df['red_flags_count'] = df.get('red_flags', []).apply(lambda x: len(x) if isinstance(x, list) else 0)
        df['strengths_count'] = df.get('strengths', []).apply(lambda x: len(x) if isinstance(x, list) else 0)
        
        numerical_features.extend([df['red_flags_count'].values, df['strengths_count'].values])
        numerical_names.extend(['red_flags_count', 'strengths_count'])
        
        # Year feature
        if 'year' in df.columns:
            years = pd.to_numeric(df['year'], errors='coerce').fillna(2025).values
        else:
            years = np.full(len(df), 2025)
        numerical_features.append(years)
        numerical_names.append('year')
        
        # Combinar todas las features
        if numerical_features:
            numerical_array = np.column_stack(numerical_features)
            domain_array = np.column_stack(domain_features) if domain_features else np.empty((len(df), 0))
            all_features = np.hstack([text_features, numerical_array, domain_array])
            feature_names = text_feature_names + numerical_names + domain_names
        else:
            all_features = text_features
            feature_names = text_feature_names
        
        # Scaler
        if fit_transform or self.scaler is None:
            self.scaler = StandardScaler()
            all_features = self.scaler.fit_transform(all_features)
        else:
            all_features = self.scaler.transform(all_features)
        
        return all_features, feature_names
    
    def predict_confidence(self, hypothesis):
        """
        Predice la confianza de una hipótesis
        
        Args:
            hypothesis: dict con keys 'title', 'abstract', 'domain' (opcional)
        
        Returns:
            dict con confidence score y categoría
        """
        if not self.is_trained:
            raise ValueError("Modelo no entrenado. Ejecuta train_from_existing_data() primero")
        
        # Preparar datos
        X, _ = self._extract_features(hypothesis)
        
        # Predecir
        confidence = float(self.model.predict(X)[0])
        
        # Categorizar
        if confidence >= self.confidence_threshold_high:
            category = "HIGH"
            recommendation = "✅ APROBAR - Alta confianza científica"
            color = "🟢"
        elif confidence >= self.confidence_threshold_low:
            category = "MEDIUM"
            recommendation = "⚠️ REVISAR - Confianza moderada, revisar manualmente"
            color = "🟡"
        else:
            category = "LOW"
            recommendation = "❌ RECHAZAR - Baja confianza, requiere mejoras significativas"
            color = "🔴"
        
        return {
            'confidence': confidence,
            'category': category,
            'recommendation': recommendation,
            'color': color,
            'threshold_high': self.confidence_threshold_high,
            'threshold_low': self.confidence_threshold_low
        }
    
    def batch_filter(self, hypotheses):
        """Filtra un batch de hipótesis"""
        results = []
        
        for i, hyp in enumerate(hypotheses):
            try:
                result = self.predict_confidence(hyp)
                result['index'] = i
                result['title'] = hyp.get('title', 'Sin título')
                results.append(result)
            except Exception as e:
                results.append({
                    'index': i,
                    'title': hyp.get('title', 'Sin título'),
                    'confidence': 0.0,
                    'category': 'ERROR',
                    'recommendation': f"Error en procesamiento: {str(e)}",
                    'color': '⚫'
                })
        
        return results
    
    def save_model(self, filepath):
        """Guarda el modelo entrenado"""
        if not self.is_trained:
            raise ValueError("No hay modelo entrenado para guardar")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'tfidf': self.tfidf,
            'feature_names': self.feature_names,
            'thresholds': {
                'low': self.confidence_threshold_low,
                'high': self.confidence_threshold_high
            },
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        print(f"💾 Modelo guardado en: {filepath}")
    
    def load_model(self, filepath):
        """Carga un modelo pre-entrenado"""
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.tfidf = model_data['tfidf']
            self.feature_names = model_data['feature_names']
            
            if 'thresholds' in model_data:
                self.confidence_threshold_low = model_data['thresholds']['low']
                self.confidence_threshold_high = model_data['thresholds']['high']
            
            self.is_trained = True
            print(f"✅ Modelo cargado desde: {filepath}")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo: {e}")
            return False

# Función de utilidad para generar hipótesis de prueba
def generate_test_hypotheses():
    """Genera hipótesis de prueba para evaluar el filtro"""
    hypotheses = [
        {
            'title': 'Novel Quantum Entanglement Applications in Renewable Energy Storage',
            'abstract': 'This study investigates the potential use of quantum entanglement phenomena to enhance the efficiency of renewable energy storage systems. We propose a theoretical framework combining quantum mechanics with energy storage technologies, focusing on scalable implementation strategies for solar and wind energy systems.',
            'domain': 'arxiv'
        },
        {
            'title': 'Perpetual Motion Machine Design Using Magnetic Levitation',
            'abstract': 'We present a revolutionary design for a perpetual motion machine that violates the laws of thermodynamics by creating infinite energy through magnetic levitation. Our prototype demonstrates continuous motion without any external energy input, solving the global energy crisis.',
            'domain': 'arxiv'
        },
        {
            'title': 'Deep Learning Approach for Early Detection of Alzheimer\'s Disease',
            'abstract': 'We developed a convolutional neural network model that analyzes brain MRI scans to detect early-stage Alzheimer\'s disease. Our model achieved 94% accuracy on a dataset of 2,000 patients, significantly outperforming current diagnostic methods. The approach could enable earlier intervention and better patient outcomes.',
            'domain': 'pubmed'
        },
        {
            'title': 'Telepathic Communication Enhancement Through Crystal Healing',
            'abstract': 'This research explores how specific crystal configurations can amplify human telepathic abilities. We conducted experiments with 50 participants using various crystal arrangements and measured telepathic transmission success rates using psychic energy meters.',
            'domain': 'base_v2'
        },
        {
            'title': 'Machine Learning for Predicting Stock Market Returns',
            'abstract': 'We present a comprehensive study using ensemble methods including Random Forest, Gradient Boosting, and neural networks to predict daily stock returns. Our model incorporates technical indicators, market sentiment analysis, and macroeconomic factors. Backtesting shows consistent 15% annual returns with controlled risk.',
            'domain': 'openalex'
        }
    ]
    
    return hypotheses

def main():
    """Demo del filtro de calidad de hipótesis"""
    print("🎯 HYPOTHESIS QUALITY FILTER - DEMO")
    print("=" * 50)
    
    # Crear y entrenar filtro
    filter_model = HypothesisQualityFilter()
    
    if not filter_model.train_from_existing_data():
        print("❌ No se pudo entrenar el modelo")
        return
    
    # Guardar modelo entrenado
    model_path = "hypothesis_quality_filter.pkl"
    filter_model.save_model(model_path)
    
    # Generar hipótesis de prueba
    print(f"\n🧪 Generando hipótesis de prueba...")
    test_hypotheses = generate_test_hypotheses()
    
    # Filtrar hipótesis
    print(f"\n🔍 Filtrando {len(test_hypotheses)} hipótesis...")
    results = filter_model.batch_filter(test_hypotheses)
    
    # Mostrar resultados
    print(f"\n📊 RESULTADOS DE FILTRADO:")
    print("=" * 60)
    
    approved = 0
    review_needed = 0 
    rejected = 0
    
    for result in results:
        print(f"\n{result['color']} **{result['category']}** (Confianza: {result['confidence']:.3f})")
        print(f"   📝 Título: {result['title'][:70]}{'...' if len(result['title']) > 70 else ''}")
        print(f"   💡 Recomendación: {result['recommendation']}")
        
        if result['category'] == 'HIGH':
            approved += 1
        elif result['category'] == 'MEDIUM':
            review_needed += 1
        else:
            rejected += 1
    
    # Resumen
    print(f"\n📈 RESUMEN:")
    print(f"   🟢 Aprobadas automáticamente: {approved}")
    print(f"   🟡 Requieren revisión: {review_needed}")
    print(f"   🔴 Rechazadas: {rejected}")
    print(f"   📊 Total procesadas: {len(results)}")
    
    print(f"\n✅ Modelo guardado en: {model_path}")
    print("🎯 Filtro listo para integración en el workflow de hipótesis")

if __name__ == "__main__":
    main()
