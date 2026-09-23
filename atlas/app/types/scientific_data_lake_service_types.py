"""
TypedDict definitions for scientific_data_lake_service router responses.

NOTE: This is a first-pass auto-generation.
TODO: Refine types based on actual return values.
"""

from typing import TypedDict, Dict, List, Any, Optional


class SafeCopyLocalResult(TypedDict, total=False):
    """Response type for _safe_copy_local."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class CopyFromS3Result(TypedDict, total=False):
    """Response type for _copy_from_s3."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class GetServiceInfoResult(TypedDict, total=False):
    """Response type for get_service_info."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class IngestResult(TypedDict, total=False):
    """Ingest a file from local path or s3:// URI into the managed lake and"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class ListEntriesResult(TypedDict, total=False):
    """List datasets from DB and (optionally) the filesystem"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class SampleResult(TypedDict, total=False):
    """Return a lightweight sample/preview of a dataset file"""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str


class StatResult(TypedDict, total=False):
    """Return basic statistics for a file within the lake."""
    success: bool
    message: str
    data: Dict[str, Any]  # TODO: Specify data structure
    error: str
    timestamp: str

