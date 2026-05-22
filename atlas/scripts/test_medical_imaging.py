#!/usr/bin/env python3
"""
Test script for medical imaging services
"""

import sys
import os

# Add atlas to path
sys.path.insert(0, '.')

# Import required modules directly
import numpy as np
from typing import Dict, Any

# Import from the specific files
from app.domains.medicine.imaging.medical_imaging_types import (
    MedicalImage, DICOMMetadata, CardiacSegmentationResult, StrainAnalysisResult,
    ImagingModality, CardiacView
)

# Import service directly
from app.domains.medicine.imaging.medical_imaging_service import MedicalImagingService

def test_medical_imaging():
    """Test medical imaging functionality"""
    print('🧪 Testing medical imaging services...')
    
    # Create service
    service = MedicalImagingService()
    
    # Test 1: Create synthetic cardiac image
    print('\\n📊 Creating synthetic cardiac image...')
    x, y, z = np.mgrid[-32:32, -32:32, -16:16]
    ellipsoid = ((x/20)**2 + (y/15)**2 + (z/12)**2) < 1
    
    synthetic_image = {
        'pixel_data': ellipsoid.astype(np.uint8) * 255,
        'metadata': {'test': 'synthetic_cardiac'},
        'spacing': (1.0, 1.0, 1.0),
        'origin': (0.0, 0.0, 0.0),
        'direction': (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
        'dimensions': (64, 64, 32)
    }
    
    # Test 2: Cardiac chamber segmentation
    print('\\n🔍 Testing cardiac chamber segmentation...')
    try:
        segmentation_result = service.segment_cardiac_chambers(synthetic_image)
        print(f'✅ Segmentation completed:')
        print(f'   - Left ventricle volume: {segmentation_result.left_ventricle_volume_ml:.1f} mL')
        print(f'   - Right ventricle volume: {segmentation_result.right_ventricle_volume_ml:.1f} mL')
        print(f'   - Myocardial mass: {segmentation_result.myocardial_mass_g:.1f} g')
        print(f'   - Ejection fraction: {segmentation_result.ejection_fraction_percent:.1f}%')
        print(f'   - Quality score: {segmentation_result.segmentation_quality_score:.2f}')
        print(f'   - Confidence scores: {segmentation_result.segmentation_confidence}')
        
    except Exception as e:
        print(f'⚠️  Segmentation test failed: {e}')
    
    # Test 3: Cardiac strain analysis
    print('\\n🔬 Testing strain analysis...')
    try:
        strain_result = service.analyze_cardiac_strain(synthetic_image)
        print(f'✅ Strain analysis completed:')
        print(f'   - Global longitudinal strain: {strain_result.global_longitudinal_strain:.2f}')
        print(f'   - Global circumferential strain: {strain_result.global_circumferential_strain:.2f}')
        print(f'   - Global radial strain: {strain_result.global_radial_strain:.2f}')
        print(f'   - Quality score: {strain_result.strain_quality_score:.2f}')
        
    except Exception as e:
        print(f'⚠️  Strain analysis test failed: {e}')
    
    # Test 4: Create MedicalImage object
    print('\\n🖼️  Testing MedicalImage creation...')
    try:
        # Create a simple 2D image
        pixel_data = np.random.rand(128, 128).astype(np.float32)
        
        medical_image = MedicalImage(
            pixel_data=pixel_data,
            metadata={'patient_id': 'test_patient', 'scan_date': '2024-01-01'},
            modality=ImagingModality.MRI,
            spacing=(1.0, 1.0),
            origin=(0.0, 0.0),
            direction=(1.0, 0.0, 0.0, 1.0)
        )
        
        print(f'✅ MedicalImage created:')
        print(f'   - Shape: {medical_image.shape}')
        print(f'   - Data type: {medical_image.dtype}')
        print(f'   - Modality: {medical_image.modality.value}')
        print(f'   - Spacing: {medical_image.spacing}')
        
    except Exception as e:
        print(f'⚠️  MedicalImage test failed: {e}')
    
    print('\\n🎉 Medical imaging tests completed!')

if __name__ == '__main__':
    test_medical_imaging()