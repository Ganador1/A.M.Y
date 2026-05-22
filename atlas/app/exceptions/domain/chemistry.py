"""Chemistry Domain Exceptions"""

from app.exceptions.base import AtlasDomainError


class ChemistryError(AtlasDomainError):
    """Base exception for chemistry domain"""
    pass


class MolecularError(ChemistryError):
    """Errores en operaciones moleculares"""
    pass


class ReactionError(ChemistryError):
    """Errores en simulación de reacciones"""
    pass


class SpectrometryError(ChemistryError):
    """Errores en espectrometría"""
    pass