"""
TypedDict definitions for scientific_hypothesis_agent router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process hypothesis agent requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class PolicyDecideResult(TypedDict, total=False):
    """Wrapper sobre PolicyEngineService.decide()."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class VerifyHypothesisWithLiteratureResult(TypedDict, total=False):
    """Response type for verify_hypothesis_with_literature."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class VerifyHypothesisWithKnowledgeResult(TypedDict, total=False):
    """Verificación ampliada usando múltiples fuentes (papers, arXiv, patentes, materiales, ChEMBL)."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateHypothesisResult(TypedDict, total=False):
    """Generate a new scientific hypothesis using prompt registry + local LLM fallback."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateHypothesisLogicResult(TypedDict, total=False):
    """Core logic for hypothesis generation using AI reasoning"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateInsightsResult(TypedDict, total=False):
    """Generate insights from hypotheses and results (lightweight heuristic)"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RefineHypothesesResult(TypedDict, total=False):
    """Refine list of hypotheses based on insights and results"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class StartResearchCycleResult(TypedDict, total=False):
    """Start a complete research cycle for a hypothesis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CreateWorkflowForHypothesisResult(TypedDict, total=False):
    """Create workflow configuration for testing a hypothesis using available ops."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RefineHypothesisResult(TypedDict, total=False):
    """Manually refine a hypothesis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeEvidenceResult(TypedDict, total=False):
    """Analyze evidence for a hypothesis"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CorroborateWithToolsResult(TypedDict, total=False):
    """Invoca orquestador de herramientas para recolectar evidencia externa."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetHypothesisResult(TypedDict, total=False):
    """Get hypothesis details"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListHypothesesResult(TypedDict, total=False):
    """List hypotheses with optional filtering"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

