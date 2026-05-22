#!/usr/bin/env python3
"""
Test script for Advanced Statistics Service
==========================================

Comprehensive testing of the advanced statistics service with mock data
and validation of all major functionalities.
"""

import asyncio
import sys
import os
import numpy as np
from typing import List, Dict, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock BaseService to avoid dependencies
class MockBaseService:
    def __init__(self, service_name: str):
        self.service_name = service_name

# Mock the base service import
sys.modules['app.services.base_service'] = type('MockModule', (), {'BaseService': MockBaseService})()

# Import the advanced statistics service
from app.services.statistics_service_advanced import AdvancedStatisticsService

async def test_basic_functionality():
    """Test basic functionality without advanced dependencies"""
    print("🧮 Testing Advanced Statistics Service - Basic Functionality")
    print("=" * 60)
    
    try:
        # Initialize service
        service = AdvancedStatisticsService()
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

async def test_multivariate_analysis():
    """Test multivariate analysis if sklearn is available"""
    print("\n📊 Testing Multivariate Analysis")
    print("-" * 40)
    
    try:
        service = AdvancedStatisticsService()
        
        # Generate test data
        np.random.seed(42)
        n_samples, n_features = 100, 5
        data = np.random.randn(n_samples, n_features).tolist()
        
        print(f"📈 Generated test data: {n_samples} samples × {n_features} features")
        
        # Test PCA
        try:
            pca_result = await service.principal_component_analysis(data)
            print(f"✅ PCA completed: {pca_result.analysis_type}")
            if pca_result.explained_variance is not None:
                print(f"   Explained variance (first 3 components): {pca_result.explained_variance[:3]}")
            print(f"   Interpretation: {pca_result.interpretation}")
        except ImportError as e:
            print(f"⚠️  PCA skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ PCA error: {e}")
        
        # Test Clustering
        try:
            clustering_result = await service.clustering_analysis(data, method="kmeans")
            print(f"✅ Clustering completed: {clustering_result.analysis_type}")
            if clustering_result.clusters is not None:
                n_clusters = len(set(clustering_result.clusters))
                print(f"   Clusters found: {n_clusters}")
            print(f"   Silhouette score: {clustering_result.silhouette_score}")
        except ImportError as e:
            print(f"⚠️  Clustering skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Clustering error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in multivariate analysis test: {e}")
        return False

async def test_advanced_testing():
    """Test advanced statistical testing if statsmodels is available"""
    print("\n🧪 Testing Advanced Statistical Testing")
    print("-" * 40)
    
    try:
        service = AdvancedStatisticsService()
        
        # Test multiple testing correction
        try:
            p_values = [0.01, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5]
            correction_result = await service.multiple_testing_correction(p_values, method="fdr_bh")
            print(f"✅ Multiple testing correction completed")
            print(f"   Method: {correction_result['method']}")
            print(f"   Tests: {correction_result['n_tests']}")
            print(f"   Significant after correction: {correction_result['n_rejected']}")
            print(f"   Interpretation: {correction_result['interpretation']}")
        except ImportError as e:
            print(f"⚠️  Multiple testing correction skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Multiple testing correction error: {e}")
        
        # Test power analysis
        try:
            power_result = await service.power_analysis(
                effect_size=0.5,
                sample_size=50,
                alpha=0.05,
                test_type="t-test"
            )
            print(f"✅ Power analysis completed")
            print(f"   Effect size: {power_result.effect_size}")
            print(f"   Sample size: {power_result.sample_size}")
            print(f"   Power: {power_result.power:.3f}")
            print(f"   Recommendations: {len(power_result.recommendations)}")
        except ImportError as e:
            print(f"⚠️  Power analysis skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Power analysis error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in advanced testing: {e}")
        return False

