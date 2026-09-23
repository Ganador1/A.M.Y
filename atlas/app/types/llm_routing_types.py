"""
TypedDict definitions for llm_routing router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetAvailableModelsResult(TypedDict, total=False):
    """Response type for get_available_models."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetRoutingStatsResult(TypedDict, total=False):
    """Response type for get_routing_stats."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class OptimizeRoutingResult(TypedDict, total=False):
    """Response type for optimize_routing."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

