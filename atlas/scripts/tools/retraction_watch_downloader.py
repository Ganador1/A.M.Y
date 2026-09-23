"""
🔧 ATLAS - Descargador de Retraction Watch Database  
===================================================

Este script descarga la base de datos de Retraction Watch desde Crossref Labs
para crear nuestro dataset negativo balanceado.

URL API: https://api.labs.crossref.org/data/retractionwatch
Formato: CSV descargable
Tamaño: ~60,000+ papers retractados
"""

import requests
import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class RetractionWatchDownloader:
    """Descargador de datos de Retraction Watch desde Crossref Labs"""
    
    def __init__(self):
        self.base_url = "https://api.labs.crossref.org"
        self.retraction_endpoint = "/data/retractionwatch"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ATLAS-Hypothesis-Filter/1.0 (https://github.com/sapientinc/atlas)',
            'Accept': 'text/csv,application/json,*/*'
        })
        
    def download_retraction_database(self, email: str = "atlas@example.com") -> Optional[pd.DataFrame]:
        """
        Descarga la base de datos de Retraction Watch
        
        Args:
            email: Email requerido por la API de Crossref
            
        Returns:
            DataFrame con los datos de papers retractados o None si falla
        """
        print("📥 Descargando Retraction Watch Database...")
        print(f"   Endpoint: {self.base_url}{self.retraction_endpoint}")
        print(f"   Email: {email}")
        
        try:
            # Construir URL con email
            params = {'mailto': email}
            url = f"{self.base_url}{self.retraction_endpoint}"
            
            print(f"   Solicitando datos desde: {url}")
            response = self.session.get(url, params=params, timeout=120)
            
            print(f"   Status code: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
            print(f"   Content-Length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                # Guardar respuesta cruda
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                raw_file = f"retraction_watch_raw_{timestamp}.csv"
                
                with open(raw_file, 'wb') as f:
                    f.write(response.content)
                print(f"   ✅ Datos crudos guardados en: {raw_file}")
                
                # Intentar parsear como CSV
                try:
                    # Leer las primeras líneas para entender el formato
                    content_preview = response.content.decode('utf-8')[:1000]
                    print(f"   📄 Vista previa del contenido:")
                    print("   " + "\n   ".join(content_preview.split('\n')[:10]))
                    
                    # Parsear CSV
                    df = pd.read_csv(raw_file, encoding='utf-8')
                    print(f"   ✅ CSV parseado exitosamente")
                    print(f"   📊 Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
                    print(f"   🏷️  Columnas: {list(df.columns[:10])}{'...' if len(df.columns) > 10 else ''}")
                    
                    return df
                    
                except Exception as e:
                    print(f"   ❌ Error parseando CSV: {e}")
                    # Intentar otros formatos o encodings
                    try:
                        df = pd.read_csv(raw_file, encoding='latin-1')
                        print(f"   ✅ CSV parseado con encoding latin-1")
                        return df
                    except Exception as e2:
                        print(f"   ❌ Error con encoding latin-1: {e2}")
                        return None
                        
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                print(f"   📄 Respuesta: {response.text[:500]}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")
            return None
            
    def analyze_retraction_data(self, df: pd.DataFrame) -> Dict:
        """Analiza los datos de retracciones para entender su estructura"""
        
        print("\n📊 ANÁLISIS DE DATOS DE RETRACTION WATCH:")
        print("-" * 45)
        
        analysis = {
            'total_retractions': len(df),
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'sample_data': {},
            'missing_data': {},
            'value_counts': {},
            'date_range': None
        }
        
        # Información básica
        print(f"📈 Total de papers retractados: {len(df):,}")
        print(f"📑 Columnas disponibles ({len(df.columns)}): {list(df.columns)}")
        
        # Análisis de columnas clave
        key_columns = ['Title', 'Journal', 'Reason', 'DOI', 'Date', 'Year']
        existing_key_columns = [col for col in key_columns if col in df.columns]
        
        print(f"\n🔑 Columnas clave encontradas: {existing_key_columns}")
        
        # Muestra de datos
        print(f"\n📋 Muestra de los primeros 3 registros:")
        for i, (idx, row) in enumerate(df.head(3).iterrows()):
            print(f"   📄 Registro {i+1}:")
            for col in df.columns[:5]:  # Mostrar solo las primeras 5 columnas
                value = str(row[col])[:100] + "..." if len(str(row[col])) > 100 else str(row[col])
                print(f"      {col}: {value}")
            print()
        
        # Datos faltantes
        print(f"\n❓ Datos faltantes por columna:")
        missing_stats = df.isnull().sum()
        for col, missing_count in missing_stats.items():
            percentage = (missing_count / len(df)) * 100
            print(f"   {col}: {missing_count:,} ({percentage:.1f}%)")
            analysis['missing_data'][col] = {'count': int(missing_count), 'percentage': round(percentage, 1)}
        
        # Análisis de razones de retractación (si existe la columna)
        reason_columns = [col for col in df.columns if 'reason' in col.lower() or 'retraction' in col.lower()]
        if reason_columns:
            print(f"\n📊 Razones de retractación (columna: {reason_columns[0]}):")
            reason_counts = df[reason_columns[0]].value_counts().head(10)
            for reason, count in reason_counts.items():
                percentage = (count / len(df)) * 100
                print(f"   {reason}: {count:,} ({percentage:.1f}%)")
            analysis['value_counts']['retraction_reasons'] = reason_counts.to_dict()
        
        # Análisis temporal (si hay columnas de fecha)
        date_columns = [col for col in df.columns if any(date_term in col.lower() for date_term in ['date', 'year', 'published'])]
        if date_columns:
            print(f"\n📅 Análisis temporal (columna: {date_columns[0]}):")
            try:
                if 'year' in date_columns[0].lower():
                    years = pd.to_numeric(df[date_columns[0]], errors='coerce').dropna()
                    print(f"   Rango de años: {int(years.min())} - {int(years.max())}")
                    print(f"   Distribución por década:")
                    decade_counts = (years // 10 * 10).value_counts().sort_index().tail(5)
                    for decade, count in decade_counts.items():
                        print(f"     {int(decade)}s: {count:,}")
                    analysis['date_range'] = {'min': int(years.min()), 'max': int(years.max())}
            except Exception as e:
                print(f"   ❌ Error analizando fechas: {e}")
        
        return analysis
    
    def create_negative_dataset_sample(self, df: pd.DataFrame, sample_size: int = 1000) -> pd.DataFrame:
        """Crea una muestra del dataset negativo para pruebas"""
        
        print(f"\n🔨 Creando muestra de dataset negativo ({sample_size:,} ejemplos)...")
        
        # Tomar muestra aleatoria
        if len(df) > sample_size:
            sample_df = df.sample(n=sample_size, random_state=42)
            print(f"   ✅ Muestra aleatoria de {sample_size:,} de {len(df):,} total")
        else:
            sample_df = df.copy()
            print(f"   ℹ️  Dataset completo usado ({len(df):,} ejemplos)")
        
        # Intentar extraer información relevante para nuestro filtro
        negative_examples = []
        
        for idx, row in sample_df.iterrows():
            example = {
                'source': 'retraction_watch',
                'confidence': 0.0,  # Baja confianza para papers retractados
                'is_plausible': False,  # Definitivamente no plausible
                'row_data': row.to_dict()
            }
            
            # Extraer título si está disponible
            title_columns = [col for col in df.columns if 'title' in col.lower()]
            if title_columns:
                example['title'] = str(row[title_columns[0]])
            
            # Extraer razón si está disponible
            reason_columns = [col for col in df.columns if 'reason' in col.lower()]
            if reason_columns:
                example['retraction_reason'] = str(row[reason_columns[0]])
            
            # Extraer journal si está disponible
            journal_columns = [col for col in df.columns if 'journal' in col.lower()]
            if journal_columns:
                example['journal'] = str(row[journal_columns[0]])
            
            negative_examples.append(example)
        
        # Crear DataFrame estructurado
        result_df = pd.DataFrame(negative_examples)
        
        print(f"   ✅ Dataset negativo creado: {len(result_df):,} ejemplos")
        print(f"   📊 Columnas: {list(result_df.columns)}")
        
        return result_df

def main():
    """Función principal"""
    
    print("🔧 ATLAS - Descargador de Retraction Watch Database")
    print("=" * 55)
    print()
    
    downloader = RetractionWatchDownloader()
    
    # Descargar datos
    email = "atlas.research@example.com"  # Email requerido por Crossref
    df = downloader.download_retraction_database(email)
    
    if df is not None:
        # Analizar datos
        analysis = downloader.analyze_retraction_data(df)
        
        # Crear muestra de dataset negativo
        negative_sample = downloader.create_negative_dataset_sample(df, sample_size=1000)
        
        # Guardar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Guardar análisis
        analysis_file = f"retraction_watch_analysis_{timestamp}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Análisis guardado en: {analysis_file}")
        
        # Guardar muestra de dataset negativo
        sample_file = f"negative_dataset_sample_{timestamp}.csv"
        negative_sample.to_csv(sample_file, index=False, encoding='utf-8')
        print(f"💾 Muestra de dataset negativo guardada en: {sample_file}")
        
        # Guardar dataset completo procesado
        processed_file = f"retraction_watch_processed_{timestamp}.csv"
        df.to_csv(processed_file, index=False, encoding='utf-8')
        print(f"💾 Dataset completo guardado en: {processed_file}")
        
        print(f"\n🎯 RESUMEN:")
        print(f"   • Papers retractados descargados: {len(df):,}")
        print(f"   • Muestra para dataset negativo: {len(negative_sample):,}")
        print(f"   • Próximo paso: Integrar con dataset actual y re-entrenar modelo")
        print(f"   • Beneficio esperado: Mejor detección de pseudociencia")
        
        return True
        
    else:
        print("❌ No se pudieron descargar los datos de Retraction Watch")
        
        # Crear dataset sintético mínimo como fallback
        print("\n🔧 Creando dataset sintético como fallback...")
        synthetic_negative = create_synthetic_pseudoscience_examples()
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        synthetic_file = f"synthetic_negative_dataset_{timestamp}.csv"
        synthetic_negative.to_csv(synthetic_file, index=False, encoding='utf-8')
        print(f"💾 Dataset sintético guardado en: {synthetic_file}")
        
        return False

def create_synthetic_pseudoscience_examples() -> pd.DataFrame:
    """Crear ejemplos sintéticos de pseudociencia como fallback"""
    
    synthetic_examples = [
        {
            'title': 'Perpetual Motion Machine Using Magnetic Fields for Infinite Energy Generation',
            'confidence': 0.0,
            'is_plausible': False,
            'source': 'synthetic',
            'category': 'perpetual_motion',
            'reason': 'Violates first law of thermodynamics'
        },
        {
            'title': 'Crystal Healing Properties for Cancer Treatment Through Vibrational Frequencies',
            'confidence': 0.0,
            'is_plausible': False,
            'source': 'synthetic',
            'category': 'alternative_medicine',
            'reason': 'No scientific mechanism or evidence'
        },
        {
            'title': 'Time Travel Communication Device Based on Quantum Entanglement Backwards Propagation',
            'confidence': 0.0,
            'is_plausible': False,
            'source': 'synthetic',
            'category': 'time_travel',
            'reason': 'Violates causality and known physics'
        },
        {
            'title': 'Homeopathic Water Memory Effects for Treating Autism Spectrum Disorders',
            'confidence': 0.0,
            'is_plausible': False,
            'source': 'synthetic',
            'category': 'homeopathy',
            'reason': 'Water has no memory mechanism'
        },
        {
            'title': 'Free Energy Device Extracting Zero-Point Energy from Vacuum Fluctuations',
            'confidence': 0.0,
            'is_plausible': False,
            'source': 'synthetic',
            'category': 'free_energy',
            'reason': 'Misunderstands quantum mechanics'
        }
    ]
    
    return pd.DataFrame(synthetic_examples)

if __name__ == "__main__":
    main()
