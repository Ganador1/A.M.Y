#!/usr/bin/env python3
"""
Pruebas avanzadas para gráficos complejos - Mathematics AI
Advanced tests for complex graphing capabilities
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

# Expresiones muy complicadas para probar
ADVANCED_EXPRESSIONS = {
    "parametric_surfaces_3d": [
        {
            "name": "Toro (Torus)",
            "x_expr": "(2 + cos(v)) * cos(u)",
            "y_expr": "(2 + cos(v)) * sin(u)",
            "z_expr": "sin(v)",
            "u_range": [0, 6.28],
            "v_range": [0, 6.28],
            "description": "Superficie toroidal clásica"
        },
        {
            "name": "Esfera paramétrica",
            "x_expr": "cos(u) * cos(v)",
            "y_expr": "cos(u) * sin(v)", 
            "z_expr": "sin(u)",
            "u_range": [-1.57, 1.57],
            "v_range": [0, 6.28],
            "description": "Esfera unitaria paramétrica"
        },
        {
            "name": "Superficie de Möbius",
            "x_expr": "(1 + 0.5*v*cos(u/2)) * cos(u)",
            "y_expr": "(1 + 0.5*v*cos(u/2)) * sin(u)",
            "z_expr": "0.5*v*sin(u/2)",
            "u_range": [0, 6.28],
            "v_range": [-1, 1],
            "description": "Banda de Möbius clásica"
        }
    ],
    
    "complex_2d_functions": [
        {
            "name": "Función con singularidades",
            "expression": "1/(sin(x) + cos(x))",
            "x_min": -10,
            "x_max": 10,
            "description": "Función con múltiples singularidades"
        },
        {
            "name": "Oscilaciones amortiguadas complejas",
            "expression": "exp(-x**2/10) * sin(x**2) * cos(3*x)",
            "x_min": -5,
            "x_max": 5,
            "description": "Producto de funciones oscilatorias con envolvente gaussiana"
        },
        {
            "name": "Función fractal simple",
            "expression": "sin(x) + sin(3*x)/3 + sin(5*x)/5 + sin(7*x)/7",
            "x_min": -6.28,
            "x_max": 6.28,
            "description": "Aproximación de onda cuadrada por serie de Fourier"
        },
        {
            "name": "Función con cúspides",
            "expression": "abs(x)**(2/3)",
            "x_min": -5,
            "x_max": 5,
            "description": "Función con cúspide en el origen"
        },
        {
            "name": "Función de Weierstrass aproximada",
            "expression": "cos(x) + cos(3*x)/4 + cos(9*x)/16 + cos(27*x)/64",
            "x_min": -3.14,
            "x_max": 3.14,
            "description": "Aproximación de función continua pero no derivable"
        }
    ],
    
    "mathematical_surfaces_3d": [
        {
            "name": "Paraboloide hiperbólico (Silla de montar)",
            "expression": "x**2 - y**2",
            "x_range": [-3, 3],
            "y_range": [-3, 3],
            "description": "Superficie silla de montar clásica"
        },
        {
            "name": "Función gaussiana 2D",
            "expression": "exp(-(x**2 + y**2))",
            "x_range": [-3, 3],
            "y_range": [-3, 3],
            "description": "Campana de Gauss bidimensional"
        },
        {
            "name": "Ondas interferentes",
            "expression": "sin(sqrt(x**2 + y**2)) / sqrt(x**2 + y**2 + 0.1)",
            "x_range": [-10, 10],
            "y_range": [-10, 10],
            "description": "Patrón de interferencia circular"
        },
        {
            "name": "Superficie de Monkey Saddle",
            "expression": "x**3 - 3*x*y**2",
            "x_range": [-2, 2],
            "y_range": [-2, 2],
            "description": "Superficie con tres direcciones de curvatura"
        }
    ]
}

def test_3d_parametric_surface(surface_data):
    """Test 3D parametric surface generation"""
    print(f"\n🎯 Testing 3D Parametric: {surface_data['name']}")
    print(f"📝 Description: {surface_data['description']}")
    
    try:
        request_data = {
            "x_expression": surface_data["x_expr"],
            "y_expression": surface_data["y_expr"],
            "z_expression": surface_data["z_expr"],
            "u_min": surface_data["u_range"][0],
            "u_max": surface_data["u_range"][1],
            "v_min": surface_data["v_range"][0],
            "v_max": surface_data["v_range"][1],
            "u_points": 50,
            "v_points": 50
        }
        
        response = requests.post(
            f"{BASE_URL}/api/graphing/generate-3d-parametric",
            json=request_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'Graph generated')}")
            if 'data' in result and 'image_path' in result['data']:
                print(f"📊 Graph saved to: {result['data']['image_path']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def test_3d_surface(surface_data):
    """Test 3D surface generation"""
    print(f"\n🎯 Testing 3D Surface: {surface_data['name']}")
    print(f"📝 Expression: {surface_data['expression']}")
    print(f"📖 Description: {surface_data['description']}")
    
    try:
        request_data = {
            "expression": surface_data["expression"],
            "x_min": surface_data["x_range"][0],
            "x_max": surface_data["x_range"][1],
            "y_min": surface_data["y_range"][0],
            "y_max": surface_data["y_range"][1],
            "x_points": 50,
            "y_points": 50
        }
        
        response = requests.post(
            f"{BASE_URL}/api/graphing/generate-3d-surface",
            json=request_data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'Graph generated')}")
            if 'data' in result and 'image_path' in result['data']:
                print(f"📊 Graph saved to: {result['data']['image_path']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def test_complex_2d_function(func_data):
    """Test complex 2D function generation"""
    print(f"\n🎯 Testing Complex 2D: {func_data['name']}")
    print(f"📝 Expression: {func_data['expression']}")
    print(f"📖 Description: {func_data['description']}")
    
    try:
        request_data = {
            "expression": func_data["expression"],
            "x_min": func_data["x_min"],
            "x_max": func_data["x_max"],
            "points": 2000,
            "variable": "x"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/graphing/generate",
            json=request_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success: {result.get('message', 'Graph generated')}")
            if 'data' in result and 'image_path' in result['data']:
                print(f"📊 Graph saved to: {result['data']['image_path']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

def main():
    """Main function to test advanced expressions"""
    print("🚀 Mathematics AI - Advanced Graph Testing")
    print("=" * 60)
    
    # Verificar servidor
    try:
        health_response = requests.get(f"{BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Server not responding")
            return
        print("✅ Server is running")
    except:
        print("❌ Cannot connect to server")
        return
    
    # Probar funciones 2D complejas
    print("\n📁 TESTING COMPLEX 2D FUNCTIONS")
    print("-" * 50)
    for func in ADVANCED_EXPRESSIONS["complex_2d_functions"]:
        test_complex_2d_function(func)
        time.sleep(1)  # Pausa entre pruebas
    
    # Probar superficies 3D
    print("\n📁 TESTING 3D SURFACES")
    print("-" * 50)
    for surface in ADVANCED_EXPRESSIONS["mathematical_surfaces_3d"]:
        test_3d_surface(surface)
        time.sleep(1)
    
    # Probar superficies paramétricas 3D
    print("\n📁 TESTING 3D PARAMETRIC SURFACES")
    print("-" * 50)
    for surface in ADVANCED_EXPRESSIONS["parametric_surfaces_3d"]:
        test_3d_parametric_surface(surface)
        time.sleep(1)
    
    print("\n🎉 Advanced graph testing completed!")

if __name__ == "__main__":
    main()
