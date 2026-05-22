"""
Sequence Analyzer with OEIS Integration for AXIOM Mathematical Laboratory
Analyzes mathematical sequences and connects to OEIS database
"""

from __future__ import annotations

import asyncio
import aiohttp
import json
import re
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np
from fractions import Fraction
import sympy as sp
from sympy import symbols, solve, simplify, series, limit, oo

logger = logging.getLogger(__name__)


@dataclass
class SequencePattern:
    """Detected pattern in a sequence"""
    pattern_type: str  # "polynomial", "exponential", "recurrence", "special"
    formula: Optional[str]
    confidence: float
    parameters: Dict[str, Any]
    generating_function: Optional[str] = None
    description: str = ""


@dataclass
class OEISMatch:
    """Match from OEIS database"""
    sequence_id: str  # e.g., "A000001"
    name: str
    sequence_data: List[int]
    formula: Optional[str]
    offset: int
    match_confidence: float
    url: str
    comments: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)


@dataclass
class SequenceAnalysisResult:
    """Complete analysis result for a sequence"""
    input_sequence: List[Union[int, float, Fraction]]
    detected_patterns: List[SequencePattern]
    oeis_matches: List[OEISMatch]
    statistical_properties: Dict[str, Any]
    generating_function: Optional[str]
    asymptotic_behavior: Optional[str]
    continuation: List[Union[int, float]]  # Next predicted terms
    novelty_score: float  # How novel/interesting the sequence is
    analysis_metadata: Dict[str, Any]


