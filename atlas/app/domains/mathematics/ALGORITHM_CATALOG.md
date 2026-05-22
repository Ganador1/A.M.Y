# Catálogo de Algoritmos en el Dominio de Mathematics

Este catálogo detalla los algoritmos y herramientas matemáticas disponibles en AXIOM, organizados por subcategoría. Cada entrada incluye una descripción breve, casos de uso y endpoints API relevantes.

## Álgebra Avanzada
- **Algoritmo de Gröbner Bases**: Para resolver sistemas de ecuaciones polinomiales.
  - Uso: Simplificación de ecuaciones en física cuántica.
  - Endpoint: `/mathematics/algebra/groebner`

- **Descomposición en Valores Singulares (SVD)**: Descomposición matricial.
  - Uso: Reducción de dimensionalidad en ML.
  - Endpoint: `/mathematics/algebra/svd`

## Ecuaciones Diferenciales
- **Método de Runge-Kutta**: Solución numérica de ODEs.
  - Uso: Modelado dinámico en biología.
  - Endpoint: `/mathematics/differential/runge-kutta`

- **Solucionador de PDEs**: Métodos de elementos finitos.
  - Uso: Simulaciones físicas.
  - Endpoint: `/mathematics/differential/pde-solver`

## Teoría de Números
- **Algoritmo de Euclides Extendido**: Para MCD y coeficientes de Bézout.
  - Uso: Criptografía.
  - Endpoint: `/mathematics/number-theory/extended-euclid`

- **Test de Primalidad (Miller-Rabin)**: Verificación de números primos.
  - Uso: Seguridad en computación cuántica.
  - Endpoint: `/mathematics/number-theory/primality-test`

## Análisis Complejo
- **Transformada de Fourier Rápida (FFT)**: Análisis de señales.
  - Uso: Procesamiento de imágenes en medicina.
  - Endpoint: `/mathematics/complex/fft`

- **Integración de Contorno**: Cálculos en el plano complejo.
  - Uso: Física teórica.
  - Endpoint: `/mathematics/complex/contour-integration`

## Topología
- **Cálculo de Números de Betti**: Análisis topológico de datos.
  - Uso: Análisis de formas en neuroscience.
  - Endpoint: `/mathematics/topology/betti-numbers`

## Teoría de Grafos
- **Algoritmo de Dijkstra**: Caminos más cortos.
  - Uso: Redes neuronales.
  - Endpoint: `/mathematics/graphs/dijkstra`

- **Detección de Comunidades (Louvain)**: Análisis de redes.
  - Uso: Biología de sistemas.
  - Endpoint: `/mathematics/graphs/community-detection`

## Optimización
- **Programación Lineal (Simplex)**: Optimización con restricciones.
  - Uso: Logística en ingeniería.
  - Endpoint: `/mathematics/optimization/linear-programming`

- **Algoritmos Genéticos**: Optimización evolutiva.
  - Uso: Diseño de materiales.
  - Endpoint: `/mathematics/optimization/genetic-algorithm`

Para implementación detallada, consulta el código fuente en subdirectorios como applied/ y computational/. Actualizaciones pendientes para más algoritmos.