"""
TypedDict definitions for experiment_scheduler_v3 router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ParsePayloadResult(TypedDict, total=False):
    """Response type for _parse_payload."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSchedulerMetricsResult(TypedDict, total=False):
    """Get comprehensive scheduler metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ProcessRequestResult(TypedDict, total=False):
    """Response type for process_request."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

