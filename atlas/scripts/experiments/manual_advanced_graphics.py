#!/usr/bin/env python3
"""
Pruebas avanzadas para la generación de gráficos
Incluye expresiones complejas y gráficos 3D
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_graphing_endpoint(endpoint, data, description):
    """Test a graphing endpoint with detailed output"""
    try:
        print(f"\n{'='*60}")
        print(f"🎯 PROBANDO: {description}")
        print(f"📡 Endpoint: {endpoint}")
        print(f"📄 Datos: {json.dumps(data, indent=2)}")
        print(f"{'='*60}")
        
        response = requests.post(f"{BASE_URL}{endpoint}", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ ÉXITO - Status: {response.status_code}")
            print(f"📊 Respuesta: {json.dumps(result, indent=2)}")
            
            # Si hay una imagen, mostrar la ruta
            if 'data' in result and 'image_path' in result['data']:
                image_path = result['data']['image_path']
                print(f"🖼️  Imagen generada: {image_path}")
                print(f"🌐 URL: {BASE_URL}/{image_path}")
        else:
            print(f"❌ ERROR - Status: {response.status_code}")
            print(f"💥 Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Error de conexión: {e}")
    except Exception as e:
        print(f"💥 Error: {e}")

def main():
    print("🧮 MATHEMATICS AI - PRUEBAS AVANZADAS DE GRÁFICOS")
    print("=" * 80)
    
    # 1. FUNCIONES COMPLEJAS 2D
    print("\n🔥 PROBANDO FUNCIONES COMPLEJAS 2D")
    
    complex_2d_expressions = [
        {
            "endpoint": "/api/graphing/generate",
            "data": {
                "expression": "sin(x)*cos(x)*exp(-x**2/10)",
                "x_min": -10,
                "x_max": 10,
                "points": 1000
            },
            "description": "Función oscilante con decaimiento exponencial"
        },
        {
            "endpoint": "/api/graphing/generate", 
            "data": {
                "expression": "x**3 - 6*x**2 + 9*x + 1",
                "x_min": -2,
                "x_max": 6,
                "points": 500
            },
            "description": "Polinomio cúbico con puntos críticos"
        },
        {
            "endpoint": "/api/graphing/generate",
            "data": {
                "expression": "tan(x)/(1 + x**2)",
                "x_min": -5,
                "x_max": 5,
                "points": 2000
            },
            "description": "Tangente dividida por función cuadrática"
        },
        {
            "endpoint": "/api/graphing/generate",
            "data": {
                "expression": "sqrt(abs(x))*sin(x**2)",
                "x_min": -4,
                "x_max": 4,
                "points": 1500
            },
            "description": "Raíz de valor absoluto con seno de x²"
        },
        {
            "endpoint": "/api/graphing/generate",
            "data": {
                "expression": "(sin(x) + cos(2*x))*exp(-abs(x)/5)",
                "x_min": -15,
                "x_max": 15,
                "points": 2000
            },
            "description": "Superposición de ondas con decaimiento"
        }
    ]
    
    for test_case in complex_2d_expressions:
        test_graphing_endpoint(
            test_case["endpoint"], 
            test_case["data"], 
            test_case["description"]
        )
        time.sleep(1)  # Pausa entre pruebas
    
    # 2. MÚLTIPLES FUNCIONES
    print("\n🎨 PROBANDO MÚLTIPLES FUNCIONES EN UN GRÁFICO")
    
    multiple_functions_test = {
        "endpoint": "/api/graphing/multiple",
        "data": {
            "expressions": [
                "sin(x)",
                "cos(x)", 
                "sin(x)*cos(x)",
                "sin(2*x)/2",
                "exp(-x**2/8)"
            ],
            "x_min": -6,
            "x_max": 6,
            "points": 1000
        },
        "description": "Múltiples funciones trigonométricas y exponencial"
    }
    
    test_graphing_endpoint(
        multiple_functions_test["endpoint"],
        multiple_functions_test["data"], 
        multiple_functions_test["description"]
    )
    
    # 3. GRÁFICOS 3D - ¡LO MÁS EMOCIONANTE!
    print("\n🌌 PROBANDO GRÁFICOS 3D ESPECTACULARES")
    
    threed_expressions = [
        {
            "endpoint": "/api/graphing/3d",
            "data": {
                "expression": "sin(sqrt(x**2 + y**2))",
                "x_min": -10,
                "x_max": 10,
                "y_min": -10,
                "y_max": 10,
                "points": 50
            },
            "description": "Ondas circulares 3D (función sinc 2D)"
        },
        {
            "endpoint": "/api/graphing/3d",
            "data": {
                "expression": "x**2 - y**2",
                "x_min": -3,
                "x_max": 3,
                "y_min": -3,
                "y_max": 3,
                "points": 60
            },
            "description": "Silla de montar (paraboloide hiperbólico)"
        },
        {
            "endpoint": "/api/graphing/3d",
            "data": {
                "expression": "exp(-(x**2 + y**2)/4)*cos(x)*sin(y)",
                "x_min": -5,
                "x_max": 5,
                "y_min": -5,
                "y_max": 5,
                "points": 80
            },
            "description": "Gaussiana modulada con ondas trigonométricas"
        },
        {
            "endpoint": "/api/graphing/3d",
            "data": {
                "expression": "cos(x)*cos(y)*exp(-(x**2 + y**2)/10)",
                "x_min": -8,
                "x_max": 8,
                "y_min": -8,
                "y_max": 8,
                "points": 70
            },
            "description": "Patrón de interferencia 3D"
        },
        {
            "endpoint": "/api/graphing/3d",
            "data": {
                "expression": "sin(x*y)/(x*y + 0.1)",
                "x_min": -3,
                "x_max": 3,
                "y_min": -3,
                "y_max": 3,
                "points": 100
            },
            "description": "Función sinc bidimensional"
        }
    ]
    
    for test_case in threed_expressions:
        test_graphing_endpoint(
            test_case["endpoint"],
            test_case["data"], 
            test_case["description"]
        )
        time.sleep(2)  # Pausa más larga para gráficos 3D
    
    # 4. GRÁFICOS POLARES
    print("\n🌀 PROBANDO GRÁFICOS POLARES")
    
    polar_test = {
        "endpoint": "/api/graphing/polar",
        "data": {
            "expression": "2 + cos(5*theta)",
            "theta_min": 0,
            "theta_max": 6.28,  # 2π
            "points": 1000
        },
        "description": "Rosa polar de 5 pétalos"
    }
    
    test_graphing_endpoint(
        polar_test["endpoint"],
        polar_test["data"], 
        polar_test["description"]
    )
    
    print("\n" + "="*80)
    print("🎉 PRUEBAS COMPLETADAS!")
    print("🖼️  Revisa las imágenes generadas en: http://localhost:8001/docs")
    print("📁 Los archivos están en: static/graphs/")
    print("="*80)

if __name__ == "__main__":
    main()
