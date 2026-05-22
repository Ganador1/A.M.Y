#!/usr/bin/env python3
"""
Quick test of hardware abstraction endpoints
"""

import requests

BASE_URL = "http://localhost:8002"

def test_endpoint(method, endpoint, data=None):
    """Test single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    response = None
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        
        if response:
            return {
                "status": response.status_code,
                "data": response.json() if response.status_code == 200 else response.text
            }
        else:
            return {"status": 0, "error": "No response"}
    except Exception as e:
        return {"status": 0, "error": str(e)}

def main():
    print("🔧 AXIOM Hardware Abstraction Layer - Quick Test")
    print("=" * 60)
    
    # Test 1: Service status
    print("\n1. Testing service status...")
    result = test_endpoint("GET", "/api/hardware/service/status")
    if result["status"] == 200:
        print("✅ Service is operational")
        stats = result["data"]["statistics"]
        print(f"   Current instruments: {stats['total_instruments']}")
    else:
        print(f"❌ Service test failed: {result}")
        return
    
    # Test 2: List protocols
    print("\n2. Testing supported protocols...")
    result = test_endpoint("GET", "/api/hardware/protocols")
    if result["status"] == 200:
        protocols = result["data"]["protocols"]
        print(f"✅ Found {len(protocols)} protocols: {list(protocols.keys())}")
    else:
        print(f"❌ Protocols test failed: {result}")
    
    # Test 3: Setup demo instruments
    print("\n3. Setting up demo instruments...")
    result = test_endpoint("POST", "/api/hardware/demo/setup")
    if result["status"] == 200:
        print(f"✅ Demo setup: {result['data']['total_registered']} instruments registered")
    else:
        print(f"❌ Demo setup failed: {result}")
        return
    
    # Test 4: List instruments
    print("\n4. Listing instruments...")
    result = test_endpoint("GET", "/api/hardware/instruments")
    if result["status"] == 200:
        instruments = result["data"]["instruments"]
        print(f"✅ Found {len(instruments)} instruments")
        for inst_id in list(instruments.keys())[:3]:  # Show first 3
            print(f"   • {inst_id}: {instruments[inst_id].get('name', 'Unknown')}")
    else:
        print(f"❌ Instruments listing failed: {result}")
        return
    
    # Test 5: Send command to first instrument
    print("\n5. Testing command execution...")
    first_instrument = list(instruments.keys())[0] if instruments else None
    if first_instrument:
        command_data = {
            "command": "GetSpectrum" if "spectrometer" in first_instrument else "ReadStatus",
            "parameters": {"test": True},
            "priority": 5
        }
        result = test_endpoint("POST", f"/api/hardware/instruments/{first_instrument}/commands", command_data)
        if result["status"] == 200:
            response = result["data"]["response"]
            print(f"✅ Command '{response['command']}' executed: {response['status']}")
        else:
            print(f"❌ Command execution failed: {result}")
    
    # Test 6: Cleanup
    print("\n6. Cleaning up demo instruments...")
    result = test_endpoint("DELETE", "/api/hardware/demo/cleanup")
    if result["status"] == 200:
        print(f"✅ Cleanup complete: {result['data']['total_removed']} instruments removed")
    else:
        print(f"❌ Cleanup failed: {result}")
    
    print("\n🎉 Hardware Abstraction Layer Quick Test Complete!")

if __name__ == "__main__":
    main()
