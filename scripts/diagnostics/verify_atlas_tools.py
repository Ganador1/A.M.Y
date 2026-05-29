#!/usr/bin/env python3
"""Exercise every Atlas tool with a REAL input and a known expected property.

This is a *verification harness*, not a unit test: it instantiates the actual
`DynamicToolRegistry` from atlas/app/run_agent_with_tools_legacy.py (bypassing
the heavy service-registration that requires fastapi), calls each tool with a
concrete input, and checks the output against a value we can verify
independently (a textbook number, an analytic identity, or a structural
property). It also runs every tool twice to catch hidden randomness.

Usage:
    .venv/bin/python scripts/diagnostics/verify_atlas_tools.py
    .venv/bin/python scripts/diagnostics/verify_atlas_tools.py --verbose

Exit code is non-zero if any tool fails its check, so it can gate CI.
"""

from __future__ import annotations

import argparse
import asyncio
import importlib.util
import os
import sys
import types
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ATLAS_ROOT = REPO_ROOT / "atlas"
LEGACY_PATH = ATLAS_ROOT / "app" / "run_agent_with_tools_legacy.py"


def _install_stubs() -> None:
    """Stub the heavy/optional imports the legacy module does at top level.

    We only stub what is needed to *import* the module and build the tool
    methods. The tool bodies themselves use sympy/numpy/networkx/scipy or our
    own core.atlas_real_tools — all real and installed.
    """
    # Make `import app.*` resolve to atlas/app
    if str(ATLAS_ROOT) not in sys.path:
        sys.path.insert(0, str(ATLAS_ROOT))
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))

    # Stub: app.services package + ollama_provider (the only hard top-level dep)
    def _mk(name: str) -> types.ModuleType:
        m = types.ModuleType(name)
        m.__path__ = []  # mark as package
        return m

    # Build the minimal package tree app -> app.services -> ...ollama_provider
    if "app" not in sys.modules:
        # Let the real `app` package load (it has __init__), but pre-empt the
        # services subpackage so its __init__ (which imports fastapi chains)
        # never runs.
        pass

    services = _mk("app.services")
    llm = _mk("app.services.llm_providers")
    ollama_mod = _mk("app.services.llm_providers.ollama_provider")

    class _StubProvider:
        def __getattr__(self, _):
            raise RuntimeError("ollama_provider is stubbed in verify harness")

    ollama_mod.ollama_provider = _StubProvider()

    sys.modules.setdefault("app.services", services)
    sys.modules.setdefault("app.services.llm_providers", llm)
    sys.modules.setdefault("app.services.llm_providers.ollama_provider", ollama_mod)


