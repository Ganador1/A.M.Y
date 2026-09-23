"""
TypedDict definitions for tool_evidence_orchestrator router responses.

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


class CorroborateResult(TypedDict, total=False):
    """Response type for _corroborate."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExecuteSpecResult(TypedDict, total=False):
    """Response type for _execute_spec."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RunInternalActionResult(TypedDict, total=False):
    """Ejecuta acciones internas sin process_request estandar."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ResolveParamsResult(TypedDict, total=False):
    """Response type for _resolve_params."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TruncateResult(TypedDict, total=False):
    """Response type for _truncate."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

