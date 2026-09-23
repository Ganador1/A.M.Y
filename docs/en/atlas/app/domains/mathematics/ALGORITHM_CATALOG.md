> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="catálogo-de-algoritmos-en-el-dominio-de-mathematics"></a>
# Algorithm Catalog in the Mathematics Domain

This catalog details the algorithms and mathematical tools available in AXIOM, organized by subcategory. Each entry includes a brief description, use cases, and relevant API endpoints.

<a id="álgebra-avanzada"></a>
## Advanced Algebra
- **Gröbner Bases Algorithm**: For solving systems of polynomial equations.
  - Use: Simplification of equations in quantum physics.
  - Endpoint: `/mathematics/algebra/groebner`

- **Singular Value Decomposition (SVD)**: Matrix decomposition.
  - Use: Dimensionality reduction in ML.
  - Endpoint: `/mathematics/algebra/svd`

<a id="ecuaciones-diferenciales"></a>
## Differential Equations
- **Runge-Kutta Method**: Numerical solution of ODEs.
  - Use: Dynamic modeling in biology.
  - Endpoint: `/mathematics/differential/runge-kutta`

- **PDE Solver**: Finite element methods.
  - Use: Physical simulations.
  - Endpoint: `/mathematics/differential/pde-solver`

<a id="teoría-de-números"></a>
## Number Theory
- **Extended Euclidean Algorithm**: For GCD and Bézout coefficients.
  - Use: Cryptography.
  - Endpoint: `/mathematics/number-theory/extended-euclid`

- **Primality Test (Miller-Rabin)**: Verification of prime numbers.
  - Use: Security in quantum computing.
  - Endpoint: `/mathematics/number-theory/primality-test`

<a id="análisis-complejo"></a>
## Complex Analysis
- **Fast Fourier Transform (FFT)**: Signal analysis.
  - Use: Image processing in medicine.
  - Endpoint: `/mathematics/complex/fft`

- **Contour Integration**: Calculations in the complex plane.
  - Use: Theoretical physics.
  - Endpoint: `/mathematics/complex/contour-integration`

<a id="topología"></a>
## Topology
- **Betti Number Calculation**: Topological data analysis.
  - Use: Shape analysis in neuroscience.
  - Endpoint: `/mathematics/topology/betti-numbers`

<a id="teoría-de-grafos"></a>
## Graph Theory
- **Dijkstra's Algorithm**: Shortest paths.
  - Use: Neural networks.
  - Endpoint: `/mathematics/graphs/dijkstra`

- **Community Detection (Louvain)**: Network analysis.
  - Use: Systems biology.
  - Endpoint: `/mathematics/graphs/community-detection`

<a id="optimización"></a>
## Optimization
- **Linear Programming (Simplex)**: Optimization with constraints.
  - Use: Logistics in engineering.
  - Endpoint: `/mathematics/optimization/linear-programming`

- **Genetic Algorithms**: Evolutionary optimization.
  - Use: Materials design.
  - Endpoint: `/mathematics/optimization/genetic-algorithm`

For detailed implementation, consult the source code in subdirectories such as applied/ and computational/. Updates pending for more algorithms.
