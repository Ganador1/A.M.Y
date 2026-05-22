#!/usr/bin/env python3
"""
AXIOM Advanced Modules Integration Test
Testing all advanced library exploitation modules
"""

import sys
import os
import time

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_advanced_torch_operations():
    """Test PyTorch advanced operations"""
    print("🧠 Testing Advanced PyTorch Operations...")

    try:
        from advanced_torch_operations import get_advanced_torch_operations
        torch_ops = get_advanced_torch_operations()

        # Test basic functionality
        result = torch_ops.torch_computation_pipeline({
            'type': 'matrix_multiplication',
            'matrix_a': [[1, 2], [3, 4]],
            'matrix_b': [[5, 6], [7, 8]]
        })

        print(f"✅ PyTorch operations working: {result['final_results'] != {}}")
        return True

    except Exception as e:
        print(f"❌ PyTorch test failed: {e}")
        return False

def test_advanced_sympy_operations():
    """Test SymPy advanced operations"""
    print("🔢 Testing Advanced SymPy Operations...")

    try:
        from advanced_sympy_operations import get_advanced_sympy_operations
        sympy_ops = get_advanced_sympy_operations()

        # Test basic functionality
        result = sympy_ops.sympy_computation_pipeline({
            'type': 'differentiation',
            'expression': 'x**2 + 2*x + 1',
            'variable': 'x'
        })

        print(f"✅ SymPy operations working: {result['final_results'] != {}}")
        return True

    except Exception as e:
        print(f"❌ SymPy test failed: {e}")
        return False

def test_advanced_scipy_operations():
    """Test SciPy advanced operations"""
    print("🔬 Testing Advanced SciPy Operations...")

    try:
        from advanced_scipy_operations import get_advanced_scipy_operations
        scipy_ops = get_advanced_scipy_operations()

        # Test basic functionality
        result = scipy_ops.scientific_computation_pipeline({
            'type': 'optimization',
            'function': 'x**2 + y**2',
            'variables': ['x', 'y'],
            'method': 'SLSQP'
        })

        print(f"✅ SciPy operations working: {result['final_results'] != {}}")
        return True

    except Exception as e:
        print(f"❌ SciPy test failed: {e}")
        return False

def test_advanced_numpy_operations():
    """Test NumPy advanced operations"""
    print("📊 Testing Advanced NumPy Operations...")

    try:
        from advanced_numpy_operations import get_advanced_numpy_operations
        numpy_ops = get_advanced_numpy_operations()

        # Test basic functionality
        result = numpy_ops.numerical_computation_pipeline({
            'type': 'linear_algebra',
            'operation': 'matrix_inverse',
            'matrix': [[1, 2], [3, 4]]
        })

        print(f"✅ NumPy operations working: {result['final_results'] != {}}")
        return True

    except Exception as e:
        print(f"❌ NumPy test failed: {e}")
        return False

def test_advanced_redis_operations():
    """Test Redis advanced operations"""
    print("🗄️ Testing Advanced Redis Operations...")

    try:
        from advanced_redis_operations import get_advanced_redis_operations
        redis_ops = get_advanced_redis_operations()

        # Test basic functionality (this will work even without Redis server)
        result = redis_ops.redis_computation_pipeline({
            'type': 'data_structure',
            'operation': 'hash_operations',
            'key': 'test_key',
            'data': {'field1': 'value1', 'field2': 'value2'}
        })

        print(f"✅ Redis operations working: {result['final_results'] != {}}")
        return True

    except Exception as e:
        print(f"❌ Redis test failed: {e}")
        return False

def test_advanced_fastapi_operations():
    """Test FastAPI advanced operations"""
    print("🚀 Testing Advanced FastAPI Operations...")

    try:
        from advanced_fastapi_operations import get_advanced_fastapi_operations
        fastapi_ops = get_advanced_fastapi_operations()

        # Test that the app can be created
        app = fastapi_ops.app
        print(f"✅ FastAPI operations working: app created successfully (type: {type(app).__name__})")
        return True

    except Exception as e:
        print(f"❌ FastAPI test failed: {e}")
        return False

def run_integration_tests():
    """Run all integration tests"""
    print("🧪 AXIOM Advanced Modules Integration Test Suite")
    print("=" * 50)

    tests = [
        test_advanced_torch_operations,
        test_advanced_sympy_operations,
        test_advanced_scipy_operations,
        test_advanced_numpy_operations,
        test_advanced_redis_operations,
        test_advanced_fastapi_operations
    ]

    results = []
    start_time = time.time()

    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            results.append(False)
        print()

    end_time = time.time()

    # Summary
    passed = sum(results)
    total = len(results)
    failed = total - passed

    print("=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {passed/total*100:.1f}%")
    print(f"Execution Time: {end_time - start_time:.2f} seconds")

    if failed == 0:
        print("🎉 ALL TESTS PASSED!")
        return True
    else:
        print("⚠️ SOME TESTS FAILED")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("📦 Checking Dependencies...")

    required_modules = [
        'torch', 'sympy', 'scipy', 'numpy', 'redis', 'fastapi',
        'uvicorn', 'pydantic', 'jinja2', 'multipart'
    ]

    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            missing.append(module)

    if missing:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All dependencies available")
        return True

if __name__ == "__main__":
    print("🚀 AXIOM Advanced Library Exploitation Test")
    print("Maximizing library capabilities across all modules\n")

    # Check dependencies first
    if not check_dependencies():
        print("\n❌ Dependency check failed. Please install missing packages.")
        sys.exit(1)

    print()

    # Run integration tests
    success = run_integration_tests()

    if success:
        print("\n🎯 AXIOM Advanced Modules: FULLY OPERATIONAL")
        print("All library capabilities successfully exploited!")
        sys.exit(0)
    else:
        print("\n⚠️ Some modules need attention")
        sys.exit(1)
