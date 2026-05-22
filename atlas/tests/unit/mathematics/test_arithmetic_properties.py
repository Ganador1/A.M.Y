"""
Property-Based Tests for Arithmetic Operations

Uses Hypothesis library to generate test cases automatically and verify
mathematical properties hold for arbitrary inputs.

ROADMAP 1: TESTING & QUALITY - Phase 3.1
Created: 2025-10-01
"""

import math
import decimal
from decimal import Decimal

import pytest
from hypothesis import assume, example, given
from hypothesis import strategies as st


# Arithmetic property tests
class TestArithmeticCommutativeProperty:
    """Test commutative property: a + b = b + a, a * b = b * a"""

    @given(st.integers(), st.integers())
    def test_addition_is_commutative(self, a: int, b: int):
        """Addition should be commutative for all integers."""
        assert a + b == b + a

    @given(st.floats(allow_nan=False, allow_infinity=False), st.floats(allow_nan=False, allow_infinity=False))
    def test_float_addition_is_commutative(self, a: float, b: float):
        """Addition should be commutative for floats (excluding NaN/Inf)."""
        assert math.isclose(a + b, b + a, rel_tol=1e-9, abs_tol=1e-9)

    @given(st.integers(), st.integers())
    def test_multiplication_is_commutative(self, a: int, b: int):
        """Multiplication should be commutative for all integers."""
        assert a * b == b * a

    @given(st.decimals(allow_nan=False, allow_infinity=False), st.decimals(allow_nan=False, allow_infinity=False))
    def test_decimal_multiplication_is_commutative(self, a: Decimal, b: Decimal):
        """Multiplication should be commutative for decimals."""
        assert a * b == b * a


class TestArithmeticAssociativeProperty:
    """Test associative property: (a + b) + c = a + (b + c)"""

    @given(st.integers(), st.integers(), st.integers())
    def test_addition_is_associative(self, a: int, b: int, c: int):
        """Addition should be associative for all integers."""
        assert (a + b) + c == a + (b + c)

    @given(st.integers(), st.integers(), st.integers())
    def test_multiplication_is_associative(self, a: int, b: int, c: int):
        """Multiplication should be associative for all integers."""
        assert (a * b) * c == a * (b * c)

    @given(
        st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False),
        st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
    )
    def test_float_addition_is_approximately_associative(self, a: float, b: float, c: float):
        """Addition should be approximately associative for floats."""
        left = (a + b) + c
        right = a + (b + c)
        assert math.isclose(left, right, rel_tol=1e-6, abs_tol=1e-6)


class TestArithmeticIdentityProperty:
    """Test identity property: a + 0 = a, a * 1 = a"""

    @given(st.integers())
    def test_addition_identity(self, a: int):
        """Adding zero should not change the value."""
        assert a + 0 == a
        assert 0 + a == a

    @given(st.integers())
    def test_multiplication_identity(self, a: int):
        """Multiplying by one should not change the value."""
        assert a * 1 == a
        assert 1 * a == a

    @given(st.floats(allow_nan=False, allow_infinity=False))
    def test_float_addition_identity(self, a: float):
        """Adding zero to float should not change the value."""
        assert math.isclose(a + 0.0, a, rel_tol=1e-9, abs_tol=1e-9)


class TestArithmeticInverseProperty:
    """Test inverse property: a + (-a) = 0, a * (1/a) = 1"""

    @given(st.integers())
    def test_additive_inverse(self, a: int):
        """Adding the opposite should give zero."""
        assert a + (-a) == 0
        assert (-a) + a == 0

    @given(st.integers(min_value=1, max_value=1000000))
    def test_multiplicative_inverse(self, a: int):
        """Multiplying by reciprocal should give one (for non-zero)."""
        assume(a != 0)
        result = a * (1 / a)
        assert math.isclose(result, 1.0, rel_tol=1e-9)

    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    def test_float_additive_inverse(self, a: float):
        """Float additive inverse property."""
        result = a + (-a)
        assert math.isclose(result, 0.0, abs_tol=1e-9)


