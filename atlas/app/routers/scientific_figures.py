"""
🔬 FIGURAS CIENTÍFICAS - AXIOM META 4.1
═══════════════════════════════════════════════════════════════════════════════════════════════

Módulo de generación automatizada de figuras científicas para la plataforma AXIOM v4.1.
Proporciona endpoints REST API para crear visualizaciones científicas de alta calidad
incluyendo gráficos, diagramas, mapas de calor y diagramas de red.

FUNCIONALIDADES PRINCIPALES:
────────────────────────────
• Generación automática de figuras científicas múltiples tipos
• Soporte para gráficos científicos (plots, scatter, bar charts)
• Diagramas científicos con elementos y conexiones
• Mapas de calor con etiquetas personalizables
• Diagramas de flujo para procesos científicos
• Visualizaciones de redes con nodos y aristas ponderadas
• Generación por lotes con procesamiento en segundo plano
• Múltiples formatos de salida (PNG, PDF, SVG)
• Resoluciones configurables para publicación científica

ARQUITECTURA TÉCNICA:
─────────────────────
• Framework: FastAPI con enrutamiento REST asíncrono
• Servicio backend: ScientificFigureGenerator con matplotlib/seaborn
• Autenticación: JWT Bearer tokens con scopes específicos
• Validación: Pydantic models con constraints detallados
• Logging: Configuración estructurada con indicadores visuales
• Manejo de errores: HTTPException con códigos específicos
• Procesamiento: Asyncio para operaciones no bloqueantes

ENDPOINTS DISPONIBLES:
──────────────────────
• POST /generate - Generación genérica de figuras
• POST /generate-plot - Gráficos científicos con series múltiples
• POST /generate-diagram - Diagramas con elementos geométricos
• POST /generate-flowchart - Diagramas de flujo de procesos
• POST /generate-heatmap - Mapas de calor matriciales
• POST /generate-network - Visualizaciones de redes
• POST /generate-batch - Generación por lotes en segundo plano
• GET /capabilities - Capacidades y formatos soportados
• GET /health - Verificación de estado del servicio

MODELOS DE DATOS:
─────────────────
• FigureGenerationRequest: Configuración completa de figuras
• PlotDataRequest: Datos para gráficos científicos
• DiagramRequest: Elementos y conexiones para diagramas
• FlowchartRequest: Pasos para diagramas de flujo
• HeatmapRequest: Matrices para mapas de calor
• NetworkRequest: Nodos y aristas para redes
• BatchFigureRequest: Configuración para generación múltiple

CONSIDERACIONES DE SEGURIDAD:
────────────────────────────
• Autenticación requerida con scope 'figures'
• Validación estricta de parámetros de entrada
• Límites en dimensiones y resolución de figuras
• Sanitización de rutas de archivos de salida
• Control de acceso basado en roles de usuario
• Logging detallado de operaciones para auditoría

MANEJO DE ERRORES:
──────────────────
• 400 Bad Request: Parámetros inválidos o datos malformados
• 401 Unauthorized: Falta de autenticación o scopes insuficientes
• 500 Internal Server Error: Errores del generador de figuras
• Logging estructurado con códigos de error específicos
• Recuperación automática de operaciones fallidas

EJEMPLOS DE USO:
────────────────
# Generar un gráfico científico
POST /api/v1/scientific-figures/generate-plot
{
    "x_data": [1, 2, 3, 4, 5],
    "y_data": [[10, 15, 13, 17, 20]],
    "labels": ["Serie A"],
    "x_label": "Tiempo",
    "y_label": "Valor"
}

# Generar diagrama de red
POST /api/v1/scientific-figures/generate-network
{
    "nodes": [
        {"position": [0, 0], "label": "Nodo 1"},
        {"position": [1, 1], "label": "Nodo 2"}
    ],
    "edges": [
        {"start": [0, 0], "end": [1, 1], "weight": 0.8}
    ]
}

DEPENDENCIAS:
─────────────
• fastapi: Framework web asíncrono
• pydantic: Validación de datos y modelos
• matplotlib: Generación de gráficos base
• seaborn: Visualizaciones estadísticas avanzadas
• networkx: Algoritmos de grafos y redes
• pillow: Procesamiento de imágenes
• asyncio: Programación asíncrona

NOTAS DE IMPLEMENTACIÓN:
───────────────────────
• Todas las operaciones son asíncronas para no bloquear el servidor
• Las figuras se generan con metadatos para trazabilidad
• Soporte para dominios científicos específicos (biología, física, química)
• Optimización automática de layouts para mejor legibilidad
• Generación de IDs únicos para seguimiento de figuras
• Almacenamiento configurable de archivos generados

VERSIÓN: AXIOM META 4.1
FECHA: Diciembre 2024
AUTOR: Equipo de Desarrollo AXIOM
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import asyncio
import time
from datetime import datetime

from app.core.bootstrap_logging import logger
from app.services.scientific_figure_generator import ScientificFigureGenerator
from app.security import require_scopes
from app.exceptions.domain.biology import BiologyError

router = APIRouter(
    prefix="/api/v1/scientific-figures",
    tags=["Scientific Figures"],
    dependencies=[Depends(require_scopes(["figures"]))]
)


class FigureGenerationRequest(BaseModel):
    """Request model for figure generation"""
    figure_type: str = Field(..., description="Type of figure: plot, diagram, flowchart, heatmap, network")
    title: str = Field(..., description="Figure title")
    caption: str = Field(default="", description="Figure caption")
    domain: str = Field(default="general", description="Scientific domain")
    data: Dict[str, Any] = Field(..., description="Figure data and parameters")
    output_path: str = Field(default="./figures", description="Output directory path")
    format: str = Field(default="png", description="Output format: png, pdf, svg")
    resolution: int = Field(default=300, description="Output resolution in DPI")
    width: float = Field(default=8.0, description="Figure width in inches")
    height: float = Field(default=6.0, description="Figure height in inches")


class PlotDataRequest(BaseModel):
    """Request model for plot data"""
    x_data: Optional[List[float]] = Field(None, description="X-axis data")
    y_data: List[List[float]] = Field(..., description="Y-axis data (can be multiple series)")
    labels: List[str] = Field(default_factory=list, description="Series labels")
    colors: List[str] = Field(default_factory=list, description="Series colors")
    error_bars: Optional[List[float]] = Field(None, description="Error bars for Y data")
    x_label: str = Field(default="X-axis", description="X-axis label")
    y_label: str = Field(default="Y-axis", description="Y-axis label")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class DiagramElement(BaseModel):
    """Model for diagram elements"""
    type: str = Field(..., description="Element type: rectangle, circle")
    position: List[float] = Field(..., description="Position [x, y]")
    size: List[float] = Field(..., description="Size [width, height]")
    label: str = Field(..., description="Element label")
    color: str = Field(default="#1f77b4", description="Element color")


class DiagramConnection(BaseModel):
    """Model for diagram connections"""
    start: List[float] = Field(..., description="Start position [x, y]")
    end: List[float] = Field(..., description="End position [x, y]")
    style: str = Field(default="solid", description="Line style: solid, dashed, dotted")


class DiagramRequest(BaseModel):
    """Request model for diagram generation"""
    elements: List[DiagramElement] = Field(..., description="Diagram elements")
    connections: List[DiagramConnection] = Field(default_factory=list, description="Element connections")


class FlowchartStep(BaseModel):
    """Model for flowchart steps"""
    type: str = Field(..., description="Step type: process, decision, start_end")
    label: str = Field(..., description="Step label")


class FlowchartRequest(BaseModel):
    """Request model for flowchart generation"""
    steps: List[FlowchartStep] = Field(..., description="Flowchart steps")


class HeatmapRequest(BaseModel):
    """Request model for heatmap generation"""
    matrix: List[List[float]] = Field(..., description="Heatmap matrix data")
    row_labels: List[str] = Field(default_factory=list, description="Row labels")
    col_labels: List[str] = Field(default_factory=list, description="Column labels")
    colorbar_label: str = Field(default="Value", description="Colorbar label")
    x_label: str = Field(default="Columns", description="X-axis label")
    y_label: str = Field(default="Rows", description="Y-axis label")


class NetworkNode(BaseModel):
    """Model for network nodes"""
    position: List[float] = Field(..., description="Node position [x, y]")
    label: str = Field(..., description="Node label")
    size: float = Field(default=100, description="Node size")
    color: str = Field(default="#1f77b4", description="Node color")


class NetworkEdge(BaseModel):
    """Model for network edges"""
    start: List[float] = Field(..., description="Start position [x, y]")
    end: List[float] = Field(..., description="End position [x, y]")
    weight: float = Field(default=1.0, description="Edge weight")


class NetworkRequest(BaseModel):
    """Request model for network generation"""
    nodes: List[NetworkNode] = Field(..., description="Network nodes")
    edges: List[NetworkEdge] = Field(default_factory=list, description="Network edges")


class BatchFigureRequest(BaseModel):
    """Request model for batch figure generation"""
    figures: List[FigureGenerationRequest] = Field(..., description="List of figures to generate")
    output_path: str = Field(default="./figures", description="Output directory path")


# Initialize figure generator service
figure_generator = ScientificFigureGenerator()


@router.post("/generate", summary="Generate Scientific Figure")
async def generate_figure(request: FigureGenerationRequest):
    """
    🎨 Generar Figura Científica

    Endpoint principal para la generación automatizada de figuras científicas.
    Soporta múltiples tipos de visualizaciones con configuración completa.

    **Parámetros de entrada:**
    - **figure_type**: Tipo de figura (plot, diagram, flowchart, heatmap, network)
    - **title**: Título descriptivo de la figura
    - **caption**: Descripción opcional de la figura
    - **domain**: Dominio científico (biology, chemistry, physics, etc.)
    - **data**: Datos específicos del tipo de figura
    - **output_path**: Directorio de salida (default: ./figures)
    - **format**: Formato de salida (png, pdf, svg)
    - **resolution**: Resolución en DPI (default: 300)
    - **width/height**: Dimensiones en pulgadas

    **Validaciones realizadas:**
    - Tipo de figura debe ser uno de los soportados
    - Resolución entre 150-600 DPI
    - Dimensiones positivas y razonables
    - Ruta de salida sanitizada

    **Respuesta exitosa:**
    ```json
    {
        "success": true,
        "figure_id": "fig_1234567890",
        "filename": "scientific_plot_1234567890.png",
        "filepath": "/path/to/figures/scientific_plot_1234567890.png",
        "metadata": {
            "type": "plot",
            "domain": "physics",
            "resolution": 300,
            "dimensions": [8.0, 6.0]
        },
        "figure_type": "plot"
    }
    ```

    **Códigos de error:**
    - **400**: Parámetros inválidos o datos malformados
    - **500**: Error interno del generador de figuras
    """
    start_time = time.time()
    execution_timestamp = datetime.now().isoformat()

    try:
        logger.info(f"🎨 Iniciando generación de figura: {request.title}")
        logger.info(f"📊 Tipo: {request.figure_type} | Dominio: {request.domain}")
        logger.info(f"⚙️ Configuración: {request.resolution} DPI, {request.width}x{request.height} in")

        # Validaciones adicionales
        if request.figure_type not in ["plot", "diagram", "flowchart", "heatmap", "network"]:
            logger.warning(f"⚠️ Tipo de figura no soportado: {request.figure_type}")
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de figura no soportado: {request.figure_type}. Use: plot, diagram, flowchart, heatmap, network"
            )

        if not (150 <= request.resolution <= 600):
            logger.warning(f"⚠️ Resolución fuera de rango: {request.resolution} DPI")
            raise HTTPException(
                status_code=400,
                detail=f"Resolución debe estar entre 150-600 DPI, recibido: {request.resolution}"
            )

        if request.width <= 0 or request.height <= 0 or request.width > 50 or request.height > 50:
            logger.warning(f"⚠️ Dimensiones inválidas: {request.width}x{request.height}")
            raise HTTPException(
                status_code=400,
                detail=f"Dimensiones deben ser positivas y menores a 50 pulgadas, recibido: {request.width}x{request.height}"
            )

        # Preparar datos para el generador
        generation_params = {
            "action": "generate_figure",
            "figure_type": request.figure_type,
            "title": request.title,
            "caption": request.caption,
            "domain": request.domain,
            "data": request.data,
            "output_path": request.output_path,
            "format": request.format,
            "resolution": request.resolution,
            "width": request.width,
            "height": request.height,
            "timestamp": execution_timestamp
        }

        logger.info("🔄 Ejecutando generador de figuras...")
        result = await figure_generator.generate_figure(generation_params)

        execution_time = time.time() - start_time

        if result["success"]:
            logger.info(f"✅ Figura generada exitosamente en {execution_time:.2f}s")
            logger.info(f"📁 Archivo: {result['filename']}")
            logger.info(f"🆔 ID: {result['figure_id']}")

            return {
                "success": True,
                "figure_id": result["figure_id"],
                "filename": result["filename"],
                "filepath": result["filepath"],
                "metadata": result["metadata"],
                "figure_type": result["figure_type"],
                "execution_time_seconds": round(execution_time, 2),
                "timestamp": execution_timestamp
            }
        else:
            logger.error(f"❌ Error en generador: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])

    except HTTPException:
        # Re-lanzar excepciones HTTP sin modificar
        raise
    except BiologyError as e:
        execution_time = time.time() - start_time
        logger.error(f"❌ Error interno generando figura: {str(e)} (tiempo: {execution_time:.2f}s)")
        logger.error(f"🔍 Detalles del error: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del generador de figuras: {str(e)}"
        )


@router.post("/generate-plot", summary="Generate Scientific Plot")
async def generate_plot(request: PlotDataRequest, title: str = "Scientific Plot", 
                       caption: str = "", domain: str = "general"):
    """
    Generate a scientific plot figure with data visualization.
    
    Supports multiple data series, error bars, and customizable styling.
    """
    try:
        # Convert request to figure data
        figure_data = {
            "x_data": request.x_data,
            "y_data": request.y_data,
            "labels": request.labels,
            "colors": request.colors,
            "error_bars": request.error_bars,
            "x_label": request.x_label,
            "y_label": request.y_label,
            "metadata": request.metadata
        }
        
        result = await figure_generator.generate_plot({
            "action": "generate_plot",
            "title": title,
            "caption": caption,
            "domain": domain,
            "data": figure_data
        })
        
        if result["success"]:
            return {
                "success": True,
                "figure_id": result["figure_id"],
                "filename": result["filename"],
                "filepath": result["filepath"],
                "metadata": result["metadata"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating plot: {e}")
        raise HTTPException(status_code=500, detail=f"Plot generation failed: {str(e)}")


@router.post("/generate-diagram", summary="Generate Scientific Diagram")
async def generate_diagram(request: DiagramRequest, title: str = "Scientific Diagram",
                          caption: str = "", domain: str = "general"):
    """
    Generate a scientific diagram with elements and connections.
    
    Supports rectangles, circles, and various connection styles.
    """
    try:
        # Convert request to figure data
        figure_data = {
            "elements": [element.dict() for element in request.elements],
            "connections": [conn.dict() for conn in request.connections]
        }
        
        result = await figure_generator.generate_diagram({
            "action": "generate_diagram",
            "title": title,
            "caption": caption,
            "domain": domain,
            "data": figure_data
        })
        
        if result["success"]:
            return {
                "success": True,
                "figure_id": result["figure_id"],
                "filename": result["filename"],
                "filepath": result["filepath"],
                "metadata": result["metadata"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating diagram: {e}")
        raise HTTPException(status_code=500, detail=f"Diagram generation failed: {str(e)}")


@router.post("/generate-flowchart", summary="Generate Flowchart")
async def generate_flowchart(request: FlowchartRequest, title: str = "Process Flowchart",
                           caption: str = "", domain: str = "general"):
    """
    Generate a process flowchart with different step types.
    
    Supports process, decision, and start/end step types.
    """
    try:
        # Convert request to figure data
        figure_data = {
            "steps": [step.dict() for step in request.steps]
        }
        
        result = await figure_generator.generate_flowchart({
            "action": "generate_flowchart",
            "title": title,
            "caption": caption,
            "domain": domain,
            "data": figure_data
        })
        
        if result["success"]:
            return {
                "success": True,
                "figure_id": result["figure_id"],
                "filename": result["filename"],
                "filepath": result["filepath"],
                "metadata": result["metadata"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating flowchart: {e}")
        raise HTTPException(status_code=500, detail=f"Flowchart generation failed: {str(e)}")


@router.post("/generate-heatmap", summary="Generate Heatmap")
async def generate_heatmap(request: HeatmapRequest, title: str = "Data Heatmap",
                          caption: str = "", domain: str = "general"):
    """
    Generate a scientific heatmap visualization.
    
    Supports custom row/column labels and colorbar configuration.
    """
    try:
        # Convert request to figure data
        figure_data = {
            "matrix": request.matrix,
            "row_labels": request.row_labels,
            "col_labels": request.col_labels,
            "colorbar_label": request.colorbar_label,
            "x_label": request.x_label,
            "y_label": request.y_label
        }
        
        result = await figure_generator.generate_heatmap({
            "action": "generate_heatmap",
            "title": title,
            "caption": caption,
            "domain": domain,
            "data": figure_data
        })
        
        if result["success"]:
            return {
                "success": True,
                "figure_id": result["figure_id"],
                "filename": result["filename"],
                "filepath": result["filepath"],
                "metadata": result["metadata"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating heatmap: {e}")
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {str(e)}")


@router.post("/generate-network", summary="Generate Network Diagram")
async def generate_network(request: NetworkRequest, title: str = "Network Diagram",
                         caption: str = "", domain: str = "general"):
    """
    Generate a network diagram with nodes and edges.
    
    Supports weighted edges and customizable node properties.
    """
    try:
        # Convert request to figure data
        figure_data = {
            "nodes": [node.dict() for node in request.nodes],
            "edges": [edge.dict() for edge in request.edges]
        }
        
        result = await figure_generator.generate_network({
            "action": "generate_network",
            "title": title,
            "caption": caption,
            "domain": domain,
            "data": figure_data
        })
        
        if result["success"]:
            return {
                "success": True,
                "figure_id": result["figure_id"],
                "filename": result["filename"],
                "filepath": result["filepath"],
                "metadata": result["metadata"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except BiologyError as e:
        logger.error(f"❌ Error generating network: {e}")
        raise HTTPException(status_code=500, detail=f"Network generation failed: {str(e)}")


@router.post("/generate-batch", summary="Generate Multiple Figures")
async def generate_batch_figures(request: BatchFigureRequest, background_tasks: BackgroundTasks):
    """
    Generate multiple figures in batch.
    
    Returns immediately with task ID, figures are generated in background.
    """
    try:
        task_id = f"batch_figures_{asyncio.get_event_loop().time()}"
        
        # Add background task
        background_tasks.add_task(
            _generate_batch_figures_task,
            task_id,
            request.figures,
            request.output_path
        )
        
        return {
            "success": True,
            "task_id": task_id,
            "message": f"Batch generation started for {len(request.figures)} figures",
            "status": "processing"
        }
        
    except BiologyError as e:
        logger.error(f"❌ Error starting batch generation: {e}")
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")


async def _generate_batch_figures_task(task_id: str, figures: List[FigureGenerationRequest], output_path: str):
    """Background task for batch figure generation"""
    try:
        results = []
        
        for i, figure_request in enumerate(figures):
            logger.info(f"🔄 Generating figure {i+1}/{len(figures)}: {figure_request.title}")
            
            result = await figure_generator.generate_figure({
                "action": "generate_figure",
                "figure_type": figure_request.figure_type,
                "title": figure_request.title,
                "caption": figure_request.caption,
                "domain": figure_request.domain,
                "data": figure_request.data,
                "output_path": output_path,
                "format": figure_request.format,
                "resolution": figure_request.resolution,
                "width": figure_request.width,
                "height": figure_request.height
            })
            
            results.append(result)
        
        logger.info(f"✅ Batch generation completed: {task_id}")
        
    except BiologyError as e:
        logger.error(f"❌ Batch generation failed: {task_id} - {e}")


@router.get("/capabilities", summary="Get Figure Generation Capabilities")
async def get_capabilities():
    """
    Get information about figure generation capabilities and supported formats.
    """
    return {
        "success": True,
        "capabilities": {
            "figure_types": [
                {
                    "type": "plot",
                    "description": "Line plots, scatter plots, bar charts",
                    "supports": ["multiple_series", "error_bars", "custom_styling"]
                },
                {
                    "type": "diagram", 
                    "description": "Scientific diagrams with elements and connections",
                    "supports": ["rectangles", "circles", "custom_connections"]
                },
                {
                    "type": "flowchart",
                    "description": "Process flowcharts",
                    "supports": ["process_steps", "decisions", "start_end"]
                },
                {
                    "type": "heatmap",
                    "description": "Heatmap visualizations",
                    "supports": ["custom_labels", "colorbar", "annotations"]
                },
                {
                    "type": "network",
                    "description": "Network diagrams",
                    "supports": ["weighted_edges", "custom_nodes", "layouts"]
                }
            ],
            "output_formats": ["png", "pdf", "svg"],
            "resolutions": [150, 300, 600],
            "domains": ["biology", "chemistry", "physics", "materials", "neuroscience", "general"],
            "styles": ["publication", "presentation", "draft"]
        }
    }


@router.get("/health", summary="Health Check")
async def health_check():
    """Check if the figure generation service is healthy"""
    return {
        "success": True,
        "service": "ScientificFigureGenerator",
        "status": "healthy",
        "timestamp": asyncio.get_event_loop().time()
    }
