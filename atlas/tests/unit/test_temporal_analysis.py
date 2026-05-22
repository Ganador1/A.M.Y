"""
Script para probar el endpoint de análisis de series temporales.
Este script envía datos de prueba al endpoint y muestra los resultados.
"""

import requests
import json
import time
from typing import Dict, Any


BASE_URL = "http://localhost:8000/ai-scientist"


def test_temporal_analysis_endpoint():
    """
    Prueba el endpoint de análisis de tendencias temporales.
    """
    print("🧪 Probando endpoint de análisis de series temporales...")
    
    # Cargar datos de prueba
    try:
        with open("test_data/single_time_series.json", "r") as f:
            test_data = json.load(f)
    except FileNotFoundError:
        print("❌ Error: No se encontraron datos de prueba")
        print("Ejecuta primero: python generate_test_data.py")
        return
    
    # Preparar payload para la API
    payload = {
        "time_series_data": test_data["data"],
        "analysis_type": "comprehensive",
        "parameters": {
            "confidence_level": 0.95,
            "seasonality_periods": [7, 30],
            "detect_anomalies": True,
            "forecast_periods": 30
        }
    }
    
    # Realizar la petición
    try:
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/analyze-temporal-trends",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120  # 2 minutos de timeout
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"⏱️  Tiempo de respuesta: {elapsed_time:.2f} segundos")
        
        if response.status_code == 200:
            print("✅ Petición exitosa!")
            
            # Mostrar resultados
            results = response.json()
            
            print(f"\n📊 RESULTADOS DEL ANÁLISIS:")
            print(f"🔹 Estado: {results.get('status', 'N/A')}")
            print(f"🔹 ID del análisis: {results.get('analysis_id', 'N/A')}")
            
            # Métricas principales
            metrics = results.get('metrics', {})
            print(f"\n📈 MÉTRICAS PRINCIPALES:")
            print(f"   • Tendencia detectada: {metrics.get('trend_detected', 'N/A')}")
            print(f"   • Coeficiente de tendencia: {metrics.get('trend_coefficient', 'N/A'):.4f}")
            print(f"   • Estacionalidad detectada: {metrics.get('seasonality_detected', 'N/A')}")
            print(f"   • Estacionariedad (p-value): {metrics.get('stationarity_p_value', 'N/A'):.4f}")
            print(f"   • Anomalías detectadas: {metrics.get('anomalies_detected', 'N/A')}")
            
            # Insights
            insights = results.get('insights', [])
            if insights:
                print(f"\n💡 INSIGHTS CIENTÍFICOS:")
                for i, insight in enumerate(insights[:3], 1):  # Mostrar primeros 3
                    print(f"   {i}. {insight}")
            
            # Forecast
            forecast = results.get('forecast', {})
            if forecast:
                print(f"\n🔮 PRONÓSTICO:")
                print(f"   • Períodos: {forecast.get('periods', 'N/A')}")
                print(f"   • Valores pronosticados: {len(forecast.get('values', []))}")
            
            # Guardar resultados completos
            with open("test_data/analysis_results.json", "w") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            print(f"\n💾 Resultados completos guardados en: test_data/analysis_results.json")
            
        else:
            print(f"❌ Error en la petición: {response.status_code}")
            print(f"Mensaje: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("Asegúrate de que el servidor esté ejecutándose en http://localhost:8000")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


def test_status_endpoint():
    """
    Prueba el endpoint de estado del servicio.
    """
    print("\n🔍 Probando endpoint de estado...")
    
    try:
        response = requests.get(f"{BASE_URL}/status", timeout=10)
        
        if response.status_code == 200:
            status_data = response.json()
            print("✅ Estado del servicio:")
            print(f"   • Servicio: {status_data.get('service', 'N/A')}")
            print(f"   • Versión: {status_data.get('version', 'N/A')}")
            print(f"   • Estado: {status_data.get('status', 'N/A')}")
            print(f"   • Timestamp: {status_data.get('timestamp', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_capabilities_endpoint():
    """
    Prueba el endpoint de capacidades.
    """
    print("\n🔧 Probando endpoint de capacidades...")
    
    try:
        response = requests.get(f"{BASE_URL}/capabilities", timeout=10)
        
        if response.status_code == 200:
            capabilities = response.json()
            print("✅ Capacidades del servicio:")
            
            for category, methods in capabilities.items():
                print(f"\n📋 {category.upper()}:")
                for method in methods:
                    print(f"   • {method}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def test_generate_test_data_endpoint():
    """
    Prueba el endpoint de generación de datos de prueba.
    """
    print("\n🧪 Probando endpoint de generación de datos de prueba...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/generate-test-data",
            json={
                "n_points": 50,
                "trend_strength": 1.0,
                "seasonal_strength": 0.8,
                "noise_level": 0.3,
                "anomaly_count": 2
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            test_data = response.json()
            print("✅ Datos de prueba generados:")
            print(f"   • Puntos generados: {len(test_data.get('data', []))}")
            print(f"   • Parámetros: {test_data.get('parameters', {})}")
            
            # Mostrar primeros 3 puntos
            data_points = test_data.get('data', [])[:3]
            for i, point in enumerate(data_points, 1):
                print(f"   • Punto {i}: {point['timestamp']} = {point['value']:.2f}")
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 TESTEO DEL ENDPOINT DE ANÁLISIS DE SERIES TEMPORALES")
    print("=" * 60)
    
    # Esperar un poco para que el servidor se inicie completamente
    print("⏳ Esperando que el servidor esté listo...")
    time.sleep(3)
    
    # Probar endpoints
    test_status_endpoint()
    test_capabilities_endpoint()
    test_generate_test_data_endpoint()
    test_temporal_analysis_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ Pruebas completadas!")
    print("=" * 60)