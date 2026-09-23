"""
Compatibility shim for app.advanced_clinical_validation_service
Re-exports from app.domains.medicine.advanced_clinical_validation_service
"""

from app.domains.medicine.advanced_clinical_validation_service import (
    AdvancedClinicalValidationService,
    ValidationResult,
    ClinicalInterpretation,
    EFCalculationMethod,
    StrainValidationMetric,
    ClinicalGuideline,
    VentricularFunction,
    StrainValidationResult,
    ClinicalReport,
    BaseEFCalculator,
    SimpsonEFCalculator,
    AreaLengthEFCalculator,
    StrainValidator,
    advanced_clinical_validation_service,
    analyze_ventricular_function,
    validate_strain_analysis
)

# Add missing data structures expected by tests
from dataclasses import dataclass
from typing import Optional

@dataclass
class CardiacFunctionMetrics:
    """Cardiac function metrics data structure"""
    ef_simpson: Optional[float] = None
    ef_area_length: Optional[float] = None
    global_strain: Optional[float] = None
    regional_strain: Optional[list] = None
    wall_motion_score: Optional[float] = None