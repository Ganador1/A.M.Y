"""
FastAPI application
"""

# Configure environment fallbacks before loading heavy modules
from .utils.hf_safe import configure_offline_mode

configure_offline_mode()

# Apply compatibility patch without importing the whole app surface.
from .core import pydantic_compat  # noqa: F401

# Ensure `app.cache.unified_cache` is importable even if `app.cache` is a
# legacy module (app/cache.py). This registers the submodule under
# `sys.modules` so tests that expect `from app.cache.unified_cache import ...`
# will succeed.
try:
    import importlib.util
    import sys
    from pathlib import Path

    unified_path = Path(__file__).parent / "cache" / "unified_cache.py"
    if unified_path.exists():
        spec = importlib.util.spec_from_file_location("app.cache.unified_cache", str(unified_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore
        sys.modules["app.cache.unified_cache"] = module

        # Ensure 'app.cache' behaves like a package so imports like
        # `from app.cache.unified_cache import ...` succeed even when a
        # legacy module file `app/cache.py` exists.
        try:
            import types
            from app.core.cache import DistributedCache, cache as cache_decorator

            pkg = types.ModuleType("app.cache")
            pkg.__path__ = [str(unified_path.parent)]
            pkg.unified_cache = module
            pkg.DistributedCache = DistributedCache
            pkg.cache = cache_decorator
            sys.modules["app.cache"] = pkg
        except Exception:
            # Best-effort; ignore errors and let imports fail later if needed.
            pass
except Exception:
    # Non-fatal in environments where file missing; imports will fail later.
    pass

# Ensure Decimal context precision is large enough for tests that create Decimals globally
import decimal
if decimal.getcontext().prec < 200:
    decimal.getcontext().prec = 200

# Avoid eager-importing routers/services/database at package import time.
# Many developer workflows import small utilities from `app.*` and shouldn't
# pay the cost of loading the full system (including config validation).
__all__ = [
    "services",
    "routers",
    "middleware",
    "database",
    "service_registry",
]


def __getattr__(name: str):
    if name in {"services", "routers", "middleware", "database"}:
        import importlib

        return importlib.import_module(f"{__name__}.{name}")

    if name == "service_registry":
        try:
            from .infrastructure import service_registry as _service_registry  # type: ignore

            return _service_registry
        except Exception:  # pragma: no cover
            return None

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
