"""
Script para generar datos de prueba realistas para análisis de series temporales.
Este script crea datos con diferentes patrones: tendencia, estacionalidad, ruido y anomalías.
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import random
from typing import Dict, List, Any


def generate_time_series_data() -> Dict[str, Any]:
    """
    Genera datos de series temporales realistas con diferentes patrones.
    
    Returns:
        Dict con datos de series temporales y metadatos
    """
    # Configuración base
    np.random.seed(42)  # Para reproducibilidad
    n_points = 365  # Un año de datos diarios
    start_date = datetime(2023, 1, 1)
    
    # Generar fechas
    dates = [start_date + timedelta(days=i) for i in range(n_points)]
    
    # Componentes de la serie temporal
    
    # 1. Tendencia lineal creciente
    trend = np.linspace(100, 200, n_points)
    
    # 2. Estacionalidad (semanal y mensual)
    # Estacionalidad semanal (7 días)
    weekly_seasonality = 20 * np.sin(2 * np.pi * np.arange(n_points) / 7)
    
    # Estacionalidad mensual (30 días)  
    monthly_seasonality = 10 * np.cos(2 * np.pi * np.arange(n_points) / 30)
    
    # 3. Ruido aleatorio
    noise = 5 * np.random.normal(0, 1, n_points)
    
    # 4. Combinar componentes
    base_series = trend + weekly_seasonality + monthly_seasonality + noise
    
    # 5. Agregar algunas anomalías
    series_with_anomalies = base_series.copy()
    
    # Anomalías puntuales (outliers)
    anomaly_indices = [50, 120, 200, 280, 340]
    for idx in anomaly_indices:
        series_with_anomalies[idx] += random.choice([-40, 60])
    
    # 6. Crear datos estructurados
    data_points = []
    for i, date in enumerate(dates):
        data_points.append({
            "timestamp": date.isoformat(),
            "value": float(series_with_anomalies[i]),
            "is_anomaly": i in anomaly_indices,
            "day_of_week": date.weekday(),
            "month": date.month,
            "week_of_year": date.isocalendar()[1]
        })
    
    # 7. Metadatos descriptivos
    metadata = {
        "dataset_name": "serie_temporal_ejemplo_2023",
        "description": "Datos sintéticos de series temporales con tendencia, estacionalidad y anomalías",
        "time_unit": "daily",
        "n_points": n_points,
        "start_date": start_date.isoformat(),
        "end_date": dates[-1].isoformat(),
        "components": {
            "trend": "lineal_creciente",
            "seasonality": ["semanal", "mensual"],
            "noise": "normal_distribution",
            "anomalies": "puntuales"
        },
        "generated_at": datetime.now().isoformat()
    }
    
    return {
        "metadata": metadata,
        "data": data_points
    }


def generate_multiple_series() -> Dict[str, Any]:
    """
    Genera múltiples series temporales con diferentes características.
    """
    series_collection = {}
    
    # Serie 1: Tendencia fuerte + estacionalidad
    series_collection["strong_trend_seasonal"] = generate_series_with_params(
        trend_strength=2.0,
        seasonal_strength=1.5,
        noise_level=0.3,
        anomaly_count=3
    )
    
    # Serie 2: Tendencia suave + ruido
    series_collection["weak_trend_noisy"] = generate_series_with_params(
        trend_strength=0.5, 
        seasonal_strength=0.1,
        noise_level=1.0,
        anomaly_count=2
    )
    
    # Serie 3: Estacionalidad dominante
    series_collection["strong_seasonal"] = generate_series_with_params(
        trend_strength=0.1,
        seasonal_strength=2.5,
        noise_level=0.2,
        anomaly_count=4
    )
    
    # Serie 4: Datos casi estacionarios
    series_collection["stationary_like"] = generate_series_with_params(
        trend_strength=0.05,
        seasonal_strength=0.1,
        noise_level=0.8,
        anomaly_count=1
    )
    
    return {
        "collection_name": "multiple_time_series_dataset",
        "description": "Colección de series temporales con diferentes patrones para testing",
        "series_count": len(series_collection),
        "series": series_collection
    }


def generate_series_with_params(trend_strength: float, seasonal_strength: float, 
                               noise_level: float, anomaly_count: int) -> Dict[str, Any]:
    """
    Genera una serie temporal con parámetros personalizados.
    """
    np.random.seed(42)
    n_points = 180  # 6 meses de datos
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_points)]
    
    # Componentes
    trend = trend_strength * np.linspace(0, 100, n_points)
    weekly_seasonality = seasonal_strength * 10 * np.sin(2 * np.pi * np.arange(n_points) / 7)
    monthly_seasonality = seasonal_strength * 5 * np.cos(2 * np.pi * np.arange(n_points) / 30)
    noise = noise_level * 5 * np.random.normal(0, 1, n_points)
    
    # Serie combinada
    series = trend + weekly_seasonality + monthly_seasonality + noise
    
    # Agregar anomalías
    anomaly_indices = random.sample(range(n_points), min(anomaly_count, n_points))
    for idx in anomaly_indices:
        series[idx] += random.choice([-30, 40])
    
    # Crear datos
    data_points = []
    for i, date in enumerate(dates):
        data_points.append({
            "timestamp": date.isoformat(),
            "value": float(series[i]),
            "is_anomaly": i in anomaly_indices
        })
    
    return {
        "parameters": {
            "trend_strength": trend_strength,
            "seasonal_strength": seasonal_strength,
            "noise_level": noise_level,
            "anomaly_count": anomaly_count
        },
        "data": data_points
    }


def save_test_data():
    """
    Guarda datos de prueba en archivos JSON.
    """
    # Datos individuales
    single_series_data = generate_time_series_data()
    with open("test_data/single_time_series.json", "w") as f:
        json.dump(single_series_data, f, indent=2, ensure_ascii=False)
    
    # Datos múltiples
    multiple_series_data = generate_multiple_series()
    with open("test_data/multiple_time_series.json", "w") as f:
        json.dump(multiple_series_data, f, indent=2, ensure_ascii=False)
    
    print("Datos de prueba generados y guardados en:")
    print("- test_data/single_time_series.json")
    print("- test_data/multiple_time_series.json")


if __name__ == "__main__":
    import os
    
    # Crear directorio si no existe
    os.makedirs("test_data", exist_ok=True)
    
    # Generar y guardar datos
    save_test_data()
    
    print("\nEjemplos de datos generados:")
    
    # Mostrar ejemplo de datos
    sample_data = generate_time_series_data()
    print(f"\nPrimeros 5 puntos de datos:")
    for i, point in enumerate(sample_data["data"][:5]):
        print(f"  {i+1}. {point['timestamp']}: {point['value']:.2f}")
    
    print(f"\nTotal de puntos: {len(sample_data['data'])}")
    print(f"Anomalías: {sum(1 for p in sample_data['data'] if p['is_anomaly'])}")