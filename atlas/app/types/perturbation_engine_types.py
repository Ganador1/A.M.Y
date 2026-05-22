"""
TypedDict definitions for perturbation_engine router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process perturbation and sensitivity analysis requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class PerturbParametersResult(TypedDict, total=False):
    """Generate parameter perturbations for reproducibility testing"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SensitivityAnalysisResult(TypedDict, total=False):
    """Perform sensitivity analysis on experimental parameters"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RobustnessAnalysisResult(TypedDict, total=False):
    """Analyze experimental robustness through multiple perturbations"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DetectCriticalConditionsResult(TypedDict, total=False):
    """Detect critical experimental conditions that affect reproducibility"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateRobustnessReportResult(TypedDict, total=False):
    """Generate comprehensive robustness report"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CalculateRobustnessMetricsResult(TypedDict, total=False):
    """Calculate robustness metrics from experiment results"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

