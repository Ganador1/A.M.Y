"""
Elliptic Curve Invariants Analyzer for AXIOM Mathematical Laboratory
Computes comprehensive mathematical invariants for elliptic curves
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from fractions import Fraction
import sympy as sp
from sympy import symbols, factor, primefactors, gcd, sqrt, Integer
from sympy.ntheory import isprime, factorint

from ..objects.elliptic_curve_enhanced import EllipticCurve, EllipticCurvePoint

logger = logging.getLogger(__name__)


@dataclass
class TorsionStructure:
    """Torsion subgroup structure"""
    points: List[Tuple[EllipticCurvePoint, int]]
    structure: str  # e.g., "Z/2Z × Z/2Z"
    order: int
    generators: List[EllipticCurvePoint]
    is_cyclic: bool


@dataclass 
class RankData:
    """Rank estimation data"""
    analytic_rank: Optional[int]
    algebraic_rank: Optional[int]
    estimated_rank: int
    confidence: float
    method_used: str
    rational_points: List[EllipticCurvePoint]
    regulator: Optional[float]


@dataclass
class ReductionData:
    """Bad reduction analysis"""
    prime: int
    reduction_type: str  # "additive", "split_multiplicative", "non_split_multiplicative"
    kodaira_symbol: str
    tamagawa_number: int
    local_contribution: float


@dataclass
class EllipticCurveInvariants:
    """Complete collection of elliptic curve invariants"""
    curve: EllipticCurve
    j_invariant: sp.Rational
    discriminant: sp.Integer
    c4: sp.Integer
    c6: sp.Integer
    conductor: int
    torsion: TorsionStructure
    rank_data: RankData
    bad_reduction: List[ReductionData]
    periods: Optional[Tuple[complex, complex]]
    l_function_data: Dict[str, Any]
    modular_form_level: Optional[int]
    
    # Classification
    cm_discriminant: Optional[int]  # Complex multiplication
    is_cm: bool
    endomorphism_ring: str
    
    # Special properties
    has_rational_2_torsion: bool
    has_isogeny_3: bool
    has_isogeny_5: bool
    
    # Computational metadata
    computation_time: float
    reliability_score: float


class EllipticCurveInvariantAnalyzer:
    """Comprehensive analyzer for elliptic curve invariants"""
    
    def __init__(self):
        self.cache = {}
        self.known_cm_discriminants = [-3, -4, -7, -8, -11, -12, -16, -19, -27, -28]
    
    async def analyze_curve(self, curve: EllipticCurve, 
                          deep_analysis: bool = True) -> EllipticCurveInvariants:
        """Perform comprehensive invariant analysis"""
        import time
        start_time = time.time()
        
        # Check cache
        cache_key = (curve.a, curve.b)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        logger.info(f"Analyzing curve {curve}")
        
        # Basic invariants
        j_inv = curve.j_invariant
        discriminant = curve.discriminant
        c4 = curve.c4
        c6 = curve.c6
        
        # Torsion analysis
        torsion_structure = await self._analyze_torsion(curve)
        
        # Rank analysis
        rank_data = await self._analyze_rank(curve, deep_analysis)
        
        # Conductor and bad reduction
        conductor, bad_reduction = await self._analyze_conductor(curve)
        
        # Complex multiplication
        cm_disc, is_cm = self._analyze_cm(curve)
        
        # L-function data (placeholder for now)
        l_func_data = await self._analyze_l_function(curve)
        
        # Special properties
        special_props = self._analyze_special_properties(curve, torsion_structure)
        
        # Periods (advanced computation - placeholder)
        periods = None
        if deep_analysis:
            periods = await self._compute_periods(curve)
        
        computation_time = time.time() - start_time
        
        invariants = EllipticCurveInvariants(
            curve=curve,
            j_invariant=j_inv,
            discriminant=discriminant,
            c4=c4,
            c6=c6,
            conductor=conductor,
            torsion=torsion_structure,
            rank_data=rank_data,
            bad_reduction=bad_reduction,
            periods=periods,
            l_function_data=l_func_data,
            modular_form_level=conductor,  # Simplified
            cm_discriminant=cm_disc,
            is_cm=is_cm,
            endomorphism_ring="Z" if not is_cm else f"Z[√{cm_disc}]",
            has_rational_2_torsion=special_props["has_2_torsion"],
            has_isogeny_3=special_props["has_3_isogeny"],
            has_isogeny_5=special_props["has_5_isogeny"],
            computation_time=computation_time,
            reliability_score=self._compute_reliability(rank_data, torsion_structure)
        )
        
        # Cache result
        self.cache[cache_key] = invariants
        return invariants
    
    async def _analyze_torsion(self, curve: EllipticCurve) -> TorsionStructure:
        """Analyze torsion subgroup structure"""
        torsion_points = curve.compute_torsion_points(16)
        
        if not torsion_points:
            return TorsionStructure(
                points=[],
                structure="trivial",
                order=1,
                generators=[],
                is_cyclic=True
            )
        
        # Analyze structure
        orders = [order for _, order in torsion_points]
        max_order = max(orders) if orders else 1
        
        # Count points of each order
        order_counts = {}
        for _, order in torsion_points:
            order_counts[order] = order_counts.get(order, 0) + 1
        
        # Determine structure type
        structure_str = self._determine_torsion_structure(order_counts, max_order)
        
        # Find generators
        generators = self._find_torsion_generators(torsion_points, curve)
        
        return TorsionStructure(
            points=torsion_points,
            structure=structure_str,
            order=len(torsion_points) + 1,  # +1 for identity
            generators=generators,
            is_cyclic=len(generators) <= 1
        )
    
    def _determine_torsion_structure(self, order_counts: Dict[int, int], 
                                   max_order: int) -> str:
        """Determine torsion group structure"""
        if max_order == 1:
            return "trivial"
        
        # Common cases
        if max_order == 2:
            count_2 = order_counts.get(2, 0)
            if count_2 == 1:
                return "Z/2Z"
            elif count_2 == 3:
                return "Z/2Z × Z/2Z"
        
        elif max_order == 3:
            return "Z/3Z"
        
        elif max_order == 4:
            return "Z/4Z"
        
        elif max_order == 5:
            return "Z/5Z"
        
        elif max_order == 6:
            return "Z/6Z"
        
        elif max_order == 7:
            return "Z/7Z"
        
        elif max_order == 8:
            return "Z/8Z"
        
        elif max_order == 9:
            return "Z/9Z"
        
        elif max_order == 10:
            return "Z/10Z"
        
        elif max_order == 12:
            return "Z/12Z"
        
        return f"Z/{max_order}Z"
    
    def _find_torsion_generators(self, torsion_points: List[Tuple[EllipticCurvePoint, int]], 
                               curve: EllipticCurve) -> List[EllipticCurvePoint]:
        """Find generators for torsion subgroup"""
        if not torsion_points:
            return []
        
        # For simplicity, return point with highest order
        max_order = max(order for _, order in torsion_points)
        generators = [pt for pt, order in torsion_points if order == max_order]
        
        return generators[:2]  # At most 2 generators for elliptic curves over Q
    
    async def _analyze_rank(self, curve: EllipticCurve, deep: bool = True) -> RankData:
        """Analyze Mordell-Weil rank"""
        # Get basic estimate from curve
        basic_estimate = curve.estimate_rank()
        
        # Find rational points
        rational_points = curve.find_rational_points(200 if deep else 50)
        
        # Filter out torsion points
        torsion_points = curve.compute_torsion_points()
        torsion_coords = {(pt.x, pt.y) for pt, _ in torsion_points if not pt.is_infinity}
        
        non_torsion = []
        for pt in rational_points:
            if not pt.is_infinity and (pt.x, pt.y) not in torsion_coords:
                non_torsion.append(pt)
        
        # Estimate rank
        estimated_rank = len(non_torsion)
        if estimated_rank > 3:
            estimated_rank = 3  # Conservative bound
        
        confidence = 0.8 if deep else 0.6
        if estimated_rank == basic_estimate["estimated_rank"]:
            confidence += 0.1
        
        return RankData(
            analytic_rank=None,  # Would need L-function computation
            algebraic_rank=None,  # Would need advanced techniques
            estimated_rank=estimated_rank,
            confidence=confidence,
            method_used="rational_point_search",
            rational_points=non_torsion,
            regulator=None  # Would need height pairing computation
        )
    
    async def _analyze_conductor(self, curve: EllipticCurve) -> Tuple[int, List[ReductionData]]:
        """Analyze conductor and bad reduction"""
        # Get basic conductor estimate
        conductor_est = curve.conductor_estimate()
        
        # Find bad primes (primes dividing discriminant)
        discriminant = abs(curve.discriminant)
        bad_primes = primefactors(discriminant)
        
        bad_reduction_data = []
        actual_conductor = 1
        
        for p in bad_primes:
            # Simplified bad reduction analysis
            v_p = 0
            temp = discriminant
            while temp % p == 0:
                temp //= p
                v_p += 1
            
            if v_p >= 12:
                reduction_type = "additive"
                kodaira = "I*_bad"
                tamagawa = p
                conductor_power = 2
            elif v_p >= 6:
                reduction_type = "multiplicative"
                kodaira = f"I_{v_p-4}"
                tamagawa = v_p - 4 if v_p > 4 else 1
                conductor_power = 1
            else:
                reduction_type = "good"
                kodaira = "I_0"
                tamagawa = 1
                conductor_power = 0
            
            if conductor_power > 0:
                actual_conductor *= p**conductor_power
            
            if reduction_type != "good":
                bad_reduction_data.append(ReductionData(
                    prime=p,
                    reduction_type=reduction_type,
                    kodaira_symbol=kodaira,
                    tamagawa_number=tamagawa,
                    local_contribution=float(tamagawa) / p
                ))
        
        return actual_conductor, bad_reduction_data
    
    def _analyze_cm(self, curve: EllipticCurve) -> Tuple[Optional[int], bool]:
        """Analyze complex multiplication"""
        j_inv = curve.j_invariant
        
        # Check for known CM j-invariants
        cm_j_invariants = {
            -3: 0,          # j = 0
            -4: 1728,       # j = 1728
            -7: -3375,      # j = -3375
            -8: 8000,       # j = 8000
            -11: -32768,    # j = -32768
            -12: 54000,     # j = 54000
            -16: 287496,    # j = 287496
            -19: -884736,   # j = -884736
            -27: -12288000, # j = -12288000
            -28: 16581375   # j = 16581375
        }
        
        for disc, j_val in cm_j_invariants.items():
            if j_inv == j_val:
                return disc, True
        
        # Check if j-invariant is integral
        if j_inv.denominator == 1:
            # Could have CM, but would need more sophisticated test
            return None, False
        
        return None, False
    
    async def _analyze_l_function(self, curve: EllipticCurve) -> Dict[str, Any]:
        """Analyze L-function data (placeholder)"""
        # This would involve computing L-function coefficients
        # For now, return basic structure
        return {
            "has_analytic_continuation": True,
            "functional_equation": "assumed",
            "critical_values": None,
            "zeros": None,
            "bsd_conjecture": {
                "predicted_order_vanishing": None,
                "leading_coefficient": None
            }
        }
    
    def _analyze_special_properties(self, curve: EllipticCurve, 
                                  torsion: TorsionStructure) -> Dict[str, bool]:
        """Analyze special isogeny and torsion properties"""
        # Check for 2-torsion
        has_2_torsion = any(order == 2 for _, order in torsion.points)
        
        # Check for potential 3-isogeny (simplified)
        j_inv = curve.j_invariant
        has_3_isogeny = False
        if j_inv == 0 or j_inv == 1728:  # Special cases
            has_3_isogeny = True
        
        # Check for potential 5-isogeny (simplified)
        has_5_isogeny = False
        
        return {
            "has_2_torsion": has_2_torsion,
            "has_3_isogeny": has_3_isogeny,
            "has_5_isogeny": has_5_isogeny
        }
    
    async def _compute_periods(self, curve: EllipticCurve) -> Optional[Tuple[complex, complex]]:
        """Compute periods of elliptic curve (placeholder)"""
        # This would involve numerical integration
        # Placeholder for now
        return None
    
    def _compute_reliability(self, rank_data: RankData, 
                           torsion: TorsionStructure) -> float:
        """Compute reliability score for invariants"""
        score = 0.5  # Base score
        
        # Add confidence from rank analysis
        score += 0.2 * rank_data.confidence
        
        # Add confidence from torsion analysis
        if len(torsion.points) > 0:
            score += 0.2
        
        # Add confidence from number of rational points found
        if len(rank_data.rational_points) > 0:
            score += 0.1
        
        return min(1.0, score)
    
    async def batch_analyze(self, curves: List[EllipticCurve], 
                          max_concurrent: int = 10) -> List[EllipticCurveInvariants]:
        """Analyze multiple curves concurrently"""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def analyze_with_semaphore(curve):
            async with semaphore:
                return await self.analyze_curve(curve)
        
        tasks = [analyze_with_semaphore(curve) for curve in curves]
        return await asyncio.gather(*tasks)
    
    def generate_invariant_report(self, invariants: EllipticCurveInvariants) -> Dict[str, Any]:
        """Generate comprehensive report of invariants"""
        return {
            "curve_equation": str(invariants.curve),
            "basic_invariants": {
                "j_invariant": str(invariants.j_invariant),
                "discriminant": int(invariants.discriminant),
                "c4": int(invariants.c4),
                "c6": int(invariants.c6),
                "conductor": invariants.conductor
            },
            "torsion_structure": {
                "structure": invariants.torsion.structure,
                "order": invariants.torsion.order,
                "generators": len(invariants.torsion.generators),
                "is_cyclic": invariants.torsion.is_cyclic
            },
            "rank_information": {
                "estimated_rank": invariants.rank_data.estimated_rank,
                "confidence": invariants.rank_data.confidence,
                "rational_points_found": len(invariants.rank_data.rational_points)
            },
            "special_properties": {
                "has_cm": invariants.is_cm,
                "cm_discriminant": invariants.cm_discriminant,
                "has_rational_2_torsion": invariants.has_rational_2_torsion,
                "endomorphism_ring": invariants.endomorphism_ring
            },
            "bad_reduction": [
                {
                    "prime": br.prime,
                    "type": br.reduction_type,
                    "kodaira_symbol": br.kodaira_symbol,
                    "tamagawa_number": br.tamagawa_number
                }
                for br in invariants.bad_reduction
            ],
            "computational_metadata": {
                "computation_time": invariants.computation_time,
                "reliability_score": invariants.reliability_score
            }
        }


if __name__ == "__main__":
    # Demo of invariant analysis
    import asyncio
    
    async def demo_invariants():
        print("🔍 Elliptic Curve Invariants Demo")
        print("=" * 50)
        
        analyzer = EllipticCurveInvariantAnalyzer()
        
        # Analyze a well-known curve
        curve = EllipticCurve(-2, 1)  # y² = x³ - 2x + 1
        
        print(f"Analyzing curve: {curve}")
        invariants = await analyzer.analyze_curve(curve)
        
        report = analyzer.generate_invariant_report(invariants)
        
        print("\n📊 Analysis Results:")
        print(f"j-invariant: {report['basic_invariants']['j_invariant']}")
        print(f"Conductor: {report['basic_invariants']['conductor']}")
        print(f"Torsion: {report['torsion_structure']['structure']}")
        print(f"Estimated rank: {report['rank_information']['estimated_rank']}")
        print(f"Has CM: {report['special_properties']['has_cm']}")
        print(f"Reliability: {report['computational_metadata']['reliability_score']:.2f}")
        
        print(f"\nBad reduction at {len(report['bad_reduction'])} primes:")
        for br in report['bad_reduction']:
            print(f"  p={br['prime']}: {br['type']} ({br['kodaira_symbol']})")
    
    asyncio.run(demo_invariants())