class TestArithmeticDistributiveProperty:
    """Test distributive property: a * (b + c) = (a * b) + (a * c)"""

    @given(st.integers(), st.integers(), st.integers())
    def test_multiplication_over_addition(self, a: int, b: int, c: int):
        """Multiplication should distribute over addition."""
        assert a * (b + c) == (a * b) + (a * c)

    @given(
        st.integers(min_value=-1000, max_value=1000),
        st.integers(min_value=-1000, max_value=1000),
        st.integers(min_value=-1000, max_value=1000)
    )
    def test_distributive_property_bounded(self, a: int, b: int, c: int):
        """Distributive property with bounded integers."""
        left = a * (b + c)
        right = (a * b) + (a * c)
        assert left == right

    @given(
        st.decimals(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False),
        st.decimals(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False),
        st.decimals(min_value=-1e10, max_value=1e10, allow_nan=False, allow_infinity=False)
    )
    def test_decimal_distributive_property(self, a: Decimal, b: Decimal, c: Decimal):
        """Distributive property for decimal numbers with bounded range and higher precision."""
        with decimal.localcontext() as ctx:
            ctx.prec = 100
            left = a * (b + c)
            right = (a * b) + (a * c)
            # Use normalize to compare regardless of internal representation
            assert left.normalize() == right.normalize()


