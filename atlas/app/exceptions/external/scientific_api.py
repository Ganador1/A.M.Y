"""Scientific API Exceptions"""

from app.exceptions.base import AtlasExternalError


class ScientificAPIError(AtlasExternalError):
    """Base scientific API error"""
    pass


class UniProtError(ScientificAPIError):
    """UniProt API error"""
    pass


class PubChemError(ScientificAPIError):
    """PubChem API error"""
    pass


class ArXivError(ScientificAPIError):
    """arXiv API error"""
    pass


class NCBIError(ScientificAPIError):
    """NCBI API error (e.g., BLAST, Entrez)"""
    pass