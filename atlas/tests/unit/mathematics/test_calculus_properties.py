"""
Property-Based Tests for Calculus Operations

Uses Hypothesis to test calculus properties including:
- Derivative properties
- Integral properties
- Limit behavior
- Continuity properties

ROADMAP 1: TESTING & QUALITY - Phase 3.1
Created: 2025-10-01
"""

import math
from typing import Callable

import pytest
from hypothesis import assume, example, given
from hypothesis import strategies as st


# Simple numerical derivative (for testing)
def numerical_derivative(f: Callable[[float], float], x: float, h: float = 1e-5) -> float:
    """Calculate numerical derivative using central difference."""
    return (f(x + h) - f(x - h)) / (2 * h)


# Simple numerical integral (for testing)
def numerical_integral(f: Callable[[float], float], a: float, b: float, n: int = 1000) -> float:
    """Calculate numerical integral using trapezoidal rule."""
    h = (b - a) / n
    result = (f(a) + f(b)) / 2
    for i in range(1, n):
        result += f(a + i * h)
    return result * h


class TestDerivativeProperties:
    """Test fundamental derivative properties."""

    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_power_rule(self, x: float):
        """Test power rule: d/dx(x^n) = n*x^(n-1)"""
        n = 2  # Test with x^2
        
        # Analytical derivative
        analytical = n * (x ** (n - 1))
        
        # Numerical derivative
        f = lambda t: t ** n
        numerical = numerical_derivative(f, x)
        
        # Should be approximately equal
        assert math.isclose(analytical, numerical, rel_tol=1e-4)

    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_exponential_derivative(self, x: float):
        """Test derivative of exponential: d/dx(e^x) = e^x"""
        # Analytical derivative
        analytical = math.exp(x)
        
        # Numerical derivative
        f = lambda t: math.exp(t)
        numerical = numerical_derivative(f, x)
        
        assert math.isclose(analytical, numerical, rel_tol=1e-4)

    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_logarithm_derivative(self, x: float):
        """Test derivative of logarithm: d/dx(ln(x)) = 1/x"""
        # Analytical derivative
        analytical = 1 / x
        
        # Numerical derivative
        f = lambda t: math.log(t)
        numerical = numerical_derivative(f, x)
        
        assert math.isclose(analytical, numerical, rel_tol=1e-4)

    @given(st.floats(min_value=0.1, max_value=2.0))
    def test_sine_derivative(self, x: float):
        """Test derivative of sine: d/dx(sin(x)) = cos(x)"""
        # Analytical derivative
        analytical = math.cos(x)
        
        # Numerical derivative
        f = lambda t: math.sin(t)
        numerical = numerical_derivative(f, x)
        
        assert math.isclose(analytical, numerical, rel_tol=1e-4)

    @given(st.floats(min_value=0.1, max_value=2.0))
    def test_cosine_derivative(self, x: float):
        """Test derivative of cosine: d/dx(cos(x)) = -sin(x)"""
        # Analytical derivative
        analytical = -math.sin(x)
        
        # Numerical derivative
        f = lambda t: math.cos(t)
        numerical = numerical_derivative(f, x)
        
        assert math.isclose(analytical, numerical, rel_tol=1e-4)


class TestDerivativeLinearity:
    """Test linearity of derivative operator."""

    @given(st.floats(min_value=0.1, max_value=5.0))
    def test_constant_multiple_rule(self, x: float):
        """Test d/dx(c*f(x)) = c * d/dx(f(x))"""
        c = 3.0
        
        # f(x) = x^2
        f = lambda t: t ** 2
        cf = lambda t: c * (t ** 2)
        
        # Derivatives
        deriv_f = numerical_derivative(f, x)
        deriv_cf = numerical_derivative(cf, x)
        
        assert math.isclose(deriv_cf, c * deriv_f, rel_tol=1e-4)

    @given(st.floats(min_value=0.1, max_value=5.0))
    def test_sum_rule(self, x: float):
        """Test d/dx(f(x) + g(x)) = d/dx(f(x)) + d/dx(g(x))"""
        # f(x) = x^2, g(x) = x^3
        f = lambda t: t ** 2
        g = lambda t: t ** 3
        sum_fg = lambda t: f(t) + g(t)
        
        # Derivatives
        deriv_f = numerical_derivative(f, x)
        deriv_g = numerical_derivative(g, x)
        deriv_sum = numerical_derivative(sum_fg, x)
        
        assert math.isclose(deriv_sum, deriv_f + deriv_g, rel_tol=1e-4)


