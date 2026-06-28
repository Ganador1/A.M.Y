"""Root conftest.

- Adds the repo root to sys.path so tests can import top-level modules
  (e.g. `from core.atlas_tools import ...`) no matter where they live.
- Adds the script directories (`scripts/analysis`, `scripts/run`) to sys.path
  so the regression tests that cover those scripts can import them by module
  name (e.g. `from double_blind_evaluator import ...`).
- Pins cwd to the repo root for the test session so legacy tests that
  use relative paths like `Path("atlas")` keep working after we moved
  them into ./tests/.
- Ignores the *script-style* `tests/test_*.py` files that are standalone
  diagnostic scripts (run with `python tests/<file>.py`), not pytest test
  modules. They contain no `test_*` functions (or only functions that take
  non-fixture parameters like `tools`) and previously raised *collection
  errors* — which masked real failures in the rest of the suite. They are
  still runnable directly; they are simply not collected by pytest.
"""
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.resolve()

# Repo root first, then the script dirs whose modules a few tests import by name.
for _p in (_ROOT, _ROOT / "scripts" / "analysis", _ROOT / "scripts" / "run"):
    _s = str(_p)
    if _p.exists() and _s not in sys.path:
        sys.path.insert(0, _s)


# Script-style files under tests/ that are NOT pytest modules. They are
# diagnostic scripts (top-level print-based code or `__main__` runners) or use
# undeclared parameters (e.g. `tools`) that pytest mistakes for missing
# fixtures. Collecting them errored; we skip them here so the real suite runs
# clean. Run any of them directly, e.g. `python tests/test_atlas_tools.py`.
_SCRIPT_STYLE_TESTS = (
    "test_all_domains.py",
    "test_amy_atlas_integration.py",
    "test_amy_generates_paper.py",
    "test_atlas_exhaustive.py",
    "test_atlas_tools.py",
    "test_enhancer.py",
    "test_literature_sources.py",
    "test_mo_novelty.py",
    "test_novelty_tools.py",
    "test_paper_with_literature.py",
    "test_provenance_integration.py",
)
collect_ignore = [str(Path("tests") / name) for name in _SCRIPT_STYLE_TESTS]


# ---------------------------------------------------------------------------
# Automatic test markers by file.
#
# The suite mixes sub-second hermetic unit tests with tests that spawn the
# Atlas worker, hit the network (arXiv/PubMed/Ollama Cloud), or run a full
# mission — some taking 40-80s each. Without a way to separate them, the only
# choice was "run everything" (minutes, and it could hang). These sets are
# derived from measured per-file runtime + what each file actually does, so
# you can run the fast lane with:
#
#     pytest -m "not (slow or network or atlas)"
#
# and the full suite (CI nightly / local pre-push) with no marker filter.
# Marking by path here keeps the 16 affected files unedited and the policy
# in one auditable place. A file may appear in several sets.
# ---------------------------------------------------------------------------

# Measured >= ~7s per file (LLM / Atlas worker startup / full missions).
_SLOW_FILES = {
    "test_atlas_misuse_guard.py",
    "test_cognitive_cycle.py",
    "test_connection.py",
    "test_edge_cases.py",
    "test_end_to_end_pipeline.py",
    "test_full_mission_simulation.py",
    "test_heartbeat_atlas_tools.py",
    "test_mathematics_deep_dive.py",
    "test_multi_domain_missions.py",
    "test_paper_quality.py",
    "test_paper_tools_integration.py",
    "test_peer_review_safe.py",
    "test_robustness.py",
    "test_sandbox_atlas_integration.py",
    "test_scientific_method.py",
    "test_security_guardrails.py",
}

# Files that spawn / talk to the Atlas worker (need the atlas venv + libs).
_ATLAS_FILES = {
    "test_atlas_misuse_guard.py",
    "test_cognitive_cycle.py",
    "test_edge_cases.py",
    "test_end_to_end_pipeline.py",
    "test_full_mission_simulation.py",
    "test_heartbeat_atlas_tools.py",
    "test_heartbeat_paper_pipeline.py",
    "test_mathematics_deep_dive.py",
    "test_multi_domain_missions.py",
    "test_paper_quality.py",
    "test_paper_tools_integration.py",
    "test_robustness.py",
    "test_sandbox_atlas_integration.py",
    "test_scientific_method.py",
    "test_security_guardrails.py",
}

# Files that reach out over the network (literature search, citation verify).
_NETWORK_FILES = {
    "test_connection.py",
    "test_end_to_end_pipeline.py",
    "test_full_mission_simulation.py",
    "test_multi_domain_missions.py",
    "test_paper_quality.py",
    "test_paper_tools_integration.py",
    "test_peer_review_safe.py",
}


def pytest_collection_modifyitems(config, items):
    for item in items:
        name = Path(str(item.fspath)).name
        if name in _SLOW_FILES:
            item.add_marker(pytest.mark.slow)
        if name in _ATLAS_FILES:
            item.add_marker(pytest.mark.atlas)
        if name in _NETWORK_FILES:
            item.add_marker(pytest.mark.network)


@pytest.fixture(autouse=True)
def _chdir_repo_root(monkeypatch):
    monkeypatch.chdir(_ROOT)
