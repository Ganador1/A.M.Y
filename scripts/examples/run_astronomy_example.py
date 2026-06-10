#!/usr/bin/env python3
"""
Reproducible Example: Astronomy Tools
This script demonstrates how to run astronomy tools directly using AtlasTools.
"""
import sys
import asyncio
from pathlib import Path

# Add the root directory to sys.path
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

from core.atlas_tools import AtlasTools

async def main():
    print("=" * 60)
    print("A.M.Y Astronomy Tools Example")
    print("=" * 60)
    
    atlas = AtlasTools()
    if not atlas.available:
        print("Error: Atlas tools not available in this environment.")
        return
    
    print("\n--- Example 1: Physical Constants ---")
    constant = "G"
    print(f"Tool: astropy_constants")
    print(f"Input: {constant}")
    result = await atlas.run_scientific_tool("astropy_constants", constant, domain="astronomy")
    print(f"Result:\n{result}")
        
    print("\n--- Example 2: Cosmology (Luminosity Distance) ---")
    query = "luminosity_distance:1.0"
    print(f"Tool: astropy_cosmology")
    print(f"Input: {query}")
    result = await atlas.run_scientific_tool("astropy_cosmology", query, domain="astronomy")
    print(f"Result:\n{result}")
        
    print("\n--- Example 3: Blackbody Radiation ---")
    temp = "5778" # Sun's temperature in Kelvin
    print(f"Tool: astropy_blackbody")
    print(f"Input: {temp}")
    result = await atlas.run_scientific_tool("astropy_blackbody", temp, domain="astronomy")
    print(f"Result:\n{result}")

if __name__ == "__main__":
    asyncio.run(main())
