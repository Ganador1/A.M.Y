"""
Compatibility wrapper for Validation Matrix Persistence API.
Re-exports the concrete implementation from app.validation.validation_matrix_persistence
so imports like `from app.domains.validation_matrix_persistence import ...` work as expected.
"""

from app.validation.validation_matrix_persistence import (
    ValidationSnapshot,
    ValidationMatrixPersistence,
    ValidationMatrixRecorder,
    get_validation_persistence,
    get_validation_recorder,
)

__all__ = [
    "ValidationSnapshot",
    "ValidationMatrixPersistence",
    "ValidationMatrixRecorder",
    "get_validation_persistence",
    "get_validation_recorder",
]
