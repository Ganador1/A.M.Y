#!/usr/bin/env python3
"""
Test script for Advanced GPU and Distributed Scaling functionality
"""

import requests
import sys

def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        print(f"\nTesting: {description}")
        print(f"URL: {url}")

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        print("✓ Success")
        print(f"  Status: {data.get('status', 'N/A')}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"✗ Failed: {str(e)}")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False

def test_gpu_endpoints(base_url):
    """Test GPU-related endpoints"""
    print("\n" + "="*50)
    print("TESTING GPU ENDPOINTS")
    print("="*50)

    endpoints = [
        (f"{base_url}/api/advanced-gpu-scaling/gpu/advanced/status", "Advanced GPU Status"),
        (f"{base_url}/api/advanced-gpu-scaling/gpu/memory/stats", "GPU Memory Statistics"),
        (f"{base_url}/api/advanced-gpu-scaling/gpu/streams/stats", "GPU Stream Statistics"),
        (f"{base_url}/api/advanced-gpu-scaling/gpu/profiling/stats", "GPU Profiling Statistics"),
    ]

    results = []
    for url, desc in endpoints:
        results.append(test_endpoint(url, desc))

    return results

def test_scaling_endpoints(base_url):
    """Test distributed scaling endpoints"""
    print("\n" + "="*50)
    print("TESTING DISTRIBUTED SCALING ENDPOINTS")
    print("="*50)

    endpoints = [
        (f"{base_url}/api/advanced-gpu-scaling/scaling/cluster/status", "Cluster Status"),
        (f"{base_url}/api/advanced-gpu-scaling/scaling/load-balancer/stats", "Load Balancer Statistics"),
        (f"{base_url}/api/advanced-gpu-scaling/scaling/auto-scaling/status", "Auto-Scaling Status"),
        (f"{base_url}/api/advanced-gpu-scaling/scaling/fault-tolerance/stats", "Fault Tolerance Statistics"),
        (f"{base_url}/api/advanced-gpu-scaling/scaling/kubernetes/nodes", "Kubernetes Nodes"),
        (f"{base_url}/api/advanced-gpu-scaling/scaling/performance/summary", "Performance Summary"),
    ]

    results = []
    for url, desc in endpoints:
        results.append(test_endpoint(url, desc))

    return results

def test_basic_endpoints(base_url):
    """Test basic application endpoints"""
    print("\n" + "="*50)
    print("TESTING BASIC ENDPOINTS")
    print("="*50)

    endpoints = [
        (f"{base_url}/health", "Health Check"),
        (f"{base_url}/", "Root Endpoint"),
    ]

    results = []
    for url, desc in endpoints:
        results.append(test_endpoint(url, desc))

    return results

def main():
    """Main test function"""
    base_url = "http://localhost:8002"

    print("AXIOM Advanced GPU and Distributed Scaling Test")
    print("="*60)
    print(f"Testing server at: {base_url}")
    print("Make sure the server is running before executing this test.")
    print()

    # Test server connectivity first
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print("✗ Server is not responding correctly")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Cannot connect to server: {str(e)}")
        print("Please start the AXIOM server first:")
        print("  python main.py")
        sys.exit(1)

    print("✓ Server connection successful")

    # Run all tests
    all_results = []

    # Basic endpoints
    basic_results = test_basic_endpoints(base_url)
    all_results.extend(basic_results)

    # GPU endpoints
    gpu_results = test_gpu_endpoints(base_url)
    all_results.extend(gpu_results)

    # Scaling endpoints
    scaling_results = test_scaling_endpoints(base_url)
    all_results.extend(scaling_results)

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    total_tests = len(all_results)
    passed_tests = sum(all_results)
    failed_tests = total_tests - passed_tests

    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(".1f")

    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("Phase 4.1 (GPU Optimization) and Phase 4.2 (Distributed Scaling)")
        print("are working correctly!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed")
        print("Please check the server logs for more details.")

    return failed_tests == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
