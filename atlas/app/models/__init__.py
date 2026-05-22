"""
Models package for Mathematics AI Application
"""

from .models import (
    # Base models
    BaseResponse,

    # Arithmetic models
    ArithmeticOperation,
    ArithmeticResult,

    # Equation models
    EquationRequest,
    EquationResponse,

    # Calculus models
    CalculusRequest,
    CalculusResponse,
    PartialDerivativeRequest,
    PartialDerivativeResponse,
    FourierTransformRequest,
    FourierTransformResponse,

    # Differential Equations models
    DifferentialEquationRequest,
    DifferentialEquationResponse,
    PartialDifferentialEquationRequest,
    PartialDifferentialEquationResponse,

    # Geometry models
    GeometryRequest,
    GeometryResponse,
    ParametricSurfaceRequest,
    ParametricSurfaceResponse,

    # Number Theory models
    NumberTheoryRequest,
    NumberTheoryResult,
    CyclicGroupGeneratorRequest,
    CyclicGroupGeneratorResponse,

    # Optimization models
    OptimizationRequest,
    OptimizationResult,
    QuadraticProgrammingRequest,
    QuadraticProgrammingResponse,

    # Math NLP models
    MathNLPRequest,
    MathNLPResult,

    # Combinatorics models
    CombinatoricsRequest,
    CombinatoricsResult,

    # Statistics models
    StatisticsRequest,
    StatisticsResponse,
    LinearRegressionRequest,
    LinearRegressionResponse,

    # Graphing models
    GraphingRequest,
    GraphResponse,

    # Graph Theory models
    GraphTheoryRequest,
    GraphResult,

    # Cryptography models
    RSAKeyRequest,
    RSAKeyResponse,
    RSAEncryptRequest,
    RSAEncryptResponse,
    RSADecryptRequest,
    RSADecryptResponse,

    # Scientific AI models
    PINNConfig,
    PINNRequest,
    PINNResponse,
    InverseProblemRequest,
    InverseProblemResponse,
    AIAgentRequest,
    AIAgentResponse,
    ScientificReasoningRequest,
    ScientificReasoningResponse,
    PINNOptimizationRequest,
    PINNOptimizationResponse,
)

# Import geometry models from separate file
from .geometry_models import (
    ShapeType,
    GeometryOperation,
    DistanceRequest,
    DistanceResponse,
    IntersectionRequest,
    IntersectionResponse,
    CircleProperties,
    EllipseProperties,
    LineProperties,
    TriangleProperties,
)

# Import database models
from .database_models import (
    User,
    EvaluationRecord,
)

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


# Missing models that services need
class ArithmeticRequest(BaseModel):
    """Model for arithmetic requests"""
    operation: str = Field(..., description="Type of operation")
    operands: List[float] = Field(..., description="List of operands")


class ArithmeticResponse(BaseModel):
    """Model for arithmetic responses"""
    result: float = Field(..., description="Result of the operation")
    operation: str = Field(..., description="Operation performed")
    operands: List[float] = Field(..., description="Operands used")


class OperationType(str, Enum):
    """Enum for operation types"""
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"
    POWER = "power"
    SQRT = "sqrt"
    LOG = "log"
    SIN = "sin"
    COS = "cos"
    TAN = "tan"


# Compatibility models for missing services
class ClaimRecord(BaseModel):
    """Claim record model"""
    id: Optional[str] = None
    claim: str = Field(..., description="The claim text")
    evidence: Optional[str] = None
    confidence: Optional[float] = None
    created_at: Optional[datetime] = None


class DecisionLedgerEntry(BaseModel):
    """Decision ledger entry model"""
    id: Optional[str] = None
    decision: str = Field(..., description="The decision made")
    rationale: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None


class PeerReviewRecord(BaseModel):
    """Peer review record model"""
    id: Optional[str] = None
    paper_id: Optional[str] = None
    reviewer_id: Optional[str] = None
    score: Optional[float] = None
    comments: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class PaperQualityMetrics(BaseModel):
    """Paper quality metrics model"""
    paper_id: Optional[str] = None
    novelty_score: Optional[float] = None
    methodology_score: Optional[float] = None
    clarity_score: Optional[float] = None
    reproducibility_score: Optional[float] = None
    overall_score: Optional[float] = None
    assessment_date: Optional[datetime] = None


