"""
Test suite for Advanced Medical Imaging Service
Tests enhanced DICOM/NIfTI processing, clinical validation, and medical imaging integration.
"""

import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json

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
from app.domains.medicine.imaging.medical_imaging_service import CardiacSegmentationResult
from app.domains.medicine.imaging.medical_imaging_types import DICOMMetadata


class TestAdvancedMedicalImagingService:
    """Test suite for Advanced Medical Imaging Service"""

    @pytest.fixture
    def service(self):
        """Create a fresh AdvancedMedicalImagingService instance for each test"""
        return AdvancedMedicalImagingService()

    @pytest.fixture
    def mock_dicom_path(self):
        """Create a mock DICOM file path"""
        return Path("/mock/path/test.dcm")

    @pytest.fixture
    def mock_nifti_path(self):
        """Create a mock NIfTI file path"""
        return Path("/mock/path/test.nii.gz")

    @pytest.fixture
    def mock_segmentation_result(self):
        """Create mock segmentation result for testing"""
        return CardiacSegmentationResult(
            left_ventricle_volume_ml=120.0,
            right_ventricle_volume_ml=100.0,
            left_atrium_volume_ml=80.0,
            right_atrium_volume_ml=60.0,
            myocardial_mass_g=150.0,
            ejection_fraction_percent=55.0,
            segmentation_quality_score=0.85,
            segmentation_confidence={
                'left_ventricle': 0.85,
                'right_ventricle': 0.80,
                'left_atrium': 0.75,
                'right_atrium': 0.70,
                'myocardium': 0.90
            },
            volume_estimates={
                'left_ventricle': 120.0,
                'right_ventricle': 100.0,
                'left_atrium': 80.0,
                'right_atrium': 60.0,
                'myocardium': 150.0
            }
        )

    def test_initialization(self, service):
        """Test service initialization"""
        assert service.base_service is not None
        assert isinstance(service.supported_formats, dict)
        assert '.dcm' in service.supported_formats
        assert '.nii' in service.supported_formats
        assert service.validation_thresholds['dice_coefficient'] == 0.85

    @patch('app.advanced_medical_imaging_service.Path.exists')
    @patch('app.advanced_medical_imaging_service.sitk.ImageFileReader')
    def test_load_dicom_enhanced_success(self, mock_reader_class, mock_exists, service, mock_dicom_path):
        """Test successful enhanced DICOM loading"""
        mock_exists.return_value = True

        # Mock SimpleITK reader
        mock_reader = MagicMock()
        mock_image = MagicMock()
        mock_image.GetArrayFromImage.return_value = np.random.randint(0, 4096, (64, 64, 10), dtype=np.uint16)
        mock_image.GetSpacing.return_value = (1.5, 1.5, 2.0)
        mock_image.GetOrigin.return_value = (0.0, 0.0, 0.0)
        mock_image.GetDirection.return_value = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        mock_reader.Execute.return_value = mock_image
        mock_reader_class.return_value = mock_reader

        with patch('app.advanced_medical_imaging_service.pydicom.dcmread') as mock_dcmread:
            mock_dicom = MagicMock()
            mock_dicom.PatientID = 'TEST001'
            mock_dicom.StudyDate = '20240908'
            mock_dicom.SeriesDescription = 'Cardiac CT'
            mock_dicom.Modality = 'CT'
            mock_dicom.SliceThickness = '2.0'
            mock_dicom.PixelSpacing = [1.5, 1.5]
            mock_dicom.Rows = 64
            mock_dicom.Columns = 64
            mock_dicom.NumberOfFrames = 10
            mock_dicom.HeartRate = 70
            mock_dcmread.return_value = mock_dicom

            result = service.load_medical_image_enhanced(str(mock_dicom_path))

            assert 'pixel_data' in result
            assert 'metadata' in result
            assert result['modality'] == ImageModality.CT
            assert result['clinical_standard'] == ClinicalStandard.DICOM

    @patch('app.advanced_medical_imaging_service.Path.exists')
    @patch('app.advanced_medical_imaging_service.nib.load')
    def test_load_nifti_enhanced_success(self, mock_nib_load, mock_exists, service, mock_nifti_path):
        """Test successful enhanced NIfTI loading"""
        mock_exists.return_value = True

        # Mock nibabel
        mock_img = MagicMock()
        mock_img.get_fdata.return_value = np.random.rand(64, 64, 20)
        mock_img.header.get_zooms.return_value = (1.0, 1.0, 2.0)
        mock_img.header.get_data_shape.return_value = (64, 64, 20)
        mock_img.header.get_data_dtype.return_value = np.float32
        mock_img.header.get_intent_name.return_value = 'T1'
        mock_img.header.get_descrip.return_value = 'T1 weighted'
        mock_img.affine = np.eye(4)
        mock_img.extensions = []
        mock_nib_load.return_value = mock_img

        result = service.load_medical_image_enhanced(str(mock_nifti_path))

        assert 'pixel_data' in result
        assert 'metadata' in result
        assert result['modality'] == ImageModality.MRI
        assert result['clinical_standard'] == ClinicalStandard.NIFTI
        assert isinstance(result['metadata'], NIFTIMetadata)

    def test_detect_modality(self, service):
        """Test modality auto-detection"""
        dicom_metadata = DICOMMetadata(
            patient_id='TEST001',
            study_date='20240908',
            series_description='Cardiac MRI',
            modality='MR',
            slice_thickness=2.0,
            pixel_spacing=(1.5, 1.5),
            image_dimensions=(64, 64),
            number_of_frames=20
        )

        modality = service._detect_modality(dicom_metadata)
        assert modality == ImageModality.MRI

        # Test with dict
        modality = service._detect_modality({'modality': 'CT'})
        assert modality == ImageModality.CT

    def test_assess_image_quality(self, service):
        """Test image quality assessment"""
        pixel_data = np.random.rand(64, 64, 10)

        quality = service._assess_image_quality(pixel_data, {'modality': 'MRI'})

        assert 'snr' in quality
        assert 'cnr' in quality
        assert 'uniformity' in quality
        assert 'dynamic_range' in quality

    def test_validate_clinical_accuracy_self_validation(self, service, mock_segmentation_result):
        """Test self-validation of segmentation"""
        metrics = service.validate_clinical_accuracy(mock_segmentation_result)

        assert isinstance(metrics, ClinicalValidationMetrics)
        assert metrics.validator_id == "clinical_heuristics"
        assert 0.0 <= metrics.clinical_accuracy_score <= 1.0

    def test_validate_clinical_accuracy_with_ground_truth(self, service, mock_segmentation_result):
        """Test validation against ground truth"""
        ground_truth = {
            'left_ventricle': np.random.randint(0, 2, (64, 64, 20), dtype=np.uint8),
            'right_ventricle': np.random.randint(0, 2, (64, 64, 20), dtype=np.uint8)
        }

        metrics = service.validate_clinical_accuracy(mock_segmentation_result, ground_truth)

        assert isinstance(metrics, ClinicalValidationMetrics)
        assert metrics.validator_id == "ground_truth_validation"
        assert 0.0 <= metrics.dice_coefficient <= 1.0

    def test_calculate_dice_coefficient(self, service):
        """Test Dice coefficient calculation"""
        pred = np.array([1, 1, 0, 0])
        gt = np.array([1, 0, 0, 0])

        dice = service._calculate_dice_coefficient(pred, gt)
        expected = 2 * 1 / (2 + 1)  # 2 * intersection / (pred_sum + gt_sum)
        assert abs(dice - expected) < 1e-6

        # Test empty masks
        dice = service._calculate_dice_coefficient(np.zeros(4), np.zeros(4))
        assert dice == 1.0

    def test_generate_clinical_validation_report(self, service):
        """Test clinical validation report generation"""
        metrics = ClinicalValidationMetrics(
            dice_coefficient=0.87,
            hausdorff_distance=2.3,
            mean_surface_distance=1.8,
            volume_difference=0.12,
            clinical_accuracy_score=0.91
        )

        patient_info = {'patient_id': 'TEST001'}

        report = service.generate_clinical_validation_report(metrics, patient_info)

        assert 'TEST001' in report
        assert '0.870' in report
        assert '2.3' in report
        assert '91.0%' in report
        assert '✅ ACEPTADO' in report

    def test_export_to_fhir(self, service):
        """Test FHIR export"""
        patient_data = {
            'patient_id': 'TEST001',
            'name': 'John Doe'
        }

        fhir_data = service._export_to_fhir(patient_data)
        fhir_json = json.loads(fhir_data)

        assert fhir_json['resourceType'] == 'Bundle'
        assert len(fhir_json['entry']) >= 1

    def test_export_to_hl7(self, service):
        """Test HL7 export"""
        patient_data = {
            'patient_id': 'TEST001',
            'validation': {'dice_coefficient': 0.85},
            'volumes': {'left_ventricle': 120.0}
        }

        hl7_data = service._export_to_hl7(patient_data)

        assert 'MSH|' in hl7_data
        assert 'TEST001' in hl7_data
        assert 'CARDIAC_001' in hl7_data

    @patch('app.advanced_medical_imaging_service.Path.exists')
    def test_load_medical_image_enhanced_file_not_found(self, mock_exists, service):
        """Test handling of non-existent files"""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            service.load_medical_image_enhanced("/nonexistent/file.dcm")

    def test_load_medical_image_enhanced_unsupported_format(self, service):
        """Test handling of unsupported file formats"""
        with patch('app.advanced_medical_imaging_service.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.suffix.lower.return_value = '.unsupported'

            with pytest.raises(ValueError, match="Unsupported format"):
                service.load_medical_image_enhanced("/mock/file.unsupported")

    def test_convenience_functions(self, mock_segmentation_result):
        """Test convenience functions"""
        # Test load_medical_image_enhanced function
        with patch.object(advanced_medical_imaging_service, 'load_medical_image_enhanced') as mock_load:
            mock_load.return_value = {'test': 'data'}
            load_medical_image_enhanced("/test/path.dcm")
            mock_load.assert_called_once_with("/test/path.dcm", None)

        # Test validate_clinical_accuracy function
        with patch.object(advanced_medical_imaging_service, 'validate_clinical_accuracy') as mock_validate:
            mock_validate.return_value = ClinicalValidationMetrics()
            validate_clinical_accuracy(mock_segmentation_result)
            mock_validate.assert_called_once_with(mock_segmentation_result, None)


class TestClinicalValidationMetrics:
    """Test suite for ClinicalValidationMetrics dataclass"""

    def test_initialization(self):
        """Test ClinicalValidationMetrics initialization"""
        metrics = ClinicalValidationMetrics()

        assert metrics.dice_coefficient == 0.0
        assert metrics.hausdorff_distance == 0.0
        assert metrics.mean_surface_distance == 0.0
        assert metrics.volume_difference == 0.0
        assert metrics.clinical_accuracy_score == 0.0
        assert metrics.inter_observer_variability == 0.0
        assert isinstance(metrics.validation_date, type(metrics.validation_date))  # datetime

    def test_custom_initialization(self):
        """Test ClinicalValidationMetrics with custom values"""
        from datetime import datetime
        custom_date = datetime(2024, 9, 8)

        metrics = ClinicalValidationMetrics(
            dice_coefficient=0.85,
            hausdorff_distance=2.5,
            mean_surface_distance=1.8,
            volume_difference=0.10,
            clinical_accuracy_score=0.92,
            inter_observer_variability=0.05,
            validation_date=custom_date
        )

        assert metrics.dice_coefficient == 0.85
        assert metrics.hausdorff_distance == 2.5
        assert metrics.validation_date == custom_date


class TestNIFTIMetadata:
    """Test suite for NIFTIMetadata dataclass"""

    def test_initialization(self):
        """Test NIFTIMetadata initialization"""
        affine = np.eye(4)
        header = {'test': 'value'}
        voxel_sizes = (1.0, 1.0, 2.0)
        data_shape = (64, 64, 20)
        data_type = 'float32'

        metadata = NIFTIMetadata(
            affine=affine,
            header=header,
            voxel_sizes=voxel_sizes,
            data_shape=data_shape,
            data_type=data_type,
            intent_name='T1',
            description='T1 weighted image',
            clinical_metadata={'Modality': 'MRI'}
        )

        assert np.array_equal(metadata.affine, affine)
        assert metadata.header == header
        assert metadata.voxel_sizes == voxel_sizes
        assert metadata.intent_name == 'T1'
        assert metadata.clinical_metadata == {'Modality': 'MRI'}
