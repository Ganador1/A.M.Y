"""
Quantum Physics Service for AXIOM
Integrates QuTiP for quantum mechanics simulations and analysis

Ethics & Safety:
- Simulaciones educativas/demostrativas; no usar para control real de hardware sin verificación rigurosa.
- Evita cargas excesivas: limita n_max, n_points y tiempos para prevenir DoS y uso excesivo de GPU/CPU.
- Revisa licencias y versiones de QuTiP; algunas funciones requieren dependencias del sistema.
- Los resultados dependen de modelos ideales; valida con literatura y experimentos cuando sea relevante.

Guía completa: ETHICS_AND_SAFETY.md
"""

import logging
from typing import Dict, Any
import numpy as np
from app.services.base_service import BaseService
from app.models import BaseResponse
from app.exceptions.domain.physics import QuantumError

logger = logging.getLogger(__name__)

# Lazy import to avoid loading QuTiP at module level
QUTIP_AVAILABLE = None

def _check_qutip():
    """Check if QuTiP is available and import it if needed"""
    global QUTIP_AVAILABLE
    if QUTIP_AVAILABLE is None:
        try:
            import qutip as qt  # noqa: F401
            QUTIP_AVAILABLE = True
            return True
        except ImportError:
            QUTIP_AVAILABLE = False
            logger.warning("QuTiP not available")
            return False
    return QUTIP_AVAILABLE


