"""
Math Physics Service
Provides mathematical physics computations and analysis
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
from scipy import constants
import sympy as sp
from scipy.integrate import odeint, quad
from scipy.optimize import minimize
from app.exceptions.domain.physics import QuantumError

logger = logging.getLogger(__name__)

class PhysicsConstants:
    """Physical constants for calculations"""
    
    # Fundamental constants
    c = constants.c  # Speed of light
    h = constants.h  # Planck constant
    hbar = constants.hbar  # Reduced Planck constant
    k_B = constants.k  # Boltzmann constant
    e = constants.e  # Elementary charge
    m_e = constants.m_e  # Electron mass
    m_p = constants.m_p  # Proton mass
    epsilon_0 = constants.epsilon_0  # Vacuum permittivity
    mu_0 = constants.mu_0  # Vacuum permeability
    G = constants.G  # Gravitational constant

class QuantumMechanics:
    """Quantum mechanics calculations"""
    
    @staticmethod
    def harmonic_oscillator_energy(n: int, omega: float) -> float:
        """Calculate energy levels of quantum harmonic oscillator"""
        hbar = PhysicsConstants.hbar
        return hbar * omega * (n + 0.5)
    
    @staticmethod
    def de_broglie_wavelength(momentum: float) -> float:
        """Calculate de Broglie wavelength"""
        h = PhysicsConstants.h
        return h / momentum
    
    @staticmethod
    def schrodinger_equation_1d_solve(potential_func, x_range: Tuple[float, float], 
                                     num_points: int = 1000) -> Dict[str, Any]:
        """Solve 1D Schrödinger equation numerically"""
        x = np.linspace(x_range[0], x_range[1], num_points)
        dx = x[1] - x[0]
        
        # Kinetic energy operator (second derivative)
        kinetic = -PhysicsConstants.hbar**2 / (2 * PhysicsConstants.m_e) * \
                  (np.roll(np.eye(num_points), -1, axis=1) - 2 * np.eye(num_points) + 
                   np.roll(np.eye(num_points), 1, axis=1)) / dx**2
        
        # Potential energy
        V = np.diag([potential_func(xi) for xi in x])
        
        # Hamiltonian
        H = kinetic + V
        
        # Solve eigenvalue problem
        try:
            eigenvalues, eigenvectors = np.linalg.eigh(H)
            return {
                "x": x,
                "eigenvalues": eigenvalues[:10],  # First 10 energy levels
                "eigenvectors": eigenvectors[:, :10],
                "success": True
            }
        except QuantumError as e:
            logger.error(f"Error solving Schrödinger equation: {e}")
            return {"success": False, "error": str(e)}

class ClassicalMechanics:
    """Classical mechanics calculations"""
    
    @staticmethod
    def lagrangian_mechanics(kinetic_energy_func, potential_energy_func, 
                           coordinates: List[str]) -> Dict[str, Any]:
        """Apply Lagrangian mechanics"""
        try:
            # Create symbolic variables
            coords = [sp.Symbol(coord) for coord in coordinates]
            coords_dot = [sp.Symbol(f"{coord}_dot") for coord in coordinates]
            t = sp.Symbol('t')
            
            # Calculate Lagrangian L = T - V
            T = kinetic_energy_func(*coords, *coords_dot)
            V = potential_energy_func(*coords)
            L = T - V
            
            # Euler-Lagrange equations
            equations = []
            for i, (q, q_dot) in enumerate(zip(coords, coords_dot)):
                eq = sp.diff(sp.diff(L, q_dot), t) - sp.diff(L, q)
                equations.append(eq)
            
            return {
                "lagrangian": str(L),
                "coordinates": coordinates,
                "euler_lagrange_equations": [str(eq) for eq in equations],
                "success": True
            }
        except QuantumError as e:
            logger.error(f"Error in Lagrangian mechanics: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def solve_newton_equations(force_func, mass: float, initial_conditions: List[float],
                              t_span: Tuple[float, float], num_points: int = 1000) -> Dict[str, Any]:
        """Solve Newton's equations of motion"""
        try:
            def equations(y, t):
                position, velocity = y
                acceleration = force_func(position, velocity, t) / mass
                return [velocity, acceleration]
            
            t = np.linspace(t_span[0], t_span[1], num_points)
            solution = odeint(equations, initial_conditions, t)
            
            return {
                "time": t,
                "position": solution[:, 0],
                "velocity": solution[:, 1],
                "success": True
            }
        except QuantumError as e:
            logger.error(f"Error solving Newton's equations: {e}")
            return {"success": False, "error": str(e)}

