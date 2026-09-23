"""
Modelos de response para el dominio Mathematics
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseResponse(BaseModel):
    """Modelo base para responses del dominio"""
    success: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    execution_time: Optional[float] = None
    trace_id: Optional[str] = None


class ComputationResponse(BaseResponse):
    """Response para operaciones de computación"""
    result: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)


class AnalysisResponse(BaseResponse):
    """Response para análisis de datos"""
    analysis_result: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    statistics: Optional[Dict[str, Any]] = None
    visualizations: List[str] = Field(default_factory=list)


class ArithmeticResponse(BaseResponse):
    """Response para operaciones aritméticas"""
    operation: str
    operands: List[float]
    result: float
    formatted_result: str
    precision: int


class CalculusResult(BaseResponse):
    """Response para operaciones de cálculo"""
    expression: str
    operation: str
    result: str
    explanation: str
    computation_time_ms: float
    symbolic: bool = True
    numerical_value: Optional[float] = None


class StatisticsResponse(BaseResponse):
    """Response para análisis estadístico"""
    data_summary: Dict[str, Any]
    results: Dict[str, Any]
    confidence_intervals: Optional[Dict[str, Any]] = None
    tests_performed: List[str] = Field(default_factory=list)


class OptimizationResponse(BaseResponse):
    """Response para optimización"""
    objective_value: float
    optimal_solution: Dict[str, Any]
    convergence_info: Dict[str, Any]
    iterations: int
    method_used: str


class ValidationResponse(BaseResponse):
    """Response para validación de datos"""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseResponse):
    """Response para errores"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None


class EquationResponse(BaseResponse):
    """Response para resolución de ecuaciones"""
    equation: str
    variable: str
    solutions: List[Any]
    solution_type: str
    steps: List[str]


class CalculusResponse(BaseResponse):
    """Response para operaciones de cálculo"""
    original_expression: str
    result: str
    operation: str
    variable: str
    steps: List[str]


class GraphResponse(BaseResponse):
    """Response para gráficos generados"""
    expression: str
    image_path: str
    x_range: List[float]
    y_range: List[float]
    points_count: int