"""
Tests for Variational Calculus Service
"""

import pytest
from app.services.variational_calculus_service import VariationalCalculusService


class TestVariationalCalculusService:
    """Test cases for VariationalCalculusService"""

    @pytest.fixture
    def service(self):
        """Create a VariationalCalculusService instance"""
        return VariationalCalculusService()

    def test_euler_lagrange_simple(self, service):
        """Test basic Euler-Lagrange equation derivation"""
        # Simple Lagrangian: L = x'^2 - x^2
        result = service.euler_lagrange_equation("x_dot**2 - x**2", "x", "t")
        assert "error" not in result
        assert "euler_lagrange_equation" in result
        assert result['status'] == 'success'

    def test_variational_derivative_simple(self, service):
        """Test basic variational derivative"""
        result = service.variational_derivative("x_dot**2 - x**2", "x", "t")
        assert "error" not in result
        assert "variational_derivative" in result
        assert result['status'] == 'success'

    def test_brachistochrone_problem(self, service):
        """Test brachistochrone problem solution"""
        result = service.solve_brachistochrone(0, 0, 1, -1, 9.81)
        assert "error" not in result
        assert "travel_time" in result
        assert "x_coordinates" in result
        assert "y_coordinates" in result
        assert "plot" in result
        assert result['status'] == 'success'

    def test_minimal_surface_area(self, service):
        """Test minimal surface area computation"""
        boundary_points = [[0, 0], [1, 0], [0.5, 1]]
        result = service.minimal_surface_area(boundary_points)
        assert "error" not in result
        assert "approximate_area" in result
        assert "x_coordinates" in result
        assert "y_coordinates" in result
        assert "plot" in result
        assert result['status'] == 'success'

    def test_least_action_principle(self, service):
        """Test principle of least action"""
        result = service.principle_of_least_action(
            "q_dot**2 - q**2",
            {"q": 0, "q_dot": 1},
            {"q": 1, "q_dot": 0},
            [0, 1]
        )
        assert "error" not in result
        assert "lagrangian" in result
        assert "principle" in result
        assert result['status'] == 'success'

    def test_get_functionals_list(self, service):
        """Test getting functionals list"""
        result = service.get_functionals_list()
        assert "functionals" in result
        assert "brachistochrone" in result["functionals"]
        assert "minimal_surface" in result["functionals"]
        assert result['count'] > 0

    def test_euler_lagrange_with_error(self, service):
        """Test Euler-Lagrange with invalid expression"""
        result = service.euler_lagrange_equation("invalid_syntax+++", "x", "t")
        assert "error" in result

    def test_variational_derivative_with_error(self, service):
        """Test variational derivative with invalid expression"""
        result = service.variational_derivative("invalid_syntax+++", "x", "t")
        assert "error" in result
