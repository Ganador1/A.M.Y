"""
TypedDict definitions for scientific_hypothesis router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GenerateHypothesisOllamaResult(TypedDict, total=False):
    """Response type for generate_hypothesis_ollama."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateHypothesisResult(TypedDict, total=False):
    """Response type for generate_hypothesis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class StartResearchCycleResult(TypedDict, total=False):
    """Response type for start_research_cycle."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RefineHypothesisResult(TypedDict, total=False):
    """Response type for refine_hypothesis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeEvidenceResult(TypedDict, total=False):
    """Response type for analyze_evidence."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetHypothesisResult(TypedDict, total=False):
    """Response type for get_hypothesis."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListHypothesesResult(TypedDict, total=False):
    """Response type for list_hypotheses."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class HealthCheckResult(TypedDict, total=False):
    """Health check for the Scientific Hypothesis Agent service"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetStatsResult(TypedDict, total=False):
    """Get statistics about the Scientific Hypothesis Agent"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

