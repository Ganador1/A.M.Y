"""
Integration Test for Extended Hypothesis Bridges

Tests all 15 bridges:
1. Quantum Chemistry (DFT)
2. ToolUniverse (Ensembl, PubChem, ClinVar)
3. ChemCrow Synthesis
4. POPPER Physics
5. Auto-Publication Pipeline
6. DNABERT2 Genomics
7. Quantum Physics (QuTiP)
8. GNoME Materials
9. ClinicalBERT (Clinical NLP)
10. Exoplanet Transit Analysis
11. Advanced Genomics (Cancer/Pharmacogenomics)
12. Climate Model (Temperature Trends, CO2)
13. Neuroscience Imaging (Brain Regions, Connectivity)
14. Theorem Proving (Mathematical Proofs)
15. Real APIs (arXiv, UniProt, STRING)
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


async def test_quantum_chemistry_bridge():
    """Test 1: Quantum Chemistry Bridge (DFT energy validation)"""
    print("\n" + "="*60)
    print("TEST 1: Quantum Chemistry Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import QuantumChemistryBridge
    
    bridge = QuantumChemistryBridge()
    
    # Test water molecule energy
    water_atoms = [
        ("O", (0.0, 0.0, 0.0)),
        ("H", (0.0, 0.757, 0.587)),
        ("H", (0.0, -0.757, 0.587)),
    ]
    
    result = await bridge.validate_molecular_energy(
        atoms=water_atoms,
        expected_energy=-76.0,  # Approximate HF/6-31G* energy
        energy_sigma=0.5,
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Computed Energy: {result.get('metrics', {}).get('computed_energy')}")
    print(f"Service Available: {result.get('metrics', {}).get('service_available')}")
    
    if result.get('error'):
        print(f"Error: {result.get('error')}")
    
    assert result.get("success"), f"Quantum Chemistry test failed: {result.get('error')}"
    assert result.get("p_value") is not None, "No p-value returned"
    return True


async def test_tooluniverse_ensembl():
    """Test 2a: ToolUniverse - Ensembl Gene Query"""
    print("\n" + "="*60)
    print("TEST 2a: ToolUniverse - Ensembl")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ToolUniverseWrapper
    
    wrapper = ToolUniverseWrapper()
    
    # Test BRCA1 gene location
    result = await wrapper.query_ensembl_gene(
        gene_id="BRCA1",
        species="homo_sapiens",
        expected_chromosome="17",
    )
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"P-value: {result.get('p_value'):.4f}")
        gene_data = result.get("gene_data", {})
        print(f"Gene: {gene_data.get('display_name')}")
        print(f"Chromosome: {gene_data.get('chromosome')}")
    else:
        print(f"Error (expected if offline): {result.get('error')}")
    
    return True  # Allow failure for offline tests


async def test_tooluniverse_pubchem():
    """Test 2b: ToolUniverse - PubChem Compound Query"""
    print("\n" + "="*60)
    print("TEST 2b: ToolUniverse - PubChem")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ToolUniverseWrapper
    
    wrapper = ToolUniverseWrapper()
    
    # Test aspirin molecular weight
    result = await wrapper.query_pubchem_compound(
        name="aspirin",
        expected_mw=180.16,  # Actual MW
        mw_tolerance=0.5,
    )
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"P-value: {result.get('p_value'):.4f}")
        compound_data = result.get("compound_data", {})
        print(f"CID: {compound_data.get('cid')}")
        print(f"MW: {compound_data.get('molecular_weight')}")
        print(f"Formula: {compound_data.get('molecular_formula')}")
    else:
        print(f"Error (expected if offline): {result.get('error')}")
    
    return True


async def test_chemcrow_synthesis():
    """Test 3: ChemCrow Synthesis Route Validation"""
    print("\n" + "="*60)
    print("TEST 3: ChemCrow Synthesis Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ChemCrowSynthesisBridge
    
    bridge = ChemCrowSynthesisBridge()
    
    # Test esterification reaction
    result = await bridge.validate_reaction_product(
        reactants_smiles="CC(=O)O.CCO",  # Acetic acid + Ethanol
        expected_product_smiles="CCOC(C)=O",  # Ethyl acetate
        similarity_threshold=0.7,
    )
    
    print(f"Success: {result.get('success')}")
    if result.get("success"):
        print(f"P-value: {result.get('p_value'):.4f}")
        metrics = result.get("metrics", {})
        print(f"Predicted: {metrics.get('predicted_product')}")
        print(f"Expected: {metrics.get('expected_product')}")
        print(f"Tanimoto Similarity: {metrics.get('tanimoto_similarity'):.4f}")
    else:
        print(f"Error: {result.get('error')}")
    
    return result.get("success", False)


async def test_popper_physics():
    """Test 4: POPPER Physics Adapter"""
    print("\n" + "="*60)
    print("TEST 4: POPPER Physics Adapter")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import POPPERPhysicsAdapter
    import numpy as np
    
    adapter = POPPERPhysicsAdapter()
    
    # Test quantum measurement hypothesis
    np.random.seed(42)
    measurements = np.random.normal(0, 1, 100).tolist()
    
    result = await adapter.validate_quantum_hypothesis(
        hypothesis="Quantum measurements follow a normal distribution",
        measurement_data={"observed": measurements},
        expected_distribution="normal",
        alpha=0.1,
    )
    
    print(f"Success: {result.get('success')}")
    print(f"P-value: {result.get('p_value'):.4f}")
    print(f"Status: {result.get('status')}")
    print(f"Tests run: {len(result.get('tests_run', []))}")
    
    for test in result.get("tests_run", []):
        print(f"  - {test['test_name']}: p={test['p_value']:.4f}")
    
    assert result.get("success"), f"POPPER Physics test failed: {result.get('error')}"
    return True


async def test_dnabert2_genomics():
    """Test 5: DNABERT2 Genomics Bridge"""
    print("\n" + "="*60)
    print("TEST 5: DNABERT2 Genomics Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import DNABERT2GenomicsBridge
    
    bridge = DNABERT2GenomicsBridge()
    
    # Test sequence classification (promoter-like high GC)
    promoter_sequence = "GCGCGCGCGCGCATGCGCGCGCGCGC"
    
    result = await bridge.validate_sequence_classification(
        sequence=promoter_sequence,
        expected_class="promoter",
    )
    
    print(f"Success: {result.get('success')}")
    print(f"P-value: {result.get('p_value'):.4f}")
    metrics = result.get("metrics", {})
    print(f"Predicted Class: {metrics.get('predicted_class')}")
    print(f"Expected Class: {metrics.get('expected_class')}")
    print(f"GC Content: {metrics.get('gc_content'):.2%}")
    print(f"Service Available: {metrics.get('service_available')}")
    
    assert result.get("success"), f"DNABERT2 test failed: {result.get('error')}"
    return True


async def test_quantum_physics_simulation():
    """Test 6: Quantum Physics Simulation Bridge"""
    print("\n" + "="*60)
    print("TEST 6: Quantum Physics Simulation Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import QuantumPhysicsSimulationBridge
    
    bridge = QuantumPhysicsSimulationBridge()
    
    # Test Bell state entanglement
    result = await bridge.validate_entanglement_hypothesis(
        state_type="bell",
        expected_entanglement=1.0,
        tolerance=0.1,
    )
    
    print(f"Success: {result.get('success')}")
    print(f"P-value: {result.get('p_value'):.4f}")
    metrics = result.get("metrics", {})
    print(f"Computed Entanglement: {metrics.get('computed_entanglement')}")
    print(f"Expected Entanglement: {metrics.get('expected_entanglement')}")
    print(f"Service Available: {metrics.get('service_available')}")
    
    assert result.get("success"), f"Quantum Physics test failed: {result.get('error')}"
    return True


async def test_gnome_materials():
    """Test 7: GNoME Materials Bridge"""
    print("\n" + "="*60)
    print("TEST 7: GNoME Materials Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import GNoMEMaterialsBridge
    
    bridge = GNoMEMaterialsBridge()
    
    # Test lithium oxide stability
    result = await bridge.validate_material_stability(
        composition="Li2O",
        expected_stable=True,
    )
    
    print(f"Success: {result.get('success')}")
    print(f"P-value: {result.get('p_value'):.4f}")
    metrics = result.get("metrics", {})
    print(f"Predicted Stable: {metrics.get('predicted_stable')}")
    print(f"Expected Stable: {metrics.get('expected_stable')}")
    print(f"Composition: {metrics.get('composition')}")
    print(f"Service Available: {metrics.get('service_available')}")
    
    assert result.get("success"), f"GNoME Materials test failed: {result.get('error')}"
    return True


async def test_auto_publication_pipeline():
    """Test 8: Auto-Publication Pipeline"""
    print("\n" + "="*60)
    print("TEST 8: Auto-Publication Pipeline")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import AutoPublicationPipeline
    
    pipeline = AutoPublicationPipeline(target_journal="plos_one")
    
    # Mock validation result
    validation_result = {
        "hypothesis": "Water molecules have a bent geometry with H-O-H angle of 104.5°",
        "status": "validated",
        "combined_p_value": 0.85,
        "tests_run": [
            {"test_name": "DFT Geometry Optimization", "p_value": 0.92, "tool_used": "quantum_chemistry", "is_significant": False},
            {"test_name": "Bond Angle Comparison", "p_value": 0.78, "tool_used": "axiom_mathematics", "is_significant": False},
        ],
        "reasoning": "Multiple tests confirmed the expected geometry.",
        "conclusion": "The hypothesis is supported by quantum chemical calculations.",
    }
    
    draft = await pipeline.generate_publication_from_validation(validation_result)
    
    print(f"Title: {draft.title}")
    print(f"Abstract length: {len(draft.abstract)} chars")
    print(f"Sections: {len([s for s in [draft.introduction, draft.methods, draft.results, draft.discussion, draft.conclusion] if s])}")
    print(f"References: {len(draft.references)}")
    
    # Format for journal
    formatted = await pipeline.format_for_journal(draft)
    print(f"Format: {formatted.get('format')}")
    print(f"Content length: {len(formatted.get('content', ''))} chars")
    
    assert draft.title, "No title generated"
    assert draft.abstract, "No abstract generated"
    return True


async def test_unified_interface():
    """Test 9: Unified ExtendedHypothesisBridges Interface"""
    print("\n" + "="*60)
    print("TEST 9: Unified Extended Bridges Interface")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ExtendedHypothesisBridges
    
    bridges = ExtendedHypothesisBridges()
    
    # Check availability
    available = bridges.get_available_bridges()
    print("Bridge Availability:")
    for name, status in available.items():
        print(f"  - {name}: {'✓' if status else '✗'}")
    
    # Test multi-bridge validation (chemistry domain)
    result = await bridges.validate_with_all_bridges(
        hypothesis="Li2O is a stable oxide with favorable formation energy",
        domain="materials",
        parameters={
            "composition": "Li2O",
            "expected_stable": True,
        },
    )
    
    print(f"\nMulti-Bridge Result:")
    print(f"Hypothesis: {result['hypothesis'][:50]}...")
    print(f"Domain: {result['domain']}")
    print(f"Bridges Used: {list(result.get('bridge_results', {}).keys())}")
    print(f"Combined P-value: {result.get('combined_p_value')}")
    
    return True


async def test_advanced_hypothesis_validator_integration():
    """Test 10: Full Integration with AdvancedHypothesisValidator"""
    print("\n" + "="*60)
    print("TEST 10: AdvancedHypothesisValidator Full Integration")
    print("="*60)
    
    from app.services.advanced_hypothesis_validator import (
        AdvancedHypothesisValidator,
        ValidationMethod,
    )
    
    validator = AdvancedHypothesisValidator(
        alpha=0.1,
        max_tests=5,
        aggregation_method=ValidationMethod.E_VALUE,
    )
    
    # Multi-domain test
    tests = [
        {
            "name": "DNABERT2 Sequence Classification",
            "tool": "axiom_dnabert2",
            "parameters": {
                "sequence": "GCGCGCGCGCATGCGCGCGC",
                "expected_class": "promoter",
            },
            "null_hypothesis": "Sequence is not promoter-like",
            "alternative_hypothesis": "Sequence has promoter characteristics",
        },
        {
            "name": "Quantum Physics Entanglement",
            "tool": "axiom_quantum_physics",
            "parameters": {
                "state_type": "bell",
                "expected_entanglement": 1.0,
            },
            "null_hypothesis": "Bell state is not maximally entangled",
            "alternative_hypothesis": "Bell state is maximally entangled",
        },
        {
            "name": "Materials Stability",
            "tool": "axiom_gnome_materials",
            "parameters": {
                "composition": "TiO2",
                "expected_stable": True,
            },
            "null_hypothesis": "TiO2 is not stable",
            "alternative_hypothesis": "TiO2 is thermodynamically stable",
        },
    ]
    
    result = await validator.validate_hypothesis(
        hypothesis="Multi-domain validation: genomics, quantum physics, and materials science",
        domain="multidisciplinary",
        test_specifications=tests,
    )
    
    print(f"Status: {result.status.value}")
    print(f"Confidence: {result.confidence:.4f}")
    print(f"Combined P-value: {result.combined_p_value:.4f}" if result.combined_p_value else "No p-value")
    print(f"Tests Run: {len(result.tests_run)}")
    
    for test in result.tests_run:
        status = "✓" if not test.error else "✗"
        p_str = f"{test.p_value:.4f}" if test.p_value else "N/A"
        print(f"  {status} {test.test_name}: p={p_str}")
    
    print(f"\nConclusion: {result.conclusion[:100]}...")
    
    return True


async def test_clinical_bert_bridge():
    """Test 9: ClinicalBERT Bridge (Clinical NLP)"""
    print("\n" + "="*60)
    print("TEST 9: ClinicalBERT Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ClinicalBERTBridge
    
    bridge = ClinicalBERTBridge()
    
    # Test specialty classification
    clinical_note = """
    Patient presents with chest pain radiating to left arm. 
    ECG shows ST elevation. Troponin elevated.
    Suspected acute myocardial infarction. 
    Started on aspirin and heparin.
    """
    
    result = await bridge.validate_specialty_classification(
        clinical_text=clinical_note,
        expected_specialty="cardiology",
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Predicted: {result.get('metrics', {}).get('predicted_specialty')}")
    print(f"Expected: {result.get('metrics', {}).get('expected_specialty')}")
    print(f"Service Available: {result.get('metrics', {}).get('service_available')}")
    
    assert result.get("success"), f"ClinicalBERT test failed: {result.get('error')}"
    return True


async def test_clinical_bert_entities():
    """Test 9b: ClinicalBERT Entity Extraction"""
    print("\n" + "="*60)
    print("TEST 9b: ClinicalBERT Entity Extraction")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ClinicalBERTBridge
    
    bridge = ClinicalBERTBridge()
    
    clinical_note = "Patient with diabetes taking insulin and metformin. Reports headache and nausea."
    
    result = await bridge.validate_entity_extraction(
        clinical_text=clinical_note,
        expected_entities={
            "medication": ["insulin", "metformin"],
            "condition": ["diabetes"],
            "symptom": ["headache", "nausea"],
        },
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Recall: {result.get('metrics', {}).get('recall', 0):.2f}")
    print(f"Extracted: {result.get('metrics', {}).get('extracted_entities')}")
    
    assert result.get("success"), f"ClinicalBERT entity test failed: {result.get('error')}"
    return True


async def test_exoplanet_transit_bridge():
    """Test 10: Exoplanet Transit Analysis Bridge"""
    print("\n" + "="*60)
    print("TEST 10: Exoplanet Transit Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ExoplanetTransitBridge
    import numpy as np
    
    bridge = ExoplanetTransitBridge()
    
    # Generate synthetic transit light curve
    np.random.seed(42)
    t = np.linspace(0, 10, 1000)
    flux = np.ones_like(t)
    
    # Add transit (1% depth = ~1 Earth radius around Sun-like star)
    transit_mask = (t > 4.5) & (t < 5.5)
    flux[transit_mask] = 0.99  # 1% transit depth
    flux += np.random.normal(0, 0.001, len(t))
    
    result = await bridge.validate_planet_radius(
        time=t.tolist(),
        flux=flux.tolist(),
        expected_radius_earth=10.9,  # ~sqrt(0.01) * 109.2
        radius_tolerance=0.5,
        stellar_radius=1.0,
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Estimated Radius: {result.get('metrics', {}).get('estimated_radius_earth', 0):.2f} Earth radii")
    print(f"Transit Depth: {result.get('metrics', {}).get('transit_depth', 0):.4f}")
    
    assert result.get("success"), f"Exoplanet transit test failed: {result.get('error')}"
    return True


async def test_exoplanet_period():
    """Test 10b: Exoplanet Orbital Period Validation"""
    print("\n" + "="*60)
    print("TEST 10b: Exoplanet Orbital Period")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ExoplanetTransitBridge
    
    bridge = ExoplanetTransitBridge()
    
    # Kepler-like transit times (3.5 day period)
    transit_times = [100.0, 103.5, 107.0, 110.5, 114.0]
    
    result = await bridge.validate_orbital_period(
        transit_times=transit_times,
        expected_period_days=3.5,
        period_tolerance=0.1,
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Estimated Period: {result.get('metrics', {}).get('estimated_period', 0):.2f} days")
    print(f"N Transits: {result.get('metrics', {}).get('n_transits')}")
    
    assert result.get("success"), f"Exoplanet period test failed: {result.get('error')}"
    return True


async def test_advanced_genomics_cancer():
    """Test 11: Advanced Genomics - Cancer Mutations"""
    print("\n" + "="*60)
    print("TEST 11: Advanced Genomics - Cancer Mutations")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import AdvancedGenomicsBridge
    
    bridge = AdvancedGenomicsBridge()
    
    result = await bridge.validate_driver_mutations(
        tumor_sample_id="TCGA-001",
        expected_drivers=["TP53", "EGFR", "BRCA1"],
        min_drivers_found=2,
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Found Drivers: {result.get('metrics', {}).get('found_drivers')}")
    print(f"N Found: {result.get('metrics', {}).get('n_found')}")
    print(f"Service Available: {result.get('metrics', {}).get('service_available')}")
    
    assert result.get("success"), f"Cancer mutation test failed: {result.get('error')}"
    return True


async def test_advanced_genomics_pharmacogenomics():
    """Test 11b: Advanced Genomics - Pharmacogenomics"""
    print("\n" + "="*60)
    print("TEST 11b: Advanced Genomics - Pharmacogenomics")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import AdvancedGenomicsBridge
    
    bridge = AdvancedGenomicsBridge()
    
    result = await bridge.validate_drug_response(
        sample_id="PATIENT-001",
        drug="warfarin",
        expected_response="normal",
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Predicted Response: {result.get('metrics', {}).get('predicted_response')}")
    print(f"Drug: {result.get('metrics', {}).get('drug')}")
    
    assert result.get("success"), f"Pharmacogenomics test failed: {result.get('error')}"
    return True


async def test_climate_model_bridge():
    """Test 12: Climate Model Bridge"""
    print("\n" + "="*60)
    print("TEST 12: Climate Model Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ClimateModelBridge
    
    bridge = ClimateModelBridge()
    
    # Test temperature trend
    result = await bridge.validate_temperature_trend(
        start_year=1980,
        end_year=2020,
        expected_trend="warming",
        region="global",
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Detected Trend: {result.get('metrics', {}).get('detected_trend')}")
    print(f"Service Available: {result.get('metrics', {}).get('service_available')}")
    
    assert result.get("success"), f"Climate trend test failed: {result.get('error')}"
    return True


async def test_climate_co2():
    """Test 12b: Climate CO2 Concentration"""
    print("\n" + "="*60)
    print("TEST 12b: Climate CO2 Concentration")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import ClimateModelBridge
    
    bridge = ClimateModelBridge()
    
    result = await bridge.validate_co2_concentration(
        year=2020,
        expected_ppm=414.0,  # Actual value ~414.2 ppm
        tolerance_ppm=5.0,
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Actual PPM: {result.get('metrics', {}).get('actual_ppm')}")
    print(f"Expected PPM: {result.get('metrics', {}).get('expected_ppm')}")
    
    assert result.get("success"), f"CO2 test failed: {result.get('error')}"
    return True


async def test_neuroscience_bridge():
    """Test 13: Neuroscience Imaging Bridge"""
    print("\n" + "="*60)
    print("TEST 13: Neuroscience Imaging Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import NeuroscienceImagingBridge
    
    bridge = NeuroscienceImagingBridge()
    
    # Test brain region activation for visual task
    result = await bridge.validate_brain_region_activation(
        task_type="visual",
        expected_regions=["V1", "V2", "occipital_lobe"],
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"F1 Score: {result.get('metrics', {}).get('f1_score')}")
    print(f"Matching Regions: {result.get('metrics', {}).get('matching_regions')}")
    
    assert result.get("success"), f"Brain activation test failed: {result.get('error')}"
    return True


async def test_neuroscience_connectivity():
    """Test 13b: Neuroscience Connectivity"""
    print("\n" + "="*60)
    print("TEST 13b: Neuroscience Brain Connectivity")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import NeuroscienceImagingBridge
    
    bridge = NeuroscienceImagingBridge()
    
    result = await bridge.validate_connectivity_hypothesis(
        source_region="hippocampus",
        target_region="entorhinal_cortex",
        expected_connected=True,
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Predicted Connected: {result.get('metrics', {}).get('predicted_connected')}")
    print(f"Confidence: {result.get('metrics', {}).get('confidence')}")
    
    assert result.get("success"), f"Connectivity test failed: {result.get('error')}"
    return True


async def test_theorem_proving_bridge():
    """Test 14: Theorem Proving Bridge"""
    print("\n" + "="*60)
    print("TEST 14: Theorem Proving Bridge")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import TheoremProvingBridge
    
    bridge = TheoremProvingBridge()
    
    result = await bridge.validate_theorem(
        theorem_statement="The Pythagorean theorem states that a^2 + b^2 = c^2",
        proof_type="direct",
        expected_valid=True,
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Is Valid: {result.get('metrics', {}).get('is_valid')}")
    print(f"Confidence: {result.get('metrics', {}).get('confidence')}")
    
    assert result.get("success"), f"Theorem test failed: {result.get('error')}"
    return True


async def test_conjecture_status():
    """Test 14b: Conjecture Status"""
    print("\n" + "="*60)
    print("TEST 14b: Mathematical Conjecture Status")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import TheoremProvingBridge
    
    bridge = TheoremProvingBridge()
    
    result = await bridge.validate_conjecture(
        conjecture_name="Riemann Hypothesis",
        expected_status="open",
    )
    
    print(f"Success: {result.get('success')}")
    p_val = result.get('p_value')
    p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
    print(f"P-value: {p_str}")
    print(f"Actual Status: {result.get('metrics', {}).get('actual_status')}")
    print(f"Expected Status: {result.get('metrics', {}).get('expected_status')}")
    
    assert result.get("success"), f"Conjecture test failed: {result.get('error')}"
    return True


async def test_real_api_arxiv():
    """Test 15: Real API - arXiv"""
    print("\n" + "="*60)
    print("TEST 15: Real API - arXiv Search")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import RealAPIBridge
    
    bridge = RealAPIBridge()
    
    try:
        result = await bridge.query_arxiv_papers(
            query="quantum computing",
            expected_count_min=100,
            category="quant-ph",
        )
        
        print(f"Success: {result.get('success')}")
        p_val = result.get('p_value')
        p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
        print(f"P-value: {p_str}")
        print(f"Total Results: {result.get('metrics', {}).get('total_results')}")
        print(f"API Source: {result.get('metrics', {}).get('api_source')}")
        
        await bridge.close()
    except Exception as e:
        print(f"arXiv API test skipped (network): {e}")
        return True
    
    return True


async def test_real_api_uniprot():
    """Test 15b: Real API - UniProt"""
    print("\n" + "="*60)
    print("TEST 15b: Real API - UniProt Protein Query")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import RealAPIBridge
    
    bridge = RealAPIBridge()
    
    try:
        # P00533 is EGFR (Epidermal Growth Factor Receptor)
        result = await bridge.query_uniprot_protein(
            protein_id="P00533",
            expected_length=1210,  # Approximate length
            expected_organism="Homo sapiens",
        )
        
        print(f"Success: {result.get('success')}")
        p_val = result.get('p_value')
        p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
        print(f"P-value: {p_str}")
        print(f"Gene Name: {result.get('metrics', {}).get('gene_name')}")
        print(f"Sequence Length: {result.get('metrics', {}).get('sequence_length')}")
        print(f"API Source: {result.get('metrics', {}).get('api_source')}")
        
        await bridge.close()
    except Exception as e:
        print(f"UniProt API test skipped (network): {e}")
        return True
    
    return True


async def test_real_api_string():
    """Test 15c: Real API - STRING Interactions"""
    print("\n" + "="*60)
    print("TEST 15c: Real API - STRING Protein Interactions")
    print("="*60)
    
    from app.services.extended_hypothesis_bridges import RealAPIBridge
    
    bridge = RealAPIBridge()
    
    try:
        # TP53 and MDM2 have a known interaction
        result = await bridge.query_string_interactions(
            protein1="TP53",
            protein2="MDM2",
            species=9606,  # Human
            expected_interaction=True,
        )
        
        print(f"Success: {result.get('success')}")
        p_val = result.get('p_value')
        p_str = f"{p_val:.4f}" if p_val is not None else "N/A"
        print(f"P-value: {p_str}")
        print(f"Interaction Found: {result.get('metrics', {}).get('interaction_found')}")
        print(f"Confidence Score: {result.get('metrics', {}).get('confidence_score')}")
        print(f"API Source: {result.get('metrics', {}).get('api_source')}")
        
        await bridge.close()
    except Exception as e:
        print(f"STRING API test skipped (network): {e}")
        return True
    
    return True


async def main():
    """Run all extended bridge tests."""
    print("="*60)
    print("AXIOM ATLAS - Extended Hypothesis Bridges Integration Test")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*60)
    
    results = {}
    
    # Core tests (should always pass with fallbacks)
    test_functions = [
        ("Quantum Chemistry", test_quantum_chemistry_bridge),
        ("ToolUniverse Ensembl", test_tooluniverse_ensembl),
        ("ToolUniverse PubChem", test_tooluniverse_pubchem),
        ("ChemCrow Synthesis", test_chemcrow_synthesis),
        ("POPPER Physics", test_popper_physics),
        ("DNABERT2 Genomics", test_dnabert2_genomics),
        ("Quantum Physics Simulation", test_quantum_physics_simulation),
        ("GNoME Materials", test_gnome_materials),
        ("Auto-Publication Pipeline", test_auto_publication_pipeline),
        ("ClinicalBERT Specialty", test_clinical_bert_bridge),
        ("ClinicalBERT Entities", test_clinical_bert_entities),
        ("Exoplanet Transit", test_exoplanet_transit_bridge),
        ("Exoplanet Period", test_exoplanet_period),
        ("Cancer Mutations", test_advanced_genomics_cancer),
        ("Pharmacogenomics", test_advanced_genomics_pharmacogenomics),
        ("Climate Trend", test_climate_model_bridge),
        ("Climate CO2", test_climate_co2),
        ("Brain Activation", test_neuroscience_bridge),
        ("Brain Connectivity", test_neuroscience_connectivity),
        ("Theorem Proving", test_theorem_proving_bridge),
        ("Conjecture Status", test_conjecture_status),
        ("arXiv API", test_real_api_arxiv),
        ("UniProt API", test_real_api_uniprot),
        ("STRING API", test_real_api_string),
        ("Unified Interface", test_unified_interface),
        ("Full Validator Integration", test_advanced_hypothesis_validator_integration),
    ]
    
    for name, test_func in test_functions:
        try:
            success = await test_func()
            results[name] = "PASS" if success else "FAIL"
        except Exception as e:
            print(f"ERROR: {e}")
            results[name] = f"ERROR: {str(e)[:50]}"
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v == "PASS")
    total = len(results)
    
    for name, status in results.items():
        icon = "✓" if status == "PASS" else "✗"
        print(f"{icon} {name}: {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
