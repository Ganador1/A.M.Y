#!/usr/bin/env python3
"""
Test hardware abstraction system with mock instruments
Tests the complete workflow: setup → register → control → cleanup
"""

import asyncio
import aiohttp
import json
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8002"

class HardwareAbstractionTester:
    """Test suite for hardware abstraction layer"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.status == 200 else await response.text()
                    }
            elif method.upper() == "POST":
                headers = {"Content-Type": "application/json"}
                async with self.session.post(url, json=data, headers=headers) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.status == 200 else await response.text()
                    }
            elif method.upper() == "DELETE":
                async with self.session.delete(url) as response:
                    return {
                        "status": response.status,
                        "data": await response.json() if response.status == 200 else await response.text()
                    }
            else:
                return {"status": 0, "error": f"Unsupported method: {method}"}
                    
        except Exception as e:
            return {"status": 0, "error": str(e)}
    
    async def run_comprehensive_test(self):
        """Run comprehensive hardware abstraction test suite"""
        
        print("\n" + "="*80)
        print("🔬 AXIOM Hardware Abstraction Layer - Comprehensive Test Suite")
        print("="*80)
        
        # Test 1: Service status
        print("\n📊 Test 1: Service Status")
        print("-" * 40)
        result = await self.test_endpoint("GET", "/api/hardware/service/status")
        if result["status"] == 200:
            print("✅ Hardware Abstraction Service is operational")
            service_info = result["data"]["service"]
            stats = result["data"]["statistics"]
            print(f"   📋 Service: {service_info['name']} v{service_info['version']}")
            print(f"   📈 Current instruments: {stats['total_instruments']}")
            print(f"   🔗 Supported protocols: {stats['supported_protocols']}")
        else:
            print(f"❌ Service status check failed: {result}")
            return
        
        # Test 2: List supported protocols
        print("\n🔗 Test 2: Supported Protocols")
        print("-" * 40)
        result = await self.test_endpoint("GET", "/api/hardware/protocols")
        if result["status"] == 200:
            protocols = result["data"]["protocols"]
            print(f"✅ Found {len(protocols)} supported protocols:")
            for protocol_name, info in protocols.items():
                print(f"   • {info['name']}")
                print(f"     Features: {', '.join(info['features'])}")
        else:
            print(f"❌ Protocol listing failed: {result}")
        
        # Test 3: List instrument types
        print("\n🔬 Test 3: Instrument Types")
        print("-" * 40)
        result = await self.test_endpoint("GET", "/api/hardware/instrument-types")
        if result["status"] == 200:
            types = result["data"]["instrument_types"]
            print(f"✅ Found {len(types)} supported instrument types:")
            for type_name, info in types.items():
                print(f"   • {info['name']}: {info['description']}")
        else:
            print(f"❌ Instrument types listing failed: {result}")
        
        # Test 4: Setup demo instruments
        print("\n🧪 Test 4: Demo Instruments Setup")
        print("-" * 40)
        result = await self.test_endpoint("POST", "/api/hardware/demo/setup")
        if result["status"] == 200:
            setup_info = result["data"]
            print(f"✅ Demo setup: {setup_info['total_registered']} instruments registered")
            for instrument in setup_info["demo_instruments"]:
                status = "✅" if instrument["registered"] else "❌"
                print(f"   {status} {instrument['name']} [{instrument['instrument_id']}]")
        else:
            print(f"❌ Demo setup failed: {result}")
            return
        
        # Test 5: List instruments
        print("\n📋 Test 5: List All Instruments")
        print("-" * 40)
        result = await self.test_endpoint("GET", "/api/hardware/instruments")
        if result["status"] == 200:
            instruments = result["data"]["instruments"]
            print(f"✅ Found {len(instruments)} registered instruments:")
            for instrument_id, info in instruments.items():
                print(f"   • {info.get('name', 'Unknown')} [{instrument_id}]")
                print(f"     Type: {info.get('type', 'Unknown')}, Protocol: {info.get('protocol', 'Unknown')}")
        else:
            print(f"❌ Instrument listing failed: {result}")
            return
        
        # Test 6: Get specific instrument info
        print("\n🔍 Test 6: Instrument Details")
        print("-" * 40)
        # Use first demo instrument
        test_instrument_id = "demo_spectrometer_01"
        result = await self.test_endpoint("GET", f"/api/hardware/instruments/{test_instrument_id}")
        if result["status"] == 200:
            instrument = result["data"]["instrument"]
            print(f"✅ Instrument details for {test_instrument_id}:")
            print(f"   📋 Name: {instrument.get('name', 'Unknown')}")
            print(f"   🔧 Type: {instrument.get('type', 'Unknown')}")
            print(f"   🔗 Protocol: {instrument.get('protocol', 'Unknown')}")
            print(f"   📊 Status: {instrument.get('current_status', 'Unknown')}")
        else:
            print(f"❌ Instrument details failed: {result}")
        
        # Test 7: Send instrument command
        print("\n📤 Test 7: Send Command to Instrument")
        print("-" * 40)
        command_data = {
            "command": "GetSpectrum",
            "parameters": {"wavelength_range": [300, 800], "resolution": 1},
            "priority": 5,
            "timeout": 30
        }
        result = await self.test_endpoint("POST", f"/api/hardware/instruments/{test_instrument_id}/commands", command_data)
        if result["status"] == 200:
            response = result["data"]["response"]
            print("✅ Command executed successfully:")
            print(f"   📋 Command: {response['command']}")
            print(f"   📊 Status: {response['status']}")
            print(f"   ⏱️  Execution time: {response['execution_time']:.3f}s")
            if response.get('data'):
                print(f"   📊 Response data: {json.dumps(response['data'], indent=2)[:200]}...")
        else:
            print(f"❌ Command execution failed: {result}")
        
        # Test 8: Queue background command
        print("\n📥 Test 8: Queue Background Command")
        print("-" * 40)
        queue_command_data = {
            "command": "Calibrate",
            "parameters": {"calibration_type": "full", "standards": ["reference1", "reference2"]},
            "priority": 3,
            "timeout": 60
        }
        result = await self.test_endpoint("POST", f"/api/hardware/instruments/{test_instrument_id}/commands/queue", queue_command_data)
        if result["status"] == 200:
            print("✅ Command queued for background execution:")
            print(f"   📋 Command: {result['data']['command']}")
            print(f"   📊 Priority: {result['data']['priority']}")
        else:
            print(f"❌ Command queueing failed: {result}")
        
        # Test 9: Check instrument status
        print("\n📊 Test 9: Instrument Status Check")
        print("-" * 40)
        result = await self.test_endpoint("GET", f"/api/hardware/instruments/{test_instrument_id}/status")
        if result["status"] == 200:
            status_info = result["data"]
            print("✅ Instrument status:")
            print(f"   📊 Status: {status_info['status']}")
            print(f"   📋 Description: {status_info['status_description']}")
        else:
            print(f"❌ Status check failed: {result}")
        
        # Test 10: Test multiple instrument types
        print("\n🔬 Test 10: Multiple Instrument Control")
        print("-" * 40)
        test_instruments = ["demo_spectrometer_01", "demo_liquid_handler_01", "demo_sensor_01"]
        
        for instrument_id in test_instruments:
            # Get instrument info
            result = await self.test_endpoint("GET", f"/api/hardware/instruments/{instrument_id}")
            if result["status"] == 200:
                instrument = result["data"]["instrument"]
                print(f"✅ {instrument.get('name', 'Unknown')} [{instrument_id}]")
                
                # Send appropriate command based on type
                if "spectrometer" in instrument_id:
                    cmd_data = {"command": "StartSpectrum", "parameters": {"integration_time": 1000}}
                elif "liquid_handler" in instrument_id:
                    cmd_data = {"command": "Aspirate", "parameters": {"volume": 100, "well": "A1"}}
                elif "sensor" in instrument_id:
                    cmd_data = {"command": "ReadTemperature", "parameters": {}}
                else:
                    continue
                
                # Send command
                cmd_result = await self.test_endpoint("POST", f"/api/hardware/instruments/{instrument_id}/commands", cmd_data)
                if cmd_result["status"] == 200:
                    response = cmd_result["data"]["response"]
                    print(f"   📤 Command '{response['command']}': {response['status']}")
                else:
                    print(f"   ❌ Command failed: {cmd_result}")
            else:
                print(f"❌ {instrument_id}: Not found")
        
        # Test 11: Service statistics after operations
        print("\n📈 Test 11: Final Service Statistics")
        print("-" * 40)
        result = await self.test_endpoint("GET", "/api/hardware/service/status")
        if result["status"] == 200:
            stats = result["data"]["statistics"]
            print("✅ Final statistics:")
            print(f"   📊 Total instruments: {stats['total_instruments']}")
            print(f"   📋 Status breakdown: {stats['status_breakdown']}")
        
        # Test 12: Cleanup demo instruments
        print("\n🧹 Test 12: Demo Cleanup")
        print("-" * 40)
        result = await self.test_endpoint("DELETE", "/api/hardware/demo/cleanup")
        if result["status"] == 200:
            cleanup_info = result["data"]
            print(f"✅ Cleanup complete: {cleanup_info['total_removed']} instruments removed")
            for instrument in cleanup_info["removed_instruments"]:
                status = "✅" if instrument["removed"] else "❌"
                print(f"   {status} {instrument['instrument_id']}")
        else:
            print(f"❌ Cleanup failed: {result}")
        
        # Final verification
        print("\n📊 Test 13: Final Verification")
        print("-" * 40)
        result = await self.test_endpoint("GET", "/api/hardware/instruments")
        if result["status"] == 200:
            remaining_instruments = len(result["data"]["instruments"])
            print(f"✅ Cleanup verified: {remaining_instruments} instruments remaining")
        
        print("\n" + "="*80)
        print("🎉 AXIOM Hardware Abstraction Layer Test Suite Complete!")
        print("="*80)

async def main():
    """Main test execution"""
    
    # Check if service is running
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/health") as response:
                if response.status != 200:
                    print("❌ AXIOM service is not running. Start it first with: python main.py")
                    return
    except aiohttp.ClientConnectorError:
        print("❌ Cannot connect to AXIOM service. Make sure it's running on http://localhost:8002")
        return
    
    # Run tests
    async with HardwareAbstractionTester() as tester:
        await tester.run_comprehensive_test()

if __name__ == "__main__":
    asyncio.run(main())
