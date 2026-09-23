"""
Property-Based Tests for Statistics Operations

Uses Hypothesis to test statistical properties including:
- Mean, median, mode properties
- Variance and standard deviation
- Distribution properties
- Correlation and regression

ROADMAP 1: TESTING & QUALITY - Phase 3.1
Created: 2025-10-01
"""

import math
import statistics
from typing import List

import pytest
from hypothesis import assume, given
from hypothesis import strategies as st


class TestMeanProperties:
    """Test properties of arithmetic mean."""

    @given(st.lists(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False), min_size=1, max_size=100))
    def test_mean_within_range(self, data: List[float]):
        """Mean should be between min and max of data."""
        mean = statistics.mean(data)
        assert min(data) <= mean <= max(data)

    @given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=50))
    def test_mean_sum_property(self, data: List[int]):
        """Mean multiplied by count equals sum."""
        mean = statistics.mean(data)
        expected_sum = mean * len(data)
        actual_sum = sum(data)
        assert math.isclose(expected_sum, actual_sum, rel_tol=1e-9)

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_mean_translation_invariance(self, data: List[float]):
        """Mean(data + c) = Mean(data) + c"""
        c = 10.0
        original_mean = statistics.mean(data)
        translated_data = [x + c for x in data]
        translated_mean = statistics.mean(translated_data)
        assert math.isclose(translated_mean, original_mean + c, rel_tol=1e-6)

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=50))
    def test_mean_scaling_property(self, data: List[float]):
        """Mean(c * data) = c * Mean(data)"""
        c = 2.5
        original_mean = statistics.mean(data)
        scaled_data = [x * c for x in data]
        scaled_mean = statistics.mean(scaled_data)
        assert math.isclose(scaled_mean, c * original_mean, rel_tol=1e-6)

    @given(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False))
    def test_mean_of_constant(self, c: float):
        """Mean of constant values equals the constant."""
        data = [c] * 10
        assert math.isclose(statistics.mean(data), c, abs_tol=1e-9)


class TestMedianProperties:
    """Test properties of median."""

    @given(st.lists(st.integers(min_value=-1000, max_value=1000), min_size=1, max_size=100))
    def test_median_within_range(self, data: List[int]):
        """Median should be between min and max."""
        median = statistics.median(data)
        assert min(data) <= median <= max(data)

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=1, max_size=50))
    def test_median_translation_invariance(self, data: List[float]):
        """Median(data + c) = Median(data) + c"""
        c = 5.0
        original_median = statistics.median(data)
        translated_data = [x + c for x in data]
        translated_median = statistics.median(translated_data)
        assert math.isclose(translated_median, original_median + c, rel_tol=1e-6)

    @given(st.lists(st.integers(min_value=1, max_value=100), min_size=1, max_size=50))
    def test_median_odd_length(self, data: List[int]):
        """For odd-length sorted list, median is the middle element."""
        if len(data) % 2 == 1:
            sorted_data = sorted(data)
            median = statistics.median(data)
            middle_index = len(sorted_data) // 2
            assert median == sorted_data[middle_index]


class TestVarianceProperties:
    """Test properties of variance."""

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_variance_non_negative(self, data: List[float]):
        """Variance is always non-negative."""
        var = statistics.variance(data)
        assert var >= 0

    @given(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False))
    def test_variance_of_constant(self, c: float):
        """Variance of constant values is zero."""
        data = [c] * 10
        var = statistics.variance(data)
        assert math.isclose(var, 0.0, abs_tol=1e-9)

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_variance_translation_invariance(self, data: List[float]):
        """Var(data + c) = Var(data)"""
        c = 10.0
        original_var = statistics.variance(data)
        translated_data = [x + c for x in data]
        translated_var = statistics.variance(translated_data)
        assert math.isclose(translated_var, original_var, rel_tol=1e-6)

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_variance_scaling_property(self, data: List[float]):
        """Var(c * data) = c^2 * Var(data)"""
        c = 2.0
        original_var = statistics.variance(data)
        scaled_data = [x * c for x in data]
        scaled_var = statistics.variance(scaled_data)
        assert math.isclose(scaled_var, (c ** 2) * original_var, rel_tol=1e-6)


class TestStandardDeviationProperties:
    """Test properties of standard deviation."""

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_stdev_non_negative(self, data: List[float]):
        """Standard deviation is always non-negative."""
        stdev = statistics.stdev(data)
        assert stdev >= 0

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_stdev_variance_relationship(self, data: List[float]):
        """StDev = sqrt(Variance)"""
        var = statistics.variance(data)
        stdev = statistics.stdev(data)
        assert math.isclose(stdev, math.sqrt(var), rel_tol=1e-9)

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=2, max_size=50))
    def test_stdev_scaling_property(self, data: List[float]):
        """StDev(c * data) = |c| * StDev(data)"""
        c = 3.0
        original_stdev = statistics.stdev(data)
        scaled_data = [x * c for x in data]
        scaled_stdev = statistics.stdev(scaled_data)
        assert math.isclose(scaled_stdev, abs(c) * original_stdev, rel_tol=1e-6)


