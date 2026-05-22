#!/usr/bin/env python3
"""Test MO novelty detector with real data."""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'atlas')

from run_amy_novelty import molecular_orbital_novelty

# Simulate MO results
results = [
    {"tool": "molecular_orbital_energy", "description": "4-carbon system (butadiene)", 
     "result": "Hückel MO Analysis (4 carbon conjugated system):\n  Energy levels (eV): [np.float64(-10.505), np.float64(-7.113), np.float64(-4.887), np.float64(-1.495)]\n  HOMO: -4.887 eV, LUMO: -7.113 eV", "success": True},
    {"tool": "molecular_orbital_energy", "description": "6-carbon system (benzene)", 
     "result": "Hückel MO Analysis (6 carbon conjugated system):\n  Energy levels (eV): [np.float64(-10.505), np.float64(-9.117), np.float64(-7.113), np.float64(-4.887), np.float64(-2.883), np.float64(-1.495)]\n  HOMO: -4.887 eV, LUMO: -2.883 eV", "success": True},
    {"tool": "molecular_orbital_energy", "description": "8-carbon system (octatetraene)", 
     "result": "Hückel MO Analysis (8 carbon conjugated system):\n  Energy levels (eV): [np.float64(-10.505), np.float64(-9.117), np.float64(-7.113), np.float64(-4.887), np.float64(-2.883), np.float64(-1.495), np.float64(-0.0), np.float64(1.495)]\n  HOMO: -2.883 eV, LUMO: -0.0 eV", "success": True},
    {"tool": "molecular_orbital_energy", "description": "10-carbon system", 
     "result": "Hückel MO Analysis (10 carbon conjugated system):\n  Energy levels (eV): [np.float64(-10.505), np.float64(-9.117), np.float64(-7.113), np.float64(-4.887), np.float64(-2.883), np.float64(-1.495), np.float64(-0.0), np.float64(1.495), np.float64(2.883), np.float64(4.887)]\n  HOMO: -1.495 eV, LUMO: 0.0 eV", "success": True},
    {"tool": "molecular_orbital_energy", "description": "12-carbon system", 
     "result": "Hückel MO Analysis (12 carbon conjugated system):\n  Energy levels (eV): [np.float64(-10.505), np.float64(-9.117), np.float64(-7.113), np.float64(-4.887), np.float64(-2.883), np.float64(-1.495), np.float64(-0.0), np.float64(1.495), np.float64(2.883), np.float64(4.887), np.float64(7.113), np.float64(9.117)]\n  HOMO: -1.495 eV, LUMO: 0.0 eV", "success": True},
    {"tool": "molecular_orbital_energy", "description": "14-carbon system", 
     "result": "Hückel MO Analysis (14 carbon conjugated system):\n  Energy levels (eV): [np.float64(-10.505), np.float64(-9.117), np.float64(-7.113), np.float64(-4.887), np.float64(-2.883), np.float64(-1.495), np.float64(-0.0), np.float64(1.495), np.float64(2.883), np.float64(4.887), np.float64(7.113), np.float64(9.117), np.float64(10.505), np.float64(12.0)]\n  HOMO: -1.495 eV, LUMO: 0.0 eV", "success": True},
]

result = molecular_orbital_novelty(results)
print("=== MO Novelty Detection ===")
print(f"Has novelty: {result['has_novelty']}")
print(f"Findings: {len(result['findings'])}")
for f in result['findings']:
    marker = "🆕" if f.get("is_novel") else "📊"
    print(f"  {marker} {f['description']}")
print(f"\nHypotheses: {len(result['hypotheses'])}")
for h in result['hypotheses']:
    print(f"  • Conf {h['confidence']:.0%}: {h['hypothesis'][:100]}...")