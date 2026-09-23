"""
TypedDict definitions for advanced_cloud_lab router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class AdvancedCloudLabHealthResult(TypedDict, total=False):
    """Health check para Cloud Lab avanzado"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetAvailableProtocolsResult(TypedDict, total=False):
    """Response type for get_available_protocols."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SubmitExperimentResult(TypedDict, total=False):
    """Response type for submit_experiment."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class MonitorExperimentResult(TypedDict, total=False):
    """Response type for monitor_experiment."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetExperimentResultsResult(TypedDict, total=False):
    """Response type for get_experiment_results."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