class ClaimRelation(BaseModel):
    """Claim relation model"""
    id: Optional[str] = None
    source_claim_id: Optional[str] = None
    target_claim_id: Optional[str] = None
    relation_type: str = Field(..., description="Type of relation")
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

# Ensure BaseResponse exists as a valid Pydantic model in case imports above failed
try:
    _ = BaseResponse  # type: ignore
    if not isinstance(BaseResponse, type) or not issubclass(BaseResponse, BaseModel):
        raise Exception("BaseResponse not a valid BaseModel")
except Exception:
    class BaseResponse(BaseModel):
        """Fallback BaseResponse used when models import fails"""
        success: bool = True
        message: Optional[str] = None
        data: Optional[Any] = None


class ValidationSnapshot(BaseModel):
    """Validation snapshot model"""
    id: Optional[str] = None
    timestamp: Optional[datetime] = None
    validation_results: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


# Export all models
__all__ = [
    # Base models
    "BaseResponse",

    # Database models
    "User",
    "EvaluationRecord",

    # Arithmetic models
    "ArithmeticOperation",
    "ArithmeticResult",
    "ArithmeticRequest",
    "ArithmeticResponse",
    "OperationType",

    # Compatibility models
    "ClaimRecord",
    "DecisionLedgerEntry", 
    "PeerReviewRecord",
    "PaperQualityMetrics",
    "ClaimRelation",
    "ValidationSnapshot",

    # Equation models
    "EquationRequest",
    "EquationResponse",

    # Calculus models
    "CalculusRequest",
    "CalculusResponse",
    "PartialDerivativeRequest",
    "PartialDerivativeResponse",
    "FourierTransformRequest",
    "FourierTransformResponse",

    # Differential Equations models
    "DifferentialEquationRequest",
    "DifferentialEquationResponse",
    "PartialDifferentialEquationRequest",
    "PartialDifferentialEquationResponse",

    # Geometry models
    "GeometryRequest",
    "GeometryResponse",
    "ParametricSurfaceRequest",
    "ParametricSurfaceResponse",
    "ShapeType",
    "GeometryOperation",
    "DistanceRequest",
    "DistanceResponse",
    "IntersectionRequest",
    "IntersectionResponse",
    "CircleProperties",
    "EllipseProperties",
    "LineProperties",
    "TriangleProperties",

    # Number Theory models
    "NumberTheoryRequest",
    "NumberTheoryResult",
    "CyclicGroupGeneratorRequest",
    "CyclicGroupGeneratorResponse",

    # Optimization models
    "OptimizationRequest",
    "OptimizationResult",
    "QuadraticProgrammingRequest",
    "QuadraticProgrammingResponse",

    # Math NLP models
    "MathNLPRequest",
    "MathNLPResult",

    # Combinatorics models
    "CombinatoricsRequest",
    "CombinatoricsResult",

    # Statistics models
    "StatisticsRequest",
    "StatisticsResponse",
    "LinearRegressionRequest",
    "LinearRegressionResponse",

    # Graphing models
    "GraphingRequest",
    "GraphResponse",

    # Graph Theory models
    "GraphTheoryRequest",
    "GraphResult",

    # Cryptography models
    "RSAKeyRequest",
    "RSAKeyResponse",
    "RSAEncryptRequest",
    "RSAEncryptResponse",
    "RSADecryptRequest",
    "RSADecryptResponse",

    # Scientific AI models
    "PINNConfig",
    "PINNRequest",
    "PINNResponse",
    "InverseProblemRequest",
    "InverseProblemResponse",
    "AIAgentRequest",
    "AIAgentResponse",
    "ScientificReasoningRequest",
    "ScientificReasoningResponse",
    "PINNOptimizationRequest",
    "PINNOptimizationResponse",
]
