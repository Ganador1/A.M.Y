"""
Operational Cross-Validation Matrix - Compatibility Wrapper
This module re-exports the canonical implementation from app.validation.operational_cross_validation_matrix
to maintain backward compatibility with imports expecting app.operational_cross_validation_matrix.
"""

from app.validation.operational_cross_validation_matrix import (
    OperationalCrossValidationMatrix,
    MathematicalCompatibilityValidator,
    PhysicsCompatibilityValidator,
    BiologicalCompatibilityValidator,
    CrossValidationRun,
    ValidationDomain,
    CompatibilityScore,
    CompatibilityLevel,
    OperationalConfig,
    operational_matrix,
    validate_service_compatibility,
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
    "OperationalConfig",
    "operational_matrix",
    "validate_service_compatibility",
]