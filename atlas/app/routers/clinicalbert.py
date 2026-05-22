"""
ClinicalBERT Router Wrapper

This module serves as a wrapper to import the clinicalbert router from the medicine domain.
It provides a consistent import path for the main application while maintaining
the domain-specific organization of the actual router implementation.
"""

from app.domains.medicine.routers.clinicalbert import router

__all__ = ['router']