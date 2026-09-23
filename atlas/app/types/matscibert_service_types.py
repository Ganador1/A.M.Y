"""
TypedDict definitions for matscibert_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class AnalyzeMaterialsTextResult(TypedDict, total=False):
    """Comprehensive materials science text analysis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExtractSynthesisInfoResult(TypedDict, total=False):
    """Extract synthesis and processing information"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateMaterialsSummaryResult(TypedDict, total=False):
    """Generate summary of materials analysis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FallbackMaterialsAnalysisResult(TypedDict, total=False):
    """Fallback analysis using keyword matching"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SimpleMaterialsSimilarityResult(TypedDict, total=False):
    """Fallback simple materials similarity"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Get MatSciBERT service information"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

