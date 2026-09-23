"""
Variational Calculus Service Compatibility Shim
===============================================

This module provides a compatibility layer for the VariationalCalculusService,
allowing tests and other modules to import from app.services.variational_calculus_service
while the actual implementation is in app.domains.mathematics.services.

This shim re-exports the VariationalCalculusService class from its actual location.
"""

from app.domains.mathematics.services.variational_calculus_service import VariationalCalculusService

# Re-export for compatibility
__all__ = ['VariationalCalculusService']