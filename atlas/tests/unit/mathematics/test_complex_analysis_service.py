"""
Unit tests for Complex Analysis Service
"""

import pytest
from unittest.mock import patch
from app.services.complex_analysis_service import ComplexAnalysisService


class TestComplexAnalysisService:
    """Test cases for ComplexAnalysisService"""

    @pytest.fixture
    def service(self):
        """Fixture for ComplexAnalysisService instance"""
        return ComplexAnalysisService()

    def test_power_series_expansion_simple_polynomial(self, service):
        """Test power series expansion of a simple polynomial"""
        result = service.power_series_expansion("1/(1-z)", "z", "0", 6)

        assert result["status"] == "success"
        assert "function" in result
        assert "power_series" in result
        assert "coefficients" in result
        assert result["variable"] == "z"
        assert result["expansion_point"] == "0"

    def test_power_series_expansion_exponential(self, service):
        """Test power series expansion of exponential function"""
        result = service.power_series_expansion("exp(z)", "z", "0", 5)

        assert result["status"] == "success"
        assert "exp(z)" in result["function"]
        assert len(result["coefficients"]) > 0

    def test_power_series_expansion_invalid_function(self, service):
        """Test power series expansion with invalid function"""
        result = service.power_series_expansion("1/(1-x)", "z", "0", 6)

        assert result["status"] == "failed"
        assert "error" in result

    def test_residue_calculation_simple_pole(self, service):
        """Test residue calculation at a simple pole"""
        result = service.residue_calculation("1/(z-1)", "1", "z")

        assert result["status"] == "success"
        assert "residue" in result
        assert "laurent_series" in result
        assert result["pole"] == "1"

    def test_residue_calculation_invalid_function(self, service):
        """Test residue calculation with invalid function"""
        result = service.residue_calculation("1/(1-x)", "0", "z")

        assert result["status"] == "failed"
        assert "error" in result

    def test_contour_integral_circle(self, service):
        """Test contour integral along a circle"""
        result = service.contour_integral("1/z", "circle", "0", "1", "z")

        assert result["status"] == "success"
        assert result["contour_type"] == "circle"
        assert "integral_value" in result
        assert result["method"] == "Residue theorem"

    def test_contour_integral_invalid_contour(self, service):
        """Test contour integral with invalid contour type"""
        result = service.contour_integral("1/z", "square", "0", "1", "z")

        assert result["status"] == "unsupported"
        assert "error" in result
        assert "available_types" in result

    def test_bessel_function_first_kind(self, service):
        """Test Bessel function of the first kind"""
        result = service.bessel_function(0, "1", "J")

        assert result["status"] == "success"
        assert result["function_type"] == "J"
        assert result["order"] == 0
        assert "result" in result
        assert "plot" in result

    def test_bessel_function_second_kind(self, service):
        """Test Bessel function of the second kind"""
        result = service.bessel_function(1, "2", "Y")

        assert result["status"] == "success"
        assert result["function_type"] == "Y"
        assert result["order"] == 1

    def test_bessel_function_modified_first_kind(self, service):
        """Test modified Bessel function of the first kind"""
        result = service.bessel_function(0, "1.5", "I")

        assert result["status"] == "success"
        assert result["function_type"] == "I"

    def test_bessel_function_invalid_type(self, service):
        """Test Bessel function with invalid type"""
        result = service.bessel_function(1, "1", "X")

        assert result["status"] == "invalid_type"
        assert "error" in result
        assert "available_types" in result

    def test_legendre_polynomial_degree_0(self, service):
        """Test Legendre polynomial of degree 0"""
        result = service.legendre_polynomial(0, "x")

        assert result["status"] == "success"
        assert result["degree"] == 0
        assert "legendre_polynomial" in result
        assert "roots" in result
        assert "plot" in result

    def test_legendre_polynomial_degree_2(self, service):
        """Test Legendre polynomial of degree 2"""
        result = service.legendre_polynomial(2, "x")

        assert result["status"] == "success"
        assert result["degree"] == 2
        assert len(result["roots"]) == 2  # P_2(x) has 2 roots

    def test_legendre_polynomial_invalid_degree(self, service):
        """Test Legendre polynomial with invalid degree"""
        result = service.legendre_polynomial(-1, "x")

        assert result["status"] == "failed"
        assert "error" in result

    def test_hermite_polynomial_degree_0(self, service):
        """Test Hermite polynomial of degree 0"""
        result = service.hermite_polynomial(0, "x")

        assert result["status"] == "success"
        assert result["degree"] == 0
        assert "hermite_polynomial" in result
        assert "plot" in result

    def test_hermite_polynomial_degree_3(self, service):
        """Test Hermite polynomial of degree 3"""
        result = service.hermite_polynomial(3, "x")

        assert result["status"] == "success"
        assert result["degree"] == 3

    def test_series_convergence_ratio_test(self, service):
        """Test series convergence using ratio test"""
        result = service.series_convergence_test("1/n**2", "n", "ratio")

        assert result["status"] == "success"
        assert "result" in result
        assert result["test_type"] == "ratio"

    def test_series_convergence_root_test(self, service):
        """Test series convergence using root test"""
        result = service.series_convergence_test("1/n", "n", "root")

        assert result["status"] == "success"
        assert "result" in result
        assert result["test_type"] == "root"

    def test_series_convergence_invalid_test(self, service):
        """Test series convergence with invalid test type"""
        result = service.series_convergence_test("1/n", "n", "invalid")

        assert result["status"] == "invalid_test"
        assert "error" in result
        assert "available_tests" in result

    def test_analytic_continuation(self, service):
        """Test analytic continuation"""
        result = service.analytic_continuation("sqrt(z)", "|z| < 1", "|z| < ∞", "z")

        assert result["status"] == "success"
        assert result["function"] == "sqrt(z)"
        assert "method" in result

    def test_get_series_examples(self, service):
        """Test getting series examples"""
        result = service.get_series_examples()

        assert "series" in result
        assert "description" in result
        assert "count" in result
        assert result["count"] == 4  # geometric, exponential, sine, cosine
        assert "geometric" in result["series"]
        assert "exponential" in result["series"]

    @patch('matplotlib.pyplot.savefig')
    def test_bessel_function_plotting(self, mock_savefig, service):
        """Test that plotting works for Bessel functions"""
        mock_savefig.return_value = None

        result = service.bessel_function(1, "2", "J")

        assert result["status"] == "success"
        assert result["plot"] is not None
        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    def test_legendre_polynomial_plotting(self, mock_savefig, service):
        """Test that plotting works for Legendre polynomials"""
        mock_savefig.return_value = None

        result = service.legendre_polynomial(2, "x")

        assert result["status"] == "success"
        assert result["plot"] is not None
        mock_savefig.assert_called_once()

    @patch('matplotlib.pyplot.savefig')
    def test_hermite_polynomial_plotting(self, mock_savefig, service):
        """Test that plotting works for Hermite polynomials"""
        mock_savefig.return_value = None

        result = service.hermite_polynomial(1, "x")

        assert result["status"] == "success"
        assert result["plot"] is not None
        mock_savefig.assert_called_once()

    def test_power_series_expansion_edge_cases(self, service):
        """Test power series expansion with edge cases"""
        # Test with very high order
        result = service.power_series_expansion("sin(z)", "z", "0", 10)
        assert result["status"] == "success"

        # Test with non-zero center
        result = service.power_series_expansion("exp(z)", "z", "1", 5)
        assert result["status"] == "success"

    def test_residue_calculation_edge_cases(self, service):
        """Test residue calculation with edge cases"""
        # Test with pole at origin
        result = service.residue_calculation("1/z", "0", "z")
        assert result["status"] == "success"

        # Test with complex pole
        result = service.residue_calculation("1/(z - I)", "I", "z")
        assert result["status"] == "success"

    def test_error_handling(self, service):
        """Test error handling in various methods"""
        # Test with invalid mathematical expression
        result = service.power_series_expansion("invalid_function", "z", "0", 5)
        assert result["status"] == "failed"

        # Test with invalid residue function
        result = service.residue_calculation("invalid", "0", "z")
        assert result["status"] == "failed"

        # Test with invalid contour integral
        result = service.contour_integral("invalid", "circle", "0", "1", "z")
        assert result["status"] == "failed"
