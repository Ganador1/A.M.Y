#!/usr/bin/env python3
"""
Advanced PDE Examples for AXIOM
Demostración de capacidades avanzadas de resolución de EDP
"""

import requests
import json
from typing import Dict, Any


class PDEAdvancedExamples:
    """Ejemplos avanzados de resolución de EDP"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url

    def solve_heat_equation_example(self) -> Dict[str, Any]:
        """Resolver ecuación de calor 1D con condiciones iniciales complejas"""
        print("🔥 Resolviendo ecuación de calor 1D...")

        params = {
            "L": 2.0, "T": 1.0, "alpha": 0.1, "nx": 100, "nt": 500,
            "initial_condition": "np.exp(-10*(x-1)**2)",
            "boundary_conditions": {"left": "0", "right": "0"}
        }

        try:
            response = requests.post(f"{self.base_url}/api/pde/heat-equation", json={
                "L": 2.0, "T": 1.0, "alpha": 0.1, "nx": 100, "nt": 500,
                "initial_condition": "np.exp(-10*(x-1)**2)",
                "boundary_left": "0",
                "boundary_right": "0"
            })
            if response.status_code == 200:
                result = response.json()
                print("✅ Ecuación de calor resuelta exitosamente")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return {}

    def solve_wave_equation_example(self) -> Dict[str, Any]:
        """Resolver ecuación de onda con condiciones iniciales de onda cuadrada"""
        print("\n🌊 Resolviendo ecuación de onda 1D...")

        params = {
            "L": 2.0, "T": 3.0, "c": 1.0, "nx": 100, "nt": 600,
            "initial_displacement": "np.where((x > 0.4) & (x < 0.6), 1, 0)",
            "initial_velocity": "0"
        }

        try:
            response = requests.post(f"{self.base_url}/api/pde/wave-equation", json={
                "L": 2.0, "T": 3.0, "c": 1.0, "nx": 100, "nt": 600,
                "initial_displacement": "np.where((x > 0.4) & (x < 0.6), 1, 0)",
                "initial_velocity": "0"
            })
            if response.status_code == 200:
                result = response.json()
                print("✅ Ecuación de onda resuelta exitosamente")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return {}

    def solve_laplace_equation_example(self) -> Dict[str, Any]:
        """Resolver ecuación de Laplace 2D con condiciones de contorno complejas"""
        print("\n🎯 Resolviendo ecuación de Laplace 2D...")

        params = {
            "nx": 80, "ny": 80,
            "boundary_conditions": {
                "top": "np.sin(2*np.pi*x) * np.exp(-x)",
                "bottom": "0.5 * np.cos(np.pi*x)",
                "left": "x * (1-x)",
                "right": "0.2 * np.sin(3*np.pi*x)"
            }
        }

        try:
            response = requests.post(f"{self.base_url}/api/pde/laplace-equation", json={
                "nx": 80, "ny": 80,
                "boundary_top": "np.sin(2*np.pi*x) * np.exp(-x)",
                "boundary_bottom": "0.5 * np.cos(np.pi*x)",
                "boundary_left": "x * (1-x)",
                "boundary_right": "0.2 * np.sin(3*np.pi*x)"
            })
            if response.status_code == 200:
                result = response.json()
                print("✅ Ecuación de Laplace resuelta exitosamente")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return {}

    def analyze_pde_example(self) -> Dict[str, Any]:
        """Analizar propiedades de una EDP"""
        print("\n🔍 Analizando propiedades de EDP...")

        equations = [
            "diff(u(x,t), t) - 0.01*diff(u(x,t), x, 2)",
            "diff(u(x,t), t, 2) - diff(u(x,t), x, 2)",
            "diff(u(x,y), x, 2) + diff(u(x,y), y, 2)",
            "diff(u(x,t), t) + u(x,t)*diff(u(x,t), x)"
        ]

        results = {}
        for i, equation in enumerate(equations):
            try:
                response = requests.post(f"{self.base_url}/api/pde/analyze-pde",
                                       json={"equation": equation})
                if response.status_code == 200:
                    result = response.json()
                    results[f"equation_{i+1}"] = result
                    print(f"✅ Ecuación {i+1} analizada")
                else:
                    print(f"❌ Error analizando ecuación {i+1}: {response.status_code}")
            except Exception as e:
                print(f"❌ Error de conexión en ecuación {i+1}: {str(e)}")

        return results

    def get_pde_info_example(self) -> Dict[str, Any]:
        """Obtener información sobre EDP soportadas"""
        print("\n📚 Obteniendo información sobre EDP soportadas...")

        try:
            response = requests.get(f"{self.base_url}/api/pde/info")
            if response.status_code == 200:
                result = response.json()
                print("✅ Información de EDP obtenida exitosamente")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                return {}
        except Exception as e:
            print(f"❌ Error de conexión: {str(e)}")
            return {}

    def run_all_examples(self):
        """Ejecutar todos los ejemplos avanzados"""
        print("🚀 Iniciando demostración de capacidades avanzadas de EDP en AXIOM")
        print("=" * 70)

        # Obtener información general
        self.get_pde_info_example()

        # Analizar ecuaciones
        self.analyze_pde_example()

        # Resolver problemas específicos
        heat_result = self.solve_heat_equation_example()
        wave_result = self.solve_wave_equation_example()
        laplace_result = self.solve_laplace_equation_example()

        print("\n" + "=" * 70)
        print("✅ Demostración completada exitosamente!")
        print("🔬 AXIOM puede resolver ecuaciones diferenciales parciales complejas")
        print("📊 Incluyendo visualizaciones y análisis detallado de convergencia")
        print("🎯 Preparado para integrarse con FEniCS, FiPy y otras librerías avanzadas")

        return {
            "heat_equation": heat_result,
            "wave_equation": wave_result,
            "laplace_equation": laplace_result
        }


def run_demo():
    """Función principal para ejecutar los ejemplos"""
    print("🧮 AXIOM - Demostración Avanzada de EDP")
    print("Resolver ecuaciones diferenciales parciales con métodos numéricos")

    # Crear instancia de ejemplos
    examples = PDEAdvancedExamples()

    # Verificar que el servidor esté ejecutándose
    try:
        response = requests.get("http://localhost:8002/health")
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
    run_demo()
