"""
Tests for Calculus Service
"""

import pytest
from app.domains.mathematics.services.calculus_service import CalculusService


class TestCalculusService:
    """Test cases for CalculusService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide CalculusService instance"""
        return CalculusService()

    def test_derivative_basic_polynomial(self, service):
        """Test basic polynomial derivative"""
        result = service.compute_derivative("x**3 + 2*x**2 + x + 1", "x")

        assert result['status'] == 'success'
        assert 'derivative' in result
        assert 'original_function' in result
        assert 'variable' in result
        assert result['derivative'] == '3*x**2 + 4*x + 1'

    def test_derivative_trigonometric(self, service):
        """Test trigonometric function derivative"""
        result = service.compute_derivative("sin(x)", "x")

        assert result['status'] == 'success'
        assert result['derivative'] == 'cos(x)'

    def test_derivative_exponential(self, service):
        """Test exponential function derivative"""
        result = service.compute_derivative("exp(x)", "x")

        assert result['status'] == 'success'
        assert result['derivative'] == 'exp(x)'

    def test_derivative_logarithmic(self, service):
        """Test logarithmic function derivative"""
        result = service.compute_derivative("log(x)", "x")

        assert result['status'] == 'success'
        assert result['derivative'] == '1/x'

    def test_derivative_higher_order(self, service):
        """Test higher order derivatives"""
        result = service.compute_derivative("x**4", "x", order=2)

        assert result['status'] == 'success'
        assert result['derivative'] == '12*x**2'

    def test_derivative_partial(self, service):
        """Test partial derivatives"""
        result = service.compute_partial_derivative("x**2*y + y**3", "x", "x")

        assert result['status'] == 'success'
        assert 'partial_derivative' in result

    def test_integral_indefinite_basic(self, service):
        """Test basic indefinite integral"""
        result = service.compute_integral("x**2", "x")

        assert result['status'] == 'success'
        assert 'integral' in result
        assert 'original_function' in result
        assert 'variable' in result

    def test_integral_definite(self, service):
        """Test definite integral"""
        result = service.compute_integral("x", "x", lower_limit=0, upper_limit=1)

        assert result['status'] == 'success'
        assert 'definite_integral' in result
        assert 'numerical_value' in result
        assert result['numerical_value'] == 0.5

    def test_integral_trigonometric(self, service):
        """Test trigonometric integral"""
        result = service.compute_integral("cos(x)", "x", lower_limit=0, upper_limit="pi/2")

        assert result['status'] == 'success'
        assert 'definite_integral' in result
        assert abs(result['numerical_value'] - 1.0) < 1e-10

    def test_integral_improper(self, service):
        """Test improper integral"""
        result = service.compute_integral("1/x**2", "x", lower_limit=1, upper_limit=float('inf'))

        assert result['status'] == 'success'
        assert 'definite_integral' in result

    def test_limit_basic(self, service):
        """Test basic limit calculation"""
        result = service.compute_limit("(x**2 - 1)/(x - 1)", "x", 1)

        assert result['status'] == 'success'
        assert 'limit_value' in result
        assert result['limit_value'] == 2

    def test_limit_infinity(self, service):
        """Test limit at infinity"""
        result = service.compute_limit("1/x", "x", float('inf'))

        assert result['status'] == 'success'
        assert result['limit_value'] == 0

    def test_limit_trigonometric(self, service):
        """Test trigonometric limit"""
        result = service.compute_limit("sin(x)/x", "x", 0)

        assert result['status'] == 'success'
        assert result['limit_value'] == 1

    def test_series_taylor(self, service):
        """Test Taylor series expansion"""
        result = service.compute_taylor_series("exp(x)", "x", 0, 5)

        assert result['status'] == 'success'
        assert 'taylor_series' in result
        assert 'expansion_point' in result
        assert 'order' in result

    def test_series_maclaurin(self, service):
        """Test Maclaurin series expansion"""
        result = service.compute_maclaurin_series("sin(x)", 6)

        assert result['status'] == 'success'
        assert 'maclaurin_series' in result
        assert 'order' in result

    def test_multiple_integral_double(self, service):
        """Test double integral"""
        result = service.compute_multiple_integral("x*y", ["x", "y"],
                                                 x_limits=(0, 1), y_limits=(0, 1))

        assert result['status'] == 'success'
        assert 'multiple_integral' in result
        assert 'numerical_value' in result

    def test_multiple_integral_triple(self, service):
        """Test triple integral"""
        result = service.compute_multiple_integral("x*y*z", ["x", "y", "z"],
                                                 x_limits=(0, 1), y_limits=(0, 1), z_limits=(0, 1))

        assert result['status'] == 'success'
        assert 'multiple_integral' in result
        assert 'numerical_value' in result

    def test_vector_calculus_gradient(self, service):
        """Test gradient calculation"""
        result = service.compute_gradient("x**2 + y**2 + z**2", ["x", "y", "z"])

        assert result['status'] == 'success'
        assert 'gradient' in result
        assert len(result['gradient']) == 3

    def test_vector_calculus_divergence(self, service):
        """Test divergence calculation"""
        result = service.compute_divergence(["x", "y", "z"], ["x", "y", "z"])

        assert result['status'] == 'success'
        assert 'divergence' in result

    def test_vector_calculus_curl(self, service):
        """Test curl calculation"""
        result = service.compute_curl(["x**2", "y**2", "z**2"], ["x", "y", "z"])

        assert result['status'] == 'success'
        assert 'curl' in result
        assert len(result['curl']) == 3

    def test_vector_calculus_line_integral(self, service):
        """Test line integral calculation"""
        result = service.compute_line_integral("x*y", "x", "y",
                                             curve_parametric={"x": "t", "y": "t**2"},
                                             parameter_range=(0, 1))

        assert result['status'] == 'success'
        assert 'line_integral' in result

    def test_vector_calculus_surface_integral(self, service):
        """Test surface integral calculation"""
        result = service.compute_surface_integral("1", "x", "y", "z",
                                                surface_parametric={"x": "u", "y": "v", "z": "u**2 + v**2"},
                                                parameter_ranges={"u": (0, 1), "v": (0, 1)})

        assert result['status'] == 'success'
        assert 'surface_integral' in result

    def test_differential_equations_first_order(self, service):
        """Test first-order differential equation solving"""
        result = service.solve_differential_equation("y' = 2*x", "y", "x")

        assert result['status'] == 'success'
        assert 'solution' in result
        assert 'general_solution' in result

    def test_differential_equations_second_order(self, service):
        """Test second-order differential equation solving"""
        result = service.solve_differential_equation("y'' + y = 0", "y", "x")

        assert result['status'] == 'success'
        assert 'solution' in result

    def test_differential_equations_with_initial_conditions(self, service):
        """Test differential equation with initial conditions"""
        result = service.solve_differential_equation("y' = y", "y", "x",
                                                   initial_conditions={"x": 0, "y": 1})

        assert result['status'] == 'success'
        assert 'solution' in result
        assert 'particular_solution' in result

    def test_numerical_integration_trapezoidal(self, service):
        """Test numerical integration using trapezoidal rule"""
        result = service.numerical_integration("x**2", "x", 0, 1, method="trapezoidal", n=100)

        assert result['status'] == 'success'
        assert 'numerical_result' in result
        assert 'exact_result' in result
        assert 'error' in result
        assert abs(result['numerical_result'] - 1/3) < 1e-4

    def test_numerical_integration_simpson(self, service):
        """Test numerical integration using Simpson's rule"""
        result = service.numerical_integration("x**2", "x", 0, 1, method="simpson", n=100)

        assert result['status'] == 'success'
        assert 'numerical_result' in result
        assert abs(result['numerical_result'] - 1/3) < 1e-6

    def test_numerical_differentiation_forward(self, service):
        """Test numerical differentiation using forward difference"""
        result = service.numerical_differentiation("x**3", "x", 1.0, method="forward", h=0.01)

        assert result['status'] == 'success'
        assert 'numerical_derivative' in result
        assert 'exact_derivative' in result
        assert abs(result['numerical_derivative'] - 3.0) < 0.1

    def test_numerical_differentiation_central(self, service):
        """Test numerical differentiation using central difference"""
        result = service.numerical_differentiation("x**3", "x", 1.0, method="central", h=0.01)

        assert result['status'] == 'success'
        assert 'numerical_derivative' in result
        assert abs(result['numerical_derivative'] - 3.0) < 0.01

    def test_calculus_with_invalid_function(self, service):
        """Test calculus with invalid function"""
        result = service.compute_derivative("invalid_function(x)", "x")

        assert result['status'] == 'error'
        assert 'error' in result

    def test_integral_with_invalid_limits(self, service):
        """Test integral with invalid limits"""
        result = service.compute_integral("x", "x", lower_limit=1, upper_limit=0)

        assert result['status'] == 'error'
        assert 'error' in result

    def test_limit_with_invalid_expression(self, service):
        """Test limit with invalid expression"""
        result = service.compute_limit("1/0", "x", 0)

        assert result['status'] == 'error'
        assert 'error' in result

    def test_get_calculus_operations(self, service):
        """Test getting available calculus operations"""
        result = service.get_calculus_operations()

        assert isinstance(result, dict)
        assert 'derivatives' in result
        assert 'integrals' in result
        assert 'limits' in result
        assert 'series' in result
        assert 'vector_calculus' in result
        assert 'differential_equations' in result
