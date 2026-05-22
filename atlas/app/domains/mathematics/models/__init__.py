"""
Modelos del dominio Mathematics
"""

from .requests import (
    BaseRequest,
    ComputationRequest,
    AnalysisRequest,
    ArithmeticRequest,
    CalculusOperationRequest,
    StatisticsRequest,
    OptimizationRequest,
    ValidationRequest,
    ExportRequest,
    EquationRequest,
    CalculusRequest,
    GraphingRequest
)

from .responses import (
    BaseResponse,
    ComputationResponse,
    AnalysisResponse,
    ArithmeticResponse,
    CalculusResult,
    StatisticsResponse,
    OptimizationResponse,
    ValidationResponse,
    ErrorResponse,
    EquationResponse,
    CalculusResponse,
    GraphResponse
)

__all__ = [
    # Requests
    'BaseRequest',
    'ComputationRequest',
    'AnalysisRequest',
    'ArithmeticRequest',
    'CalculusOperationRequest',
    'StatisticsRequest',
    'OptimizationRequest',
    'ValidationRequest',
    'ExportRequest',
    'EquationRequest',
    'CalculusRequest',
    'GraphingRequest',
    # Responses
    'BaseResponse',
    'ComputationResponse',
    'AnalysisResponse',
    'ArithmeticResponse',
    'CalculusResult',
    'StatisticsResponse',
    'OptimizationResponse',
    'ValidationResponse',
    'ErrorResponse',
    'EquationResponse',
    'CalculusResponse',
    'GraphResponse'
]
