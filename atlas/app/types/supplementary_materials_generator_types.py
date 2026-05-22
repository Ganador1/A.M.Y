"""
TypedDict definitions for supplementary_materials_generator router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process supplementary materials generation requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateSupplementaryPackageResult(TypedDict, total=False):
    """Generate complete supplementary materials package"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateExtendedMethodsResult(TypedDict, total=False):
    """Generate extended methods document"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateSupplementaryDataResult(TypedDict, total=False):
    """Generate supplementary data document"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateProtocolResult(TypedDict, total=False):
    """Generate detailed experimental protocol"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateSupplementaryFigureResult(TypedDict, total=False):
    """Generate supplementary figure document"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GenerateSupplementaryTableResult(TypedDict, total=False):
    """Generate supplementary table document"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

