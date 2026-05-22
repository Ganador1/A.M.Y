"""
TypedDict definitions for scibert_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class AnalyzeScientificTextResult(TypedDict, total=False):
    """Comprehensive scientific text analysis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeDomainOverlapResult(TypedDict, total=False):
    """Analyze overlap between research domains"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AssessImpactPotentialResult(TypedDict, total=False):
    """Assess potential research impact"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackScientificAnalysisResult(TypedDict, total=False):
    """Fallback analysis using keyword matching"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RuleBasedPaperClassificationResult(TypedDict, total=False):
    """Fallback rule-based paper classification"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SimpleResearchSimilarityResult(TypedDict, total=False):
    """Fallback simple research similarity"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Get SciBERT service information"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

