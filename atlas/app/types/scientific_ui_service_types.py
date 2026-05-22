"""
TypedDict definitions for scientific_ui_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class CreateDragDropWorkflowResult(TypedDict, total=False):
    """Create a drag-and-drop workflow interface"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class TranslateNaturalLanguageResult(TypedDict, total=False):
    """Translate natural language query to API calls"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateDomainTemplatesResult(TypedDict, total=False):
    """Generate pre-configured templates for specific domain"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CreateAdaptiveInterfaceResult(TypedDict, total=False):
    """Create adaptive UI based on user profile"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateUiComponentsResult(TypedDict, total=False):
    """Generate UI components for workflow"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SuggestWorkflowFromIntentResult(TypedDict, total=False):
    """Suggest workflow based on detected intent"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateTemplatePreviewResult(TypedDict, total=False):
    """Generate template preview"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetDomainInterfaceConfigResult(TypedDict, total=False):
    """Get domain-specific interface configuration"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

