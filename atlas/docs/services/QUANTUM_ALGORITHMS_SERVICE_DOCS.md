# Quantum Algorithms Service

## Alcance
- Servicio: `QuantumAlgorithmsService` (`app/domains/physics/services/quantum_algorithms_service.py`).
- Propósito: Ejecución y simulación de algoritmos cuánticos para optimización y química computacional.
- Implementación: Utiliza `Qiskit`, `Cirq` y `Pennylane` para el diseño de circuitos y ejecución en simuladores o hardware real.

## Capacidades
- **Optimización Cuántica (QAOA)**: Resolución de problemas de optimización combinatoria mediante el Quantum Approximate Optimization Algorithm.
- **Química Cuántica (VQE)**: Estimación de energías del estado fundamental de moléculas usando el Variational Quantum Eigensolver.
- **Simulación de Circuitos**: Ejecución de circuitos cuánticos arbitrarios con modelos de ruido configurables.
- **Benchmarking**: Comparación de rendimiento entre algoritmos cuánticos y clásicos.

## Algoritmos Soportados
- **QAOA**: Para problemas tipo Max-Cut, TSP, y optimización de carteras.
- **VQE**: Con soporte para diversos ansatze (UCCSD, Hardware Efficient).
- **Grover's Search**: Búsqueda en bases de datos no estructuradas.

## Acciones Principales

### `run_qaoa_optimization`
Resuelve un problema de optimización definido como un Hamiltoniano de Ising.
- **Entrada**:
  - `qubit_op`: Operador que define el problema.
  - `p` (int): Número de pasos de repetición.
- **Salida**:
  - `optimal_parameters` (List): Parámetros encontrados por el optimizador clásico.
  - `best_measurement` (str): Cadena de bits con la solución óptima.

### `compute_vqe_ground_state`
Calcula la energía mínima de una molécula.
- **Entrada**:
  - `molecule_data` (Dict): Especificación de la geometría y base atómica.
  - `optimizer` (str): Algoritmo de optimización (ej. 'COBYLA', 'SPSA').
- **Salida**:
  - `ground_state_energy` (float): Energía calculada en Hartrees.

## Ejemplo de Uso
```python
from app.domains.physics.services.quantum_algorithms_service import QuantumAlgorithmsService

service = QuantumAlgorithmsService()
result = await service.compute_vqe_ground_state(
    molecule_data={"geometry": "H 0 0 0; H 0 0 0.735", "basis": "sto3g"}
)
print(f"Energía del estado fundamental: {result['ground_state_energy']} Ha")
```

## Pruebas
- Ejecutar tests unitarios:
  - `"/Volumes/Ganador disk/atlas/.venv_new/bin/python" -m pytest -q tests/unit/test_quantum_algorithms_service.py`
