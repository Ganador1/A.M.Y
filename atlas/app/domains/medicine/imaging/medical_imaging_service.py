"""
Medical Imaging Integration Service for Cardiac Modeling
Handles DICOM/MRI data processing, cardiac segmentation, and patient-specific model calibration.
"""

import numpy as np
try:
    import pydicom
    import SimpleITK as sitk
except ImportError:
    pydicom = None
    sitk = None

from typing import Dict, List, Any, Tuple, Union
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

from app.domains.medicine.imaging.medical_imaging_types import (
    DICOMMetadata,
    CardiacSegmentationResult,
    StrainAnalysisResult,
    MedicalImage
)
from app.exceptions.domain.medicine import MedicalError

from app.domains.medicine.biomechanics.cardiac_region_models import (
    CardiacRegion,
    RegionalGeometry,
    RegionalMaterialProperties,
    CardiacRegionModelsService
)

from app.domains.medicine.imaging.advanced_segmentation_service import AdvancedSegmentationService

logger = logging.getLogger(__name__)


class MedicalImagingService:
    """Service for medical imaging integration with cardiac models"""

    def __init__(self):
        self.cardiac_service = CardiacRegionModelsService()
        self.advanced_segmentation = AdvancedSegmentationService()
        self.supported_formats = ['.dcm', '.dicom', '.nii', '.nii.gz', '.mha', '.nrrd']

        logger.info("🏥 Medical Imaging Service initialized with advanced segmentation")

    def cleanup(self):
        """Cleanup distributed resources"""
        from app.distributed.distributed_manager import distributed_manager
        distributed_manager.cleanup()

    def parse_dicom_series(self, dicom_directory: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a DICOM series for cardiac imaging

        Args:
            dicom_directory: Path to directory containing DICOM files

        Returns:
            Parsed DICOM data with metadata and pixel data
        """
        logger.info(f"🔍 Parsing DICOM series from: {dicom_directory}")

        dicom_path = Path(dicom_directory)
        if not dicom_path.exists():
            raise FileNotFoundError(f"DICOM directory not found: {dicom_directory}")

        # Find all DICOM files
        dicom_files = []
        for ext in self.supported_formats[:2]:  # Only DICOM formats
            dicom_files.extend(list(dicom_path.glob(f"**/*{ext}")))

        if not dicom_files:
            raise ValueError(f"No DICOM files found in {dicom_directory}")

        # Read DICOM series using SimpleITK
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(str(dicom_directory))
        reader.SetFileNames(dicom_names)
        image = reader.Execute()

        # Extract metadata from first file
        first_dicom = pydicom.dcmread(dicom_names[0])
        metadata = self._extract_dicom_metadata(first_dicom)

        # Convert to numpy array
        pixel_array = sitk.GetArrayFromImage(image)

        result = {
            'metadata': metadata,
            'pixel_data': pixel_array,
            'spacing': image.GetSpacing(),
            'origin': image.GetOrigin(),
            'direction': image.GetDirection(),
            'dimensions': image.GetSize(),
            'number_of_files': len(dicom_names)
        }

        logger.info(f"✅ DICOM series parsed: {len(dicom_names)} files, shape: {pixel_array.shape}")
        return result

    def _extract_dicom_metadata(self, dicom_file) -> DICOMMetadata:
        """Extract relevant metadata from DICOM file"""
        try:
            patient_id = getattr(dicom_file, 'PatientID', 'Unknown')
            study_date = getattr(dicom_file, 'StudyDate', 'Unknown')
            modality = getattr(dicom_file, 'Modality', 'Unknown')
            series_desc = getattr(dicom_file, 'SeriesDescription', 'Unknown')

            # Extract slice thickness and pixel spacing
            slice_thickness = float(getattr(dicom_file, 'SliceThickness', 1.0))
            pixel_spacing = getattr(dicom_file, 'PixelSpacing', [1.0, 1.0])
            pixel_spacing = (float(pixel_spacing[0]), float(pixel_spacing[1]))

            # Image dimensions
            rows = getattr(dicom_file, 'Rows', 0)
            cols = getattr(dicom_file, 'Columns', 0)
            dimensions = (rows, cols)

            # Number of frames (for cine sequences)
            number_of_frames = getattr(dicom_file, 'NumberOfFrames', 1)

            # Cardiac-specific metadata
            cardiac_phase = getattr(dicom_file, 'CardiacPhase', None)
            heart_rate = getattr(dicom_file, 'HeartRate', None)
            if heart_rate:
                heart_rate = float(heart_rate)

            return DICOMMetadata(
                patient_id=patient_id,
                study_date=study_date,
                modality=modality,
                series_description=series_desc,
                slice_thickness=slice_thickness,
                pixel_spacing=pixel_spacing,
                image_dimensions=dimensions,
                number_of_frames=number_of_frames,
                cardiac_phase=cardiac_phase,
                heart_rate=heart_rate
            )

        except MedicalError as e:
            logger.warning(f"Error extracting DICOM metadata: {e}")
            return DICOMMetadata(
                patient_id='Unknown',
                study_date='Unknown',
                modality='Unknown',
                series_description='Unknown',
                slice_thickness=1.0,
                pixel_spacing=(1.0, 1.0),
                image_dimensions=(0, 0),
                number_of_frames=1
            )

    def load_medical_image(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Load various medical imaging formats

        Args:
            file_path: Path to medical image file

        Returns:
            Image data and metadata
        """
        logger.info(f"📂 Loading medical image: {file_path}")

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Image file not found: {file_path}")

        file_ext = file_path.suffix.lower()

        if file_ext in ['.dcm', '.dicom']:
            # Single DICOM file
            dicom_data = pydicom.dcmread(str(file_path))
            pixel_array = dicom_data.pixel_array
            metadata = self._extract_dicom_metadata(dicom_data)

            return {
                'metadata': metadata,
                'pixel_data': pixel_array,
                'format': 'dicom'
            }

        elif file_ext in ['.nii', '.nii.gz']:
            # NIfTI format - placeholder for now
            raise NotImplementedError("NIfTI support coming soon")

        elif file_ext in ['.mha', '.nrrd']:
            # ITK formats
            image = sitk.ReadImage(str(file_path))
            pixel_array = sitk.GetArrayFromImage(image)

            return {
                'pixel_data': pixel_array,
                'spacing': image.GetSpacing(),
                'origin': image.GetOrigin(),
                'direction': image.GetDirection(),
                'dimensions': image.GetSize(),
                'format': 'itk'
            }

        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def segment_cardiac_chambers(self, image_data: Union[Dict[str, Any], MedicalImage],
                                 segmentation_method: str = 'enhanced_threshold') -> CardiacSegmentationResult:
        """
        Segment cardiac chambers from medical images

        Args:
            image_data: Medical image data (dict or MedicalImage object)
            segmentation_method: Segmentation algorithm to use
                                Options: 'threshold', 'region_growing', 'deep_learning',
                                        'enhanced_threshold', 'region_growing_enhanced'

        Returns:
            Segmentation results for all cardiac chambers
        """
        logger.info(f"🫀 Segmenting cardiac chambers using {segmentation_method}")

        # Handle both dict and MedicalImage objects
        if isinstance(image_data, MedicalImage):
            pixel_data = image_data.pixel_data
            image_dict = {
                'pixel_data': image_data.pixel_data,
                'metadata': image_data.metadata,
                'modality': image_data.modality,
                'spacing': image_data.spacing,
                'origin': image_data.origin,
                'direction': image_data.direction
            }
        else:
            pixel_data = image_data['pixel_data']
            image_dict = image_data

        # Use advanced segmentation service for enhanced methods
        if segmentation_method in ['enhanced_threshold', 'region_growing_enhanced']:
            return self.advanced_segmentation.segment_with_deep_learning(image_dict, segmentation_method)
        elif segmentation_method == 'threshold':
            return self._threshold_segmentation(pixel_data)
        elif segmentation_method == 'region_growing':
            return self._region_growing_segmentation(pixel_data)
        elif segmentation_method == 'deep_learning':
            return self._deep_learning_segmentation(pixel_data)
        else:
            raise ValueError(f"Unknown segmentation method: {segmentation_method}")

    def get_available_segmentation_methods(self) -> Dict[str, List[str]]:
        """
        Get available segmentation methods

        Returns:
            Dictionary with basic and advanced segmentation methods
        """
        basic_methods = ['threshold', 'region_growing', 'deep_learning']
        advanced_methods = self.advanced_segmentation.get_available_models()

        return {
            'basic_methods': basic_methods,
            'advanced_methods': advanced_methods,
            'all_methods': basic_methods + advanced_methods
        }

    def _threshold_segmentation(self, pixel_data: np.ndarray) -> CardiacSegmentationResult:
        """Simple threshold-based segmentation"""
        if pixel_data.ndim < 2:
            raise ValueError("Pixel data must have at least 2 dimensions")

        # Normalize pixel data
        normalized = (pixel_data - np.min(pixel_data)) / (np.max(pixel_data) - np.min(pixel_data))

        # Simple thresholding for different chambers
        # These are placeholder values - would need proper training/validation
        lv_threshold = 0.6
        rv_threshold = 0.5
        la_threshold = 0.4
        ra_threshold = 0.35
        myo_threshold = 0.7

        lv_mask = (normalized > lv_threshold).astype(np.uint8)
        rv_mask = ((normalized > rv_threshold) & (normalized <= lv_threshold)).astype(np.uint8)
        la_mask = ((normalized > la_threshold) & (normalized <= rv_threshold)).astype(np.uint8)
        ra_mask = ((normalized > ra_threshold) & (normalized <= la_threshold)).astype(np.uint8)
        myocardium_mask = (normalized > myo_threshold).astype(np.uint8)

        # Calculate volumes (simplified)
        voxel_volume = 1.0  # mm³ - would need proper spacing
        volumes = {
            'left_ventricle': np.sum(lv_mask) * voxel_volume,
            'right_ventricle': np.sum(rv_mask) * voxel_volume,
            'left_atrium': np.sum(la_mask) * voxel_volume,
            'right_atrium': np.sum(ra_mask) * voxel_volume,
            'myocardium': np.sum(myocardium_mask) * voxel_volume
        }

        # Calculate ejection fraction (simplified)
        lv_volume = volumes['left_ventricle']
        rv_volume = volumes['right_ventricle']
        la_volume = volumes['left_atrium']
        ra_volume = volumes['right_atrium']
        myocardial_mass = volumes['myocardium'] * 1.05  # Assume density of 1.05 g/mL

        # Estimate ejection fraction (placeholder)
        ejection_fraction = 55.0  # %

        return CardiacSegmentationResult(
            left_ventricle_volume_ml=lv_volume,
            right_ventricle_volume_ml=rv_volume,
            left_atrium_volume_ml=la_volume,
            right_atrium_volume_ml=ra_volume,
            myocardial_mass_g=myocardial_mass,
            ejection_fraction_percent=ejection_fraction,
            segmentation_quality_score=0.85,
            segmentation_confidence={
                'left_ventricle': 0.85,
                'right_ventricle': 0.80,
                'left_atrium': 0.75,
                'right_atrium': 0.70,
                'myocardium': 0.90
            },
            volume_estimates=volumes
        )

    def _region_growing_segmentation(self, pixel_data: np.ndarray) -> CardiacSegmentationResult:
        """Region growing segmentation using SimpleITK"""
        # Convert to SimpleITK image
        # sitk_image = sitk.GetImageFromArray(pixel_data.astype(np.float32))  # Not used in current implementation

        # Placeholder implementation - would need proper seed points
        # This is a simplified version
        return self._threshold_segmentation(pixel_data)

    def _deep_learning_segmentation(self, pixel_data: np.ndarray) -> CardiacSegmentationResult:
        """Deep learning-based segmentation (placeholder)"""
        # Placeholder for future deep learning implementation
        logger.info("Deep learning segmentation not yet implemented - using threshold fallback")
        return self._threshold_segmentation(pixel_data)

    def extract_geometry_from_segmentation(self, segmentation: CardiacSegmentationResult,
                                           pixel_spacing: Tuple[float, float, float]) -> Dict[str, RegionalGeometry]:
        """
        Extract geometric parameters from segmentation results

        Args:
            segmentation: Cardiac segmentation results
            pixel_spacing: Voxel spacing in mm

        Returns:
            Regional geometry for each cardiac chamber
        """
        logger.info("📐 Extracting geometry from segmentation")

        geometries = {}

        # Create synthetic masks based on volume data for geometry calculations
        # In a real implementation, these would be the actual segmentation masks
        synthetic_masks = self._create_synthetic_masks_from_volumes(segmentation, pixel_spacing)

        if not synthetic_masks:
            return geometries

        for region in CardiacRegion:
            # Initialize default values
            mask = synthetic_masks.get('myocardium', np.ones((50, 50, 50)))  # Default synthetic mask
            wall_thickness = 8.0  # Default wall thickness
            cavity_volume = 50.0  # Default cavity volume
            surface_area = 100.0  # Default surface area

            if region == CardiacRegion.LEFT_VENTRICLE:
                mask = synthetic_masks.get('left_ventricle', np.ones((40, 40, 40)))
                wall_thickness = 10.0  # mm - typical LV wall thickness
                cavity_volume = segmentation.left_ventricle_volume_ml
                surface_area = self._calculate_surface_area(mask, pixel_spacing)

            elif region == CardiacRegion.RIGHT_VENTRICLE:
                mask = synthetic_masks.get('right_ventricle', np.ones((35, 35, 35)))
                wall_thickness = 4.0  # mm - typical RV wall thickness
                cavity_volume = segmentation.right_ventricle_volume_ml
                surface_area = self._calculate_surface_area(mask, pixel_spacing)

            elif region == CardiacRegion.LEFT_ATRIUM:
                mask = synthetic_masks.get('left_atrium', np.ones((25, 25, 25)))
                wall_thickness = 2.0  # mm - typical LA wall thickness
                cavity_volume = segmentation.left_atrium_volume_ml
                surface_area = self._calculate_surface_area(mask, pixel_spacing)

            elif region == CardiacRegion.RIGHT_ATRIUM:
                mask = synthetic_masks.get('right_atrium', np.ones((25, 25, 25)))
                wall_thickness = 2.5  # mm - typical RA wall thickness
                cavity_volume = segmentation.right_atrium_volume_ml
                surface_area = self._calculate_surface_area(mask, pixel_spacing)

            elif region == CardiacRegion.INTERVENTRICULAR_SEPTUM:
                # Septum doesn't have its own mask, use myocardium
                mask = synthetic_masks.get('myocardium', np.ones((50, 50, 50)))
                wall_thickness = 12.0  # mm - typical septal thickness
                cavity_volume = 0.0  # Septum has no cavity
                surface_area = self._calculate_surface_area(mask, pixel_spacing) * 0.3  # Estimate

            # Estimate fiber orientation (simplified)
            fiber_orientation = self._estimate_fiber_orientation(mask)

            # Regional strain (placeholder - would be calculated from deformation)
            regional_strain = {
                'global': -0.18,
                'longitudinal': -0.20,
                'circumferential': -0.16
            }

            geometries[region] = RegionalGeometry(
                region=region,
                wall_thickness=wall_thickness,
                cavity_volume=cavity_volume,
                surface_area=surface_area,
                fiber_orientation=fiber_orientation,
                regional_strain=regional_strain
            )

        logger.info("✅ Geometry extraction completed")
        return geometries

    def _calculate_surface_area(self, mask: np.ndarray, pixel_spacing: Tuple[float, float, float]) -> float:
        """Calculate surface area of a 3D mask"""
        # Simplified surface area calculation
        # In practice, would use marching cubes or similar
        surface_voxels = 0
        for i in range(1, mask.shape[0] - 1):
            for j in range(1, mask.shape[1] - 1):
                for k in range(1, mask.shape[2] - 1):
                    if mask[i, j, k]:
                        # Check if this is a surface voxel
                        neighbors = mask[i - 1:i + 2, j - 1:j + 2, k - 1:k + 2]
                        if np.sum(neighbors) < 27:  # Not completely surrounded
                            surface_voxels += 1

        # Approximate surface area
        voxel_area = pixel_spacing[0] * pixel_spacing[1]
        return surface_voxels * voxel_area

    def _create_synthetic_masks_from_volumes(self, segmentation: CardiacSegmentationResult, 
                                             pixel_spacing: Tuple[float, float, float]) -> Dict[str, np.ndarray]:
        """
        Create synthetic masks from volume data for geometry calculations
        
        Args:
            segmentation: Cardiac segmentation results with volumes
            pixel_spacing: Voxel spacing in mm
            
        Returns:
            Dictionary of synthetic masks for each cardiac structure
        """

        if any(p == 0 for p in pixel_spacing):
            logger.warning("Pixel spacing contains zero values, cannot create masks.")
            return {}
        
        # Estimate dimensions based on typical cardiac anatomy and volumes
        # This is a simplified approach - in practice, you'd have the actual masks
        
        masks = {}
        
        # Create ellipsoidal masks approximating cardiac chambers
        # Volume = 4/3 * pi * a * b * c for ellipsoid
        
        # Left ventricle (ellipsoid)
        lv_volume_ml = segmentation.left_ventricle_volume_ml
        lv_volume_mm3 = lv_volume_ml * 1000  # Convert mL to mm³
        # Assume aspect ratio typical for LV: length ~ 2x width
        lv_radius = (3 * lv_volume_mm3 / (8 * np.pi)) ** (1/3)  # Simplified calculation
        lv_size = int(lv_radius / pixel_spacing[0])
        lv_mask = self._create_ellipsoid_mask(lv_size, lv_size, 2*lv_size)
        masks['left_ventricle'] = lv_mask
        
        # Right ventricle (crescent shape approximated by ellipsoid)
        rv_volume_ml = segmentation.right_ventricle_volume_ml
        rv_volume_mm3 = rv_volume_ml * 1000
        rv_radius = (3 * rv_volume_mm3 / (8 * np.pi)) ** (1/3)
        rv_size = int(rv_radius / pixel_spacing[0])
        rv_mask = self._create_ellipsoid_mask(rv_size, rv_size, int(1.5*rv_size))
        masks['right_ventricle'] = rv_mask
        
        # Left atrium (smaller ellipsoid)
        la_volume_ml = segmentation.left_atrium_volume_ml
        la_volume_mm3 = la_volume_ml * 1000
        la_radius = (3 * la_volume_mm3 / (8 * np.pi)) ** (1/3)
        la_size = int(la_radius / pixel_spacing[0])
        la_mask = self._create_ellipsoid_mask(la_size, la_size, la_size)
        masks['left_atrium'] = la_mask
        
        # Right atrium (similar to LA)
        ra_volume_ml = segmentation.right_atrium_volume_ml
        ra_volume_mm3 = ra_volume_ml * 1000
        ra_radius = (3 * ra_volume_mm3 / (8 * np.pi)) ** (1/3)
        ra_size = int(ra_radius / pixel_spacing[0])
        ra_mask = self._create_ellipsoid_mask(ra_size, ra_size, ra_size)
        masks['right_atrium'] = ra_mask
        
        # Myocardium (combined LV wall approximation)
        # Assume myocardial volume is roughly 40% of LV cavity volume for wall thickness
        myo_volume_mm3 = segmentation.myocardial_mass_g  # Mass in g ≈ volume in mm³ for myocardium
        myo_thickness = 10.0  # mm - typical LV wall thickness
        myo_size = int((myo_volume_mm3 / (myo_thickness * np.pi)) ** 0.5 / pixel_spacing[0])
        myo_mask = self._create_spherical_shell_mask(myo_size, myo_thickness/pixel_spacing[0])
        masks['myocardium'] = myo_mask
        
        logger.info(f"✅ Created synthetic masks for {len(masks)} cardiac structures")
        return masks
    
    def _create_ellipsoid_mask(self, a: int, b: int, c: int) -> np.ndarray:
        """Create a 3D ellipsoid mask"""
        # Create coordinate grids
        x = np.linspace(-a, a, 2*a+1)
        y = np.linspace(-b, b, 2*b+1)
        z = np.linspace(-c, c, 2*c+1)
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Ellipsoid equation: x²/a² + y²/b² + z²/c² ≤ 1
        mask = (X**2/a**2 + Y**2/b**2 + Z**2/c**2) <= 1
        return mask.astype(np.uint8)
    
    def _create_spherical_shell_mask(self, radius: int, thickness: float) -> np.ndarray:
        """Create a spherical shell mask"""
        size = 2*radius + 1
        center = radius
        
        # Create coordinate grids
        x = np.arange(size) - center
        y = np.arange(size) - center  
        z = np.arange(size) - center
        X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
        
        # Distance from center
        R = np.sqrt(X**2 + Y**2 + Z**2)
        
        # Spherical shell: outer_radius ≥ R ≥ inner_radius
        outer_radius = radius
        inner_radius = max(0, radius - thickness)
        mask = (R <= outer_radius) & (R >= inner_radius)
        
        return mask.astype(np.uint8)

    def _estimate_fiber_orientation(self, mask: np.ndarray) -> np.ndarray:
        """Estimate myocardial fiber orientation from mask"""
        # Simplified fiber orientation estimation
        # In practice, would use DT-MRI or rule-based methods
        return np.array([0.8, 0.6, 0.0])  # Default helical orientation

    def analyze_myocardial_strain(self, image_sequence: np.ndarray,
                                  time_points: List[float]) -> StrainAnalysisResult:
        """
        Analyze myocardial strain from cine imaging sequence

        Args:
            image_sequence: 4D array (time, height, width, slices)
            time_points: Time points for each frame

        Returns:
            Strain analysis results
        """
        logger.info("🔬 Analyzing myocardial strain")

        # Placeholder implementation - would use optical flow or similar
        # This is a simplified version

        global_longitudinal_strain = -0.18
        global_circumferential_strain = -0.16
        global_radial_strain = 0.25

        regional_strain = {
            'left_ventricle': {
                'longitudinal': -0.20,
                'circumferential': -0.18,
                'radial': 0.28
            },
            'right_ventricle': {
                'longitudinal': -0.25,
                'circumferential': -0.22,
                'radial': 0.30
            },
            'left_atrium': {
                'longitudinal': -0.30,
                'circumferential': -0.25,
                'radial': 0.35
            },
            'right_atrium': {
                'longitudinal': -0.28,
                'circumferential': -0.24,
                'radial': 0.32
            }
        }

        return StrainAnalysisResult(
            global_longitudinal_strain=global_longitudinal_strain,
            global_circumferential_strain=global_circumferential_strain,
            global_radial_strain=global_radial_strain,
            strain_quality_score=0.85,  # Placeholder quality score
            regional_strain=regional_strain
        )

    def calibrate_patient_specific_model(self, imaging_data: Dict[str, Any],
                                         segmentation: CardiacSegmentationResult,
                                         strain_analysis: StrainAnalysisResult) -> Dict[str, Any]:
        """
        Calibrate regional cardiac models with patient-specific data

        Args:
            imaging_data: Patient imaging data
            segmentation: Cardiac segmentation results
            strain_analysis: Strain analysis results

        Returns:
            Calibrated patient-specific model parameters
        """
        logger.info("🔧 Calibrating patient-specific cardiac model")

        # Extract patient geometry
        pixel_spacing = imaging_data.get('spacing', (1.0, 1.0, 1.0))
        if len(pixel_spacing) == 2:
            pixel_spacing = pixel_spacing + (1.0,)

        patient_geometries = self.extract_geometry_from_segmentation(
            segmentation, pixel_spacing
        )

        # Calibrate material properties based on strain analysis
        calibrated_properties = {}
        for region, geometry in patient_geometries.items():
            # Ensure region is CardiacRegion enum
            if not isinstance(region, CardiacRegion):
                continue

            # Adjust material properties based on patient-specific strain
            base_props = self.cardiac_service.regional_models[region]['geometry']

            # Strain-based calibration (simplified)
            strain_factor = abs(geometry.regional_strain['global']) / 0.18  # Normalize to reference
            calibrated_props = {
                'region': region,
                'stiffness_modulus': 25.0 * (1.0 + strain_factor),  # Default LV value
                'poisson_ratio': 0.49,
                'density': 1.06,
                'active_stress_max': 80.0 * (1.0 - strain_factor * 0.3),
                'active_stress_slope': 2.0,
                'activation_time_constant': 0.05,
                'relaxation_time_constant': 0.15
            }

            calibrated_properties[region] = calibrated_props

        # Generate comprehensive patient report
        patient_report = {
            'patient_id': imaging_data.get('patient_id', 'UNKNOWN'),
            'study_date': imaging_data.get('study_date', 'UNKNOWN'),
            'geometry': patient_geometries,
            'material_properties': calibrated_properties,
            'strain_analysis': strain_analysis,
            'volume_estimates': segmentation.volume_estimates,
            'segmentation_confidence': segmentation.segmentation_confidence,
            'recommendations': self._generate_patient_recommendations(
                patient_geometries, strain_analysis
            )
        }

        logger.info("✅ Patient-specific model calibration completed")
        return patient_report

    def _generate_patient_recommendations(self, geometries: Dict[str, RegionalGeometry],
                                          strain_analysis: StrainAnalysisResult) -> List[str]:
        """Generate clinical recommendations based on analysis"""
        recommendations = []

        # Check for abnormal strain values
        if abs(strain_analysis.global_longitudinal_strain) < 0.15:
            recommendations.append("Reduced global longitudinal strain detected - consider further evaluation")

        if strain_analysis.global_radial_strain < 0.20:
            recommendations.append("Reduced radial strain suggests impaired contractility")

        # Check for regional wall motion abnormalities
        for region, geometry in geometries.items():
            if abs(geometry.regional_strain['global']) < 0.10:
                recommendations.append(f"Reduced strain in {region.value} - possible wall motion abnormality")

        if not recommendations:
            recommendations.append("Cardiac function appears within normal limits")

        return recommendations

    def generate_report(self, patient_data: Dict[str, Any]) -> str:
        """Generate comprehensive patient report"""
        report = f"""
CARDIAC IMAGING ANALYSIS REPORT
================================

Patient ID: {patient_data['patient_id']}
Study Date: {patient_data['study_date']}

VOLUME ANALYSIS:
- Left Ventricle: {patient_data['volume_estimates']['left_ventricle']:.1f} mL
- Right Ventricle: {patient_data['volume_estimates']['right_ventricle']:.1f} mL
- Left Atrium: {patient_data['volume_estimates']['left_atrium']:.1f} mL
- Right Atrium: {patient_data['volume_estimates']['right_atrium']:.1f} mL
- Myocardium: {patient_data['volume_estimates']['myocardium']:.1f} mL

STRAIN ANALYSIS:
- Global Longitudinal Strain: {patient_data['strain_analysis'].global_longitudinal_strain:.2f}
- Global Circumferential Strain: {patient_data['strain_analysis'].global_circumferential_strain:.2f}
- Global Radial Strain: {patient_data['strain_analysis'].global_radial_strain:.2f}

CLINICAL RECOMMENDATIONS:
"""
        for rec in patient_data['recommendations']:
            report += f"- {rec}\n"

        return report

    def analyze_cardiac_strain(self, image_data: Dict[str, Any]) -> StrainAnalysisResult:
        """
        Analyze cardiac strain from imaging data (wrapper for analyze_myocardial_strain)
        
        Args:
            image_data: Image data with pixel data and metadata
            
        Returns:
            Strain analysis results
        """
        logger.info("🔬 Analyzing cardiac strain")
        
        # Extract pixel data and create synthetic time points if needed
        pixel_data = image_data.get('pixel_data', np.zeros((1, 64, 64)))
        
        # If 3D data, add time dimension
        if len(pixel_data.shape) == 3:
            # Create synthetic time series (simulate cardiac cycle)
            time_points = np.linspace(0, 1.0, pixel_data.shape[0])
            # Use the first slice as a simple approximation
            image_sequence = pixel_data[:, :, :, np.newaxis] if len(pixel_data.shape) == 3 else pixel_data
        else:
            # Create simple time series
            time_points = [0.0, 0.5, 1.0]
            image_sequence = np.stack([pixel_data] * 3, axis=0)
        
        # Call the main strain analysis method
        return self.analyze_myocardial_strain(image_sequence, time_points.tolist() if hasattr(time_points, 'tolist') else list(time_points))


# Global instance for convenience
medical_imaging_service = MedicalImagingService()