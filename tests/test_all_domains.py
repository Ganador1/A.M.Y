#!/usr/bin/env python3
"""
Test ALL remaining Atlas domains through the worker.
Verifica que A.M.Y puede usar cada dominio correctamente.
"""
import sys, os, json, asyncio

ATLAS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atlas")
sys.path.insert(0, ATLAS_ROOT)
os.chdir(ATLAS_ROOT)
os.environ["ENABLE_REDIS_CACHE"] = "false"
import logging
logging.disable(logging.CRITICAL)

from run_agent_with_tools import DynamicToolRegistry

# Dominios ya probados: astronomy, mathematics, chemistry, physics, biology, statistics
# Dominios NUEVOS a probar:
NEW_DOMAINS = {
    "medicine": [
        ("service_alphafold3proteinstructureservice", "MVLSPADKTNVKAAWGKVGA", "AlphaFold protein structure"),
        ("evidence_corroborate_medicine", "mRNA vaccines are effective against COVID-19", "Medical evidence"),
    ],
    "neuroscience": [
        ("service_neurosciencelightservice", "analyze:neural_activity", "Neural activity analysis"),
        ("evidence_corroborate_neuroscience", "Synaptic plasticity is the basis of learning and memory", "Neuroscience evidence"),
    ],
    "climate": [
        ("service_climateevidenceservice", "analyze:co2_trend", "CO2 trend analysis"),
        ("evidence_corroborate_climate", "Global average temperature has risen since the Industrial Revolution", "Climate evidence"),
    ],
    "engineering": [
        ("service_additivemanufacturingservice", "analyze:3d_printing_parameters", "3D printing analysis"),
        ("evidence_corroborate_engineering", "Finite element analysis predicts structural failure modes", "Engineering evidence"),
    ],
    "genomics": [
        ("evidence_corroborate_genomics", "CRISPR-Cas9 enables precise genome editing in human cells", "Genomics evidence"),
    ],
    "drug_discovery": [
        ("evidence_corroborate_drug_discovery", "Molecular docking predicts drug-target binding affinity", "Drug discovery evidence"),
    ],
    "energy_storage": [
        ("evidence_corroborate_energy_storage", "Lithium-ion batteries degrade with charge-discharge cycles", "Energy storage evidence"),
    ],
    "plasma_physics": [
        ("evidence_corroborate_plasma_physics", "Magnetic confinement fusion requires plasma temperatures above 100 million Kelvin", "Plasma physics evidence"),
    ],
    "quantum_computing": [
        ("evidence_corroborate_quantum_computing", "Quantum supremacy has been demonstrated for specific computational tasks", "Quantum computing evidence"),
    ],
    "materials_science": [
        ("evidence_corroborate_materials_science", "Graphene has exceptional mechanical and electrical properties", "Materials science evidence"),
    ],
}

async def test():
    reg = DynamicToolRegistry()
    results = {}
    
    print("=" * 70)
    print("  TESTING ALL ATLAS DOMAINS THROUGH A.M.Y WORKER")
    print("=" * 70)
    
    for domain, tools in sorted(NEW_DOMAINS.items()):
        print(f"\n{'─' * 70}")
        print(f"  DOMAIN: {domain.upper()}")
        print(f"{'─' * 70}")
        
        domain_results = {}
        for tool_name, tool_input, desc in tools:
            print(f"  Running {tool_name}... ", end="", flush=True)
            try:
                result = await reg.execute_tool(tool_name, tool_input)
                domain_results[tool_name] = str(result)
                preview = str(result)[:80].replace("\n", " ")
                print(f"✅ {preview}")
            except Exception as e:
                domain_results[tool_name] = f"Error: {e}"
                print(f"❌ {e}")
        
        results[domain] = domain_results
    
    # Summary
    print(f"\n{'=' * 70}")
    print(f"  RESULTS SUMMARY")
    print(f"{'=' * 70}")
    
    total_tools = 0
    total_ok = 0
    for domain, domain_results in sorted(results.items()):
        ok = sum(1 for v in domain_results.values() if "Error" not in v)
        total = len(domain_results)
        total_tools += total
        total_ok += ok
        status = "✅" if ok == total else f"⚠️  ({ok}/{total})"
        print(f"  {status} {domain}: {ok}/{total} tools OK")
    
    print(f"\n  Total: {total_ok}/{total_tools} tools working")
    print(f"  Success rate: {100*total_ok//total_tools}%")
    
    # Save results
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "all_domains_test_results.json")
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n  Results saved to {outpath}")

asyncio.run(test())
