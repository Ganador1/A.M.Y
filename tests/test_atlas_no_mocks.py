"""Regression tests against re-introducing mock/random/hardcoded outputs.

These tests scan the Atlas tool source (when present) for the specific
patterns that the v1.0.0 hardening removed, and they cross-check selected
core.atlas_real_tools outputs against textbook reference values.

They run on every PR. If someone re-adds `random.random()` in a tool
method, or a literal "p < 2.2e-16" without computing it, this will fail.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from core.atlas_real_tools import (
    automated_prover_induction_sum_first_n_powers,
    automated_prover_irrational_root,
    collatz_sequence,
    correlation_analysis,
    euler_characteristic_named_space,
    goldbach_decomposition,
    graph_chromatic_number,
)


ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "atlas" / "app" / "run_agent_with_tools_legacy.py"


# ─── Source-level audits ──────────────────────────────────────────────────────


@pytest.mark.skipif(not LEGACY.exists(), reason="atlas legacy module not present")
class TestNoRandomInLegacyTools:
    """Pattern guards against re-introducing fake science."""

    @pytest.fixture(scope="class")
    def src(self) -> str:
        return LEGACY.read_text(encoding="utf-8")

    def test_no_random_random_calls(self, src):
        # Match `random.random(`, `random.choice(`, `random.uniform(` etc.
        matches = re.findall(r"\brandom\.(random|choice|uniform|normalvariate)\s*\(", src)
        assert matches == [], (
            f"forbidden random.* calls re-introduced in legacy tools: {matches}"
        )

    def test_no_np_random(self, src):
        # `np.random.normal(`, `np.random.uniform(`, etc.
        matches = re.findall(r"\bnp\.random\.\w+\s*\(", src)
        assert matches == [], (
            f"forbidden np.random.* calls in legacy tools: {matches}. "
            "Use core.atlas_real_tools.deterministic_sample with an explicit seed."
        )

    def test_no_hardcoded_pearson_824(self, src):
        # The old `_correlation_analysis` returned a literal r=0.824 for a
        # specific magic input. Make sure that string doesn't come back.
        assert "r: 0.824" not in src
        assert "Pearson r: 0.824" not in src

    def test_no_random_p_value_string(self, src):
        # The old DNABERT2 motif analysis emitted "p < 2.2e-16" as if it
        # were computed; today we only emit p-values from scipy.stats.
        assert "p < 2.2e-16" not in src
        assert "p-value: < 2.2e-16" not in src

    def test_no_simulated_publication_marker(self, src):
        # "Validated. Data ready for publication." was a sign that a tool
        # returned text not derived from its input.
        assert "Validated. Data ready for publication" not in src

    def test_legacy_imports_real_tools(self, src):
        assert "from core import atlas_real_tools" in src


# ─── Textbook value cross-checks (independent of the implementation) ──────────


class TestTextbookValues:
    """Each assertion is anchored in a citation, not in the tool's own code."""

    # Mathematics
    def test_collatz_27_takes_111_steps(self):
        # Lagarias (1985), "The 3x+1 problem and its generalizations": for
        # n=27 the trajectory has 111 steps to 1, with max 9232.
        out = collatz_sequence(27)
        assert "steps: 111" in out
        # Max value 9232 should appear in the digest line
        assert "9232" in out

    def test_goldbach_for_100_has_six_pairs(self):
        # 100 = 3+97 = 11+89 = 17+83 = 29+71 = 41+59 = 47+53 → 6 pairs
        out = goldbach_decomposition(100)
        assert "decompositions found: 6" in out

    def test_sum_of_squares_15_equals_1240(self):
        # Σ k² from 1..15 = 15·16·31/6 = 1240
        out = automated_prover_induction_sum_first_n_powers(2, n_max=15)
        assert "n=15: LHS=1240, RHS=1240" in out

    def test_sqrt_2_irrational(self):
        out = automated_prover_irrational_root(2)
        assert "irrational" in out

    def test_sqrt_49_rational(self):
        out = automated_prover_irrational_root(49)
        assert "rational" in out
        assert "= 7" in out

    # Topology — textbook χ values for surfaces
    def test_chi_sphere(self):
        # χ(S²) = 2  (Euler)
        out = euler_characteristic_named_space("sphere")
        assert "χ = 2" in out

    def test_chi_torus(self):
        # χ(T²) = 0
        out = euler_characteristic_named_space("torus")
        assert "χ = 0" in out

    def test_chi_klein(self):
        # χ(K) = 0
        out = euler_characteristic_named_space("klein_bottle")
        assert "χ = 0" in out

    def test_chi_rp2(self):
        # χ(RP²) = 1
        out = euler_characteristic_named_space("rp2")
        assert "χ = 1" in out

    # Graph theory — chromatic textbook values
    def test_chromatic_petersen_is_3(self):
        # Petersen graph: χ = 3 (well-known, Royle/Godsil 2001)
        out = graph_chromatic_number("petersen")
        assert "exact χ" in out and ": 3" in out

    def test_chromatic_K7_is_7(self):
        out = graph_chromatic_number("complete:7")
        assert "exact χ" in out and ": 7" in out

    def test_chromatic_C_7_is_3(self):
        # Odd cycles have χ = 3
        out = graph_chromatic_number("cycle:7")
        assert "exact χ" in out and ": 3" in out

    # Statistics — Pearson sign and magnitude
    def test_pearson_perfect_positive(self):
        out = correlation_analysis([1, 2, 3, 4, 5], [10, 20, 30, 40, 50])
        assert "Pearson r  = +1.000000" in out

    def test_pearson_anticorrelated(self):
        # Mirror sequence gives r = -1
        out = correlation_analysis([1, 2, 3, 4, 5], [50, 40, 30, 20, 10])
        assert "Pearson r  = -1.000000" in out
