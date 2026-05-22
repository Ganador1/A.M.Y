"""
Grover's Search Algorithm Module
===============================

This module provides implementations for Grover's Search Algorithm.
Grover's algorithm gives a quadratic speedup for searching unstructured databases.

Algorithm Steps:
1. Initialize qubits in equal superposition state |s⟩
2. Apply Oracle operator Uw (flips phase of target state |w⟩)
3. Apply Diffusion operator Us (inversion about mean)
4. Repeat steps 2 & 3 approx √N times
5. Measure

Author: AXIOM Team (Refactored)
"""

from typing import Dict, Any, Optional, List, Union
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Framework availability checks
try:
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector
    QISKIT_AVAILABLE = True
except ImportError:
    QISKIT_AVAILABLE = False


def create_grover_search_qiskit(
    n_qubits: int = 2,
    target_state: str = "11"
) -> Dict[str, Any]:
    """
    Implement Grover's search algorithm using Qiskit.
    
    This implementation constructs the circuit explicity for educational purposes,
    building the Oracle and Diffusion operators gate-by-gate.

    Args:
        n_qubits (int): Number of qubits to search. Currently optimized for 2 qubits.
        target_state (str): Binary string representing the state to find (e.g., "11", "101").

    Returns:
        Dict[str, Any]: Results including the circuit, probabilities, and the 
                        most likely measured state.

    Raises:
        RuntimeError: If Qiskit is not available.
    """
    if not QISKIT_AVAILABLE:
        raise RuntimeError("Qiskit is not installed.")

    try:
        # Robustness: Restrict to 2 qubits for this specific implementation
        # The original logic was hardcoded for 2 qubits structure (cz gate usage)
        # Extending to N qubits requires MCX (Multi-Controlled X) gates.
        if n_qubits != 2:
            logger.warning("Current manual implementation optimized for 2 qubits. Forcing n_qubits=2.")
            n_qubits = 2

        qc = QuantumCircuit(n_qubits)

        # 1. Initialization: Equal superposition |s⟩ = H^n |0⟩
        for q in range(n_qubits):
            qc.h(q)

        # 2. Oracle: Flip phase of target state |w⟩
        # We want Uw|x⟩ = -|x⟩ if x=w, else |x⟩
        # For |11⟩, CZ does exactly this.
        # For other states, we wrap CZ with X gates on '0' bits to transform w to 11.
        
        # Ensure target state string length matches n_qubits, padding with '0' if needed
        # or taking last n bits. For clarity, let's normalize.
        target = target_state.zfill(n_qubits)[-n_qubits:]
        
        # Qiskit uses little-endian (q0 is propertly the rightmost bit in string, 
        # but string indexing target[0] usually implies MSB. 
        # Let's align with the original implementation logic:
        # "reversed(target)" suggests matching string index to qubit index properly.
        
        # Pre-processing (X gates for 0s)
        for i, bit in enumerate(reversed(target)):
            if bit == '0':
                qc.x(i)
        
        # Phase flip for |11...1⟩ equivalent
        # For 2 qubits, CZ works. For N, we'd need MCP (Multi-Controlled Phase) or MCU1.
        if n_qubits == 2:
            qc.cz(0, 1)
        else:
            # Fallback placeholder for potential future expansion
            qc.cz(0, 1) 

        # Post-processing (X gates to restore basis)
        for i, bit in enumerate(reversed(target)):
            if bit == '0':
                qc.x(i)

        # 3. Diffusion Operator (Us): 2|s⟩⟨s| - I
        # Implemented as: H^n -> X^n -> Multi-Controlled Z -> X^n -> H^n
        for q in range(n_qubits):
            qc.h(q)
            qc.x(q)
        
        # Multi-controlled Z logic (for 2 qubits: H(1) -> CZ(0,1) -> H(1))
        # Equivalent to CZ but acting on different basis
        qc.h(1)
        qc.cz(0, 1)
        qc.h(1)
        
        for q in range(n_qubits):
            qc.x(q)
            qc.h(q)

        # 4. Simulation
        probabilities: List[float]
        try:
            sv = Statevector.from_instruction(qc)
            probabilities = (np.abs(sv.data) ** 2).tolist()
        except Exception as e:
            # Fallback if statevector fails could be added, but usually 
            # implies Qiskit issue if creating it failed.
            raise RuntimeError(f"Statevector simulation failed: {e}")

        # Compute results
        idx = int(np.argmax(probabilities))
        # Format most likely state as bitstring
        most_likely = format(idx, f"0{n_qubits}b")

        return {
            "framework": "qiskit",
            "algorithm": "grover_search",
            "parameters": {
                "n_qubits": n_qubits,
                "target_state": target
            },
            "results": {
                "probabilities": probabilities,
                "most_likely_state": most_likely,
                "success_probability": float(max(probabilities))
            }
        }

    except Exception as e:
        logger.error(f"Error in create_grover_search_qiskit: {e}")
        raise RuntimeError(f"Grover search failed: {str(e)}") from e
