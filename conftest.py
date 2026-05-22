"""Root conftest.

- Adds the repo root to sys.path so tests can import top-level modules
  (e.g. `from core.atlas_tools import ...`) no matter where they live.
- Pins cwd to the repo root for the test session so legacy tests that
  use relative paths like `Path("atlas")` keep working after we moved
  them into ./tests/.
"""
import os
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).parent.resolve()
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


@pytest.fixture(autouse=True)
def _chdir_repo_root(monkeypatch):
    monkeypatch.chdir(_ROOT)