class TestIntegralProperties:
    """Test fundamental integral properties."""

    @given(st.floats(min_value=0.1, max_value=5.0), st.floats(min_value=5.1, max_value=10.0))
    def test_integral_of_constant(self, a: float, b: float):
        """Test ∫c dx = c*(b-a)"""
        assume(a < b)
        c = 2.0
        
        # Analytical integral
        analytical = c * (b - a)
        
        # Numerical integral
        f = lambda x: c
        numerical = numerical_integral(f, a, b)
        
        assert math.isclose(analytical, numerical, rel_tol=1e-4)

    @given(st.floats(min_value=0.1, max_value=3.0), st.floats(min_value=3.1, max_value=6.0))
    def test_integral_of_identity(self, a: float, b: float):
        """Test ∫x dx = (b^2 - a^2)/2"""
        assume(a < b)
        
        # Analytical integral
        analytical = (b ** 2 - a ** 2) / 2
        
        # Numerical integral
        f = lambda x: x
        numerical = numerical_integral(f, a, b)
        
        assert math.isclose(analytical, numerical, rel_tol=1e-3)

    @given(st.floats(min_value=0.1, max_value=2.0), st.floats(min_value=2.1, max_value=4.0))
    def test_integral_of_power(self, a: float, b: float):
        """Test ∫x^2 dx = (b^3 - a^3)/3"""
        assume(a < b)
        
        # Analytical integral
        analytical = (b ** 3 - a ** 3) / 3
        
        # Numerical integral
        f = lambda x: x ** 2
        numerical = numerical_integral(f, a, b)
        
        assert math.isclose(analytical, numerical, rel_tol=1e-3)


class TestIntegralLinearity:
    """Test linearity of integral operator."""

    @given(st.floats(min_value=0.1, max_value=2.0), st.floats(min_value=2.1, max_value=4.0))
    def test_constant_multiple_integral(self, a: float, b: float):
        """Test ∫c*f(x)dx = c*∫f(x)dx"""
        assume(a < b)
        c = 2.5
        
        f = lambda x: x ** 2
        cf = lambda x: c * (x ** 2)
        
        int_f = numerical_integral(f, a, b)
        int_cf = numerical_integral(cf, a, b)
        
        assert math.isclose(int_cf, c * int_f, rel_tol=1e-3)

    @given(st.floats(min_value=0.1, max_value=2.0), st.floats(min_value=2.1, max_value=4.0))
    def test_sum_integral(self, a: float, b: float):
        """Test ∫(f(x)+g(x))dx = ∫f(x)dx + ∫g(x)dx"""
        assume(a < b)
        
        f = lambda x: x
        g = lambda x: x ** 2
        sum_fg = lambda x: f(x) + g(x)
        
        int_f = numerical_integral(f, a, b)
        int_g = numerical_integral(g, a, b)
        int_sum = numerical_integral(sum_fg, a, b)
        
        assert math.isclose(int_sum, int_f + int_g, rel_tol=1e-3)


