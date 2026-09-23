"""
Number Theory Service Compatibility Shim
========================================

This module provides a compatibility layer for the NumberTheoryService,
allowing tests and other modules to import from app.services.number_theory
while the actual implementation is in app.domains.mathematics.services.

This shim re-exports the NumberTheoryService class from its actual location.
"""

from app.domains.mathematics.services.number_theory_service import NumberTheoryService

# Re-export for compatibility
__all__ = ['NumberTheoryService']