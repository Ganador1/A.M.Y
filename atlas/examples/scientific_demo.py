#!/usr/bin/env python3
"""
Demostración completa de las nuevas capacidades científicas de AXIOM
Integra química computacional, física cuántica, computación cuántica e IA científica
"""

import requests
import json
import time
from typing import Dict, Any


class AXIOMScientificDemo:
    """Demostración completa de capacidades científicas avanzadas"""

    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url

    def demonstrate_computational_chemistry(self) -> Dict[str, Any]:
        """Demostrar capacidades de química computacional"""
        print("🧪 Probando química computacional...")

        results = {}

        # Analizar molécula
        try:
            response = requests.post(f"{self.base_url}/api/chemistry/analyze-molecule?smiles=CCO")
            if response.status_code == 200:
                results["molecule_analysis"] = response.json()
                print("✅ Análisis molecular completado")
            else:
                print(f"❌ Error en análisis molecular: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando química: {str(e)}")

        # Generar conformeros
        try:
            response = requests.post(f"{self.base_url}/api/chemistry/generate-conformers?smiles=CCO&num_conformers=5")
            if response.status_code == 200:
                results["conformer_generation"] = response.json()
                print("✅ Generación de conformeros completada")
            else:
                print(f"❌ Error en conformeros: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando conformeros: {str(e)}")

        # Analizar secuencia
        try:
            response = requests.post(f"{self.base_url}/api/chemistry/analyze-sequence?sequence=ATCGATCG&sequence_type=dna")
            if response.status_code == 200:
                results["sequence_analysis"] = response.json()
                print("✅ Análisis de secuencia completado")
            else:
                print(f"❌ Error en secuencia: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando secuencia: {str(e)}")

        return results

    def demonstrate_quantum_physics(self) -> Dict[str, Any]:
        """Demostrar capacidades de física cuántica"""
        print("\n🔬 Probando física cuántica...")

        results = {}

        # Evolución de espín
        try:
            response = requests.post(f"{self.base_url}/api/quantum-physics/spin-evolution?Bx=1.0&By=0.0&Bz=1.0&t_max=5.0&n_points=50")
            if response.status_code == 200:
                results["spin_evolution"] = response.json()
                print("✅ Evolución de espín completada")
            else:
                print(f"❌ Error en evolución de espín: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando espín: {str(e)}")

        # Oscilador armónico
        try:
            response = requests.post(f"{self.base_url}/api/quantum-physics/harmonic-oscillator?omega=1.0&n_max=8&alpha=1.5&t_max=10.0&n_points=100")
            if response.status_code == 200:
                results["harmonic_oscillator"] = response.json()
                print("✅ Oscilador armónico completado")
            else:
                print(f"❌ Error en oscilador: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando oscilador: {str(e)}")

        # Análisis de entrelazamiento
        try:
            response = requests.post(f"{self.base_url}/api/quantum-physics/entanglement-analysis?state_type=bell")
            if response.status_code == 200:
                results["entanglement"] = response.json()
                print("✅ Análisis de entrelazamiento completado")
            else:
                print(f"❌ Error en entrelazamiento: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando entrelazamiento: {str(e)}")

        return results

    def demonstrate_quantum_computing(self) -> Dict[str, Any]:
        """Demostrar capacidades de computación cuántica"""
        print("\n⚛️ Probando computación cuántica...")

        results = {}

        # Estado de Bell
        try:
            response = requests.post(f"{self.base_url}/api/quantum-computing/bell-state?framework=qiskit")
            if response.status_code == 200:
                results["bell_state"] = response.json()
                print("✅ Estado de Bell completado")
            else:
                print(f"❌ Error en Bell: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando Bell: {str(e)}")

        # Búsqueda de Grover
        try:
            response = requests.post(f"{self.base_url}/api/quantum-computing/grover-search?n_qubits=3&target_state=101")
            if response.status_code == 200:
                results["grover_search"] = response.json()
                print("✅ Búsqueda de Grover completada")
            else:
                print(f"❌ Error en Grover: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando Grover: {str(e)}")

        # Transformada de Fourier Cuántica
        try:
            response = requests.post(f"{self.base_url}/api/quantum-computing/quantum-fourier-transform?n_qubits=3")
            if response.status_code == 200:
                results["qft"] = response.json()
                print("✅ Transformada de Fourier completada")
            else:
                print(f"❌ Error en QFT: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando QFT: {str(e)}")

        return results

    def demonstrate_scientific_ai(self) -> Dict[str, Any]:
        """Demostrar capacidades de IA científica"""
        print("\n🤖 Probando IA científica...")

        results = {}

        # Resolver EDP con PINN
        try:
            response = requests.post(f"{self.base_url}/api/scientific-ai/solve-pde-pinn?pde_type=heat&epochs=500")
            if response.status_code == 200:
                results["pinn_pde"] = response.json()
                print("✅ EDP con PINN completada")
            else:
                print(f"❌ Error en PINN: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando PINN: {str(e)}")

        # Flujo de razonamiento científico
        try:
            response = requests.post(f"{self.base_url}/api/scientific-ai/scientific-reasoning?problem=Determinar%20la%20conductividad%20térmica%20de%20un%20material")
            if response.status_code == 200:
                results["scientific_reasoning"] = response.json()
                print("✅ Razonamiento científico completado")
            else:
                print(f"❌ Error en razonamiento: {response.status_code}")
        except Exception as e:
            print(f"❌ Error conectando razonamiento: {str(e)}")

        return results

    def get_service_status(self) -> Dict[str, Any]:
        """Obtener estado de todos los servicios"""
        print("\n📊 Verificando estado de servicios...")

        services = {
            "chemistry": "/api/chemistry/info",
            "quantum_physics": "/api/quantum-physics/info",
            "quantum_computing": "/api/quantum-computing/info",
            "scientific_ai": "/api/scientific-ai/info"
        }

        status = {}

        for service_name, endpoint in services.items():
            try:
                response = requests.get(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    status[service_name] = {
                        "status": "available",
                        "libraries": data.get("data", {})
                    }
                    print(f"✅ {service_name}: Disponible")
                else:
                    status[service_name] = {"status": "error", "code": response.status_code}
                    print(f"❌ {service_name}: Error {response.status_code}")
            except Exception as e:
                status[service_name] = {"status": "unavailable", "error": str(e)}
                print(f"❌ {service_name}: No disponible - {str(e)}")

        return status

    def run_complete_demo(self) -> Dict[str, Any]:
        """Ejecutar demostración completa"""
        print("🚀 AXIOM - Demostración de Capacidades Científicas Avanzadas")
        print("=" * 70)

        # Verificar estado de servicios
        service_status = self.get_service_status()

        # Ejecutar demostraciones
        chemistry_results = self.demonstrate_computational_chemistry()
        quantum_physics_results = self.demonstrate_quantum_physics()
        quantum_computing_results = self.demonstrate_quantum_computing()
        scientific_ai_results = self.demonstrate_scientific_ai()

        print("\n" + "=" * 70)
        print("✅ DEMOSTRACIÓN COMPLETADA")
        print("🔬 AXIOM ahora incluye capacidades avanzadas de:")
        print("   • 🧪 Química Computacional (RDKit, Biopython, PySCF)")
        print("   • ⚛️ Física Cuántica (QuTiP)")
        print("   • 🧮 Computación Cuántica (Qiskit, Cirq)")
        print("   • 🤖 IA Científica (DeepXDE, LangChain)")
        print("🎯 Preparado para investigación científica de vanguardia")

        return {
            "service_status": service_status,
            "chemistry": chemistry_results,
            "quantum_physics": quantum_physics_results,
            "quantum_computing": quantum_computing_results,
            "scientific_ai": scientific_ai_results,
            "timestamp": time.time(),
            "version": "AXIOM v2.0 - Scientific Computing"
        }


def main():
    """Función principal"""
    demo = AXIOMScientificDemo()

    # Verificar que el servidor esté funcionando
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code != 200:
            print("❌ Servidor AXIOM no está funcionando")
            print("💡 Inicia el servidor con: python main.py")
            return
    except:
        print("❌ No se puede conectar al servidor AXIOM")
        print("💡 Asegúrate de que esté ejecutándose en http://localhost:8002")
        return

    # Ejecutar demostración
    results = demo.run_complete_demo()

    # Guardar resultados
    with open("axiom_scientific_demo_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    print("💾 Resultados guardados en 'axiom_scientific_demo_results.json'")


if __name__ == "__main__":
    main()
