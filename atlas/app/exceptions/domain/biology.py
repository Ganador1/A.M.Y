"""
Biology Domain Exceptions
"""

from app.exceptions.base import AtlasDomainError


class BiologyError(AtlasDomainError):
    """Base exception for biology domain"""
    pass


class ProteinAnalysisError(BiologyError):
    """Errores en análisis de proteínas"""
    pass


class SequenceAlignmentError(BiologyError):
    """Errores en alineamiento de secuencias"""
    pass


class GenomicsError(BiologyError):
    """Errores en análisis genómico"""
    pass


class StructurePredictionError(BiologyError):
    """Errores en predicción de estructura"""
    pass


class BiodiversityAnalysisError(BiologyError):
    """Errores en análisis de biodiversidad"""
    pass