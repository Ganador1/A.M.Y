"""
TypedDict definitions for multi_agent_coordinator router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class LoadYamlResult(TypedDict, total=False):
    """Response type for _load_yaml."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ReloadConfigurationResult(TypedDict, total=False):
    """Recarga agents.yaml y models.yaml en caliente."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RunPipelineResult(TypedDict, total=False):
    """Response type for run_pipeline."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class RunPipelineIntegratedAsyncResult(TypedDict, total=False):
    """Pipeline profundo que integra ScientificHypothesisAgent + ToolEvidenceOrchestrator."""
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


class HandleDomainRequestResult(TypedDict, total=False):
    """Response type for handle_domain_request."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

