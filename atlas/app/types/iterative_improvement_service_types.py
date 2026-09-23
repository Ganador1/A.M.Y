"""
TypedDict definitions for iterative_improvement_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetLearningInsightsResult(TypedDict, total=False):
    """Response type for get_learning_insights."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceHealthResult(TypedDict, total=False):
    """Get service health status"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

