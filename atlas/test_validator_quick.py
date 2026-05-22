#!/usr/bin/env python3
"""
Quick test for Advanced Hypothesis Validator.
Tests core functionality with minimal dependencies.
"""

import asyncio
import sys
sys.path.insert(0, "/Volumes/Ganador disk/atlas")

async def test_quick():
    """Run quick validation tests."""
    print("="*60)
    print("🔬 QUICK HYPOTHESIS VALIDATOR TEST")
    print("="*60)
    
    # Test 1: Import check
    print("\n1️⃣ Testing imports...")
    try:
        from app.services.advanced_hypothesis_validator import (
            AdvancedHypothesisValidator,
            ValidationMethod,
            ScientificToolAdapter,
            StatisticalAggregator,
            HypothesisStatus
        )
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return
    
    # Test 2: Statistical Aggregator
    print("\n2️⃣ Testing Statistical Aggregator...")
    try:
        # Test Fisher's method
        p_values = [0.03, 0.04, 0.06]
        is_sig, combined_p = StatisticalAggregator.fishers_method(p_values, alpha=0.1)
        print(f"   Fisher's method: p-values={p_values}")
        print(f"   Combined p-value: {combined_p:.4f}, Significant: {is_sig}")
        
        # Test E-value method
        is_sig_e, e_val = StatisticalAggregator.e_value_kappa_calibrator(p_values, alpha=0.1)
        print(f"   E-value method: Combined e-value={e_val:.4f}, Significant: {is_sig_e}")
        print("   ✅ Statistical aggregator works")
    except Exception as e:
        print(f"   ❌ Statistical aggregator error: {e}")
    
    # Test 3: Tool Adapter - Molecular Descriptors
    print("\n3️⃣ Testing Scientific Tool Adapter (RDKit)...")
    try:
        adapter = ScientificToolAdapter()
        
        # Available tools
        available = [t for t, info in adapter.available_tools.items() if info["available"]]
        print(f"   Available tools: {len(available)}")
        for t in available[:5]:
            print(f"     - {t}")
        if len(available) > 5:
            print(f"     ... and {len(available)-5} more")
        
        # Test molecular descriptors
        result = await adapter.execute_tool("molecular_descriptors", {
            "smiles": "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5"  # Imatinib
        })
        
        if result.get("success"):
            d = result["descriptors"]
            print(f"   Imatinib analysis:")
            print(f"     MW: {d['molecular_weight']:.1f}")
            print(f"     LogP: {d['logp']:.2f}")
            print(f"     TPSA: {d['tpsa']:.1f}")
            print("   ✅ RDKit tool works")
        else:
            print(f"   ❌ RDKit error: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Tool adapter error: {e}")
    
    # Test 4: Statistical Tests
    print("\n4️⃣ Testing Statistical Tests...")
    try:
        result = await adapter.execute_tool("statistical_tests", {
            "test_type": "ttest",
            "data1": [4.5, 4.8, 5.1, 4.9, 5.0],
            "data2": [3.2, 3.5, 3.1, 3.4, 3.3]
        })
        
        if result.get("success"):
            print(f"   T-test result:")
            print(f"     Statistic: {result['statistic']:.3f}")
            print(f"     P-value: {result['p_value']:.4e}")
            print(f"     Significant at 0.05: {result['significant_at_05']}")
            print("   ✅ Statistical tests work")
        else:
            print(f"   ❌ Stats error: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    # Test 5: Thermal Conductivity Model
    print("\n5️⃣ Testing Thermal Conductivity Model...")
    try:
        result = await adapter.execute_tool("thermal_conductivity", {
            "k_matrix": 0.4,
            "k_filler": 5000,
            "volume_fractions": [0.01, 0.05, 0.10]
        })
        
        if result.get("success"):
            print(f"   Maxwell-Garnett model:")
            for r in result["results"]:
                print(f"     {r['volume_fraction']*100:.0f}%: k={r['k_effective']:.3f} W/m·K (+{r['improvement_percent']:.1f}%)")
            print("   ✅ Thermal model works")
        else:
            print(f"   ❌ Thermal error: {result.get('error')}")
    except Exception as e:
        print(f"   ❌ Thermal error: {e}")
    
    # Test 6: Full Validator
    print("\n6️⃣ Testing Full Validator...")
    try:
        validator = AdvancedHypothesisValidator(
            alpha=0.1,
            max_tests=3,
            aggregation_method=ValidationMethod.FISHERS
        )
        
        # Simple hypothesis with pre-computed data
        hypothesis = "Drug-like molecules have LogP < 5"
        tests = [
            {
                "name": "LogP Distribution Test",
                "tool": "statistical_tests",
                "parameters": {
                    "test_type": "ttest",
                    "data1": [3.5, 4.2, 2.8, 3.9, 4.1],  # Sample LogP values
                    "popmean": 5
                },
                "description": "Test if mean LogP differs from 5",
                "null_hypothesis": "Mean LogP equals 5",
                "alternative_hypothesis": "Mean LogP differs from 5"
            }
        ]
        
        result = await validator.validate_hypothesis(hypothesis, "chemistry", tests)
        
        print(f"   Hypothesis: '{hypothesis}'")
        print(f"   Status: {result.status.value.upper()}")
        print(f"   P-value: {result.combined_p_value:.4e}" if result.combined_p_value else "   P-value: N/A")
        print(f"   Confidence: {result.confidence:.1%}")
        print(f"   Conclusion: {result.conclusion[:80]}...")
        print("   ✅ Full validator works")
    except Exception as e:
        print(f"   ❌ Validator error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 7: Quantum Simulation (if available)
    print("\n7️⃣ Testing Quantum Simulation (Qiskit)...")
    try:
        result = await adapter.execute_tool("quantum_simulation", {
            "circuit_type": "bell_state",
            "shots": 1000,
            "error_rate": 0.01
        })
        
        if result.get("success"):
            counts = result["counts"]
            total = sum(counts.values())
            correlated = counts.get("00", 0) + counts.get("11", 0)
            fidelity = correlated / total * 100
            print(f"   Bell state simulation:")
            print(f"     Shots: {result['shots']}")
            print(f"     Error rate: {result['error_rate']}")
            print(f"     Counts: {counts}")
            print(f"     Fidelity: {fidelity:.1f}%")
            print("   ✅ Quantum simulation works")
        else:
            print(f"   ⚠️ Qiskit not available: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️ Qiskit error: {e}")
    
    # Test 8: Sequence Analysis (if available)
    print("\n8️⃣ Testing Sequence Analysis (BioPython)...")
    try:
        result = await adapter.execute_tool("sequence_analysis", {
            "sequence": "ATGCGATCGATCGATCGATCG",
            "type": "dna"
        })
        
        if result.get("success"):
            print(f"   DNA sequence analysis:")
            print(f"     Length: {result['sequence_length']}")
            print(f"     GC content: {result['gc_content']:.1f}%")
            print("   ✅ Sequence analysis works")
        else:
            print(f"   ⚠️ BioPython not available: {result.get('error')}")
    except Exception as e:
        print(f"   ⚠️ BioPython error: {e}")
    
    print("\n" + "="*60)
    print("✅ QUICK TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_quick())
