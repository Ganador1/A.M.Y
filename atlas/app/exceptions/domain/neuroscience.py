"""Neuroscience Domain Exceptions"""

from app.exceptions.base import AtlasDomainError


class NeuroscienceError(AtlasDomainError):
    """Base exception for neuroscience domain"""
    pass


class BrainImagingError(NeuroscienceError):
    """Errores en neuroimagen"""
    pass


class NeuroModelError(NeuroscienceError):
    """Errores en modelos neuronales"""
    pass