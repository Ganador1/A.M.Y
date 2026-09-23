"""
TypedDict definitions for router_registry router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class GetRouterInfoResult(TypedDict, total=False):
    """Obtener información de todos los routers disponibles"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

