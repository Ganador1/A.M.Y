#!/usr/bin/env python3
"""
Meta 4 Scientific Computing Validation
AXIOM AI - Advanced Scientific Domains Test Suite

Validates the three enhanced scientific computing services:
- Química Computacional 
- Física Computacional
- Biología Computacional
"""

import asyncio
import json
import sys

async def test_computational_chemistry():
    """Test Química Computacional enhancements"""
    print("🧪 Testing Computational Chemistry Service...")
    
    try:
        from app.services.computational_chemistry import ComputationalChemistryService
        service = ComputationalChemistryService()
        
        test_results = {}
        
        # Test crystal structure analysis
        try:
            crystal_request = {
                "structure_type": "perovskite",
                "composition": {"A": "Ca", "B": "Ti", "X": "O"},
                "analysis_level": "basic"
            }
            result = await service.analyze_crystal_structure(crystal_request)
            test_results["crystal_analysis"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["crystal_analysis"] = f"❌ ERROR: {str(e)}"
        
        # Test metabolic network analysis
        try:
            metabolic_request = {
                "model_name": "iJO1366",
                "objective": "biomass",
                "analysis_type": "fba"
            }
            result = await service.metabolic_network_analysis(metabolic_request)
            test_results["metabolic_analysis"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["metabolic_analysis"] = f"❌ ERROR: {str(e)}"
        
        # Test molecular dynamics setup
        try:
            md_request = {
                "system_type": "water",
                "forcefield": "amber14/tip3p.xml",
                "water_model": "tip3p",
                "temperature": 300,
                "pressure": 1.0,
                "pdb_structure": "CRYST1   30.000   30.000   30.000  90.00  90.00  90.00 P 1           1\nATOM      1  O   HOH A   1       0.000   0.000   0.000  1.00  0.00           O\nATOM      2  H1  HOH A   1       0.957   0.000   0.000  1.00  0.00           H\nATOM      3  H2  HOH A   1      -0.240   0.927   0.000  1.00  0.00           H\nTER\n"
            }
            result = await service.molecular_dynamics_setup(md_request)
            if result.get("success"):
                test_results["md_setup"] = "✅ OK"
            else:
                test_results["md_setup"] = "❌ FAILED"
                print(f"⚠️ MD Setup Error: {result}")
        except Exception as e:
            test_results["md_setup"] = f"❌ ERROR: {str(e)}"
            print(f"⚠️ MD Setup Exception: {str(e)}")
        
        # Test materials screening
        try:
            # Create a valid Pymatgen structure dict for Silicon (simplified)
            si_structure = {
                "@module": "pymatgen.core.structure",
                "@class": "Structure",
                "charge": None,
                "lattice": {
                    "matrix": [[3.84, 0.0, 0.0], [1.92, 3.3255, 0.0], [1.92, 1.1085, 3.135]],
                    "a": 3.84, "b": 3.84, "c": 3.84, "alpha": 60.0, "beta": 60.0, "gamma": 60.0,
                    "volume": 40.03
                },
                "sites": [
                    {"species": [{"element": "Si", "occu": 1}], "abc": [0.0, 0.0, 0.0], "xyz": [0.0, 0.0, 0.0], "label": "Si"},
                    {"species": [{"element": "Si", "occu": 1}], "abc": [0.25, 0.25, 0.25], "xyz": [1.92, 1.1085, 0.7837], "label": "Si"}
                ]
            }
            
            screening_request = {
                "materials": [si_structure],
                "criteria": ["stability", "bandgap"]
            }
            result = await service.materials_screening(screening_request)
            # The service returns a list of results, not a success flag directly in the root if it's a list
            # But looking at the code: results = []; ... return {"success": True, "results": results} (Wait, let me check the return)
            # Checking code again...
            # It returns: return {"success": True, "count": len(results), "results": results}
            
            test_results["materials_screening"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["materials_screening"] = f"❌ ERROR: {str(e)}"
        
        print("🧪 Chemistry Results:", json.dumps(test_results, indent=2))
        return test_results
        
    except Exception as e:
        print(f"❌ Chemistry Service Error: {str(e)}")
        return {"service_error": str(e)}

async def test_solid_state_physics():
    """Test Física Computacional enhancements"""
    print("🔬 Testing Solid State Physics Service...")
    
    try:
        from app.services.solid_state_physics import SolidStatePhysicsService
        service = SolidStatePhysicsService()
        
        test_results = {}
        
        # Test Quantum Espresso calculation
        try:
            qe_request = {
                "calculation_type": "scf",
                "structure": {
                    "lattice_parameter": 5.43,
                    "crystal_system": "cubic"
                },
                "k_points": [8, 8, 8],
                "cutoff_energy": 40
            }
            result = await service.quantum_espresso_calculation(qe_request)
            if result.get("success"):
                test_results["quantum_espresso"] = "✅ OK"
            else:
                test_results["quantum_espresso"] = "❌ FAILED"
                print(f"⚠️ Quantum Espresso Error: {result}")
        except Exception as e:
            test_results["quantum_espresso"] = f"❌ ERROR: {str(e)}"
            print(f"⚠️ Quantum Espresso Exception: {str(e)}")
        
        # Test astrophysical material analysis
        try:
            astro_request = {
                "material_type": "stellar_core",
                "composition": {"H": 0.7, "He": 0.28, "metals": 0.02},
                "conditions": {"temperature": 1.5e7, "density": 150}
            }
            result = await service.astrophysical_material_analysis(astro_request)
            if result.get("success"):
                test_results["astrophysical_analysis"] = "✅ OK"
            else:
                test_results["astrophysical_analysis"] = "❌ FAILED"
                print(f"⚠️ Astrophysical Analysis Error: {result}")
        except Exception as e:
            test_results["astrophysical_analysis"] = f"❌ ERROR: {str(e)}"
            print(f"⚠️ Astrophysical Analysis Exception: {str(e)}")
        
        # Test cosmological simulation
        try:
            cosmo_request = {
                "simulation_type": "dark_matter",
                "box_size": 100,  # Mpc
                "resolution": 512,
                "redshift_range": [0, 5]
            }
            result = await service.cosmological_simulation(cosmo_request)
            if result.get("success"):
                test_results["cosmological_sim"] = "✅ OK"
            else:
                test_results["cosmological_sim"] = "❌ FAILED"
                print(f"⚠️ Cosmological Sim Error: {result}")
        except Exception as e:
            test_results["cosmological_sim"] = f"❌ ERROR: {str(e)}"
            print(f"⚠️ Cosmological Sim Exception: {str(e)}")
        
        # Test particle physics analysis
        try:
            particle_request = {
                "process": "higgs_decay",
                "energy": 125,  # GeV
                "decay_channel": "bb",
                "detector": "CMS"
            }
            result = await service.particle_physics_analysis(particle_request)
            test_results["particle_physics"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["particle_physics"] = f"❌ ERROR: {str(e)}"
        
        print("🔬 Physics Results:", json.dumps(test_results, indent=2))
        return test_results
        
    except Exception as e:
        print(f"❌ Physics Service Error: {str(e)}")
        return {"service_error": str(e)}

async def test_computational_biology():
    """Test Biología Computacional service"""
    print("🧬 Testing Computational Biology Service...")
    
    try:
        from app.services.computational_biology import ComputationalBiologyService
        service = ComputationalBiologyService()
        
        test_results = {}
        
        # Test neural network simulation
        try:
            neural_request = {
                "network_type": "spiking",
                "neurons": 1000,
                "simulation_time": 100,  # ms
                "input_current": 10  # nA
            }
            result = await service.neural_network_simulation(neural_request)
            if result.get("success"):
                test_results["neural_simulation"] = "✅ OK"
            else:
                test_results["neural_simulation"] = "❌ FAILED"
                print(f"⚠️ Neural Simulation Error: {result}")
        except Exception as e:
            test_results["neural_simulation"] = f"❌ ERROR: {str(e)}"
            print(f"⚠️ Neural Simulation Exception: {str(e)}")
        
        # Test detailed neuron modeling
        try:
            neuron_request = {
                "cell_type": "pyramidal",
                "morphology": "realistic",
                "channels": ["Na", "K", "Ca"],
                "stimulation": {"type": "current_clamp", "amplitude": 0.5}
            }
            result = await service.neuron_detailed_model(neuron_request)
            if result.get("success"):
                test_results["neuron_modeling"] = "✅ OK"
            else:
                test_results["neuron_modeling"] = "❌ FAILED"
                print(f"⚠️ Neuron Modeling Error: {result}")
        except Exception as e:
            test_results["neuron_modeling"] = f"❌ ERROR: {str(e)}"
            print(f"⚠️ Neuron Modeling Exception: {str(e)}")
        
        # Test gene regulatory network analysis
        try:
            gene_request = {
                "organism": "human",
                "pathway": "cell_cycle",
                "analysis_type": "centrality",
                "network_size": 100
            }
            result = await service.regulatory_network_analysis(gene_request)
            test_results["gene_networks"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["gene_networks"] = f"❌ ERROR: {str(e)}"
        
        # Test ecosystem simulation
        try:
            eco_request = {
                "model_type": "predator_prey",
                "species": ["wolves", "rabbits"],
                "parameters": {"alpha": 1.0, "beta": 0.1, "gamma": 1.5, "delta": 0.075},
                "time_span": [0, 20],
                "initial_conditions": [10, 5]
            }
            result = await service.ecosystem_simulation(eco_request)
            test_results["ecosystem_sim"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["ecosystem_sim"] = f"❌ ERROR: {str(e)}"
        
        # Test population dynamics
        try:
            pop_request = {
                "model": "exponential",
                "initial_population": 1000,
                "growth_rate": 0.05,
                "carrying_capacity": 10000,
                "time_horizon": 50
            }
            result = await service.population_dynamics(pop_request)
            test_results["population_dynamics"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["population_dynamics"] = f"❌ ERROR: {str(e)}"
        
        # Test biodiversity analysis
        try:
            bio_request = {
                "data_type": "species_abundance",
                "location": "tropical_rainforest",
                "indices": ["shannon", "simpson", "pielou"],
                "sample_size": 500
            }
            result = await service.biodiversity_analysis(bio_request)
            test_results["biodiversity"] = "✅ OK" if result.get("success") else "❌ FAILED"
        except Exception as e:
            test_results["biodiversity"] = f"❌ ERROR: {str(e)}"
        
        print("🧬 Biology Results:", json.dumps(test_results, indent=2))
        return test_results
        
    except Exception as e:
        print(f"❌ Biology Service Error: {str(e)}")
        return {"service_error": str(e)}

async def test_service_integration():
    """Test service integration and availability"""
    print("🔧 Testing Service Integration...")
    
    try:
        from app.services import (
            ComputationalChemistryService,
            SolidStatePhysicsService, 
            ComputationalBiologyService
        )
        
        integration_results = {
            "chemistry_service": "✅ Imported",
            "physics_service": "✅ Imported", 
            "biology_service": "✅ Imported"
        }
        
        # Test service instantiation
        try:
            ComputationalChemistryService()
            SolidStatePhysicsService()
            ComputationalBiologyService()
            
            integration_results["service_instantiation"] = "✅ All services instantiated"
        except Exception as e:
            integration_results["service_instantiation"] = f"❌ ERROR: {str(e)}"
        
        print("🔧 Integration Results:", json.dumps(integration_results, indent=2))
        return integration_results
        
    except Exception as e:
        print(f"❌ Integration Error: {str(e)}")
        return {"integration_error": str(e)}

async def main():
    """Main test execution"""
    print("🚀 AXIOM Meta 4 Scientific Computing Validation")
    print("=" * 50)
    
    # Run all tests
    chemistry_results = await test_computational_chemistry()
    physics_results = await test_solid_state_physics()
    biology_results = await test_computational_biology()
    integration_results = await test_service_integration()
    
    # Compile results
    full_results = {
        "timestamp": "2025-01-18",
        "meta_4_validation": {
            "computational_chemistry": chemistry_results,
            "solid_state_physics": physics_results,
            "computational_biology": biology_results,
            "service_integration": integration_results
        }
    }
    
    # Save results
    with open("meta4_validation_results.json", "w") as f:
        json.dump(full_results, f, indent=2)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 META 4 VALIDATION SUMMARY")
    print("=" * 50)
    
    total_tests = 0
    passed_tests = 0
    
    for service, results in full_results["meta_4_validation"].items():
        print(f"\n🔬 {service.upper()}:")
        for test, status in results.items():
            total_tests += 1
            if "✅" in str(status):
                passed_tests += 1
            print(f"  {test}: {status}")
    
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n🎯 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 Meta 4 Scientific Computing Enhancement: SUCCESSFUL!")
        return 0
    else:
        print("⚠️  Meta 4 validation needs attention")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