class Thermodynamics:
    """Thermodynamics calculations"""
    
    @staticmethod
    def ideal_gas_law(pressure: float = None, volume: float = None, 
                     temperature: float = None, n_moles: float = None) -> Dict[str, float]:
        """Apply ideal gas law PV = nRT"""
        R = constants.R  # Gas constant
        
        # Count non-None values
        values = [pressure, volume, temperature, n_moles]
        known_count = sum(1 for v in values if v is not None)
        
        if known_count != 3:
            raise ValueError("Exactly 3 out of 4 parameters must be provided")
        
        result = {}
        if pressure is None:
            result["pressure"] = n_moles * R * temperature / volume
        elif volume is None:
            result["volume"] = n_moles * R * temperature / pressure
        elif temperature is None:
            result["temperature"] = pressure * volume / (n_moles * R)
        elif n_moles is None:
            result["n_moles"] = pressure * volume / (R * temperature)
        
        return result
    
    @staticmethod
    def maxwell_boltzmann_distribution(v: np.ndarray, temperature: float, 
                                     molecular_mass: float) -> np.ndarray:
        """Calculate Maxwell-Boltzmann velocity distribution"""
        k_B = PhysicsConstants.k_B
        m = molecular_mass
        T = temperature
        
        # Distribution function
        coefficient = 4 * np.pi * (m / (2 * np.pi * k_B * T))**(3/2)
        exponential = np.exp(-m * v**2 / (2 * k_B * T))
        
        return coefficient * v**2 * exponential
    
    @staticmethod
    def carnot_efficiency(hot_temp: float, cold_temp: float) -> float:
        """Calculate Carnot engine efficiency"""
        return 1 - cold_temp / hot_temp

class Electromagnetism:
    """Electromagnetic calculations"""
    
    @staticmethod
    def coulomb_force(q1: float, q2: float, distance: float) -> float:
        """Calculate Coulomb force between two charges"""
        k = 1 / (4 * np.pi * PhysicsConstants.epsilon_0)
        return k * abs(q1 * q2) / distance**2
    
    @staticmethod
    def electromagnetic_wave_properties(frequency: float) -> Dict[str, float]:
        """Calculate properties of electromagnetic wave"""
        c = PhysicsConstants.c
        
        return {
            "wavelength": c / frequency,
            "angular_frequency": 2 * np.pi * frequency,
            "wave_number": frequency / c,
            "energy_per_photon": PhysicsConstants.h * frequency
        }
    
    @staticmethod
    def maxwell_equations_in_vacuum() -> Dict[str, str]:
        """Return Maxwell's equations in vacuum"""
        return {
            "gauss_law": "∇ · E = ρ/ε₀",
            "gauss_law_magnetism": "∇ · B = 0",
            "faraday_law": "∇ × E = -∂B/∂t",
            "ampere_maxwell_law": "∇ × B = μ₀(J + ε₀∂E/∂t)"
        }

class Relativity:
    """Special and general relativity calculations"""
    
    @staticmethod
    def lorentz_factor(velocity: float) -> float:
        """Calculate Lorentz factor γ"""
        c = PhysicsConstants.c
        if velocity >= c:
            raise ValueError("Velocity must be less than speed of light")
        
        return 1 / np.sqrt(1 - (velocity / c)**2)
    
    @staticmethod
    def time_dilation(proper_time: float, velocity: float) -> float:
        """Calculate time dilation effect"""
        gamma = Relativity.lorentz_factor(velocity)
        return gamma * proper_time
    
    @staticmethod
    def length_contraction(proper_length: float, velocity: float) -> float:
        """Calculate length contraction"""
        gamma = Relativity.lorentz_factor(velocity)
        return proper_length / gamma
    
    @staticmethod
    def relativistic_energy(mass: float, velocity: float) -> Dict[str, float]:
        """Calculate relativistic energy and momentum"""
        c = PhysicsConstants.c
        gamma = Relativity.lorentz_factor(velocity)
        
        return {
            "rest_energy": mass * c**2,
            "kinetic_energy": (gamma - 1) * mass * c**2,
            "total_energy": gamma * mass * c**2,
            "momentum": gamma * mass * velocity
        }

