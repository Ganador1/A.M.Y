"""Load testing for router registry startup time and performance."""
import time
import statistics
from typing import Dict, List, Any
import pytest
import psutil
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from app.routers.registry import RouterRegistry


class StartupMetrics:
    """Collects metrics for startup time testing."""
    
    def __init__(self):
        self.startup_times: List[float] = []
        self.memory_usage: List[float] = []
        self.cpu_usage: List[float] = []
        self.success_count = 0
        self.error_count = 0
        self.errors: List[str] = []
        self.lock = threading.Lock()
    
    def record_startup(self, startup_time: float, success: bool, error: str = None):
        """Record metrics for a single startup."""
        with self.lock:
            self.startup_times.append(startup_time)
            if success:
                self.success_count += 1
            else:
                self.error_count += 1
                if error:
                    self.errors.append(error)
    
    def record_system_metrics(self):
        """Record current system resource usage."""
        with self.lock:
            process = psutil.Process(os.getpid())
            self.memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
            self.cpu_usage.append(process.cpu_percent())
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the startup tests."""
        if not self.startup_times:
            return {"error": "No startup times recorded"}
        
        return {
            "total_startups": len(self.startup_times),
            "success_count": self.success_count,
            "error_count": self.error_count,
            "success_rate": self.success_count / len(self.startup_times) * 100,
            "startup_stats": {
                "mean": statistics.mean(self.startup_times),
                "median": statistics.median(self.startup_times),
                "p95": self._percentile(self.startup_times, 95),
                "p99": self._percentile(self.startup_times, 99),
                "min": min(self.startup_times),
                "max": max(self.startup_times),
            },
            "memory_stats": {
                "mean_mb": statistics.mean(self.memory_usage) if self.memory_usage else 0,
                "max_mb": max(self.memory_usage) if self.memory_usage else 0,
            },
            "cpu_stats": {
                "mean_percent": statistics.mean(self.cpu_usage) if self.cpu_usage else 0,
                "max_percent": max(self.cpu_usage) if self.cpu_usage else 0,
            },
            "errors": self.errors[:10],  # First 10 errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


def test_router_registry_startup() -> tuple[bool, float, str]:
    """Test router registry startup time."""
    start_time = time.time()
    
    try:
        # Create a new router registry instance
        registry = RouterRegistry()
        
        # Measure startup time
        startup_time = time.time() - start_time
        
        # Verify registry is functional
        assert registry is not None
        assert hasattr(registry, 'get_router')
        assert hasattr(registry, 'list_routers')
        
        return True, startup_time, None
        
    except Exception as e:
        startup_time = time.time() - start_time
        return False, startup_time, str(e)


def test_router_registry_with_imports() -> tuple[bool, float, str]:
    """Test router registry startup time with imports."""
    start_time = time.time()
    
    try:
        # Import router modules to simulate real usage
        from app.routers.system import router as system_router
        from app.routers.friendly import router as friendly_router
        from app.routers.llm_routing import router as llm_router
        
        # Create registry and register routers
        registry = RouterRegistry()
        registry.register_router("system", system_router)
        registry.register_router("friendly", friendly_router)
        registry.register_router("llm_routing", llm_router)
        
        # Measure startup time
        startup_time = time.time() - start_time
        
        # Verify functionality
        assert registry.get_router("system") is not None
        assert registry.get_router("friendly") is not None
        assert registry.get_router("llm_routing") is not None
        assert len(registry.list_routers()) >= 3
        
        return True, startup_time, None
        
    except Exception as e:
        startup_time = time.time() - start_time
        return False, startup_time, str(e)


def test_router_registry_lazy_loading() -> tuple[bool, float, str]:
    """Test router registry lazy loading performance."""
    start_time = time.time()
    
    try:
        # Create registry
        registry = RouterRegistry()
        
        # Register routers without importing them yet
        registry.register_router("system", "app.routers.system:router")
        registry.register_router("friendly", "app.routers.friendly:router")
        registry.register_router("llm_routing", "app.routers.llm_routing:router")
        
        # Measure startup time
        startup_time = time.time() - start_time
        
        # Test lazy loading
        router = registry.get_router("system")
        assert router is not None
        
        return True, startup_time, None
        
    except Exception as e:
        startup_time = time.time() - start_time
        return False, startup_time, str(e)


class TestRouterRegistryStartupTime:
    """Load tests for router registry startup time and performance."""
    
    @pytest.mark.performance
    def test_router_registry_basic_startup(self):
        """Test basic router registry startup time."""
        metrics = StartupMetrics()
        
        # Test parameters
        total_startups = 50
        
        for i in range(total_startups):
            success, startup_time, error = test_router_registry_startup()
            metrics.record_startup(startup_time, success, error)
            metrics.record_system_metrics()
        
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 95.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["startup_stats"]["p95"] <= 0.1, f"P95 startup time too high: {summary['startup_stats']['p95']:.3f}s"
        assert summary["startup_stats"]["max"] <= 0.5, f"Max startup time too high: {summary['startup_stats']['max']:.3f}s"
        assert summary["memory_stats"]["max_mb"] <= 50, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Router Registry Basic Startup Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Mean Startup Time: {summary['startup_stats']['mean']:.3f}s")
        print(f"  P95 Startup Time: {summary['startup_stats']['p95']:.3f}s")
        print(f"  Max Startup Time: {summary['startup_stats']['max']:.3f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    def test_router_registry_with_imports_startup(self):
        """Test router registry startup time with router imports."""
        metrics = StartupMetrics()
        
        # Test parameters
        total_startups = 20  # Fewer tests due to import overhead
        
        for i in range(total_startups):
            success, startup_time, error = test_router_registry_with_imports()
            metrics.record_startup(startup_time, success, error)
            metrics.record_system_metrics()
        
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 90.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["startup_stats"]["p95"] <= 2.0, f"P95 startup time too high: {summary['startup_stats']['p95']:.3f}s"
        assert summary["startup_stats"]["max"] <= 5.0, f"Max startup time too high: {summary['startup_stats']['max']:.3f}s"
        assert summary["memory_stats"]["max_mb"] <= 200, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Router Registry with Imports Startup Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Mean Startup Time: {summary['startup_stats']['mean']:.3f}s")
        print(f"  P95 Startup Time: {summary['startup_stats']['p95']:.3f}s")
        print(f"  Max Startup Time: {summary['startup_stats']['max']:.3f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    def test_router_registry_lazy_loading_startup(self):
        """Test router registry lazy loading startup time."""
        metrics = StartupMetrics()
        
        # Test parameters
        total_startups = 30
        
        for i in range(total_startups):
            success, startup_time, error = test_router_registry_lazy_loading()
            metrics.record_startup(startup_time, success, error)
            metrics.record_system_metrics()
        
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 90.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["startup_stats"]["p95"] <= 0.5, f"P95 startup time too high: {summary['startup_stats']['p95']:.3f}s"
        assert summary["startup_stats"]["max"] <= 1.0, f"Max startup time too high: {summary['startup_stats']['max']:.3f}s"
        assert summary["memory_stats"]["max_mb"] <= 100, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Router Registry Lazy Loading Startup Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Mean Startup Time: {summary['startup_stats']['mean']:.3f}s")
        print(f"  P95 Startup Time: {summary['startup_stats']['p95']:.3f}s")
        print(f"  Max Startup Time: {summary['startup_stats']['max']:.3f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_concurrent_router_registry_startup(self):
        """Test concurrent router registry startup performance."""
        metrics = StartupMetrics()
        
        # Test parameters
        concurrent_startups = 10
        total_startups = 50
        
        with ThreadPoolExecutor(max_workers=concurrent_startups) as executor:
            futures = []
            
            for i in range(total_startups):
                if i % 3 == 0:
                    future = executor.submit(test_router_registry_with_imports)
                elif i % 3 == 1:
                    future = executor.submit(test_router_registry_lazy_loading)
                else:
                    future = executor.submit(test_router_registry_startup)
                futures.append(future)
            
            for future in as_completed(futures):
                success, startup_time, error = future.result()
                metrics.record_startup(startup_time, success, error)
                metrics.record_system_metrics()
        
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 85.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["startup_stats"]["p95"] <= 3.0, f"P95 startup time too high: {summary['startup_stats']['p95']:.3f}s"
        assert summary["memory_stats"]["max_mb"] <= 300, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        print(f"Concurrent Router Registry Startup Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Mean Startup Time: {summary['startup_stats']['mean']:.3f}s")
        print(f"  P95 Startup Time: {summary['startup_stats']['p95']:.3f}s")
        print(f"  Max Startup Time: {summary['startup_stats']['max']:.3f}s")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
    
    @pytest.mark.performance
    def test_router_registry_memory_footprint(self):
        """Test router registry memory footprint under load."""
        metrics = StartupMetrics()
        
        # Test parameters - create many instances to test memory
        total_startups = 100
        
        for i in range(total_startups):
            success, startup_time, error = test_router_registry_startup()
            metrics.record_startup(startup_time, success, error)
            metrics.record_system_metrics()
        
        summary = metrics.get_summary()
        
        # Assertions
        assert summary["success_rate"] >= 95.0, f"Success rate too low: {summary['success_rate']:.1f}%"
        assert summary["memory_stats"]["max_mb"] <= 100, f"Memory usage too high: {summary['memory_stats']['max_mb']:.1f}MB"
        
        # Check for memory leaks (max should not be significantly higher than mean)
        memory_ratio = summary["memory_stats"]["max_mb"] / summary["memory_stats"]["mean_mb"] if summary["memory_stats"]["mean_mb"] > 0 else 1
        assert memory_ratio <= 2.0, f"Potential memory leak detected: max/mean ratio = {memory_ratio:.2f}"
        
        print(f"Router Registry Memory Footprint Test Results:")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Mean Memory: {summary['memory_stats']['mean_mb']:.1f}MB")
        print(f"  Max Memory: {summary['memory_stats']['max_mb']:.1f}MB")
        print(f"  Memory Ratio: {memory_ratio:.2f}")
        print(f"  Mean Startup Time: {summary['startup_stats']['mean']:.3f}s")
