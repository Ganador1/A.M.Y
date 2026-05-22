"""
TypedDict definitions for xray_crystallography_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class LoadCommonPhasesResult(TypedDict, total=False):
    """Load common crystal phase database"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ProcessRequestResult(TypedDict, total=False):
    """Process generic crystallography request"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class HealthCheckResult(TypedDict, total=False):
    """Service health check"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

