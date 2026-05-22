"""
Tests for Optimization Service
"""

import pytest
import numpy as np
from app.domains.mathematics.services.optimization_service import OptimizationService


class TestOptimizationService:
    """Test cases for OptimizationService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide OptimizationService instance"""
        return OptimizationService()

    def test_simulated_annealing_basic(self, service):
        """Test basic simulated annealing optimization"""
        result = service.simulated_annealing(
            objective_function="x**2 + y**2",
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            initial_temperature=100.0,
            cooling_rate=0.95,
            max_iterations=50
        )

        assert result['status'] == 'success'
        assert 'optimal_value' in result
        assert 'optimal_variables' in result
        assert 'iterations' in result
        assert len(result['optimal_variables']) == 2
        assert abs(result['optimal_value']) < 1.0  # Should be close to 0

    def test_genetic_algorithm_basic(self, service):
        """Test basic genetic algorithm optimization"""
        result = service.genetic_algorithm(
            objective_function="x**2 + y**2",
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            population_size=20,
            generations=10,
            mutation_rate=0.1
        )

        assert result['status'] == 'success'
        assert 'optimal_value' in result
        assert 'optimal_variables' in result
        assert 'generations' in result
        assert len(result['optimal_variables']) == 2

    def test_particle_swarm_basic(self, service):
        """Test basic particle swarm optimization"""
        result = service.particle_swarm_optimization(
            objective_function="x**2 + y**2",
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            num_particles=20,
            max_iterations=30,
            inertia_weight=0.7,
            cognitive_weight=1.4,
            social_weight=1.4
        )

        assert result['status'] == 'success'
        assert 'optimal_value' in result
        assert 'optimal_variables' in result
        assert len(result['optimal_variables']) == 2

    def test_simulated_annealing_with_constraints(self, service):
        """Test simulated annealing with constraints"""
        result = service.simulated_annealing(
            objective_function="x**2 + y**2",
            variables=["x", "y"],
            bounds=[(-2, 2), (-2, 2)],
            constraints=["x + y <= 1", "x - y >= -1"],
            initial_temperature=50.0,
            cooling_rate=0.9,
            max_iterations=30
        )

        assert result['status'] == 'success'
        assert 'optimal_value' in result
        assert 'optimal_variables' in result
        # Check constraints are satisfied
        x, y = result['optimal_variables']
        assert x + y <= 1.1  # Allow small tolerance
        assert x - y >= -1.1

    def test_genetic_algorithm_multiobjective(self, service):
        """Test genetic algorithm with multiple objectives"""
        result = service.genetic_algorithm_multiobjective(
            objective_functions=["x**2 + y**2", "(x-1)**2 + (y-1)**2"],
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            population_size=30,
            generations=15
        )

        assert result['status'] == 'success'
        assert 'pareto_front' in result
        assert 'pareto_solutions' in result
        assert len(result['pareto_front']) > 0

    def test_differential_evolution_basic(self, service):
        """Test basic differential evolution"""
        result = service.differential_evolution(
            objective_function="x**2 + y**2 + z**2",
            variables=["x", "y", "z"],
            bounds=[(-3, 3), (-3, 3), (-3, 3)],
            population_size=15,
            max_generations=20,
            mutation_factor=0.8,
            crossover_probability=0.9
        )

        assert result['status'] == 'success'
        assert 'optimal_value' in result
        assert 'optimal_variables' in result
        assert len(result['optimal_variables']) == 3

    def test_optimization_with_invalid_function(self, service):
        """Test optimization with invalid objective function"""
        result = service.simulated_annealing(
            objective_function="invalid_function(x, y)",
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            initial_temperature=100.0,
            cooling_rate=0.95,
            max_iterations=10
        )

        assert result['status'] == 'error'
        assert 'error' in result

    def test_optimization_with_invalid_bounds(self, service):
        """Test optimization with invalid bounds"""
        result = service.genetic_algorithm(
            objective_function="x**2 + y**2",
            variables=["x", "y"],
            bounds=[(5, -5), (-5, 5)],  # Invalid: lower > upper
            population_size=10,
            generations=5
        )

        assert result['status'] == 'error'
        assert 'error' in result

    def test_get_optimization_methods(self, service):
        """Test getting available optimization methods"""
        result = service.get_optimization_methods()

        assert isinstance(result, dict)
        assert 'simulated_annealing' in result
        assert 'genetic_algorithm' in result
        assert 'particle_swarm' in result
        assert 'differential_evolution' in result

    def test_optimization_comparison(self, service):
        """Test comparing different optimization methods"""
        result = service.compare_optimization_methods(
            objective_function="x**4 - 3*x**3 + 2",
            variables=["x"],
            bounds=[(-2, 3)],
            methods=['simulated_annealing', 'genetic_algorithm'],
            max_evaluations=50
        )

        assert result['status'] == 'success'
        assert 'results' in result
        assert 'comparison' in result
        assert len(result['results']) == 2

    def test_optimization_convergence_analysis(self, service):
        """Test optimization convergence analysis"""
        result = service.analyze_convergence(
            objective_function="x**2 + y**2",
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            method='simulated_annealing',
            num_runs=3,
            max_iterations=20
        )

        assert result['status'] == 'success'
        assert 'convergence_data' in result
        assert 'statistics' in result
        assert len(result['convergence_data']) == 3

    def test_optimization_sensitivity_analysis(self, service):
        """Test optimization sensitivity analysis"""
        result = service.sensitivity_analysis(
            objective_function="a*x**2 + b*y**2",
            variables=["x", "y"],
            bounds=[(-2, 2), (-2, 2)],
            parameters={"a": [0.5, 1.0, 2.0], "b": [0.5, 1.0, 2.0]},
            method='genetic_algorithm',
            num_samples=5
        )

        assert result['status'] == 'success'
        assert 'sensitivity_results' in result
        assert 'parameter_effects' in result

    def test_optimization_with_custom_initial_guess(self, service):
        """Test optimization with custom initial guess"""
        result = service.simulated_annealing(
            objective_function="x**2 + (y-1)**2",
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            initial_guess=[2.0, -1.0],
            initial_temperature=50.0,
            cooling_rate=0.9,
            max_iterations=30
        )

        assert result['status'] == 'success'
        assert 'optimal_value' in result
        assert 'optimal_variables' in result
        # Should converge to (0, 1)
        x, y = result['optimal_variables']
        assert abs(x) < 1.0
        assert abs(y - 1.0) < 1.0

    def test_optimization_stopping_criteria(self, service):
        """Test optimization with different stopping criteria"""
        result = service.simulated_annealing(
            objective_function="x**2 + y**2",
            variables=["x", "y"],
            bounds=[(-5, 5), (-5, 5)],
            initial_temperature=100.0,
            cooling_rate=0.95,
            max_iterations=100,
            tolerance=1e-6,
            patience=10
        )

        assert result['status'] == 'success'
        assert 'optimal_value' in result
        assert 'stopping_reason' in result
        assert result['optimal_value'] < 1e-5  # Should be very close to 0