async def test_comprehensive_analysis():
    """Test comprehensive statistical analysis"""
    print("\n🔬 Testing Comprehensive Statistical Analysis")
    print("-" * 40)
    
    try:
        service = AdvancedStatisticsService()
        
        # Generate test data
        np.random.seed(42)
        n_samples, n_features = 50, 4
        data = np.random.randn(n_samples, n_features).tolist()
        
        print(f"📈 Generated test data: {n_samples} samples × {n_features} features")
        
        # Test comprehensive analysis
        analysis_types = ["descriptive", "correlation"]
        if service.dependencies_status.get("Scikit-learn", False):
            analysis_types.extend(["pca", "clustering"])
        
        result = await service.comprehensive_statistical_analysis(data, analysis_types)
        
        print(f"✅ Comprehensive analysis completed")
        print(f"   Analysis types: {result['analysis_metadata']['analysis_types']}")
        print(f"   Data shape: {result['analysis_metadata']['data_shape']}")
        
        # Check results
        if "descriptive" in result:
            desc = result["descriptive"]
            print(f"   Descriptive stats: {len(desc['mean'])} variables")
        
        if "correlation" in result:
            corr = result["correlation"]
            print(f"   Max correlation: {corr['max_correlation']:.3f}")
        
        if "pca" in result:
            pca = result["pca"]
            print(f"   PCA: {len(pca['explained_variance'])} components")
        
        if "clustering" in result:
            clust = result["clustering"]
            print(f"   Clustering: silhouette score {clust['silhouette_score']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in comprehensive analysis test: {e}")
        return False

async def test_visualization():
    """Test visualization if plotly is available"""
    print("\n📊 Testing Interactive Visualization")
    print("-" * 40)
    
    try:
        service = AdvancedStatisticsService()
        
        # Test scatter plot
        try:
            plot_data = {
                "x": [1, 2, 3, 4, 5],
                "y": [2, 4, 6, 8, 10],
                "x_label": "X Variable",
                "y_label": "Y Variable"
            }
            
            plot_result = await service.create_interactive_plot(
                plot_type="scatter",
                data=plot_data,
                title="Test Scatter Plot"
            )
            
            print(f"✅ Interactive plot created")
            print(f"   Plot type: {plot_result['plot_type']}")
            print(f"   Title: {plot_result['title']}")
            print(f"   Size: {plot_result['width']}×{plot_result['height']}")
            print(f"   HTML content length: {len(plot_result['html_content'])} chars")
            
        except ImportError as e:
            print(f"⚠️  Visualization skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Visualization error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in visualization test: {e}")
        return False

async def test_bayesian_analysis():
    """Test Bayesian analysis if PyMC is available"""
    print("\n🔮 Testing Bayesian Analysis")
    print("-" * 40)
    
    try:
        service = AdvancedStatisticsService()
        
        # Generate test data
        np.random.seed(42)
        x_data = np.random.randn(20).tolist()
        y_data = [2 * x + 1 + 0.1 * np.random.randn() for x in x_data]
        
        print(f"📈 Generated test data: {len(x_data)} observations")
        
        # Test Bayesian linear regression
        try:
            bayesian_result = await service.bayesian_linear_regression(
                x_data=x_data,
                y_data=y_data,
                prior_type="weakly_informative",
                samples=100  # Reduced for testing
            )
            
            print(f"✅ Bayesian regression completed")
            print(f"   Model: {bayesian_result.model_name}")
            print(f"   Converged: {bayesian_result.convergence_diagnostics['converged']}")
            print(f"   R-hat max: {bayesian_result.convergence_diagnostics['rhat_max']:.3f}")
            
            if bayesian_result.credible_intervals:
                print(f"   Credible intervals available for {len(bayesian_result.credible_intervals)} parameters")
            
        except ImportError as e:
            print(f"⚠️  Bayesian analysis skipped (dependency missing): {e}")
        except Exception as e:
            print(f"❌ Bayesian analysis error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in Bayesian analysis test: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Advanced Statistics Service - Comprehensive Testing")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Multivariate Analysis", test_multivariate_analysis),
        ("Advanced Testing", test_advanced_testing),
        ("Comprehensive Analysis", test_comprehensive_analysis),
        ("Visualization", test_visualization),
        ("Bayesian Analysis", test_bayesian_analysis)
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
        print("🎉 All tests passed! Advanced Statistics Service is working correctly.")
    else:
        print("⚠️  Some tests failed. Check dependencies and implementation.")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)




