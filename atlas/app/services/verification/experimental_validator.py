"""
Compatibility wrapper for experimental_validator service.
Re-exports from app.domains.engineering.services.experimental_validator
"""

from app.domains.engineering.services.experimental_validator import (
    ExperimentalValidator,
    ValidationResult,
    ExperimentalData,
    StatisticalTest,
    MultipleTestingCorrection,
    OutlierMethod,
    get_experimental_validator
)

__all__ = [
    "ExperimentalValidator",
    "ValidationResult", 
    "ExperimentalData",
    "StatisticalTest",
    "MultipleTestingCorrection",
    "OutlierMethod",
    "get_experimental_validator"
]