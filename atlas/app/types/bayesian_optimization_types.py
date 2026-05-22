"""
TypedDict definitions for bayesian_optimization router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process Bayesian optimization requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CreateOptimizerResult(TypedDict, total=False):
    """Create a new Bayesian optimizer"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RunOptimizationResult(TypedDict, total=False):
    """Run complete Bayesian optimization"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SuggestNextPointResult(TypedDict, total=False):
    """Suggest next point for evaluation"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AddObservationResult(TypedDict, total=False):
    """Add observation to optimizer"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetOptimizerStatusResult(TypedDict, total=False):
    """Get optimizer status"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetOptimizationResultsResult(TypedDict, total=False):
    """Get optimization results"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class OptimizeDesignResult(TypedDict, total=False):
    """High-level method for design optimization"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

