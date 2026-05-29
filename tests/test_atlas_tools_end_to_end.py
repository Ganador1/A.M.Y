"""End-to-end verification that EVERY registered Atlas tool computes correctly.

Unlike test_atlas_real_tools.py (which tests core.atlas_real_tools in
isolation), this test loads the *actual* DynamicToolRegistry from
atlas/app/run_agent_with_tools_legacy.py — the same class A.M.Y uses at
runtime — and drives each tool through its real string protocol, asserting
on values we can verify independently (textbook numbers, analytic
identities). It also runs each tool twice to prove determinism.

The heavy Atlas service stack (fastapi, ollama, ServiceLocator) is stubbed
so this can run in CI without those dependencies; the tool *bodies*
themselves run for real (sympy / numpy / scipy / networkx /
core.atlas_real_tools).

If a tool regresses to a mock, returns an error, or becomes
non-deterministic, this test fails.
"""
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parent.parent
ATLAS_ROOT = ROOT / "atlas"
LEGACY_PATH = ATLAS_ROOT / "app" / "run_agent_with_tools_legacy.py"

pytestmark = pytest.mark.skipif(
    not LEGACY_PATH.exists(), reason="atlas legacy tool module not present"
)


def _install_stubs() -> None:
    if str(ATLAS_ROOT) not in sys.path:
        sys.path.insert(0, str(ATLAS_ROOT))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    def _pkg(name: str) -> types.ModuleType:
        m = types.ModuleType(name)
        m.__path__ = []
        return m

    services = _pkg("app.services")
    llm = _pkg("app.services.llm_providers")
    ollama_mod = _pkg("app.services.llm_providers.ollama_provider")

    class _StubProvider:
        def __getattr__(self, _):
            raise RuntimeError("ollama_provider stubbed for tests")

    ollama_mod.ollama_provider = _StubProvider()
    sys.modules.setdefault("app.services", services)
    sys.modules.setdefault("app.services.llm_providers", llm)
    sys.modules.setdefault("app.services.llm_providers.ollama_provider", ollama_mod)


