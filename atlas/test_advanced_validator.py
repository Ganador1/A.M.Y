#!/usr/bin/env python3
"""
Test the Advanced Hypothesis Validator with real scientific hypotheses.

This script demonstrates:
1. POPPER-style sequential falsification with statistical rigor
2. Multiple scientific tool integrations
3. Proper aggregation of multiple test results (Fisher's method, E-values)
"""

import asyncio
import json
import numpy as np
from datetime import datetime

# Add project root to path
import sys
sys.path.insert(0, "/Volumes/Ganador disk/atlas")

from app.services.advanced_hypothesis_validator import (
    AdvancedHypothesisValidator,
    ValidationMethod,
    ScientificToolAdapter,
    validate_scientific_hypothesis
)


async def test_chemistry_hypothesis():
    """Test a drug discovery hypothesis using RDKit tools."""
    print("\n" + "="*70)
    print("🧪 TEST 1: DRUG DISCOVERY HYPOTHESIS")
    print("="*70)
    
    hypothesis = "Kinase inhibitors with LogP < 5 have better bioavailability than those with LogP > 5"
    
    # Define test compounds (known kinase inhibitors)
    low_logp_compounds = [
        "CC1=C(C=C(C=C1)NC(=O)C2=CC=C(C=C2)CN3CCN(CC3)C)NC4=NC=CC(=N4)C5=CN=CC=C5",  # Imatinib
        "CC1=C(C=C(C=C1)C(=O)NC2=CC(=C(C=C2)CN3CCN(CC3)C)C(F)(F)F)C#CC4=CN=C5C=CC=CC5=N4",  # Nilotinib
    ]
    
    high_logp_compounds = [
        "COC1=CC2=C(C=C1OCCCN3CCOCC3)C(=NC=N2)NC4=CC(=C(C=C4)F)Cl",  # Gefitinib
        "C#CC1=CC=CC(=C1)NC2=NC=NC3=C2C=C(C=C3)OCCOC",  # Erlotinib
    ]
    
    # Calculate descriptors for each group
    adapter = ScientificToolAdapter()
    
    low_logp_results = []
    high_logp_results = []
    
    print(f"\nHypothesis: {hypothesis}")
    print(f"\nAnalyzing {len(low_logp_compounds)} low-LogP and {len(high_logp_compounds)} high-LogP compounds...")
    
    for smiles in low_logp_compounds:
        result = await adapter.execute_tool("molecular_descriptors", {"smiles": smiles})
        if result.get("success"):
            low_logp_results.append(result["descriptors"])
            print(f"  Low-LogP compound: MW={result['descriptors']['molecular_weight']:.1f}, LogP={result['descriptors']['logp']:.2f}")
    
    for smiles in high_logp_compounds:
        result = await adapter.execute_tool("molecular_descriptors", {"smiles": smiles})
        if result.get("success"):
            high_logp_results.append(result["descriptors"])
            print(f"  High-LogP compound: MW={result['descriptors']['molecular_weight']:.1f}, LogP={result['descriptors']['logp']:.2f}")
    
    # Run statistical tests
    tests = [
        {
            "name": "LogP Comparison",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": [d["logp"] for d in low_logp_results],
                "data2": [d["logp"] for d in high_logp_results]
            },
            "description": "Compare LogP values between groups",
            "null_hypothesis": "No difference in LogP between groups",
            "alternative_hypothesis": "Groups have different LogP values"
        },
        {
            "name": "TPSA Comparison",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": [d["tpsa"] for d in low_logp_results],
                "data2": [d["tpsa"] for d in high_logp_results]
            },
            "description": "Compare TPSA (bioavailability indicator) between groups",
            "null_hypothesis": "No difference in TPSA between groups",
            "alternative_hypothesis": "Groups have different TPSA values"
        },
        {
            "name": "HBD Comparison",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": [d["hbd"] for d in low_logp_results],
                "data2": [d["hbd"] for d in high_logp_results]
            },
            "description": "Compare H-bond donors between groups",
            "null_hypothesis": "No difference in HBD between groups",
            "alternative_hypothesis": "Groups have different HBD values"
        }
    ]
    
    validator = AdvancedHypothesisValidator(
        alpha=0.1,
        max_tests=5,
        aggregation_method=ValidationMethod.E_VALUE
    )
    
    result = await validator.validate_hypothesis(hypothesis, "chemistry", tests)
    
    print(f"\n📊 RESULTS:")
    print(f"  Status: {result.status.value.upper()}")
    print(f"  Combined p-value: {result.combined_p_value:.4e}" if result.combined_p_value else "  Combined p-value: N/A")
    print(f"  Combined e-value: {result.combined_e_value:.4f}" if result.combined_e_value else "  Combined e-value: N/A")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"\n💡 Conclusion: {result.conclusion}")
    
    return result


