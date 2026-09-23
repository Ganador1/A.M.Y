"""
TypedDict definitions for counterexample_fuzzer router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class AnalyzeExpressionResult(TypedDict, total=False):
    """Analizar una expresión matemática para extraer variables y tipos"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

