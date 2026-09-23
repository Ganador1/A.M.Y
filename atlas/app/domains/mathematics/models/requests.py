"""
Modelos de request para el dominio Mathematics
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


class ArithmeticRequest(BaseRequest):
    """Request para operaciones aritméticas"""
    operation: str = Field(..., description="Operación aritmética (+, -, *, /, pow, sqrt, etc.)")
    operands: List[float] = Field(..., description="Operandos para la operación")
    precision: Optional[int] = Field(default=6, description="Precisión decimal")


class CalculusOperationRequest(BaseRequest):
    """Request para operaciones de cálculo"""
    expression: str = Field(..., description="Expresión matemática")
    operation: str = Field(..., description="Tipo de operación (derivative, integral, limit)")
    variable: str = Field(default="x", description="Variable principal")
    order: int = Field(default=1, description="Orden de la operación")
    limits: Optional[List[float]] = Field(None, description="Límites para integrales")
    point: Optional[float] = Field(default=0.0, description="Punto para límites o series")


class StatisticsRequest(BaseRequest):
    """Request para análisis estadístico"""
    data: List[float] = Field(..., description="Datos para análisis")
    operations: List[str] = Field(..., description="Operaciones estadísticas a realizar")
    confidence_level: float = Field(default=0.95, description="Nivel de confianza")


class OptimizationRequest(BaseRequest):
    """Request para optimización"""
    objective_function: str = Field(..., description="Función objetivo")
    variables: List[str] = Field(..., description="Variables de decisión")
    constraints: Optional[List[str]] = Field(None, description="Restricciones")
    bounds: Optional[Dict[str, List[float]]] = Field(None, description="Límites de variables")


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


class EquationRequest(BaseRequest):
    """Request para resolver ecuaciones"""
    equation: str = Field(..., description="Ecuación matemática a resolver")
    variable: str = Field(default="x", description="Variable a resolver")
    method: Optional[str] = Field(default="auto", description="Método de resolución")


class CalculusRequest(BaseRequest):
    """Request para operaciones de cálculo"""
    expression: str = Field(..., description="Expresión matemática")
    operation: str = Field(..., description="Tipo de operación (derivative, integral)")
    variable: str = Field(default="x", description="Variable principal")
    order: Optional[int] = Field(default=1, description="Orden de la derivada")
    limits: Optional[List[float]] = Field(None, description="Límites para integral definida")


class GraphingRequest(BaseRequest):
    """Request para generar gráficos"""
    expression: str = Field(..., description="Expresión matemática a graficar")
    variable: str = Field(default="x", description="Variable independiente")
    x_min: float = Field(default=-10, description="Valor mínimo de x")
    x_max: float = Field(default=10, description="Valor máximo de x")
    points: int = Field(default=1000, description="Número de puntos")
    title: Optional[str] = Field(None, description="Título del gráfico")