class QuantumPhysicsService(BaseService):
    """Service for quantum physics simulations"""

    def __init__(self):
        super().__init__("QuantumPhysicsService")
        self.qutip_available = _check_qutip()

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a quantum physics request"""
        try:
            operation = request_data.get("operation", "")
            self.log_request(request_data)

            if operation == "simulate_spin_evolution":
                result = self.simulate_spin_evolution(request_data.get("parameters", {}))
            elif operation == "simulate_harmonic_oscillator":
                result = self.simulate_harmonic_oscillator(request_data.get("parameters", {}))
            elif operation == "simulate_two_level_system":
                result = self.simulate_two_level_system(request_data.get("parameters", {}))
            elif operation == "calculate_quantum_entanglement":
                result = self.calculate_quantum_entanglement(request_data.get("state_type", "bell"))
            elif operation == "simulate_quantum_optics":
                result = self.simulate_quantum_optics(request_data.get("parameters", {}))
            elif operation == "service_info":
                result = self.get_service_info()
            else:
                result = {"error": f"Unknown operation: {operation}"}

            self.log_response(result)
            return result

        except QuantumError as e:
            return self.handle_error(e, "process_request")

    def get_service_info(self) -> Dict[str, Any]:
        """Get information about quantum physics capabilities"""
        if not _check_qutip():
            return {"qutip": {"available": False, "version": None, "capabilities": []}}

        import qutip as qt
        return {
            "qutip": {
                "available": True,
                "version": qt.__version__,
                "capabilities": [
                    "Quantum state evolution",
                    "Density matrix calculations",
                    "Quantum optics simulations",
                    "Open quantum systems",
                    "Quantum control theory"
                ]
            }
        }

    def simulate_spin_evolution(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate spin-1/2 particle evolution in magnetic field"""
        if not _check_qutip():
            return {"error": "QuTiP not available"}

        import qutip as qt
        from qutip import basis, sigmax, sigmay, sigmaz, sesolve

        try:
            # Extract parameters
            Bx = parameters.get("Bx", 1.0)
            By = parameters.get("By", 0.0)
            Bz = parameters.get("Bz", 1.0)
            t_max = parameters.get("t_max", 10.0)
            n_points = parameters.get("n_points", 100)

            # Initial state (spin up along z)
            psi0 = basis(2, 0)

            # Hamiltonian (Zeeman interaction)
            H = (Bx * sigmax() + By * sigmay() + Bz * sigmaz()) / 2

            # Time array
            t = np.linspace(0, t_max, n_points)

            # Solve Schrödinger equation
            result = sesolve(H, psi0, t, [])

            # Calculate expectation values
            sx_exp = qt.expect(sigmax(), result.states)
            sy_exp = qt.expect(sigmay(), result.states)
            sz_exp = qt.expect(sigmaz(), result.states)

            return {
                "simulation_type": "spin_evolution",
                "parameters": {
                    "magnetic_field": {"Bx": Bx, "By": By, "Bz": Bz},
                    "time_range": {"t_min": 0, "t_max": t_max, "n_points": n_points}
                },
                "results": {
                    "time": t.tolist(),
                    "expectation_values": {
                        "sx": sx_exp.tolist(),
                        "sy": sy_exp.tolist(),
                        "sz": sz_exp.tolist()
                    }
                }
            }

        except QuantumError as e:
            return {"error": f"Spin evolution simulation failed: {str(e)}"}

    def simulate_harmonic_oscillator(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate quantum harmonic oscillator"""
        if not _check_qutip():
            return {"error": "QuTiP not available"}

        import qutip as qt
        from qutip import destroy, sesolve

        try:
            # Extract parameters
            omega = parameters.get("omega", 1.0)
            n_max = parameters.get("n_max", 10)
            t_max = parameters.get("t_max", 20.0)
            n_points = parameters.get("n_points", 200)

            # Create harmonic oscillator Hamiltonian
            a = destroy(n_max)
            H = omega * (a.dag() * a + 0.5)

            # Initial coherent state
            alpha = parameters.get("alpha", 2.0)
            psi0 = qt.coherent(n_max, alpha)

            # Time array
            t = np.linspace(0, t_max, n_points)

            # Solve Schrödinger equation
            result = sesolve(H, psi0, t, [])

            # Calculate position and momentum expectation values
            x = (a + a.dag()) / np.sqrt(2)
            p = 1j * (a.dag() - a) / np.sqrt(2)

            x_exp = qt.expect(x, result.states)
            p_exp = qt.expect(p, result.states)

            # Calculate Wigner function at final time
            rho_final = qt.ket2dm(result.states[-1])
            x_vec = np.linspace(-4, 4, 50)
            p_vec = np.linspace(-4, 4, 50)
            W = qt.wigner(rho_final, x_vec, p_vec)

            return {
                "simulation_type": "harmonic_oscillator",
                "parameters": {
                    "omega": omega,
                    "n_max": n_max,
                    "alpha": alpha,
                    "time_range": {"t_min": 0, "t_max": t_max, "n_points": n_points}
                },
                "results": {
                    "time": t.tolist(),
                    "expectation_values": {
                        "position": x_exp.tolist(),
                        "momentum": p_exp.tolist()
                    },
                    "wigner_function": {
                        "x": x_vec.tolist(),
                        "p": p_vec.tolist(),
                        "W": W.tolist()
                    }
                }
            }

        except QuantumError as e:
            return {"error": f"Harmonic oscillator simulation failed: {str(e)}"}

    def simulate_two_level_system(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate two-level quantum system with dissipation"""
        if not _check_qutip():
            return {"error": "QuTiP not available"}

        import qutip as qt
        from qutip import sigmaz, sigmam, basis, mesolve

        try:
            # Extract parameters
            omega = parameters.get("omega", 1.0)
            gamma = parameters.get("gamma", 0.1)
            t_max = parameters.get("t_max", 25.0)
            n_points = parameters.get("n_points", 250)

            # Two-level system operators
            sz = sigmaz()
            sm = sigmam()
            sp = sm.dag()

            # Hamiltonian
            H = omega * sz / 2

            # Initial state
            psi0 = basis(2, 0)

            # Collapse operators (dissipation)
            c_ops = [np.sqrt(gamma) * sm]

            # Time array
            t = np.linspace(0, t_max, n_points)

            # Solve master equation
            result = mesolve(H, psi0, t, c_ops, [])

            # Calculate expectation values
            sz_exp = qt.expect(sz, result.states)
            population_ground = qt.expect(qt.ket2dm(basis(2, 0)), result.states)
            population_excited = qt.expect(qt.ket2dm(basis(2, 1)), result.states)

            return {
                "simulation_type": "two_level_system",
                "parameters": {
                    "omega": omega,
                    "gamma": gamma,
                    "time_range": {"t_min": 0, "t_max": t_max, "n_points": n_points}
                },
                "results": {
                    "time": t.tolist(),
                    "expectation_values": {
                        "sz": sz_exp.tolist(),
                        "population_ground": population_ground.tolist(),
                        "population_excited": population_excited.tolist()
                    }
                }
            }

        except QuantumError as e:
            return {"error": f"Two-level system simulation failed: {str(e)}"}

    def calculate_quantum_entanglement(self, state_type: str = "bell") -> Dict[str, Any]:
        """Calculate entanglement measures for quantum states"""
        if not _check_qutip():
            return {"error": "QuTiP not available"}

        import qutip as qt
        from qutip import basis

        try:
            if state_type == "bell":
                # Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
                psi = (qt.tensor(basis(2, 0), basis(2, 0)) +
                       qt.tensor(basis(2, 1), basis(2, 1))) / np.sqrt(2)
            elif state_type == "werner":
                # Werner state - first create the Bell state for the Werner state
                bell_psi = (qt.tensor(basis(2, 0), basis(2, 0)) +
                           qt.tensor(basis(2, 1), basis(2, 1))) / np.sqrt(2)
                p = 0.8
                # identity placeholder not required explicitly
                psi_max = qt.maximally_mixed_dm(4)
                psi = p * qt.ket2dm(bell_psi) + (1-p) * psi_max
            else:
                return {"error": f"Unsupported state type: {state_type}"}

            # Convert to density matrix if needed
            rho = qt.ket2dm(psi) if state_type == "bell" else psi

            # Calculate concurrence
            concurrence = qt.concurrence(rho)

            # Calculate entanglement entropy
            entropy = qt.entropy_von_neumann(rho)

            # Calculate negativity
            negativity = qt.negativity(rho, [2, 2])

            return {
                "state_type": state_type,
                "entanglement_measures": {
                    "concurrence": concurrence,
                    "von_neumann_entropy": entropy,
                    "negativity": negativity
                },
                "is_entangled": concurrence > 1e-10
            }

        except QuantumError as e:
            return {"error": f"Entanglement calculation failed: {str(e)}"}

    def simulate_quantum_optics(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate quantum optics phenomena"""
        if not _check_qutip():
            return {"error": "QuTiP not available"}

        import qutip as qt
        from qutip import destroy, basis, mesolve

        try:
            # Extract parameters
            n_max = parameters.get("n_max", 20)
            kappa = parameters.get("kappa", 0.1)  # Cavity decay rate
            g = parameters.get("g", 0.1)  # Coupling strength
            t_max = parameters.get("t_max", 50.0)
            n_points = parameters.get("n_points", 500)

            # Jaynes-Cummings model
            a = destroy(n_max)  # Annihilation operator
            sp = qt.sigmap()   # Raising operator for two-level system
            sm = qt.sigmam()   # Lowering operator for two-level system

            # Hamiltonian
            H = g * (a * sp + a.dag() * sm)

            # Initial state: cavity in coherent state, atom in ground state
            alpha = parameters.get("alpha", 3.0)
            psi_cavity = qt.coherent(n_max, alpha)
            psi_atom = basis(2, 0)  # Ground state
            psi0 = qt.tensor(psi_cavity, psi_atom)

            # Collapse operators
            c_ops = [np.sqrt(kappa) * qt.tensor(a, qt.qeye(2))]

            # Time array
            t = np.linspace(0, t_max, n_points)

            # Solve master equation
            result = mesolve(H, psi0, t, c_ops, [])

            # Calculate expectation values
            n_cavity = qt.expect(qt.tensor(a.dag() * a, qt.qeye(2)), result.states)
            sz_atom = qt.expect(qt.tensor(qt.qeye(n_max), qt.sigmaz()), result.states)

            return {
                "simulation_type": "jaynes_cummings",
                "parameters": {
                    "n_max": n_max,
                    "kappa": kappa,
                    "g": g,
                    "alpha": alpha,
                    "time_range": {"t_min": 0, "t_max": t_max, "n_points": n_points}
                },
                "results": {
                    "time": t.tolist(),
                    "expectation_values": {
                        "photon_number": n_cavity.tolist(),
                        "atomic_inversion": sz_atom.tolist()
                    }
                }
            }

        except QuantumError as e:
            return {"error": f"Quantum optics simulation failed: {str(e)}"}
