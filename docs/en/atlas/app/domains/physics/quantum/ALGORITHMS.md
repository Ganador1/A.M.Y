> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="catálogo-de-algoritmos-cuánticos"></a>
# Quantum Algorithm Catalog

This document lists the supported quantum algorithms, their purpose, common parameters, and performance considerations.

<a id="vqe-variational-quantum-eigensolver"></a>
## VQE (Variational Quantum Eigensolver)
- **Objective:** Approximate the ground state of a Hamiltonian.
- **Flow:** Parameterized circuit + classical optimizer.
- **Parameters:** Ansatz, initialization, optimizer, shots.
- **Endpoint:** `POST /api/physics/quantum/algorithms/vqe`
- **Complexity:** Depends on the ansatz and the optimizer; measurement cost.

<a id="qaoa-quantum-approximate-optimization-algorithm"></a>
## QAOA (Quantum Approximate Optimization Algorithm)
- **Objective:** Combinatorial optimization (e.g., MaxCut).
- **Flow:** Alternates cost and mixer operators with depth `p`.
- **Parameters:** Graph/problem, `p`, optimizer.
- **Endpoint:** `POST /api/physics/quantum/algorithms/qaoa`
- **Complexity:** Scales with `p` and graph size.

<a id="grovers-algorithm"></a>
## Grover's Algorithm
- **Objective:** Unstructured search with quadratic advantage.
- **Parameters:** Oracle, number of iterations.
- **Endpoint:** `POST /api/physics/quantum/algorithms/grover`
- **Complexity:** O(√N) iterations.

<a id="shors-algorithm"></a>
## Shor's Algorithm
- **Objective:** Integer factorization using QFT.
- **Parameters:** Number to factor, noise control.
- **Endpoint:** `POST /api/physics/quantum/algorithms/shor`
- **Complexity:** Quantum polynomial; high classical simulation cost.

<a id="quantum-fourier-transform-qft"></a>
## Quantum Fourier Transform (QFT)
- **Objective:** Transform in the quantum basis; key subroutine.
- **Parameters:** Number of qubits, ordering.
- **Endpoint:** `POST /api/physics/quantum/algorithms/qft`
- **Complexity:** O(n^2) gates for n qubits.

<a id="ejemplos"></a>
## Examples
- See [EXAMPLES.md](../../../../../../../atlas/app/domains/physics/EXAMPLES.md) and the Physics API guide.

<a id="consideraciones"></a>
## Considerations
- Adjust depth and shots to balance accuracy/time.
- Use noisy simulators for realism.
