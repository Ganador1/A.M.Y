"""Helpers to load the real matplotlib package when the repo ships local stubs."""

from __future__ import annotations

from pathlib import Path
import sys
from types import ModuleType


_REPO_ROOT = Path(__file__).resolve().parents[2]


def _matplotlib_module_names() -> list[str]:
    return [
        name
        for name in list(sys.modules)
        if name == "matplotlib"
        or name.startswith("matplotlib.")
        or name == "mpl_toolkits"
        or name.startswith("mpl_toolkits.")
    ]


def ensure_real_matplotlib() -> ModuleType:
    """Import matplotlib from site-packages instead of the repository stubs."""
    existing = sys.modules.get("matplotlib")
    existing_origin = str(getattr(existing, "__file__", "") or "")
    if existing and "site-packages/matplotlib" in existing_origin:
        return existing

    original_path = list(sys.path)
    removed_modules = {name: sys.modules[name] for name in _matplotlib_module_names()}
    try:
        for bad in ("", str(_REPO_ROOT)):
            while bad in sys.path:
                sys.path.remove(bad)
        for name in _matplotlib_module_names():
            sys.modules.pop(name, None)

        import matplotlib  # type: ignore

        matplotlib.use("Agg")
        return matplotlib
    except Exception:
        for name in _matplotlib_module_names():
            sys.modules.pop(name, None)
        sys.modules.update(removed_modules)
        raise
    finally:
        sys.path[:] = original_path


def get_real_pyplot() -> ModuleType:
    """Return matplotlib.pyplot from the real installed package."""
    original_path = list(sys.path)
    removed_modules = {name: sys.modules[name] for name in _matplotlib_module_names()}
    try:
        for bad in ("", str(_REPO_ROOT)):
            while bad in sys.path:
                sys.path.remove(bad)
        for name in _matplotlib_module_names():
            sys.modules.pop(name, None)

        import matplotlib  # type: ignore
        import matplotlib.pyplot as plt  # type: ignore

        matplotlib.use("Agg")
        return plt
    except Exception:
        for name in _matplotlib_module_names():
            sys.modules.pop(name, None)
        sys.modules.update(removed_modules)
        raise
    finally:
        sys.path[:] = original_path
