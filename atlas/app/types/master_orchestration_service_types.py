"""
TypedDict definitions for master_orchestration_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Response type for process_request."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Get information about orchestration capabilities"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ResolveParameterReferencesResult(TypedDict, total=False):
    """Resolve parameter references to previous task results with advanced path traversal"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetPipelineStatusResult(TypedDict, total=False):
    """Get status of a specific pipeline"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TaskToDictResult(TypedDict, total=False):
    """Convert task to dictionary"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

