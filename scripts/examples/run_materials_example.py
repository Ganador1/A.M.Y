#!/usr/bin/env python3
"""
Reproducible Example: Materials Science Tools
This script demonstrates how to run materials science tools directly using AtlasTools.
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
    print("A.M.Y Materials Science Tools Example")
    print("=" * 60)
    
    atlas = AtlasTools()
    if not atlas.available:
        print("Error: Atlas tools not available in this environment.")
        return
    
    print("\n--- Example 1: Material Structure (PyMatGen) ---")
    material = "TiO2"
    print(f"Tool: pymatgen_structure")
    print(f"Input: {material}")
    result = await atlas.run_scientific_tool("pymatgen_structure", material, domain="materials_science")
    print(f"Result:\n{result}")
        
    print("\n--- Example 2: Material Info (GNoME) ---")
    query = "crystal_info:TiO2"
    print(f"Tool: gnome_materials")
    print(f"Input: {query}")
    result = await atlas.run_scientific_tool("gnome_materials", query, domain="materials_science")
    print(f"Result:\n{result}")

if __name__ == "__main__":
    asyncio.run(main())