class TestCorrelationProperties:
    """Test properties of correlation."""

    @given(
        st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=3, max_size=50),
        st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=3, max_size=50)
    )
    def test_correlation_range(self, x: List[float], y: List[float]):
        """Correlation coefficient should be between -1 and 1."""
        assume(len(x) == len(y))
        assume(statistics.stdev(x) > 0 and statistics.stdev(y) > 0)
        
        # Calculate Pearson correlation
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = math.sqrt(
            sum((x[i] - mean_x) ** 2 for i in range(n)) *
            sum((y[i] - mean_y) ** 2 for i in range(n))
        )
        
        if denominator > 0:
            correlation = numerator / denominator
            assert -1.0 <= correlation <= 1.0

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=3, max_size=30))
    def test_perfect_positive_correlation(self, x: List[float]):
        """Correlation of x with itself is 1."""
        assume(statistics.stdev(x) > 0)
        
        n = len(x)
        mean_x = statistics.mean(x)
        
        numerator = sum((x[i] - mean_x) * (x[i] - mean_x) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        correlation = numerator / denominator if denominator > 0 else 1.0
        assert math.isclose(correlation, 1.0, abs_tol=1e-6)


class TestSumStatistics:
    """Test properties of sum statistics."""

    @given(st.lists(st.integers(min_value=-100, max_value=100), min_size=1, max_size=100))
    def test_sum_associative(self, data: List[int]):
        """Sum should be associative."""
        # Split data into two parts
        mid = len(data) // 2
        part1 = data[:mid]
        part2 = data[mid:]
        
        total = sum(data)
        sum_parts = sum(part1) + sum(part2)
        assert total == sum_parts

    @given(st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=50))
    def test_sum_non_negative_positive(self, data: List[int]):
        """Sum of non-negative numbers is non-negative."""
        assert sum(data) >= 0

    @given(st.lists(st.integers(min_value=-100, max_value=0), min_size=1, max_size=50))
    def test_sum_non_positive_negative(self, data: List[int]):
        """Sum of non-positive numbers is non-positive."""
        assert sum(data) <= 0


class TestQuantileProperties:
    """Test properties of quantiles/percentiles."""

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=4, max_size=100))
    def test_quantiles_ordered(self, data: List[float]):
        """Quantiles should be in ascending order."""
        quantiles = statistics.quantiles(data, n=4)  # Quartiles
        for i in range(len(quantiles) - 1):
            assert quantiles[i] <= quantiles[i + 1]

    @given(st.lists(st.floats(min_value=-100, max_value=100, allow_nan=False, allow_infinity=False), min_size=10, max_size=100))
    def test_quantiles_within_range(self, data: List[float]):
        """Quantiles should be within data range."""
        quantiles = statistics.quantiles(data, n=10)
        min_val = min(data)
        max_val = max(data)
        for q in quantiles:
            assert min_val <= q <= max_val


class TestMinMaxProperties:
    """Test properties of min and max."""

    @given(st.lists(st.integers(), min_size=1, max_size=100))
    def test_min_less_than_max(self, data: List[int]):
        """Min should be <= Max."""
        assert min(data) <= max(data)

    @given(st.lists(st.integers(), min_size=1, max_size=100))
    def test_min_in_data(self, data: List[int]):
        """Min should be in data."""
        assert min(data) in data

    @given(st.lists(st.integers(), min_size=1, max_size=100))
    def test_max_in_data(self, data: List[int]):
        """Max should be in data."""
        assert max(data) in data

    @given(st.lists(st.integers(min_value=-100, max_value=100), min_size=2, max_size=100))
    def test_range_property(self, data: List[int]):
        """Range = Max - Min."""
        data_range = max(data) - min(data)
        assert data_range >= 0


class TestModeProperties:
    """Test properties of mode."""

    @given(st.lists(st.integers(min_value=1, max_value=10), min_size=5, max_size=50))
    def test_mode_in_data(self, data: List[int]):
        """Mode should be in the data."""
        try:
            mode = statistics.mode(data)
            assert mode in data
        except statistics.StatisticsError:
            # Multiple modes - acceptable
            pass

    @given(st.integers(min_value=-100, max_value=100))
    def test_mode_of_constant(self, c: int):
        """Mode of constant values is the constant."""
        data = [c] * 10
        mode = statistics.mode(data)
        assert mode == c


# Summary test
def test_statistics_properties_summary():
    """Summary of statistics property tests."""
    print("\n" + "=" * 60)
    print("📊 STATISTICS PROPERTY-BASED TESTING SUMMARY")
    print("=" * 60)
    print("\n✅ Properties Tested:")
    print("   - Mean properties (range, sum, translation, scaling)")
    print("   - Median properties (range, translation invariance)")
    print("   - Variance properties (non-negative, invariance)")
    print("   - Standard deviation properties")
    print("   - Correlation properties (range, perfect correlation)")
    print("   - Sum statistics (associative, sign preservation)")
    print("   - Quantile properties (ordering, range)")
    print("   - Min/Max properties")
    print("   - Mode properties")
    print("\n🎯 Test Generation:")
    print("   - Hypothesis generates 100+ test cases per property")
    print("   - Covers various data distributions")
    print("   - Tests edge cases automatically")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
