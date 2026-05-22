"""
TypedDict definitions for lab_automation router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class HealthResult(TypedDict, total=False):
    """Response type for health."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RunPcrResult(TypedDict, total=False):
    """Response type for run_pcr."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RunElisaResult(TypedDict, total=False):
    """Response type for run_elisa."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

