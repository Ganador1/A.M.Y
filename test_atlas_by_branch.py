"""Systematic Atlas tool testing by scientific branch.
Tests representative tools per domain, capturing real outputs + timing.
"""
import asyncio
import sys
import time
sys.path.insert(0, '.')
from core.atlas_tools import AtlasTools

# Tests organized by scientific branch.
# Format: (tool_name, input, expected_substring_or_None)
TESTS_BY_BRANCH = {
    "MATHEMATICS": [
        ("sympy_solve_equation", "x**2-4", "-2"),
        ("sympy_simplify", "(x**2-1)/(x-1)", None),
        ("prime_gap_analysis", "1000", None),
        ("number_theory_advanced", "goldbach:20", "VERIFIED"),
        ("number_theory_advanced", "twin_primes:100", None),
        ("z3_prover", "x>0", None),
        ("graph_theory", "chromatic:complete5", None),
        ("graph_theory", "eulerian:cycle", None),
        ("topology_invariants", "euler_char:torus", "0"),
        ("topology_invariants", "betti:sphere", None),
    ],
    "PHYSICS": [
        ("quantum_energy_levels", "hydrogen:1", "-13.6"),
        ("quantum_energy_levels", "hydrogen:2", "-3.4"),
        ("quantum_energy_levels", "hydrogen:3", "-1.51"),
        ("quantum_circuit", "bell:2", None),
        ("calculus_engine", "taylor:exp(x):x:0:5", None),
        ("calculus_engine", "fourier:sin(x)", None),
        ("calculus_engine", "limit:1/x:x->inf", None),
    ],
    "CHEMISTRY": [
        ("molecular_weight_calc", "H2O", "18.015"),
        ("molecular_weight_calc", "C6H12O6", "180.156"),
        ("molecular_weight_calc", "NaCl", "58.443"),
        ("molecular_weight_calc", "He", "4.003"),
        ("bond_energy_analyzer", "N-H", "391"),
        ("bond_energy_analyzer", "O-H", "463"),
        ("bond_energy_analyzer", "C-C", "347"),
        ("molecular_orbital_energy", "4", None),
        ("computational_chemistry", "analyze_molecule:C6H6", None),
    ],
    "BIOLOGY": [
        ("dna_analyzer", "ATCGATCGATCG", None),
        ("dna_analyzer", "GC:GCGCGCGC", None),
        ("protein_properties", "MKVLWAALLVTFLAGCQA", None),
    ],
    "STATISTICS": [
        ("numpy_statistics", "summary:[1,2,3,4,5,6,7,8,9,10]", "5.5"),
        ("numpy_distribution", "normal:100,0,1", None),
        ("numpy_correlation", "correlation:[1,2,3,4,5]:[2,4,6,8,10]", "1.0"),
        ("correlation_analysis", "[1,2,3,4,5]:[1,4,9,16,25]", None),
    ],
    "HYPOTHESIS_TESTING": [
        ("hypothesis_tester", "ttest:[1,2,3]:[4,5,6]", None),
        ("validate_hypothesis", "physics:Speed of light is constant", None),
    ],
    "EVIDENCE_CORROBORATION": [
        ("evidence_corroborate_physics", "speed of light is 299792458 m/s", None),
        ("evidence_corroborate_chemistry", "water molecular weight is 18.015", None),
        ("evidence_corroborate_mathematics", "Pi is irrational", None),
    ],
    "LITERATURE": [
        ("literature_search", "glioblastoma BBB drug delivery", None),
    ],
    "ADVANCED_DISCOVERY": [
        ("mathematical_discovery", "pattern_analysis:primes", None),
        ("conjecture_engine", "generate:primes", None),
    ],
}


async def run_branch(at, branch, tests):
    results = []
    for tool, inp, expected in tests:
        t0 = time.time()
        try:
            out = await at.run_scientific_tool(tool, inp)
            dt = time.time() - t0
            out_str = str(out)
            ok = True
            note = ""

            # Check for failure markers
            if any(m in out_str.lower() for m in [
                "error", "not found", "traceback", "unknown operation",
                "not implemented", "placeholder", "mock", "atlas no disponible"
            ]):
                ok = False
                note = "marker_failure"
            elif expected and expected not in out_str:
                ok = False
                note = f"expected '{expected}' not found"

            results.append({
                "tool": tool, "input": inp[:40], "ok": ok,
                "dt": dt, "note": note,
                "out_preview": out_str[:100].replace("\n", " | ")
            })
        except Exception as e:
            dt = time.time() - t0
            results.append({
                "tool": tool, "input": inp[:40], "ok": False,
                "dt": dt, "note": f"exception:{type(e).__name__}",
                "out_preview": str(e)[:100]
            })
    return branch, results


async def main():
    at = AtlasTools()
    print(f"=== Atlas tools by scientific branch ===\n")

    total_ok = 0
    total = 0
    branch_summary = []

    for branch, tests in TESTS_BY_BRANCH.items():
        print(f"\n--- {branch} ({len(tests)} tests) ---")
        _, results = await run_branch(at, branch, tests)
        ok_count = sum(1 for r in results if r["ok"])
        total_ok += ok_count
        total += len(results)
        branch_summary.append((branch, ok_count, len(results)))

        for r in results:
            mark = "OK " if r["ok"] else "FAIL"
            print(f"  [{mark}] {r['tool']:30s} ({r['dt']:5.1f}s) {r['out_preview'][:80]}")
            if not r["ok"]:
                print(f"         → {r['note']}")

    print(f"\n=== SUMMARY ===")
    for branch, ok, n in branch_summary:
        pct = 100 * ok / n if n else 0
        bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
        print(f"  {branch:25s} {bar} {ok}/{n} ({pct:.0f}%)")
    print(f"\n  OVERALL: {total_ok}/{total} ({100*total_ok/total:.1f}%)")


if __name__ == "__main__":
    asyncio.run(main())
