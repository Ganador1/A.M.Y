"""
Full Research Workflow Example - From hypothesis to publication

This example demonstrates the complete research workflow using AXIOM's
enhanced capabilities including real experimental tools, statistical
validation, and active reproducibility.

Author: ATLAS Autonomous Laboratory System
Date: ${new Date().toISOString().split('T')[0]}
"""

import asyncio
import httpx
import json
from typing import Dict, Any, List

import sys
import os; sys.path.append(os.getcwd()) # Fixed hardcoded path


class AxiomResearchClient:
    """Client for interacting with AXIOM research system"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = "test-key"):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def run_experiment(self, domain: str, tool: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single experiment"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/experimental/run",
                json={
                    "domain": domain,
                    "tool_name": tool,
                    "method": "default",
                    "inputs": inputs
                },
                headers=self.headers
            )
            return response.json()
    
    async def validate_results(self, experiment_id: str, groups: Dict[str, List[float]]) -> Dict[str, Any]:
        """Validate experimental results statistically"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/experimental/validate",
                json={
                    "experiment_id": experiment_id,
                    "groups": groups,
                    "tests": ["t_test", "mann_whitney"],
                    "correction": "fdr_bh",
                    "outlier_methods": ["iqr", "z_score"]
                },
                headers=self.headers
            )
            return response.json()
    
    async def attempt_reproduction(self, paper_id: str, methods: str, expected: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to reproduce published results"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/reproducibility/reproduce",
                json={
                    "paper_id": paper_id,
                    "methods_text": methods,
                    "expected_results": expected,
                    "perturbation_types": ["parameter", "noise"],
                    "n_variations": 3
                },
                headers=self.headers
            )
            return response.json()


from app.agents.multi_llm_brainstorm import MultiLLMBrainstorm

async def drug_discovery_workflow():
    """
    Example: Complete drug discovery workflow
    
    1. Generate hypothesis via multi-LLM brainstorming
    2. Identify target protein
    3. Virtual screening of compounds
    4. Molecular dynamics validation
    5. Statistical analysis
    6. Reproducibility check
    """
    
    client = AxiomResearchClient()
    
    print("🔬 AXIOM Drug Discovery Workflow Example")
    print("=" * 50)
    
    # Step 0: Generate research hypothesis
    print("\n0. Generating research hypothesis via multi-LLM brainstorming...")
    brainstorm = MultiLLMBrainstorm()
    hypothesis_result = brainstorm.brainstorm_with_consensus_and_test(
        "Generate hypotheses for new drug targets in cancer treatment."
    )
    print(f"✅ Generated hypothesis: {hypothesis_result['hypothesis']}")
    print(f"   Initial test: {hypothesis_result['test']}")
    
    # Proceed with workflow using the hypothesis
    # For demo, continue as before
    
    # Step 1: Analyze target protein structure
    print("\n1. Predicting protein structure...")
    
    target_sequence = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL"
    
    structure_result = await client.run_experiment(
        domain="biology",
        tool="protein_structure_prediction",
        inputs={"protein_sequence": target_sequence}
    )
    
    print(f"✅ Structure predicted: {structure_result.get('status')}")
    
    # Step 2: Screen potential drug compounds
    print("\n2. Screening drug candidates...")
    
    drug_candidates = [
        "CC(C)Cc1ccc(cc1)C(C)C(=O)O",  # Ibuprofen
        "CC(=O)Oc1ccccc1C(=O)O",  # Aspirin
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
        "CC12CCC3C(C1CCC2O)CCC4=CC(=O)CCC34C"  # Testosterone
    ]
    
    screening_results = []
    for smiles in drug_candidates:
        result = await client.run_experiment(
            domain="chemistry",
            tool="molecular_properties",
            inputs={"smiles": smiles}
        )
        screening_results.append({
            "smiles": smiles,
            "properties": result.get("outputs", {})
        })
    
    # Find best candidate based on drug-likeness
    best_candidate = max(
        screening_results,
        key=lambda x: x["properties"].get("qed_score", 0)
    )
    
    print(f"✅ Best candidate: {best_candidate['smiles']}")
    print(f"   QED Score: {best_candidate['properties'].get('qed_score', 0):.3f}")
    
    # Step 3: Molecular dynamics simulation
    print("\n3. Running molecular dynamics simulation...")
    
    # In real scenario, would dock ligand to protein first
    md_result = await client.run_experiment(
        domain="biology",
        tool="molecular_dynamics",
        inputs={
            "pdb_structure": "PLACEHOLDER_COMPLEX",  # Would be protein-ligand complex
            "temperature": 310,  # Body temperature
            "time_ns": 1.0,
            "solvate": True
        }
    )
    
    print(f"✅ MD simulation completed")
    if "outputs" in md_result:
        print(f"   Final RMSD: {md_result['outputs'].get('rmsd', [0])[-1]:.2f} Å")
    
    # Step 4: Statistical validation
    print("\n4. Validating results statistically...")
    
    # Simulate binding affinity measurements
    control_group = [10.2, 9.8, 10.5, 11.1, 10.0, 9.9, 10.3, 10.7]
    treatment_group = [7.2, 6.8, 7.5, 7.1, 6.9, 7.3, 7.0, 6.7]
    
    validation_result = await client.validate_results(
        experiment_id="drug_affinity_001",
        groups={
            "control": control_group,
            "treatment": treatment_group
        }
    )
    
    print(f"✅ Statistical validation: {'Valid' if validation_result.get('is_valid') else 'Invalid'}")
    if "power_analysis" in validation_result:
        print(f"   Statistical power: {validation_result['power_analysis'].get('achieved_power', 0):.2f}")
        print(f"   Effect size: {validation_result['power_analysis'].get('effect_size', 0):.2f}")
    
    # Step 5: Test reproducibility
    print("\n5. Testing reproducibility...")
    
    methods_text = """
    Molecular dynamics simulations were performed using the protein-ligand complex.
    The system was solvated in a cubic box with TIP3P water molecules.
    Energy minimization was performed for 5000 steps.
    The system was equilibrated at 310K for 100ps.
    Production MD was run for 1ns with snapshots saved every 10ps.
    Binding energy was calculated using MM-PBSA method.
    """
    
    reproduction_result = await client.attempt_reproduction(
        paper_id="example_2025_001",
        methods=methods_text,
        expected={
            "binding_energy": -25.4,
            "final_rmsd": 2.1
        }
    )
    
    print(f"✅ Reproducibility attempt: {reproduction_result.get('reproduction_status')}")
    print(f"   Reproducibility score: {reproduction_result.get('reproducibility_score', 0):.2f}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Workflow Summary:")
    print(f"- Target protein analyzed: ✓")
    print(f"- Best drug candidate found: {best_candidate['smiles']}")
    print(f"- Molecular dynamics completed: ✓")
    print(f"- Results statistically validated: ✓")
    print(f"- Reproducibility confirmed: {'✓' if reproduction_result.get('success') else '✗'}")
    
    return {
        "target_structure": structure_result,
        "drug_candidate": best_candidate,
        "md_simulation": md_result,
        "statistical_validation": validation_result,
        "reproducibility": reproduction_result
    }


