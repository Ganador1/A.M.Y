#!/usr/bin/env python3
"""
Test Extended Hypothesis Bridges

Validates all 5 new expansion features:
1. Quantum Chemistry Bridge (DFT calculations)
2. ToolUniverse Integration (Ensembl, PubChem, ClinVar)
3. ChemCrow Synthesis Bridge (reaction prediction)
4. POPPER Physics Adapter (quantum/particle data)
5. Auto-Publication Pipeline (paper generation)

Run with:
    python test_extended_bridges.py
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np


async def test_quantum_chemistry_bridge():
    """Test 1: Quantum Chemistry Bridge."""
    print("\n" + "=" * 60)
    print("🔬 TEST 1: Quantum Chemistry Bridge")
    print("=" * 60)

    from app.services.extended_hypothesis_bridges import QuantumChemistryBridge

    bridge = QuantumChemistryBridge()

    # Test: Validate water molecule energy
    water_atoms = [
        ("O", (0.0, 0.0, 0.0)),
        ("H", (0.0, 0.757, 0.587)),
        ("H", (0.0, -0.757, 0.587)),
    ]

    # Expected energy for H2O at B3LYP/6-31G* is approximately -76.4 Hartree
    result = await bridge.validate_molecular_energy(
        atoms=water_atoms,
        expected_energy=-76.4,
        energy_sigma=0.1,
        method="b3lyp",
        basis="6-31g*",
    )

    print(f"  Hypothesis: H2O has energy ≈ -76.4 Hartree")
    print(f"  Service available: {result.get('metrics', {}).get('service_available', 'N/A')}")
    print(f"  Computed energy: {result.get('metrics', {}).get('computed_energy', 'N/A'):.4f} Hartree")
    print(f"  P-value: {result.get('p_value', 'N/A'):.4f}")
    print(f"  Status: {'✅ PASS' if result.get('success') else '❌ FAIL'}")

    return result.get("success", False) and result.get("p_value") is not None


async def test_tooluniverse_ensembl():
    """Test 2a: ToolUniverse Ensembl Integration."""
    print("\n" + "=" * 60)
    print("🧬 TEST 2a: ToolUniverse - Ensembl Gene Query")
    print("=" * 60)

    from app.services.extended_hypothesis_bridges import ToolUniverseWrapper

    wrapper = ToolUniverseWrapper()

    # Test: Validate BRCA1 is on chromosome 17
    result = await wrapper.query_ensembl_gene(
        gene_id="BRCA1",
        species="homo_sapiens",
        expected_chromosome="17",
    )

    if result.get("success"):
        gene_data = result.get("gene_data", {})
        print(f"  Hypothesis: BRCA1 is located on chromosome 17")
        print(f"  Gene ID: {gene_data.get('id')}")
        print(f"  Chromosome: {gene_data.get('chromosome')}")
        print(f"  P-value: {result.get('p_value', 'N/A'):.4f}")
        print(f"  Status: {'✅ PASS' if result['p_value'] > 0.5 else '❌ FAIL'}")
    else:
        print(f"  Error: {result.get('error')}")
        print(f"  Status: ⚠️ SKIPPED (API unavailable)")

    return result.get("success", False)


async def test_tooluniverse_pubchem():
    """Test 2b: ToolUniverse PubChem Integration."""
    print("\n" + "=" * 60)
    print("⚗️ TEST 2b: ToolUniverse - PubChem Compound Query")
    print("=" * 60)

    from app.services.extended_hypothesis_bridges import ToolUniverseWrapper

    wrapper = ToolUniverseWrapper()

    # Test: Validate aspirin molecular weight
    result = await wrapper.query_pubchem_compound(
        name="aspirin",
        expected_mw=180.16,  # Aspirin MW
        mw_tolerance=0.5,
    )

    if result.get("success"):
        compound_data = result.get("compound_data", {})
        print(f"  Hypothesis: Aspirin has MW ≈ 180.16 g/mol")
        print(f"  CID: {compound_data.get('cid')}")
        print(f"  Actual MW: {compound_data.get('molecular_weight')}")
        print(f"  Formula: {compound_data.get('molecular_formula')}")
        print(f"  P-value: {result.get('p_value', 'N/A'):.4f}")
        print(f"  Status: {'✅ PASS' if result['p_value'] > 0.5 else '❌ FAIL'}")
    else:
        print(f"  Error: {result.get('error')}")
        print(f"  Status: ⚠️ SKIPPED (API unavailable)")

    return result.get("success", False)


async def test_chemcrow_synthesis():
    """Test 3: ChemCrow Synthesis Bridge."""
    print("\n" + "=" * 60)
    print("🧪 TEST 3: ChemCrow Synthesis Route Validation")
    print("=" * 60)

    from app.services.extended_hypothesis_bridges import ChemCrowSynthesisBridge

    bridge = ChemCrowSynthesisBridge()

    # Test: Validate esterification reaction
    # Acetic acid + Ethanol → Ethyl acetate + Water
    result = await bridge.validate_reaction_product(
        reactants_smiles="CC(=O)O.CCO",  # Acetic acid + Ethanol
        expected_product_smiles="CCOC(C)=O",  # Ethyl acetate
        similarity_threshold=0.7,
    )

    if result.get("success"):
        metrics = result.get("metrics", {})
        print(f"  Hypothesis: Acetic acid + Ethanol → Ethyl acetate")
        print(f"  Predicted product: {metrics.get('predicted_product', 'N/A')}")
        print(f"  Expected product: {metrics.get('expected_product', 'N/A')}")
        print(f"  Tanimoto similarity: {metrics.get('tanimoto_similarity', 0):.4f}")
        print(f"  RXN4Chem used: {metrics.get('rxn4chem_used', False)}")
        print(f"  P-value: {result.get('p_value', 'N/A'):.4f}")
        print(f"  Status: {'✅ PASS' if result['p_value'] > 0.5 else '⚠️ PARTIAL'}")
    else:
        print(f"  Error: {result.get('error')}")
        print(f"  Status: ❌ FAIL")

    return result.get("success", False)


async def test_popper_physics():
    """Test 4: POPPER Physics Adapter."""
    print("\n" + "=" * 60)
    print("⚛️ TEST 4: POPPER Physics - Quantum Measurement Validation")
    print("=" * 60)

    from app.services.extended_hypothesis_bridges import POPPERPhysicsAdapter

    adapter = POPPERPhysicsAdapter()

    # Test: Validate that quantum measurements follow normal distribution
    np.random.seed(42)
    measurements = np.random.normal(loc=0, scale=1, size=200).tolist()

    result = await adapter.validate_quantum_hypothesis(
        hypothesis="Quantum position measurements follow a normal distribution",
        measurement_data={"observed": measurements},
        expected_distribution="normal",
        alpha=0.1,
    )

    if result.get("success"):
        metrics = result.get("metrics", {})
        tests = result.get("tests_run", [])
        print(f"  Hypothesis: Position measurements ~ N(0,1)")
        print(f"  N observations: {metrics.get('num_observations')}")
        print(f"  Mean: {metrics.get('mean', 0):.4f}")
        print(f"  Std: {metrics.get('std', 0):.4f}")
        print(f"  Tests run: {len(tests)}")
        for t in tests:
            print(f"    - {t['test_name']}: p={t['p_value']:.4f}")
        print(f"  Combined P-value: {result.get('p_value', 'N/A'):.4f}")
        print(f"  Status: {result.get('status', 'N/A').upper()}")
        print(f"  Result: {'✅ PASS' if result['status'] == 'validated' else '⚠️ CHECK'}")
    else:
        print(f"  Error: {result.get('error')}")
        print(f"  Status: ❌ FAIL")

    return result.get("success", False)


async def test_particle_physics():
    """Test 4b: POPPER Physics - Particle Resonance."""
    print("\n" + "=" * 60)
    print("🔭 TEST 4b: POPPER Physics - Particle Resonance Detection")
    print("=" * 60)

    from app.services.extended_hypothesis_bridges import POPPERPhysicsAdapter

    adapter = POPPERPhysicsAdapter()

    # Simulate Higgs-like resonance data
    np.random.seed(42)
    background = np.random.uniform(100, 150, size=800)
    signal = np.random.normal(loc=125, scale=2, size=50)  # Higgs at 125 GeV
    masses = np.concatenate([background, signal]).tolist()

    result = await adapter.validate_particle_physics_data(
        event_data={"invariant_mass": masses},
        expected_mass=125.0,  # Higgs mass
        mass_resolution=2.0,
        background_rate=0.8,
    )

    if result.get("success"):
        metrics = result.get("metrics", {})
        print(f"  Hypothesis: Resonance exists at 125 GeV")
        print(f"  Signal events: {metrics.get('signal_events')}")
        print(f"  Expected background: {metrics.get('expected_background', 0):.1f}")
        print(f"  Significance: {metrics.get('significance_sigma', 0):.2f}σ")
        print(f"  P-value: {result.get('p_value', 'N/A'):.4e}")
        print(f"  Conclusion: {result.get('conclusion', 'N/A')}")
        print(f"  Status: {'✅ PASS' if metrics.get('significance_sigma', 0) > 2 else '⚠️ CHECK'}")
    else:
        print(f"  Error: {result.get('error')}")
        print(f"  Status: ❌ FAIL")

    return result.get("success", False)


async def test_auto_publication_pipeline():
    """Test 5: Auto-Publication Pipeline."""
    print("\n" + "=" * 60)
    print("📝 TEST 5: Auto-Publication Pipeline")
    print("=" * 60)

    from app.services.extended_hypothesis_bridges import AutoPublicationPipeline

    pipeline = AutoPublicationPipeline(target_journal="plos_one")

    # Create a mock validation result
    validation_result = {
        "hypothesis": "Graphene-polymer composites enhance thermal conductivity",
        "status": "validated",
        "combined_p_value": 0.78,
        "combined_e_value": 2.5,
        "tests_run": [
            {
                "test_name": "Thermal conductivity measurement",
                "p_value": 0.85,
                "tool_used": "thermal_conductivity",
                "is_significant": False,
            },
            {
                "test_name": "Maxwell-Garnett model validation",
                "p_value": 0.72,
                "tool_used": "statistical_tests",
                "is_significant": False,
            },
        ],
        "reasoning": "Ran 2 falsification tests. None showed significant refutation.",
        "conclusion": "The hypothesis is supported by experimental evidence.",
    }

    # Generate publication draft
    draft = await pipeline.generate_publication_from_validation(validation_result)

    print(f"  Title: {draft.title[:60]}...")
    print(f"  Abstract: {len(draft.abstract)} chars")
    print(f"  Sections: {len([s for s in [draft.introduction, draft.methods, draft.results, draft.discussion, draft.conclusion] if s])}")
    print(f"  References: {len(draft.references)}")

    # Format for journal
    formatted = await pipeline.format_for_journal(draft, "plos_one")

    print(f"  Target journal: {formatted.get('journal')}")
    print(f"  Format: {formatted.get('format')}")
    print(f"  Content length: {len(formatted.get('content', ''))}")
    print(f"  Status: {'✅ PASS' if formatted.get('success') else '❌ FAIL'}")

    # Show sample of generated content
    print("\n  --- Sample Generated Abstract ---")
    print(f"  {draft.abstract[:300]}...")

    return formatted.get("success", False)


async def test_integrated_validation():
    """Test 6: Integrated Validation with Extended Bridges."""
    print("\n" + "=" * 60)
    print("🔗 TEST 6: Integrated Validation via AdvancedHypothesisValidator")
    print("=" * 60)

    from app.services.advanced_hypothesis_validator import AdvancedHypothesisValidator

    validator = AdvancedHypothesisValidator(alpha=0.1, max_tests=5)

    # Test with multiple extended bridges
    test_specs = [
        {
            "name": "Quantum Chemistry: Water Energy",
            "tool": "axiom_quantum_chemistry",
            "parameters": {
                "atoms": [
                    ("O", (0.0, 0.0, 0.0)),
                    ("H", (0.0, 0.757, 0.587)),
                    ("H", (0.0, -0.757, 0.587)),
                ],
                "expected_energy": -76.4,
            },
            "null_hypothesis": "Water energy differs from -76.4 Hartree",
            "alternative_hypothesis": "Water energy ≈ -76.4 Hartree",
        },
        {
            "name": "POPPER Physics: Measurement Distribution",
            "tool": "popper_physics",
            "parameters": {
                "hypothesis": "Measurements follow normal distribution",
                "measurement_data": {"observed": np.random.normal(0, 1, 100).tolist()},
            },
            "null_hypothesis": "Measurements are non-normal",
            "alternative_hypothesis": "Measurements are normally distributed",
        },
        {
            "name": "ChemCrow: Esterification Reaction",
            "tool": "chemcrow_synthesis",
            "parameters": {
                "reactants_smiles": "CC(=O)O.CCO",
                "expected_product": "CCOC(C)=O",
            },
            "null_hypothesis": "Reaction does not produce ethyl acetate",
            "alternative_hypothesis": "Reaction produces ethyl acetate",
        },
    ]

    result = await validator.validate_hypothesis(
        hypothesis="Multi-domain scientific validation demonstrates integrated tool ecosystem",
        domain="multidisciplinary",
        test_specifications=test_specs,
    )

    print(f"  Hypothesis: {result.hypothesis[:60]}...")
    print(f"  Tests run: {len(result.tests_run)}")
    for t in result.tests_run:
        status = "✓" if t.p_value and t.p_value > 0.3 else "✗"
        p_str = f"{t.p_value:.4f}" if t.p_value else "N/A"
        print(f"    [{status}] {t.test_name}: p={p_str}")
    print(f"  Combined P-value: {result.combined_p_value:.4f}" if result.combined_p_value else "  Combined P-value: N/A")
    print(f"  Status: {result.status.value.upper()}")
    print(f"  Confidence: {result.confidence:.2%}")
    print(f"  Conclusion: {result.conclusion[:100]}...")
    print(f"  Result: {'✅ PASS' if result.status.value in ['validated', 'insufficient_evidence'] else '⚠️ CHECK'}")

    return len(result.tests_run) >= 2


async def test_full_pipeline():
    """Test 7: Complete Pipeline from Validation to Publication."""
    print("\n" + "=" * 60)
    print("🚀 TEST 7: Complete Pipeline (Validation → Publication)")
    print("=" * 60)

    from app.services.advanced_hypothesis_validator import AdvancedHypothesisValidator
    from app.services.extended_hypothesis_bridges import AutoPublicationPipeline

    # Step 1: Validate hypothesis
    validator = AdvancedHypothesisValidator(alpha=0.1, max_tests=3)

    test_specs = [
        {
            "name": "Statistical Analysis",
            "tool": "statistical_tests",
            "parameters": {
                "test_type": "ttest",
                "data1": np.random.normal(10, 2, 50).tolist(),
                "data2": np.random.normal(10.5, 2, 50).tolist(),
            },
        },
        {
            "name": "Physics Validation",
            "tool": "popper_physics",
            "parameters": {
                "hypothesis": "Data follows expected distribution",
                "measurement_data": {"observed": np.random.normal(0, 1, 100).tolist()},
            },
        },
    ]

    validation_result = await validator.validate_hypothesis(
        hypothesis="Novel treatment shows statistically significant improvement",
        domain="medicine",
        test_specifications=test_specs,
    )

    print(f"  Step 1 - Validation: {validation_result.status.value}")

    # Step 2: Generate publication
    pipeline = AutoPublicationPipeline(target_journal="nature")
    draft = await pipeline.generate_publication_from_validation(validation_result.to_dict())

    print(f"  Step 2 - Draft generated: {len(draft.title)} char title")

    # Step 3: Format for journal
    formatted = await pipeline.format_for_journal(draft, "nature")

    print(f"  Step 3 - Formatted for: {formatted.get('journal')}")
    print(f"  Content length: {len(formatted.get('content', ''))} chars")
    print(f"  Pipeline Status: {'✅ COMPLETE' if formatted.get('success') else '❌ FAILED'}")

    return formatted.get("success", False)


async def main():
    """Run all extended bridge tests."""
    print("=" * 60)
    print("🧪 AXIOM ATLAS - Extended Hypothesis Bridges Test Suite")
    print("=" * 60)
    print("Testing all 5 expansion features + integration...")

    results = {}

    # Run all tests
    tests = [
        ("Quantum Chemistry Bridge", test_quantum_chemistry_bridge),
        ("ToolUniverse Ensembl", test_tooluniverse_ensembl),
        ("ToolUniverse PubChem", test_tooluniverse_pubchem),
        ("ChemCrow Synthesis", test_chemcrow_synthesis),
        ("POPPER Quantum Physics", test_popper_physics),
        ("POPPER Particle Physics", test_particle_physics),
        ("Auto-Publication Pipeline", test_auto_publication_pipeline),
        ("Integrated Validation", test_integrated_validation),
        ("Full Pipeline", test_full_pipeline),
    ]

    for name, test_func in tests:
        try:
            results[name] = await test_func()
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            results[name] = False

    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")

    print("=" * 60)
    print(f"  TOTAL: {passed}/{total} tests passed")
    print("=" * 60)

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
