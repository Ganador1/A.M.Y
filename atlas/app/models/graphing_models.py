"""
Modelos para graficado 3D y avanzado
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class Graph3DRequest(BaseModel):
    """Solicitud para gráfico 3D"""
    expression: str = Field(..., description="Expresión matemática con variables x e y")
    x_min: float = Field(-5, description="Valor mínimo de x")
    x_max: float = Field(5, description="Valor máximo de x")
    y_min: float = Field(-5, description="Valor mínimo de y")
    y_max: float = Field(5, description="Valor máximo de y")
    points: int = Field(50, description="Número de puntos por eje")
    colorscale: Optional[str] = Field(None, description="Escala de colores para la superficie (ej. 'Viridis', 'Plasma')")
    opacity: Optional[float] = Field(None, description="Opacidad de la superficie (0.0 a 1.0)")


class PolarGraphRequest(BaseModel):
    """Solicitud para gráfico polar"""
    expression: str = Field(..., description="Expresión en términos de theta")
    theta_min: float = Field(0, description="Valor mínimo de theta")
    theta_max: float = Field(6.28, description="Valor máximo de theta (2*pi)")
    points: int = Field(1000, description="Número de puntos")


class MultipleGraphRequest(BaseModel):
    """Solicitud para múltiples gráficos"""
    expressions: List[str] = Field(..., description="Lista de expresiones matemáticas")
    x_min: float = Field(-10, description="Valor mínimo de x")
    x_max: float = Field(10, description="Valor máximo de x")
    points: int = Field(1000, description="Número de puntos")
    variable: str = Field('x', description="Variable independiente")


class ParametricGraphRequest(BaseModel):
    """Solicitud para gráfico paramétrico"""
    x_expr: str = Field(..., description="Expresión paramétrica para x")
    y_expr: str = Field(..., description="Expresión paramétrica para y")
    z_expr: Optional[str] = Field(None, description="Expresión paramétrica para z (3D)")
    t_min: float = Field(0, description="Valor mínimo del parámetro t")
    t_max: float = Field(6.28, description="Valor máximo del parámetro t")
    points: int = Field(1000, description="Número de puntos")


class GraphResponse(BaseModel):
    """Respuesta con información del gráfico"""
    expression: str = Field(..., description="Expresión graficada")
    image_path: str = Field(..., description="Ruta del archivo de imagen")
    x_range: List[float] = Field(..., description="Rango de x")
    y_range: Optional[List[float]] = Field(None, description="Rango de y")
    points_count: int = Field(..., description="Número de puntos")

class SurfaceData(BaseModel):
    expression: str = Field(..., description="Expresión matemática para la superficie")
    x_min: float = Field(-5, description="Valor mínimo de x")
    x_max: float = Field(5, description="Valor máximo de x")
    y_min: float = Field(-5, description="Valor mínimo de y")
    y_max: float = Field(5, description="Valor máximo de y")
    colorscale: Optional[str] = Field(None, description="Escala de colores para la superficie")
    opacity: Optional[float] = Field(None, description="Opacidad de la superficie")

class MultiSurface3DRequest(BaseModel):
    """Solicitud para múltiples superficies 3D en un mismo gráfico"""
    surfaces: List[SurfaceData] = Field(..., description="Lista de datos para cada superficie")
    title: Optional[str] = Field("Múltiples Superficies 3D", description="Título del gráfico")
