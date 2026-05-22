"""Re-exports y helpers para ValidationMatrixPersistence (compatibilidad con imports históricos).

Exporta:
- ValidationSnapshot
- ValidationMatrixPersistence
- ValidationMatrixRecorder
- get_validation_persistence()
"""
from __future__ import annotations

from app.validation.validation_matrix_persistence import (
    ValidationSnapshot,
    ValidationMatrixPersistence,
    ValidationMatrixRecorder,
)

_singleton: ValidationMatrixPersistence | None = None


def get_validation_persistence() -> ValidationMatrixPersistence:
    global _singleton
    if _singleton is None:
        _singleton = ValidationMatrixPersistence()
    return _singleton
