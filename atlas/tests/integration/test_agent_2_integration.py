"""
Integration Tests for AXIOM Meta Agent 2 - Mathematical Computation Laboratory
Basic test suite validating core components
"""

import pytest
import sympy as sp

# Import all Agent 2 components
from app.mathlab.objects.elliptic_curve_enhanced import EllipticCurve, EllipticCurvePoint


class TestEllipticCurveIntegration:
    """Test elliptic curve mathematical operations"""

    def test_curve_creation_and_validation(self):
        """Test creating and validating elliptic curves"""
        # Valid curve
        curve = EllipticCurve(a=1, b=1)  # y^2 = x^3 + x + 1
        # The constructor already validates non-singularity
        assert curve.discriminant == -496  # -16(4a^3 + 27b^2) = -16(4 + 27) = -16*31 = -496

    def test_point_operations(self):
        """Test elliptic curve point arithmetic"""
        curve = EllipticCurve(a=1, b=1)

        # Test point on curve
        P = EllipticCurvePoint(sp.Integer(0), sp.Integer(1))
        assert curve.is_on_curve(P)

        # Test point addition
        Q = EllipticCurvePoint(sp.Integer(0), sp.Integer(-1))  # Inverse of P
        o = curve.point_addition(P, Q)  # Should be point at infinity
        assert o.is_infinity


def test_component_imports():
    """Test that all components can be imported successfully"""
    # This test ensures all modules are properly structured
    assert EllipticCurve is not None
    assert EllipticCurvePoint is not None


if __name__ == "__main__":
    # Run specific test groups
    print("🧪 Running Agent 2 Integration Tests")
    print("=" * 50)

    # You can run with: python -m pytest tests/integration/test_agent_2_integration.py -v
    pytest.main([__file__, "-v", "--tb=short"])
