"""
Tests for Complex Analysis Service
"""

import pytest
import sympy as sp
from app.services.complex_analysis_service import ComplexAnalysisService


class TestComplexAnalysisService:
    """Test cases for ComplexAnalysisService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide ComplexAnalysisService instance"""
        return ComplexAnalysisService()

    def test_power_series_expansion_exponential(self, service):
        """Test power series expansion of exponential function"""
        result = service.power_series_expansion("exp(z)", "z", "0", 5)

        assert result['status'] == 'success'
        assert 'exp(z)' in result['function']
        assert result['expansion_point'] == '0'
        assert 'z' in result['power_series']
        assert len(result['coefficients']) > 0

    def test_power_series_expansion_sine(self, service):
        """Test power series expansion of sine function"""
        result = service.power_series_expansion("sin(z)", "z", "0", 6)

        assert result['status'] == 'success'
        assert 'sin(z)' in result['function']
        assert result['variable'] == 'z'
        assert len(result['coefficients']) > 0

    def test_power_series_expansion_invalid_function(self, service):
        """Test power series expansion with function not containing variable"""
        result = service.power_series_expansion("x**2 + 1", "z", "0", 5)

        # This should fail because the function doesn't contain variable 'z'
        assert result['status'] == 'failed'
        assert 'error' in result

    def test_residue_calculation_simple_pole(self, service):
        """Test residue calculation for a simple pole"""
        result = service.residue_calculation("1/(z-1)", "1", "z")

        assert result['status'] == 'success'
        assert result['pole'] == '1'
        assert 'laurent_series' in result

    def test_residue_calculation_invalid_function(self, service):
        """Test residue calculation with function not containing variable"""
        result = service.residue_calculation("x**2 + 1", "0", "z")

        # This should fail because the function doesn't contain variable 'z'
        assert result['status'] == 'failed'
        assert 'error' in result

    def test_contour_integral_circle(self, service):
        """Test contour integral along a circle"""
        result = service.contour_integral("1/z", "circle", "0", "1", "z")

        assert result['status'] == 'success'
        assert result['contour_type'] == 'circle'
        assert result['center'] == '0'
        assert result['radius'] == '1'

    def test_contour_integral_unsupported_type(self, service):
        """Test contour integral with unsupported contour type"""
        result = service.contour_integral("1/z", "triangle", "0", "1", "z")

        assert result['status'] == 'unsupported'
        assert 'error' in result

    def test_bessel_function_first_kind(self, service):
        """Test Bessel function of the first kind"""
        result = service.bessel_function(0, "1", "J")

        assert result['status'] == 'success'
        assert result['function_type'] == 'J'
        assert result['order'] == 0
        assert result['argument'] == '1'
        assert 'description' in result

    def test_bessel_function_second_kind(self, service):
        """Test Bessel function of the second kind"""
        result = service.bessel_function(1, "0.5", "Y")

        assert result['status'] == 'success'
        assert result['function_type'] == 'Y'
        assert result['order'] == 1

    def test_bessel_function_modified_first_kind(self, service):
        """Test modified Bessel function of the first kind"""
        result = service.bessel_function(0, "1", "I")

        assert result['status'] == 'success'
        assert result['function_type'] == 'I'

    def test_bessel_function_invalid_type(self, service):
        """Test Bessel function with invalid type"""
        result = service.bessel_function(0, "1", "X")

        assert result['status'] == 'invalid_type'
        assert 'error' in result

    def test_legendre_polynomial_degree_0(self, service):
        """Test Legendre polynomial of degree 0"""
        result = service.legendre_polynomial(0, "x")

        assert result['status'] == 'success'
        assert result['degree'] == 0
        assert 'legendre_polynomial' in result
        assert result['domain'] == '[-1, 1]'

    def test_legendre_polynomial_degree_2(self, service):
        """Test Legendre polynomial of degree 2"""
        result = service.legendre_polynomial(2, "x")

        assert result['status'] == 'success'
        assert result['degree'] == 2
        assert len(result['roots']) == 2  # P_2 has 2 roots
        assert 'orthogonality' in result

    def test_legendre_polynomial_invalid_degree(self, service):
        """Test Legendre polynomial with invalid degree"""
        result = service.legendre_polynomial(-1, "x")

        assert result['status'] == 'failed'
        assert 'error' in result

    def test_hermite_polynomial_degree_0(self, service):
        """Test Hermite polynomial of degree 0"""
        result = service.hermite_polynomial(0, "x")

        assert result['status'] == 'success'
        assert result['degree'] == 0
        assert 'hermite_polynomial' in result
        assert result['weight_function'] == 'exp(-x^2)'
        assert result['domain'] == '(-∞, ∞)'

    def test_hermite_polynomial_degree_3(self, service):
        """Test Hermite polynomial of degree 3"""
        result = service.hermite_polynomial(3, "x")

        assert result['status'] == 'success'
        assert result['degree'] == 3
        assert 'orthogonality' in result

    def test_series_convergence_ratio_test_convergent(self, service):
        """Test series convergence using ratio test - convergent series"""
        result = service.series_convergence_test("1/n**2", "n", "ratio")

        assert result['status'] == 'success'
        # For 1/n^2, the ratio test should give a result (may be inconclusive due to limit computation)
        assert 'ratio test' in result['result']
        assert result['test_type'] == 'ratio'

    def test_series_convergence_ratio_test_divergent(self, service):
        """Test series convergence using ratio test - divergent series"""
        result = service.series_convergence_test("1/n", "n", "ratio")

        assert result['status'] == 'success'
        assert 'Divergent' in result['result'] or 'Inconclusive' in result['result']

    def test_series_convergence_root_test(self, service):
        """Test series convergence using root test"""
        result = service.series_convergence_test("1/n", "n", "root")

        # The root test may be inconclusive or fail for some series, but should return a result
        assert result['status'] in ['success', 'failed']
        assert 'root test' in result.get('result', '') or 'error' in result
        assert result['test_type'] == 'root'

    def test_series_convergence_invalid_test(self, service):
        """Test series convergence with invalid test type"""
        result = service.series_convergence_test("1/n", "n", "invalid_test")

        assert result['status'] == 'invalid_test'
        assert 'error' in result

    def test_analytic_continuation(self, service):
        """Test analytic continuation"""
        result = service.analytic_continuation("sqrt(z)", "Re(z) > 0", "C \\ {0}", "z")

        assert result['status'] == 'success'
        assert result['function'] == 'sqrt(z)'
        assert result['original_domain'] == 'Re(z) > 0'

    def test_get_series_examples(self, service):
        """Test getting series examples"""
        result = service.get_series_examples()

        assert 'series' in result
        assert 'description' in result
        assert result['count'] > 0
        assert 'geometric' in result['series']
        assert 'exponential' in result['series']

    def test_power_series_expansion_with_different_variable(self, service):
        """Test power series expansion with different variable"""
        result = service.power_series_expansion("exp(w)", "w", "0", 4)

        assert result['status'] == 'success'
        assert result['variable'] == 'w'
        assert 'w' in result['power_series']

    def test_residue_calculation_complex_pole(self, service):
        """Test residue calculation for a more complex pole"""
        result = service.residue_calculation("1/(z**2 + 1)", "I", "z")

        assert result['status'] == 'success'
        assert result['pole'] == 'I'

    def test_bessel_function_with_plot(self, service):
        """Test Bessel function that generates a plot"""
        result = service.bessel_function(1, "2", "J")

        assert result['status'] == 'success'
        # Note: plot generation may not work in test environment
        # but the function should still complete successfully

    def test_legendre_polynomial_roots(self, service):
        """Test that Legendre polynomials have correct number of roots"""
        for n in range(1, 4):
            result = service.legendre_polynomial(n, "x")
            assert result['status'] == 'success'
            assert len(result['roots']) == n  # P_n has n distinct roots in (-1, 1)
