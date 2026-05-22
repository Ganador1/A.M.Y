#!/usr/bin/env python3
"""
Test script for QuantumComputingService improvements
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_quantum_computing_improvements():
    """Test the improved QuantumComputingService"""
    print("🧪 Testing QuantumComputingService Improvements")
    print("=" * 60)
    
    try:
        # Import the service
        from services.quantum_computing import QuantumComputingService
        
        # Create service instance
        service = QuantumComputingService()
        
        print(f"✅ Service created successfully")
        print(f"📊 Max qubits: {service.max_qubits}")
        print(f"🔧 Advanced config: {service.advanced_config}")
        
        # Test 1: Advanced VQE
        print("\n🔬 Testing Advanced VQE...")
        vqe_params = {
            "n_qubits": 2,
            "ansatz_type": "TwoLocal",
            "optimizer_type": "COBYLA",
            "reps": 2
        }
        
        vqe_result = service.create_advanced_vqe(vqe_params)
        if "error" not in vqe_result:
            print(f"✅ Advanced VQE successful")
            print(f"   Eigenvalue: {vqe_result['results']['eigenvalue']:.6f}")
            print(f"   Cost function evals: {vqe_result['results']['cost_function_evals']}")
            print(f"   Optimizer time: {vqe_result['results']['optimizer_time']:.3f}s")
        else:
            print(f"❌ Advanced VQE failed: {vqe_result['error']}")
        
        # Test 2: Advanced QAOA
        print("\n🎯 Testing Advanced QAOA...")
        qaoa_params = {
            "n_qubits": 3,
            "layers": 2,
            "optimizer_type": "COBYLA"
        }
        
        qaoa_result = service.create_advanced_qaoa(qaoa_params)
        if "error" not in qaoa_result:
            print(f"✅ Advanced QAOA successful")
            print(f"   Eigenvalue: {qaoa_result['results']['eigenvalue']:.6f}")
            print(f"   Cost function evals: {qaoa_result['results']['cost_function_evals']}")
            print(f"   Optimizer time: {qaoa_result['results']['optimizer_time']:.3f}s")
        else:
            print(f"❌ Advanced QAOA failed: {qaoa_result['error']}")
        
        # Test 3: Quantum Fourier Transform
        print("\n🌊 Testing Quantum Fourier Transform...")
        qft_params = {
            "n_qubits": 3,
            "optimized": True
        }
        
        qft_result = service.create_quantum_fourier_transform(qft_params)
        if "error" not in qft_result:
            print(f"✅ QFT successful")
            print(f"   Circuit depth: {qft_result['results']['circuit_depth']}")
            print(f"   Gate count: {qft_result['results']['gate_count']}")
            print(f"   Max probability: {max(qft_result['results']['probabilities']):.6f}")
        else:
            print(f"❌ QFT failed: {qft_result['error']}")
        
        # Test 4: Grover's Algorithm
        print("\n🔍 Testing Grover's Algorithm...")
        grover_params = {
            "n_qubits": 3,
            "target_state": "101"
        }
        
        grover_result = service.create_grover_algorithm(grover_params)
        if "error" not in grover_result:
            print(f"✅ Grover's algorithm successful")
            print(f"   Target state: {grover_params['target_state']}")
            print(f"   Iterations: {grover_result['results']['iterations']}")
            print(f"   Success probability: {grover_result['results']['success_probability']:.6f}")
            print(f"   Circuit depth: {grover_result['results']['circuit_depth']}")
        else:
            print(f"❌ Grover's algorithm failed: {grover_result['error']}")
        
        # Test 5: Noise Model
        print("\n🌪️ Testing Noise Model...")
        noise_params = {
            "n_qubits": 2,
            "gate_error_rate": 0.01,
            "thermal_relaxation_time": 100.0
        }
        
        noise_result = service.create_noise_model(noise_params)
        if "error" not in noise_result:
            print(f"✅ Noise model created successfully")
            print(f"   Single-qubit gate error: {noise_result['results']['error_rates']['single_qubit_gates']}")
            print(f"   Two-qubit gate error: {noise_result['results']['error_rates']['two_qubit_gates']}")
            print(f"   Thermal relaxation time: {noise_result['results']['error_rates']['thermal_relaxation']}")
        else:
            print(f"❌ Noise model creation failed: {noise_result['error']}")
        
        # Test 6: Circuit Performance Analysis
        print("\n📊 Testing Circuit Performance Analysis...")
        circuit_params = {
            "circuit_type": "ghz_state",
            "n_qubits": 3
        }
        
        circuit_result = service.analyze_circuit_performance(circuit_params)
        if "error" not in circuit_result:
            print(f"✅ Circuit analysis successful")
            print(f"   Circuit type: {circuit_params['circuit_type']}")
            print(f"   Circuit depth: {circuit_result['results']['circuit_depth']}")
            print(f"   Gate count: {circuit_result['results']['gate_count']}")
            print(f"   Max probability: {circuit_result['results']['max_probability']:.6f}")
            print(f"   Entropy: {circuit_result['results']['entropy']:.6f}")
        else:
            print(f"❌ Circuit analysis failed: {circuit_result['error']}")
        
        # Test 7: Legacy methods still work
        print("\n🔄 Testing Legacy Methods...")
        legacy_params = {"n_qubits": 2}
        
        # Test run_advanced_vqe (should use new implementation)
        legacy_vqe = service.run_advanced_vqe(legacy_params)
        if "error" not in legacy_vqe:
            print(f"✅ Legacy run_advanced_vqe works")
        else:
            print(f"❌ Legacy run_advanced_vqe failed: {legacy_vqe['error']}")
        
        # Test run_advanced_qaoa (should use new implementation)
        legacy_qaoa = service.run_advanced_qaoa(legacy_params)
        if "error" not in legacy_qaoa:
            print(f"✅ Legacy run_advanced_qaoa works")
        else:
            print(f"❌ Legacy run_advanced_qaoa failed: {legacy_qaoa['error']}")
        
        print("\n🎉 Quantum Computing Service Improvements Test Complete!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_quantum_computing_improvements()
    sys.exit(0 if success else 1)
