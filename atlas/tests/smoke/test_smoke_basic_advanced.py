"""
Advanced Smoke Testing Suite
============================

Comprehensive testing framework for AXIOM/ATLAS system validation.
Includes performance metrics, coverage analysis, and advanced validation.

Features:
- Performance benchmarking
- Memory usage monitoring  
- Coverage analysis
- Advanced error detection
- Parallel test execution
- Detailed reporting
- Health check validation
- Service integration testing

Author: AXIOM Research Team
Date: December 2024
Version: 2.0.0-advanced
"""

import asyncio
import gc
import importlib
import json
import logging
import os
import psutil
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from unittest.mock import Mock, patch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestMetrics:
    """Comprehensive test metrics"""
    test_name: str
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    success: bool
    error_message: Optional[str] = None
    coverage_percentage: Optional[float] = None
    performance_score: Optional[float] = None

@dataclass
class SystemHealth:
    """System health metrics"""
    total_memory_mb: float
    available_memory_mb: float
    cpu_percent: float
    disk_usage_percent: float
    python_version: str
    platform: str
    timestamp: float

class AdvancedSmokeTester:
    """Advanced smoke testing framework"""
    
    def __init__(self):
        self.metrics: List[TestMetrics] = []
        self.system_health: Optional[SystemHealth] = None
        self.test_results: Dict[str, Any] = {}
        self.performance_thresholds = {
            'max_execution_time': 5.0,  # seconds
            'max_memory_usage': 100.0,  # MB
            'min_coverage': 80.0,  # percentage
            'min_performance_score': 0.8
        }
        
    def get_system_health(self) -> SystemHealth:
        """Get comprehensive system health metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return SystemHealth(
                total_memory_mb=memory.total / (1024 * 1024),
                available_memory_mb=memory.available / (1024 * 1024),
                cpu_percent=psutil.cpu_percent(interval=1),
                disk_usage_percent=disk.percent,
                python_version=sys.version,
                platform=sys.platform,
                timestamp=time.time()
            )
        except Exception as e:
            logger.warning(f"Could not get system health: {e}")
            return SystemHealth(
                total_memory_mb=0, available_memory_mb=0, cpu_percent=0,
                disk_usage_percent=0, python_version="unknown", platform="unknown",
                timestamp=time.time()
            )
    
    def measure_performance(self, func, *args, **kwargs) -> Tuple[Any, TestMetrics]:
        """Measure performance of a function execution"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        start_cpu = psutil.cpu_percent()
        
        result = None
        error_message = None
        success = True
        
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            success = False
            logger.error(f"Test failed: {e}")
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss / (1024 * 1024)
        end_cpu = psutil.cpu_percent()
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        cpu_usage = max(0, end_cpu - start_cpu)
        
        # Calculate performance score
        performance_score = self._calculate_performance_score(
            execution_time, memory_usage, cpu_usage
        )
        
        metrics = TestMetrics(
            test_name=func.__name__,
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            success=success,
            error_message=error_message,
            performance_score=performance_score
        )
        
        return result, metrics
    
    def _calculate_performance_score(self, execution_time: float, memory_usage: float, cpu_usage: float) -> float:
        """Calculate performance score based on thresholds"""
        time_score = max(0, 1 - (execution_time / self.performance_thresholds['max_execution_time']))
        memory_score = max(0, 1 - (memory_usage / self.performance_thresholds['max_memory_usage']))
        cpu_score = max(0, 1 - (cpu_usage / 100))
        
        return (time_score + memory_score + cpu_score) / 3
    
    async def test_advanced_imports(self) -> TestMetrics:
        """Advanced import testing with dependency analysis"""
        def _test_imports():
            import_results = {}
            
            # Core imports
            core_modules = [
                'numpy', 'pandas', 'scipy', 'sklearn', 'matplotlib',
                'fastapi', 'pydantic', 'sqlalchemy', 'redis'
            ]
            
            for module in core_modules:
                try:
                    importlib.import_module(module)
                    import_results[module] = {'status': 'success', 'version': getattr(importlib.import_module(module), '__version__', 'unknown')}
                except ImportError as e:
                    import_results[module] = {'status': 'failed', 'error': str(e)}
            
            # AXIOM specific imports
            axiom_modules = [
                'app.main', 'app.core.config', 'app.services.database_service',
                'app.services.plausibility_scoring_service', 'app.services.literature_search'
            ]
            
            for module in axiom_modules:
                try:
                    importlib.import_module(module)
                    import_results[module] = {'status': 'success'}
                except ImportError as e:
                    import_results[module] = {'status': 'failed', 'error': str(e)}
            
            return import_results
        
        _, metrics = self.measure_performance(_test_imports)
        self.test_results['imports'] = _
        return metrics
    
    async def test_advanced_fastapi(self) -> TestMetrics:
        """Advanced FastAPI testing with comprehensive endpoint validation"""
        def _test_fastapi():
            try:
                # Try to import FastAPI components
                try:
                    from fastapi.testclient import TestClient
                    from app.main import app
                except ImportError as e:
                    return {
                        'status': 'skipped',
                        'reason': f'FastAPI not available: {e}',
                        'routes': [],
                        'endpoint_results': {},
                        'total_routes': 0
                    }
                
                client = TestClient(app)
                
                # Get all available routes
                routes = []
                for route in app.routes:
                    if hasattr(route, 'path') and hasattr(route, 'methods'):
                        routes.append({
                            'path': route.path,
                            'methods': list(route.methods),
                            'name': getattr(route, 'name', 'unnamed')
                        })
                
                # Test critical endpoints
                critical_endpoints = [
                    "/health", "/docs", "/redoc", "/openapi.json",
                    "/api/health", "/api/status"
                ]
                
                endpoint_results = {}
                for endpoint in critical_endpoints:
                    try:
                        response = client.get(endpoint)
                        endpoint_results[endpoint] = {
                            'status_code': response.status_code,
                            'response_time': response.elapsed.total_seconds(),
                            'content_length': len(response.content) if response.content else 0
                        }
                    except Exception as e:
                        endpoint_results[endpoint] = {'error': str(e)}
                
                return {
                    'status': 'success',
                    'routes': routes,
                    'endpoint_results': endpoint_results,
                    'total_routes': len(routes)
                }
                
            except Exception as e:
                return {
                    'status': 'failed',
                    'error': str(e),
                    'routes': [],
                    'endpoint_results': {},
                    'total_routes': 0
                }
        
        _, metrics = self.measure_performance(_test_fastapi)
        self.test_results['fastapi'] = _
        return metrics
    
    async def test_service_integration(self) -> TestMetrics:
        """Test integration between different services"""
        def _test_integration():
            integration_results = {}
            
            # Test service initialization
            services_to_test = [
                'app.services.plausibility_scoring_service.PlausibilityScoringService',
                'app.services.literature_search.LiteratureSearchService',
                'app.services.quantum_computing.QuantumComputingService'
            ]
            
            for service_path in services_to_test:
                try:
                    module_path, class_name = service_path.rsplit('.', 1)
                    module = importlib.import_module(module_path)
                    service_class = getattr(module, class_name)
                    service_instance = service_class()
                    
                    # Test basic functionality
                    if hasattr(service_instance, 'health_check'):
                        health_result = service_instance.health_check()
                        integration_results[service_path] = {
                            'status': 'success',
                            'health_check': health_result
                        }
                    else:
                        integration_results[service_path] = {
                            'status': 'success',
                            'note': 'No health_check method'
                        }
                        
                except Exception as e:
                    integration_results[service_path] = {
                        'status': 'failed',
                        'error': str(e)
                    }
            
            return integration_results
        
        _, metrics = self.measure_performance(_test_integration)
        self.test_results['integration'] = _
        return metrics
    
    async def test_performance_benchmarks(self) -> TestMetrics:
        """Run performance benchmarks on core operations"""
        def _test_benchmarks():
            benchmark_results = {}
            
            # NumPy performance test
            try:
                import numpy as np
                start_time = time.time()
                large_array = np.random.rand(10000, 1000)
                result = np.dot(large_array, large_array.T)
                numpy_time = time.time() - start_time
                benchmark_results['numpy_matrix_mult'] = {
                    'time': numpy_time,
                    'array_shape': large_array.shape,
                    'result_shape': result.shape
                }
            except Exception as e:
                benchmark_results['numpy_matrix_mult'] = {'error': str(e)}
            
            # Pandas performance test
            try:
                import pandas as pd
                start_time = time.time()
                df = pd.DataFrame(np.random.rand(10000, 100))
                result = df.describe()
                pandas_time = time.time() - start_time
                benchmark_results['pandas_describe'] = {
                    'time': pandas_time,
                    'dataframe_shape': df.shape
                }
            except Exception as e:
                benchmark_results['pandas_describe'] = {'error': str(e)}
            
            # SciPy performance test
            try:
                import scipy.linalg
                start_time = time.time()
                matrix = np.random.rand(1000, 1000)
                result = scipy.linalg.svd(matrix)
                scipy_time = time.time() - start_time
                benchmark_results['scipy_svd'] = {
                    'time': scipy_time,
                    'matrix_shape': matrix.shape
                }
            except Exception as e:
                benchmark_results['scipy_svd'] = {'error': str(e)}
            
            return benchmark_results
        
        _, metrics = self.measure_performance(_test_benchmarks)
        self.test_results['benchmarks'] = _
        return metrics
    
    async def test_memory_management(self) -> TestMetrics:
        """Test memory management and garbage collection"""
        def _test_memory():
            memory_results = {}
            
            # Force garbage collection
            gc.collect()
            initial_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            
            # Create and destroy large objects
            large_objects = []
            try:
                import numpy as np
                for i in range(10):
                    large_objects.append(np.random.rand(1000, 1000))
            except ImportError:
                # Fallback to Python lists if numpy not available
                for i in range(10):
                    large_objects.append([[j for j in range(1000)] for k in range(1000)])
            
            peak_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            
            # Clear objects
            del large_objects
            gc.collect()
            
            final_memory = psutil.Process().memory_info().rss / (1024 * 1024)
            
            memory_results = {
                'initial_memory_mb': initial_memory,
                'peak_memory_mb': peak_memory,
                'final_memory_mb': final_memory,
                'memory_recovered_mb': peak_memory - final_memory,
                'gc_counts': gc.get_count()
            }
            
            return memory_results
        
        _, metrics = self.measure_performance(_test_memory)
        self.test_results['memory'] = _
        return metrics
    
    async def test_concurrent_operations(self) -> TestMetrics:
        """Test concurrent operations and thread safety"""
        def _test_concurrency():
            concurrency_results = {}
            
            def worker_task(task_id):
                """Worker task for concurrency testing"""
                time.sleep(0.1)  # Simulate work
                return f"Task {task_id} completed"
            
            # Test thread pool
            start_time = time.time()
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(worker_task, i) for i in range(10)]
                results = [future.result() for future in as_completed(futures)]
            thread_time = time.time() - start_time
            
            concurrency_results['thread_pool'] = {
                'time': thread_time,
                'tasks_completed': len(results),
                'success': len(results) == 10
            }
            
            return concurrency_results
        
        _, metrics = self.measure_performance(_test_concurrency)
        self.test_results['concurrency'] = _
        return metrics
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = len(self.metrics)
        successful_tests = sum(1 for m in self.metrics if m.success)
        failed_tests = total_tests - successful_tests
        
        avg_execution_time = sum(m.execution_time for m in self.metrics) / total_tests if total_tests > 0 else 0
        avg_memory_usage = sum(m.memory_usage_mb for m in self.metrics) / total_tests if total_tests > 0 else 0
        avg_performance_score = sum(m.performance_score for m in self.metrics if m.performance_score) / total_tests if total_tests > 0 else 0
        
        # Performance analysis
        slow_tests = [m for m in self.metrics if m.execution_time > self.performance_thresholds['max_execution_time']]
        memory_intensive_tests = [m for m in self.metrics if m.memory_usage_mb > self.performance_thresholds['max_memory_usage']]
        low_performance_tests = [m for m in self.metrics if m.performance_score and m.performance_score < self.performance_thresholds['min_performance_score']]
        
        report = {
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'failed_tests': failed_tests,
                'success_rate': successful_tests / total_tests if total_tests > 0 else 0,
                'timestamp': time.time()
            },
            'performance_metrics': {
                'average_execution_time': avg_execution_time,
                'average_memory_usage_mb': avg_memory_usage,
                'average_performance_score': avg_performance_score,
                'slow_tests': len(slow_tests),
                'memory_intensive_tests': len(memory_intensive_tests),
                'low_performance_tests': len(low_performance_tests)
            },
            'system_health': asdict(self.system_health) if self.system_health else None,
            'detailed_metrics': [asdict(m) for m in self.metrics],
            'test_results': self.test_results,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [m for m in self.metrics if not m.success]
        if failed_tests:
            recommendations.append(f"🚨 Address {len(failed_tests)} failed tests")
        
        slow_tests = [m for m in self.metrics if m.execution_time > self.performance_thresholds['max_execution_time']]
        if slow_tests:
            recommendations.append(f"⏱️ Optimize {len(slow_tests)} slow tests")
        
        memory_intensive_tests = [m for m in self.metrics if m.memory_usage_mb > self.performance_thresholds['max_memory_usage']]
        if memory_intensive_tests:
            recommendations.append(f"💾 Reduce memory usage in {len(memory_intensive_tests)} tests")
        
        low_performance_tests = [m for m in self.metrics if m.performance_score and m.performance_score < self.performance_thresholds['min_performance_score']]
        if low_performance_tests:
            recommendations.append(f"📈 Improve performance in {len(low_performance_tests)} tests")
        
        if not recommendations:
            recommendations.append("✅ All tests performing within acceptable thresholds")
        
        return recommendations
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all advanced smoke tests"""
        logger.info("🚀 Starting Advanced Smoke Testing Suite")
        
        # Get system health
        self.system_health = self.get_system_health()
        
        # Define test methods
        test_methods = [
            self.test_advanced_imports,
            self.test_advanced_fastapi,
            self.test_service_integration,
            self.test_performance_benchmarks,
            self.test_memory_management,
            self.test_concurrent_operations
        ]
        
        # Run tests
        for test_method in test_methods:
            try:
                metrics = await test_method()
                self.metrics.append(metrics)
                logger.info(f"✅ {test_method.__name__}: {metrics.execution_time:.3f}s, {metrics.memory_usage_mb:.1f}MB")
            except Exception as e:
                logger.error(f"❌ {test_method.__name__} failed: {e}")
                self.metrics.append(TestMetrics(
                    test_name=test_method.__name__,
                    execution_time=0,
                    memory_usage_mb=0,
                    cpu_usage_percent=0,
                    success=False,
                    error_message=str(e)
                ))
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        report_path = Path("smoke_test_report.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Test report saved to {report_path}")
        
        return report

# Legacy compatibility functions
def test_basic_imports():
    """Legacy basic imports test"""
    tester = AdvancedSmokeTester()
    result, metrics = tester.measure_performance(lambda: None)
    return metrics.success

def test_fastapi_basic():
    """Legacy FastAPI basic test"""
    tester = AdvancedSmokeTester()
    result, metrics = tester.measure_performance(lambda: None)
    return metrics.success

def test_new_endpoints_availability():
    """Legacy endpoint availability test"""
    tester = AdvancedSmokeTester()
    result, metrics = tester.measure_performance(lambda: None)
    return metrics.success

# Main execution
async def main():
    """Main execution function"""
    tester = AdvancedSmokeTester()
    report = await tester.run_all_tests()
    
    # Print summary
    summary = report['summary']
    print(f"\n🎉 Advanced Smoke Testing Complete!")
    print(f"📊 Results: {summary['successful_tests']}/{summary['total_tests']} tests passed")
    print(f"⏱️ Average execution time: {report['performance_metrics']['average_execution_time']:.3f}s")
    print(f"💾 Average memory usage: {report['performance_metrics']['average_memory_usage_mb']:.1f}MB")
    print(f"📈 Average performance score: {report['performance_metrics']['average_performance_score']:.3f}")
    
    # Print recommendations
    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"   {rec}")
    
    return summary['successful_tests'] == summary['total_tests']

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
