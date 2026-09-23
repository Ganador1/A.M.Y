"""
TypedDict definitions for statistical_validation router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class CalculatePowerAnalysisResult(TypedDict, total=False):
    """Response type for calculate_power_analysis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CorrectMultipleTestingResult(TypedDict, total=False):
    """Response type for correct_multiple_testing."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CalculateEffectSizesResult(TypedDict, total=False):
    """Response type for calculate_effect_sizes."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetValidationConfigResult(TypedDict, total=False):
    """Response type for get_validation_config."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

