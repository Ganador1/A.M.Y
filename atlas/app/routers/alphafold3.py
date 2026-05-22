"""
AlphaFold3 Router Wrapper

This module serves as a wrapper to import the alphafold3 router from the medicine domain.
It provides a consistent import path for the main application while maintaining
the domain-specific organization of the actual router implementation.
"""

from app.domains.medicine.routers.alphafold3 import router

__all__ = ['router']