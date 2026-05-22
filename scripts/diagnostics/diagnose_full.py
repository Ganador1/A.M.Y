#!/usr/bin/env python3
"""Diagnóstico completo de literature_search y evidence tools."""
import sys, os, json, asyncio

ATLAS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "atlas")
sys.path.insert(0, ATLAS_ROOT)
os.chdir(ATLAS_ROOT)
os.environ["ENABLE_REDIS_CACHE"] = "false"
import logging
logging.disable(logging.CRITICAL)

from run_agent_with_tools import DynamicToolRegistry

async def main():
    reg = DynamicToolRegistry()
    output = {}
    
    # 1. Literature search - full results
    print("=" * 60)
    print("LITERATURE SEARCH - FULL RESULTS")
    print("=" * 60)
    
    queries = [
        ("prime gaps distribution", "mathematics"),
        ("CRISPR gene therapy", "medicine"),
        ("climate change temperature records", "climate"),
        ("exoplanet atmosphere characterization", "astronomy"),
        ("deep learning drug discovery", "drug_discovery"),
    ]
    
    for query, domain in queries:
        print(f"\n--- Query: {query} (domain: {domain}) ---")
        try:
            r = await reg.execute_tool("literature_search", query)
            data = json.loads(r) if isinstance(r, str) else r
            if isinstance(data, dict):
                results = data.get("results", [])
                source = data.get("source", "N/A")
                print(f"  Source: {source}")
                print(f"  Results: {len(results)} papers")
                for i, p in enumerate(results[:3]):
                    if isinstance(p, dict):
                        title = p.get("title", "N/A")
                        year = p.get("year", "N/A")
                        authors = p.get("authors", "N/A")
                        venue = p.get("venue", "N/A")
                        url = p.get("url", "N/A")
                        if isinstance(authors, list):
                            authors = ", ".join(str(a) for a in authors[:3])
                        print(f"  [{i+1}] {str(title)[:80]}")
                        print(f"       Authors: {str(authors)[:60]}")
                        print(f"       Year: {year} | Venue: {str(venue)[:40]}")
                        print(f"       URL: {str(url)[:80]}")
                output[query] = data
        except Exception as e:
            print(f"  Error: {e}")
    
    # 2. Evidence tools - key metrics
    print("\n" + "=" * 60)
    print("EVIDENCE TOOLS - KEY METRICS")
    print("=" * 60)
    
    evidence_tests = [
        ("evidence_corroborate_medicine", "mRNA vaccines are effective against COVID-19"),
        ("evidence_corroborate_climate", "Global average temperature has risen since the Industrial Revolution"),
        ("evidence_corroborate_genomics", "CRISPR-Cas9 enables precise genome editing"),
        ("evidence_corroborate_quantum_computing", "Quantum supremacy has been demonstrated"),
    ]
    
    for tool, hypothesis in evidence_tests:
        print(f"\n--- {tool} ---")
        try:
            r = await reg.execute_tool(tool, hypothesis)
            data = json.loads(r) if isinstance(r, str) else r
            if isinstance(data, dict):
                print(f"  support_score: {data.get('support_score', 'N/A')}")
                print(f"  real_success_count: {data.get('real_success_count', 'N/A')}")
                print(f"  failure_count: {data.get('failure_count', 'N/A')}")
                print(f"  tool_realism_score: {data.get('tool_realism_score', 'N/A')}")
                print(f"  tier_counts: {data.get('tier_counts', 'N/A')}")
                output[tool] = data
        except Exception as e:
            print(f"  Error: {e}")
    
    # Save
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "literature_evidence_full.json")
    with open(outpath, "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved to {outpath}")

asyncio.run(main())