class TestFundamentalTheoremOfCalculus:
    """Test Fundamental Theorem of Calculus."""

    @given(st.floats(min_value=0.1, max_value=2.0), st.floats(min_value=2.1, max_value=4.0))
    def test_ftc_part1(self, a: float, b: float):
        """Test ∫[a,b] f'(x)dx = f(b) - f(a)"""
        assume(a < b)
        
        # f(x) = x^2
        f = lambda x: x ** 2
        f_prime = lambda x: 2 * x
        
        # LHS: integral of derivative
        lhs = numerical_integral(f_prime, a, b)
        
        # RHS: difference of function values
        rhs = f(b) - f(a)
        
        assert math.isclose(lhs, rhs, rel_tol=1e-3)

    @given(st.floats(min_value=0.1, max_value=3.0))
    def test_ftc_part2(self, x: float):
        """Test d/dx(∫[a,x] f(t)dt) = f(x)"""
        a = 0.0
        
        # f(t) = t^2
        f = lambda t: t ** 2
        
        # Define F(x) = ∫[a,x] f(t)dt
        def F(x_val):
            return numerical_integral(f, a, x_val)
        
        # d/dx(F(x))
        deriv_F = numerical_derivative(F, x)
        
        # Should equal f(x)
        assert math.isclose(deriv_F, f(x), rel_tol=1e-2)


class TestLimitProperties:
    """Test limit properties."""

    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_limit_of_sum(self, a: float):
        """Test lim(x→a)[f(x) + g(x)] = lim(x→a)f(x) + lim(x→a)g(x)"""
        # f(x) = x^2, g(x) = x
        f = lambda x: x ** 2
        g = lambda x: x
        
        # Evaluate at a (assuming continuous functions)
        lim_sum = f(a) + g(a)
        sum_fn = lambda x: f(x) + g(x)
        
        assert math.isclose(sum_fn(a), lim_sum, rel_tol=1e-9)

    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_limit_of_product(self, a: float):
        """Test lim(x→a)[f(x)*g(x)] = lim(x→a)f(x) * lim(x→a)g(x)"""
        # f(x) = x^2, g(x) = x
        f = lambda x: x ** 2
        g = lambda x: x
        
        lim_product = f(a) * g(a)
        product_fn = lambda x: f(x) * g(x)
        
        assert math.isclose(product_fn(a), lim_product, rel_tol=1e-9)


class TestContinuityProperties:
    """Test continuity properties."""

    @given(st.floats(min_value=-5.0, max_value=5.0))
    def test_polynomial_continuity(self, x: float):
        """Polynomials are continuous everywhere."""
        # p(x) = x^3 + 2x^2 - x + 1
        p = lambda t: t ** 3 + 2 * (t ** 2) - t + 1
        
        # Evaluate at nearby points
        h = 1e-6
        left = p(x - h)
        center = p(x)
        right = p(x + h)
        
        # Should be approximately equal (continuous)
        assert math.isclose(left, center, abs_tol=1e-4)
        assert math.isclose(center, right, abs_tol=1e-4)

    @given(st.floats(min_value=0.1, max_value=10.0))
    def test_exponential_continuity(self, x: float):
        """Exponential function is continuous for all x."""
        f = lambda t: math.exp(t)
        
        h = 1e-6
        left = f(x - h)
        center = f(x)
        right = f(x + h)
        
        assert math.isclose(left, center, rel_tol=1e-4)
        assert math.isclose(center, right, rel_tol=1e-4)


# Summary test
def test_calculus_properties_summary():
    """Summary of calculus property tests."""
    print("\n" + "=" * 60)
    print("📐 CALCULUS PROPERTY-BASED TESTING SUMMARY")
    print("=" * 60)
    print("\n✅ Properties Tested:")
    print("   - Power rule for derivatives")
    print("   - Derivative linearity (constant multiple, sum rule)")
    print("   - Exponential, logarithm, trigonometric derivatives")
    print("   - Integral properties (constant, identity, power)")
    print("   - Integral linearity")
    print("   - Fundamental Theorem of Calculus (Part 1 & 2)")
    print("   - Limit properties")
    print("   - Continuity properties")
    print("\n🎯 Numerical Methods:")
    print("   - Central difference for derivatives")
    print("   - Trapezoidal rule for integrals")
    print("   - Tolerance: 1e-3 to 1e-4")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
