"""
TypedDict definitions for literature_mining_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetServiceInfoResult(TypedDict, total=False):
    """Get information about literature mining capabilities"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ResultToDictResult(TypedDict, total=False):
    """Convert LiteratureResult to dictionary"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeTemporalTrendsResult(TypedDict, total=False):
    """Analizar tendencias temporales en la literatura"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class IdentifyResearchGapsResult(TypedDict, total=False):
    """Identificar gaps en la investigación actual"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeCollaborationNetworksResult(TypedDict, total=False):
    """Analizar redes de colaboración entre autores"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeMethodologiesResult(TypedDict, total=False):
    """Analizar metodologías utilizadas en la investigación"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeImpactMetricsResult(TypedDict, total=False):
    """Response type for _analyze_impact_metrics."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SynthesizeKeyFindingsResult(TypedDict, total=False):
    """Sintetizar hallazgos clave de la literatura"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateResearchDirectionsResult(TypedDict, total=False):
    """Generar direcciones para investigación futura"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSemanticScholarCitationsResult(TypedDict, total=False):
    """Get citation data from Semantic Scholar API"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetSemanticScholarMetricsResult(TypedDict, total=False):
    """Get detailed metrics from Semantic Scholar API using DOI or title"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExtractKeyConceptsResult(TypedDict, total=False):
    """Extract key concepts from text using NLP (async with CPU executor)"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExtractConceptsSyncResult(TypedDict, total=False):
    """Synchronous concept extraction for CPU executor"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetCitationNetworkResult(TypedDict, total=False):
    """Get citation network for a paper"""
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