def _load_registry_class():
    _install_stubs()
    spec = importlib.util.spec_from_file_location("atlas_legacy_tools", LEGACY_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules["atlas_legacy_tools"] = module
    spec.loader.exec_module(module)
    return module


def _make_registry(module):
    """Build a registry instance WITHOUT running heavy __init__ service hooks.

    We construct via __new__ and only set the attributes the tool methods read,
    then register the built-in tools (pure functions) ourselves.
    """
    Reg = module.DynamicToolRegistry
    reg = Reg.__new__(Reg)
    reg.tools = {}
    reg._global_domains = {"research"}
    reg._domain_aliases = {}
    reg._scope_domain = None
    reg._allowed_domains = None
    # Built-in (pure) tools.
    reg._register_builtin_tools()
    # Advanced tools (dnabert2, correlation_analysis, computational_chemistry,
    # gnome_materials, quantum_circuit, number_theory_advanced, conjecture_engine,
    # automated_prover, graph_theory, topology_invariants, sequence_analyzer,
    # mathematical_discovery, ...). These are pure too; the only thing that
    # needs the heavy stack is the ServiceLocator scan, which we skip.
    if hasattr(reg, "_register_advanced_tools"):
        reg._register_advanced_tools()
    return reg


async def _call(reg, name: str, payload: str) -> str:
    """Invoke a tool by name, awaiting if the function is a coroutine."""
    tool = reg.tools.get(name)
    if tool is None:
        return f"__MISSING_TOOL__:{name}"
    fn = tool.function
    result = fn(payload)
    if asyncio.iscoroutine(result):
        result = await result
    return str(result)


# ─────────────────────────────────────────────────────────────────────────────
# Checks. Each entry: (tool_name, input, predicate, human_description)
# predicate(output:str) -> bool
# ─────────────────────────────────────────────────────────────────────────────


def _is_error(out: str) -> bool:
    """Any output that begins with an error marker is an automatic FAIL."""
    head = out.strip()[:40].lower()
    return head.startswith(("error", "__missing_tool__", "unknown ")) or "error:" in out[:20].lower()


def contains(*subs):
    def _p(out: str) -> bool:
        if _is_error(out):
            return False
        return all(s in out for s in subs)
    return _p


def contains_any(*subs):
    def _p(out: str) -> bool:
        if _is_error(out):
            return False
        return any(s in out for s in subs)
    return _p


CHECKS = [
    # ── Mathematics: SymPy ────────────────────────────────────────────────
    ("sympy_solve_equation", "x**2 - 4", contains_any("-2", "2"),
     "x²-4=0 → roots ±2"),
    ("sympy_simplify", "(x**2 - 1)/(x - 1)", contains("x + 1"),
     "(x²-1)/(x-1) simplifies to x+1"),
    ("sympy_derivative", "x**3, x", contains("3*x**2"),
     "d/dx x³ = 3x²"),
    ("sympy_integrate", "2*x, x", contains("x**2"),
     "∫2x dx = x²"),
    ("sympy_prime_analysis", "is_prime:97", contains_any("prime", "True", "97"),
     "97 is prime"),
    ("sympy_prime_analysis", "is_prime:91", contains_any("not", "False", "composite", "7", "13"),
     "91 = 7·13 is NOT prime"),
    # ── Mathematics: number theory / primes ───────────────────────────────
    ("prime_gap_analysis", "1000", contains_any("gap", "prime"),
     "prime gaps up to 1000"),
    ("number_theory_advanced", "goldbach:20", contains("ALL VERIFIED", "10 = 3 + 7"),
     "Goldbach 4..20 all verified, 10=3+7"),
    ("number_theory_advanced", "twin_primes:100", contains("8", "(71, 73)"),
     "8 twin-prime pairs ≤100, last (71,73)"),
    # ── Mathematics: sequences / discovery / provers ──────────────────────
    ("sequence_analyzer", "generate:fibonacci:10", contains("55"),
     "10th Fibonacci term family contains 55"),
    ("sequence_analyzer", "find_formula:2,4,6,8,10", contains_any("2*n", "linear"),
     "arithmetic sequence formula"),
    ("conjecture_engine", "evaluate:collatz:27", contains("111"),
     "Collatz(27) = 111 steps"),
    ("automated_prover", "induction:sum_powers:2:15", contains("1240"),
     "Σk² 1..15 = 1240"),
    ("automated_prover", "contradiction:sqrt:2", contains("irrational"),
     "√2 is irrational"),
    ("mathematical_discovery", "pattern_analysis:sequences:fibonacci",
     contains_any("phi", "golden", "1.618", "φ"),
     "Fibonacci ratio → golden ratio"),
    # ── Mathematics: graph theory / topology ──────────────────────────────
    ("graph_theory", "chromatic:petersen", contains(": 3"),
     "χ(Petersen) = 3"),
    ("graph_theory", "chromatic:complete:7", contains(": 7"),
     "χ(K₇) = 7"),
    ("graph_theory", "eulerian:cycle:6", contains("Eulerian circuit"),
     "C₆ has Eulerian circuit"),
    ("topology_invariants", "euler_char:sphere", contains("2"),
     "χ(S²) = 2"),
    ("topology_invariants", "euler_char:torus", contains("0"),
     "χ(T²) = 0"),
    ("topology_invariants", "betti:torus", contains("[1, 2, 1]"),
     "Betti(T²) = (1,2,1)"),
    # ── Statistics ────────────────────────────────────────────────────────
    ("numpy_statistics", "mean:1,2,3,4,5", contains("3"),
     "mean(1..5)=3"),
    ("numpy_distribution", "normal:1000,0,1,42", contains_any("mean", "seed=42"),
     "seeded normal sample"),
    ("numpy_correlation", "[1,2,3,4,5];[2,4,6,8,10]", contains("1.0"),
     "perfectly correlated → r=1"),
    ("hypothesis_tester", "ttest:[1,2,3,4,5]:[6,7,8,9,10]",
     contains("t-statistic=-5.0000", "p-value=0.0011"),
     "t-test([1..5],[6..10]) → t=-5.0, p=0.0011"),
    ("hypothesis_tester", "ttest:[1,2,3,4,5];[6,7,8,9,10]",
     contains("t-statistic=-5.0000"),
     "t-test tolerant of ';' separator too"),
    ("correlation_analysis", "[1,2,3,4,5];[2,4,6,8,10]", contains("+1.000000"),
     "correlation r=+1"),
    # ── Chemistry / materials ─────────────────────────────────────────────
    ("molecular_weight_calc", "H2O", contains("18.015"),
     "M(H₂O) = 18.015 g/mol (2·1.008+15.999)"),
    ("molecular_weight_calc", "C6H12O6", contains("180.156"),
     "M(glucose) = 180.156 g/mol"),
    ("molecular_orbital_energy", "6", contains("HOMO-LUMO gap: 2.225 eV"),
     "Hückel linear C₆ gap = 2.225 eV"),
    ("bond_energy_analyzer", "C-H", contains("413 kJ/mol"),
     "E(C-H) = 413 kJ/mol (lit.)"),
    ("computational_chemistry", "analyze_molecule:C6H6",
     contains("78.11", "Heavy atoms: 6"),
     "C₆H₆: MW=78.11, 6 heavy atoms"),
    ("gnome_materials", "stability:TiO2", contains_any("TABULATED", "rutile", "-9.78"),
     "TiO₂ tabulated, labelled"),
    # ── Physics / quantum ─────────────────────────────────────────────────
    ("quantum_energy_levels", "hydrogen:1", contains("-13.6"),
     "H ground state -13.6 eV"),
    ("quantum_energy_levels", "hydrogen:2", contains("-3.4"),
     "H n=2 -3.4 eV"),
    ("quantum_circuit", "bell:2", contains("Entanglement entropy: 1.0 bit"),
     "Bell state entropy = 1 bit"),
    ("quantum_circuit", "grover:4", contains("Search space: 16", "Optimal iterations: 3"),
     "Grover 4-qubit: 16 elems, 3 iterations"),
    ("quantum_circuit", "qft:3", contains("Total gates: 9"),
     "QFT 3-qubit: 9 gates"),
    ("quantum_circuit", "vqe:H2", contains("TABULATED", "-1.137"),
     "VQE H₂ tabulated, labelled, -1.137 Ha"),
    # ── Biology ───────────────────────────────────────────────────────────
    ("dna_analyzer", "GC_content:ATGCATGC", contains("GC content: 50.0%", "GCATGCAT"),
     "GC=50%, revcomp(ATGCATGC)=GCATGCAT"),
    ("protein_properties", "MKVL", contains("489.7 Da"),
     "M(MKVL peptide) = 489.7 Da"),
    ("dnabert2_analysis", "motifs:TATAATAAATTGACA",
     contains("TATAAT", "−10 box", "TTGACA"),
     "motif scan finds −10 and −35 boxes"),
]


async def run_checks(verbose: bool) -> int:
    module = _load_registry_class()
    reg = _make_registry(module)
    real_loaded = getattr(module, "_REAL_TOOLS_AVAILABLE", False)
    registered = sorted(reg.tools.keys())

    print(f"core.atlas_real_tools loaded inside legacy module: {real_loaded}")
    print(f"built-in tools registered: {len(registered)}")
    print("=" * 78)

    passed, failed, missing, nondet = 0, 0, 0, 0
    results = []

    for name, payload, predicate, *desc in CHECKS:
        label = desc[0] if desc else ""
        out = await _call(reg, name, payload)
        out2 = await _call(reg, name, payload)

        if out.startswith("__MISSING_TOOL__"):
            status = "MISSING"
            missing += 1
        elif out != out2:
            status = "NONDET"  # output changed between identical calls!
            nondet += 1
        elif predicate(out):
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        results.append((status, name, payload, label, out))
        mark = {"PASS": "✓", "FAIL": "✗", "MISSING": "?", "NONDET": "🎲"}[status]
        line = f"{mark} [{status:7}] {name:28} {payload[:30]:30} | {label}"
        print(line)
        if verbose or status in ("FAIL", "MISSING", "NONDET"):
            preview = out.replace("\n", " ⏎ ")[:300]
            print(f"            └─ {preview}")

    print("=" * 78)
    print(f"PASS={passed}  FAIL={failed}  MISSING={missing}  NONDET={nondet}  "
          f"(total {len(CHECKS)})")

    return 0 if (failed == 0 and missing == 0 and nondet == 0) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true", help="print every output")
    args = ap.parse_args()
    return asyncio.run(run_checks(args.verbose))


if __name__ == "__main__":
    raise SystemExit(main())
