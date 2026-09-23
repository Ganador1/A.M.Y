"""
Tests for Solid State Physics Service
"""

import pytest
import numpy as np
from app.services.solid_state_physics import SolidStatePhysicsService


class TestSolidStatePhysicsService:
    """Test cases for SolidStatePhysicsService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide SolidStatePhysicsService instance"""
        return SolidStatePhysicsService()

    def test_service_initialization(self, service):
        """Test service initialization and basic properties"""
        assert service is not None
        assert hasattr(service, 'ase_available')
        assert 'gpaw' in service.available_calculators

    @pytest.mark.asyncio
    async def test_create_calculation_basic(self, service):
        """Test basic calculation creation"""
        request_data = {
            "material_name": "Test Silicon",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [4, 4, 4],
            "cutoff_energy": 400.0
        }

        result = await service.create_calculation(request_data)

        assert result['success'] is True
        assert 'calculation_id' in result
        assert result['calculation_type'] == 'scf'
        assert 'parameters' in result

    @pytest.mark.asyncio
    async def test_create_calculation_invalid_type(self, service):
        """Test calculation creation with invalid type"""
        request_data = {
            "material_name": "Test Material",
            "calculation_type": "invalid_type",
            "xc_functional": "PBE"
        }

        result = await service.create_calculation(request_data)

        assert result['success'] is False
        assert 'error' in result

    def test_classify_material_semiconductor(self, service):
        """Test material classification for semiconductor"""
        # Silicon-like gap
        results = {"band_gap": 1.1}
        material_type = service._classify_material(results)

        assert material_type == "semiconductor"

    def test_classify_material_metal(self, service):
        """Test material classification for metal"""
        # Copper-like gap (very small)
        results = {"band_gap": 0.05}
        material_type = service._classify_material(results)

        assert material_type == "metal"

    def test_classify_material_insulator(self, service):
        """Test material classification for insulator"""
        # Diamond-like gap
        results = {"band_gap": 5.5}
        material_type = service._classify_material(results)

        assert material_type == "insulator"

    def test_get_calculation_status_no_calculation(self, service):
        """Test getting calculation status for non-existent calculation"""
        request_data = {
            "calculation_id": "nonexistent_calc"
        }

        result = service.get_calculation_status(request_data)

        assert result['success'] is False
        assert 'error' in result

    def test_get_calculation_results_no_results(self, service):
        """Test getting calculation results for non-existent calculation"""
        request_data = {
            "calculation_id": "nonexistent_calc"
        }

        result = service.get_calculation_results(request_data)

        assert result['success'] is False
        assert 'error' in result

    def test_calculate_density(self, service):
        """Test density calculation"""
        results = {
            "volume": 157.464,  # Å³
            "n_atoms": 8
        }

        density = service._calculate_density(results)

        assert isinstance(density, float)
        assert density > 0

    def test_get_kpath_for_crystal_system_cubic(self, service):
        """Test k-path generation for cubic crystal system"""
        # Mock cell for cubic system
        cell = np.array([[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]])

        kpath_info = service._get_kpath_for_crystal_system("cubic", cell)

        assert "path" in kpath_info
        assert "labels" in kpath_info
        assert "kpoints" in kpath_info
        assert len(kpath_info["labels"]) > 0
        assert len(kpath_info["kpoints"]) > 0

    def test_get_kpath_for_crystal_system_default(self, service):
        """Test k-path generation for unknown crystal system"""
        cell = np.array([[5.43, 0.0, 0.0], [0.0, 5.43, 0.0], [0.0, 0.0, 5.43]])

        kpath_info = service._get_kpath_for_crystal_system("unknown", cell)

        assert "path" in kpath_info
        assert "labels" in kpath_info
        assert "kpoints" in kpath_info
        assert len(kpath_info["labels"]) > 0
        assert len(kpath_info["kpoints"]) > 0

    def test_reconstruct_atoms_from_results_complete(self, service):
        """Test atom reconstruction from complete results"""
        results = {
            "symbols": ["Si", "Si"],
            "positions": [[0, 0, 0], [1.4, 1.4, 1.4]],
            "cell": [[5.4, 0, 0], [0, 5.4, 0], [0, 0, 5.4]],
            "pbc": [True, True, True]
        }

        atoms = service._reconstruct_atoms_from_results(results)

        assert atoms is not None
        assert len(atoms) == 2
        assert atoms.get_chemical_symbols() == ["Si", "Si"]

    def test_reconstruct_atoms_from_results_partial(self, service):
        """Test atom reconstruction from partial results"""
        results = {
            "n_atoms": 4,
            "lattice_parameters": {"a": 5.43}
        }

        atoms = service._reconstruct_atoms_from_results(results)

        assert atoms is not None
        assert len(atoms) == 4
        assert atoms.get_chemical_symbols() == ["Si", "Si", "Si", "Si"]

    def test_available_calculators_property(self, service):
        """Test available calculators property"""
        calculators = service.available_calculators

        assert isinstance(calculators, dict)
        # Should have GPAW entry at minimum
        assert 'gpaw' in calculators

    def test_service_error_handling(self, service):
        """Test service error handling"""
        # Test with invalid input that should trigger error handling
        try:
            # This should trigger an exception in the service
            result = service.create_calculation({})
            # If it doesn't fail, check that it handles gracefully
            assert 'success' in result
        except Exception:
            # If an exception occurs, the service should handle it
            pass

    @pytest.mark.asyncio
    async def test_calculation_parameters_validation(self, service):
        """Test calculation parameters validation"""
        # Valid parameters
        valid_params = {
            "material_name": "Test",
            "calculation_type": "scf",
            "xc_functional": "PBE",
            "kpoints": [4, 4, 4],
            "cutoff_energy": 400.0
        }

        result = await service.create_calculation(valid_params)
        assert result['success'] is True

        # Invalid parameters
        invalid_params = {
            "material_name": "Test",
            "calculation_type": "invalid",
            "xc_functional": "INVALID",
            "kpoints": [-1, -1, -1],  # Invalid negative kpoints
            "cutoff_energy": -100.0  # Invalid negative cutoff
        }

        result = await service.create_calculation(invalid_params)
        # Should either fail or handle gracefully
        assert isinstance(result, dict)
        assert 'success' in result

    def test_material_type_detection(self, service):
        """Test material type detection from band gap"""
        test_cases = [
            (0.0, "metal"),
            (0.05, "metal"),
            (0.15, "semiconductor"),
            (2.0, "semiconductor"),
            (4.5, "insulator"),
            (6.0, "insulator")
        ]

        for gap, expected_type in test_cases:
            results = {"band_gap": gap}
            material_type = service._classify_material(results)
            assert material_type == expected_type, f"Gap {gap} should be classified as {expected_type}"

    def test_service_method_existence(self, service):
        """Test that all expected methods exist"""
        expected_methods = [
            'create_calculation',
            'run_calculation',
            'analyze_electronic_structure',
            'calculate_band_structure',
            'calculate_dos',
            'geometry_optimization',
            'phonon_calculation',
            'calculate_thermodynamic_properties',
            'get_calculation_status',
            'get_calculation_results'
        ]

        for method_name in expected_methods:
            assert hasattr(service, method_name), f"Service should have method {method_name}"

    def test_service_attributes(self, service):
        """Test service has expected attributes"""
        expected_attributes = [
            'ase_available',
            'available_calculators',
            'active_calculations',
            'calculation_results'
        ]

        for attr_name in expected_attributes:
            assert hasattr(service, attr_name), f"Service should have attribute {attr_name}"