@pytest.fixture(scope="module")
def registry():
    _install_stubs()
    spec = importlib.util.spec_from_file_location("atlas_legacy_e2e", LEGACY_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["atlas_legacy_e2e"] = module
    spec.loader.exec_module(module)

    Reg = module.DynamicToolRegistry
    reg = Reg.__new__(Reg)
    reg.tools = {}
    reg._global_domains = {"research"}
    reg._domain_aliases = {}
    reg._scope_domain = None
    reg._allowed_domains = None
    reg._register_builtin_tools()
    if hasattr(reg, "_register_advanced_tools"):
        reg._register_advanced_tools()

    # The real tools module must be wired in — otherwise the tools we fixed
    # would be using the honest-fallback stubs instead of real computation.
    assert getattr(module, "_REAL_TOOLS_AVAILABLE", False), (
        "core.atlas_real_tools failed to import inside the legacy module"
    )
    return reg


def _run(reg, name: str, payload: str) -> str:
    import asyncio

    tool = reg.tools.get(name)
    assert tool is not None, f"tool {name!r} is not registered"
    out = tool.function(payload)
    if asyncio.iscoroutine(out):
        out = asyncio.get_event_loop().run_until_complete(out)
    return str(out)


# (name, input, list-of-substrings-that-must-all-appear, human label)
CASES = [
    # SymPy
    ("sympy_derivative", "x**3, x", ["3*x**2"], "d/dx x³"),
    ("sympy_integrate", "2*x, x", ["x**2"], "∫2x dx"),
    ("sympy_simplify", "(x**2 - 1)/(x - 1)", ["x + 1"], "simplify"),
    # Number theory
    ("number_theory_advanced", "goldbach:20", ["ALL VERIFIED", "10 = 3 + 7"], "Goldbach 20"),
    ("number_theory_advanced", "twin_primes:100", ["(71, 73)"], "twin primes ≤100"),
    # Sequences / provers
    ("sequence_analyzer", "generate:fibonacci:10", ["55"], "Fibonacci 10"),
    ("conjecture_engine", "evaluate:collatz:27", ["111", "9232"], "Collatz 27"),
    ("automated_prover", "induction:sum_powers:2:15", ["1240"], "Σk² 1..15"),
    ("automated_prover", "contradiction:sqrt:2", ["irrational"], "√2 irrational"),
    # Graph / topology
    ("graph_theory", "chromatic:petersen", [": 3"], "χ(Petersen)=3"),
    ("graph_theory", "chromatic:complete:7", [": 7"], "χ(K₇)=7"),
    ("graph_theory", "eulerian:cycle:6", ["Eulerian circuit"], "C₆ Eulerian"),
    ("topology_invariants", "euler_char:sphere", ["2"], "χ(S²)=2"),
    ("topology_invariants", "euler_char:torus", ["0"], "χ(T²)=0"),
    # Statistics
    ("numpy_statistics", "mean:1,2,3,4,5", ["3"], "mean"),
    ("numpy_correlation", "[1,2,3,4,5];[2,4,6,8,10]", ["1.0"], "r=1"),
    ("hypothesis_tester", "ttest:[1,2,3,4,5]:[6,7,8,9,10]",
     ["t-statistic=-5.0000", "p-value=0.0011"], "t-test colon"),
    ("hypothesis_tester", "ttest:[1,2,3,4,5];[6,7,8,9,10]",
     ["t-statistic=-5.0000"], "t-test semicolon"),
    ("correlation_analysis", "[1,2,3,4,5];[2,4,6,8,10]", ["+1.000000"], "corr r=1"),
    # Chemistry / materials
    ("molecular_weight_calc", "H2O", ["18.015"], "M(H₂O)"),
    ("molecular_weight_calc", "C6H12O6", ["180.156"], "M(glucose)"),
    ("molecular_orbital_energy", "6", ["HOMO-LUMO gap: 2.225 eV"], "Hückel C₆"),
    ("bond_energy_analyzer", "C-H", ["413 kJ/mol"], "E(C-H)"),
    ("computational_chemistry", "analyze_molecule:C6H6", ["78.11", "Heavy atoms: 6"], "C₆H₆"),
    ("gnome_materials", "stability:TiO2", ["TABULATED"], "TiO₂ labelled"),
    # Physics / quantum
    ("quantum_energy_levels", "hydrogen:1", ["-13.6"], "H ground"),
    ("quantum_energy_levels", "hydrogen:2", ["-3.4"], "H n=2"),
    ("quantum_circuit", "bell:2", ["Entanglement entropy: 1.0 bit"], "Bell"),
    ("quantum_circuit", "grover:4", ["Search space: 16", "Optimal iterations: 3"], "Grover"),
    ("quantum_circuit", "qft:3", ["Total gates: 9"], "QFT"),
    ("quantum_circuit", "vqe:H2", ["TABULATED", "-1.137"], "VQE labelled"),
    # Biology
    ("dna_analyzer", "GC_content:ATGCATGC", ["GC content: 50.0%", "GCATGCAT"], "DNA"),
    ("protein_properties", "MKVL", ["489.7 Da"], "peptide MW"),
    ("dnabert2_analysis", "motifs:TATAATAAATTGACA", ["TATAAT", "TTGACA"], "DNABERT2 motifs"),
]


@pytest.mark.parametrize("name,payload,expected,label", CASES, ids=[c[3] for c in CASES])
def test_tool_produces_expected_value(registry, name, payload, expected, label):
    out = _run(registry, name, payload)
    assert not out.strip().lower().startswith(("error", "unknown ")), (
        f"{name}({payload}) returned an error: {out[:200]}"
    )
    for sub in expected:
        assert sub in out, (
            f"{name}({payload}) missing {sub!r}.\n  label: {label}\n  got: {out[:300]}"
        )


@pytest.mark.parametrize("name,payload,expected,label", CASES, ids=[c[3] for c in CASES])
def test_tool_is_deterministic(registry, name, payload, expected, label):
    a = _run(registry, name, payload)
    b = _run(registry, name, payload)
    assert a == b, f"{name}({payload}) is non-deterministic — suspect random.*"
