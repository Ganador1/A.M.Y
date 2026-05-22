"""
Refined TypedDict definitions for mathlab router responses.

Based on actual return values from mathlab router.
Refined with specific fields and required/optional markers.
"""

from typing import TypedDict, Dict, List, Any, Optional


# Base response structure - common fields
class _MathLabResponseRequired(TypedDict):
    """Required fields for mathlab responses."""
    id: str
    object_id: str


class RegisterObjectResult(_MathLabResponseRequired, total=False):
    """Response for registering a mathematical object.

    Fields:
        id: Unique identifier for the object
        object_id: Alias for id
        semantic_hash: Hash for deduplication
        type: Type of mathematical object
    """
    semantic_hash: str
    type: str


class CreateIntegerResult(_MathLabResponseRequired, total=False):
    """Response for creating an integer object.

    Fields:
        id: Unique identifier
        object_id: Alias for id
        semantic_hash: Hash for deduplication
        type: Object type (e.g., "integer")
    """
    semantic_hash: str
    type: str


class GetObjectResult(TypedDict, total=False):
    """Response for retrieving a mathematical object.

    Returns the full object data including type and properties.
    """
    id: str
    object_id: str
    type: str
    semantic_hash: str
    data: Dict[str, Any]


class ListObjectsResult(TypedDict):
    """Response for listing mathematical objects.

    Fields:
        objects: List of mathematical objects
        total: Total count of objects
    """
    objects: List[Dict[str, Any]]
    total: int


class CreateErGraphResult(_MathLabResponseRequired, total=False):
    """Response for creating an Erdős-Rényi graph.

    Creates a random graph with specified parameters.
    """
    semantic_hash: str
    type: str
    graph_data: Dict[str, Any]


class GraphInvariantsData(TypedDict, total=False):
    """Graph invariants computation data.

    Common graph properties and metrics.
    """
    num_vertices: int
    num_edges: int
    density: float
    diameter: Optional[int]
    average_degree: float
    clustering_coefficient: float


class ComputeGraphInvariantsResult(_MathLabResponseRequired):
    """Response for computing graph invariants.

    Always includes id and invariants data.
    """
    invariants: GraphInvariantsData


class NumberInvariantsData(TypedDict, total=False):
    """Number invariants computation data.

    Mathematical properties of integers.
    """
    value: int
    is_prime: bool
    factors: List[int]
    is_perfect: bool
    divisor_count: int


class ComputeNumberInvariantsResult(_MathLabResponseRequired):
    """Response for computing number invariants.

    Always includes id and invariants data.
    """
    invariants: NumberInvariantsData


class EmbeddingData(TypedDict):
    """Embedding vector data.

    Vector representation in n-dimensional space.
    """
    vector: List[float]
    dimension: int


class GraphEmbeddingResult(_MathLabResponseRequired):
    """Response for graph embedding computation.

    Converts graph structure to vector representation.
    """
    embedding: EmbeddingData


class NumberEmbeddingResult(_MathLabResponseRequired):
    """Response for number embedding computation.

    Converts number to vector representation.
    """
    embedding: EmbeddingData


class BatchJobStatus(TypedDict):
    """Status of a batch computation job.

    Fields:
        job_id: Unique job identifier
        status: Current status ("pending", "running", "completed", "failed")
        total_objects: Total number of objects to process
        processed: Number of objects processed so far
        progress: Progress as fraction (0.0 to 1.0)
    """
    job_id: str
    status: str
    total_objects: int
    processed: int
    progress: float


class BatchComputeInvariantsResult(TypedDict):
    """Response for batch invariants computation.

    Returns job information for tracking.
    """
    job: BatchJobStatus


class SubmitBatchInvariantsResult(TypedDict):
    """Response for submitting batch invariants job.

    Fields:
        job_id: Unique job identifier for tracking
        total_objects: Total objects in the batch
        status: Initial status (usually "pending")
    """
    job_id: str
    total_objects: int
    status: str


class BatchInvariantsStatusResult(TypedDict):
    """Response for checking batch job status.

    Fields:
        job: Current job status
        results: Computation results (if completed)
    """
    job: BatchJobStatus
    results: Optional[List[Dict[str, Any]]]
