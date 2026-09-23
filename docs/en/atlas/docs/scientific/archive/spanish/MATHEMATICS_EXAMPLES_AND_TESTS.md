> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="-mathematics-domain---ejemplos-de-uso-y-casos-de-prueba"></a>
# 🧮 Mathematics Domain - Usage Examples and Test Cases

<a id="-índice"></a>
## 📋 **Table of Contents**
1. [Basic Examples](#ejemplos-básicos)
2. [Advanced Use Cases](#casos-de-uso-avanzados)
3. [Test Cases](#casos-de-prueba)
4. [Demo Scripts](#scripts-de-demostración)
5. [Troubleshooting](#troubleshooting)

<a id="-ejemplos-básicos"></a>
## 🔢 **Basic Examples**

<a id="1-computación-simbólica-con-sympy"></a>
### **1. Symbolic Computation with SymPy**

<a id="simplificar-expresión"></a>
#### Simplify Expression
```bash
curl -X POST "http://localhost:8000/api/mathematics/execute/sympy/simplify" \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "x^2 + 2*x + 1"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Operation simplify executed on sympy",
  "data": {
    "success": true,
    "operation": "simplify",
    "expression": "x^2 + 2*x + 1",
    "simplified": "(x + 1)^2",
    "processing_time": 0.1
  }
}
```

<a id="resolver-ecuación"></a>
#### Solve Equation
```bash
curl -X POST "http://localhost:8000/api/mathematics/execute/sympy/solve" \
  -H "Content-Type: application/json" \
  -d '{
    "equation": "x^2 - 5*x + 6",
    "variable": "x"
  }'
```

<a id="calcular-derivada"></a>
#### Calculate Derivative
```bash
curl -X POST "http://localhost:8000/api/mathematics/execute/sympy/differentiate" \
  -H "Content-Type: application/json" \
  -d '{
    "expression": "x^3 + 2*x^2 + x + 1",
    "variable": "x",
    "order": 1
  }'
```

<a id="2-análisis-numérico-con-julia"></a>
### **2. Numerical Analysis with Julia**

<a id="encontrar-raíces"></a>
#### Find Roots
```bash
curl -X POST "http://localhost:8000/api/mathematics/execute/julia/root_finding" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "x^2 - 2",
    "initial_guess": 1.0
  }'
```

<a id="integración-numérica"></a>
#### Numerical Integration
```bash
curl -X POST "http://localhost:8000/api/mathematics/execute/julia/integration" \
  -H "Content-Type: application/json" \
  -d '{
    "function": "x^2",
    "lower": 0,
    "upper": 1
  }'
```

<a id="3-álgebra-computacional-con-sagemath"></a>
### **3. Computational Algebra with SageMath**

<a id="teoría-de-números"></a>
#### Number Theory
```bash
curl -X POST "http://localhost:8000/api/mathematics/execute/sagemath/elliptic_curves" \
  -H "Content-Type: application/json" \
  -d '{
    "a": 1,
    "b": 1
  }'
```

<a id="geometría-algebraica"></a>
#### Algebraic Geometry
```bash
curl -X POST "http://localhost:8000/api/mathematics/execute/sagemath/varieties" \
  -H "Content-Type: application/json" \
  -d '{
    "equation": "x^2 + y^2 - 1"
  }'
```

<a id="-casos-de-uso-avanzados"></a>
## 🚀 **Advanced Use Cases**

<a id="1-motor-de-descubrimiento-matemático"></a>
### **1. Mathematical Discovery Engine**

<a id="generar-conjetura"></a>
#### Generate Conjecture
```bash
curl -X POST "http://localhost:8000/api/mathematics/discovery/generate-conjecture" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "number_theory",
    "method": "pattern_analysis",
    "parameters": {
      "pattern_type": "primes"
    }
  }'
```

<a id="investigar-conjetura"></a>
#### Investigate Conjecture
```bash
curl -X POST "http://localhost:8000/api/mathematics/discovery/investigate/conj_001_20241201_120000" \
  -H "Content-Type: application/json" \
  -d '{
    "investigation_method": "numerical_analysis",
    "parameters": {
      "range": "n=1 to 1000"
    }
  }'
```

<a id="2-análisis-topológico-de-datos"></a>
### **2. Topological Data Analysis**

<a id="homología-persistente"></a>
#### Persistent Homology
```bash
curl -X POST "http://localhost:8000/api/mathematics/topology/persistent-homology/vietoris_rips" \
  -H "Content-Type: application/json" \
  -d '{
    "points": [
      [0, 0], [1, 1], [2, 0], [1, 0], [0.5, 0.5]
    ],
    "max_dimension": 2,
    "max_edge_length": 1.5
  }'
```

<a id="algoritmo-mapper"></a>
#### Mapper Algorithm
```bash
curl -X POST "http://localhost:8000/api/mathematics/topology/mapper/mapper_analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      [0, 0], [1, 1], [2, 0], [1, 0], [0.5, 0.5]
    ],
    "resolution": 10,
    "gain": 0.5
  }'
```

<a id="3-computación-cuántica"></a>
### **3. Quantum Computing**

<a id="algoritmo-de-grover"></a>
#### Grover's Algorithm
```bash
curl -X POST "http://localhost:8000/api/mathematics/quantum/algorithms/grover_search" \
  -H "Content-Type: application/json" \
  -d '{
    "n_qubits": 3,
    "target_state": "110"
  }'
```

<a id="simulación-cuántica"></a>
#### Quantum Simulation
```bash
curl -X POST "http://localhost:8000/api/mathematics/quantum/simulation/state_vector" \
  -H "Content-Type: application/json" \
  -d '{
    "n_qubits": 2,
    "initial_state": "00"
  }'
```

<a id="4-machine-learning-matemático"></a>
### **4. Mathematical Machine Learning**

<a id="aproximación-de-funciones"></a>
#### Function Approximation
```bash
curl -X POST "http://localhost:8000/api/mathematics/ml/neural-networks/mathematical_function_approximation" \
  -H "Content-Type: application/json" \
  -d '{
    "function_type": "polynomial",
    "n_samples": 1000,
    "n_epochs": 100
  }'
```

<a id="optimización-matemática"></a>
#### Mathematical Optimization
```bash
curl -X POST "http://localhost:8000/api/mathematics/ml/optimization/gradient_descent" \
  -H "Content-Type: application/json" \
  -d '{
    "learning_rate": 0.01,
    "n_iterations": 1000,
    "function_type": "quadratic"
  }'
```

<a id="-casos-de-prueba"></a>
## 🧪 **Test Cases**

<a id="1-pruebas-de-integración"></a>
### **1. Integration Tests**

<a id="test-de-servicios-básicos"></a>
#### Basic Services Test
```python
import requests
import json

def test_basic_services():
    """Prueba servicios básicos del dominio mathematics"""
    base_url = "http://localhost:8000/api/mathematics"
    
    # Test 1: Estado del sistema
    response = requests.get(f"{base_url}/status")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "total_services" in data["data"]
    
    # Test 2: Capacidades
    response = requests.get(f"{base_url}/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "sympy" in data["data"]
    
    # Test 3: Operación básica
    response = requests.post(
        f"{base_url}/execute/sympy/simplify",
        json={"expression": "x^2 + 2*x + 1"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

if __name__ == "__main__":
    test_basic_services()
    print("✅ Todas las pruebas básicas pasaron")
```

<a id="test-de-rendimiento"></a>
#### Performance Test
```python
import time
import requests
import concurrent.futures

def test_performance():
    """Prueba de rendimiento con múltiples requests"""
    base_url = "http://localhost:8000/api/mathematics"
    
    def make_request():
        response = requests.post(
            f"{base_url}/execute/sympy/simplify",
            json={"expression": "x^2 + 2*x + 1"}
        )
        return response.status_code == 200
    
    # Test con 10 requests concurrentes
    start_time = time.time()
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [future.result() for future in futures]
    
    end_time = time.time()
    duration = end_time - start_time
    
    assert all(results), "Algunas requests fallaron"
    assert duration < 5.0, f"Demasiado lento: {duration}s"
    
    print(f"✅ Test de rendimiento pasó: {duration:.2f}s para 10 requests")

if __name__ == "__main__":
    test_performance()
```

<a id="2-pruebas-de-casos-edge"></a>
### **2. Edge Case Tests**

<a id="test-de-entrada-inválida"></a>
#### Invalid Input Test
```python
def test_invalid_input():
    """Prueba manejo de entrada inválida"""
    base_url = "http://localhost:8000/api/mathematics"
    
    # Test con expresión inválida
    response = requests.post(
        f"{base_url}/execute/sympy/simplify",
        json={"expression": "invalid_expression!!!"}
    )
    
    # Debe manejar el error gracefully
    assert response.status_code in [200, 400, 422]
    data = response.json()
    # Puede ser exitoso con error o fallar con error
    if data["success"]:
        assert "error" in data["data"]
    else:
        assert "error" in data

if __name__ == "__main__":
    test_invalid_input()
    print("✅ Test de entrada inválida pasó")
```

<a id="test-de-servicio-no-disponible"></a>
#### Service Unavailable Test
```python
def test_service_unavailable():
    """Prueba cuando un servicio no está disponible"""
    base_url = "http://localhost:8000/api/mathematics"
    
    # Test con servicio inexistente
    response = requests.post(
        f"{base_url}/execute/nonexistent_service/operation",
        json={"param": "value"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == False
    assert "no encontrado" in data["data"]["error"]

if __name__ == "__main__":
    test_service_unavailable()
    print("✅ Test de servicio no disponible pasó")
```

<a id="-scripts-de-demostración"></a>
## 📜 **Demo Scripts**

<a id="1-demo-completo-del-sistema"></a>
### **1. Full System Demo**

```python
#!/usr/bin/env python3
"""
Demo completo del dominio Mathematics
Muestra todas las capacidades principales del sistema
"""

import requests
import json
import time

class MathematicsDemo:
    def __init__(self, base_url="http://localhost:8000/api/mathematics"):
        self.base_url = base_url
        
    def demo_overview(self):
        """Demo de vista general"""
        print("🔍 Obteniendo vista general del dominio...")
        response = requests.get(f"{self.base_url}/")
        data = response.json()
        
        if data["success"]:
            info = data["data"]
            print(f"✅ Dominio: {info['domain']}")
            print(f"✅ Versión: {info['version']}")
            print(f"✅ Servicios: {len(info['services'])}")
            print(f"✅ Capacidades: {len(info['capabilities'])}")
        else:
            print(f"❌ Error: {data['message']}")
    
    def demo_status(self):
        """Demo de estado del sistema"""
        print("\n📊 Verificando estado del sistema...")
        response = requests.get(f"{self.base_url}/status")
        data = response.json()
        
        if data["success"]:
            status = data["data"]
            print(f"✅ Estado general: {status['manager_status']}")
            print(f"✅ Servicios totales: {status['total_services']}")
            print(f"✅ Servicios activos: {status['active_services']}")
            print(f"✅ Servicios con error: {status['error_services']}")
        else:
            print(f"❌ Error: {data['message']}")
    
    def demo_sympy(self):
        """Demo de SymPy"""
        print("\n🧮 Demo de SymPy - Computación Simbólica")
        
        # Simplificar expresión
        response = requests.post(
            f"{self.base_url}/execute/sympy/simplify",
            json={"expression": "x^2 + 2*x + 1"}
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Simplificar: {result['expression']} → {result['simplified']}")
        
        # Resolver ecuación
        response = requests.post(
            f"{self.base_url}/execute/sympy/solve",
            json={"equation": "x^2 - 5*x + 6", "variable": "x"}
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Resolver: {result['equation']} → {result['solutions']}")
    
    def demo_julia(self):
        """Demo de Julia"""
        print("\n🔢 Demo de Julia - Computación Numérica")
        
        # Encontrar raíces
        response = requests.post(
            f"{self.base_url}/execute/julia/root_finding",
            json={"function": "x^2 - 2", "initial_guess": 1.0}
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Raíz de x²-2: {result.get('root', 'calculado')}")
        
        # Integración
        response = requests.post(
            f"{self.base_url}/execute/julia/integration",
            json={"function": "x^2", "lower": 0, "upper": 1}
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Integral de x²: {result.get('integral', 'calculado')}")
    
    def demo_discovery(self):
        """Demo del motor de descubrimiento"""
        print("\n🔍 Demo del Motor de Descubrimiento")
        
        # Generar conjetura
        response = requests.post(
            f"{self.base_url}/discovery/generate-conjecture",
            json={
                "domain": "number_theory",
                "method": "pattern_analysis",
                "parameters": {"pattern_type": "primes"}
            }
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Conjetura generada: {result['conjecture']['statement']}")
            print(f"✅ Confianza: {result['conjecture']['confidence']}")
    
    def demo_topology(self):
        """Demo de topología"""
        print("\n🔺 Demo de Topología Avanzada")
        
        # Análisis de homología persistente
        response = requests.post(
            f"{self.base_url}/topology/persistent-homology/vietoris_rips",
            json={
                "points": [[0, 0], [1, 1], [2, 0], [1, 0]],
                "max_dimension": 2
            }
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Puntos analizados: {result['points_count']}")
            print(f"✅ Números de Betti: {result.get('betti_numbers', 'calculados')}")
    
    def demo_quantum(self):
        """Demo de computación cuántica"""
        print("\n⚛️ Demo de Computación Cuántica")
        
        # Algoritmo de Grover
        response = requests.post(
            f"{self.base_url}/quantum/algorithms/grover_search",
            json={"n_qubits": 3, "target_state": "110"}
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Grover con {result['n_qubits']} qubits")
            print(f"✅ Estado objetivo: {result['target_state']}")
    
    def demo_ml(self):
        """Demo de machine learning"""
        print("\n🤖 Demo de Machine Learning Matemático")
        
        # Aproximación de funciones
        response = requests.post(
            f"{self.base_url}/ml/neural-networks/mathematical_function_approximation",
            json={
                "function_type": "polynomial",
                "n_samples": 1000,
                "n_epochs": 100
            }
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Función: {result['function_type']}")
            print(f"✅ Muestras: {result['n_samples']}")
            print(f"✅ Épocas: {result['n_epochs']}")
    
    def demo_batch_operations(self):
        """Demo de operaciones en lote"""
        print("\n📦 Demo de Operaciones en Lote")
        
        operations = [
            {
                "service_name": "sympy",
                "operation": "simplify",
                "parameters": {"expression": "x^2 + 2*x + 1"}
            },
            {
                "service_name": "sympy",
                "operation": "differentiate",
                "parameters": {"expression": "x^3", "variable": "x"}
            },
            {
                "service_name": "julia",
                "operation": "root_finding",
                "parameters": {"function": "x^2 - 4", "initial_guess": 1.0}
            }
        ]
        
        response = requests.post(
            f"{self.base_url}/batch-execute",
            json={"operations": operations}
        )
        data = response.json()
        if data["success"]:
            result = data["data"]
            print(f"✅ Operaciones totales: {result['total_operations']}")
            print(f"✅ Exitosas: {result['successful_operations']}")
            print(f"✅ Fallidas: {result['failed_operations']}")
    
    def run_full_demo(self):
        """Ejecutar demo completo"""
        print("🚀 Iniciando Demo Completo del Dominio Mathematics")
        print("=" * 60)
        
        try:
            self.demo_overview()
            self.demo_status()
            self.demo_sympy()
            self.demo_julia()
            self.demo_discovery()
            self.demo_topology()
            self.demo_quantum()
            self.demo_ml()
            self.demo_batch_operations()
            
            print("\n" + "=" * 60)
            print("🎉 Demo completado exitosamente!")
            
        except Exception as e:
            print(f"\n❌ Error en demo: {e}")

if __name__ == "__main__":
    demo = MathematicsDemo()
    demo.run_full_demo()
```

<a id="2-script-de-monitoreo"></a>
### **2. Monitoring Script**

```python
#!/usr/bin/env python3
"""
Script de monitoreo del dominio Mathematics
Verifica el estado y rendimiento del sistema
"""

import requests
import time
import json
from datetime import datetime

class MathematicsMonitor:
    def __init__(self, base_url="http://localhost:8000/api/mathematics"):
        self.base_url = base_url
        
    def check_health(self):
        """Verificar salud del sistema"""
        try:
            response = requests.get(f"{self.base_url}/health")
            data = response.json()
            
            if data["success"]:
                health = data["data"]
                print(f"🏥 Estado general: {health['overall_status']}")
                print(f"⏰ Timestamp: {health['timestamp']}")
                
                for service, status in health["services_health"].items():
                    emoji = "✅" if status["status"] == "healthy" else "❌"
                    print(f"{emoji} {service}: {status['status']}")
                
                return health["overall_status"] == "healthy"
            else:
                print(f"❌ Error en health check: {data['message']}")
                return False
                
        except Exception as e:
            print(f"❌ Error conectando al sistema: {e}")
            return False
    
    def get_statistics(self):
        """Obtener estadísticas del sistema"""
        try:
            response = requests.get(f"{self.base_url}/statistics")
            data = response.json()
            
            if data["success"]:
                stats = data["data"]
                print(f"📊 Servicios totales: {stats['total_services']}")
                print(f"💾 Entradas en cache: {stats['cache_entries']}")
                print(f"🔄 Operaciones totales: {stats['total_operations']}")
                
                print("\n📈 Rendimiento promedio por servicio:")
                for service, avg_time in stats["average_performance"].items():
                    print(f"  {service}: {avg_time:.3f}s")
                
                return stats
            else:
                print(f"❌ Error obteniendo estadísticas: {data['message']}")
                return None
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def monitor_continuously(self, interval=30):
        """Monitoreo continuo"""
        print(f"🔄 Iniciando monitoreo continuo (intervalo: {interval}s)")
        print("Presiona Ctrl+C para detener")
        
        try:
            while True:
                print(f"\n{'='*50}")
                print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                # Health check
                is_healthy = self.check_health()
                
                # Estadísticas
                stats = self.get_statistics()
                
                if not is_healthy:
                    print("⚠️ Sistema no saludable - considerando acciones correctivas")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoreo detenido por usuario")

if __name__ == "__main__":
    monitor = MathematicsMonitor()
    
    # Verificación única
    print("🔍 Verificación inicial del sistema...")
    is_healthy = monitor.check_health()
    
    if is_healthy:
        print("\n📊 Obteniendo estadísticas...")
        monitor.get_statistics()
        
        # Preguntar si continuar con monitoreo
        response = input("\n¿Iniciar monitoreo continuo? (y/n): ")
        if response.lower() == 'y':
            monitor.monitor_continuously()
    else:
        print("❌ Sistema no está saludable - revisar configuración")
```

<a id="-troubleshooting"></a>
## 🔧 **Troubleshooting**

<a id="problemas-comunes"></a>
### **Common Problems**

<a id="1-servicio-no-responde"></a>
#### 1. **Service not responding**
```bash
<a id="verificar-estado"></a>
# Verificar estado
curl -X GET "http://localhost:8000/api/mathematics/status"

<a id="verificar-salud"></a>
# Verificar salud
curl -X GET "http://localhost:8000/api/mathematics/health"

<a id="reiniciar-servicio-específico"></a>
# Reiniciar servicio específico
curl -X POST "http://localhost:8000/api/mathematics/services/sympy/restart"
```

<a id="2-error-de-dependencias"></a>
#### 2. **Dependency error**
```bash
<a id="verificar-capacidades"></a>
# Verificar capacidades
curl -X GET "http://localhost:8000/api/mathematics/capabilities/sympy"

<a id="el-sistema-funciona-en-modo-simulación-si-las-librerías-no-están-disponibles"></a>
# El sistema funciona en modo simulación si las librerías no están disponibles
```

<a id="3-problemas-de-rendimiento"></a>
#### 3. **Performance problems**
```bash
<a id="limpiar-cache"></a>
# Limpiar cache
curl -X POST "http://localhost:8000/api/mathematics/cache/clear"

<a id="optimizar-sistema"></a>
# Optimizar sistema
curl -X POST "http://localhost:8000/api/mathematics/optimize"

<a id="ver-estadísticas"></a>
# Ver estadísticas
curl -X GET "http://localhost:8000/api/mathematics/statistics"
```

<a id="4-errores-de-validación"></a>
#### 4. **Validation errors**
```bash
<a id="verificar-formato-de-entrada"></a>
# Verificar formato de entrada
curl -X POST "http://localhost:8000/api/mathematics/execute/sympy/simplify" \
  -H "Content-Type: application/json" \
  -d '{"expression": "x^2 + 2*x + 1"}'
```

<a id="logs-y-debugging"></a>
### **Logs and Debugging**

<a id="habilitar-logs-detallados"></a>
#### Enable detailed logs
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

<a id="verificar-logs-del-sistema"></a>
#### Check system logs
```bash
<a id="en-modo-desarrollo-los-logs-aparecen-en-consola"></a>
# En modo desarrollo, los logs aparecen en consola
<a id="en-producción-revisar-archivos-de-log-del-servidor"></a>
# En producción, revisar archivos de log del servidor
```

---

*Examples and test cases for AXIOM Mathematics Domain v2.0.0*
