"""Minimal stub package for COBRApy used in tests to avoid heavy C-extension dependencies.
This stub implements the `io.sbml` interface used during import and provides minimal model objects.
"""
from . import io

__all__ = ["io"]
