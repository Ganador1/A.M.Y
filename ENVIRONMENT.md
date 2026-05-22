# A.M.Y Environment Layout

A.M.Y uses **two Python environments** by design. They are not interchangeable.

## 1. `/Volumes/Ganador disk/A.M.Y/.venv` — A.M.Y runtime

- **Python**: 3.14.3
- **Purpose**: Runs the A.M.Y cognitive cycle, heartbeat, memory, paper generation, tests.
- **Install**: `pip install -r requirements.txt && pip install pytest pytest-asyncio`
- **Used by**: `amy.py`, `run_amy_*.py`, all `test_*.py` in repo root.

## 2. `/Volumes/Ganador disk/A.M.Y/atlas/.venv_new` — Atlas worker

- **Python**: 3.13.5 (Atlas scientific libs do not yet support 3.14)
- **Purpose**: Runs Atlas tools (sympy, rdkit, brian2, libsbml, scipy, etc.) as subprocess workers spawned by A.M.Y.
- **Install**: `cd atlas && pip install -r requirements.txt`
- **Referenced by**: `core/atlas_tools.py` (ATLAS_VENV_PYTHON), `core/atlas_bridge.py`.

## 3. `atlas/.venv` — DEPRECATED

The older `atlas/.venv` (4.1 GB) is no longer referenced by any A.M.Y code. Safe to delete:

```bash
rm -rf atlas/.venv
```

## Why two environments?

A.M.Y subprocess-spawns Atlas tools to keep scientific computations isolated from cognitive state. The version split is forced by ecosystem compatibility (Python 3.14 is too new for parts of the science stack).

## Quick sanity check

```bash
# A.M.Y venv runs tests:
.venv/bin/python -m pytest test_atlas_misuse_guard.py -q

# Atlas venv runs tools:
atlas/.venv_new/bin/python -c "import sympy, numpy, scipy; print('OK')"
```