async def test_materials_hypothesis():
    """Test a materials science hypothesis using thermal conductivity models."""
    print("\n" + "="*70)
    print("🔬 TEST 2: MATERIALS SCIENCE HYPOTHESIS")
    print("="*70)
    
    hypothesis = "Adding 5% graphene nanofillers increases polymer thermal conductivity by at least 50%"
    
    adapter = ScientificToolAdapter()
    
    # Test with Maxwell-Garnett model
    result = await adapter.execute_tool("thermal_conductivity", {
        "k_matrix": 0.4,  # Typical polymer (W/m·K)
        "k_filler": 5000,  # Graphene (W/m·K)
        "volume_fractions": [0.01, 0.03, 0.05, 0.07, 0.10]
    })
    
    print(f"\nHypothesis: {hypothesis}")
    print(f"\nMaxwell-Garnett Model Results:")
    
    improvements = []
    for r in result.get("results", []):
        print(f"  Volume fraction {r['volume_fraction']*100:.0f}%: k={r['k_effective']:.3f} W/m·K (improvement: {r['improvement_percent']:.1f}%)")
        improvements.append(r['improvement_percent'])
    
    # Check if 5% gives 50% improvement
    five_percent_improvement = improvements[2] if len(improvements) > 2 else 0
    
    # Create statistical test
    tests = [
        {
            "name": "Improvement Threshold Test",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": improvements,
                "popmean": 50  # Expected 50% improvement
            },
            "description": "Test if mean improvement significantly differs from 50%",
            "null_hypothesis": "Mean improvement equals 50%",
            "alternative_hypothesis": "Mean improvement differs from 50%"
        }
    ]
    
    validator = AdvancedHypothesisValidator(
        alpha=0.1,
        aggregation_method=ValidationMethod.FISHERS
    )
    
    result = await validator.validate_hypothesis(hypothesis, "materials", tests)
    
    print(f"\n📊 RESULTS:")
    print(f"  Actual improvement at 5%: {five_percent_improvement:.1f}%")
    print(f"  Required for hypothesis: 50%")
    print(f"  Status: {result.status.value.upper()}")
    print(f"\n💡 Conclusion: {result.conclusion}")
    
    # Direct validation
    if five_percent_improvement >= 50:
        print(f"\n✅ HYPOTHESIS VALIDATED: {five_percent_improvement:.1f}% >= 50%")
    else:
        print(f"\n❌ HYPOTHESIS REFUTED: {five_percent_improvement:.1f}% < 50%")
    
    return result


async def test_quantum_hypothesis():
    """Test a quantum computing hypothesis using Qiskit simulations."""
    print("\n" + "="*70)
    print("⚛️ TEST 3: QUANTUM COMPUTING HYPOTHESIS")
    print("="*70)
    
    hypothesis = "Bell states maintain >90% fidelity at error rates below 1%"
    
    adapter = ScientificToolAdapter()
    
    # Test at various error rates
    error_rates = [0.001, 0.005, 0.01, 0.02, 0.05]
    fidelities = []
    
    print(f"\nHypothesis: {hypothesis}")
    print(f"\nSimulating Bell state at different error rates...")
    
    for error_rate in error_rates:
        result = await adapter.execute_tool("quantum_simulation", {
            "circuit_type": "bell_state",
            "shots": 10000,
            "error_rate": error_rate
        })
        
        if result.get("success"):
            counts = result["counts"]
            total = sum(counts.values())
            # For perfect Bell state, we expect only "00" and "11"
            correlated = counts.get("00", 0) + counts.get("11", 0)
            fidelity = correlated / total * 100
            fidelities.append(fidelity)
            print(f"  Error rate {error_rate*100:.1f}%: Fidelity = {fidelity:.1f}%")
    
    # Test the hypothesis
    below_1_percent = [f for i, f in enumerate(fidelities) if error_rates[i] <= 0.01]
    
    tests = [
        {
            "name": "Fidelity Threshold Test",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": below_1_percent,
                "popmean": 90
            },
            "description": "Test if fidelity is significantly above 90% at low error rates",
            "null_hypothesis": "Fidelity equals 90%",
            "alternative_hypothesis": "Fidelity differs from 90%"
        }
    ]
    
    validator = AdvancedHypothesisValidator(
        alpha=0.1,
        aggregation_method=ValidationMethod.E_VALUE
    )
    
    result = await validator.validate_hypothesis(hypothesis, "quantum", tests)
    
    avg_fidelity_low_error = np.mean(below_1_percent)
    
    print(f"\n📊 RESULTS:")
    print(f"  Average fidelity at ≤1% error: {avg_fidelity_low_error:.1f}%")
    print(f"  Threshold: 90%")
    print(f"  Status: {result.status.value.upper()}")
    
    if avg_fidelity_low_error > 90:
        print(f"\n✅ HYPOTHESIS VALIDATED: {avg_fidelity_low_error:.1f}% > 90%")
    else:
        print(f"\n❌ HYPOTHESIS REFUTED: {avg_fidelity_low_error:.1f}% ≤ 90%")
    
    return result


