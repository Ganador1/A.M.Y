> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="mathematics---servicios-disponibles"></a>
# Mathematics - Available Services

<a id="overview"></a>
## Overview
This document describes the services of the Mathematics domain in AXIOM ATLAS and their main capabilities. It covers symbolic computation, numerical analysis, topology, number theory, optimization, and more. The services are exposed via the consolidated router and specialized sub-routers.

<a id="servicios-principales"></a>
## Main Services

<a id="advancedalgebraservice"></a>
### AdvancedAlgebraService
- Description: Advanced algebra, factorization, decompositions, symbolic linear algebra.
- Endpoints: `/mathematics/execute/advanced_algebra/{operation}`

<a id="advancednumbertheoryservice"></a>
### AdvancedNumberTheoryService
- Description: Number theory (primality, factorization, arithmetic functions).
- Endpoints: `/mathematics/execute/number_theory/{operation}`

<a id="differentialequationservice"></a>
### DifferentialEquationService
- Description: Analytical and numerical solving of ODEs/PDEs.
- Endpoints: `/mathematics/execute/differential_equations/{operation}`

<a id="optimizationservice"></a>
### OptimizationService
- Description: Convex/non-convex optimization, LP/QP, heuristics.
- Endpoints: `/mathematics/execute/optimization/{operation}`

<a id="advancedsympyservice--symengineservice"></a>
### AdvancedSymPyService / SymEngineService
- Description: Symbolic computation (derivatives, integrals, simplification).
- Endpoints: `/mathematics/execute/sympy/{operation}`, `/mathematics/execute/symengine/{operation}`

<a id="sagemathservice--juliaservice"></a>
### SageMathService / JuliaService
- Description: Integration with SageMath and Julia for advanced calculations.
- Endpoints: `/mathematics/execute/sagemath/{operation}`, `/mathematics/execute/julia/{operation}`

<a id="topologyservice--advancedtopologyservice"></a>
### TopologyService / AdvancedTopologyService
- Description: Topological data analysis, invariants, graphs.
- Endpoints: `/mathematics/execute/topology/{operation}`

<a id="quantummathservice"></a>
### QuantumMathService
- Description: Mathematical tools for quantum algorithms (QFT, states, operators).
- Endpoints: `/mathematics/execute/quantum/{operation}`

<a id="statisticsservice"></a>
### StatisticsService
- Description: Descriptive/inferential statistics, tests, estimators.
- Endpoints: `/mathematics/execute/statistics/{operation}`

<a id="combinatoricsservice"></a>
### CombinatoricsService
- Description: Combinatorics, counting, permutations, graphs.
- Endpoints: `/mathematics/execute/combinatorics/{operation}`

<a id="calculusservice"></a>
### CalculusService
- Description: Differential and integral calculus (symbolic and numerical).
- Endpoints: `/mathematics/execute/calculus/{operation}`

<a id="arithmeticservice"></a>
### ArithmeticService
- Description: Advanced arithmetic operations and utilities.
- Endpoints: `/mathematics/execute/arithmetic/{operation}`

<a id="distributedcomputingservice"></a>
### DistributedComputingService
- Description: Distributed execution of mathematical tasks.
- Endpoints: `/mathematics/execute/distributed/{operation}`

<a id="mathmlservice--mathnlp"></a>
### MathMLService / MathNLP
- Description: ML applied to mathematical problems; mathematical NLP.
- Endpoints: `/mathematics/execute/ml/{operation}`, `/mathematics/execute/math_nlp/{operation}`

<a id="automatedtheoremprovingservice"></a>
### AutomatedTheoremProvingService
- Description: Automated theorem proving and verification.
- Endpoints: `/mathematics/execute/theorem_proving/{operation}`

<a id="visualizationservice"></a>
### VisualizationService
- Description: Visualization and mathematical graphics.
- Endpoints: `/mathematics/execute/visualization/{operation}`

<a id="uso-del-router-consolidado"></a>
## Use of the Consolidated Router
- List of services: `GET /mathematics/services`
- Capabilities: `GET /mathematics/capabilities`
- Execute operation: `POST /mathematics/execute/{service_name}/{operation}`
- Batch: `POST /mathematics/batch-execute`

For concrete examples, see `EXAMPLES.md` and `API_GUIDE.md`.
