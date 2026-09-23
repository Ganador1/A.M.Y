"""
TypedDict definitions for structural_db router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetPdbResult(TypedDict, total=False):
    """Fetch PDB file (async)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetUniprotResult(TypedDict, total=False):
    """Fetch UniProt metadata (async)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetAlphafoldResult(TypedDict, total=False):
    """Fetch AlphaFold prediction (async)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SequenceSearchResult(TypedDict, total=False):
    """Search similar structures by sequence (async)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

