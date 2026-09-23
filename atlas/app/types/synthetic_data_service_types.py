"""
TypedDict definitions for synthetic_data_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class FallbackTabularGenerationResult(TypedDict, total=False):
    """Fallback method for tabular data generation without SDV"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CompareStatisticsResult(TypedDict, total=False):
    """Compare basic statistics between original and synthetic data"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Get service information and capabilities"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

