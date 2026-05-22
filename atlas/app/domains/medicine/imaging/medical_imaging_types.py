"""
Shared data types for Medical Imaging Services
Contains dataclasses and enums used across medical imaging modules

Enhanced Features:
- Input validation
- Example values
- Better documentation
- Serialization support
- Unit conversion utilities
"""

import numpy as np
from typing import Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json
import asyncio
# Removed unused imports to satisfy linters
import warnings

# Constants for physiological ranges
NORMAL_HEART_RATE_RANGE = (50, 120)  # beats per minute
NORMAL_GLS_RANGE = (-30, 0)  # percent
NORMAL_GCS_RANGE = (-30, 0)  # percent
NORMAL_GRS_RANGE = (0, 100)  # percent

class ImagingModality(Enum):
    """Supported medical imaging modalities
    
    Attributes:
        MRI: Magnetic Resonance Imaging
        CT: Computed Tomography
        ULTRASOUND: Ultrasound imaging
        PET: Positron Emission Tomography
    """
    MRI = "mri"
    CT = "ct"
    ULTRASOUND = "ultrasound"
    PET = "pet"

    @classmethod
    def supported_modalities(cls) -> list[str]:
        """Returns list of all supported modality names"""
        return [m.value for m in cls]

# Backward-compatibility alias expected by some routers/tests
# ImageModality was the previous name; keep it as alias to ImagingModality
ImageModality = ImagingModality


class CardiacView(Enum):
    """Cardiac imaging views
    
    Attributes:
        SAX: Short-axis view
        LAX: Long-axis view
        HLA: Horizontal long-axis
        VLA: Vertical long-axis
        FOUR_CHAMBER: Four chamber view
        TWO_CHAMBER: Two chamber view
    """
    SAX = "sax"  # Short-axis
    LAX = "lax"  # Long-axis
    HLA = "hla"  # Horizontal long-axis
    VLA = "vla"  # Vertical long-axis
    FOUR_CHAMBER = "four_chamber"
    TWO_CHAMBER = "two_chamber"

    @classmethod
    def is_standard_view(cls, view: str) -> bool:
        """Check if view is one of the standard cardiac views"""
        return view.upper() in cls.__members__


@dataclass
class DICOMMetadata:
    """
    DICOM file metadata with validation
    
    Attributes:
        patient_id: Unique patient identifier
        study_date: Date of the study in YYYYMMDD format
        modality: Imaging modality (e.g. MRI, CT, etc.)
        series_description: Description of the series
        slice_thickness: Thickness of each slice in mm
        pixel_spacing: Spacing between pixels in mm
        image_dimensions: Dimensions of the image in pixels
        number_of_frames: Number of frames in the series
        cardiac_phase: Cardiac phase (optional)
        heart_rate: Heart rate in beats per minute (optional)
    
    Example:
    >>> meta = DICOMMetadata(
    ...     patient_id="12345",
    ...     study_date="20230101",
    ...     modality="MRI",
    ...     series_description="Cardiac Cine",
    ...     slice_thickness=8.0,
    ...     pixel_spacing=(1.5, 1.5),
    ...     image_dimensions=(256, 256),
    ...     number_of_frames=30
    ... )
    """
    patient_id: str
    study_date: str
    modality: str
    series_description: str
    slice_thickness: float
    pixel_spacing: Tuple[float, float]
    image_dimensions: Tuple[int, int]
    number_of_frames: int
    cardiac_phase: Optional[str] = None
    heart_rate: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate metadata after initialization"""
        self.validate()
    
    def validate(self) -> None:
        """Validate DICOM metadata values"""
        if self.slice_thickness <= 0:
            raise ValueError(f"Slice thickness must be positive, got {self.slice_thickness}")
        if any(p <= 0 for p in self.pixel_spacing):
            raise ValueError(f"Pixel spacing values must be positive, got {self.pixel_spacing}")
        if any(d <= 0 for d in self.image_dimensions):
            raise ValueError(f"Image dimensions must be positive, got {self.image_dimensions}")
        if self.number_of_frames <= 0:
            raise ValueError(f"Number of frames must be positive, got {self.number_of_frames}")
        if self.heart_rate is not None and not (NORMAL_HEART_RATE_RANGE[0] <= self.heart_rate <= NORMAL_HEART_RATE_RANGE[1]):
            warnings.warn(f"Heart rate {self.heart_rate} bpm is outside normal range {NORMAL_HEART_RATE_RANGE}")
    
    def get_pixel_area(self) -> float:
        """Calculate pixel area in mm²"""
        return self.pixel_spacing[0] * self.pixel_spacing[1]
    
    def get_image_area(self) -> float:
        """Calculate total image area in mm²"""
        return self.image_dimensions[0] * self.image_dimensions[1] * self.get_pixel_area()
    
    def to_json(self) -> str:
        """Serialize to JSON string"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DICOMMetadata':
        """Deserialize from JSON string"""
        data = json.loads(json_str)
        return cls(**data)
    
    @classmethod
    def create_cardiac_mri(
        cls,
        patient_id: str,
        study_date: str,
        series_description: str,
        slice_thickness: float = 8.0,
        pixel_spacing: Tuple[float, float] = (1.5, 1.5),
        image_dimensions: Tuple[int, int] = (256, 256),
        number_of_frames: int = 30,
        cardiac_phase: Optional[str] = None,
        heart_rate: Optional[float] = None
    ) -> 'DICOMMetadata':
        """Create DICOM metadata for cardiac MRI with default values"""
        return cls(
            patient_id=patient_id,
            study_date=study_date,
            modality=ImagingModality.MRI.value,
            series_description=series_description,
            slice_thickness=slice_thickness,
            pixel_spacing=pixel_spacing,
            image_dimensions=image_dimensions,
            number_of_frames=number_of_frames,
            cardiac_phase=cardiac_phase,
            heart_rate=heart_rate
        )


