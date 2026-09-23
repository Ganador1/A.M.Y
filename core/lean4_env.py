"""
Lean 4 & Mathlib Environment Resolution Utility.

Provides robust detection of Lean 4 / Lake binaries, toolchain paths,
and constructs canonical LEAN_PATH / LEAN_SRC_PATH pointing to precompiled
Mathlib and dependency packages in the repository.
"""
from __future__ import annotations

import functools
import os
import shutil
from pathlib import Path
from typing import Optional, List, Dict


def find_lean_project_dir() -> Optional[Path]:
    """Find the Lean 4 project directory containing lakefile and .lake packages."""
    candidates = [
        # Explicit env override
        Path(os.environ["LEAN_PROJECT_DIR"]) if "LEAN_PROJECT_DIR" in os.environ else None,
        # Standard repository relative paths
        Path(__file__).resolve().parents[4] / "formal" / "lean",
        Path(__file__).resolve().parents[3] / "formal" / "lean",
        Path("/workspace/A.M.Y/formal/lean"),
        Path.cwd() / "formal" / "lean",
        Path.cwd() if ((Path.cwd() / "lakefile.toml").exists() or (Path.cwd() / "lakefile.lean").exists()) else None,
    ]
    for c in candidates:
        if c and c.exists() and ((c / "lakefile.toml").exists() or (c / "lakefile.lean").exists()):
            return c.resolve()
    return None


def find_lean_binary() -> Optional[str]:
    """Return path to lean executable or None."""
    # 1. Environment variable override
    env_bin = os.getenv("LEAN_BIN")
    if env_bin and os.path.isfile(env_bin) and os.access(env_bin, os.X_OK):
        return env_bin

    # 2. Known elan locations
    candidates = [
        os.path.expanduser("~/.elan/bin/lean"),
        "/workspace/.amy-toolchains/elan/bin/lean",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c

    # 3. Path lookup
    which = shutil.which("lean")
    if which:
        return which

    return None


def find_lake_binary() -> Optional[str]:
    """Return path to lake executable or None."""
    env_bin = os.getenv("LAKE_BIN")
    if env_bin and os.path.isfile(env_bin) and os.access(env_bin, os.X_OK):
        return env_bin

    candidates = [
        os.path.expanduser("~/.elan/bin/lake"),
        "/workspace/.amy-toolchains/elan/bin/lake",
    ]
    for c in candidates:
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c

    which = shutil.which("lake")
    if which:
        return which

    return None


@functools.lru_cache(maxsize=1)
def resolve_lean_search_paths() -> tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Discover all LEAN_PATH (.olean directories) and LEAN_SRC_PATH directories.
    Returns (lean_paths_tuple, lean_src_paths_tuple).
    """
    lean_paths: List[str] = []
    lean_src_paths: List[str] = []

    # 1. Existing LEAN_PATH from environment
    if "LEAN_PATH" in os.environ:
        for p in os.environ["LEAN_PATH"].split(os.pathsep):
            p = p.strip()
            if p and os.path.isdir(p) and p not in lean_paths:
                lean_paths.append(p)

    # 2. Search packages in formal/lean/.lake/packages
    proj_dir = find_lean_project_dir()
    if proj_dir:
        packages_dir = proj_dir / ".lake" / "packages"
        if packages_dir.exists():
            for pkg in sorted(packages_dir.iterdir()):
                if not pkg.is_dir():
                    continue
                # Compiled olean path
                lib_lean = pkg / ".lake" / "build" / "lib" / "lean"
                if lib_lean.exists():
                    lean_paths.append(str(lib_lean))
                # Source path
                lean_src_paths.append(str(pkg))

        # Project's own build output and source
        proj_lib = proj_dir / ".lake" / "build" / "lib" / "lean"
        if proj_lib.exists():
            lean_paths.append(str(proj_lib))
        lean_src_paths.append(str(proj_dir))

    # 3. Toolchain lib/lean
    elan_roots = [
        Path(os.path.expanduser(os.getenv("ELAN_HOME", "~/.elan"))),
        Path("/workspace/.amy-toolchains/elan"),
    ]
    for elan_root in elan_roots:
        tc_dir = elan_root / "toolchains"
        if tc_dir.exists():
            for tc in sorted(tc_dir.glob("leanprover--lean4*")):
                lib_lean = tc / "lib" / "lean"
                if lib_lean.exists() and str(lib_lean) not in lean_paths:
                    lean_paths.append(str(lib_lean))

    # Deduplicate while preserving order
    deduped_paths: List[str] = []
    seen = set()
    for p in lean_paths:
        if p not in seen:
            seen.add(p)
            deduped_paths.append(p)

    deduped_src: List[str] = []
    seen_src = set()
    for p in lean_src_paths:
        if p not in seen_src:
            seen_src.add(p)
            deduped_src.append(p)

    return tuple(deduped_paths), tuple(deduped_src)


def get_lean_env(base_env: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Construct an execution environment dictionary with LEAN_PATH, LEAN_SRC_PATH,
    ELAN_HOME, and PATH properly configured for Lean 4 and Mathlib.
    """
    env = dict(base_env if base_env is not None else os.environ)
    lean_paths, lean_src_paths = resolve_lean_search_paths()

    if lean_paths:
        env["LEAN_PATH"] = os.pathsep.join(lean_paths)
    if lean_src_paths:
        env["LEAN_SRC_PATH"] = os.pathsep.join(lean_src_paths)

    # Elan home
    if "ELAN_HOME" not in env:
        elan_home = os.path.expanduser("~/.elan")
        if not os.path.exists(elan_home) and os.path.exists("/workspace/.amy-toolchains/elan"):
            elan_home = "/workspace/.amy-toolchains/elan"
        env["ELAN_HOME"] = elan_home

    # Ensure elan bin is in PATH
    elan_bin = str(Path(env["ELAN_HOME"]) / "bin")
    cur_path = env.get("PATH", "")
    if elan_bin not in cur_path.split(os.pathsep):
        env["PATH"] = f"{elan_bin}{os.pathsep}{cur_path}" if cur_path else elan_bin

    return env


def is_mathlib_available() -> bool:
    """Check if Mathlib.olean is present in any configured LEAN_PATH entry."""
    lean_paths, _ = resolve_lean_search_paths()
    for p in lean_paths:
        if (Path(p) / "Mathlib.olean").exists() or (Path(p) / "Mathlib").is_dir():
            return True
    return False
