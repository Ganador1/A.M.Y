"""Mathematics Domain Exceptions"""

from app.exceptions.base import AtlasDomainError


class MathError(AtlasDomainError):
    """Base exception for mathematics domain"""
    pass


# Alias for consistency with migration script
MathematicsError = MathError


class SymbolicError(MathError):
    """Errores en álgebra simbólica"""
    pass


class OptimizationError(MathError):
    """Errores en optimización"""
    pass


class GraphTheoryError(MathError):
    """Errores en teoría de grafos"""
    pass