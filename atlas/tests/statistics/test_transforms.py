#!/usr/bin/env python3
"""
Test script for Transform endpoints
"""

import requests

BASE_URL = "http://localhost:8002"

def test_transform_endpoint(name, endpoint, data=None):
    """Test a transform endpoint"""
    url = f"{BASE_URL}{endpoint}"

    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"\n🧪 Testing {name}:")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            if 'data' in result:
                data = result['data']
                if 'fourier_transform' in data:
                    print(f"Fourier Transform: {data['fourier_transform']}")
                elif 'laplace_transform' in data:
                    print(f"Laplace Transform: {data['laplace_transform']}")
                elif 'dft_coefficients' in data:
                    print(f"DFT computed with {len(data['dft_coefficients'])} coefficients")
                elif 'pairs' in data:
                    print(f"Found {len(data['pairs'])} transform pairs")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Transform Endpoints")
    print("=" * 50)

    # Test Fourier transform
    test_transform_endpoint(
        "Fourier Transform",
        "/api/transform/fourier-transform",
        {"expression": "sin(t)", "variable": "t", "result_variable": "f"}
    )

    # Test Laplace transform
    test_transform_endpoint(
        "Laplace Transform",
        "/api/transform/laplace-transform",
        {"expression": "t", "variable": "t", "result_variable": "s"}
    )

    # Test DFT
    test_transform_endpoint(
        "Discrete Fourier Transform",
        "/api/transform/discrete-fourier-transform",
        {"signal": [1.0, 0.0, 1.0, 0.0], "sampling_rate": 1.0}
    )

    # Test transform pairs
    test_transform_endpoint(
        "Fourier Transform Pairs",
        "/api/transform/transform-pairs/fourier"
    )

    print("\n" + "=" * 50)
    print("✨ Transform endpoints testing completed!")

if __name__ == "__main__":
    main()
