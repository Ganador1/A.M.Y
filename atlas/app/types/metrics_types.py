"""
TypedDict definitions for metrics router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetMetricsResult(TypedDict, total=False):
    """Get custom metrics in JSON format"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSystemMetricsEndpointResult(TypedDict, total=False):
    """Get detailed system metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetDatabaseMetricsResult(TypedDict, total=False):
    """Get database-specific metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetToolAdaptersMetricsResult(TypedDict, total=False):
    """Get tool adapters metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetMedicalImagingMetricsResult(TypedDict, total=False):
    """Get medical imaging metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExportMetricsResult(TypedDict, total=False):
    """Export metrics to JSON file"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetMetricsSummaryResult(TypedDict, total=False):
    """Get a human-readable summary of current metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetHealthWithMetricsResult(TypedDict, total=False):
    """Get health status integrated with metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetPerformanceMetricsResult(TypedDict, total=False):
    """Get performance-specific metrics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ResetMetricsResult(TypedDict, total=False):
    """Reset all metrics (admin endpoint)"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

