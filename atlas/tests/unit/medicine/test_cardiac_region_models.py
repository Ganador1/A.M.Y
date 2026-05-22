"""
Test suite for Cardiac Region Models Service
Tests regional cardiac modeling capabilities including constitutive models,
active stress models, and regional geometry specifications.
"""

import numpy as np
import torch

from app.cardiac_region_models import (
    CardiacRegion,
    RegionalMaterialProperties,
    RegionalGeometry,
    RegionalConstitutiveModel,
    RegionalActiveStressModel,
    RegionalCardiacPINN,
    CardiacRegionModelsService,
    estimate_left_ventricle_properties,
    simulate_right_atrium_mechanics
)


class TestCardiacRegionModels:
    """Test suite for cardiac region models"""

    def test_cardiac_region_enum(self):
        """Test CardiacRegion enum values"""
        assert CardiacRegion.LEFT_VENTRICLE.value == "left_ventricle"
        assert CardiacRegion.RIGHT_VENTRICLE.value == "right_ventricle"
        assert CardiacRegion.LEFT_ATRIUM.value == "left_atrium"
        assert CardiacRegion.RIGHT_ATRIUM.value == "right_atrium"
        assert CardiacRegion.INTERVENTRICULAR_SEPTUM.value == "interventricular_septum"

    def test_regional_material_properties(self):
        """Test RegionalMaterialProperties dataclass"""
        props = RegionalMaterialProperties(
            region=CardiacRegion.LEFT_VENTRICLE,
            young_modulus=25.0,
            poisson_ratio=0.49,
            active_stress=80.0,
            conductivity=0.5,
            anisotropy_ratio=3.0
        )

        assert props.region == CardiacRegion.LEFT_VENTRICLE
        assert props.young_modulus == 25.0
        assert props.active_stress == 80.0
        assert props.anisotropy_ratio == 3.0

    def test_regional_geometry(self):
        """Test RegionalGeometry dataclass"""
        geometry = RegionalGeometry(
            region=CardiacRegion.LEFT_VENTRICLE,
            wall_thickness=10.0,
            cavity_volume=120.0,
            surface_area=150.0,
            fiber_orientation=np.array([0.8, 0.6, 0.0]),
            regional_strain={'global': -0.18, 'longitudinal': -0.20, 'circumferential': -0.16}
        )

        assert geometry.region == CardiacRegion.LEFT_VENTRICLE
        assert geometry.wall_thickness == 10.0
        assert geometry.cavity_volume == 120.0
        assert np.allclose(geometry.fiber_orientation, [0.8, 0.6, 0.0])
        assert geometry.regional_strain['global'] == -0.18

    def test_regional_constitutive_model(self):
        """Test RegionalConstitutiveModel functionality"""
        from app.biomechanical_models import NeoHookeanModel

        # Create base model
        base_model = NeoHookeanModel(mu=10.0, kappa=1000.0)

        # Create regional model
        regional_model = RegionalConstitutiveModel(
            CardiacRegion.LEFT_VENTRICLE,
            base_model
        )

        # Test regional properties
        assert regional_model.region == CardiacRegion.LEFT_VENTRICLE
        assert regional_model.regional_properties.young_modulus == 25.0

        # Test material parameters
        params = regional_model.material_parameters()
        assert 'regional_young_modulus' in params
        assert params['regional_young_modulus'] == 25.0
        assert params['anisotropy_ratio'] == 3.0

        # Test strain energy density (abstract method implementation)
        deformation_gradient = torch.eye(3).unsqueeze(0)
        energy = regional_model.strain_energy_density(deformation_gradient)
        assert isinstance(energy, torch.Tensor)

    def test_regional_active_stress_model(self):
        """Test RegionalActiveStressModel functionality"""
        active_model = RegionalActiveStressModel(CardiacRegion.LEFT_VENTRICLE)

        # Test regional properties
        assert active_model.region == CardiacRegion.LEFT_VENTRICLE
        assert active_model.regional_properties['max_stress'] == 80.0
        assert active_model.regional_properties['activation_time'] == 0.25

        # Test active tension calculation
        time = torch.tensor([0.1, 0.2, 0.3])
        fiber_direction = torch.tensor([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

        tension = active_model.active_tension(time, fiber_direction)
        assert isinstance(tension, torch.Tensor)
        assert tension.shape[0] == 3  # One for each time point

    def test_regional_cardiac_pinn(self):
        """Test RegionalCardiacPINN initialization and basic functionality"""
        pinn = RegionalCardiacPINN(CardiacRegion.RIGHT_VENTRICLE)

        # Test initialization
        assert pinn.region == CardiacRegion.RIGHT_VENTRICLE
        assert isinstance(pinn.constitutive_model, RegionalConstitutiveModel)
        assert isinstance(pinn.active_model, RegionalActiveStressModel)
        assert isinstance(pinn.geometry, RegionalGeometry)

        # Test regional geometry
        assert pinn.geometry.wall_thickness == 4.0
        assert pinn.geometry.cavity_volume == 100.0
        assert np.allclose(pinn.geometry.fiber_orientation, [0.7, 0.7, 0.0])

        # Test regional physics loss
        x = torch.randn(10, 3)
        t = torch.randn(10, 1)
        loss = pinn.regional_physics_loss(x, t)
        assert isinstance(loss, torch.Tensor)

    def test_cardiac_region_models_service(self):
        """Test CardiacRegionModelsService functionality"""
        service = CardiacRegionModelsService()

        # Test initialization
        assert len(service.regional_models) == 5  # All cardiac regions
        assert CardiacRegion.LEFT_VENTRICLE in service.regional_models
        assert CardiacRegion.INTERVENTRICULAR_SEPTUM in service.regional_models

        # Test regional property estimation
        experimental_data = {
            'strain': np.random.normal(0, 0.1, (50, 3, 3)),
            'stress': np.random.normal(20, 5, (50, 3))
        }

        result = service.estimate_regional_properties(
            experimental_data,
            CardiacRegion.LEFT_VENTRICLE
        )

        assert result['region'] == 'left_ventricle'
        assert 'estimated_parameters' in result
        assert result['estimated_parameters']['young_modulus'] == 25.0
        assert result['validation_status'] == 'regional_model_validated'

        # Test regional mechanics simulation
        boundary_conditions = {'pressure': 10.0, 'flow': 5.0}
        sim_result = service.simulate_regional_mechanics(
            CardiacRegion.RIGHT_ATRIUM,
            boundary_conditions
        )

        assert sim_result['region'] == 'right_atrium'
        assert 'regional_metrics' in sim_result
        assert 'ejection_fraction' in sim_result['regional_metrics']
        assert sim_result['validation_status'] == 'regional_simulation_validated'

    def test_regional_model_comparison(self):
        """Test comparison of regional models"""
        service = CardiacRegionModelsService()

        regions_to_compare = [
            CardiacRegion.LEFT_VENTRICLE,
            CardiacRegion.RIGHT_VENTRICLE,
            CardiacRegion.LEFT_ATRIUM
        ]

        comparison = service.compare_regional_models(regions_to_compare)

        assert len(comparison) == 3
        assert 'left_ventricle' in comparison
        assert 'right_ventricle' in comparison
        assert 'left_atrium' in comparison

        # Check that each region has the expected properties
        lv_props = comparison['left_ventricle']
        assert lv_props['geometry']['wall_thickness'] == 10.0
        assert lv_props['geometry']['cavity_volume'] == 120.0

        rv_props = comparison['right_ventricle']
        assert rv_props['geometry']['wall_thickness'] == 4.0
        assert rv_props['geometry']['cavity_volume'] == 100.0

    def test_convenience_functions(self):
        """Test convenience functions for specific regions"""
        # Test left ventricle estimation
        experimental_data = {
            'strain': np.random.normal(0, 0.1, (30, 3, 3)),
            'stress': np.random.normal(25, 8, (30, 3))
        }

        lv_result = estimate_left_ventricle_properties(experimental_data)
        assert lv_result['region'] == 'left_ventricle'
        assert lv_result['estimated_parameters']['young_modulus'] == 25.0

        # Test right atrium simulation
        ra_result = simulate_right_atrium_mechanics({'pressure': 5.0})
        assert ra_result['region'] == 'right_atrium'
        assert ra_result['regional_metrics']['wall_thickness_mm'] == 2.5

    def test_regional_metrics_calculation(self):
        """Test calculation of regional-specific metrics"""
        service = CardiacRegionModelsService()

        # Create mock solution data
        solution = {
            'region': 'left_ventricle',
            'displacement': np.random.normal(0, 0.01, (100, 3)),
            'stress': np.random.normal(40, 10, (100, 6)),
            'strain': np.random.normal(0, 0.05, (100, 6)),
            'method': 'regional_pinn_left_ventricle'
        }

        geometry = RegionalGeometry(
            region=CardiacRegion.LEFT_VENTRICLE,
            wall_thickness=10.0,
            cavity_volume=120.0,
            surface_area=150.0,
            fiber_orientation=np.array([0.8, 0.6, 0.0]),
            regional_strain={'global': -0.18, 'longitudinal': -0.20, 'circumferential': -0.16}
        )

        metrics = service._calculate_regional_metrics(solution, geometry, CardiacRegion.LEFT_VENTRICLE)

        # Check expected metrics
        assert 'max_stress_kpa' in metrics
        assert 'ejection_fraction' in metrics
        assert 'stroke_volume_ml' in metrics
        assert metrics['ejection_fraction'] == 0.65  # LV specific
        assert metrics['stroke_volume_ml'] == 120.0 * 0.65  # cavity_volume * ejection_fraction
        assert metrics['wall_thickness_mm'] == 10.0

    def test_regional_report_generation(self):
        """Test generation of regional cardiac reports"""
        service = CardiacRegionModelsService()

        # Mock estimation and simulation results
        estimation_result = {
            'geometry': RegionalGeometry(
                region=CardiacRegion.LEFT_VENTRICLE,
                wall_thickness=10.0,
                cavity_volume=120.0,
                surface_area=150.0,
                fiber_orientation=np.array([0.8, 0.6, 0.0]),
                regional_strain={'global': -0.18, 'longitudinal': -0.20, 'circumferential': -0.16}
            ),
            'estimated_parameters': {
                'young_modulus': 25.0,
                'active_stress': 80.0,
                'anisotropy_ratio': 3.0
            },
            'validation_status': 'regional_model_validated'
        }

        simulation_result = {
            'regional_metrics': {
                'regional_strain_global': -0.18,
                'regional_strain_longitudinal': -0.20,
                'regional_strain_circumferential': -0.16,
                'ejection_fraction': 0.65,
                'stroke_volume_ml': 78.0,
                'max_stress_kpa': 85.0
            }
        }

        report = service.generate_regional_report(
            CardiacRegion.LEFT_VENTRICLE,
            estimation_result,
            simulation_result
        )

        # Check report content
        assert 'Ventrículo Izquierdo' in report
        assert '25.0 kPa' in report  # Young modulus
        assert '80.0 kPa' in report  # Active stress
        assert '0.65' in report      # Ejection fraction
        assert '78.0 mL' in report   # Stroke volume
        assert 'regional_model_validated' in report


if __name__ == "__main__":
    # Run basic validation
    print("🧪 Running Cardiac Region Models Tests...")

    # Test enum
    print("✅ Testing CardiacRegion enum...")
    assert CardiacRegion.LEFT_VENTRICLE.value == "left_ventricle"

    # Test service initialization
    print("✅ Testing CardiacRegionModelsService...")
    service = CardiacRegionModelsService()
    assert len(service.regional_models) == 5

    # Test regional estimation
    print("✅ Testing regional property estimation...")
    experimental_data = {
        'strain': np.random.normal(0, 0.1, (20, 3, 3)),
        'stress': np.random.normal(20, 5, (20, 3))
    }
    result = service.estimate_regional_properties(experimental_data, CardiacRegion.LEFT_VENTRICLE)
    assert result['estimated_parameters']['young_modulus'] == 25.0

    print("🎉 All basic tests passed!")
    print("📊 Regional cardiac models validation complete")
