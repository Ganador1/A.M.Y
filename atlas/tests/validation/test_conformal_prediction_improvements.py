#!/usr/bin/env python3
"""
Test script for Advanced Conformal Prediction improvements
=========================================================

This script tests the enhanced features of the conformal prediction service
without requiring the full AXIOM application dependencies.

Author: AXIOM Research Team
Date: December 2024
"""

import asyncio
import numpy as np
import sys
import time
from pathlib import Path
from unittest.mock import patch, Mock

# Direct import without app dependencies
sys.path.insert(0, str(Path(__file__).parent / 'app' / 'services'))

# Import directly
from conformal_prediction_improved import (
    AdvancedConformalPredictionService,
    AdvancedSplitConformalPredictor,
    ConditionalConformalPredictor,
    OnlineAdaptiveConformalPredictor,
    ConformalResult
)

def generate_test_data(n_samples=200, n_features=5, noise_level=0.1, random_state=42):
    """Generate synthetic test data for conformal prediction"""
    np.random.seed(random_state)
    
    # Generate features
    X = np.random.randn(n_samples, n_features)
    
    # Generate targets with some non-linear relationship (ensure we don't exceed n_features)
    if n_features >= 4:
        y = (X[:, 0] ** 2 + 
             2 * X[:, 1] + 
             0.5 * X[:, 2] * X[:, 3] + 
             noise_level * np.random.randn(n_samples))
    elif n_features >= 3:
        y = (X[:, 0] ** 2 + 
             2 * X[:, 1] + 
             0.5 * X[:, 2] + 
             noise_level * np.random.randn(n_samples))
    elif n_features >= 2:
        y = (X[:, 0] ** 2 + 
             2 * X[:, 1] + 
             noise_level * np.random.randn(n_samples))
    else:
        y = (X[:, 0] ** 2 + 
             noise_level * np.random.randn(n_samples))
    
    return X, y

async def test_basic_initialization():
    """Test basic service initialization"""
    print("🔧 Testing basic initialization...")
    
    service = AdvancedConformalPredictionService()
    
    print(f"   Available methods: {list(service.predictors.keys())}")
    print(f"   Parallel processing: {service.enable_parallel}")
    print(f"   Cache enabled: {service.cache_predictions}")
    
    assert len(service.predictors) >= 3, "Should have at least 3 prediction methods"
    assert 'advanced_split' in service.predictors, "Should have advanced split method"
    assert 'conditional' in service.predictors, "Should have conditional method"
    assert 'online_adaptive' in service.predictors, "Should have online adaptive method"
    
    print("   ✅ Basic initialization passed!")
    return True

