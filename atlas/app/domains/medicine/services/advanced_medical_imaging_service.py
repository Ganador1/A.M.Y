"""
Compatibility shim for advanced medical imaging service.
Re-exports classes and functions from the actual implementation.
"""

# Import necessary dependencies for test patching
import SimpleITK as sitk
import nibabel as nib
import pydicom
from pathlib import Path

from app.domains.medicine.imaging.advanced_medical_imaging_service import (
    AdvancedMedicalImagingService,
    ClinicalValidationMetrics,
    ClinicalStandard,
    ImageModality,
    NIFTIMetadata,
    advanced_medical_imaging_service,
    load_medical_image_enhanced,
    validate_clinical_accuracy
)

# Convenience functions
def load_medical_image_enhanced(image_path, modality=None):
    """Load medical image with enhanced metadata"""
    return advanced_medical_imaging_service.load_medical_image_enhanced(image_path, modality)

def validate_clinical_accuracy(segmentation_result, ground_truth=None):
    """Validate clinical accuracy of segmentation"""
    return advanced_medical_imaging_service.validate_clinical_accuracy(segmentation_result, ground_truth)