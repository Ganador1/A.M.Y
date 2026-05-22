# Catálogo de Algoritmos Cuánticos

Este documento lista los algoritmos cuánticos soportados, su propósito, parámetros comunes y consideraciones de rendimiento.

## VQE (Variational Quantum Eigensolver)
- **Objetivo:** Aproximar el estado fundamental de un Hamiltoniano.
- **Flujo:** Circuito parametrizado + optimizador clásico.
- **Parámetros:** Ansatz, inicialización, optimizador, shots.
- **Endpoint:** `POST /api/physics/quantum/algorithms/vqe`
- **Complejidad:** Dependiente del ansatz y del optimizador; coste de mediciones.

## QAOA (Quantum Approximate Optimization Algorithm)
- **Objetivo:** Optimización combinatoria (ej. MaxCut).
- **Flujo:** Alterna operadores de costo y mezcla con profundidad `p`.
- **Parámetros:** Grafo/problema, `p`, optimizador.
- **Endpoint:** `POST /api/physics/quantum/algorithms/qaoa`
- **Complejidad:** Escala con `p` y tamaño del grafo.

## Grover's Algorithm
- **Objetivo:** Búsqueda no estructurada con ventaja cuadrática.
- **Parámetros:** Oráculo, número de iteraciones.
- **Endpoint:** `POST /api/physics/quantum/algorithms/grover`
- **Complejidad:** O(√N) iteraciones.

## Shor's Algorithm
- **Objetivo:** Factoreo entero usando QFT.
- **Parámetros:** Número a factorizar, control de ruido.
- **Endpoint:** `POST /api/physics/quantum/algorithms/shor`
- **Complejidad:** Polinomial cuántica; alto costo de simulación clásica.

## Quantum Fourier Transform (QFT)
- **Objetivo:** Transformada en base cuántica; subrutina clave.
- **Parámetros:** Número de qubits, ordenamiento.
- **Endpoint:** `POST /api/physics/quantum/algorithms/qft`
- **Complejidad:** O(n^2) puertas para n qubits.

## Ejemplos
- Ver [EXAMPLES.md](../EXAMPLES.md) y la guía API de Physics.

## Consideraciones
- Ajustar profundidad y shots para balancear precisión/tiempo.
- Usar simuladores con ruido para realismo.