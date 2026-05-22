"""Compatibility entrypoint for the refactored FastAPI application.

Historically the project exposed the modular app from ``main_refactored.py``.
The current implementation lives in ``main.py``, but docs, scripts, tests and
developer workflows still import ``main_refactored``. Keep this shim so those
entrypoints remain valid.
"""

from __future__ import annotations

import main as _main

app = _main.app


def __getattr__(name: str):
    return getattr(_main, name)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_refactored:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True,
        access_log=True,
    )
