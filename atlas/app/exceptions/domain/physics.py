"""Physics Domain Exceptions"""

from app.exceptions.base import AtlasDomainError


class PhysicsError(AtlasDomainError):
    """Base exception for physics domain"""
    pass


class QuantumError(PhysicsError):
    """Errores en cómputo cuántico"""
    pass


class ComputationalPhysicsError(PhysicsError):
    """Errores en física computacional"""
    pass


class ParticlePhysicsError(PhysicsError):
    """Errores en física de partículas"""
    pass


class SimulationError(PhysicsError):
    """Errores en simulaciones físicas"""
    pass