#!/usr/bin/env python3
"""
Expresiones de prueba para generación de gráficos - Mathematics AI
Test expressions for graph generation
"""

import requests
import json
import os

BASE_URL = "http://localhost:8001"

# Colección de expresiones matemáticas para probar
GRAPH_EXPRESSIONS = {
    "funciones_basicas": {
        "description": "Funciones matemáticas básicas",
        "expressions": [
            {
                "name": "Función lineal",
                "expression": "2*x + 1",
                "x_min": -10,
                "x_max": 10,
                "description": "Una línea recta con pendiente 2"
            },
            {
                "name": "Función cuadrática",
                "expression": "x**2",
                "x_min": -5,
                "x_max": 5,
                "description": "Parábola básica"
            },
            {
                "name": "Función cúbica",
                "expression": "x**3 - 3*x",
                "x_min": -3,
                "x_max": 3,
                "description": "Función cúbica con inflexión"
            },
            {
                "name": "Función raíz cuadrada",
                "expression": "sqrt(x)",
                "x_min": 0,
                "x_max": 25,
                "description": "Función raíz cuadrada"
            }
        ]
    },
    
    "funciones_trigonometricas": {
        "description": "Funciones trigonométricas",
        "expressions": [
            {
                "name": "Seno",
                "expression": "sin(x)",
                "x_min": -6.28,
                "x_max": 6.28,
                "description": "Función seno de -2π a 2π"
            },
            {
                "name": "Coseno",
                "expression": "cos(x)",
                "x_min": -6.28,
                "x_max": 6.28,
                "description": "Función coseno de -2π a 2π"
            },
            {
                "name": "Tangente",
                "expression": "tan(x)",
                "x_min": -3.14,
                "x_max": 3.14,
                "description": "Función tangente con asíntotas"
            },
            {
                "name": "Seno amortiguado",
                "expression": "exp(-x/5) * sin(x)",
                "x_min": 0,
                "x_max": 20,
                "description": "Oscilación amortiguada exponencialmente"
            }
        ]
    },
    
    "funciones_exponenciales": {
        "description": "Funciones exponenciales y logarítmicas",
        "expressions": [
            {
                "name": "Exponencial natural",
                "expression": "exp(x)",
                "x_min": -3,
                "x_max": 3,
                "description": "Función e^x"
            },
            {
                "name": "Exponencial decreciente",
                "expression": "exp(-x)",
                "x_min": -1,
                "x_max": 5,
                "description": "Función e^(-x)"
            },
            {
                "name": "Logaritmo natural",
                "expression": "log(x)",
                "x_min": 0.1,
                "x_max": 10,
                "description": "Función ln(x)"
            },
            {
                "name": "Función Gaussiana",
                "expression": "exp(-x**2)",
                "x_min": -4,
                "x_max": 4,
                "description": "Campana de Gauss"
            }
        ]
    },
    
    "funciones_complejas": {
        "description": "Funciones matemáticas complejas",
        "expressions": [
            {
                "name": "Función racional",
                "expression": "1/(x**2 + 1)",
                "x_min": -5,
                "x_max": 5,
                "description": "Función racional con denominador cuadrático"
            },
            {
                "name": "Función sinc",
                "expression": "sin(x)/x",
                "x_min": -15,
                "x_max": 15,
                "description": "Función sinc sin(x)/x"
            },
            {
                "name": "Polinomio de grado 4",
                "expression": "x**4 - 5*x**2 + 4",
                "x_min": -3,
                "x_max": 3,
                "description": "Polinomio cuártico con múltiples raíces"
            },
            {
                "name": "Función hiperbólica",
                "expression": "sinh(x)",
                "x_min": -3,
                "x_max": 3,
                "description": "Seno hiperbólico"
            }
        ]
    },
    
    "funciones_especiales": {
        "description": "Funciones matemáticas especiales",
        "expressions": [
            {
                "name": "Función escalón modificada",
                "expression": "atan(10*x)",
                "x_min": -2,
                "x_max": 2,
                "description": "Aproximación suave de función escalón"
            },
            {
                "name": "Oscilación con frecuencia variable",
                "expression": "sin(x**2)",
                "x_min": -4,
                "x_max": 4,
                "description": "Seno con frecuencia cuadrática"
            },
            {
                "name": "Función de Witch of Agnesi",
                "expression": "1/(1 + x**2)",
                "x_min": -5,
                "x_max": 5,
                "description": "Curva de Agnesi"
            },
            {
                "name": "Función logística",
                "expression": "1/(1 + exp(-x))",
                "x_min": -6,
                "x_max": 6,
                "description": "Función sigmoide/logística"
            }
        ]
    }
}

def test_graph_generation(expression_data):
    """Test graph generation for a specific expression"""
    print(f"\\n🎯 Testing: {expression_data['name']}")
    print(f"📝 Expression: {expression_data['expression']}")
    print(f"📖 Description: {expression_data['description']}")
    
    try:
        # Preparar datos para la API
        graph_request = {
            "expression": expression_data["expression"],
            "x_min": expression_data["x_min"],
            "x_max": expression_data["x_max"],
            "points": 1000,
            "variable": "x"
        }
        
        # Hacer petición a la API
        response = requests.post(
            f"{BASE_URL}/api/graphing/generate",
            json=graph_request,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'Graph generated')}")
            if 'data' in result and 'image_path' in result['data']:
                print(f"📊 Graph saved to: {result['data']['image_path']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Connection error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

def main():
    """Main function to test all graph expressions"""
    print("🔬 Mathematics AI - Graph Generation Test Suite")
    print("=" * 60)
    
    # Verificar que el servidor esté ejecutándose
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not responding. Please start the server first.")
            return
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server. Please start the server first.")
        return
    
    # Probar cada categoría de funciones
    for category, category_data in GRAPH_EXPRESSIONS.items():
        print(f"\\n📁 Category: {category_data['description']}")
        print("-" * 50)
        
        for expression in category_data["expressions"]:
            test_graph_generation(expression)
    
    print("\\n🎉 Graph generation testing completed!")
    print("\\n📝 Summary of test expressions:")
    for category, category_data in GRAPH_EXPRESSIONS.items():
        print(f"\\n{category_data['description']}:")
        for expr in category_data["expressions"]:
            print(f"  • {expr['name']}: {expr['expression']}")

def print_expressions_only():
    """Print just the expressions for manual testing"""
    print("🎯 EXPRESIONES PARA PROBAR GRÁFICOS")
    print("=" * 50)
    
    for category, category_data in GRAPH_EXPRESSIONS.items():
        print(f"\\n📁 {category_data['description'].upper()}")
        print("-" * 40)
        
        for expr in category_data["expressions"]:
            print(f"\\n🔸 {expr['name']}")
            print(f"   Expresión: {expr['expression']}")
            print(f"   Rango: x ∈ [{expr['x_min']}, {expr['x_max']}]")
            print(f"   Descripción: {expr['description']}")
            
            # Comando curl para probar
            curl_command = f'''curl -X POST "{BASE_URL}/api/graphing/generate" \\
  -H "Content-Type: application/json" \\
  -d '{{"expression": "{expr['expression']}", "x_min": {expr['x_min']}, "x_max": {expr['x_max']}, "points": 1000, "variable": "x"}}\''''
            print(f"   💻 Test command:")
            print(f"   {curl_command}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        print_expressions_only()
    else:
        main()
