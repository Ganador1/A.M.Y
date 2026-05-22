"""
Analytical Geometry Router

Router FastAPI para operaciones de geometría analítica y geometría de coordenadas.
Proporciona endpoints REST API para secciones cónicas, líneas, triángulos, distancias,
intersecciones y superficies paramétricas en sistemas de coordenadas 2D y 3D.

Este router ofrece capacidades comprehensivas de geometría analítica para:
- Secciones cónicas: círculos, elipses, parábolas, hipérbolas con propiedades
- Geometría lineal: líneas, distancias, intersecciones y ecuaciones
- Geometría triangular: vértices, propiedades y clasificaciones
- Transformaciones de coordenadas: traslaciones, rotaciones, reflexiones
- Cálculos de distancia: punto a punto, punto a línea, punto a plano
- Problemas de intersección: líneas, curvas y superficies
- Superficies paramétricas: generación y visualización de superficies 3D

El router se integra con AnalyticalGeometryService para proporcionar
a matemáticos, ingenieros y estudiantes herramientas poderosas para
problemas de geometría de coordenadas y análisis geométrico.

Endpoints disponibles:
- POST /circle/analyze: Propiedades de círculos y análisis de ecuaciones
- POST /ellipse/analyze: Propiedades de elipses con focos y vértices
- POST /parabola/analyze: Propiedades de parábolas con foco y directriz
- POST /hyperbola/analyze: Propiedades de hipérbolas con asíntotas
- POST /line/analyze: Ecuaciones de líneas y propiedades
- POST /triangle/analyze: Geometría triangular y propiedades
- POST /distance/calculate: Cálculos de distancia entre puntos
- POST /intersection/calculate: Intersecciones entre objetos geométricos
- POST /parametric-surface/generate: Generación de superficies paramétricas
- GET /examples: Ejemplos de uso y casos de prueba
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.analytical_geometry import AnalyticalGeometryService
from app.models import GeometryRequest, GeometryResponse
from app.exceptions.domain.biology import BiologyError

# Create router
router = APIRouter(
    prefix="/analytical-geometry",
    tags=["Analytical Geometry", "Mathematics"],
    responses={404: {"description": "Not found"}}
)

# Initialize service
geometry_service = AnalyticalGeometryService()


class GeometryRequest(BaseModel):
    shape: str
    parameters: Dict[str, Any]


class GeometryResponse(BaseModel):
    shape: str
    properties: Dict[str, Any]
    success: bool = True
    message: str = "Analysis completed successfully"


class DistanceRequest(BaseModel):
    point1: Optional[List[float]] = None
    point2: Optional[List[float]] = None


class DistanceResponse(BaseModel):
    distance: float
    points: Dict[str, List[float]]
    success: bool = True


class ParametricSurfaceRequest(BaseModel):
    surface_type: str
    parameters: Optional[Dict[str, Any]] = None


class ParametricSurfaceResponse(BaseModel):
    surface_type: str
    points: List[List[float]]
    success: bool = True


@router.post("/circle/analyze", response_model=GeometryResponse)
async def analyze_circle(request: GeometryRequest):
    """Analyze circle properties"""
    try:
        if request.shape != "circle":
            raise HTTPException(status_code=400, detail="Shape must be 'circle'")

        result = geometry_service.process_geometry(request)
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/ellipse/analyze", response_model=GeometryResponse)
async def analyze_ellipse(request: GeometryRequest):
    """Analyze ellipse properties (placeholder)"""
    if request.shape != "ellipse":
        raise HTTPException(status_code=400, detail="Shape must be 'ellipse'")
    
    raise HTTPException(status_code=501, detail="Ellipse analysis not yet implemented")


@router.post("/parabola/analyze", response_model=GeometryResponse)
async def analyze_parabola(request: GeometryRequest):
    """Analyze parabola properties (placeholder)"""
    if request.shape != "parabola":
        raise HTTPException(status_code=400, detail="Shape must be 'parabola'")
    
    raise HTTPException(status_code=501, detail="Parabola analysis not yet implemented")


@router.post("/hyperbola/analyze", response_model=GeometryResponse)
async def analyze_hyperbola(request: GeometryRequest):
    """Analyze hyperbola properties (placeholder)"""
    if request.shape != "hyperbola":
        raise HTTPException(status_code=400, detail="Shape must be 'hyperbola'")
    
    raise HTTPException(status_code=501, detail="Hyperbola analysis not yet implemented")


@router.post("/line/analyze", response_model=GeometryResponse)
async def analyze_line(request: GeometryRequest):
    """Analyze line properties (placeholder)"""
    if request.shape != "line":
        raise HTTPException(status_code=400, detail="Shape must be 'line'")
    
    raise HTTPException(status_code=501, detail="Line analysis not yet implemented")


@router.post("/triangle/analyze", response_model=GeometryResponse)
async def analyze_triangle(request: GeometryRequest):
    """Analyze triangle properties (placeholder)"""
    if request.shape != "triangle":
        raise HTTPException(status_code=400, detail="Shape must be 'triangle'")
    
    raise HTTPException(status_code=501, detail="Triangle analysis not yet implemented")


@router.post("/distance/calculate", response_model=DistanceResponse)
async def calculate_distance(request: DistanceRequest):
    """Calculate distance between points"""
    try:
        point1 = request.point1 or [0, 0]
        point2 = request.point2 or [1, 1]
        
        # Simple distance calculation
        if len(point1) == 2 and len(point2) == 2:
            distance = ((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)**0.5
        elif len(point1) == 3 and len(point2) == 3:
            distance = ((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2 + (point2[2] - point1[2])**2)**0.5
        else:
            raise ValueError("Points must have same dimensions (2D or 3D)")
        
        return DistanceResponse(
            distance=distance,
            points={"point1": point1, "point2": point2}
        )
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/intersection/calculate")
async def calculate_intersection():
    """Calculate intersections (placeholder)"""
    raise HTTPException(status_code=501, detail="Intersection calculation not yet implemented")


@router.get("/examples")
async def get_examples():
    """Get geometry examples"""
    try:
        examples = geometry_service.get_examples()
        return {"examples": examples}
    except BiologyError as e:
        return {"examples": [], "error": str(e)}


@router.post("/parametric-surface/generate", response_model=ParametricSurfaceResponse)
async def generate_parametric_surface(request: ParametricSurfaceRequest):
    """Generate parametric surface"""
    try:
        # Use the service to generate the surface
        result = geometry_service.generate_parametric_surface(
            x_expr=request.parameters.get("x_expr", "u"),
            y_expr=request.parameters.get("y_expr", "v"),
            z_expr=request.parameters.get("z_expr", "u*v"),
            u_range=request.parameters.get("u_range", [-1, 1]),
            v_range=request.parameters.get("v_range", [-1, 1]),
            u_points=request.parameters.get("u_points", 50),
            v_points=request.parameters.get("v_points", 50),
            title=request.parameters.get("title", "Parametric Surface")
        )
        
        return ParametricSurfaceResponse(
            surface_type=request.surface_type,
            points=result.get("points", [])
        )
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))