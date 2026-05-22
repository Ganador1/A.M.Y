"""
TypedDict definitions for ai_scientist_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetServiceInfoResult(TypedDict, total=False):
    """Get information about AI Scientist capabilities"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateResearchHypothesisResult(TypedDict, total=False):
    """Generate a novel research hypothesis in the specified domain"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DesignExperimentResult(TypedDict, total=False):
    """Design an experiment to test the given hypothesis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ConductLiteratureReviewResult(TypedDict, total=False):
    """Conduct automated literature review"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TrackResearchProgressResult(TypedDict, total=False):
    """Track progress of ongoing research"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListActiveResearchResult(TypedDict, total=False):
    """List all active research projects"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExportPaperResult(TypedDict, total=False):
    """Export paper in specified format"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateHypothesisTemplateResult(TypedDict, total=False):
    """Generate hypothesis using template-based approach"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeLiteratureTemplateResult(TypedDict, total=False):
    """Analyze literature using template approach"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CalculateDescriptiveStatsResult(TypedDict, total=False):
    """Calculate comprehensive descriptive statistics"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeTrendsResult(TypedDict, total=False):
    """Analyze temporal trends in the data"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DecomposeSeasonalityResult(TypedDict, total=False):
    """Decompose time series into trend, seasonal, and residual components"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TestStationarityResult(TypedDict, total=False):
    """Perform stationarity tests on time series data"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateForecastsResult(TypedDict, total=False):
    """Generate forecasts using multiple methods"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class DetectAnomaliesResult(TypedDict, total=False):
    """Detect anomalies in time series data"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FilterInsightsByConfidenceResult(TypedDict, total=False):
    """Filter insights by confidence threshold"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class LimitInsightsResult(TypedDict, total=False):
    """Limit the number of insights returned"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateScientificInsightsResult(TypedDict, total=False):
    """Generate scientific insights from time series analysis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ProcessRequestResult(TypedDict, total=False):
    """Response type for process_request."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

