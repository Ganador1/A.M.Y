"""Compatibility import for the paper audit tool."""

from scripts.analysis import audit_papers as _impl

globals().update(
    {
        name: value
        for name, value in vars(_impl).items()
        if not name.startswith("__")
    }
)

__all__ = [name for name in globals() if not name.startswith("__")]
