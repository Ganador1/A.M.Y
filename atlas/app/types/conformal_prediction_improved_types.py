"""
TypedDict definitions for conformal_prediction_improved router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class TestExchangeabilityResult(TypedDict, total=False):
    """Test exchangeability assumption"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RunsTestResult(TypedDict, total=False):
    """Wald-Wolfowitz runs test for randomness"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ComputeAutocorrelationResult(TypedDict, total=False):
    """Compute autocorrelation of residuals"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class LjungBoxTestResult(TypedDict, total=False):
    """Ljung-Box test for autocorrelation"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TestHomoscedasticityResult(TypedDict, total=False):
    """Test for homoscedasticity (constant variance)"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetCacheInfoResult(TypedDict, total=False):
    """Get cache information"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

