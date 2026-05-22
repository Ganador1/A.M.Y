"""
Tests for Statistics Service
"""

import pytest
import numpy as np
from app.domains.mathematics.services.statistics_service import StatisticsService


class TestStatisticsService:
    """Test cases for StatisticsService"""

    @pytest.fixture
    def service(self):
        """Fixture to provide StatisticsService instance"""
        return StatisticsService()

    def test_descriptive_statistics_basic(self, service):
        """Test basic descriptive statistics"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = service.descriptive_statistics(data)

        assert result['status'] == 'success'
        assert result['count'] == 10
        assert result['mean'] == 5.5
        assert result['median'] == 5.5
        assert result['std_dev'] == pytest.approx(3.02765, rel=1e-5)
        assert result['min'] == 1
        assert result['max'] == 10

    def test_descriptive_statistics_with_outliers(self, service):
        """Test descriptive statistics with outliers"""
        data = [1, 2, 3, 4, 5, 100]  # 100 is an outlier
        result = service.descriptive_statistics(data)

        assert result['status'] == 'success'
        assert result['count'] == 6
        assert result['mean'] == pytest.approx(19.16667, rel=1e-5)
        assert result['median'] == 3.5
        assert result['min'] == 1
        assert result['max'] == 100

    def test_probability_distributions_normal(self, service):
        """Test normal distribution calculations"""
        result = service.normal_distribution(
            mean=0, std_dev=1, x_value=1.0
        )

        assert result['status'] == 'success'
        assert 'pdf' in result
        assert 'cdf' in result
        assert 'percentile' in result
        assert result['pdf'] > 0
        assert result['cdf'] == pytest.approx(0.84134, rel=1e-5)

    def test_probability_distributions_binomial(self, service):
        """Test binomial distribution calculations"""
        result = service.binomial_distribution(
            n=10, p=0.5, k=5
        )

        assert result['status'] == 'success'
        assert 'pmf' in result
        assert 'cdf' in result
        assert 'mean' in result
        assert 'variance' in result
        assert result['pmf'] == pytest.approx(0.24609, rel=1e-5)
        assert result['mean'] == 5.0
        assert result['variance'] == 2.5

    def test_probability_distributions_poisson(self, service):
        """Test Poisson distribution calculations"""
        result = service.poisson_distribution(
            lambda_param=3.0, k=2
        )

        assert result['status'] == 'success'
        assert 'pmf' in result
        assert 'cdf' in result
        assert 'mean' in result
        assert 'variance' in result
        assert result['pmf'] > 0
        assert result['mean'] == 3.0
        assert result['variance'] == 3.0

    def test_hypothesis_testing_t_test(self, service):
        """Test t-test hypothesis testing"""
        sample1 = [1, 2, 3, 4, 5]
        sample2 = [2, 3, 4, 5, 6]

        result = service.t_test(sample1, sample2)

        assert result['status'] == 'success'
        assert 't_statistic' in result
        assert 'p_value' in result
        assert 'degrees_of_freedom' in result
        assert 'confidence_interval' in result

    def test_hypothesis_testing_chi_square(self, service):
        """Test chi-square test"""
        observed = [10, 12, 8, 10]
        expected = [10, 10, 10, 10]

        result = service.chi_square_test(observed, expected)

        assert result['status'] == 'success'
        assert 'chi_square_statistic' in result
        assert 'p_value' in result
        assert 'degrees_of_freedom' in result

    def test_correlation_analysis_pearson(self, service):
        """Test Pearson correlation analysis"""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]

        result = service.correlation_analysis(x, y, method='pearson')

        assert result['status'] == 'success'
        assert 'correlation_coefficient' in result
        assert 'p_value' in result
        assert result['correlation_coefficient'] == 1.0

    def test_correlation_analysis_spearman(self, service):
        """Test Spearman correlation analysis"""
        x = [1, 2, 3, 4, 5]
        y = [1, 3, 2, 5, 4]

        result = service.correlation_analysis(x, y, method='spearman')

        assert result['status'] == 'success'
        assert 'correlation_coefficient' in result
        assert 'p_value' in result
        assert result['correlation_coefficient'] > 0

    def test_regression_analysis_linear(self, service):
        """Test linear regression analysis"""
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]

        result = service.linear_regression(x, y)

        assert result['status'] == 'success'
        assert 'slope' in result
        assert 'intercept' in result
        assert 'r_squared' in result
        assert 'p_value' in result
        assert result['slope'] == 2.0
        assert result['intercept'] == 0.0
        assert result['r_squared'] == 1.0

    def test_regression_analysis_polynomial(self, service):
        """Test polynomial regression analysis"""
        x = [1, 2, 3, 4, 5]
        y = [1, 4, 9, 16, 25]  # x^2

        result = service.polynomial_regression(x, y, degree=2)

        assert result['status'] == 'success'
        assert 'coefficients' in result
        assert 'r_squared' in result
        assert result['r_squared'] == 1.0
        assert len(result['coefficients']) == 3

    def test_confidence_intervals_mean(self, service):
        """Test confidence interval for mean"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = service.confidence_interval_mean(data, confidence_level=0.95)

        assert result['status'] == 'success'
        assert 'mean' in result
        assert 'confidence_interval' in result
        assert 'margin_of_error' in result
        assert len(result['confidence_interval']) == 2

    def test_confidence_intervals_proportion(self, service):
        """Test confidence interval for proportion"""
        successes = 35
        total = 100
        result = service.confidence_interval_proportion(successes, total, confidence_level=0.95)

        assert result['status'] == 'success'
        assert 'proportion' in result
        assert 'confidence_interval' in result
        assert 'margin_of_error' in result
        assert result['proportion'] == 0.35

    def test_anova_single_factor(self, service):
        """Test single-factor ANOVA"""
        group1 = [1, 2, 3, 4, 5]
        group2 = [2, 3, 4, 5, 6]
        group3 = [3, 4, 5, 6, 7]

        result = service.anova_single_factor([group1, group2, group3])

        assert result['status'] == 'success'
        assert 'f_statistic' in result
        assert 'p_value' in result
        assert 'degrees_of_freedom' in result

    def test_time_series_analysis_trend(self, service):
        """Test time series trend analysis"""
        data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        result = service.time_series_trend_analysis(data)

        assert result['status'] == 'success'
        assert 'trend_coefficient' in result
        assert 'trend_intercept' in result
        assert 'r_squared' in result

    def test_time_series_analysis_seasonal(self, service):
        """Test time series seasonal analysis"""
        # Create data with seasonal pattern
        data = [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4]
        result = service.time_series_seasonal_analysis(data, season_length=4)

        assert result['status'] == 'success'
        assert 'seasonal_indices' in result
        assert 'trend' in result
        assert 'residuals' in result

    def test_quality_control_control_charts(self, service):
        """Test quality control using control charts"""
        data = [10.1, 9.9, 10.0, 10.2, 9.8, 10.1, 9.9, 10.0, 10.1, 9.9]
        result = service.control_chart_x_bar(data, subgroup_size=2)

        assert result['status'] == 'success'
        assert 'center_line' in result
        assert 'upper_control_limit' in result
        assert 'lower_control_limit' in result
        assert 'points' in result

    def test_quality_control_capability_analysis(self, service):
        """Test process capability analysis"""
        data = np.random.normal(10, 0.5, 100)
        result = service.process_capability_analysis(data, lsl=9.0, usl=11.0)

        assert result['status'] == 'success'
        assert 'cp' in result
        assert 'cpk' in result
        assert 'pp' in result
        assert 'ppk' in result

    def test_bayesian_statistics_beta_binomial(self, service):
        """Test Bayesian beta-binomial analysis"""
        successes = 7
        trials = 10
        result = service.bayesian_beta_binomial(successes, trials, alpha_prior=1, beta_prior=1)

        assert result['status'] == 'success'
        assert 'posterior_mean' in result
        assert 'posterior_variance' in result
        assert 'credible_interval' in result

    def test_bayesian_statistics_normal_normal(self, service):
        """Test Bayesian normal-normal analysis"""
        data = [9.8, 10.1, 9.9, 10.0, 10.2]
        result = service.bayesian_normal_normal(data, mu_prior=10, sigma_prior=1, sigma_known=0.5)

        assert result['status'] == 'success'
        assert 'posterior_mean' in result
        assert 'posterior_variance' in result
        assert 'credible_interval' in result

    def test_statistics_with_invalid_data(self, service):
        """Test statistics with invalid data"""
        result = service.descriptive_statistics([])

        assert result['status'] == 'error'
        assert 'error' in result

    def test_correlation_with_mismatched_lengths(self, service):
        """Test correlation with mismatched data lengths"""
        x = [1, 2, 3]
        y = [1, 2]

        result = service.correlation_analysis(x, y)

        assert result['status'] == 'error'
        assert 'error' in result

    def test_regression_with_insufficient_data(self, service):
        """Test regression with insufficient data"""
        x = [1]
        y = [2]

        result = service.linear_regression(x, y)

        assert result['status'] == 'error'
        assert 'error' in result
