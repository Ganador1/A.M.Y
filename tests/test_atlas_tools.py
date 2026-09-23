#!/usr/bin/env python3
"""Test Atlas scientific tools across domains."""
import sys
sys.path.insert(0, '.')

from app.run_agent_with_tools_legacy import DynamicToolRegistry

reg = DynamicToolRegistry()

print("=" * 60)
print("ATLAS SCIENTIFIC TOOLS VALIDATION")
print("=" * 60)

# Test 1: Mathematics - Prime gap analysis
print("\n=== TEST 1: MATHEMATICS (Prime Gap Analysis) ===")
try:
    result = reg.tools['prime_gap_analysis'].function('100000')
    print(result)
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

# Test 2: Mathematics - SymPy Derivative
print("\n=== TEST 2: MATHEMATICS (SymPy Derivative) ===")
try:
    result = reg.tools['sympy_derivative'].function('x**3, x')
    print(result)
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

# Test 3: Mathematics - Number Theory
print("\n=== TEST 3: MATHEMATICS (Number Theory) ===")
try:
    result = reg.tools['number_theory_advanced'].function('prime_counting, 1000000')
    print(result[:400])
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

# Test 4: Statistics - Hypothesis Test
print("\n=== TEST 4: STATISTICS (T-Test) ===")
try:
    result = reg.tools['hypothesis_tester'].function('ttest: [1,2,3,4,5]: [3,4,5,6,7]')
    print(result)
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

# Test 5: Physics - Quantum Energy Levels
print("\n=== TEST 5: PHYSICS (Quantum Energy Levels) ===")
try:
    result = reg.tools['quantum_energy_levels'].function('particle_in_box, n=5, L=1e-9')
    print(result[:400])
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

# Test 6: Chemistry - Molecular Weight
print("\n=== TEST 6: CHEMISTRY (Molecular Weight) ===")
try:
    result = reg.tools['molecular_weight_calc'].function('C6H12O6')
    print(result)
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

# Test 7: Biology - DNA Analysis
print("\n=== TEST 7: BIOLOGY (DNA Analysis) ===")
try:
    result = reg.tools['dna_analyzer'].function('ATCGATCGATCG')
    print(result[:400])
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

# Test 8: Research - Literature Search
print("\n=== TEST 8: RESEARCH (Literature Search) ===")
try:
    result = reg.tools['literature_search'].function('prime gaps distribution')
    print(result[:500])
    print("STATUS: PASS")
except Exception as e:
    print(f"STATUS: FAIL - {e}")

print("\n" + "=" * 60)
print("VALIDATION COMPLETE")
print("=" * 60)
