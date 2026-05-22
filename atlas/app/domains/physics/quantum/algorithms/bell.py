"""
Bell State Algorithms Module
===========================

This module provides implementations for creating and simulating Bell states
using various quantum frameworks (Qiskit, Cirq).

Bell states are specific quantum states of two qubits that represent
the simplest examples of quantum entanglement.

The four Bell states are:
    |Φ+⟩ = (|00⟩ + |11⟩) / √2
    |Φ-⟩ = (|00⟩ - |11⟩) / √2
    |Ψ+⟩ = (|01⟩ + |10⟩) / √2
    |Ψ-⟩ = (|01⟩ - |10⟩) / √2

Author: AXIOM Team (Refactored)
"""

from typing import Dict, Any, Optional, List, Union, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Framework availability checks
try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.quantum_info import Statevector
    from qiskit import Aer
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False

try:
    import cirq
    CIRQ_AVAILABLE = True
except ImportError:
    CIRQ_AVAILABLE = False


def create_bell_state_qiskit(
    backend_name: str = "statevector_simulator"
) -> Dict[str, Any]:
    """
    Create and simulate a Bell state (|Φ+⟩) using Qiskit.

    Generates the circuit:
        q_0: ──H────■──
             q_1: ──────┼──X──

    Args:
        backend_name (str): The simulation backend to use. 
                            Defaults to "statevector_simulator".

    Returns:
        Dict[str, Any]: A dictionary containing:
            - framework: "qiskit"
            - circuit_type: "bell_state"
            - circuit: Metadata about the circuit (depth, qubits)
            - results: Probabilities of measured states.

    Raises:
        RuntimeError: If Qiskit is not installed or simulation fails.
    """
    if not QISKIT_AVAILABLE:
        raise RuntimeError("Qiskit is not installed.")

    try:
        # Create Bell state circuit
        qc = QuantumCircuit(2)
        qc.h(0)     # Hadamard on first qubit
        qc.cx(0, 1) # CNOT gate (control=0, target=1)

        probabilities: Union[List[float], Dict[str, float]]
        backend_used = "statevector_simulator"

        try:
            # Preferred: use measurement-free statevector simulation
            sv = Statevector.from_instruction(qc)
            probs = (np.abs(sv.data) ** 2).tolist()
            probabilities = probs
            backend_used = "statevector"
        except Exception as sv_error:
            logger.debug(f"Statevector simulation failed, falling back to Aer: {sv_error}")
            # Fallback: Aer simulator with measurement
            
            # Create a copy with measurement
            qc_meas = qc.copy()
            qc_meas.measure_all()
            
            # Get backend
            try:
                backend = Aer.get_backend("qasm_simulator")
            except Exception:
                # Last resort fallback if 'qasm_simulator' not found directly via Aer
                # This handles newer qiskit versions structure differences
                from qiskit.providers.basic_provider import BasicProvider
                backend = BasicProvider().get_backend("basic_simulator")

            tqc = transpile(qc_meas, backend)
            job = backend.run(tqc, shots=1024)
            result = job.result()
            counts = result.get_counts()
            
            # Normalize counts to probabilities
            total_shots = sum(counts.values())
            probabilities = {
                state: count / total_shots 
                for state, count in counts.items()
            }
            backend_used = "qasm_simulator"

        return {
            "framework": "qiskit",
            "circuit_type": "bell_state",
            "circuit": {
                "num_qubits": qc.num_qubits,
                "num_clbits": qc.num_clbits,
                "depth": qc.depth(),
                # Note: 'diagram' generation is omitted to keep pure logic clean.
                # It can be handled by the presentation layer or service.
            },
            "results": {
                "probabilities": probabilities,
                "backend": backend_used
            }
        }

    except Exception as e:
        logger.error(f"Error in create_bell_state_qiskit: {e}")
        raise RuntimeError(f"Bell state simulation failed: {str(e)}") from e


def create_bell_state_cirq() -> Dict[str, Any]:
    """
    Create and simulate a Bell state (|Φ+⟩) using Cirq.

    Args:
        None

    Returns:
        Dict[str, Any]: A dictionary containing results and circuit metadata.

    Raises:
        RuntimeError: If Cirq is not installed.
    """
    if not CIRQ_AVAILABLE:
        raise RuntimeError("Cirq is not installed.")

    try:
        # Create qubits
        q0, q1 = cirq.LineQubit.range(2)

        # Create Bell state circuit
        circuit = cirq.Circuit(
            cirq.H(q0),
            cirq.CNOT(q0, q1),
            cirq.measure(q0, q1, key='result')
        )

        # Simulate
        simulator = cirq.Simulator()
        result = simulator.run(circuit, repetitions=1024)

        # Get measurement results
        measurements = result.measurements['result']
        
        # Calculate counts manually
        counts: Dict[str, int] = {}
        # measurements is a numpy array of shape (repetitions, num_qubits)
        # We need to convert each row to a bitstring
        for row in measurements:
            state = ''.join(str(int(bit)) for bit in row)
            counts[state] = counts.get(state, 0) + 1

        probabilities = {
            state: count / 1024 
            for state, count in counts.items()
        }

        return {
            "framework": "cirq",
            "circuit_type": "bell_state",
            "circuit": {
                "num_qubits": 2,
                "circuit_text": str(circuit)
            },
            "results": {
                "probabilities": probabilities,
                "measurements": counts
            }
        }

    except Exception as e:
        logger.error(f"Error in create_bell_state_cirq: {e}")
        raise RuntimeError(f"Cirq Bell state simulation failed: {str(e)}") from e
