"""
TypedDict definitions for uncertainty_quantification router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class MonteCarloUncertaintyResult(TypedDict, total=False):
    """Response type for monte_carlo_uncertainty."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class EnsembleUncertaintyResult(TypedDict, total=False):
    """Response type for ensemble_uncertainty."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ConformalPredictionResult(TypedDict, total=False):
    """Response type for conformal_prediction."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class BootstrapUncertaintyResult(TypedDict, total=False):
    """Response type for bootstrap_uncertainty."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CompareUncertaintyMethodsResult(TypedDict, total=False):
    """Response type for compare_uncertainty_methods."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetAvailableMethodsResult(TypedDict, total=False):
    """Response type for get_available_methods."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

