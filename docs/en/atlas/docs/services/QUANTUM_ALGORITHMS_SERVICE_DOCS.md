> English translation and privacy-reviewed derivative of an archived manual. Historical technical claims have not been revalidated for this release. Public maintainer: **Ganador1**.

<a id="quantum-algorithms-service"></a>
# Quantum Algorithms Service

<a id="alcance"></a>
## Scope
- Service: `QuantumAlgorithmsService` (`app/domains/physics/services/quantum_algorithms_service.py`).
- Purpose: Execution and simulation of quantum algorithms for optimization and computational chemistry.
- Implementation: Uses `Qiskit`, `Cirq`, and `Pennylane` for circuit design and execution on simulators or real hardware.

<a id="capacidades"></a>
## Capabilities
- **Quantum Optimization (QAOA)**: Solving combinatorial optimization problems using the Quantum Approximate Optimization Algorithm.
- **Quantum Chemistry (VQE)**: Estimation of ground-state energies of molecules using the Variational Quantum Eigensolver.
- **Circuit Simulation**: Execution of arbitrary quantum circuits with configurable noise models.
- **Benchmarking**: Performance comparison between quantum and classical algorithms.

<a id="algoritmos-soportados"></a>
## Supported Algorithms
- **QAOA**: For Max-Cut, TSP, and portfolio optimization problems.
- **VQE**: With support for various ansatze (UCCSD, Hardware Efficient).
- **Grover's Search**: Search in unstructured databases.

<a id="acciones-principales"></a>
## Main Actions

<a id="run_qaoa_optimization"></a>
### `run_qaoa_optimization`
Solves an optimization problem defined as an Ising Hamiltonian.
- **Input**:
  - `qubit_op`: Operator that defines the problem.
  - `p` (int): Number of repetition steps.
- **Output**:
  - `optimal_parameters` (List): Parameters found by the classical optimizer.
  - `best_measurement` (str): Bit string with the optimal solution.

<a id="compute_vqe_ground_state"></a>
### `compute_vqe_ground_state`
Computes the minimum energy of a molecule.
- **Input**:
  - `molecule_data` (Dict): Specification of the geometry and atomic basis.
  - `optimizer` (str): Optimization algorithm (e.g., 'COBYLA', 'SPSA').
- **Output**:
  - `ground_state_energy` (float): Energy calculated in Hartrees.

<a id="ejemplo-de-uso"></a>
## Usage Example
```python
from app.domains.physics.services.quantum_algorithms_service import QuantumAlgorithmsService

service = QuantumAlgorithmsService()
result = await service.compute_vqe_ground_state(
    molecule_data={"geometry": "H 0 0 0; H 0 0 0.735", "basis": "sto3g"}
)
print(f"Energía del estado fundamental: {result['ground_state_energy']} Ha")
```

<a id="pruebas"></a>
## Tests
- Run unit tests:
  - `"/workspace/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_quantum_algorithms_service.py`
