#!/usr/bin/env python3
"""
Test script for Mathematics AI endpoints
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_endpoint(method, endpoint, data=None, params=None):
    """Test an API endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, params=params, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, params=params, timeout=5)
        
        print(f"\n{method.upper()} {endpoint}")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    print("Testing Mathematics AI API Endpoints")
    print("=" * 50)
    
    # Test health check
    test_endpoint("GET", "/health")
    
    # Test basic arithmetic
    test_endpoint("GET", "/api/arithmetic/operations")
    
    # Test number theory
    test_endpoint("GET", "/api/number-theory/info")
    test_endpoint("POST", "/api/number-theory/prime-check", params={"number": 17})
    
    # Test optimization
    test_endpoint("GET", "/api/optimization/info")
    
    # Test math NLP
    test_endpoint("GET", "/api/math-nlp/info")
    
    # Test advanced algebra
    test_endpoint("GET", "/api/advanced-algebra/info")
    
    # Test matrix operations
    matrix_data = {"matrix": [[1, 2], [3, 4]]}
    test_endpoint("POST", "/api/advanced-algebra/matrix/determinant", data=matrix_data)
    
    # Test complex number operations
    test_endpoint("POST", "/api/complex/add", params={
        "real1": 1, "imag1": 2, "real2": 3, "imag2": 4
    })

if __name__ == "__main__":
    main()