# Module-level utility functions
def validate_modality(modality: str) -> bool:
    """Validate if modality is supported"""
    return modality.lower() in [m.value for m in ImagingModality]


def get_modality_enum(modality_str: str) -> Optional[ImagingModality]:
    """Get ImagingModality enum from string"""
    try:
        return ImagingModality(modality_str.lower())
    except ValueError:
        return None


def calculate_volume_from_mask(mask: np.ndarray, pixel_spacing: Tuple[float, float], slice_thickness: float) -> float:
    """Calculate volume from a binary mask
    
    Args:
        mask: Binary numpy array representing the structure
        pixel_spacing: Pixel spacing in mm (row_spacing, col_spacing)
        slice_thickness: Slice thickness in mm
    
    Returns:
        Volume in mm³
    """
    pixel_area = pixel_spacing[0] * pixel_spacing[1]
    voxel_volume = pixel_area * slice_thickness
    return np.sum(mask) * voxel_volume


@dataclass
class CardiacSegmentationResult:
    """Result of cardiac chamber segmentation"""
    left_ventricle_volume_ml: float
    right_ventricle_volume_ml: float
    left_atrium_volume_ml: float
    right_atrium_volume_ml: float
    myocardial_mass_g: float
    ejection_fraction_percent: float
    segmentation_quality_score: float
    segmentation_confidence: Dict[str, float]
    volume_estimates: Dict[str, float]  # Additional volume estimates

    def __post_init__(self):
        """Validate segmentation results"""
        if self.ejection_fraction_percent < 0 or self.ejection_fraction_percent > 100:
            raise ValueError("Ejection fraction must be between 0 and 100%")
        if self.segmentation_quality_score < 0 or self.segmentation_quality_score > 1:
            raise ValueError("Segmentation quality score must be between 0 and 1")
    
    def get_total_cardiac_volume(self) -> float:
        """Get total cardiac volume in mL"""
        return (self.left_ventricle_volume_ml + self.right_ventricle_volume_ml +
                self.left_atrium_volume_ml + self.right_atrium_volume_ml)
    
    def get_chamber_volumes(self) -> Dict[str, float]:
        """Get all chamber volumes as dictionary"""
        return {
            'left_ventricle': self.left_ventricle_volume_ml,
            'right_ventricle': self.right_ventricle_volume_ml,
            'left_atrium': self.left_atrium_volume_ml,
            'right_atrium': self.right_atrium_volume_ml
        }


@dataclass
class StrainAnalysisResult:
    """Result of cardiac strain analysis"""
    global_longitudinal_strain: float
    global_circumferential_strain: float
    global_radial_strain: float
    strain_quality_score: float
    regional_strain: Dict[str, Dict[str, float]]  # Regional strain values
    
    def __post_init__(self):
        """Validate strain results"""
        if self.strain_quality_score < 0 or self.strain_quality_score > 1:
            raise ValueError("Strain quality score must be between 0 and 1")


@dataclass
class MedicalImage:
    """Represents a medical image with metadata"""
    pixel_data: np.ndarray
    metadata: Dict[str, Any]
    modality: str
    spacing: Tuple[float, ...]
    origin: Tuple[float, ...]
    direction: Tuple[float, ...]
    clinical_metadata: Optional[Dict[str, Any]] = None
    quality_metrics: Optional[Dict[str, float]] = None
    
    @property
    def shape(self) -> Tuple[int, ...]:
        """Get the shape of the pixel data"""
        return getattr(self.pixel_data, 'shape', ())
    
    @property
    def dtype(self) -> str:
        """Get the data type of the pixel data"""
        return str(getattr(self.pixel_data, 'dtype', 'unknown'))


# Make sure we export everything needed
__all__ = [
    "ImagingModality",
    "ImageModality",
    "CardiacView",
    "DICOMMetadata",
    "CardiacSegmentationResult",
    "StrainAnalysisResult",
    "MedicalImage",
    "validate_modality",
    "get_modality_enum",
    "calculate_volume_from_mask",
    "NORMAL_HEART_RATE_RANGE",
    "NORMAL_GLS_RANGE",
    "NORMAL_GCS_RANGE",
    "NORMAL_GRS_RANGE"
]
