#!/usr/bin/env python3
"""Quick test of literature_search output structure."""
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
    
    r = await reg.execute_tool("literature_search", "prime gaps distribution")
    data = json.loads(r) if isinstance(r, str) else r
    
    if isinstance(data, dict):
        print("keys:", list(data.keys()))
        for k, v in data.items():
            if isinstance(v, list):
                print(f"  {k}: list of {len(v)} items")
                if v and isinstance(v[0], dict):
                    print(f"    first item keys: {list(v[0].keys())[:5]}")
            elif isinstance(v, (int, float, str)):
                print(f"  {k}: {v}")
            else:
                print(f"  {k}: {type(v).__name__}")
    else:
        print("type:", type(data).__name__)
        print("preview:", str(data)[:200])

asyncio.run(main())
