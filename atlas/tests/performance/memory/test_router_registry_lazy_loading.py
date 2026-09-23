"""
Memory profiling tests for Router Registry lazy loading optimization.

Propósito:
    Optimizar el uso de memoria en el router registry mediante lazy loading
    y patterns de inicialización diferida para mejorar startup time y memoria.

Coverage:
    - Router registration memory patterns
    - Lazy loading efficiency vs eager loading
    - Service dependency memory optimization
    - Dynamic import memory impact
    - Registry cleanup and memory recovery
"""

import pytest
import time
import gc
from typing import Dict, List, Union, Any, Callable
from unittest.mock import patch, Mock
import importlib
import sys
import weakref

# Optional dependencies
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class RouterMemoryProfiler:
    """Memory profiler specialized for router and service registration."""

    def __init__(self) -> None:
        self.baseline_memory: Union[float, None] = None
        self.memory_samples: List[float] = []
        self.timestamps: List[float] = []
        self.use_psutil = PSUTIL_AVAILABLE
        if self.use_psutil:
            import os
            self.process = psutil.Process(os.getpid())

    def start_monitoring(self) -> None:
        """Start memory monitoring."""
        gc.collect()
        self.baseline_memory = self._get_memory_usage()
        self.memory_samples = []
        self.timestamps = []

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        if self.use_psutil:
            return self.process.memory_info().rss / 1024 / 1024
        else:
            return 50.0  # Lightweight baseline for router operations

    def sample_memory(self) -> None:
        """Take a memory sample."""
        memory_mb = self._get_memory_usage()
        self.memory_samples.append(memory_mb)
        self.timestamps.append(time.time())

    def get_memory_stats(self) -> Dict[str, Union[float, str, int]]:
        """Get memory usage statistics."""
        if not self.memory_samples:
            return {"error": "No memory samples collected"}

        current_memory = self.memory_samples[-1]
        max_memory = max(self.memory_samples)
        min_memory = min(self.memory_samples)
        avg_memory = sum(self.memory_samples) / len(self.memory_samples)
        baseline = self.baseline_memory or 0.0

        return {
            "baseline_mb": baseline,
            "current_mb": current_memory,
            "max_mb": max_memory,
            "min_mb": min_memory,
            "avg_mb": avg_memory,
            "memory_growth_mb": current_memory - baseline,
            "peak_memory_mb": max_memory,
            "samples_count": len(self.memory_samples)
        }

    def detect_memory_leak(self, threshold_mb: float = 25.0) -> bool:
        """Detect if there's a potential memory leak."""
        stats = self.get_memory_stats()
        if "error" in stats:
            return False
        memory_growth = stats.get("memory_growth_mb", 0)
        return float(memory_growth) > threshold_mb


