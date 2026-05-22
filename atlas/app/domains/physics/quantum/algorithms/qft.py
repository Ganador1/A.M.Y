"""
Quantum Fourier Transform (QFT) Module
=====================================

This module provides implementations for the Quantum Fourier Transform.
QFT is the quantum analogue of the discrete Fourier transform and is
a key component in many quantum algorithms (Shor's, Phase Estimation).

Author: AXIOM Team (Refactored)
"""

from typing import Dict, Any, List
import numpy as np
import logging

logger = logging.getLogger(__name__)

try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


def create_quantum_fourier_transform_qiskit(
    n_qubits: int = 3
) -> Dict[str, Any]:
    """
    Implement the Quantum Fourier Transform (QFT) using Qiskit.

    The circuit consists of:
    1. A series of Hadamard gates and Controlled-Phase rotations.
    2. SWAP gates at the end to reverse the qubit order (standard QFT convention).

    Args:
        n_qubits (int): Number of qubits for the QFT.

    Returns:
        Dict[str, Any]: Results containing statevector and probabilities.

    Raises:
        RuntimeError: If Qiskit is not available or simulation fails.
    """
    if not QISKIT_AVAILABLE:
        raise RuntimeError("Qiskit is not installed.")

    try:
        # Recursive function for QFT rotations
        def qft_rotations(circuit: QuantumCircuit, n: int):
            """Performs qft rotations on the first n qubits."""
            if n == 0:
                return circuit
            n -= 1
            circuit.h(n)
            for i in range(n):
                # Apply controlled phase rotation
                # Angle: pi / 2^(k) where k is distance between qubits
                circuit.cp(np.pi / 2**(n - i), i, n)
            qft_rotations(circuit, n)

        # Helper for swapping registers (reversing order)
        def swap_registers(circuit: QuantumCircuit, n: int):
            for i in range(n // 2):
                circuit.swap(i, n - i - 1)

        # Create main circuit
        qc = QuantumCircuit(n_qubits)

        # 1. State Initialization:
        # Create a superposition state to demonstrate the transform "visually"
        # Applying H to all qubits puts system in uniform superposition.
        # Note: In a real library, QFT is usually applied to an *input* state.
        # This function creates a demo circuit that INCLUDES input prep.
        for i in range(n_qubits):
            qc.h(i)

        # 2. Apply QFT sequence
        # We append a QFT sub-circuit to keep logic clean structure
        qc_qft = QuantumCircuit(n_qubits)
        qft_rotations(qc_qft, n_qubits)
        swap_registers(qc_qft, n_qubits)
        
        # Compose QFT into main circuit
        qc.compose(qc_qft, inplace=True)

        # 3. Simulation
        statevector: Statevector
        try:
            statevector = Statevector.from_instruction(qc)
        except Exception as e:
            raise RuntimeError(f"Statevector simulation failed: {e}")

        # Data extraction
        # statevector.data is a complex numpy array
        # We convert to list for JSON serialization compatibility
        sv_list = statevector.data.tolist()
        
        # Calculate probabilities
        probs = (np.abs(statevector.data) ** 2).tolist()

        return {
            "framework": "qiskit",
            "algorithm": "quantum_fourier_transform",
            "parameters": {"n_qubits": n_qubits},
            "results": {
                # Truncating statevector if too large? 
                # For >10 qubits, sending full vector is heavy.
                # Assuming modest demo sizes (<=10) per original code logic.
                "statevector": sv_list[:100] if n_qubits > 6 else sv_list,
                "probabilities": probs[:100] if n_qubits > 6 else probs,
                "note": "Output truncated if > 64 states" if n_qubits > 6 else None
            }
        }

    except Exception as e:
        logger.error(f"Error in create_quantum_fourier_transform_qiskit: {e}")
        raise RuntimeError(f"QFT generation failed: {str(e)}") from e
