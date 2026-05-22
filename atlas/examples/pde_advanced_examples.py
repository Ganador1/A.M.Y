#!/usr/bin/env python3
"""
Advanced PDE Examples for AXIOM
Demostración de capacidades avanzadas de resolución de EDP
"""

import requests
import json
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, Any


class PDEAdvancedExamples:
    """Ejemplos avanzados de resolución de EDP"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def solve_heat_equation_example(self) -> Dict[str, Any]:
        """
        Resolver ecuación de calor 1D con condiciones iniciales complejas
        """
        print("🔥 Resolviendo ecuación de calor 1D...")

        # Parámetros del problema
        params = {
            "L": 2.0,  # Longitud del dominio
            "T": 1.0,  # Tiempo total
            "alpha": 0.1,  # Difusividad térmica
            "nx": 100,  # Puntos espaciales
            "nt": 500,  # Pasos temporales
            "initial_condition": "np.exp(-10*(x-1)**2)",  # Gaussiana centrada
            "boundary_conditions": {
                "left": "0",
                "right": "0"
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/pde/solve/heat-1d",
                json=params
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ Ecuación de calor resuelta exitosamente")
                print(f"📊 Parámetros: L={params['L']}, T={params['T']}, α={params['alpha']}")
                print(f"🔢 Resolución: {params['nx']}x{params['nt']} puntos")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return None

    def solve_wave_equation_example(self) -> Dict[str, Any]:
        """
        Resolver ecuación de onda con condiciones iniciales de onda cuadrada
        """
        print("\n🌊 Resolviendo ecuación de onda 1D...")

        # Parámetros del problema
        params = {
            "L": 2.0,  # Longitud del dominio
            "T": 3.0,  # Tiempo total
            "c": 1.0,  # Velocidad de la onda
            "nx": 100,  # Puntos espaciales
            "nt": 600,  # Pasos temporales
            "initial_displacement": "np.where((x > 0.4) & (x < 0.6), 1, 0)",  # Onda cuadrada
            "initial_velocity": "0"
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/pde/solve/wave-1d",
                json=params
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ Ecuación de onda resuelta exitosamente")
                print(f"📊 Parámetros: L={params['L']}, T={params['T']}, c={params['c']}")
                print(f"🔢 Resolución: {params['nx']}x{params['nt']} puntos")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return None

    def solve_laplace_equation_example(self) -> Dict[str, Any]:
        """
        Resolver ecuación de Laplace 2D con condiciones de contorno complejas
        """
        print("\n🎯 Resolviendo ecuación de Laplace 2D...")

        # Parámetros del problema
        params = {
            "nx": 80,  # Puntos en x
            "ny": 80,  # Puntos en y
            "boundary_conditions": {
                "top": "np.sin(2*np.pi*x) * np.exp(-x)",     # Función exponencial senoidal
                "bottom": "0.5 * np.cos(np.pi*x)",           # Coseno
                "left": "x * (1-x)",                         # Parábola
                "right": "0.2 * np.sin(3*np.pi*x)"           # Seno de frecuencia triple
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/pde/solve/laplace-2d",
                json=params
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ Ecuación de Laplace resuelta exitosamente")
                print(f"📊 Resolución: {params['nx']}x{params['ny']} puntos")
                print("🔢 Condiciones de contorno aplicadas en todos los bordes")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return None

    def analyze_pde_example(self) -> Dict[str, Any]:
        """
        Analizar propiedades de una EDP
        """
        print("\n🔍 Analizando propiedades de EDP...")

        # Ejemplos de ecuaciones para analizar
        equations = [
            "diff(u(x,t), t) - 0.01*diff(u(x,t), x, 2)",  # Ecuación de calor
            "diff(u(x,t), t, 2) - diff(u(x,t), x, 2)",     # Ecuación de onda
            "diff(u(x,y), x, 2) + diff(u(x,y), y, 2)",     # Ecuación de Laplace
            "diff(u(x,t), t) + u(x,t)*diff(u(x,t), x)"     # Ecuación de Burgers (no lineal)
        ]

        results = {}
        for i, equation in enumerate(equations):
            try:
                response = requests.post(
                    f"{self.base_url}/api/pde/analyze",
                    json={"equation": equation}
                )

                if response.status_code == 200:
                    result = response.json()
                    results[f"equation_{i+1}"] = result
                    print(f"✅ Ecuación {i+1} analizada: {result['analysis']['classification']}")
                else:
                    print(f"❌ Error analizando ecuación {i+1}: {response.status_code}")

            except Exception as e:
                print(f"❌ Error de conexión en ecuación {i+1}: {str(e)}")

        return results

    def get_pde_info_example(self) -> Dict[str, Any]:
        """
        Obtener información sobre EDP soportadas
        """
        print("\n📚 Obteniendo información sobre EDP soportadas...")

        try:
            response = requests.get(f"{self.base_url}/api/pde/info")

            if response.status_code == 200:
                result = response.json()
                print("✅ Información de EDP obtenida exitosamente")
                print("🔧 Métodos numéricos disponibles:")
                for method in result['info']['numerical_methods']:
                    print(f"   • {method}")
                print("📐 EDP implementadas:")
                for pde_name in result['info']['supported_pdes'].keys():
                    print(f"   • {pde_name.replace('_', ' ').title()}")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return None

        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return {}


def main():
    """Función principal para ejecutar los ejemplos"""
    print("🧮 AXIOM - Demostración Avanzada de EDP")
    print("Resolver ecuaciones diferenciales parciales con métodos numéricos")

    # Crear instancia de ejemplos
    examples = PDEAdvancedExamples()

    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Servidor AXIOM detectado y funcionando")
        else:
            print("⚠️  Servidor AXIOM no responde correctamente")
            return
    except:
        print("❌ No se puede conectar al servidor AXIOM")
        print("� Asegúrate de que el servidor esté ejecutándose con: python main.py")
        return

    # Ejecutar ejemplos
    results = examples.run_all_examples()

    # Guardar resultados si es necesario
    if results:
        with open("pde_advanced_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("💾 Resultados guardados en 'pde_advanced_results.json'")


if __name__ == "__main__":
    main()


def main():
    """Función principal para ejecutar los ejemplos"""
    print("🧮 AXIOM - Demostración Avanzada de EDP")
    print("Resolver ecuaciones diferenciales parciales con métodos numéricos")

    # Crear instancia de ejemplos
    examples = PDEAdvancedExamples()

    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ Servidor AXIOM detectado y funcionando")
        else:
            print("⚠️  Servidor AXIOM no responde correctamente")
            return
    except:
        print("❌ No se puede conectar al servidor AXIOM")
        print("💡 Asegúrate de que el servidor esté ejecutándose con: python main.py")
        return

    # Ejecutar ejemplos
    results = examples.run_all_examples()

    # Guardar resultados si es necesario
    if results:
        with open("pde_advanced_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("💾 Resultados guardados en 'pde_advanced_results.json'")


if __name__ == "__main__":
    main()</content>
<parameter name="filePath">./pde_advanced_examples.py
