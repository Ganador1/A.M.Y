#!/usr/bin/env python3
"""Probar herramientas astronómicas con formato JSON correcto."""
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
    
    # 1. Astronomical ML with JSON
    print("=" * 60)
    print("1. service_astronomicalmlservice (JSON)")
    print("=" * 60)
    
    payload = json.dumps({
        "operation": "classify_stellar_object",
        "features": {"magnitude": 12.5, "color_index": 0.8, "redshift": 0.05},
        "algorithm": "random_forest"
    })
    try:
        result = await reg.execute_tool("service_astronomicalmlservice", payload)
        print("classify_stellar_object:", str(result)[:300])
        results["classify_stellar"] = str(result)
    except Exception as e:
        print("classify_stellar_object Error:", e)
    
    payload2 = json.dumps({
        "operation": "detect_anomalies",
        "time": [0, 1, 2, 3, 4, 5],
        "flux": [1.0, 1.02, 0.95, 1.01, 0.98, 1.0],
        "algorithm": "isolation_forest",
        "contamination": 0.1
    })
    try:
        result = await reg.execute_tool("service_astronomicalmlservice", payload2)
        print("detect_anomalies:", str(result)[:300])
        results["detect_anomalies"] = str(result)
    except Exception as e:
        print("detect_anomalies Error:", e)
    
    # 2. evidence_corroborate_astronomy
    print("\n" + "=" * 60)
    print("2. evidence_corroborate_astronomy")
    print("=" * 60)
    hypotheses = [
        "The James Webb Space Telescope has observed galaxies at redshift z>10 that challenge early galaxy formation models",
        "Exoplanet atmospheres can be characterized through transmission spectroscopy with JWST",
        "The Hubble constant tension between early and late universe measurements suggests new physics beyond Lambda-CDM",
    ]
    for h in hypotheses:
        try:
            result = await reg.execute_tool("evidence_corroborate_astronomy", h)
            data = json.loads(result) if isinstance(result, str) else result
            support = data.get("support_score", data.get("score", "N/A"))
            print(f"  support={support} | {h[:60]}...")
            results[f"evidence_{h[:20]}"] = str(result)[:500]
        except Exception as e:
            print(f"  Error: {e}")
    
    # 3. quantum_energy_levels for stellar context
    print("\n" + "=" * 60)
    print("3. Hydrogen energy levels (stellar astrophysics)")
    print("=" * 60)
    for n in [1, 2, 3, 5, 10, 20]:
        try:
            result = await reg.execute_tool("quantum_energy_levels", f"hydrogen:{n}")
            print(f"  n={n}: {str(result)[:150]}")
            results[f"hydrogen_n{n}"] = str(result)
        except Exception as e:
            print(f"  n={n} Error: {e}")
    
    # 4. numpy statistics for astronomical data
    print("\n" + "=" * 60)
    print("4. numpy statistics (astronomical context)")
    print("=" * 60)
    try:
        result = await reg.execute_tool("numpy_statistics", "summary:[1.0,2.5,3.2,4.8,5.1,6.3,7.0,8.9,9.5,10.2]")
        print(f"  stats: {str(result)[:200]}")
        results["numpy_stats"] = str(result)
    except Exception as e:
        print(f"  Error: {e}")
    
    try:
        result = await reg.execute_tool("numpy_correlation", "[1,2,3,4,5,6,7,8,9,10];[2.1,4.2,5.8,8.1,9.9,12.2,14.1,15.9,18.0,20.1]")
        print(f"  correlation: {str(result)[:200]}")
        results["numpy_corr"] = str(result)
    except Exception as e:
        print(f"  Error: {e}")
    
    # Save results
    outpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "astro_tool_results.json")
    with open(outpath, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to {outpath}")

asyncio.run(test())