class TestDivisionProperties:
    """Test division-specific properties."""

    @given(st.integers(min_value=1), st.integers(min_value=1))
    def test_division_identity(self, a: int, b: int):
        """Division properties for positive integers."""
        assume(b != 0)
        # (a // b) * b + (a % b) should be a
        assert (a // b) * b + (a % b) == a

    @given(st.integers(min_value=1, max_value=1000000))
    def test_self_division(self, a: int):
        """Any number divided by itself equals 1."""
        assume(a != 0)
        assert a // a == 1

    @given(st.integers())
    def test_division_by_one(self, a: int):
        """Division by 1 returns the same number."""
        assert a // 1 == a

    @given(st.integers())
    def test_zero_divided_by_nonzero(self, a: int):
        """Zero divided by any non-zero number is zero."""
        assume(a != 0)
        assert 0 // a == 0


class TestPowerProperties:
    """Test exponentiation properties."""

    @given(st.integers(min_value=0, max_value=100))
    def test_power_of_zero(self, n: int):
        """Zero raised to any positive power is zero."""
        assume(n > 0)
        assert 0 ** n == 0

    @given(st.integers(min_value=-100, max_value=100))
    def test_power_of_one(self, n: int):
        """One raised to any power is one."""
        assert 1 ** n == 1

    @given(st.integers(min_value=1, max_value=10))
    def test_any_number_power_zero(self, a: int):
        """Any non-zero number raised to power 0 is 1."""
        assert a ** 0 == 1

    @given(st.integers(min_value=1, max_value=100), st.integers(min_value=1, max_value=5), st.integers(min_value=1, max_value=5))
    def test_power_multiplication_property(self, a: int, m: int, n: int):
        """a^m * a^n = a^(m+n)"""
        left = (a ** m) * (a ** n)
        right = a ** (m + n)
        assert left == right

    @given(st.integers(min_value=1, max_value=10), st.integers(min_value=1, max_value=3), st.integers(min_value=1, max_value=3))
    def test_power_of_power_property(self, a: int, m: int, n: int):
        """(a^m)^n = a^(m*n)"""
        left = (a ** m) ** n
        right = a ** (m * n)
        assert left == right


class TestAbsoluteValueProperties:
    """Test absolute value properties."""

    @given(st.integers())
    def test_absolute_value_non_negative(self, a: int):
        """Absolute value is always non-negative."""
        assert abs(a) >= 0

    @given(st.integers())
    def test_absolute_value_of_negative(self, a: int):
        """abs(-a) = abs(a)"""
        assert abs(-a) == abs(a)

    @given(st.integers(), st.integers())
    def test_absolute_value_triangle_inequality(self, a: int, b: int):
        """Triangle inequality: |a + b| <= |a| + |b|"""
        assert abs(a + b) <= abs(a) + abs(b)

    @given(st.integers(), st.integers())
    def test_absolute_value_multiplicative(self, a: int, b: int):
        """abs(a * b) = abs(a) * abs(b)"""
        assert abs(a * b) == abs(a) * abs(b)


class TestModuloProperties:
    """Test modulo operation properties."""

    @given(st.integers(), st.integers(min_value=1))
    def test_modulo_range(self, a: int, b: int):
        """Result of a % b should be in range [0, b)."""
        result = a % b
        assert 0 <= result < b

    @given(st.integers(min_value=1), st.integers(min_value=1))
    def test_division_modulo_relationship(self, a: int, b: int):
        """Relationship between division and modulo."""
        quotient = a // b
        remainder = a % b
        assert a == (quotient * b) + remainder

    @given(st.integers())
    def test_modulo_by_one(self, a: int):
        """Any number modulo 1 is 0."""
        assert a % 1 == 0


class TestComparisonProperties:
    """Test comparison operation properties."""

    @given(st.integers())
    def test_equality_reflexive(self, a: int):
        """Equality is reflexive: a == a"""
        assert a == a

    @given(st.integers(), st.integers())
    def test_equality_symmetric(self, a: int, b: int):
        """Equality is symmetric: if a == b then b == a"""
        if a == b:
            assert b == a

    @given(st.integers(), st.integers(), st.integers())
    def test_equality_transitive(self, a: int, b: int, c: int):
        """Equality is transitive: if a == b and b == c then a == c"""
        if a == b and b == c:
            assert a == c

    @given(st.integers())
    def test_less_than_irreflexive(self, a: int):
        """Less-than is irreflexive: not (a < a)"""
        assert not (a < a)

    @given(st.integers(), st.integers(), st.integers())
    def test_less_than_transitive(self, a: int, b: int, c: int):
        """Less-than is transitive: if a < b and b < c then a < c"""
        if a < b and b < c:
            assert a < c


# Edge case tests with specific examples
class TestArithmeticEdgeCases:
    """Test edge cases for arithmetic operations."""

    @given(st.integers())
    @example(0)
    @example(1)
    @example(-1)
    @example(2**31 - 1)  # Max 32-bit int
    @example(-(2**31))   # Min 32-bit int
    def test_special_values_addition(self, a: int):
        """Test addition with special values."""
        assert a + 0 == a
        assert 0 + a == a

    @given(st.integers())
    @example(0)
    @example(1)
    @example(-1)
    def test_special_values_multiplication(self, a: int):
        """Test multiplication with special values."""
        assert a * 0 == 0
        assert 0 * a == 0
        assert a * 1 == a
        assert 1 * a == a


# Summary test
def test_arithmetic_properties_summary():
    """Summary of arithmetic property tests."""
    print("\n" + "=" * 60)
    print("🧮 ARITHMETIC PROPERTY-BASED TESTING SUMMARY")
    print("=" * 60)
    print("\n✅ Properties Tested:")
    print("   - Commutative property (addition, multiplication)")
    print("   - Associative property (addition, multiplication)")
    print("   - Identity property (0 for +, 1 for *)")
    print("   - Inverse property (additive, multiplicative)")
    print("   - Distributive property")
    print("   - Division properties")
    print("   - Power properties")
    print("   - Absolute value properties")
    print("   - Modulo properties")
    print("   - Comparison properties")
    print("\n🎯 Test Generation:")
    print("   - Hypothesis generates 100+ test cases per property")
    print("   - Covers integers, floats, decimals")
    print("   - Tests edge cases automatically")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
