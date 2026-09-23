"""
TypedDict definitions for experimental_protocols router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class ProcessRequestResult(TypedDict, total=False):
    """Process protocol requests"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListProtocolsResult(TypedDict, total=False):
    """List available protocols"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetProtocolResult(TypedDict, total=False):
    """Get detailed protocol information"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CreateProtocolResult(TypedDict, total=False):
    """Create a new protocol"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ValidateProtocolResult(TypedDict, total=False):
    """Validate a protocol"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ExecuteProtocolResult(TypedDict, total=False):
    """Execute a protocol"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetExecutionStatusResult(TypedDict, total=False):
    """Get execution status"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ConvertProtocolResult(TypedDict, total=False):
    """Convert protocol between formats"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ParseHumanProtocolResult(TypedDict, total=False):
    """Parsea un protocolo en texto humano a estructura ejecutable"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class OptimizeProtocolResult(TypedDict, total=False):
    """Optimiza parámetros del protocolo en base a resultados/objetivos"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

