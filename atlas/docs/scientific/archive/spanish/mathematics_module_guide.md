# Guía Completa del Módulo Matemático AXIOM

## 📋 Índice
1. [Introducción](#introducción)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Servicios Disponibles](#servicios-disponibles)
4. [Guías de Uso](#guías-de-uso)
5. [Ejemplos Prácticos](#ejemplos-prácticos)
6. [API Reference](#api-reference)
7. [Configuración y Dependencias](#configuración-y-dependencias)
8. [Troubleshooting](#troubleshooting)

## 🎯 Introducción

El módulo matemático de AXIOM es un sistema completo y modular que proporciona capacidades matemáticas avanzadas, desde operaciones básicas hasta computación cuántica y machine learning matemático.

### Características Principales
- **Modular**: Servicios independientes y especializados
- **Escalable**: Arquitectura distribuida con balanceador de carga
- **Completo**: Desde aritmética básica hasta IA matemática
- **Interactivo**: Visualizaciones y notebooks integrados
- **Robusto**: Manejo de errores y validación automática

## 🏗️ Arquitectura del Sistema

```
app/domains/mathematics/
├── models/           # Modelos de datos (requests/responses)
├── services/         # Lógica de negocio matemática
├── routers/          # Endpoints API REST
└── utils/           # Utilidades y helpers
```

### Gestor de Servicios
El `MathematicsServiceManager` actúa como orquestador central:
- Pool de conexiones optimizado
- Cache inteligente de resultados
- Balanceador de carga automático
- Monitoreo de rendimiento

## 🔧 Servicios Disponibles

### 1. Servicios Básicos

#### ArithmeticService
**Operaciones soportadas:**
- Básicas: `add`, `subtract`, `multiply`, `divide`
- Potencias: `power`, `sqrt`, `cbrt`, `nth_root`
- Trigonométricas: `sin`, `cos`, `tan`, `asin`, `acos`, `atan`
- Hiperbólicas: `sinh`, `cosh`, `tanh`, `asinh`, `acosh`, `atanh`
- Logaritmos: `log`, `log10`, `log2`, `ln`
- Otras: `abs`, `factorial`, `ceil`, `floor`, `round`

#### CalculusService
**Capacidades:**
- Derivadas ordinarias y parciales
- Integrales definidas e indefinidas
- Límites en puntos finitos e infinitos
- Series de Taylor y Fourier
- Operaciones multivariables

#### StatisticsService
**Funcionalidades:**
- Estadísticas descriptivas completas
- Análisis de correlación
- Regresión lineal
- Pruebas de hipótesis
- Análisis de distribuciones

### 2. Servicios Avanzados

#### QuantumMathematicsService
**Características:**
- Algoritmos cuánticos (Grover, Shor, QFT)
- Simulación de circuitos cuánticos
- Análisis de entrelazamiento
- Teleportación cuántica

#### MathematicalMLService
**Capacidades:**
- Redes neuronales matemáticas
- Optimización con ML
- Reconocimiento de patrones
- Modelos predictivos

#### MathVisualizationService
**Herramientas:**
- Gráficos interactivos 2D/3D
- Animaciones matemáticas
- Visualizaciones geométricas
- Campos vectoriales

### 3. Servicios Especializados

#### AdvancedMathAIService
- Razonamiento matemático avanzado
- Resolución de problemas complejos
- Generación de explicaciones
- Verificación de soluciones

#### OptimizationService
- Programación lineal y no lineal
- Algoritmos genéticos
- Optimización multiobjetivo
- Métodos estocásticos

## 📖 Guías de Uso

### Configuración Inicial

```python
from app.domains.mathematics.services import mathematics_service_manager

# Inicializar el gestor de servicios
await mathematics_service_manager.initialize()

# Verificar servicios disponibles
status = await mathematics_service_manager.get_service_status()
print(status)
```

### Uso Básico - Aritmética

```python
from app.domains.mathematics.models import ArithmeticRequest
from app.domains.mathematics.services import ArithmeticService

# Operación básica
request = ArithmeticRequest(
    operation="add",
    operands=[1, 2, 3, 4, 5]
)
result = ArithmeticService.calculate(request)
print(f"Resultado: {result.result}")  # 15.0

# Función trigonométrica
request = ArithmeticRequest(
    operation="sin",
    operands=[3.14159/2]
)
result = ArithmeticService.calculate(request)
print(f"sin(π/2) = {result.formatted_result}")  # 1.000000
```

### Uso Avanzado - Cálculo

```python
from app.domains.mathematics.models import CalculusRequest
from app.domains.mathematics.services import CalculusService

# Derivada
request = CalculusRequest(
    expression="x^3 + 2*x^2 + x + 1",
    operation="derivative",
    variable="x",
    order=1
)
result = CalculusService.calculate(request)
print(f"Derivada: {result.result}")

# Integral definida
request = CalculusRequest(
    expression="x^2",
    operation="integral",
    variable="x",
    limits=[0, 2]
)
result = CalculusService.calculate(request)
print(f"Integral: {result.result}")
```

### Uso Especializado - Machine Learning

```python
from app.domains.mathematics.services import MathematicalMLService

ml_service = MathematicalMLService()

# Aproximación de función con red neuronal
result = await ml_service.mathematical_function_approximation(
    function_data={"x": [1, 2, 3, 4], "y": [1, 4, 9, 16]},
    target_function="polynomial",
    parameters={"degree": 2}
)
print(f"Función aproximada: {result['approximated_function']}")
```

## 🎯 Ejemplos Prácticos

### Ejemplo 1: Análisis Completo de Función

```python
import asyncio
from app.domains.mathematics.services import (
    CalculusService, 
    MathVisualizationService,
    StatisticsService
)

async def analyze_function(expression="x^3 - 3*x^2 + 2*x"):
    # 1. Calcular derivada
    derivative_request = CalculusRequest(
        expression=expression,
        operation="derivative",
        variable="x"
    )
    derivative = CalculusService.calculate(derivative_request)
    
    # 2. Encontrar puntos críticos
    critical_points_request = CalculusRequest(
        expression=derivative.result,
        operation="solve",
        variable="x"
    )
    critical_points = CalculusService.calculate(critical_points_request)
    
    # 3. Generar visualización
    viz_service = MathVisualizationService()
    plot = await viz_service.plot_function_2d(
        expression=expression,
        x_range=[-2, 4],
        show_derivative=True,
        show_critical_points=True
    )
    
    return {
        "function": expression,
        "derivative": derivative.result,
        "critical_points": critical_points.result,
        "visualization": plot
    }

# Ejecutar análisis
result = asyncio.run(analyze_function())
```

### Ejemplo 2: Optimización Multiobjetivo

```python
from app.domains.mathematics.services import OptimizationService

opt_service = OptimizationService()

# Definir problema de optimización
problem = {
    "objectives": [
        "minimize x^2 + y^2",  # Minimizar distancia al origen
        "maximize x + y"       # Maximizar suma
    ],
    "constraints": [
        "x + y <= 10",
        "x >= 0",
        "y >= 0"
    ],
    "variables": {
        "x": {"type": "continuous", "bounds": [0, 10]},
        "y": {"type": "continuous", "bounds": [0, 10]}
    }
}

# Resolver con NSGA-II
result = opt_service.solve_multi_objective(
    problem=problem,
    method="nsga2",
    population_size=100,
    generations=50
)

print(f"Frente de Pareto: {result['pareto_front']}")
```

### Ejemplo 3: Análisis Estadístico Completo

```python
from app.domains.mathematics.services import StatisticsService
import numpy as np

# Generar datos de ejemplo
data = np.random.normal(100, 15, 1000).tolist()

# Análisis descriptivo
stats_request = StatisticsRequest(
    data=data,
    operation="comprehensive_analysis"
)
analysis = StatisticsService.calculate(stats_request)

print(f"Media: {analysis.result['mean']}")
print(f"Desviación estándar: {analysis.result['std']}")
print(f"Distribución: {analysis.result['distribution_test']}")
```

## 📚 API Reference

### Endpoints Principales

#### Aritmética
- `POST /api/arithmetic/calculate` - Operación aritmética
- `GET /api/arithmetic/operations` - Operaciones disponibles
- `POST /api/arithmetic/batch` - Operaciones por lotes
- `GET /api/arithmetic/examples` - Ejemplos de uso

#### Cálculo
- `POST /api/calculus/calculate` - Operación de cálculo
- `GET /api/calculus/operations` - Operaciones disponibles
- `POST /api/calculus/batch` - Cálculos por lotes

#### Estadística
- `POST /api/statistics/analyze` - Análisis estadístico
- `POST /api/statistics/correlation` - Análisis de correlación
- `POST /api/statistics/regression` - Regresión lineal

### Modelos de Datos

#### ArithmeticRequest
```python
{
    "operation": str,           # Operación a realizar
    "operands": List[float],    # Operandos numéricos
    "precision": int = 6,       # Precisión decimal
    "format": str = "decimal"   # Formato de salida
}
```

#### CalculusRequest
```python
{
    "expression": str,          # Expresión matemática
    "operation": str,           # Tipo de operación
    "variable": str = "x",      # Variable principal
    "order": int = 1,          # Orden (para derivadas)
    "limits": List[float] = None # Límites (para integrales)
}
```

## ⚙️ Configuración y Dependencias

### Dependencias Principales
```bash
# Matemáticas básicas
numpy>=1.21.0
scipy>=1.7.0
sympy>=1.9

# Machine Learning
tensorflow>=2.8.0  # Opcional
torch>=1.11.0      # Opcional
scikit-learn>=1.0.0

# Computación cuántica
qiskit>=0.34.0     # Opcional
cirq>=0.14.0       # Opcional

# Visualización
matplotlib>=3.5.0
plotly>=5.6.0
```

### Variables de Entorno
```bash
# Configuración de servicios
MATH_SERVICE_CACHE_SIZE=1000
MATH_SERVICE_TIMEOUT=30
MATH_PRECISION_DEFAULT=6

# Servicios opcionales
ENABLE_QUANTUM_MATH=true
ENABLE_ML_MATH=true
ENABLE_VISUALIZATION=true
```

### Configuración de Rendimiento
```python
# En service_manager.py
PERFORMANCE_CONFIG = {
    "cache_size": 1000,
    "connection_pool_size": 10,
    "timeout_seconds": 30,
    "max_concurrent_operations": 50
}
```

## 🔧 Troubleshooting

### Problemas Comunes

#### 1. Error de Importación de Dependencias
```python
# Verificar disponibilidad de librerías
from app.domains.mathematics.services import MathematicalMLService

ml_service = MathematicalMLService()
capabilities = ml_service.get_capabilities()
print(f"TensorFlow disponible: {capabilities['tensorflow_available']}")
```

#### 2. Timeout en Operaciones Complejas
```python
# Aumentar timeout para operaciones complejas
result = await mathematics_service_manager.execute_operation(
    service="quantum_math",
    operation="complex_algorithm",
    parameters=params,
    timeout=120  # 2 minutos
)
```

#### 3. Errores de Precisión Numérica
```python
# Usar mayor precisión para cálculos sensibles
request = ArithmeticRequest(
    operation="divide",
    operands=[1, 3],
    precision=15  # Mayor precisión
)
```

### Logs y Debugging
```python
import logging

# Habilitar logs detallados
logging.getLogger('mathematics').setLevel(logging.DEBUG)

# Verificar estado de servicios
status = await mathematics_service_manager.health_check()
for service, health in status.items():
    print(f"{service}: {health['status']}")
```

## 📈 Métricas y Monitoreo

### Métricas Disponibles
- Tiempo de respuesta por servicio
- Tasa de éxito/error
- Uso de memoria y CPU
- Cache hit ratio
- Operaciones por segundo

### Dashboard de Monitoreo
```python
# Obtener métricas en tiempo real
metrics = await mathematics_service_manager.get_metrics()
print(f"Operaciones totales: {metrics['total_operations']}")
print(f"Tiempo promedio: {metrics['avg_response_time']}ms")
```

---

## 📞 Soporte

Para soporte técnico o reportar bugs:
- Crear issue en el repositorio
- Consultar logs del sistema
- Verificar configuración de dependencias

**Versión:** 1.0.0  
**Última actualización:** Enero 2024