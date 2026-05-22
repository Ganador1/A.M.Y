"""
Modelos de request para el dominio Biology
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime


class BaseRequest(BaseModel):
    """Modelo base para requests del dominio"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_context: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None


class ComputationRequest(BaseRequest):
    """Request para operaciones de computación"""
    operation: str = Field(..., description="Tipo de operación a realizar")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    precision: str = Field(default="float64")
    use_gpu: bool = Field(default=False)


class AnalysisRequest(BaseRequest):
    """Request para análisis de datos"""
    data: Dict[str, Any] = Field(..., description="Datos a analizar")
    analysis_type: str = Field(..., description="Tipo de análisis")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    output_format: str = Field(default="json")


class ValidationRequest(BaseRequest):
    """Request para validación de datos"""
    data: Dict[str, Any] = Field(..., description="Datos a validar")
    schema_name: str = Field(..., description="Esquema de validación")
    strict_mode: bool = Field(default=True)


class ExportRequest(BaseRequest):
    """Request para exportar resultados"""
    data: Dict[str, Any] = Field(..., description="Datos a exportar")
    format: str = Field(default="json", description="Formato de exportación")
    include_metadata: bool = Field(default=True)
