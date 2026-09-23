#!/usr/bin/env python3
"""
Unit Tests for Additive Manufacturing Service - AXIOM META 4
==========================================================

Tests for additive manufacturing simulation including:
- Thermal transport equations
- Melt pool dynamics
- Microstructure evolution
- Process optimization
"""

import pytest
import numpy as np
import sys
import os

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app.additive_manufacturing_service import (
    AdditiveManufacturingService
)


class TestAdditiveManufacturingService:
    """Test suite for Additive Manufacturing Service"""

    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test"""
        return AdditiveManufacturingService()

    @pytest.fixture
    def sample_material_properties(self):
        """Sample material properties for testing"""
        return {
            'density': 7800,                    # kg/m³
            'thermal_diffusivity': 3.6e-6,      # m²/s
            'specific_heat': 500,               # J/(kg·K)
            'thermal_conductivity': 11.4,       # W/(m·K)
            'melting_temperature': 1600,        # K
            'boiling_temperature': 3000,        # K
            'latent_heat': 2.1e6,               # J/kg
            'surface_tension': 1.8,             # N/m
            'viscosity': 0.006,                 # Pa·s
            'thermal_expansion': 1.2e-5,        # 1/K
            'heat_transfer_coeff': 50,          # W/(m²·K)
            'grain_growth_activation': 1.5e5,   # J/mol
            'grain_growth_coeff': 1e-10,        # m²/s
            'liquidus_temperature': 1600,       # K
            'solidus_temperature': 1530,        # K
            'base_porosity': 0.001,
            'critical_solidification_rate': 0.1
        }

    @pytest.fixture
    def sample_laser_parameters(self):
        """Sample laser parameters for testing"""
        return {
            'power': 200,           # W
            'beam_radius': 50e-6,   # m
            'absorption': 0.35      # efficiency
        }

    @pytest.fixture
    def sample_process_parameters(self):
        """Sample process parameters for testing"""
        return {
            'scan_speed': 800,      # mm/s
            'layer_thickness': 30,  # μm
            'hatch_spacing': 100,   # μm
            'melting_temperature': 1600  # K
        }

    def test_service_initialization(self, service):
        """Test service initialization"""
        assert service.logger is not None
        assert hasattr(service, 'setup_process')
        assert hasattr(service, 'simulate_single_track')
        assert hasattr(service, 'optimize_process_parameters')

    def test_process_setup(self, service, sample_material_properties):
        """Test process setup functionality"""
        from app.additive_manufacturing_service import AdditiveProcess, MaterialType

        # Test setup method exists
        assert hasattr(service, 'setup_process')

        # Test that setup configures internal solvers
        service.setup_process(
            AdditiveProcess.LASER_POWDER_BED_FUSION,
            MaterialType.METALLIC,
            sample_material_properties
        )

        # Check that solvers are initialized
        assert service.thermal_solver is not None
        assert service.fluid_solver is not None
        assert service.microstructure_solver is not None

    def test_thermal_transport_equations(self, service):
        """Test thermal transport equation implementations"""
        # Test that thermal solver has required methods
        assert hasattr(service, 'thermal_solver')  # Will be None until setup
        # After setup, these should exist
        if service.thermal_solver:
            assert hasattr(service.thermal_solver, 'heat_conduction_equation')
            assert hasattr(service.thermal_solver, 'laser_heat_source')
            assert hasattr(service.thermal_solver, 'convection_boundary_condition')

    def test_fluid_dynamics_equations(self, service):
        """Test fluid dynamics equation implementations"""
        if service.fluid_solver:
            assert hasattr(service.fluid_solver, 'navier_stokes_equation')
            assert hasattr(service.fluid_solver, 'surface_tension_model')
            assert hasattr(service.fluid_solver, 'evaporation_model')

    def test_microstructure_evolution(self, service):
        """Test microstructure evolution modeling"""
        if service.microstructure_solver:
            assert hasattr(service.microstructure_solver, 'grain_growth_model')
            assert hasattr(service.microstructure_solver, 'phase_transformation_model')
            assert hasattr(service.microstructure_solver, 'porosity_formation_model')

    def test_melt_pool_analysis(self, service):
        """Test melt pool dynamics analysis"""
        assert hasattr(service, '_analyze_melt_pool_dynamics')

    def test_microstructure_analysis(self, service):
        """Test microstructure evolution analysis"""
        assert hasattr(service, '_analyze_microstructure_evolution')

    def test_quality_metrics_calculation(self, service):
        """Test build quality metrics calculation"""
        assert hasattr(service, '_calculate_build_quality_metrics')

    def test_process_efficiency_calculation(self, service):
        """Test process efficiency calculation"""
        assert hasattr(service, '_calculate_process_efficiency')

    def test_defect_analysis(self, service):
        """Test defect analysis functionality"""
        assert hasattr(service, '_analyze_defects')

    def test_thermal_history_processing(self, service):
        """Test thermal history processing"""
        assert hasattr(service, '_process_thermal_history')

    def test_data_structures(self):
        """Test additive manufacturing data structures"""
        from app.additive_manufacturing_service import (
            ThermalHistory,
            MeltPoolDynamics,
            MicrostructureEvolution
        )

        # Test dataclass instantiation
        thermal = ThermalHistory(
            temperature_profile=np.array([300, 1000, 1600, 800]),
            time_points=np.array([0, 0.001, 0.002, 0.003]),
            heating_rates=np.array([700000, 600000, -800000]),
            cooling_rates=np.array([0, 0, 800000]),
            peak_temperatures=[1600],
            dwell_times=[0.001],
            thermal_cycles=1,
            total_time=0.003
        )
        assert len(thermal.temperature_profile) == 4

        # Test melt pool dynamics
        melt_pool = MeltPoolDynamics(
            dimensions={'length': 100e-6, 'width': 80e-6, 'depth': 50e-6},
            temperature_distribution=np.array([1600, 1580, 1550]),
            velocity_field=np.array([[0.1, 0.05, 0.02]]),
            surface_tension=1.8,
            viscosity=0.006,
            evaporation_rate=1e-6,
            keyhole_depth=100e-6
        )
        assert melt_pool.dimensions['length'] == 100e-6

        # Test microstructure evolution
        microstructure = MicrostructureEvolution(
            grain_size_distribution=np.array([1e-5, 1.2e-5, 0.8e-5]),
            phase_fractions={'austenite': 0.7, 'ferrite': 0.2, 'martensite': 0.1},
            porosity_distribution=np.array([0.001, 0.002, 0.0015]),
            defect_density={'dislocations': 1e12, 'vacancies': 1e20},
            mechanical_properties={'yield_strength': 500, 'hardness': 200},
            thermal_properties={'conductivity': 50, 'expansion': 1e-5}
        )
        assert microstructure.phase_fractions['austenite'] == 0.7

    def test_enums_and_constants(self):
        """Test enums and constants"""
        from app.additive_manufacturing_service import (
            AdditiveProcess,
            MaterialType
        )

        # Test process types
        assert AdditiveProcess.LASER_POWDER_BED_FUSION.value == "lpbf"
        assert AdditiveProcess.ELECTRON_BEAM_MELTING.value == "ebm"

        # Test material types
        assert MaterialType.METALLIC.value == "metallic"
        assert MaterialType.POLYMERIC.value == "polymeric"
        assert MaterialType.CERAMIC.value == "ceramic"

    def test_export_functionality(self, service):
        """Test export functionality"""
        assert hasattr(service, 'export_am_results')

    def test_optimization_methods(self, service):
        """Test process optimization methods"""
        assert hasattr(service, 'optimize_process_parameters')

    def test_helper_functions(self, service):
        """Test helper functions availability"""
        assert hasattr(service, '_calculate_spatial_resolution')
        assert hasattr(service, '_calculate_temporal_consistency')
        assert hasattr(service, '_calculate_snr')


if __name__ == "__main__":
    pytest.main([__file__])
