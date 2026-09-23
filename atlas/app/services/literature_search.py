"""
Literature Search Service - Compatibility Wrapper
Re-exports LiteratureSearchService from the literature module
"""

from app.services.literature.literature_search_improved import LiteratureSearchService

__all__ = ['LiteratureSearchService']
