# Mathematics - Servicios Disponibles

## Overview
Este documento describe los servicios del dominio Mathematics en AXIOM ATLAS y sus capacidades principales. Cubre computación simbólica, análisis numérico, topología, teoría de números, optimización, y más. Los servicios se exponen vía el router consolidado y sub-routers especializados.

## Servicios Principales

### AdvancedAlgebraService
- Descripción: Álgebra avanzada, factorización, descomposiciones, álgebra lineal simbólica.
- Endpoints: `/mathematics/execute/advanced_algebra/{operation}`

### AdvancedNumberTheoryService
- Descripción: Teoría de números (primalidad, factorización, funciones aritméticas).
- Endpoints: `/mathematics/execute/number_theory/{operation}`

### DifferentialEquationService
- Descripción: Resolución de ODE/PDE analítica y numérica.
- Endpoints: `/mathematics/execute/differential_equations/{operation}`

### OptimizationService
- Descripción: Optimización convexa/no convexa, LP/QP, heurísticos.
- Endpoints: `/mathematics/execute/optimization/{operation}`

### AdvancedSymPyService / SymEngineService
- Descripción: Computación simbólica (derivadas, integrales, simplificación).
- Endpoints: `/mathematics/execute/sympy/{operation}`, `/mathematics/execute/symengine/{operation}`

### SageMathService / JuliaService
- Descripción: Integración con SageMath y Julia para cálculos avanzados.
- Endpoints: `/mathematics/execute/sagemath/{operation}`, `/mathematics/execute/julia/{operation}`

### TopologyService / AdvancedTopologyService
- Descripción: Análisis topológico de datos, invariantes, grafos.
- Endpoints: `/mathematics/execute/topology/{operation}`

### QuantumMathService
- Descripción: Herramientas matemáticas para algoritmos cuánticos (QFT, estados, operadores).
- Endpoints: `/mathematics/execute/quantum/{operation}`

### StatisticsService
- Descripción: Estadística descriptiva/inferencial, tests, estimadores.
- Endpoints: `/mathematics/execute/statistics/{operation}`

### CombinatoricsService
- Descripción: Combinatoria, conteos, permutaciones, grafos.
- Endpoints: `/mathematics/execute/combinatorics/{operation}`

### CalculusService
- Descripción: Cálculo diferencial e integral (simbólico y numérico).
- Endpoints: `/mathematics/execute/calculus/{operation}`

### ArithmeticService
- Descripción: Operaciones aritméticas avanzadas y utilidades.
- Endpoints: `/mathematics/execute/arithmetic/{operation}`

### DistributedComputingService
- Descripción: Ejecución distribuida de tareas matemáticas.
- Endpoints: `/mathematics/execute/distributed/{operation}`

### MathMLService / MathNLP
- Descripción: ML aplicado a problemas matemáticos; NLP matemático.
- Endpoints: `/mathematics/execute/ml/{operation}`, `/mathematics/execute/math_nlp/{operation}`

### AutomatedTheoremProvingService
- Descripción: Prueba automática de teoremas y verificación.
- Endpoints: `/mathematics/execute/theorem_proving/{operation}`

### VisualizationService
- Descripción: Visualización y gráficos matemáticos.
- Endpoints: `/mathematics/execute/visualization/{operation}`

## Uso del Router Consolidado
- Lista de servicios: `GET /mathematics/services`
- Capacidades: `GET /mathematics/capabilities`
- Ejecutar operación: `POST /mathematics/execute/{service_name}/{operation}`
- Batch: `POST /mathematics/batch-execute`

Para ejemplos concretos, ver `EXAMPLES.md` y `API_GUIDE.md`.