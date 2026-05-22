#!/usr/bin/env python3
"""
Minimal test script - self-contained output to file
"""
import sys
import asyncio
from datetime import datetime
sys.path.insert(0, "/Volumes/Ganador disk/atlas")

OUTPUT_FILE = "/Volumes/Ganador disk/atlas/validator_test_output.txt"

async def run_test():
    output = []
    output.append("="*60)
    output.append("ADVANCED HYPOTHESIS VALIDATOR TEST")
    output.append(f"Timestamp: {datetime.now().isoformat()}")
    output.append("="*60)
    
    # Test imports
    output.append("\n1. Testing imports...")
    try:
        from app.services.advanced_hypothesis_validator import (
            AdvancedHypothesisValidator,
            ValidationMethod,
            ScientificToolAdapter,
            StatisticalAggregator,
        )
        output.append("   ✅ Imports OK")
    except Exception as e:
        output.append(f"   ❌ Import error: {e}")
        with open(OUTPUT_FILE, "w") as f:
            f.write("\n".join(output))
        return
    
    # Test StatisticalAggregator
    output.append("\n2. Testing StatisticalAggregator...")
    try:
        p_values = [0.03, 0.04, 0.06]
        is_sig, combined_p = StatisticalAggregator.fishers_method(p_values, alpha=0.1)
        output.append(f"   Fisher's: p-values={p_values} -> combined={combined_p:.4f}, sig={is_sig}")
        output.append("   ✅ StatisticalAggregator OK")
    except Exception as e:
        output.append(f"   ❌ Error: {e}")
    
    # Test ScientificToolAdapter
    output.append("\n3. Testing ScientificToolAdapter...")
    try:
        adapter = ScientificToolAdapter()
        available = [t for t, info in adapter.available_tools.items() if info["available"]]
        output.append(f"   Available tools: {len(available)}")
        
        # Test molecular descriptors
        result = await adapter.execute_tool("molecular_descriptors", {
            "smiles": "c1ccccc1"  # benzene
        })
        if result.get("success"):
            d = result["descriptors"]
            output.append(f"   Benzene: MW={d['molecular_weight']:.1f}, LogP={d['logp']:.2f}")
            output.append("   ✅ RDKit OK")
        else:
            output.append(f"   ⚠️ RDKit: {result.get('error')}")
    except Exception as e:
        output.append(f"   ❌ Error: {e}")
    
    # Test statistical test
    output.append("\n4. Testing statistical tests...")
    try:
        result = await adapter.execute_tool("statistical_tests", {
            "test_type": "ttest",
            "data1": [4.5, 4.8, 5.1, 4.9, 5.0],
            "data2": [3.2, 3.5, 3.1, 3.4, 3.3]
        })
        if result.get("success"):
            output.append(f"   T-test: stat={result['statistic']:.3f}, p={result['p_value']:.4e}")
            output.append("   ✅ Statistical tests OK")
        else:
            output.append(f"   ❌ Error: {result.get('error')}")
    except Exception as e:
        output.append(f"   ❌ Error: {e}")
    
    # Test thermal model
    output.append("\n5. Testing thermal conductivity model...")
    try:
        result = await adapter.execute_tool("thermal_conductivity", {
            "k_matrix": 0.4,
            "k_filler": 5000,
            "volume_fractions": [0.01, 0.05, 0.10]
        })
        if result.get("success"):
            for r in result["results"]:
                output.append(f"   VF={r['volume_fraction']*100:.0f}%: improvement={r['improvement_percent']:.1f}%")
            output.append("   ✅ Thermal model OK")
        else:
            output.append(f"   ❌ Error: {result.get('error')}")
    except Exception as e:
        output.append(f"   ❌ Error: {e}")
    
    # Test full validator
    output.append("\n6. Testing Full Validator...")
    try:
        validator = AdvancedHypothesisValidator(
            alpha=0.1,
            max_tests=3,
            aggregation_method=ValidationMethod.FISHERS
        )
        
        hypothesis = "Drug-like molecules have LogP < 5"
        tests = [{
            "name": "LogP Test",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": [3.5, 4.2, 2.8, 3.9, 4.1],
                "popmean": 5
            },
            "description": "Test if LogP differs from 5",
            "null_hypothesis": "Mean LogP = 5",
            "alternative_hypothesis": "Mean LogP ≠ 5"
        }]
        
        result = await validator.validate_hypothesis(hypothesis, "chemistry", tests)
        output.append(f"   Hypothesis: '{hypothesis}'")
        output.append(f"   Status: {result.status.value}")
        output.append(f"   P-value: {result.combined_p_value:.4e}" if result.combined_p_value else "   P-value: N/A")
        output.append(f"   Confidence: {result.confidence:.1%}")
        output.append("   ✅ Full Validator OK")
    except Exception as e:
        output.append(f"   ❌ Error: {e}")
        import traceback
        output.append(traceback.format_exc())
    
    # Test Qiskit
    output.append("\n7. Testing Qiskit (optional)...")
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
            output.append(f"   Bell state fidelity: {fidelity:.1f}%")
            output.append("   ✅ Qiskit OK")
        else:
            output.append(f"   ⚠️ Qiskit not available: {result.get('error', 'unknown')}")
    except Exception as e:
        output.append(f"   ⚠️ Qiskit error: {e}")
    
    # Test BioPython
    output.append("\n8. Testing BioPython (optional)...")
    try:
        result = await adapter.execute_tool("sequence_analysis", {
            "sequence": "ATGCGATCGATCGATCGATCG",
            "type": "dna"
        })
        if result.get("success"):
            output.append(f"   GC content: {result['gc_content']:.1f}%")
            output.append("   ✅ BioPython OK")
        else:
            output.append(f"   ⚠️ BioPython not available: {result.get('error', 'unknown')}")
    except Exception as e:
        output.append(f"   ⚠️ BioPython error: {e}")
    
    output.append("\n" + "="*60)
    output.append("TEST COMPLETE")
    output.append("="*60)
    
    # Write to file
    with open(OUTPUT_FILE, "w") as f:
        f.write("\n".join(output))
    
    # Also print
    print("\n".join(output))

if __name__ == "__main__":
    asyncio.run(run_test())
    print(f"\n📄 Output saved to: {OUTPUT_FILE}")
