"""
TypedDict definitions for structural_database_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class FetchPdbResult(TypedDict, total=False):
    """Response type for fetch_pdb."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FetchUniprotResult(TypedDict, total=False):
    """Response type for fetch_uniprot."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FetchAlphafoldPredictionResult(TypedDict, total=False):
    """Response type for fetch_alphafold_prediction."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SearchSimilarStructuresResult(TypedDict, total=False):
    """Response type for search_similar_structures."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FetchPdbBatchResult(TypedDict, total=False):
    """Response type for fetch_pdb_batch."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FetchUniprotBatchResult(TypedDict, total=False):
    """Response type for fetch_uniprot_batch."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class FetchAlphafoldBatchResult(TypedDict, total=False):
    """Response type for fetch_alphafold_batch."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

