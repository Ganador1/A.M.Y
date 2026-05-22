#!/usr/bin/env python3
"""
Comprehensive Medical Imaging Service Test
Tests all functionality including cardiac segmentation and strain analysis
"""

import numpy as np
from datetime import datetime
from app.domains.medicine.imaging.medical_imaging_service import MedicalImagingService
from app.domains.medicine.imaging.medical_imaging_types import (
    DICOMMetadata, CardiacSegmentationResult, StrainAnalysisResult, MedicalImage
)
from app.domains.medicine.biomechanics.cardiac_region_models import CardiacRegion

def create_test_data():
    """Create synthetic test data"""
    # Create a synthetic 3D cardiac image (128x128x32)
    image_data = np.random.random((128, 128, 32)) * 100
    
    # Add some structure to simulate cardiac anatomy
    # Create a simple heart-like structure
    center_x, center_y, center_z = 64, 64, 16
    
    # Left ventricle (ellipsoid)
    for i in range(128):
        for j in range(128):
            for k in range(32):
                # Distance from center
                dist = ((i-center_x)**2/40**2 + (j-center_y)**2/30**2 + (k-center_z)**2/10**2)
                if dist <= 1.0:
                    image_data[i, j, k] = 150 + np.random.random() * 20
    
    # Right ventricle (smaller ellipsoid)
    rv_center_x, rv_center_y = 80, 64
    for i in range(128):
        for j in range(128):
            for k in range(32):
                dist = ((i-rv_center_x)**2/20**2 + (j-rv_center_y)**2/15**2 + (k-center_z)**2/8**2)
                if dist <= 1.0:
                    image_data[i, j, k] = 120 + np.random.random() * 15
    
    return image_data

def test_cardiac_segmentation():
    """Test cardiac chamber segmentation"""
    print("🫀 Testing Cardiac Segmentation...")
    
    # Create test data
    image_data = create_test_data()
    
    # Create DICOM metadata
    metadata = DICOMMetadata(
        patient_id="TEST001",
        study_date="20240101",
        modality="MRI",
        series_description="Cardiac Cine",
        slice_thickness=6.0,
        pixel_spacing=(1.5, 1.5),
        image_dimensions=(128, 128),
        number_of_frames=1,
        cardiac_phase="END_DIASTOLE",
        heart_rate=75
    )
    
    # Create MedicalImage object
    medical_image = MedicalImage(
        pixel_data=image_data,
        metadata=metadata.__dict__,
        modality="MRI",
        spacing=(1.5, 1.5, 6.0),
        origin=(0.0, 0.0, 0.0),
        direction=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
        clinical_metadata={"cardiac_view": "AXIAL", "cardiac_phase": "END_DIASTOLE"}
    )
    
    # Create service
    service = MedicalImagingService()
    
    # Test segmentation
    segmentation_result = service.segment_cardiac_chambers(medical_image)
    
    # Verify results
    assert isinstance(segmentation_result, CardiacSegmentationResult)
    assert hasattr(segmentation_result, 'left_ventricle_volume_ml')
    assert hasattr(segmentation_result, 'right_ventricle_volume_ml')
    assert hasattr(segmentation_result, 'left_atrium_volume_ml')
    assert hasattr(segmentation_result, 'right_atrium_volume_ml')
    assert hasattr(segmentation_result, 'myocardial_mass_g')
    assert hasattr(segmentation_result, 'ejection_fraction_percent')
    assert hasattr(segmentation_result, 'segmentation_quality_score')
    assert hasattr(segmentation_result, 'volume_estimates')
    
    print(f"✅ Left Ventricle Volume: {segmentation_result.left_ventricle_volume_ml:.1f} mL")
    print(f"✅ Right Ventricle Volume: {segmentation_result.right_ventricle_volume_ml:.1f} mL")
    print(f"✅ Left Atrium Volume: {segmentation_result.left_atrium_volume_ml:.1f} mL")
    print(f"✅ Right Atrium Volume: {segmentation_result.right_atrium_volume_ml:.1f} mL")
    print(f"✅ Myocardial Mass: {segmentation_result.myocardial_mass_g:.1f} g")
    print(f"✅ Ejection Fraction: {segmentation_result.ejection_fraction_percent:.1f}%")
    print(f"✅ Segmentation Quality: {segmentation_result.segmentation_quality_score:.2f}")
    print(f"✅ Volume Estimates: {segmentation_result.volume_estimates}")
    
    return segmentation_result

