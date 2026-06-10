#!/usr/bin/env python3
"""
Reproducible Example: Chemistry Tools
This script demonstrates how to run chemistry tools directly using AtlasTools.
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
    print("A.M.Y Chemistry Tools Example")
    print("=" * 60)
    
    atlas = AtlasTools()
    if not atlas.available:
        print("Error: Atlas tools not available in this environment.")
        return
    
    print("\n--- Example 1: Molecular Weight ---")
    molecule = "C6H12O6"
    print(f"Tool: molecular_weight_calc")
    print(f"Input: {molecule}")
    result = await atlas.run_scientific_tool("molecular_weight_calc", molecule, domain="chemistry")
    print(f"Result: {result}")
        
    print("\n--- Example 2: Quantum Chemistry (Hartree-Fock) ---")
    atoms = "H 0 0 0; H 0 0 0.74;basis=sto-3g"
    print(f"Tool: pyscf_hf_energy")
    print(f"Input: {atoms}")
    result = await atlas.run_scientific_tool("pyscf_hf_energy", atoms, domain="chemistry")
    print(f"Result:\n{result}")
        
    print("\n--- Example 3: ASE Geometry Optimization ---")
    mol = "H2O"
    print(f"Tool: ase_optimize")
    print(f"Input: {mol}")
    result = await atlas.run_scientific_tool("ase_optimize", mol, domain="chemistry")
    print(f"Result:\n{result}")

if __name__ == "__main__":
    asyncio.run(main())
