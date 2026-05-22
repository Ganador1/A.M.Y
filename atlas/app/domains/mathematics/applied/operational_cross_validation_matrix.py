"""
Operational Cross-Validation Matrix - Compatibility Shim
This module re-exports the canonical implementation from app.validation.operational_cross_validation_matrix
so that imports like `from app.domains.operational_cross_validation_matrix import ...` work as expected in tests.
"""

from __future__ import annotations
from app.exceptions.domain.mathematics import MathematicsError

try:
    from app.validation.operational_cross_validation_matrix import (
        OperationalCrossValidationMatrix,
        MathematicalCompatibilityValidator,
        PhysicsCompatibilityValidator,
        BiologicalCompatibilityValidator,
        CrossValidationRun,
        ValidationDomain,
        CompatibilityScore,
        CompatibilityLevel,
        operational_matrix,
    )
except MathematicsError as e:  # pragma: no cover - make failures explicit if the canonical module changes
    # Provide a clear error early if the canonical implementation cannot be imported
    raise ImportError(
        "Failed to import canonical Operational Cross-Validation Matrix implementation: "
        f"{e}"
    )

__all__ = [
    "OperationalCrossValidationMatrix",
    "MathematicalCompatibilityValidator",
    "PhysicsCompatibilityValidator",
    "BiologicalCompatibilityValidator",
    "CrossValidationRun",
    "ValidationDomain",
    "CompatibilityScore",
    "CompatibilityLevel",
    "operational_matrix",
]
