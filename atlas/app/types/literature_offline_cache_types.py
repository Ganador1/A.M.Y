"""
TypedDict definitions for literature_offline_cache router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class SaveContentResult(TypedDict, total=False):
    """Save content to compressed file"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetStatsResult(TypedDict, total=False):
    """Get cache statistics (async)"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetBatchResult(TypedDict, total=False):
    """Response type for get_batch."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

