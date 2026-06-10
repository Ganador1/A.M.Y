#!/usr/bin/env python3
"""
Reproducible Example: Mathematics Tools
This script demonstrates how to run mathematical tools directly using AtlasTools.
"""
import sys
import asyncio
import json
from pathlib import Path

# Add the root directory to sys.path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from core.atlas_tools import AtlasTools

async def main():
    print("=" * 60)
    print("A.M.Y Mathematics Tools Example")
    print("=" * 60)
    
    atlas = AtlasTools()
    if not atlas.available:
        print("Error: Atlas tools not available in this environment.")
        return

    print("\n--- Example 1: Solving Equations ---")
    eq = "x**2 - 5*x + 6 = 0"
    print(f"Tool: sympy_solve_equation")
    print(f"Input: {eq}")
    result = await atlas.run_scientific_tool("sympy_solve_equation", eq, domain="mathematics")
    print(f"Result: {result}")
        
    print("\n--- Example 2: Prime Number Theory ---")
    n = "1000"
    print(f"Tool: prime_gap_analysis")
    print(f"Input: {n}")
    result = await atlas.run_scientific_tool("prime_gap_analysis", n, domain="mathematics")
    print(f"Result: {result}")
        
    print("\n--- Example 3: Hypothesis Testing ---")
    params = json.dumps({
        "test_type": "t_test_1samp",
        "samples": [2.5, 2.8, 3.1, 2.9, 3.2, 2.7, 3.0],
        "popmean": 2.0
    })
    print(f"Tool: hypothesis_tester")
    print(f"Input: {params}")
    result = await atlas.run_scientific_tool("hypothesis_tester", params, domain="mathematics")
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