async def test_advanced_split_conformal():
    """Test advanced split conformal prediction"""
    print("\n📊 Testing advanced split conformal prediction...")
    
    # Generate test data
    X, y = generate_test_data(n_samples=150, n_features=3)
    X_train, y_train = X[:100], y[:100]
    X_test, y_test = X[100:], y[100:]
    
    service = AdvancedConformalPredictionService()
    
    try:
        result = await service.fit_and_predict(
            X_train, y_train, X_test,
            method='advanced_split',
            confidence_level=0.9,
            enable_cross_validation=True,
            enable_diagnostics=True
        )
        
        print(f"   Predictions shape: {result.predictions.shape}")
        print(f"   Confidence level: {result.confidence_level}")
        print(f"   Method: {result.method}")
        print(f"   Mean interval width: {np.mean(result.interval_width):.3f}")
        
        # Validate result structure
        assert isinstance(result, ConformalResult), "Should return ConformalResult"
        assert len(result.predictions) == len(X_test), "Predictions length should match test data"
        assert len(result.lower_bound) == len(X_test), "Lower bound length should match"
        assert len(result.upper_bound) == len(X_test), "Upper bound length should match"
        assert np.all(result.lower_bound <= result.upper_bound), "Lower bound should be <= upper bound"
        
        # Check efficiency metrics
        if result.efficiency_metrics:
            print(f"   Efficiency metrics: {len(result.efficiency_metrics)} metrics")
            assert 'mean_interval_width' in result.efficiency_metrics, "Should have efficiency metrics"
        
        # Check computational metrics
        if result.computational_metrics:
            print(f"   Computational time: {result.computational_metrics.get('prediction_time', 0):.3f}s")
            assert 'prediction_time' in result.computational_metrics, "Should have timing metrics"
        
        # Evaluate coverage
        coverage_eval = service.evaluate_comprehensive_coverage(y_test, result)
        print(f"   Empirical coverage: {coverage_eval.get('empirical_coverage', 0):.3f}")
        print(f"   Coverage error: {coverage_eval.get('coverage_error', 0):.3f}")
        
        assert 'empirical_coverage' in coverage_eval, "Should evaluate coverage"
        
        print("   ✅ Advanced split conformal prediction passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_conditional_conformal():
    """Test conditional conformal prediction"""
    print("\n🎯 Testing conditional conformal prediction...")
    
    # Generate heteroscedastic test data
    np.random.seed(42)
    X = np.random.randn(100, 2)
    # Heteroscedastic noise (variance depends on X)
    noise_variance = 0.1 + 0.5 * np.abs(X[:, 0])
    y = X[:, 0] + X[:, 1] + noise_variance * np.random.randn(100)
    
    X_train, y_train = X[:70], y[:70]
    X_test, y_test = X[70:], y[70:]
    
    service = AdvancedConformalPredictionService()
    
    try:
        result = await service.fit_and_predict(
            X_train, y_train, X_test,
            method='conditional',
            confidence_level=0.9
        )
        
        print(f"   Predictions generated: {len(result.predictions)}")
        print(f"   Method: {result.method}")
        print(f"   Interval width variance: {np.var(result.interval_width):.3f}")
        
        # Validate adaptive intervals (should have different widths)
        width_variance = np.var(result.interval_width)
        assert width_variance > 0, "Conditional method should produce variable interval widths"
        
        # Basic validation
        assert len(result.predictions) == len(X_test), "Correct number of predictions"
        assert result.method == 'conditional', "Correct method identifier"
        
        print("   ✅ Conditional conformal prediction passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_online_adaptive_conformal():
    """Test online adaptive conformal prediction"""
    print("\n🔄 Testing online adaptive conformal prediction...")
    
    X, y = generate_test_data(n_samples=120, n_features=2)
    X_train, y_train = X[:80], y[:80]
    X_test, y_test = X[80:100], y[80:100]
    X_update, y_update = X[100:], y[100:]
    
    service = AdvancedConformalPredictionService()
    
    try:
        # Initial fit and predict
        result = await service.fit_and_predict(
            X_train, y_train, X_test,
            method='online_adaptive',
            confidence_level=0.9,
            window_size=50,
            adaptation_rate=0.05
        )
        
        print(f"   Initial predictions: {len(result.predictions)}")
        print(f"   Method: {result.method}")
        
        # Validate basic structure
        assert result.method == 'online_adaptive', "Correct method identifier"
        assert len(result.predictions) == len(X_test), "Correct number of predictions"
        
        # Test update capability (create predictor directly for update test)
        predictor = OnlineAdaptiveConformalPredictor(window_size=50)
        X_cal = X_train[:30]
        y_cal = y_train[:30]
        X_tr = X_train[30:]
        y_tr = y_train[30:]
        
        predictor.fit(X_tr, y_tr, X_cal, y_cal)
        
        # Test update
        predictor.update(X_update, y_update, actual_coverage=0.85)
        
        # Check that history was updated
        assert len(predictor.conformity_scores_history) > 0, "Should have conformity scores"
        assert len(predictor.coverage_history) > 0, "Should track coverage history"
        
        print(f"   Conformity scores history: {len(predictor.conformity_scores_history)} scores")
        print(f"   Coverage history: {len(predictor.coverage_history)} entries")
        
        print("   ✅ Online adaptive conformal prediction passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_comprehensive_evaluation():
    """Test comprehensive evaluation features"""
    print("\n📈 Testing comprehensive evaluation...")
    
    X, y = generate_test_data(n_samples=100, n_features=3)
    X_train, y_train = X[:70], y[:70]
    X_test, y_test = X[70:], y[70:]
    
    service = AdvancedConformalPredictionService()
    
    try:
        result = await service.fit_and_predict(
            X_train, y_train, X_test,
            method='advanced_split',
            confidence_level=0.9
        )
        
        # Comprehensive evaluation
        evaluation = service.evaluate_comprehensive_coverage(y_test, result)
        
        print(f"   Evaluation metrics: {len(evaluation)} metrics")
        print(f"   Empirical coverage: {evaluation.get('empirical_coverage', 0):.3f}")
        print(f"   Coverage error: {evaluation.get('coverage_error', 0):.3f}")
        print(f"   Efficiency score: {evaluation.get('efficiency_score', 0):.3f}")
        print(f"   Calibration error: {evaluation.get('calibration_error', 0):.3f}")
        
        # Validate evaluation structure
        expected_metrics = [
            'empirical_coverage', 'target_coverage', 'coverage_error',
            'mean_interval_width', 'efficiency_score', 'calibration_error'
        ]
        
        for metric in expected_metrics:
            assert metric in evaluation, f"Evaluation should include {metric}"
        
        # Check conditional coverage
        if 'conditional_coverage' in evaluation:
            print(f"   Conditional coverage: {len(evaluation['conditional_coverage'])} quantiles")
        
        print("   ✅ Comprehensive evaluation passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_legacy_compatibility():
    """Test legacy compatibility methods"""
    print("\n🔄 Testing legacy compatibility...")
    
    X, y = generate_test_data(n_samples=80, n_features=2)
    X_cal, y_cal = X[:40], y[:40]
    X_test, y_test = X[40:], y[40:]
    
    service = AdvancedConformalPredictionService()
    
    try:
        # Test legacy split conformal method
        result = service.split_conformal_prediction(
            X_cal, y_cal, X_test, alpha=0.1
        )
        
        print(f"   Legacy result keys: {list(result.keys())}")
        print(f"   Predictions shape: {result['predictions'].shape}")
        print(f"   Intervals shape: {result['prediction_intervals'].shape}")
        print(f"   Coverage probability: {result['coverage_probability']}")
        
        # Validate legacy format
        expected_keys = [
            'predictions', 'prediction_intervals', 'coverage_probability',
            'interval_width', 'method', 'alpha'
        ]
        
        for key in expected_keys:
            assert key in result, f"Legacy result should include {key}"
        
        assert result['method'] == 'split_conformal', "Should use legacy method name"
        assert result['alpha'] == 0.1, "Should preserve alpha parameter"
        assert result['prediction_intervals'].shape[1] == 2, "Should have lower and upper bounds"
        
        print("   ✅ Legacy compatibility passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_caching_functionality():
    """Test caching functionality"""
    print("\n💾 Testing caching functionality...")
    
    X, y = generate_test_data(n_samples=60, n_features=2)
    X_train, y_train = X[:40], y[:40]
    X_test, y_test = X[40:], y[40:]
    
    service = AdvancedConformalPredictionService(cache_predictions=True)
    
    try:
        # First prediction (should cache)
        start_time = time.time()
        result1 = await service.fit_and_predict(
            X_train, y_train, X_test,
            method='advanced_split',
            confidence_level=0.9
        )
        first_time = time.time() - start_time
        
        # Second prediction (should use cache)
        start_time = time.time()
        result2 = await service.fit_and_predict(
            X_train, y_train, X_test,
            method='advanced_split',
            confidence_level=0.9
        )
        second_time = time.time() - start_time
        
        print(f"   First prediction time: {first_time:.3f}s")
        print(f"   Second prediction time: {second_time:.3f}s")
        print(f"   Speedup ratio: {first_time / second_time:.1f}x" if second_time > 0 else "   Instant cache hit")
        
        # Validate cache info
        cache_info = service.get_cache_info()
        print(f"   Cache size: {cache_info['cache_size']}")
        print(f"   Cache enabled: {cache_info['cache_enabled']}")
        
        assert cache_info['cache_size'] > 0, "Cache should contain predictions"
        assert cache_info['cache_enabled'], "Cache should be enabled"
        
        # Results should be identical
        np.testing.assert_array_equal(result1.predictions, result2.predictions, 
                                    "Cached results should be identical")
        
        # Test cache clearing
        service.clear_cache()
        cache_info_after = service.get_cache_info()
        assert cache_info_after['cache_size'] == 0, "Cache should be empty after clearing"
        
        print("   ✅ Caching functionality passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_error_handling():
    """Test robust error handling"""
    print("\n🛡️ Testing error handling...")
    
    service = AdvancedConformalPredictionService()
    
    try:
        # Test with invalid inputs
        test_cases = [
            # Invalid method
            {
                'X_train': np.random.randn(50, 2),
                'y_train': np.random.randn(50),
                'X_test': np.random.randn(10, 2),
                'method': 'invalid_method',
                'expected_error': ValueError
            },
            # Invalid confidence level
            {
                'X_train': np.random.randn(50, 2),
                'y_train': np.random.randn(50),
                'X_test': np.random.randn(10, 2),
                'confidence_level': 1.5,
                'expected_error': ValueError
            },
            # Mismatched dimensions
            {
                'X_train': np.random.randn(50, 2),
                'y_train': np.random.randn(50),
                'X_test': np.random.randn(10, 3),  # Different number of features
                'expected_error': ValueError
            }
        ]
        
        errors_caught = 0
        
        for i, test_case in enumerate(test_cases):
            try:
                await service.fit_and_predict(**{k: v for k, v in test_case.items() if k != 'expected_error'})
                print(f"   ❌ Test case {i+1}: Expected {test_case['expected_error'].__name__} but no error raised")
            except test_case['expected_error']:
                print(f"   ✅ Test case {i+1}: Correctly caught {test_case['expected_error'].__name__}")
                errors_caught += 1
            except Exception as e:
                print(f"   ⚠️ Test case {i+1}: Unexpected error {type(e).__name__}: {e}")
        
        assert errors_caught == len(test_cases), f"Should catch all {len(test_cases)} expected errors"
        
        print("   ✅ Error handling passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def test_performance_benchmarks():
    """Test performance with various data sizes"""
    print("\n⚡ Testing performance benchmarks...")
    
    service = AdvancedConformalPredictionService()
    
    data_sizes = [50, 100, 200]
    performance_results = {}
    
    try:
        for n_samples in data_sizes:
            X, y = generate_test_data(n_samples=n_samples, n_features=5)
            X_train, y_train = X[:int(0.7*n_samples)], y[:int(0.7*n_samples)]
            X_test, y_test = X[int(0.7*n_samples):], y[int(0.7*n_samples):]
            
            start_time = time.time()
            result = await service.fit_and_predict(
                X_train, y_train, X_test,
                method='advanced_split',
                confidence_level=0.9
            )
            total_time = time.time() - start_time
            
            performance_results[n_samples] = {
                'total_time': total_time,
                'time_per_prediction': total_time / len(X_test),
                'mean_interval_width': np.mean(result.interval_width)
            }
            
            print(f"   Size {n_samples}: {total_time:.3f}s total, {total_time/len(X_test)*1000:.1f}ms per prediction")
        
        # Check that performance scales reasonably
        small_time = performance_results[50]['time_per_prediction']
        large_time = performance_results[200]['time_per_prediction']
        
        # Performance shouldn't degrade too much with size
        scaling_factor = large_time / small_time
        print(f"   Performance scaling factor: {scaling_factor:.2f}x")
        
        assert scaling_factor < 10, "Performance shouldn't degrade too much with data size"
        
        print("   ✅ Performance benchmarks passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Testing Advanced Conformal Prediction Service")
    print("=" * 70)
    
    tests = [
        test_basic_initialization,
        test_advanced_split_conformal,
        test_conditional_conformal,
        test_online_adaptive_conformal,
        test_comprehensive_evaluation,
        test_legacy_compatibility,
        test_caching_functionality,
        test_error_handling,
        test_performance_benchmarks
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    start_time = time.time()
    
    for test in tests:
        try:
            success = await test()
            if success:
                passed_tests += 1
        except Exception as e:
            print(f"   ❌ Test failed with error: {e}")
    
    total_time = time.time() - start_time
    
    print("\n" + "=" * 70)
    print(f"🎉 Test Results: {passed_tests}/{total_tests} tests passed")
    print(f"⏱️ Total test time: {total_time:.2f} seconds")
    
    if passed_tests == total_tests:
        print("✨ All tests passed successfully!")
        print("\n🎯 Advanced Conformal Prediction features verified:")
        print("   ✅ Enhanced service initialization and configuration")
        print("   ✅ Advanced split conformal prediction with diagnostics")
        print("   ✅ Conditional conformal prediction for heteroscedastic data")
        print("   ✅ Online adaptive conformal prediction with updates")
        print("   ✅ Comprehensive evaluation and coverage analysis")
        print("   ✅ Legacy compatibility with existing interfaces")
        print("   ✅ Intelligent caching and performance optimization")
        print("   ✅ Robust error handling and validation")
        print("   ✅ Performance scaling and benchmarking")
        print("\n🚀 Ready for production use with advanced uncertainty quantification!")
        return True
    else:
        print("⚠️ Some tests failed - check the implementation")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
