"""
Modelos de response para el dominio Engineering
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
