#!/usr/bin/env python3
"""Run evidence_corroborate_astronomy for paper generation."""
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
    results = {}
    
    hypotheses = [
        "The James Webb Space Telescope has observed galaxies at redshift z>10 that challenge early galaxy formation models",
        "Exoplanet atmospheres can be characterized through transmission spectroscopy with JWST",
        "The Hubble constant tension between early and late universe measurements suggests new physics beyond Lambda-CDM",
        "Supermassive black holes at the center of galaxies correlate with galaxy bulge properties",
        "The expansion rate of the universe is accelerating due to dark energy",
    ]
    
    for h in hypotheses:
        try:
            result = await reg.execute_tool("evidence_corroborate_astronomy", h)
            data = json.loads(result) if isinstance(result, str) else result
            support = data.get("support_score", "N/A")
            real_success = data.get("real_success_count", "N/A")
            print(f"\nHypothesis: {h[:70]}...")
            print(f"  support_score={support}, real_success_count={real_success}")
            results[h[:40]] = {"support": support, "real_success": real_success, "raw": str(data)[:300]}
        except Exception as e:
            print(f"  Error: {e}")
            results[h[:40]] = {"error": str(e)}
    
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "astro_evidence_results.json")
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nSaved to {outpath}")

asyncio.run(main())