class MathPhysicsService:
    """Main service for mathematical physics computations"""
    
    def __init__(self):
        self.quantum = QuantumMechanics()
        self.classical = ClassicalMechanics()
        self.thermo = Thermodynamics()
        self.electromag = Electromagnetism()
        self.relativity = Relativity()
        self.constants = PhysicsConstants()
        logger.info("Math Physics Service initialized")
    
    def solve_physics_problem(self, problem_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Solve various physics problems"""
        try:
            result = {"problem_type": problem_type, "timestamp": datetime.now().isoformat()}
            
            if problem_type == "harmonic_oscillator":
                n = parameters.get("n", 0)
                omega = parameters.get("omega", 1.0)
                energy = self.quantum.harmonic_oscillator_energy(n, omega)
                result["energy"] = energy
                
            elif problem_type == "ideal_gas":
                gas_result = self.thermo.ideal_gas_law(**parameters)
                result.update(gas_result)
                
            elif problem_type == "coulomb_force":
                force = self.electromag.coulomb_force(
                    parameters["q1"], parameters["q2"], parameters["distance"]
                )
                result["force"] = force
                
            elif problem_type == "relativistic_motion":
                rel_result = self.relativity.relativistic_energy(
                    parameters["mass"], parameters["velocity"]
                )
                result.update(rel_result)
                
            elif problem_type == "maxwell_boltzmann":
                v = np.array(parameters["velocities"])
                distribution = self.thermo.maxwell_boltzmann_distribution(
                    v, parameters["temperature"], parameters["molecular_mass"]
                )
                result["distribution"] = distribution.tolist()
                result["velocities"] = v.tolist()
                
            else:
                result["error"] = f"Unknown problem type: {problem_type}"
                return result
            
            result["success"] = True
            return result
            
        except QuantumError as e:
            logger.error(f"Error solving physics problem: {e}")
            return {
                "problem_type": problem_type,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_physical_constants(self) -> Dict[str, float]:
        """Get commonly used physical constants"""
        return {
            "speed_of_light": self.constants.c,
            "planck_constant": self.constants.h,
            "reduced_planck": self.constants.hbar,
            "boltzmann_constant": self.constants.k_B,
            "elementary_charge": self.constants.e,
            "electron_mass": self.constants.m_e,
            "proton_mass": self.constants.m_p,
            "vacuum_permittivity": self.constants.epsilon_0,
            "vacuum_permeability": self.constants.mu_0,
            "gravitational_constant": self.constants.G
        }
    
    def analyze_wave_function(self, wave_function_str: str, x_values: List[float]) -> Dict[str, Any]:
        """Analyze a quantum wave function"""
        try:
            x = sp.Symbol('x')
            psi = sp.sympify(wave_function_str)
            
            # Calculate probability density
            prob_density = sp.Abs(psi)**2
            
            # Evaluate at given points
            x_vals = np.array(x_values)
            psi_vals = [complex(psi.subs(x, xi)) for xi in x_vals]
            prob_vals = [abs(psi_val)**2 for psi_val in psi_vals]
            
            # Calculate normalization
            normalization_integral = sp.integrate(prob_density, (x, -sp.oo, sp.oo))
            
            return {
                "wave_function": wave_function_str,
                "probability_density": str(prob_density),
                "x_values": x_vals.tolist(),
                "psi_values": [(p.real, p.imag) for p in psi_vals],
                "probability_values": prob_vals,
                "normalization_integral": str(normalization_integral),
                "success": True
            }
            
        except QuantumError as e:
            logger.error(f"Error analyzing wave function: {e}")
            return {"success": False, "error": str(e)}

# Global service instance
math_physics_service = MathPhysicsService()

def solve_physics_problem(problem_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Solve a physics problem"""
    return math_physics_service.solve_physics_problem(problem_type, parameters)

def get_physical_constants() -> Dict[str, float]:
    """Get physical constants"""
    return math_physics_service.get_physical_constants()
