#!/usr/bin/env python3
"""Test literature_search across multiple domains."""
import sys, os, json, asyncio

ATLAS_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "atlas")
sys.path.insert(0, ATLAS_ROOT)
os.chdir(ATLAS_ROOT)
os.environ["ENABLE_REDIS_CACHE"] = "false"
import logging
logging.disable(logging.CRITICAL)

from run_agent_with_tools import DynamicToolRegistry

async def main():
    reg = DynamicToolRegistry()
    
    print("=" * 70)
    print("  LITERATURE SEARCH - ALL DOMAINS")
    print("=" * 70)
    
    queries = [
        ("prime gaps distribution", "mathematics"),
        ("molecular weight calculation organic compounds", "chemistry"),
        ("hydrogen energy levels quantum mechanics", "physics"),
        ("DNA sequence analysis bioinformatics", "biology"),
        ("normal distribution statistical testing", "statistics"),
        ("exoplanet atmosphere characterization", "astronomy"),
        ("CRISPR gene therapy clinical trials", "medicine"),
        ("synaptic plasticity learning memory", "neuroscience"),
        ("global temperature records climate change", "climate"),
        ("additive manufacturing 3D printing parameters", "engineering"),
    ]
    
    for query, domain in queries:
        print(f"\n{'─' * 60}")
        print(f"  Domain: {domain}")
        print(f"  Query: {query}")
        print(f"{'─' * 60}")
        try:
            r = await reg.execute_tool("literature_search", query)
            data = json.loads(r) if isinstance(r, str) else r
            if isinstance(data, dict):
                results = data.get("results", [])
                source = data.get("source", "N/A")
                print(f"  Source: {source}")
                print(f"  Papers: {len(results)}")
                for i, p in enumerate(results[:2]):
                    if isinstance(p, dict):
                        title = p.get("title", "N/A")
                        year = p.get("year", "N/A")
                        authors = p.get("authors", "N/A")
                        if isinstance(authors, list):
                            authors = ", ".join(str(a) for a in authors[:2])
                        print(f"  [{i+1}] {str(title)[:80]}")
                        print(f"       {str(authors)[:60]} ({year})")
            else:
                print(f"  Result type: {type(data).__name__}")
        except Exception as e:
            print(f"  Error: {e}")
    
    print("\nDone!")

asyncio.run(main())
