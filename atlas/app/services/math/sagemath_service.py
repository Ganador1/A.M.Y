"""
Compatibility wrapper for sagemath_service.
Re-exports the service from the domains structure.
"""

from app.domains.mathematics.services.sagemath_service import SageMathService

__all__ = ["SageMathService"]