async def test_biology_hypothesis():
    """Test a biology hypothesis using sequence analysis."""
    print("\n" + "="*70)
    print("🧬 TEST 4: BIOLOGY HYPOTHESIS")
    print("="*70)
    
    hypothesis = "GC-rich promoter regions (>60% GC) have different structural properties than AT-rich regions"
    
    adapter = ScientificToolAdapter()
    
    # Sample promoter-like sequences
    gc_rich_sequences = [
        "GCCGCGCGGCGCCGCGCGGCGCCGCGCGGCGCCGCGCGGC",  # 87.5% GC
        "CGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCGCG",  # 100% GC
        "GCGCGCATGCGCGCATGCGCGCATGCGCGCATGCGCGCAT",  # 70% GC
    ]
    
    at_rich_sequences = [
        "ATATATATATATATATATATATATATATATATATATAT",  # 0% GC
        "AATTAATTAATTAATTAATTAATTAATTAATTAATTAA",  # 0% GC
        "TATAATATAATATAATATAATATAATATAATATAATATA",  # 10% GC
    ]
    
    print(f"\nHypothesis: {hypothesis}")
    print(f"\nAnalyzing sequences...")
    
    gc_contents_gc_rich = []
    gc_contents_at_rich = []
    
    for seq in gc_rich_sequences:
        result = await adapter.execute_tool("sequence_analysis", {"sequence": seq, "type": "dna"})
        if result.get("success"):
            gc_contents_gc_rich.append(result["gc_content"])
            print(f"  GC-rich: GC content = {result['gc_content']:.1f}%")
    
    for seq in at_rich_sequences:
        result = await adapter.execute_tool("sequence_analysis", {"sequence": seq, "type": "dna"})
        if result.get("success"):
            gc_contents_at_rich.append(result["gc_content"])
            print(f"  AT-rich: GC content = {result['gc_content']:.1f}%")
    
    # Statistical comparison
    tests = [
        {
            "name": "GC Content Comparison",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": gc_contents_gc_rich,
                "data2": gc_contents_at_rich
            },
            "description": "Compare GC content between groups",
            "null_hypothesis": "No difference in GC content between groups",
            "alternative_hypothesis": "Groups have different GC content"
        }
    ]
    
    validator = AdvancedHypothesisValidator(alpha=0.1)
    result = await validator.validate_hypothesis(hypothesis, "biology", tests)
    
    print(f"\n📊 RESULTS:")
    print(f"  Mean GC content (GC-rich): {np.mean(gc_contents_gc_rich):.1f}%")
    print(f"  Mean GC content (AT-rich): {np.mean(gc_contents_at_rich):.1f}%")
    print(f"  P-value: {result.combined_p_value:.4e}" if result.combined_p_value else "  P-value: N/A")
    print(f"  Status: {result.status.value.upper()}")
    print(f"\n💡 Conclusion: {result.conclusion}")
    
    return result


async def run_all_tests():
    """Run all hypothesis tests and summarize results."""
    print("\n" + "="*70)
    print("🔬 ADVANCED HYPOTHESIS VALIDATOR - COMPREHENSIVE TEST SUITE")
    print("   Combining POPPER, ToolUniverse, and AXIOM methodologies")
    print("="*70)
    
    results = {}
    
    # Run all tests
    try:
        results["chemistry"] = await test_chemistry_hypothesis()
    except Exception as e:
        print(f"❌ Chemistry test failed: {e}")
        results["chemistry"] = None
    
    try:
        results["materials"] = await test_materials_hypothesis()
    except Exception as e:
        print(f"❌ Materials test failed: {e}")
        results["materials"] = None
    
    try:
        results["quantum"] = await test_quantum_hypothesis()
    except Exception as e:
        print(f"❌ Quantum test failed: {e}")
        results["quantum"] = None
    
    try:
        results["biology"] = await test_biology_hypothesis()
    except Exception as e:
        print(f"❌ Biology test failed: {e}")
        results["biology"] = None
    
    # Summary
    print("\n" + "="*70)
    print("📋 SUMMARY")
    print("="*70)
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "tests_run": 4,
        "results": {}
    }
    
    for domain, result in results.items():
        if result:
            status = result.status.value
            print(f"  {domain.upper()}: {status}")
            summary["results"][domain] = {
                "status": status,
                "confidence": result.confidence,
                "p_value": result.combined_p_value,
                "e_value": result.combined_e_value
            }
        else:
            print(f"  {domain.upper()}: FAILED")
            summary["results"][domain] = {"status": "error"}
    
    # Save results
    output_file = f"/Volumes/Ganador disk/atlas/advanced_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Count validated vs refuted
    validated = sum(1 for r in results.values() if r and r.status.value == "validated")
    refuted = sum(1 for r in results.values() if r and r.status.value == "refuted")
    insufficient = sum(1 for r in results.values() if r and r.status.value == "insufficient_evidence")
    
    print(f"\n📊 FINAL STATISTICS:")
    print(f"  ✅ Validated: {validated}")
    print(f"  ❌ Refuted: {refuted}")
    print(f"  ⚠️ Insufficient evidence: {insufficient}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
