"""
TypedDict definitions for health_checks router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class HealthCheckResult(TypedDict, total=False):
    """Basic health check endpoint"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class HealthCheckNoSlashResult(TypedDict, total=False):
    """Response type for health_check_no_slash."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DetailedHealthCheckResult(TypedDict, total=False):
    """Comprehensive health check with all system components"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DatabaseHealthCheckResult(TypedDict, total=False):
    """Enhanced database health check with comprehensive monitoring"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ToolAdaptersHealthCheckResult(TypedDict, total=False):
    """Tool adapters health check"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class MedicalImagingHealthCheckResult(TypedDict, total=False):
    """Medical imaging system health check"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SystemHealthCheckResult(TypedDict, total=False):
    """System resources health check"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ResetDatabaseHealthResult(TypedDict, total=False):
    """Reset database health status (admin endpoint)"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetToolAdaptersStatusResult(TypedDict, total=False):
    """Get status of all tool adapters"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetMedicalImagingStatusResult(TypedDict, total=False):
    """Get medical imaging system status"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSystemResourcesResult(TypedDict, total=False):
    """Get detailed system resource information"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

