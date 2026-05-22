#!/usr/bin/env python3
"""Ver output completo de evidence tools y fuentes literarias."""
import sys, os, json, asyncio

ATLAS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atlas")
sys.path.insert(0, ATLAS_ROOT)
os.chdir(ATLAS_ROOT)
os.environ["ENABLE_REDIS_CACHE"] = "false"
import logging
logging.disable(logging.CRITICAL)

from run_agent_with_tools import DynamicToolRegistry

async def test():
    reg = DynamicToolRegistry()
    results = {}
    
    print("=" * 70)
    print("  EVIDENCE TOOLS - FULL DIAGNOSTIC")
    print("=" * 70)
    
    tests = [
        ("evidence_corroborate_medicine", "mRNA vaccines are effective against COVID-19"),
        ("evidence_corroborate_neuroscience", "Synaptic plasticity is the basis of learning and memory"),
        ("evidence_corroborate_climate", "Global average temperature has risen since the Industrial Revolution"),
        ("evidence_corroborate_genomics", "CRISPR-Cas9 enables precise genome editing in human cells"),
        ("evidence_corroborate_drug_discovery", "Molecular docking predicts drug-target binding affinity"),
        ("evidence_corroborate_quantum_computing", "Quantum supremacy has been demonstrated for specific computational tasks"),
        ("evidence_corroborate_engineering", "Finite element analysis predicts structural failure modes"),
        ("evidence_corroborate_energy_storage", "Lithium-ion batteries degrade with charge-discharge cycles"),
        ("evidence_corroborate_plasma_physics", "Magnetic confinement fusion requires plasma temperatures above 100 million Kelvin"),
        ("evidence_corroborate_materials_science", "Graphene has exceptional mechanical and electrical properties"),
    ]
    
    for tool, hypothesis in tests:
        print(f"\n{'─' * 60}")
        print(f"  {tool}")
        print(f"  Hypothesis: {hypothesis[:70]}...")
        print(f"{'─' * 60}")
        try:
            result = await reg.execute_tool(tool, hypothesis)
            data = json.loads(result) if isinstance(result, str) else result
            results[tool] = data
            
            for key in ["support_score", "real_success_count", "failure_count", "tool_realism_score"]:
                val = data.get(key, "N/A")
                print(f"  {key}: {val}")
            
            tier = data.get("tier_counts", {})
            if tier:
                print(f"  tier_counts: {json.dumps(tier)}")
            
            top = data.get("top_evidence", data.get("evidence", []))
            if top and isinstance(top, list):
                for i, e in enumerate(top[:2]):
                    if isinstance(e, dict):
                        print(f"  evidence[{i}]: {json.dumps(e, default=str)[:200]}")
                    else:
                        print(f"  evidence[{i}]: {str(e)[:200]}")
        except Exception as e:
            print(f"  Error: {e}")
            results[tool] = {"error": str(e)}
    
    # Now test literature_search
    print(f"\n{'=' * 70}")
    print("  LITERATURE SEARCH (sources)")
    print(f"{'=' * 70}")
    
    lit_tests = [
        ("literature_search", "prime gaps distribution", "mathematics"),
        ("literature_search", "CRISPR gene therapy clinical trials", "medicine"),
        ("literature_search", "climate change temperature records", "climate"),
    ]
    
    for tool, query, domain in lit_tests:
        print(f"\n  Query: {query} (domain: {domain})")
        try:
            result = await reg.execute_tool(tool, query)
            data = json.loads(result) if isinstance(result, str) else result
            if isinstance(data, dict):
                papers = data.get("papers", data.get("results", []))
                sources = data.get("sources", data.get("source", "N/A"))
                print(f"  Papers found: {len(papers) if isinstance(papers, list) else 'N/A'}")
                print(f"  Sources: {sources}")
                if isinstance(papers, list) and papers:
                    for i, p in enumerate(papers[:2]):
                        if isinstance(p, dict):
                            print(f"  paper[{i}]: title={str(p.get('title',''))[:60]}, source={p.get('source','N/A')}")
            else:
                print(f"  Result: {str(data)[:200]}")
        except Exception as e:
            print(f"  Error: {e}")
    
    # Save
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "evidence_literature_diagnostic.json")
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {outpath}")

asyncio.run(test())
