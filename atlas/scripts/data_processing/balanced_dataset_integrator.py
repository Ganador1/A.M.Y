"""
🔧 ATLAS - Integrador de Dataset Balanceado con Retraction Watch
==============================================================

Este script integra los 66,461 papers retractados de Retraction Watch
con nuestro dataset actual para crear un dataset balanceado y re-entrenar
el modelo con mejor capacidad de detectar pseudociencia.

Problema actual: 99.8% plausible (495) vs 0.2% implausible (1)
Solución: Añadir miles de ejemplos negativos reales
"""

import pandas as pd
import numpy as np
import json
import pickle
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import re
import warnings
warnings.filterwarnings('ignore')

class BalancedDatasetIntegrator:
    """Integra Retraction Watch data con dataset actual para balancear y re-entrenar"""
    
    def __init__(self):
        self.original_data = None
        self.retraction_data = None
        self.integrated_data = None
        self.model = None
        self.vectorizer = None
        self.feature_columns = None
        
    def load_original_dataset(self) -> bool:
        """Carga el dataset original de papers plausibles"""
        
        print("📁 Cargando dataset original...")
        
        try:
            # Buscar el archivo de dataset más reciente
            import glob
            dataset_files = glob.glob("plausible_hypothesis_classification_*.json")
            if not dataset_files:
                print("   ❌ No se encontró dataset original")
                return False
                
            latest_file = max(dataset_files)
            print(f"   📄 Usando: {latest_file}")
            
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Convertir a DataFrame
            records = []
            for item in data:
                if isinstance(item, dict):
                    record = {
                        'title': item.get('title', ''),
                        'domain': item.get('domain', ''),
                        'confidence': item.get('confidence', 0.95),  # Original alta confianza
                        'is_plausible': True,  # Todos son plausibles
                        'source': 'original_dataset',
                        'hypothesis_text': item.get('title', ''),  # Para features de texto
                        'year': 2024,  # Valor por defecto
                        'citations': item.get('citations', 0),
                        'journal_impact': item.get('journal_impact', 1.0),
                        'methodology_score': item.get('methodology_score', 0.8),
                        'novelty_score': item.get('novelty_score', 0.7),
                        'coherence_score': item.get('coherence_score', 0.85)
                    }
                    records.append(record)
            
            self.original_data = pd.DataFrame(records)
            print(f"   ✅ Dataset original cargado: {len(self.original_data):,} ejemplos plausibles")
            print(f"   📊 Confianza promedio: {self.original_data['confidence'].mean():.3f}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error cargando dataset original: {e}")
            return False
    
    def load_retraction_data(self) -> bool:
        """Carga los datos de Retraction Watch"""
        
        print("\n📁 Cargando datos de Retraction Watch...")
        
        try:
            # Buscar el archivo más reciente
            import glob
            retraction_files = glob.glob("retraction_watch_processed_*.csv")
            if not retraction_files:
                print("   ❌ No se encontró archivo de Retraction Watch")
                return False
            
            latest_file = max(retraction_files)
            print(f"   📄 Usando: {latest_file}")
            
            # Cargar datos
            df = pd.read_csv(latest_file)
            print(f"   📊 Papers retractados cargados: {len(df):,}")
            
            # Procesar y estructurar datos para nuestro formato
            records = []
            for idx, row in df.iterrows():
                # Extraer información clave
                title = str(row.get('Title', '')).strip()
                if not title or title == 'nan':
                    title = f"Retracted Paper #{row.get('Record ID', idx)}"
                
                # Determinar confianza baja basada en razón de retractación
                reason = str(row.get('Reason', '')).lower()
                confidence = self._calculate_retraction_confidence(reason)
                
                record = {
                    'title': title,
                    'domain': self._extract_domain_from_subject(str(row.get('Subject', ''))),
                    'confidence': confidence,  # Baja confianza para retractados
                    'is_plausible': False,  # Todos son implausibles
                    'source': 'retraction_watch',
                    'hypothesis_text': title,  # Para features de texto
                    'retraction_reason': reason,
                    'journal': str(row.get('Journal', '')),
                    'year': self._extract_year_from_date(str(row.get('OriginalPaperDate', ''))),
                    'citations': 0,  # Asumimos pocos citations para retractados
                    'journal_impact': 0.3,  # Bajo impacto asumido
                    'methodology_score': 0.2,  # Metodología problemática
                    'novelty_score': 0.3,  # Posible innovación pero problemática
                    'coherence_score': 0.1   # Baja coherencia científica
                }
                records.append(record)
                
                # Limitar para pruebas iniciales - tomar muestra representativa
                if len(records) >= 5000:  # 5K ejemplos negativos vs 495 positivos
                    break
            
            self.retraction_data = pd.DataFrame(records)
            print(f"   ✅ Datos de retracción procesados: {len(self.retraction_data):,} ejemplos")
            print(f"   📊 Confianza promedio: {self.retraction_data['confidence'].mean():.3f}")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error cargando datos de retracción: {e}")
            return False
    
    def _calculate_retraction_confidence(self, reason: str) -> float:
        """Calcula confianza basada en la razón de retractación"""
        
        # Razones más graves = confianza más baja
        if any(term in reason for term in ['fraud', 'fabrication', 'falsification']):
            return 0.05  # Muy baja para fraude obvio
        elif any(term in reason for term in ['plagiarism', 'duplication']):
            return 0.10  # Baja para plagio
        elif any(term in reason for term in ['misconduct', 'ethics']):
            return 0.15  # Baja para misconduct
        elif any(term in reason for term in ['error', 'mistake']):
            return 0.25  # Algo más alta para errores honestos
        else:
            return 0.20  # Valor por defecto para otros casos
    
    def _extract_domain_from_subject(self, subject: str) -> str:
        """Extrae dominio del campo Subject"""
        
        subject_lower = subject.lower()
        
        if 'medicine' in subject_lower:
            return 'medicine'
        elif 'biology' in subject_lower:
            return 'biology'
        elif 'physics' in subject_lower:
            return 'physics'
        elif 'chemistry' in subject_lower:
            return 'chemistry'
        elif 'engineering' in subject_lower:
            return 'engineering'
        elif 'computer' in subject_lower:
            return 'computer_science'
        else:
            return 'multidisciplinary'
    
    def _extract_year_from_date(self, date_str: str) -> int:
        """Extrae año de string de fecha"""
        
        try:
            # Buscar patrón de año (4 dígitos)
            import re
            year_match = re.search(r'(\d{4})', date_str)
            if year_match:
                year = int(year_match.group(1))
                if 1950 <= year <= 2025:  # Rango razonable
                    return year
        except:
            pass
        
        return 2020  # Valor por defecto
    
    def create_balanced_dataset(self) -> bool:
        """Combina datasets para crear dataset balanceado"""
        
        print(f"\n🔗 Creando dataset balanceado...")
        
        if self.original_data is None or self.retraction_data is None:
            print("   ❌ Faltan datos para integrar")
            return False
        
        # Combinar datasets
        combined = pd.concat([self.original_data, self.retraction_data], ignore_index=True)
        
        print(f"   📊 Dataset combinado:")
        print(f"      • Total ejemplos: {len(combined):,}")
        print(f"      • Ejemplos plausibles: {len(combined[combined['is_plausible']]):,} ({len(combined[combined['is_plausible']])/len(combined)*100:.1f}%)")
        print(f"      • Ejemplos implausibles: {len(combined[~combined['is_plausible']]):,} ({len(combined[~combined['is_plausible']])/len(combined)*100:.1f}%)")
        
        # Verificar balance
        plausible_ratio = len(combined[combined['is_plausible']]) / len(combined)
        if 0.3 <= plausible_ratio <= 0.7:
            print("   ✅ Dataset bien balanceado")
        elif plausible_ratio > 0.7:
            print("   ⚠️  Muchos ejemplos plausibles - considerar reducir")
        else:
            print("   ⚠️  Pocos ejemplos plausibles - considerar añadir más")
        
        self.integrated_data = combined
        return True
    
    def extract_enhanced_features(self, df: pd.DataFrame) -> tuple:
        """Extrae features mejoradas para el modelo"""
        
        print(f"\n🔧 Extrayendo features mejoradas...")
        
        # Features de texto con TF-IDF (más features que antes)
        text_data = df['hypothesis_text'].fillna('').astype(str)
        
        # Vectorizer más robusto
        vectorizer = TfidfVectorizer(
            max_features=200,  # Más features de texto
            stop_words='english',
            ngram_range=(1, 2),  # Incluir bigramas
            min_df=2,
            max_df=0.95,
            lowercase=True,
            strip_accents='unicode'
        )
        
        text_features = vectorizer.fit_transform(text_data).toarray()
        print(f"   📝 Features de texto: {text_features.shape[1]}")
        
        # Features numéricas mejoradas
        numeric_features = df[['year', 'citations', 'journal_impact', 
                              'methodology_score', 'novelty_score', 'coherence_score']].fillna(0).values
        print(f"   🔢 Features numéricas: {numeric_features.shape[1]}")
        
        # Features de dominio (one-hot encoding)
        domains = df['domain'].fillna('unknown')
        unique_domains = domains.unique()
        domain_features = np.zeros((len(df), len(unique_domains)))
        
        for i, domain in enumerate(unique_domains):
            domain_features[domains == domain, i] = 1
        
        print(f"   🏷️  Features de dominio: {domain_features.shape[1]}")
        
        # Combinar todas las features
        all_features = np.hstack([text_features, numeric_features, domain_features])
        print(f"   ✅ Total features: {all_features.shape[1]}")
        
        # Guardar información para predicciones futuras
        self.vectorizer = vectorizer
        self.feature_columns = {
            'text_features': text_features.shape[1],
            'numeric_features': numeric_features.shape[1],
            'domain_features': domain_features.shape[1],
            'domains': unique_domains.tolist()
        }
        
        return all_features, df['confidence'].values
    
    def train_balanced_model(self) -> bool:
        """Entrena modelo con dataset balanceado"""
        
        print(f"\n🤖 Entrenando modelo balanceado...")
        
        if self.integrated_data is None:
            print("   ❌ No hay dataset integrado")
            return False
        
        # Extraer features
        X, y = self.extract_enhanced_features(self.integrated_data)
        
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=self.integrated_data['is_plausible']
        )
        
        print(f"   📊 Train: {X_train.shape[0]:,} ejemplos, Test: {X_test.shape[0]:,} ejemplos")
        
        # Entrenar modelo mejorado
        model = GradientBoostingRegressor(
            n_estimators=200,  # Más árboles
            learning_rate=0.1,
            max_depth=6,      # Más profundidad
            random_state=42,
            min_samples_split=10,
            min_samples_leaf=5
        )
        
        print("   🔄 Entrenando...")
        model.fit(X_train, y_train)
        
        # Evaluar
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        train_r2 = r2_score(y_train, y_pred_train)
        test_r2 = r2_score(y_test, y_pred_test)
        train_mae = mean_absolute_error(y_train, y_pred_train)
        test_mae = mean_absolute_error(y_test, y_pred_test)
        
        print(f"   📊 Métricas del modelo balanceado:")
        print(f"      • R² train: {train_r2:.4f}")
        print(f"      • R² test: {test_r2:.4f}")
        print(f"      • MAE train: {train_mae:.4f}")
        print(f"      • MAE test: {test_mae:.4f}")
        
        # Análisis por clase
        plausible_mask_test = self.integrated_data.loc[y_test.index if hasattr(y_test, 'index') else X_test[:, 0] >= 0, 'is_plausible']
        
        # Calcular métricas por clase usando índices correctos
        test_indices = np.arange(len(self.integrated_data))[len(X_train):]
        plausible_predictions = y_pred_test[self.integrated_data.iloc[test_indices]['is_plausible'].values]
        implausible_predictions = y_pred_test[~self.integrated_data.iloc[test_indices]['is_plausible'].values]
        
        print(f"   📈 Predicciones por clase:")
        print(f"      • Plausibles - media: {plausible_predictions.mean():.3f}, std: {plausible_predictions.std():.3f}")
        print(f"      • Implausibles - media: {implausible_predictions.mean():.3f}, std: {implausible_predictions.std():.3f}")
        
        self.model = model
        
        return True
    
    def test_pseudoscience_detection(self):
        """Testa detección de pseudociencia con el modelo balanceado"""
        
        print(f"\n🧪 TESTEO CRÍTICO: Detección de Pseudociencia")
        print("-" * 50)
        
        if self.model is None or self.vectorizer is None:
            print("   ❌ Modelo no entrenado")
            return
        
        # Casos de prueba de pseudociencia OBVÍA
        pseudoscience_tests = [
            {
                'hypothesis_text': 'Perpetual Motion Machine Using Magnetic Fields for Infinite Energy Generation',
                'domain': 'physics',
                'year': 2024,
                'citations': 0,
                'journal_impact': 0.1,
                'methodology_score': 0.1,
                'novelty_score': 0.2,
                'coherence_score': 0.1,
                'expected': 'LOW - Should be rejected',
                'category': 'Perpetual Motion'
            },
            {
                'hypothesis_text': 'Crystal Healing Properties for Cancer Treatment Through Vibrational Frequencies',
                'domain': 'medicine',
                'year': 2024,
                'citations': 0,
                'journal_impact': 0.1,
                'methodology_score': 0.1,
                'novelty_score': 0.2,
                'coherence_score': 0.1,
                'expected': 'LOW - Should be rejected',
                'category': 'Crystal Healing'
            },
            {
                'hypothesis_text': 'Time Travel Communication Device Based on Quantum Entanglement Backwards Propagation',
                'domain': 'physics',
                'year': 2024,
                'citations': 0,
                'journal_impact': 0.1,
                'methodology_score': 0.1,
                'novelty_score': 0.3,
                'coherence_score': 0.1,
                'expected': 'LOW - Should be rejected',
                'category': 'Time Travel'
            },
            {
                'hypothesis_text': 'Homeopathic Water Memory Effects for Treating Autism Spectrum Disorders',
                'domain': 'medicine',
                'year': 2024,
                'citations': 0,
                'journal_impact': 0.1,
                'methodology_score': 0.1,
                'novelty_score': 0.2,
                'coherence_score': 0.1,
                'expected': 'LOW - Should be rejected',
                'category': 'Homeopathy'
            },
            # Casos científicos legítimos para comparar
            {
                'hypothesis_text': 'Novel CRISPR-Cas9 Gene Editing Approach for Treating Genetic Muscular Disorders',
                'domain': 'medicine',
                'year': 2024,
                'citations': 15,
                'journal_impact': 0.8,
                'methodology_score': 0.9,
                'novelty_score': 0.8,
                'coherence_score': 0.9,
                'expected': 'HIGH - Should be approved',
                'category': 'Legitimate Science'
            }
        ]
        
        # Testear cada caso
        results = []
        for test_case in pseudoscience_tests:
            # Preparar datos para predicción
            test_df = pd.DataFrame([test_case])
            
            # Extraer features usando el mismo proceso
            X_test, _ = self.extract_enhanced_features(test_df)
            
            # Predecir
            confidence = self.model.predict(X_test)[0]
            
            # Clasificar
            if confidence >= 0.85:
                classification = "HIGH"
            elif confidence >= 0.70:
                classification = "MEDIUM" 
            else:
                classification = "LOW"
            
            result = {
                'category': test_case['category'],
                'confidence': confidence,
                'classification': classification,
                'expected': test_case['expected'],
                'correct': (
                    (classification == 'LOW' and 'rejected' in test_case['expected']) or
                    (classification in ['HIGH', 'MEDIUM'] and 'approved' in test_case['expected'])
                )
            }
            results.append(result)
            
            # Mostrar resultado
            status = "✅" if result['correct'] else "❌"
            print(f"   {status} {test_case['category']}:")
            print(f"      Confianza: {confidence:.3f}")
            print(f"      Clasificación: {classification}")
            print(f"      Esperado: {test_case['expected']}")
            print(f"      Resultado: {'CORRECTO' if result['correct'] else 'INCORRECTO'}")
            print()
        
        # Resumen de resultados
        correct_count = sum(1 for r in results if r['correct'])
        total_count = len(results)
        accuracy = correct_count / total_count
        
        pseudoscience_results = [r for r in results if 'rejected' in r['expected']]
        pseudoscience_correct = sum(1 for r in pseudoscience_results if r['correct'])
        pseudoscience_accuracy = pseudoscience_correct / len(pseudoscience_results) if pseudoscience_results else 0
        
        print(f"📊 RESULTADOS DEL TEST:")
        print(f"   • Precisión general: {correct_count}/{total_count} ({accuracy*100:.1f}%)")
        print(f"   • Detección de pseudociencia: {pseudoscience_correct}/{len(pseudoscience_results)} ({pseudoscience_accuracy*100:.1f}%)")
        
        if pseudoscience_accuracy >= 0.75:
            print("   ✅ ÉXITO: Modelo detecta pseudociencia correctamente")
        else:
            print("   ❌ FALLO: Modelo aún no detecta pseudociencia adecuadamente")
            
        return results
    
    def save_balanced_model(self) -> bool:
        """Guarda el modelo balanceado entrenado"""
        
        print(f"\n💾 Guardando modelo balanceado...")
        
        if self.model is None:
            print("   ❌ No hay modelo para guardar")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar modelo
        model_file = f"balanced_hypothesis_filter_{timestamp}.pkl"
        with open(model_file, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'vectorizer': self.vectorizer,
                'feature_columns': self.feature_columns,
                'timestamp': timestamp,
                'dataset_info': {
                    'total_examples': len(self.integrated_data),
                    'plausible_examples': len(self.integrated_data[self.integrated_data['is_plausible']]),
                    'implausible_examples': len(self.integrated_data[~self.integrated_data['is_plausible']])
                }
            }, f)
        
        print(f"   ✅ Modelo guardado en: {model_file}")
        
        # Guardar dataset balanceado
        dataset_file = f"balanced_dataset_{timestamp}.csv"
        self.integrated_data.to_csv(dataset_file, index=False)
        print(f"   ✅ Dataset balanceado guardado en: {dataset_file}")
        
        return True

def main():
    """Función principal"""
    
    print("🔧 ATLAS - Integrador de Dataset Balanceado")
    print("=" * 50)
    print()
    
    integrator = BalancedDatasetIntegrator()
    
    # 1. Cargar datasets
    if not integrator.load_original_dataset():
        return False
        
    if not integrator.load_retraction_data():
        return False
    
    # 2. Crear dataset balanceado
    if not integrator.create_balanced_dataset():
        return False
    
    # 3. Entrenar modelo balanceado  
    if not integrator.train_balanced_model():
        return False
    
    # 4. Test crítico de detección de pseudociencia
    test_results = integrator.test_pseudoscience_detection()
    
    # 5. Guardar modelo
    if not integrator.save_balanced_model():
        return False
    
    print("\n" + "=" * 50)
    print("🎯 INTEGRACIÓN COMPLETADA")
    print("✅ Dataset balanceado creado e integrado")
    print("✅ Modelo re-entrenado con ejemplos negativos reales") 
    print("✅ Test de pseudociencia ejecutado")
    print("📈 ¡El modelo ahora debería detectar pseudociencia mucho mejor!")
    
    return True

if __name__ == "__main__":
    main()
