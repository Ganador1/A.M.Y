"""
TypedDict definitions for virtual_microscopes router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process microscope requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListMicroscopesResult(TypedDict, total=False):
    """List available microscopes"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CaptureImageResult(TypedDict, total=False):
    """Capture an image with a microscope"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeImageResult(TypedDict, total=False):
    """Analyze a microscope image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeOpticalImageResult(TypedDict, total=False):
    """Analyze optical microscope image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeConfocalImageResult(TypedDict, total=False):
    """Analyze confocal microscope image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeElectronImageResult(TypedDict, total=False):
    """Analyze electron microscope image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeFluorescenceImageResult(TypedDict, total=False):
    """Analyze fluorescence microscope image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzePhaseContrastImageResult(TypedDict, total=False):
    """Analyze phase contrast image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeDicImageResult(TypedDict, total=False):
    """Analyze DIC image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzeStedImageResult(TypedDict, total=False):
    """Analyze STED image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class AnalyzePalmImageResult(TypedDict, total=False):
    """Analyze PALM image"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

