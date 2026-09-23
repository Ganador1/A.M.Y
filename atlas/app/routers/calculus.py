"""
Calculus router module - wrapper for domains.mathematics.routers.calculus
"""

from app.domains.mathematics.routers.calculus import (
    router,
    validate_mathematical_expression,
    format_calculus_result,
    CalculusOperationRequest,
    CalculusResult
)

# Expose the service for tests and easy patching
from app.domains.mathematics.services.calculus_service import CalculusService

__all__ = [
    "router",
    "validate_mathematical_expression",
    "format_calculus_result",
    "CalculusOperationRequest",
    "CalculusResult"
]