class SequenceAnalyzer:
    """Comprehensive sequence analyzer with OEIS integration"""
    
    def __init__(self):
        self.oeis_base_url = "https://oeis.org/search"
        self.session = None
        self.pattern_cache = {}
        
        # Pattern recognition functions
        self.pattern_detectors = {
            "polynomial": self._detect_polynomial_pattern,
            "exponential": self._detect_exponential_pattern,
            "fibonacci_like": self._detect_fibonacci_pattern,
            "arithmetic": self._detect_arithmetic_pattern,
            "geometric": self._detect_geometric_pattern,
            "factorial_like": self._detect_factorial_pattern,
            "prime_related": self._detect_prime_pattern,
            "power_sums": self._detect_power_sum_pattern
        }
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def analyze_sequence(self, 
                             sequence: List[Union[int, float, Fraction]], 
                             deep_analysis: bool = True) -> SequenceAnalysisResult:
        """Perform comprehensive sequence analysis"""
        if not sequence:
            raise ValueError("Empty sequence provided")
        
        logger.info(f"Analyzing sequence of length {len(sequence)}: {sequence[:10]}...")
        
        # Convert to appropriate numeric types
        normalized_seq = self._normalize_sequence(sequence)
        
        # Detect patterns
        patterns = await self._detect_all_patterns(normalized_seq)
        
        # Search OEIS if session is available
        oeis_matches = []
        if self.session and deep_analysis:
            oeis_matches = await self._search_oeis(normalized_seq)
        
        # Statistical analysis
        stats = self._compute_statistical_properties(normalized_seq)
        
        # Generate continuation
        continuation = self._predict_continuation(normalized_seq, patterns)
        
        # Compute generating function if possible
        gen_func = self._compute_generating_function(normalized_seq, patterns)
        
        # Asymptotic analysis
        asymptotic = self._analyze_asymptotic_behavior(normalized_seq, patterns)
        
        # Compute novelty score
        novelty = self._compute_novelty_score(patterns, oeis_matches, stats)
        
        return SequenceAnalysisResult(
            input_sequence=sequence,
            detected_patterns=patterns,
            oeis_matches=oeis_matches,
            statistical_properties=stats,
            generating_function=gen_func,
            asymptotic_behavior=asymptotic,
            continuation=continuation,
            novelty_score=novelty,
            analysis_metadata={
                "sequence_length": len(sequence),
                "patterns_detected": len(patterns),
                "oeis_matches": len(oeis_matches),
                "deep_analysis": deep_analysis
            }
        )
    
    def _normalize_sequence(self, sequence: List[Union[int, float, Fraction]]) -> List[float]:
        """Normalize sequence to consistent numeric type"""
        normalized = []
        for term in sequence:
            if isinstance(term, Fraction):
                normalized.append(float(term))
            else:
                normalized.append(float(term))
        return normalized
    
    async def _detect_all_patterns(self, sequence: List[float]) -> List[SequencePattern]:
        """Detect all possible patterns in the sequence"""
        patterns = []
        
        for pattern_name, detector in self.pattern_detectors.items():
            try:
                pattern = await detector(sequence)
                if pattern and pattern.confidence > 0.1:
                    patterns.append(pattern)
            except Exception as e:
                logger.warning(f"Pattern detector {pattern_name} failed: {e}")
        
        # Sort by confidence
        patterns.sort(key=lambda p: p.confidence, reverse=True)
        
        return patterns[:5]  # Keep top 5 patterns
    
    async def _detect_polynomial_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect polynomial patterns using finite differences"""
        if len(sequence) < 4:
            return None
        
        # Compute finite differences
        diffs = [sequence]
        for level in range(min(len(sequence) - 1, 6)):
            new_diff = [diffs[-1][i+1] - diffs[-1][i] for i in range(len(diffs[-1]) - 1)]
            if not new_diff:
                break
            diffs.append(new_diff)
            
            # Check if this level is constant
            if len(set(new_diff)) <= 1 and len(new_diff) >= 2:
                # Found polynomial of degree 'level'
                try:
                    # Fit polynomial
                    n = symbols('n')
                    x_vals = list(range(len(sequence)))
                    poly = sp.interpolate(list(zip(x_vals, sequence)), n)
                    
                    # Verify fit quality
                    predicted = [float(poly.subs(n, i)) for i in x_vals]
                    mse = np.mean([(p - s)**2 for p, s in zip(predicted, sequence)])
                    
                    if mse < 1e-6:  # Good fit
                        return SequencePattern(
                            pattern_type="polynomial",
                            formula=str(poly),
                            confidence=1.0 - min(mse, 0.5),
                            parameters={"degree": level, "polynomial": str(poly)},
                            description=f"Polynomial sequence of degree {level}"
                        )
                except Exception:
                    pass
        
        return None
    
    async def _detect_exponential_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect exponential patterns"""
        if len(sequence) < 3 or any(x <= 0 for x in sequence):
            return None
        
        try:
            # Check if ratios are approximately constant
            ratios = [sequence[i+1] / sequence[i] for i in range(len(sequence) - 1)]
            ratio_mean = np.mean(ratios)
            ratio_std = np.std(ratios)
            
            if ratio_std < 0.1 * ratio_mean and ratio_mean > 0:
                # Exponential pattern detected
                base = ratio_mean
                initial = sequence[0]
                
                # Verify fit
                predicted = [initial * (base ** i) for i in range(len(sequence))]
                mse = np.mean([(p - s)**2 for p, s in zip(predicted, sequence)])
                relative_error = mse / (np.mean(sequence)**2)
                
                if relative_error < 0.01:
                    return SequencePattern(
                        pattern_type="exponential",
                        formula=f"{initial:.3f} * {base:.3f}^n",
                        confidence=1.0 - min(relative_error * 10, 0.9),
                        parameters={"base": base, "initial": initial},
                        description=f"Exponential sequence with base {base:.3f}"
                    )
        except Exception:
            pass
        
        return None
    
    async def _detect_fibonacci_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect Fibonacci-like recurrence patterns"""
        if len(sequence) < 4:
            return None
        
        try:
            # Check F(n) = F(n-1) + F(n-2) pattern
            errors = []
            for i in range(2, len(sequence)):
                expected = sequence[i-1] + sequence[i-2]
                error = abs(expected - sequence[i]) / (abs(sequence[i]) + 1e-10)
                errors.append(error)
            
            avg_error = np.mean(errors)
            
            if avg_error < 0.05:  # Good Fibonacci-like pattern
                return SequencePattern(
                    pattern_type="fibonacci_like",
                    formula="F(n) = F(n-1) + F(n-2)",
                    confidence=1.0 - min(avg_error * 20, 0.9),
                    parameters={
                        "initial_terms": sequence[:2],
                        "recurrence_relation": "F(n) = F(n-1) + F(n-2)"
                    },
                    description="Fibonacci-like recurrence relation"
                )
            
            # Check for generalized Fibonacci: F(n) = a*F(n-1) + b*F(n-2)
            if len(sequence) >= 6:
                # Try to fit a, b
                X = np.array([[sequence[i-1], sequence[i-2]] for i in range(2, len(sequence))])
                y = np.array(sequence[2:])
                
                try:
                    coeffs = np.linalg.lstsq(X, y, rcond=None)[0]
                    a, b = coeffs
                    
                    # Verify fit
                    predicted = sequence[:2] + [a * sequence[i-1] + b * sequence[i-2] 
                                              for i in range(2, len(sequence))]
                    mse = np.mean([(p - s)**2 for p, s in zip(predicted, sequence)])
                    relative_error = mse / (np.var(sequence) + 1e-10)
                    
                    if relative_error < 0.01:
                        return SequencePattern(
                            pattern_type="fibonacci_like",
                            formula=f"F(n) = {a:.3f}*F(n-1) + {b:.3f}*F(n-2)",
                            confidence=1.0 - min(relative_error * 50, 0.9),
                            parameters={"a": a, "b": b, "initial_terms": sequence[:2]},
                            description=f"Generalized Fibonacci with coefficients a={a:.3f}, b={b:.3f}"
                        )
                except Exception:
                    pass
        
        except Exception:
            pass
        
        return None
    
    async def _detect_arithmetic_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect arithmetic progressions"""
        if len(sequence) < 3:
            return None
        
        try:
            differences = [sequence[i+1] - sequence[i] for i in range(len(sequence) - 1)]
            diff_std = np.std(differences)
            diff_mean = np.mean(differences)
            
            if diff_std < 1e-6 or diff_std < 0.01 * abs(diff_mean):
                return SequencePattern(
                    pattern_type="arithmetic",
                    formula=f"{sequence[0]} + {diff_mean:.3f}*n",
                    confidence=1.0 - min(diff_std / (abs(diff_mean) + 1e-10), 0.9),
                    parameters={"first_term": sequence[0], "common_difference": diff_mean},
                    description=f"Arithmetic sequence with difference {diff_mean:.3f}"
                )
        except Exception:
            pass
        
        return None
    
    async def _detect_geometric_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect geometric progressions"""
        if len(sequence) < 3 or any(abs(x) < 1e-10 for x in sequence):
            return None
        
        try:
            ratios = [sequence[i+1] / sequence[i] for i in range(len(sequence) - 1)]
            ratio_std = np.std(ratios)
            ratio_mean = np.mean(ratios)
            
            if ratio_std < 1e-6 or ratio_std < 0.01 * abs(ratio_mean):
                return SequencePattern(
                    pattern_type="geometric",
                    formula=f"{sequence[0]} * {ratio_mean:.3f}^n",
                    confidence=1.0 - min(ratio_std / (abs(ratio_mean) + 1e-10), 0.9),
                    parameters={"first_term": sequence[0], "common_ratio": ratio_mean},
                    description=f"Geometric sequence with ratio {ratio_mean:.3f}"
                )
        except Exception:
            pass
        
        return None
    
    async def _detect_factorial_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect factorial-related patterns"""
        if len(sequence) < 4:
            return None
        
        try:
            # Check if sequence[n] = n!
            factorials = [1]
            for i in range(1, len(sequence)):
                factorials.append(factorials[-1] * i)
            
            if len(factorials) >= len(sequence):
                errors = [abs(sequence[i] - factorials[i]) / (factorials[i] + 1e-10) 
                         for i in range(len(sequence))]
                avg_error = np.mean(errors)
                
                if avg_error < 0.01:
                    return SequencePattern(
                        pattern_type="factorial_like",
                        formula="n!",
                        confidence=1.0 - min(avg_error * 100, 0.9),
                        parameters={"type": "factorial"},
                        description="Factorial sequence"
                    )
            
            # Check for double factorial, subfactorial, etc.
            # (Simplified implementation)
        except Exception:
            pass
        
        return None
    
    async def _detect_prime_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect prime-related patterns"""
        if len(sequence) < 5:
            return None
        
        try:
            # Check if sequence consists of primes
            int_sequence = [int(round(x)) for x in sequence if x == int(x)]
            
            if len(int_sequence) == len(sequence) and len(int_sequence) >= 3:
                from sympy.ntheory import isprime
                
                prime_count = sum(1 for x in int_sequence if isprime(x))
                prime_ratio = prime_count / len(int_sequence)
                
                if prime_ratio > 0.8:  # Most terms are prime
                    return SequencePattern(
                        pattern_type="prime_related",
                        formula="sequence of primes",
                        confidence=prime_ratio,
                        parameters={"prime_ratio": prime_ratio},
                        description=f"Prime-related sequence ({prime_ratio:.1%} are prime)"
                    )
        except Exception:
            pass
        
        return None
    
    async def _detect_power_sum_pattern(self, sequence: List[float]) -> Optional[SequencePattern]:
        """Detect power sum patterns like 1^k + 2^k + ... + n^k"""
        if len(sequence) < 4:
            return None
        
        try:
            # Check for various power sums
            for k in range(1, 5):
                predicted = []
                for n in range(1, len(sequence) + 1):
                    power_sum = sum(i**k for i in range(1, n + 1))
                    predicted.append(power_sum)
                
                if len(predicted) >= len(sequence):
                    errors = [abs(sequence[i] - predicted[i]) / (predicted[i] + 1e-10) 
                             for i in range(len(sequence))]
                    avg_error = np.mean(errors)
                    
                    if avg_error < 0.01:
                        return SequencePattern(
                            pattern_type="power_sums",
                            formula=f"sum(i^{k} for i=1..n)",
                            confidence=1.0 - min(avg_error * 100, 0.9),
                            parameters={"power": k},
                            description=f"Sum of {k}-th powers"
                        )
        except Exception:
            pass
        
        return None
    
    async def _search_oeis(self, sequence: List[float]) -> List[OEISMatch]:
        """Search OEIS database for matching sequences"""
        if not self.session:
            return []
        
        try:
            # Convert to integers if possible
            int_sequence = []
            for x in sequence[:20]:  # OEIS searches work better with first 20 terms
                if abs(x - round(x)) < 1e-10:
                    int_sequence.append(int(round(x)))
                else:
                    int_sequence.append(x)
            
            # Create search query
            search_terms = ",".join(str(x) for x in int_sequence[:15])
            
            params = {
                "q": search_terms,
                "fmt": "json",
                "n": 5  # Get top 5 matches
            }
            
            async with self.session.get(self.oeis_base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_oeis_response(data, sequence)
        
        except Exception as e:
            logger.warning(f"OEIS search failed: {e}")
        
        return []
    
    def _parse_oeis_response(self, data: Dict, original_sequence: List[float]) -> List[OEISMatch]:
        """Parse OEIS API response"""
        matches = []
        
        if "results" not in data:
            return matches
        
        for result in data["results"]:
            try:
                seq_id = result.get("number", "")
                name = result.get("name", "")
                
                # Parse sequence data
                data_str = result.get("data", "")
                seq_data = []
                if data_str:
                    # Extract numbers from data string
                    numbers = re.findall(r'-?\d+', data_str)
                    seq_data = [int(x) for x in numbers[:50]]
                
                # Calculate match confidence
                confidence = self._calculate_match_confidence(original_sequence, seq_data)
                
                if confidence > 0.5:  # Only include good matches
                    match = OEISMatch(
                        sequence_id=seq_id,
                        name=name,
                        sequence_data=seq_data,
                        formula=result.get("formula"),
                        offset=result.get("offset", [0])[0] if result.get("offset") else 0,
                        match_confidence=confidence,
                        url=f"https://oeis.org/{seq_id}",
                        comments=result.get("comment", [])
                    )
                    matches.append(match)
            
            except Exception as e:
                logger.warning(f"Failed to parse OEIS result: {e}")
        
        return sorted(matches, key=lambda m: m.match_confidence, reverse=True)
    
    def _calculate_match_confidence(self, seq1: List[float], seq2: List[int]) -> float:
        """Calculate confidence of sequence match"""
        if not seq1 or not seq2:
            return 0.0
        
        # Compare overlapping parts
        min_len = min(len(seq1), len(seq2))
        if min_len < 3:
            return 0.0
        
        matches = 0
        for i in range(min_len):
            if abs(seq1[i] - seq2[i]) < 1e-6:
                matches += 1
        
        # Base confidence on match ratio and length
        match_ratio = matches / min_len
        length_factor = min(min_len / 10.0, 1.0)  # Favor longer matches
        
        return match_ratio * length_factor
    
    def _compute_statistical_properties(self, sequence: List[float]) -> Dict[str, Any]:
        """Compute statistical properties of the sequence"""
        if not sequence:
            return {}
        
        properties = {
            "length": len(sequence),
            "mean": np.mean(sequence),
            "median": np.median(sequence),
            "std_dev": np.std(sequence),
            "min_value": min(sequence),
            "max_value": max(sequence),
            "range": max(sequence) - min(sequence)
        }
        
        if len(sequence) > 1:
            properties["growth_rate"] = (sequence[-1] - sequence[0]) / (len(sequence) - 1)
            
            # Compute differences
            diffs = [sequence[i+1] - sequence[i] for i in range(len(sequence) - 1)]
            properties["mean_difference"] = np.mean(diffs)
            properties["difference_std"] = np.std(diffs)
            
            # Monotonicity
            increasing = all(diffs[i] >= 0 for i in range(len(diffs)))
            decreasing = all(diffs[i] <= 0 for i in range(len(diffs)))
            properties["is_monotonic"] = increasing or decreasing
            properties["is_increasing"] = increasing
            properties["is_decreasing"] = decreasing
        
        return properties
    
    def _predict_continuation(self, sequence: List[float], 
                            patterns: List[SequencePattern]) -> List[float]:
        """Predict next terms in the sequence"""
        if not patterns:
            # Simple linear extrapolation as fallback
            if len(sequence) >= 2:
                diff = sequence[-1] - sequence[-2]
                return [sequence[-1] + diff * i for i in range(1, 4)]
            return []
        
        # Use best pattern for prediction
        best_pattern = patterns[0]
        next_terms = []
        
        try:
            if best_pattern.pattern_type == "arithmetic":
                diff = best_pattern.parameters["common_difference"]
                for i in range(1, 4):
                    next_terms.append(sequence[-1] + diff * i)
            
            elif best_pattern.pattern_type == "geometric":
                ratio = best_pattern.parameters["common_ratio"]
                for i in range(1, 4):
                    next_terms.append(sequence[-1] * (ratio ** i))
            
            elif best_pattern.pattern_type == "polynomial":
                # Use the polynomial formula
                n = symbols('n')
                poly_str = best_pattern.parameters["polynomial"]
                poly = sp.sympify(poly_str)
                
                current_n = len(sequence)
                for i in range(1, 4):
                    next_val = float(poly.subs(n, current_n + i - 1))
                    next_terms.append(next_val)
            
            elif best_pattern.pattern_type == "fibonacci_like":
                # Use recurrence relation
                if "a" in best_pattern.parameters and "b" in best_pattern.parameters:
                    a = best_pattern.parameters["a"]
                    b = best_pattern.parameters["b"]
                    
                    current_seq = list(sequence)
                    for i in range(3):
                        next_val = a * current_seq[-1] + b * current_seq[-2]
                        next_terms.append(next_val)
                        current_seq.append(next_val)
                else:
                    # Standard Fibonacci
                    current_seq = list(sequence)
                    for i in range(3):
                        next_val = current_seq[-1] + current_seq[-2]
                        next_terms.append(next_val)
                        current_seq.append(next_val)
            
            else:
                # Fallback to linear extrapolation
                if len(sequence) >= 2:
                    diff = sequence[-1] - sequence[-2]
                    for i in range(1, 4):
                        next_terms.append(sequence[-1] + diff * i)
        
        except Exception as e:
            logger.warning(f"Continuation prediction failed: {e}")
            # Fallback
            if len(sequence) >= 2:
                diff = sequence[-1] - sequence[-2]
                next_terms = [sequence[-1] + diff * i for i in range(1, 4)]
        
        return next_terms
    
    def _compute_generating_function(self, sequence: List[float], 
                                   patterns: List[SequencePattern]) -> Optional[str]:
        """Attempt to compute generating function"""
        if not patterns:
            return None
        
        best_pattern = patterns[0]
        
        try:
            if best_pattern.pattern_type == "geometric":
                ratio = best_pattern.parameters["common_ratio"]
                initial = best_pattern.parameters["first_term"]
                return f"{initial}/(1 - {ratio}*x)"
            
            elif best_pattern.pattern_type == "arithmetic":
                return "x/(1-x)^2"  # Generating function for 1,2,3,4,...
            
            elif best_pattern.pattern_type == "fibonacci_like":
                if best_pattern.formula == "F(n) = F(n-1) + F(n-2)":
                    return "x/(1 - x - x^2)"
        
        except Exception:
            pass
        
        return None
    
    def _analyze_asymptotic_behavior(self, sequence: List[float], 
                                   patterns: List[SequencePattern]) -> Optional[str]:
        """Analyze asymptotic growth behavior"""
        if not patterns or len(sequence) < 5:
            return None
        
        best_pattern = patterns[0]
        
        try:
            if best_pattern.pattern_type == "exponential":
                base = best_pattern.parameters["base"]
                return f"O({base:.3f}^n)"
            
            elif best_pattern.pattern_type == "polynomial":
                degree = best_pattern.parameters["degree"]
                return f"O(n^{degree})"
            
            elif best_pattern.pattern_type == "factorial_like":
                return "O(n!)"
            
            elif best_pattern.pattern_type == "arithmetic":
                return "O(n)"
            
            elif best_pattern.pattern_type == "geometric":
                ratio = abs(best_pattern.parameters["common_ratio"])
                if ratio > 1:
                    return f"O({ratio:.3f}^n)"
                else:
                    return "O(1)"
        
        except Exception:
            pass
        
        return None
    
    def _compute_novelty_score(self, patterns: List[SequencePattern], 
                             oeis_matches: List[OEISMatch],
                             stats: Dict[str, Any]) -> float:
        """Compute how novel/interesting the sequence is"""
        score = 0.5  # Base score
        
        # Reduce score for OEIS matches
        if oeis_matches:
            best_match_confidence = max(m.match_confidence for m in oeis_matches)
            score -= 0.3 * best_match_confidence
        
        # Increase score for complex patterns
        if patterns:
            complex_patterns = ["fibonacci_like", "polynomial", "exponential"]
            for pattern in patterns:
                if pattern.pattern_type in complex_patterns:
                    score += 0.1 * pattern.confidence
        
        # Increase score for unusual statistical properties
        if stats.get("is_monotonic", True) == False:
            score += 0.1
        
        if len(patterns) > 2:  # Multiple patterns detected
            score += 0.1
        
        return max(0.0, min(1.0, score))


async def demo_sequence_analysis():
    """Demo of sequence analysis capabilities"""
    print("🔢 Sequence Analysis Demo")
    print("=" * 50)
    
    async with SequenceAnalyzer() as analyzer:
        # Test sequences
        test_sequences = [
            [1, 1, 2, 3, 5, 8, 13, 21, 34, 55],  # Fibonacci
            [1, 4, 9, 16, 25, 36, 49, 64],        # Squares
            [1, 2, 6, 24, 120, 720, 5040],        # Factorials
            [2, 3, 5, 7, 11, 13, 17, 19, 23],     # Primes
            [1, 3, 6, 10, 15, 21, 28, 36]         # Triangular numbers
        ]
        
        sequence_names = ["Fibonacci", "Squares", "Factorials", "Primes", "Triangular"]
        
        for seq, name in zip(test_sequences, sequence_names):
            print(f"\n📊 Analyzing {name}: {seq}")
            
            result = await analyzer.analyze_sequence(seq, deep_analysis=False)
            
            print(f"  Patterns detected: {len(result.detected_patterns)}")
            if result.detected_patterns:
                top_pattern = result.detected_patterns[0]
                print(f"  Best pattern: {top_pattern.pattern_type}")
                print(f"  Formula: {top_pattern.formula}")
                print(f"  Confidence: {top_pattern.confidence:.2f}")
            
            print(f"  Predicted next terms: {result.continuation}")
            print(f"  Novelty score: {result.novelty_score:.2f}")
            
            if result.oeis_matches:
                print(f"  OEIS matches: {len(result.oeis_matches)}")
                best_match = result.oeis_matches[0]
                print(f"    Best: {best_match.sequence_id} - {best_match.name}")


if __name__ == "__main__":
    asyncio.run(demo_sequence_analysis())
