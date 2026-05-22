#!/usr/bin/env python3
"""
Simple test for Mathematics AI Simulated Annealing endpoint
"""

import requests
import time

def main():
    print("🧪 Testing Simulated Annealing Endpoint")
    print("=" * 40)

    # Wait for server
    print("⏳ Waiting for server...")
    time.sleep(2)

    url = "http://localhost:8002/api/optimization/simulated_annealing"
    data = {
        "objective_function": "x**2 + y**2",
        "variables": ["x", "y"],
        "bounds": {"x": [-5, 5], "y": [-5, 5]}
    }

    try:
        print(f"📡 Making request to: {url}")
        response = requests.post(url, json=data, timeout=10)

        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Status: {result.get('status')}")
            print(".4f")
            print(f"Variables: {result.get('optimal_variables')}")
        else:
            print("❌ Request failed")
            print(f"Response: {response.text}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()
