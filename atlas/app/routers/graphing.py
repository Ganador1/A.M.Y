"""
Router de Graficación Matemática - Visualización y Gráficos Científicos

Módulo FastAPI para graficación matemática integral y visualización de datos
en la plataforma de computación científica AXIOM. Proporciona endpoints REST API para
generar gráficos 2D/3D, plots paramétricos, coordenadas polares y visualizaciones
multi-superficie para funciones matemáticas y datos científicos.

Capacidades principales:
- Graficación 2D: plotting de funciones con rangos y resolución personalizables
- Graficación 3D: plotting de superficies para funciones de dos variables
- Curvas paramétricas: generación de curvas y superficies paramétricas en 2D y 3D
- Coordenadas polares: plotting para funciones angulares
- Múltiples funciones: plotting de múltiples funciones en figuras únicas
- Visualizaciones multi-superficie 3D: con controles interactivos
- Generación de imágenes: para integración web
- Biblioteca de ejemplos: plantillas para funciones matemáticas comunes

Catálogo de Endpoints:
- POST /generate: Generación de gráfico 2D desde expresión matemática
- POST /multiple: Creación de plots multi-función en figura única
- POST /3d: Generación de gráficos 3D de superficie interactivos
- POST /3d-surface: Creación de visualizaciones de superficie 3D
- POST /3d-parametric: Generación de plots paramétricos 3D
- POST /2d-parametric: Creación de plots de curvas paramétricas 2D
- POST /polar: Generación de plots en coordenadas polares
- POST /multi-surface-3d: Creación de visualizaciones multi-superficie 3D
- GET /image/{filename}: Servicio de imágenes de gráficos generados
- GET /examples: Ejemplos de graficación y plantillas

Dependencias:
- GraphingService: Motor central de plotting y visualización matemática
- Matplotlib: Biblioteca de plotting 2D/3D con salida de calidad publicación
- Plotly: Visualizaciones web interactivas y dashboards
- NumPy: Computaciones numéricas para evaluación de funciones
- SymPy: Matemáticas simbólicas para parsing y manipulación de expresiones
- ImageStorage: Almacenamiento y servicio de imágenes de gráficos
- TemplateLibrary: Biblioteca de plantillas y ejemplos predefinidos

Uso del Servicio:
    Las expresiones matemáticas soportan sintaxis estándar Python/NumPy.
    Los plots paramétricos usan t como variable parámetro, los 3D usan variables x,y.
    Las imágenes se almacenan en directorio static/graphs/ para servicio web.
    Los plots 3D interactivos soportan zoom, rotación e inspección de datos.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from app.models import GraphingRequest, GraphResponse
from app.models.graphing_models import Graph3DRequest, PolarGraphRequest, MultipleGraphRequest, ParametricGraphRequest, MultiSurface3DRequest
from app.domains.mathematics.services.graphing_service import GraphingService
from app.exceptions.domain.biology import BiologyError

router = APIRouter()

@router.post("/generate", response_model=GraphResponse)
async def generate_graph(request: GraphingRequest):
    """
    Genera un gráfico de una función matemática
    
    Args:
        request: Solicitud con parámetros del gráfico
        
    Returns:
        Información del gráfico generado
    """
    try:
        result = GraphingService.generate_graph(request)
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/multiple")
async def generate_multiple_graphs(request: MultipleGraphRequest):
    """
    Genera múltiples gráficos en una misma figura
    
    Args:
        request: Solicitud con parámetros de múltiples gráficos
        
    Returns:
        Información del gráfico múltiple
    """
    try:
        result = GraphingService.generate_multiple_graphs(
            request.expressions, request.x_min, request.x_max, request.points, request.variable
        )
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/3d")
async def generate_3d_graph(request: Graph3DRequest):
    """
    Genera un gráfico 3D interactivo de una función de dos variables
    
    Args:
        request: Solicitud con parámetros del gráfico 3D
        
    Returns:
        Información del gráfico 3D interactivo
    """
    try:
        result = GraphingService.generate_3d_graph(
            request.expression, request.x_min, request.x_max, 
            request.y_min, request.y_max, request.points
        )
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/3d-surface")
async def generate_3d_surface(request: Graph3DRequest):
    """
    Genera un gráfico 3D de superficie interactivo
    
    Args:
        request: Solicitud con parámetros del gráfico 3D
        
    Returns:
        Información del gráfico 3D de superficie interactivo
    """
    try:
        result = GraphingService.generate_3d_surface(
            request.expression, request.x_min, request.x_max, 
            request.y_min, request.y_max, request.points
        )
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/3d-parametric")
async def generate_3d_parametric(request: ParametricGraphRequest):
    """
    Genera un gráfico 3D paramétrico
    
    Args:
        request: Solicitud con parámetros del gráfico paramétrico
        
    Returns:
        Información del gráfico 3D paramétrico
    """
    try:
        if not request.z_expr:
            raise HTTPException(status_code=400, detail="z_expr es requerido para gráficos 3D paramétricos")
        
        result = GraphingService.generate_3d_parametric(
            request.x_expr, request.y_expr, request.z_expr,
            request.t_min, request.t_max, request.points
        )
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/2d-parametric")
async def generate_2d_parametric(request: ParametricGraphRequest):
    """
    Genera un gráfico 2D paramétrico
    
    Args:
        request: Solicitud con parámetros del gráfico paramétrico 2D
        
    Returns:
        Información del gráfico 2D paramétrico
    """
    try:
        result = GraphingService.generate_2d_parametric(
            request.x_expr, request.y_expr,
            request.t_min, request.t_max, request.points
        )
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/polar")
async def generate_polar_graph(request: PolarGraphRequest):
    """
    Genera un gráfico polar
    
    Args:
        request: Solicitud con parámetros del gráfico polar
        
    Returns:
        Información del gráfico polar
    """
    try:
        result = GraphingService.generate_polar_graph(
            request.expression, request.theta_min, request.theta_max, request.points
        )
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/multi-surface-3d")
async def generate_multi_surface_3d(request: MultiSurface3DRequest):
    """
    Genera un gráfico 3D interactivo con múltiples superficies
    
    Args:
        request: Solicitud con datos para múltiples superficies
        
    Returns:
        Información del gráfico 3D interactivo
    """
    try:
        result = GraphingService.generate_multi_surface_3d(
            [surface.dict() for surface in request.surfaces], request.title
        )
        return result
    except BiologyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/image/{filename}")
async def get_graph_image(filename: str):
    """
    Obtiene una imagen de gráfico generada
    
    Args:
        filename: Nombre del archivo de imagen
        
    Returns:
        Archivo de imagen
    """
    try:
        file_path = f"static/graphs/{filename}"
        return FileResponse(file_path, media_type="image/png")
    except BiologyError:
        raise HTTPException(status_code=404, detail="Imagen no encontrada")

@router.get("/examples")
async def get_examples():
    """
    Obtiene ejemplos de gráficos
    
    Returns:
        Lista de ejemplos
    """
    return GraphingService.get_graph_examples()
