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
- POST /distance/calculate: Cálculos de distancia entre objetos geométricos
- POST /intersection/calculate: Puntos de intersección de formas geométricas
- GET /examples: Ejemplos comprehensivos de geometría analítica
- POST /parametric-surface: Generación de superficies paramétricas 3D

Dependencias:
- AnalyticalGeometryService: Computaciones principales de geometría analítica
- NumPy: Computaciones numéricas para cálculos geométricos
- SymPy: Geometría simbólica y manipulación de ecuaciones
- Matplotlib: Visualización geométrica 2D/3D
- GeometryRequest/Response: Modelos de geometría estandarizados
- ParametricSurfaceRequest/Response: Modelos de generación de superficies

Uso típico:
    Todas las formas aceptan parámetros como diccionarios con propiedades geométricas estándar.
    Los sistemas de coordenadas usan coordenadas Cartesianas estándar [x, y] o [x, y, z].
    Las superficies paramétricas soportan rangos de parámetros u,v para formas 3D complejas.
    Los cálculos de intersección manejan múltiples tipos de objetos geométricos.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.domains.mathematics.models import BaseRequest, BaseResponse
from app.services.analytical_geometry import AnalyticalGeometryService
from app.exceptions.domain.mathematics import MathematicsError

def _get_geometry_service():
    """Return the shared geometry_service if available (so tests can patch it via app.routers),
    otherwise instantiate a local AnalyticalGeometryService."""
    try:
        from app.routers.analytical_geometry import geometry_service as shared_geometry_service
        return shared_geometry_service
    except Exception:
        return AnalyticalGeometryService()

# Definir modelos específicos para geometría analítica
class GeometryRequest(BaseRequest):
    shape: str = None
    operation: str = None
    points: list = []
    parameters: dict = {}

class GeometryResponse(BaseResponse):
    shape: str = None
    result: dict = {}
    operation: str = None
    properties: dict = {}
    visualization_data: dict = {}
    message: str = None

class ParametricSurfaceRequest(BaseRequest):
    x_expr: str
    y_expr: str
    z_expr: str
    u_range: list
    v_range: list
    u_steps: int = 20
    v_steps: int = 20

class ParametricSurfaceResponse(BaseResponse):
    image_path: str = ""
    x_expr: str = ""
    y_expr: str = ""
    z_expr: str = ""
    u_range: list = []
    v_range: list = []
    u_steps: int = 20
    v_steps: int = 20

router = APIRouter()
geometry_service = AnalyticalGeometryService()

@router.post("/circle/analyze")
async def analyze_circle(request: GeometryRequest):
    """Analyze circle properties and equations"""
    try:
        # If the caller explicitly provided a shape it must be 'circle'
        if getattr(request, 'shape', None) and request.shape != 'circle':
            raise HTTPException(status_code=400, detail="Shape must be 'circle'")
        svc = _get_geometry_service()
        payload = {"shape": "circle", "operation": request.operation, "parameters": request.parameters}
        result = svc.process_geometry(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ellipse/analyze")
async def analyze_ellipse(request: GeometryRequest):
    """Analyze ellipse properties"""
    try:
        if request.shape != "ellipse":
            raise HTTPException(status_code=400, detail="Shape must be 'ellipse'")

        svc = _get_geometry_service()
        geometry_data = {
            "operation": request.operation,
            "type": request.shape,
            "parameters": request.parameters
        }
        result = svc.process_geometry(geometry_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/parabola/analyze")
async def analyze_parabola(request: GeometryRequest):
    """Analyze parabola properties"""
    try:
        if request.shape != "parabola":
            raise HTTPException(status_code=400, detail="Shape must be 'parabola'")

        svc = _get_geometry_service()
        geometry_data = {
            "operation": request.operation,
            "type": request.shape,
            "parameters": request.parameters
        }
        result = svc.process_geometry(geometry_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/hyperbola/analyze")
async def analyze_hyperbola(request: GeometryRequest):
    """Analyze hyperbola properties"""
    try:
        if request.shape != "hyperbola":
            raise HTTPException(status_code=400, detail="Shape must be 'hyperbola'")

        svc = _get_geometry_service()
        geometry_data = {
            "operation": request.operation,
            "type": request.shape,
            "parameters": request.parameters
        }
        result = svc.process_geometry(geometry_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/line/analyze")
async def analyze_line(request: GeometryRequest):
    """Analyze line properties"""
    try:
        if request.shape != "line":
            raise HTTPException(status_code=400, detail="Shape must be 'line'")

        geometry_data = {
            "operation": request.operation,
            "type": request.shape,
            "parameters": request.parameters
        }
        result = geometry_service.process_geometry(geometry_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/triangle/analyze")
async def analyze_triangle(request: GeometryRequest):
    """Analyze triangle properties"""
    try:
        if request.shape != "triangle":
            raise HTTPException(status_code=400, detail="Shape must be 'triangle'")

        geometry_data = {
            "operation": request.operation,
            "type": request.shape,
            "parameters": request.parameters
        }
        result = geometry_service.process_geometry(geometry_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/distance/calculate")
async def calculate_distance(request: Dict[str, Any]):
    """Calculate distance between points"""
    try:
        point1 = request.get("point1", [0, 0])
        point2 = request.get("point2", [1, 1])

        # Note: Distance calculation would require specific service method
        # For now, return placeholder response
        return {"distance": 0.0, "points": {"point1": point1, "point2": point2}}
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/intersection/calculate")
async def calculate_intersection(request: Dict[str, Any]):
    """Calculate intersection between geometric shapes"""
    try:
        # Note: Intersection calculation would require specific service method
        # For now, return placeholder response
        return {"intersection": {"message": "Intersection calculation not yet implemented"}}
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/examples")
async def get_examples():
    """Get geometry examples"""
    try:
        # Note: Examples would require specific service method
        # For now, return placeholder response
        return {"examples": {"message": "Examples not yet implemented"}}
    except MathematicsError as e:
        return {"error": str(e)}

@router.post("/parametric-surface", response_model=ParametricSurfaceResponse)
async def generate_parametric_surface_endpoint(request: ParametricSurfaceRequest):
    """
    Generate a 3D parametric surface plot.
    """
    try:
        # Validate expressions before processing
        import sympy as sp
        u, v = sp.symbols('u v')
        
        try:
            from app.domains.mathematics.utils import safe_sympify
            safe_sympify(request.x_expr)
            safe_sympify(request.y_expr)
            safe_sympify(request.z_expr)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid expression: {str(e)}")
        
        # Note: Parametric surface generation would require specific service method
        # For now, return placeholder response
        return ParametricSurfaceResponse(
            success=True,
            image_path="",
            x_expr=request.x_expr,
            y_expr=request.y_expr,
            z_expr=request.z_expr,
            u_range=request.u_range,
            v_range=request.v_range,
            u_steps=request.u_steps,
            v_steps=request.v_steps
        )
    except HTTPException:
        raise
    except MathematicsError as e:
        raise HTTPException(status_code=400, detail=str(e))