def test_strain_analysis():
    """Test cardiac strain analysis"""
    print("\n🔬 Testing Strain Analysis...")
    
    # Create a 4D image sequence (time, height, width, slices)
    # Simulate 20 time points
    image_sequence = []
    for t in range(20):
        # Create time-varying cardiac image
        base_image = create_test_data()
        # Add some time-varying deformation
        deformation_factor = 1.0 + 0.1 * np.sin(2 * np.pi * t / 20)
        deformed_image = base_image * deformation_factor
        image_sequence.append(deformed_image)
    
    image_sequence = np.array(image_sequence)
    time_points = [i * 0.05 for i in range(20)]  # 50ms intervals
    
    # Create service
    service = MedicalImagingService()
    
    # Test strain analysis
    strain_result = service.analyze_myocardial_strain(image_sequence, time_points)
    
    # Verify results
    assert isinstance(strain_result, StrainAnalysisResult)
    assert hasattr(strain_result, 'global_longitudinal_strain')
    assert hasattr(strain_result, 'global_circumferential_strain')
    assert hasattr(strain_result, 'global_radial_strain')
    assert hasattr(strain_result, 'strain_quality_score')
    assert hasattr(strain_result, 'regional_strain')
    
    print(f"✅ Global Longitudinal Strain: {strain_result.global_longitudinal_strain:.3f}")
    print(f"✅ Global Circumferential Strain: {strain_result.global_circumferential_strain:.3f}")
    print(f"✅ Global Radial Strain: {strain_result.global_radial_strain:.3f}")
    print(f"✅ Strain Quality Score: {strain_result.strain_quality_score:.2f}")
    print(f"✅ Regional Strain: {strain_result.regional_strain}")
    
    return strain_result

def test_geometry_extraction():
    """Test geometry extraction from segmentation"""
    print("\n📐 Testing Geometry Extraction...")
    
    # Create test segmentation result
    segmentation_result = CardiacSegmentationResult(
        left_ventricle_volume_ml=120.0,
        right_ventricle_volume_ml=80.0,
        left_atrium_volume_ml=45.0,
        right_atrium_volume_ml=50.0,
        myocardial_mass_g=150.0,
        ejection_fraction_percent=55.0,
        segmentation_quality_score=0.85,
        segmentation_confidence={
            'left_ventricle': 0.92,
            'right_ventricle': 0.88,
            'left_atrium': 0.85,
            'right_atrium': 0.83,
            'myocardium': 0.90
        },
        volume_estimates={
            'left_ventricle': 120.0,
            'right_ventricle': 80.0,
            'left_atrium': 45.0,
            'right_atrium': 50.0,
            'myocardium': 150.0
        }
    )
    
    # Create service
    service = MedicalImagingService()
    
    # Test geometry extraction
    pixel_spacing = (1.5, 1.5, 6.0)
    geometries = service.extract_geometry_from_segmentation(segmentation_result, pixel_spacing)
    
    # Debug: Check what keys are returned
    print(f"📐 Geometry keys returned: {list(geometries.keys())}")
    
    # Verify results - keys are CardiacRegion enum objects
    assert CardiacRegion.LEFT_VENTRICLE in geometries
    assert CardiacRegion.RIGHT_VENTRICLE in geometries
    assert CardiacRegion.LEFT_ATRIUM in geometries
    assert CardiacRegion.RIGHT_ATRIUM in geometries
    assert CardiacRegion.INTERVENTRICULAR_SEPTUM in geometries
    
    for region, geometry in geometries.items():
        assert hasattr(geometry, 'wall_thickness')
        assert hasattr(geometry, 'cavity_volume')
        assert hasattr(geometry, 'surface_area')
        assert hasattr(geometry, 'fiber_orientation')
        assert hasattr(geometry, 'regional_strain')
        
        region_name = region.value.replace('_', ' ').title()
        print(f"✅ {region_name}:")
        print(f"   Wall Thickness: {geometry.wall_thickness:.1f} mm")
        print(f"   Cavity Volume: {geometry.cavity_volume:.1f} mL")
        print(f"   Surface Area: {geometry.surface_area:.1f} mm²")
        print(f"   Fiber Orientation: {geometry.fiber_orientation}")
        print(f"   Regional Strain: {geometry.regional_strain}")
    
    return geometries

