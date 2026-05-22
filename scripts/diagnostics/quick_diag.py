#!/usr/bin/env python3
"""Quick test of evidence tools and literature search."""
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
    
    print("=== EVIDENCE TOOLS ===")
    r = await reg.execute_tool("evidence_corroborate_medicine", "mRNA vaccines are effective against COVID-19")
    data = json.loads(r) if isinstance(r, str) else r
    print("support_score:", data.get("support_score"))
    print("real_success_count:", data.get("real_success_count"))
    print("tier_counts:", data.get("tier_counts"))
    print("tool_realism_score:", data.get("tool_realism_score"))
    
    print("\n=== LITERATURE SEARCH ===")
    r2 = await reg.execute_tool("literature_search", "prime gaps distribution")
    data2 = json.loads(r2) if isinstance(r2, str) else r2
    if isinstance(data2, dict):
        papers = data2.get("papers", data2.get("results", []))
        print("papers found:", len(papers) if isinstance(papers, list) else type(papers).__name__)
        if isinstance(papers, list) and papers:
            for p in papers[:2]:
                if isinstance(p, dict):
                    print("  title:", str(p.get("title", ""))[:60])
                    print("  source:", p.get("source", "N/A"))
        else:
            print("  raw keys:", list(data2.keys())[:5])
            print("  raw preview:", json.dumps(data2, default=str)[:300])

asyncio.run(main())
