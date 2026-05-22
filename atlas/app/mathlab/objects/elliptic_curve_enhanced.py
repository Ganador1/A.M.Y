"""
Enhanced Elliptic Curve implementation for AXIOM Mathematical Laboratory
Provides comprehensive elliptic curve operations, invariants, and analysis
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any
from fractions import Fraction
import sympy as sp
from sympy import symbols, gcd, factor, simplify
from sympy.ntheory import isprime, primefactors
import logging

logger = logging.getLogger(__name__)


@dataclass
class EllipticCurvePoint:
    """Point on an elliptic curve"""
    x: Optional[sp.Expr]
    y: Optional[sp.Expr]
    is_infinity: bool = False
    
    def __post_init__(self):
        if not self.is_infinity and (self.x is None or self.y is None):
            raise ValueError("Non-infinity point must have x and y coordinates")
    
    def __str__(self) -> str:
        if self.is_infinity:
            return "O (point at infinity)"
        return f"({self.x}, {self.y})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, EllipticCurvePoint):
            return False
        if self.is_infinity and other.is_infinity:
            return True
        if self.is_infinity or other.is_infinity:
            return False
        return self.x == other.x and self.y == other.y


class EllipticCurve:
    """
    Enhanced elliptic curve class supporting:
    - Weierstrass form: y² = x³ + ax + b
    - Point operations (addition, multiplication)
    - Invariant computations
    - Torsion analysis
    - Rank estimation
    """
    
    def __init__(self, a: int, b: int, field_char: int = 0):
        """
        Initialize elliptic curve y² = x³ + ax + b
        
        Args:
            a: Coefficient of x
            b: Constant term
            field_char: Field characteristic (0 for rationals)
        """
        self.a = sp.Integer(a)
        self.b = sp.Integer(b)
        self.field_char = field_char
        
        # Verify non-singular
        discriminant = -16 * (4 * a**3 + 27 * b**2)
        if discriminant == 0:
            raise ValueError(f"Singular curve: discriminant = 0 for a={a}, b={b}")
        
        self._discriminant = discriminant
        self._j_invariant = None
        self._torsion_points = None
        self._rank_estimate = None
        
        # For canonical representation
        self._canonical_hash = None
    
    @property
    def discriminant(self) -> sp.Integer:
        """Compute discriminant Δ = -16(4a³ + 27b²)"""
        return self._discriminant
    
    @property
    def j_invariant(self) -> sp.Rational:
        """Compute j-invariant j = -1728(4a)³/Δ"""
        if self._j_invariant is None:
            numerator = -1728 * (4 * self.a)**3
            self._j_invariant = sp.Rational(numerator, self.discriminant)
        return self._j_invariant
    
    @property
    def c4(self) -> sp.Integer:
        """Compute c₄ = -48a"""
        return -48 * self.a
    
    @property
    def c6(self) -> sp.Integer:
        """Compute c₆ = -864b"""
        return -864 * self.b
    
    def canonical_hash(self) -> str:
        """Generate canonical hash for the curve"""
        if self._canonical_hash is None:
            # Use j-invariant and discriminant for canonical representation
            data = f"j={self.j_invariant},delta={self.discriminant}"
            self._canonical_hash = hashlib.sha256(data.encode()).hexdigest()[:16]
        return self._canonical_hash
    
    def is_on_curve(self, point: EllipticCurvePoint) -> bool:
        """Check if point lies on the curve"""
        if point.is_infinity:
            return True
        
        x, y = point.x, point.y
        left_side = y**2
        right_side = x**3 + self.a * x + self.b
        
        return simplify(left_side - right_side) == 0
    
    def point_addition(self, P: EllipticCurvePoint, Q: EllipticCurvePoint) -> EllipticCurvePoint:
        """Add two points on the elliptic curve"""
        # Handle infinity cases
        if P.is_infinity:
            return Q
        if Q.is_infinity:
            return P
        
        x1, y1 = P.x, P.y
        x2, y2 = Q.x, Q.y
        
        # Same x-coordinate cases
        if x1 == x2:
            if y1 == -y2:
                # P + (-P) = O
                return EllipticCurvePoint(None, None, is_infinity=True)
            elif y1 == y2:
                # Point doubling: P + P
                return self._point_doubling(P)
        
        # General case: P + Q where P ≠ ±Q
        slope = (y2 - y1) / (x2 - x1)
        x3 = slope**2 - x1 - x2
        y3 = slope * (x1 - x3) - y1
        
        return EllipticCurvePoint(simplify(x3), simplify(y3))
    
    def _point_doubling(self, P: EllipticCurvePoint) -> EllipticCurvePoint:
        """Double a point: compute 2P"""
        if P.is_infinity:
            return P
        
        x, y = P.x, P.y
        
        # Check for point of order 2
        if y == 0:
            return EllipticCurvePoint(None, None, is_infinity=True)
        
        # Compute slope: λ = (3x² + a) / (2y)
        slope = (3 * x**2 + self.a) / (2 * y)
        
        # New coordinates
        x3 = slope**2 - 2 * x
        y3 = slope * (x - x3) - y
        
        return EllipticCurvePoint(simplify(x3), simplify(y3))
    
    def scalar_multiplication(self, k: int, P: EllipticCurvePoint) -> EllipticCurvePoint:
        """Compute k*P using binary method"""
        if k == 0 or P.is_infinity:
            return EllipticCurvePoint(None, None, is_infinity=True)
        
        if k < 0:
            # k*P = (-k)*(-P)
            neg_P = EllipticCurvePoint(P.x, -P.y) if not P.is_infinity else P
            return self.scalar_multiplication(-k, neg_P)
        
        # Binary method
        result = EllipticCurvePoint(None, None, is_infinity=True)
        addend = P
        
        while k > 0:
            if k & 1:  # k is odd
                result = self.point_addition(result, addend)
            addend = self.point_addition(addend, addend)  # Double
            k >>= 1  # k //= 2
        
        return result
    
    def find_rational_points(self, search_bound: int = 100) -> List[EllipticCurvePoint]:
        """Find rational points with bounded coordinates"""
        points = []
        
        for x_num in range(-search_bound, search_bound + 1):
            for x_den in range(1, search_bound + 1):
                if gcd(x_num, x_den) > 1:
                    continue  # Skip non-reduced fractions
                
                x = sp.Rational(x_num, x_den)
                y_squared = x**3 + self.a * x + self.b
                
                # Check if y_squared is a perfect square
                if y_squared.is_rational:
                    y_float = float(y_squared)
                    if y_float >= 0:
                        y_sqrt = sp.sqrt(y_squared)
                        if y_sqrt.is_rational:
                            # Found rational point
                            points.append(EllipticCurvePoint(x, y_sqrt))
                            if y_sqrt != 0:
                                points.append(EllipticCurvePoint(x, -y_sqrt))
        
        return points
    
    def compute_torsion_points(self, max_order: int = 12) -> List[EllipticCurvePoint]:
        """Find torsion points up to given order"""
        if self._torsion_points is not None:
            return self._torsion_points
        
        torsion_points = []
        rational_points = self.find_rational_points(50)
        
        for point in rational_points:
            if point.is_infinity:
                continue
                
            # Check if point has finite order
            for order in range(2, max_order + 1):
                multiple = self.scalar_multiplication(order, point)
                if multiple.is_infinity:
                    torsion_points.append((point, order))
                    break
        
        self._torsion_points = torsion_points
        return torsion_points
    
    def estimate_rank(self) -> Dict[str, Any]:
        """Estimate the rank using various methods"""
        if self._rank_estimate is not None:
            return self._rank_estimate
        
        # Method 1: Count independent rational points
        rational_points = self.find_rational_points(100)
        non_torsion_points = []
        
        # Filter out torsion points
        torsion_points = [pt for pt, _ in self.compute_torsion_points()]
        
        for point in rational_points:
            is_torsion = any(
                point.x == tpt.x and point.y == tpt.y 
                for tpt in torsion_points
            )
            if not is_torsion and not point.is_infinity:
                non_torsion_points.append(point)
        
        # Estimate rank from linear independence
        estimated_rank = min(len(non_torsion_points), 3)  # Conservative estimate
        
        # Method 2: Use discriminant heuristic
        disc_factors = len(primefactors(abs(self.discriminant)))
        heuristic_rank = max(0, disc_factors - 2)
        
        self._rank_estimate = {
            "estimated_rank": estimated_rank,
            "heuristic_rank": heuristic_rank,
            "rational_points_found": len(rational_points),
            "non_torsion_points": len(non_torsion_points),
            "confidence": "low" if estimated_rank != heuristic_rank else "medium"
        }
        
        return self._rank_estimate
    
    def conductor_estimate(self) -> int:
        """Estimate the conductor (simplified version)"""
        # Rough estimate based on discriminant
        disc_abs = abs(self.discriminant)
        
        # Factor discriminant and compute rough conductor
        factors = primefactors(disc_abs)
        conductor = 1
        
        for p in factors:
            # Simplified Tate algorithm approximation
            v_p = 0
            temp = disc_abs
            while temp % p == 0:
                temp //= p
                v_p += 1
            
            if v_p >= 4:
                conductor *= p**2
            elif v_p >= 2:
                conductor *= p
        
        return conductor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "a": int(self.a),
            "b": int(self.b),
            "discriminant": int(self.discriminant),
            "j_invariant": str(self.j_invariant),
            "canonical_hash": self.canonical_hash(),
            "field_char": self.field_char,
            "invariants": {
                "c4": int(self.c4),
                "c6": int(self.c6),
                "conductor_estimate": self.conductor_estimate()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EllipticCurve:
        """Create elliptic curve from dictionary"""
        return cls(
            a=data["a"],
            b=data["b"],
            field_char=data.get("field_char", 0)
        )
    
    def __str__(self) -> str:
        return f"y² = x³ + {self.a}x + {self.b}"
    
    def __repr__(self) -> str:
        return f"EllipticCurve(a={self.a}, b={self.b})"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, EllipticCurve):
            return False
        return self.a == other.a and self.b == other.b
    
    def __hash__(self) -> int:
        return hash((int(self.a), int(self.b)))


# Utility functions for elliptic curve operations
def generate_random_curves(count: int, param_bound: int = 100) -> List[EllipticCurve]:
    """Generate random non-singular elliptic curves"""
    import random
    
    curves = []
    attempts = 0
    max_attempts = count * 10
    
    while len(curves) < count and attempts < max_attempts:
        a = random.randint(-param_bound, param_bound)
        b = random.randint(-param_bound, param_bound)
        
        try:
            curve = EllipticCurve(a, b)
            curves.append(curve)
        except ValueError:
            # Skip singular curves
            pass
        
        attempts += 1
    
    return curves


def curves_with_good_properties(max_discriminant: int = 10000) -> List[EllipticCurve]:
    """Generate curves with interesting mathematical properties"""
    interesting_curves = []
    
    # Some well-known curves with special properties
    special_curves = [
        (0, -1),    # y² = x³ - 1 (has rational points)
        (-1, 0),    # y² = x³ - x (rank 0)
        (-2, 1),    # y² = x³ - 2x + 1 (rank 1)
        (0, -2),    # y² = x³ - 2
        (-4, 4),    # y² = x³ - 4x + 4 (rank 0)
        (1, 0),     # y² = x³ + x
        (0, 1),     # y² = x³ + 1
        (-1, 1),    # y² = x³ - x + 1
    ]
    
    for a, b in special_curves:
        try:
            curve = EllipticCurve(a, b)
            if abs(curve.discriminant) <= max_discriminant:
                interesting_curves.append(curve)
        except ValueError:
            continue
    
    return interesting_curves


if __name__ == "__main__":
    # Demo of elliptic curve functionality
    print("🔮 Elliptic Curve Demo")
    print("=" * 50)
    
    # Create a curve
    curve = EllipticCurve(-2, 1)  # y² = x³ - 2x + 1
    print(f"Curve: {curve}")
    print(f"Discriminant: {curve.discriminant}")
    print(f"j-invariant: {curve.j_invariant}")
    
    # Find rational points
    points = curve.find_rational_points(20)
    print(f"\nRational points found: {len(points)}")
    for i, pt in enumerate(points[:5]):
        print(f"  P_{i+1}: {pt}")
    
    # Analyze torsion
    torsion = curve.compute_torsion_points()
    print(f"\nTorsion points: {len(torsion)}")
    for pt, order in torsion:
        print(f"  {pt} has order {order}")
    
    # Rank estimation
    rank_info = curve.estimate_rank()
    print(f"\nRank estimation: {rank_info}")
