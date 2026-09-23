"""
TypedDict definitions for sequence_oeis router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class OeisSearchResult(TypedDict, total=False):
    """Response type for oeis_search."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

