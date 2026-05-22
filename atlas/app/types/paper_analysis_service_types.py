"""
TypedDict definitions for paper_analysis_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class RedFlagsResult(TypedDict, total=False):
    """Response type for _red_flags."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class MapClaimsToHypothesisResult(TypedDict, total=False):
    """Crea ClaimRelation supports cuando core claim contiene alguna variable de la hipótesis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzePapersResult(TypedDict, total=False):
    """Response type for analyze_papers."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

