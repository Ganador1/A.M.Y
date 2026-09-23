#!/usr/bin/env python3
"""
Unit Tests for Advanced Clinical Validation Service - AXIOM META 4
==================================================================

Tests for advanced clinical validation including:
- EF calculation methods
- Strain validation
- Clinical reporting
- Risk assessment
"""

import pytest
import numpy as np
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.advanced_clinical_validation_service import (
    AdvancedClinicalValidationService
)


class TestAdvancedClinicalValidationService:
    """Test suite for Advanced Clinical Validation Service"""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test"""
        return AdvancedClinicalValidationService()

    @pytest.fixture
    def sample_cardiac_data(self):
        """Sample cardiac data for testing"""
        return {
            'volumes': {
                'edv': 150.0,  # mL
                'esv': 60.0,   # mL
                'sv': 90.0     # mL
            },
            'strain_data': {
                'global_longitudinal_strain': -18.5,
                'regional_strains': np.random.normal(-18, 3, 17),  # 17 AHA segments
                'strain_rate': -1.2
            },
            'timing': {
                'heart_rate': 70,
                'rr_interval': 850,  # ms
                'contraction_time': 300  # ms
            }
        }

    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service.logger is not None
        assert hasattr(service, 'calculate_ejection_fraction')
        assert hasattr(service, 'validate_strain_measurements')
        assert hasattr(service, 'generate_clinical_report')

    def test_ejection_fraction_methods(self, service, sample_cardiac_data):
        """Test different EF calculation methods"""
        volumes = sample_cardiac_data['volumes']

        # Test Simpson method
        ef_simpson = service._calculate_ef_simpson(volumes['edv'], volumes['esv'])
        expected_ef = (volumes['edv'] - volumes['esv']) / volumes['edv']
        assert abs(ef_simpson - expected_ef) < 0.01

        # Test area-length method
        ef_al = service._calculate_ef_area_length(volumes['edv'], volumes['esv'])
        assert abs(ef_al - expected_ef) < 0.01

        # Test Teichholz method
        ef_teichholz = service._calculate_ef_teichholz(volumes['edv'], volumes['esv'])
        assert abs(ef_teichholz - expected_ef) < 0.05  # More tolerance for empirical methods

    def test_strain_validation(self, service, sample_cardiac_data):
        """Test strain validation methods"""
        strain_data = sample_cardiac_data['strain_data']

        # Test global strain validation
        global_validation = service._validate_global_strain(strain_data['global_longitudinal_strain'])
        assert 'is_normal' in global_validation
        assert 'confidence' in global_validation

        # Test regional strain validation
        regional_validation = service._validate_regional_strains(strain_data['regional_strains'])
        assert 'homogeneity_index' in regional_validation
        assert 'abnormal_segments' in regional_validation

    def test_ventricular_function_analysis(self, service, sample_cardiac_data):
        """Test ventricular function analysis"""
        analysis = service._analyze_ventricular_function(sample_cardiac_data)

        assert 'ef_assessment' in analysis
        assert 'strain_assessment' in analysis
        assert 'overall_function' in analysis
        assert 'risk_factors' in analysis

    def test_clinical_report_generation(self, service, sample_cardiac_data):
        """Test clinical report generation"""
        report = service._generate_clinical_report(sample_cardiac_data)

        assert isinstance(report, str)
        assert len(report) > 100  # Should be a substantial report
        assert 'EF' in report.upper()
        assert 'STRAIN' in report.upper()

    def test_risk_assessment(self, service, sample_cardiac_data):
        """Test risk assessment functionality"""
        risk_assessment = service._assess_cardiac_risk(sample_cardiac_data)

        assert 'risk_level' in risk_assessment
        assert 'risk_factors' in risk_assessment
        assert 'recommendations' in risk_assessment
        assert risk_assessment['risk_level'] in ['low', 'moderate', 'high', 'critical']

    def test_complete_validation_workflow(self, service, sample_cardiac_data):
        """Test complete validation workflow"""
        # Test that main validation method exists
        assert hasattr(service, 'validate_cardiac_function')

        # Test workflow components
        assert hasattr(service, '_validate_input_data')
        assert hasattr(service, '_perform_comprehensive_analysis')
        assert hasattr(service, '_generate_validation_summary')

    def test_data_structures(self):
        """Test data structures and enums"""
        # Test that required data structures exist
        from app.advanced_clinical_validation_service import (
            CardiacFunctionMetrics
        )

        # Test dataclass instantiation
        metrics = CardiacFunctionMetrics()
        assert hasattr(metrics, 'ef_simpson')
        assert hasattr(metrics, 'ef_area_length')
        assert hasattr(metrics, 'global_strain')

    def test_validation_algorithms(self, service):
        """Test validation algorithms"""
        assert hasattr(service, '_validate_measurement_consistency')
        assert hasattr(service, '_detect_artifacts')
        assert hasattr(service, '_assess_measurement_quality')

    def test_export_functionality(self, service):
        """Test export functionality"""
        assert hasattr(service, 'export_validation_results')

    def test_helper_functions(self, service):
        """Test helper functions availability"""
        assert hasattr(service, '_calculate_confidence_intervals')
        assert hasattr(service, '_normalize_measurements')
        assert hasattr(service, '_compare_to_normative_data')


if __name__ == "__main__":
    pytest.main([__file__])
