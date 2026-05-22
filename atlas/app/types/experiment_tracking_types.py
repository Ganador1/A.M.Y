"""
TypedDict definitions for experiment_tracking router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process experiment tracking requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class StartExperimentResult(TypedDict, total=False):
    """Start a new scientific experiment"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class LogMetricResult(TypedDict, total=False):
    """Log a metric for an experiment"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class LogParameterResult(TypedDict, total=False):
    """Log a parameter for an experiment"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class LogArtifactResult(TypedDict, total=False):
    """Log an artifact for an experiment"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class EndExperimentResult(TypedDict, total=False):
    """End an experiment"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetExperimentResult(TypedDict, total=False):
    """Get experiment details"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListExperimentsResult(TypedDict, total=False):
    """List all tracked experiments"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CompareExperimentsResult(TypedDict, total=False):
    """Compare multiple experiments"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

