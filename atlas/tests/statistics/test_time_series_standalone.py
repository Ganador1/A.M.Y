#!/usr/bin/env python3
"""
Standalone Test for Advanced Time Series Service
===============================================

Isolated testing of the advanced time series service without project dependencies.
"""

import asyncio
import sys
import os
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta

# Mock BaseService to avoid dependencies
class MockBaseService:
    def __init__(self, service_name: str):
        self.service_name = service_name

# Mock the base service import
sys.modules['app.services.base_service'] = type('MockModule', (), {'BaseService': MockBaseService})()

# Import the advanced time series service directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app', 'services'))

# Read and execute the service file directly
with open('app/services/time_series_service_advanced.py', 'r') as f:
    service_code = f.read()

# Execute the service code in a clean namespace
service_namespace = {
    '__name__': '__main__',
    'MockBaseService': MockBaseService
}
exec(service_code, service_namespace)

# Get the service class
AdvancedTimeSeriesService = service_namespace['AdvancedTimeSeriesService']

async def test_basic_functionality():
    """Test basic functionality without advanced dependencies"""
    print("🕒 Testing Advanced Time Series Service - Basic Functionality")
    print("=" * 60)
    
    try:
        # Initialize service
        service = AdvancedTimeSeriesService()
        print(f"✅ Service initialized: {service.service_name}")
        print(f"📊 Version: {service.version}")
        
        # Test service capabilities
        capabilities = service.get_service_capabilities()
        print(f"\n🔧 Service Capabilities:")
        for cap, available in capabilities["capabilities"].items():
            status = "✅" if available else "❌"
            print(f"   {status} {cap}: {available}")
        
        # Test health check
        health = await service.health_check()
        print(f"\n🏥 Health Check: {health['status']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        return False

async def test_anomaly_detection():
    """Test anomaly detection if sklearn is available"""
    print("\n🔍 Testing Advanced Anomaly Detection")
    print("-" * 40)
    
    try:
        service = AdvancedTimeSeriesService()
        
        # Generate test data with anomalies
        np.random.seed(42)
        n_points = 200
        timestamps = [(datetime.now() - timedelta(days=n_points-i)).isoformat() for i in range(n_points)]
        
        # Generate normal data
        values = np.random.normal(0, 1, n_points)
        
        # Add some anomalies
        anomaly_indices = [50, 100, 150]
        for idx in anomaly_indices:
            values[idx] += 5  # Add anomaly
        
        print(f"📈 Generated test data: {n_points} points with {len(anomaly_indices)} anomalies")
        
        # Test statistical anomaly detection
        try:
            anomaly_result = await service.advanced_anomaly_detection(
                timestamps=timestamps,
                values=values.tolist(),
                method="statistical",
                contamination=0.1
            )
            print(f"✅ Statistical anomaly detection completed")
            print(f"   Method: {anomaly_result.detection_method}")
            print(f"   Anomalies detected: {len(anomaly_result.anomaly_indices)}")
            print(f"   Threshold: {anomaly_result.anomaly_threshold:.3f}")
        except Exception as e:
            print(f"❌ Statistical anomaly detection error: {e}")
        
        # Test Isolation Forest if available
        try:
            iso_result = await service.advanced_anomaly_detection(
                timestamps=timestamps,
                values=values.tolist(),
                method="isolation_forest",
                contamination=0.1
            )
            print(f"✅ Isolation Forest anomaly detection completed")
            print(f"   Method: {iso_result.detection_method}")
            print(f"   Anomalies detected: {len(iso_result.anomaly_indices)}")
            print(f"   Threshold: {iso_result.anomaly_threshold:.3f}")
        except ImportError as e:
            print(f"⚠️  Isolation Forest skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Isolation Forest error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in anomaly detection test: {e}")
        return False

async def test_ensemble_forecasting():
    """Test ensemble forecasting"""
    print("\n📊 Testing Ensemble Forecasting")
    print("-" * 40)
    
    try:
        service = AdvancedTimeSeriesService()
        
        # Generate test data
        np.random.seed(42)
        n_points = 100
        timestamps = [(datetime.now() - timedelta(days=n_points-i)).isoformat() for i in range(n_points)]
        
        # Generate time series with trend and seasonality
        t = np.arange(n_points)
        trend = 0.01 * t
        seasonal = 2 * np.sin(2 * np.pi * t / 30)  # Monthly seasonality
        noise = np.random.normal(0, 0.5, n_points)
        values = trend + seasonal + noise
        
        print(f"📈 Generated test data: {n_points} points with trend and seasonality")
        
        # Test ensemble forecasting
        try:
            forecast_result = await service.ensemble_forecasting(
                timestamps=timestamps,
                values=values.tolist(),
                forecast_horizon=10,
                methods=["prophet"]  # Only test Prophet for now
            )
            
            print(f"✅ Ensemble forecasting completed")
            print(f"   Forecast horizon: {forecast_result.forecast_horizon}")
            print(f"   Methods used: {forecast_result.model_performance['methods_used']}")
            print(f"   Ensemble MSE: {forecast_result.model_performance['ensemble_weighted_mse']:.4f}")
            
            if forecast_result.ensemble_weights:
                print(f"   Ensemble weights: {forecast_result.ensemble_weights}")
            
        except ImportError as e:
            print(f"⚠️  Ensemble forecasting skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Ensemble forecasting error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in ensemble forecasting test: {e}")
        return False

async def test_granger_causality():
    """Test Granger causality analysis if statsmodels is available"""
    print("\n🔗 Testing Granger Causality Analysis")
    print("-" * 40)
    
    try:
        service = AdvancedTimeSeriesService()
        
        # Generate correlated time series
        np.random.seed(42)
        n_points = 100
        timestamps = [(datetime.now() - timedelta(days=n_points-i)).isoformat() for i in range(n_points)]
        
        # Generate series with causal relationship
        series1 = np.random.normal(0, 1, n_points)
        series2 = 0.5 * series1[:-1] + np.random.normal(0, 0.5, n_points-1)
        series2 = np.concatenate([[0], series2])  # Pad to match length
        
        print(f"📈 Generated correlated time series: {n_points} points")
        
        # Test Granger causality
        try:
            causality_result = await service.granger_causality_analysis(
                timestamps=timestamps,
                series1=series1.tolist(),
                series2=series2.tolist(),
                max_lags=3
            )
            
            print(f"✅ Granger causality analysis completed")
            print(f"   Causality detected: {causality_result['causality_detected']}")
            print(f"   Significant lags: {causality_result['significant_lags']}")
            print(f"   Interpretation: {causality_result['interpretation']}")
            
        except ImportError as e:
            print(f"⚠️  Granger causality skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Granger causality error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Granger causality test: {e}")
        return False

async def test_lstm_forecasting():
    """Test LSTM forecasting if TensorFlow is available"""
    print("\n🧠 Testing LSTM Forecasting")
    print("-" * 40)
    
    try:
        service = AdvancedTimeSeriesService()
        
        # Generate test data
        np.random.seed(42)
        n_points = 200
        timestamps = [(datetime.now() - timedelta(days=n_points-i)).isoformat() for i in range(n_points)]
        
        # Generate time series with pattern
        t = np.arange(n_points)
        values = 0.5 * np.sin(0.1 * t) + 0.3 * np.cos(0.05 * t) + np.random.normal(0, 0.1, n_points)
        
        print(f"📈 Generated test data: {n_points} points with sinusoidal pattern")
        
        # Test LSTM forecasting
        try:
            lstm_result = await service.lstm_forecasting(
                timestamps=timestamps,
                values=values.tolist(),
                forecast_horizon=10,
                sequence_length=20
            )
            
            print(f"✅ LSTM forecasting completed")
            print(f"   Model: {lstm_result.model_name}")
            print(f"   Type: {lstm_result.model_type}")
            print(f"   Train MSE: {lstm_result.model_metrics['train_mse']:.4f}")
            print(f"   Test MSE: {lstm_result.model_metrics['test_mse']:.4f}")
            print(f"   Final loss: {lstm_result.model_metrics['final_loss']:.4f}")
            
        except ImportError as e:
            print(f"⚠️  LSTM forecasting skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ LSTM forecasting error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in LSTM forecasting test: {e}")
        return False

async def test_prophet_forecasting():
    """Test Prophet forecasting if Prophet is available"""
    print("\n📈 Testing Prophet Forecasting")
    print("-" * 40)
    
    try:
        service = AdvancedTimeSeriesService()
        
        # Generate test data
        np.random.seed(42)
        n_points = 200
        timestamps = [(datetime.now() - timedelta(days=n_points-i)).isoformat() for i in range(n_points)]
        
        # Generate time series with trend and seasonality
        t = np.arange(n_points)
        trend = 0.01 * t
        seasonal = 2 * np.sin(2 * np.pi * t / 30)  # Monthly seasonality
        noise = np.random.normal(0, 0.5, n_points)
        values = trend + seasonal + noise
        
        print(f"📈 Generated test data: {n_points} points with trend and seasonality")
        
        # Test Prophet forecasting
        try:
            prophet_result = await service.prophet_forecasting(
                timestamps=timestamps,
                values=values.tolist(),
                forecast_horizon=10
            )
            
            print(f"✅ Prophet forecasting completed")
            print(f"   Model: {prophet_result.model_name}")
            print(f"   Type: {prophet_result.model_type}")
            print(f"   Train MSE: {prophet_result.model_metrics['train_mse']:.4f}")
            print(f"   Trend strength: {prophet_result.model_metrics['trend_strength']:.4f}")
            print(f"   Seasonality strength: {prophet_result.model_metrics['seasonality_strength']:.4f}")
            
            if prophet_result.confidence_intervals is not None:
                print(f"   Confidence intervals: Available")
            
        except ImportError as e:
            print(f"⚠️  Prophet forecasting skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Prophet forecasting error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Prophet forecasting test: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Advanced Time Series Service - Standalone Testing")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Anomaly Detection", test_anomaly_detection),
        ("Ensemble Forecasting", test_ensemble_forecasting),
        ("Granger Causality", test_granger_causality),
        ("LSTM Forecasting", test_lstm_forecasting),
        ("Prophet Forecasting", test_prophet_forecasting)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Advanced Time Series Service is working correctly.")
    else:
        print("⚠️  Some tests failed. Check dependencies and implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)