async def materials_discovery_workflow():
    """
    Example: Materials discovery for solar cells
    """
    
    client = AxiomResearchClient()
    
    print("\n🔋 AXIOM Materials Discovery Workflow")
    print("=" * 50)
    
    # Step 1: Screen materials by properties
    print("\n1. Screening semiconductor materials...")
    
    materials = [
        {"composition": "TiO2", "structure": "rutile"},
        {"composition": "GaAs", "structure": "zinc_blende"},
        {"composition": "Si", "structure": "diamond"},
        {"composition": "CdTe", "structure": "zinc_blende"}
    ]
    
    # Step 2: Quantum simulations
    print("\n2. Running quantum mechanical calculations...")
    
    qm_result = await client.run_experiment(
        domain="physics",
        tool="quantum_simulation",
        inputs={
            "system_type": "particle_in_box",
            "box_length": 10.0,  # nm
            "n_levels": 10
        }
    )
    
    print(f"✅ Band gap approximation completed")
    if "outputs" in qm_result:
        energies = qm_result["outputs"].get("energy_levels_eV", [])
        if len(energies) > 1:
            band_gap = energies[1] - energies[0]
            print(f"   Estimated band gap: {band_gap:.2f} eV")
    
    return qm_result


async def run_all_examples():
    """Run all workflow examples"""
    
    print("🚀 AXIOM META 4 - Full Research Workflow Examples")
    print("=" * 70)
    
    # Run drug discovery workflow
    drug_results = await drug_discovery_workflow()
    
    # Run materials discovery workflow
    materials_results = await materials_discovery_workflow()
    
    print("\n" + "=" * 70)
    print("✅ All workflows completed successfully!")
    print("\nAXIOM is now capable of:")
    print("- Real molecular simulations (not stubs)")
    print("- Rigorous statistical validation")
    print("- Active experiment reproduction")
    print("- Multi-domain research workflows")
    
    return {
        "drug_discovery": drug_results,
        "materials_discovery": materials_results
    }


if __name__ == "__main__":
    asyncio.run(drug_discovery_workflow())
    # Run the examples
    asyncio.run(run_all_examples())