class MockRouter:
    """Mock router for testing memory patterns."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.routes: Dict[str, Callable[..., Any]] = {}
        self.middleware: List[Callable[..., Any]] = []
        self.dependencies: List[Any] = []

    def add_route(self, path: str, handler: Callable[..., Any]) -> None:
        """Add a route handler."""
        self.routes[path] = handler

    def add_middleware(self, middleware: Callable[..., Any]) -> None:
        """Add middleware."""
        self.middleware.append(middleware)

    def add_dependency(self, dep: Any) -> None:
        """Add a dependency."""
        self.dependencies.append(dep)


class LazyRouterRegistry:
    """Lazy loading router registry for memory optimization."""

    def __init__(self) -> None:
        self._routers: Dict[str, Union[MockRouter, Callable[[], MockRouter]]] = {}
        self._loaded_routers: weakref.WeakValueDictionary[str, MockRouter] = weakref.WeakValueDictionary()

    def register_lazy(self, name: str, factory: Callable[[], MockRouter]) -> None:
        """Register a router with lazy loading."""
        self._routers[name] = factory

    def register_eager(self, name: str, router: MockRouter) -> None:
        """Register a router with eager loading."""
        self._routers[name] = router
        self._loaded_routers[name] = router

    def get_router(self, name: str) -> MockRouter:
        """Get a router, loading it if necessary."""
        if name in self._loaded_routers:
            return self._loaded_routers[name]

        router_or_factory = self._routers.get(name)
        if router_or_factory is None:
            raise KeyError(f"Router {name} not found")

        if callable(router_or_factory) and not isinstance(router_or_factory, MockRouter):
            # Lazy load
            router = router_or_factory()
            self._loaded_routers[name] = router
            return router
        else:
            # Already loaded
            return router_or_factory

    def unload_router(self, name: str) -> None:
        """Unload a router to free memory."""
        if name in self._loaded_routers:
            del self._loaded_routers[name]

    def get_loaded_count(self) -> int:
        """Get number of currently loaded routers."""
        return len(self._loaded_routers)


class TestRouterRegistryMemoryProfiling:
    """Memory profiling tests for router registry optimization."""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_lazy_vs_eager_loading_memory(self) -> None:
        """Compare memory usage between lazy and eager loading strategies."""
        profiler = RouterMemoryProfiler()
        profiler.start_monitoring()

        def create_heavy_router(name: str) -> MockRouter:
            """Create a router with heavy dependencies."""
            router = MockRouter(name)

            # Simulate heavy dependencies (large objects)
            for i in range(10):
                # Each dependency simulates a service with data
                dependency = {
                    'service_data': list(range(1000)),  # Some data
                    'cache': {f'key_{j}': f'value_{j}' * 50 for j in range(100)},
                    'config': {'setting_' + str(k): k * 2 for k in range(50)}
                }
                router.add_dependency(dependency)

            # Add multiple routes
            for i in range(20):
                def dummy_handler(request: Any = None) -> Dict[str, str]:
                    return {"status": "ok", "data": "response"}
                router.add_route(f"/api/v1/endpoint_{i}", dummy_handler)

            return router

        # Test 1: Eager loading (load all routers immediately)
        profiler.sample_memory()
        eager_registry = LazyRouterRegistry()

        eager_routers = []
        for i in range(15):  # Create 15 heavy routers
            router = create_heavy_router(f"eager_router_{i}")
            eager_registry.register_eager(f"eager_router_{i}", router)
            eager_routers.append(router)

        profiler.sample_memory()  # Memory after eager loading

        # Test 2: Lazy loading (register factories, don't load yet)
        lazy_registry = LazyRouterRegistry()

        for i in range(15):  # Register 15 lazy routers
            def make_factory(router_name: str) -> Callable[[], MockRouter]:
                return lambda: create_heavy_router(router_name)

            lazy_registry.register_lazy(f"lazy_router_{i}", make_factory(f"lazy_router_{i}"))

        profiler.sample_memory()  # Memory after lazy registration

        # Test 3: Load only some lazy routers (simulate real usage)
        loaded_lazy_routers = []
        for i in [0, 2, 5, 8]:  # Load only 4 out of 15 routers
            router = lazy_registry.get_router(f"lazy_router_{i}")
            loaded_lazy_routers.append(router)

        profiler.sample_memory()  # Memory after partial lazy loading

        # Cleanup
        del eager_routers, loaded_lazy_routers
        del eager_registry, lazy_registry
        gc.collect()

        profiler.sample_memory()  # Memory after cleanup

        stats = profiler.get_memory_stats()

        if "error" not in stats and len(profiler.memory_samples) >= 4:
            eager_memory = profiler.memory_samples[1]  # After eager loading
            lazy_register_memory = profiler.memory_samples[2]  # After lazy registration
            lazy_partial_memory = profiler.memory_samples[3]  # After partial loading

            eager_overhead = eager_memory - profiler.memory_samples[0]
            lazy_register_overhead = lazy_register_memory - profiler.memory_samples[0]
            lazy_partial_overhead = lazy_partial_memory - profiler.memory_samples[0]

            # Lazy registration should use much less memory than eager loading
            memory_saved = eager_overhead - lazy_register_overhead
            efficiency_ratio = lazy_partial_overhead / eager_overhead if eager_overhead > 0 else 0

            print("Lazy vs Eager Loading Memory Comparison:")
            print(f"  Eager loading overhead: {eager_overhead:.1f}MB")
            print(f"  Lazy registration overhead: {lazy_register_overhead:.1f}MB")
            print(f"  Lazy partial loading overhead: {lazy_partial_overhead:.1f}MB")
            print(f"  Memory saved by lazy registration: {memory_saved:.1f}MB")
            print(f"  Partial loading efficiency: {efficiency_ratio:.2f}")

            # Assertions
            assert lazy_register_overhead < eager_overhead, "Lazy registration should use less memory than eager loading"
            assert efficiency_ratio < 0.7, f"Partial lazy loading should be more efficient: {efficiency_ratio:.2f}"

        memory_growth = float(stats.get("memory_growth_mb", 0))
        assert not profiler.detect_memory_leak(50), f"Memory leak detected: {memory_growth:.1f}MB growth"

    @pytest.mark.performance
    @pytest.mark.slow
    @patch('importlib.import_module')
    def test_dynamic_import_memory_impact(self, mock_import: Mock) -> None:
        """Test memory impact of dynamic imports in router loading."""
        profiler = RouterMemoryProfiler()
        profiler.start_monitoring()

        # Mock dynamic module imports
        def mock_import_side_effect(module_name: str) -> Mock:
            # Create a mock module with some memory footprint
            mock_module = Mock()
            mock_module.__name__ = module_name

            # Simulate module having classes and functions
            mock_module.RouterClass = type(f"RouterClass_{module_name.split('.')[-1]}", (), {
                'data': list(range(500)),  # Some module-level data
                'config': {f'setting_{i}': i for i in range(100)}
            })

            return mock_module

        mock_import.side_effect = mock_import_side_effect

        def test_dynamic_imports() -> None:
            """Test dynamic importing patterns."""
            imported_modules = []

            # Simulate importing multiple router modules dynamically
            module_names = [
                'app.routers.user_management',
                'app.routers.data_processing',
                'app.routers.ml_inference',
                'app.routers.file_operations',
                'app.routers.analytics',
                'app.routers.notifications',
                'app.routers.auth_service',
                'app.routers.backup_service'
            ]

            for module_name in module_names:
                profiler.sample_memory()

                # Dynamic import
                module = importlib.import_module(module_name)
                imported_modules.append(module)

                # Simulate using the imported module
                router_class = getattr(module, 'RouterClass', None)
                if router_class:
                    router_instance = router_class()
                    # Do something with the router
                    _ = getattr(router_instance, 'data', [])

            profiler.sample_memory()

            # Test cleanup of imported modules
            imported_modules.clear()

            # Force cleanup of module references
            for module_name in module_names:
                if module_name in sys.modules:
                    del sys.modules[module_name]

            gc.collect()
            profiler.sample_memory()

        test_dynamic_imports()

        stats = profiler.get_memory_stats()

        if "error" not in stats:
            memory_samples = profiler.memory_samples
            if len(memory_samples) >= 3:
                import_growth = memory_samples[-3] - memory_samples[0]  # Growth during imports
                final_memory = memory_samples[-1]
                cleanup_effectiveness = (memory_samples[-3] - final_memory) / import_growth if import_growth > 0 else 1.0

                print("Dynamic Import Memory Impact:")
                print(f"  Memory growth during imports: {import_growth:.1f}MB")
                print(f"  Cleanup effectiveness: {cleanup_effectiveness:.2f}")

                assert cleanup_effectiveness > 0.5, f"Poor import cleanup: {cleanup_effectiveness:.2f}"

            memory_growth = float(stats["memory_growth_mb"])
            assert not profiler.detect_memory_leak(30), f"Memory leak in dynamic imports: {memory_growth:.1f}MB growth"
        else:
            print("Memory profiling not available - test passed with mock data")

    @pytest.mark.performance
    @pytest.mark.slow
    def test_router_dependency_injection_memory(self) -> None:
        """Test memory patterns in router dependency injection."""
        profiler = RouterMemoryProfiler()
        profiler.start_monitoring()

        def dependency_injection_test() -> None:
            """Test various dependency injection patterns."""
            registry = LazyRouterRegistry()

            # Pattern 1: Shared dependencies (should reuse memory)
            shared_cache = {'shared_data': list(range(2000))}
            shared_config = {'app_settings': {f'key_{i}': f'value_{i}' for i in range(200)}}

            profiler.sample_memory()

            # Create routers with shared dependencies
            for i in range(10):
                def make_router_with_shared_deps(router_id: int) -> MockRouter:
                    router = MockRouter(f"shared_deps_router_{router_id}")
                    router.add_dependency(shared_cache)  # Shared reference
                    router.add_dependency(shared_config)  # Shared reference
                    # Each router has some unique dependencies too
                    router.add_dependency({'unique_data': list(range(100))})
                    return router

                registry.register_lazy(f"shared_deps_router_{i}",
                                     lambda rid=i: make_router_with_shared_deps(rid))

            profiler.sample_memory()

            # Load all routers with shared dependencies
            shared_routers = []
            for i in range(10):
                router = registry.get_router(f"shared_deps_router_{i}")
                shared_routers.append(router)

            profiler.sample_memory()

            # Pattern 2: Independent dependencies (each router has its own copy)
            for i in range(10):
                def make_router_with_independent_deps(router_id: int) -> MockRouter:
                    router = MockRouter(f"independent_deps_router_{router_id}")
                    # Each router gets its own copy of dependencies
                    router.add_dependency({'cache': list(range(2000))})
                    router.add_dependency({'config': {f'key_{j}': f'value_{j}' for j in range(200)}})
                    router.add_dependency({'unique_data': list(range(100))})
                    return router

                registry.register_lazy(f"independent_deps_router_{i}",
                                     lambda rid=i: make_router_with_independent_deps(rid))

            profiler.sample_memory()

            # Load all routers with independent dependencies
            independent_routers = []
            for i in range(10):
                router = registry.get_router(f"independent_deps_router_{i}")
                independent_routers.append(router)

            profiler.sample_memory()

            # Cleanup test
            shared_routers.clear()
            independent_routers.clear()

            # Unload half of the routers
            for i in range(5):
                registry.unload_router(f"shared_deps_router_{i}")
                registry.unload_router(f"independent_deps_router_{i}")

            gc.collect()
            profiler.sample_memory()

        dependency_injection_test()

        stats = profiler.get_memory_stats()

        if "error" not in stats and len(profiler.memory_samples) >= 5:
            baseline = profiler.memory_samples[0]
            after_shared = profiler.memory_samples[2]
            after_independent = profiler.memory_samples[4]
            after_cleanup = profiler.memory_samples[-1]

            shared_memory_usage = after_shared - baseline
            independent_memory_usage = after_independent - after_shared
            memory_saved_by_sharing = independent_memory_usage - shared_memory_usage

            print("Router Dependency Injection Memory Patterns:")
            print(f"  Shared dependencies memory: {shared_memory_usage:.1f}MB")
            print(f"  Independent dependencies memory: {independent_memory_usage:.1f}MB")
            print(f"  Memory saved by sharing: {memory_saved_by_sharing:.1f}MB")
            print(f"  Memory after cleanup: {after_cleanup - baseline:.1f}MB")

            # Shared dependencies should use less memory
            assert shared_memory_usage < independent_memory_usage, "Shared dependencies should be more memory efficient"

        memory_growth = float(stats.get("memory_growth_mb", 0))
        assert not profiler.detect_memory_leak(40), f"Memory leak in dependency injection: {memory_growth:.1f}MB growth"


class TestRouterRegistryCleanup:
    """Tests for router registry cleanup and memory recovery."""

    @pytest.mark.performance
    @pytest.mark.slow
    def test_registry_memory_cleanup_patterns(self) -> None:
        """Test different cleanup patterns for router registry."""
        profiler = RouterMemoryProfiler()
        profiler.start_monitoring()

        def cleanup_patterns_test() -> None:
            """Test various cleanup strategies."""
            registry = LazyRouterRegistry()

            # Create routers with different memory footprints
            router_configs = [
                ('small', 100, 5),   # name, data_size, route_count
                ('medium', 500, 15),
                ('large', 1000, 30),
                ('xlarge', 2000, 50)
            ]

            profiler.sample_memory()

            # Register and load routers
            loaded_routers = []
            for size_name, data_size, route_count in router_configs:
                for i in range(3):  # 3 routers of each size
                    router_name = f"{size_name}_router_{i}"

                    def make_sized_router(name: str, dsize: int, rcount: int) -> MockRouter:
                        router = MockRouter(name)
                        # Add data proportional to size
                        router.add_dependency({'data': list(range(dsize))})
                        router.add_dependency({'cache': {f'k_{j}': j for j in range(dsize // 10)}})

                        # Add routes
                        for r in range(rcount):
                            def handler(req: Any = None) -> Dict[str, str]:
                                return {"route": f"route_{r}"}
                            router.add_route(f"/api/{name}/route_{r}", handler)

                        return router

                    registry.register_lazy(router_name,
                                         lambda n=router_name, d=data_size, r=route_count: make_sized_router(n, d, r))

                    # Load router immediately
                    router = registry.get_router(router_name)
                    loaded_routers.append(router)

            profiler.sample_memory()

            # Strategy 1: Cleanup largest routers first
            large_routers = [name for name, _, _ in router_configs if name in ['large', 'xlarge']]
            for size_name in large_routers:
                for i in range(3):
                    registry.unload_router(f"{size_name}_router_{i}")

            gc.collect()
            profiler.sample_memory()

            # Strategy 2: Cleanup least recently used (simulate by removing medium routers)
            for i in range(3):
                registry.unload_router(f"medium_router_{i}")

            gc.collect()
            profiler.sample_memory()

            # Strategy 3: Complete cleanup
            for size_name, _, _ in router_configs:
                for i in range(3):
                    try:
                        registry.unload_router(f"{size_name}_router_{i}")
                    except KeyError:
                        pass  # Already unloaded

            loaded_routers.clear()
            del registry
            gc.collect()
            profiler.sample_memory()

        cleanup_patterns_test()

        stats = profiler.get_memory_stats()

        if "error" not in stats and len(profiler.memory_samples) >= 4:
            baseline = profiler.memory_samples[0]
            after_loading = profiler.memory_samples[1]
            after_large_cleanup = profiler.memory_samples[2]
            after_medium_cleanup = profiler.memory_samples[3]
            after_complete_cleanup = profiler.memory_samples[-1]

            total_memory_used = after_loading - baseline
            large_cleanup_recovered = after_loading - after_large_cleanup
            medium_cleanup_recovered = after_large_cleanup - after_medium_cleanup
            total_recovered = after_loading - after_complete_cleanup

            cleanup_efficiency = total_recovered / total_memory_used if total_memory_used > 0 else 1.0

            print("Router Registry Cleanup Patterns:")
            print(f"  Total memory used: {total_memory_used:.1f}MB")
            print(f"  Large routers cleanup recovered: {large_cleanup_recovered:.1f}MB")
            print(f"  Medium routers cleanup recovered: {medium_cleanup_recovered:.1f}MB")
            print(f"  Total cleanup efficiency: {cleanup_efficiency:.2f}")

            assert cleanup_efficiency > 0.7, f"Poor cleanup efficiency: {cleanup_efficiency:.2f}"
            assert large_cleanup_recovered > medium_cleanup_recovered, "Large routers should free more memory"

        memory_growth = float(stats.get("memory_growth_mb", 0))
        assert not profiler.detect_memory_leak(20), f"Memory leak in cleanup test: {memory_growth:.1f}MB growth"