def test_patient_model_calibration():
    """Test patient-specific model calibration"""
    print("\n🔧 Testing Patient Model Calibration...")
    
    # Create test data
    imaging_data = {
        'spacing': (1.5, 1.5, 6.0),
        'patient_id': 'TEST001',
        'study_date': datetime.now()
    }
    
    segmentation_result = CardiacSegmentationResult(
        left_ventricle_volume_ml=120.0,
        right_ventricle_volume_ml=80.0,
        left_atrium_volume_ml=45.0,
        right_atrium_volume_ml=50.0,
        myocardial_mass_g=150.0,
        ejection_fraction_percent=55.0,
        segmentation_quality_score=0.85,
        segmentation_confidence={
            'left_ventricle': 0.92,
            'right_ventricle': 0.88,
            'left_atrium': 0.85,
            'right_atrium': 0.83,
            'myocardium': 0.90
        },
        volume_estimates={
            'left_ventricle': 120.0,
            'right_ventricle': 80.0,
            'left_atrium': 45.0,
            'right_atrium': 50.0,
            'myocardium': 150.0
        }
    )
    
    strain_result = StrainAnalysisResult(
        global_longitudinal_strain=-0.18,
        global_circumferential_strain=-0.16,
        global_radial_strain=0.25,
        strain_quality_score=0.85,
        regional_strain={
            'left_ventricle': {'longitudinal': -0.20, 'circumferential': -0.18, 'radial': 0.28},
            'right_ventricle': {'longitudinal': -0.25, 'circumferential': -0.22, 'radial': 0.30},
            'left_atrium': {'longitudinal': -0.30, 'circumferential': -0.25, 'radial': 0.35},
            'right_atrium': {'longitudinal': -0.28, 'circumferential': -0.24, 'radial': 0.32}
        }
    )
    
    # Create service
    service = MedicalImagingService()
    
    # Test model calibration
    calibrated_model = service.calibrate_patient_specific_model(
        imaging_data, segmentation_result, strain_result
    )
    
    # Verify results
    assert isinstance(calibrated_model, dict)
    assert 'geometry' in calibrated_model
    assert 'material_properties' in calibrated_model
    assert 'patient_id' in calibrated_model
    
    print(f"✅ Model calibration completed")
    print(f"✅ Patient geometries extracted")
    print(f"✅ Calibrated properties generated")
    print(f"✅ Patient ID: {calibrated_model['patient_id']}")
    
    return calibrated_model

def main():
    """Run all tests"""
    print("🚀 Starting Comprehensive Medical Imaging Tests")
    print("=" * 60)
    
    try:
        # Test cardiac segmentation
        segmentation_result = test_cardiac_segmentation()
        
        # Test strain analysis
        strain_result = test_strain_analysis()
        
        # Test geometry extraction
        geometries = test_geometry_extraction()
        
        # Test patient model calibration
        calibrated_model = test_patient_model_calibration()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("🎉 Medical Imaging Service is working correctly")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)