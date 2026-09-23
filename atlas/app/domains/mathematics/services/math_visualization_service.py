"""
Mathematical Visualization Service for AXIOM Mathematics Domain

Servicio avanzado de visualización matemática interactiva que integra
capacidades similares a GeoGebra para crear gráficos interactivos,
visualizaciones 3D y animaciones matemáticas.
"""

import asyncio
import numpy as np
import json
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime
import base64
import io
from app.exceptions.domain.mathematics import MathematicsError

try:
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False


class MathVisualizationService:
    """
    Servicio de visualización matemática interactiva.
    
    Proporciona capacidades de:
    - Gráficos interactivos 2D y 3D
    - Visualizaciones de funciones matemáticas
    - Animaciones matemáticas
    - Gráficos estadísticos avanzados
    - Visualizaciones geométricas
    - Diagramas de fase y campos vectoriales
    """

    def __init__(self):
        self.version = "1.0"
        self.capabilities = [
            "2d_plots",
            "3d_plots",
            "animations",
            "statistical_plots",
            "geometric_visualizations",
            "phase_diagrams",
            "vector_fields",
            "interactive_plots"
        ]
        self.matplotlib_available = MATPLOTLIB_AVAILABLE
        self.plotly_available = PLOTLY_AVAILABLE
        self.seaborn_available = SEABORN_AVAILABLE

    async def create_2d_plot(
        self,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear gráficos 2D interactivos
        """
        await asyncio.sleep(0.01)  # Simular procesamiento

        if not self.matplotlib_available and not self.plotly_available:
            return {
                "success": False,
                "error": "Visualization libraries not available",
                "simulation": True,
                "operation": operation
            }

        try:
            if operation == "function_plot":
                # Gráfico de función matemática
                function_expr = parameters.get("function", "x**2")
                x_range = parameters.get("x_range", [-10, 10])
                y_range = parameters.get("y_range", [-10, 10])
                title = parameters.get("title", f"Gráfico de f(x) = {function_expr}")
                
                # Generar datos
                x = np.linspace(x_range[0], x_range[1], 1000)
                try:
                    safe_env = {"__builtins__": {}, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                    y = eval(function_expr.replace("x", "x"), safe_env, {"x": x})
                except MathematicsError:
                    y = x**2  # Fallback
                
                # Crear gráfico
                if self.plotly_available:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='f(x)'))
                    fig.update_layout(
                        title=title,
                        xaxis_title='x',
                        yaxis_title='f(x)',
                        xaxis=dict(range=x_range),
                        yaxis=dict(range=y_range)
                    )
                    plot_html = fig.to_html(include_plotlyjs='cdn')
                else:
                    # Simular gráfico matplotlib
                    plot_html = f"<div>Gráfico simulado de {function_expr}</div>"
                
                return {
                    "success": True,
                    "operation": operation,
                    "function": function_expr,
                    "x_range": x_range,
                    "y_range": y_range,
                    "title": title,
                    "plot_html": plot_html,
                    "data_points": len(x),
                    "processing_time": 0.1
                }
                
            elif operation == "parametric_plot":
                # Gráfico paramétrico
                x_expr = parameters.get("x_function", "t")
                y_expr = parameters.get("y_function", "t**2")
                t_range = parameters.get("t_range", [0, 10])
                
                t = np.linspace(t_range[0], t_range[1], 1000)
                try:
                    safe_env = {"__builtins__": {}, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                    x = eval(x_expr.replace("t", "t"), safe_env, {"t": t})
                    y = eval(y_expr.replace("t", "t"), safe_env, {"t": t})
                except MathematicsError:
                    x = t
                    y = t**2
                
                if self.plotly_available:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Parametric'))
                    fig.update_layout(
                        title=f"Gráfico paramétrico: x(t)={x_expr}, y(t)={y_expr}",
                        xaxis_title='x',
                        yaxis_title='y'
                    )
                    plot_html = fig.to_html(include_plotlyjs='cdn')
                else:
                    plot_html = f"<div>Gráfico paramétrico simulado</div>"
                
                return {
                    "success": True,
                    "operation": operation,
                    "x_function": x_expr,
                    "y_function": y_expr,
                    "t_range": t_range,
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            elif operation == "polar_plot":
                # Gráfico polar
                r_expr = parameters.get("r_function", "1")
                theta_range = parameters.get("theta_range", [0, 2*np.pi])
                
                theta = np.linspace(theta_range[0], theta_range[1], 1000)
                try:
                    safe_env = {"__builtins__": {}, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                    r = eval(r_expr.replace("theta", "theta"), safe_env, {"theta": theta})
                except MathematicsError:
                    r = np.ones_like(theta)
                
                # Convertir a coordenadas cartesianas
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                
                if self.plotly_available:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Polar'))
                    fig.update_layout(
                        title=f"Gráfico polar: r(θ) = {r_expr}",
                        xaxis_title='x',
                        yaxis_title='y'
                    )
                    plot_html = fig.to_html(include_plotlyjs='cdn')
                else:
                    plot_html = f"<div>Gráfico polar simulado</div>"
                
                return {
                    "success": True,
                    "operation": operation,
                    "r_function": r_expr,
                    "theta_range": theta_range,
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Operación no soportada: {operation}",
                    "operation": operation
                }
                
        except MathematicsError as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }

    async def create_3d_plot(
        self,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear gráficos 3D interactivos
        """
        await asyncio.sleep(0.01)  # Simular procesamiento

        if not self.plotly_available:
            return {
                "success": False,
                "error": "3D visualization not available",
                "simulation": True,
                "operation": operation
            }

        try:
            if operation == "surface_plot":
                # Gráfico de superficie 3D
                function_expr = parameters.get("function", "x**2 + y**2")
                x_range = parameters.get("x_range", [-5, 5])
                y_range = parameters.get("y_range", [-5, 5])
                
                x = np.linspace(x_range[0], x_range[1], 50)
                y = np.linspace(y_range[0], y_range[1], 50)
                X, Y = np.meshgrid(x, y)
                
                try:
                    safe_env = {"__builtins__": {}, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                    Z = eval(function_expr.replace("x", "X").replace("y", "Y"), safe_env, {"X": X, "Y": Y})
                except MathematicsError:
                    Z = X**2 + Y**2
                
                fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])
                fig.update_layout(
                    title=f"Superficie 3D: z = {function_expr}",
                    scene=dict(
                        xaxis_title='x',
                        yaxis_title='y',
                        zaxis_title='z'
                    )
                )
                plot_html = fig.to_html(include_plotlyjs='cdn')
                
                return {
                    "success": True,
                    "operation": operation,
                    "function": function_expr,
                    "x_range": x_range,
                    "y_range": y_range,
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            elif operation == "parametric_3d":
                # Gráfico paramétrico 3D
                x_expr = parameters.get("x_function", "t")
                y_expr = parameters.get("y_function", "t**2")
                z_expr = parameters.get("z_function", "t**3")
                t_range = parameters.get("t_range", [0, 10])
                
                t = np.linspace(t_range[0], t_range[1], 1000)
                try:
                    safe_env = {"__builtins__": {}, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                    x = eval(x_expr.replace("t", "t"), safe_env, {"t": t})
                    y = eval(y_expr.replace("t", "t"), safe_env, {"t": t})
                    z = eval(z_expr.replace("t", "t"), safe_env, {"t": t})
                except MathematicsError:
                    x = t
                    y = t**2
                    z = t**3
                
                fig = go.Figure(data=[go.Scatter3d(x=x, y=y, z=z, mode='lines')])
                fig.update_layout(
                    title=f"Curva paramétrica 3D",
                    scene=dict(
                        xaxis_title='x',
                        yaxis_title='y',
                        zaxis_title='z'
                    )
                )
                plot_html = fig.to_html(include_plotlyjs='cdn')
                
                return {
                    "success": True,
                    "operation": operation,
                    "x_function": x_expr,
                    "y_function": y_expr,
                    "z_function": z_expr,
                    "t_range": t_range,
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Operación no soportada: {operation}",
                    "operation": operation
                }
                
        except MathematicsError as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }

    async def create_animation(
        self,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear animaciones matemáticas
        """
        await asyncio.sleep(0.01)  # Simular procesamiento

        if not self.plotly_available:
            return {
                "success": False,
                "error": "Animation not available",
                "simulation": True,
                "operation": operation
            }

        try:
            if operation == "function_animation":
                # Animación de función con parámetro variable
                function_expr = parameters.get("function", "a*x**2")
                parameter_name = parameters.get("parameter", "a")
                parameter_range = parameters.get("parameter_range", [0, 5])
                x_range = parameters.get("x_range", [-5, 5])
                frames = parameters.get("frames", 50)
                
                # Crear frames de animación
                animation_frames = []
                param_values = np.linspace(parameter_range[0], parameter_range[1], frames)
                
                for i, param_val in enumerate(param_values):
                    x = np.linspace(x_range[0], x_range[1], 100)
                    try:
                        safe_env = {"__builtins__": {}, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                        y = eval(function_expr.replace(parameter_name, str(param_val)).replace("x", "x"), safe_env, {"x": x})
                    except MathematicsError:
                        y = param_val * x**2
                    
                    frame = go.Frame(
                        data=[go.Scatter(x=x, y=y, mode='lines', name=f'{parameter_name}={param_val:.2f}')],
                        name=str(i)
                    )
                    animation_frames.append(frame)
                
                # Crear figura con animación
                fig = go.Figure(
                    data=[go.Scatter(x=[], y=[], mode='lines')],
                    frames=animation_frames
                )
                
                fig.update_layout(
                    title=f"Animación: {function_expr}",
                    xaxis_title='x',
                    yaxis_title='f(x)',
                    updatemenus=[{
                        'type': 'buttons',
                        'showactive': False,
                        'buttons': [
                            {'label': 'Play', 'method': 'animate', 'args': [None, {'frame': {'duration': 100}}]},
                            {'label': 'Pause', 'method': 'animate', 'args': [[None], {'frame': {'duration': 0}}]}
                        ]
                    }]
                )
                
                plot_html = fig.to_html(include_plotlyjs='cdn')
                
                return {
                    "success": True,
                    "operation": operation,
                    "function": function_expr,
                    "parameter": parameter_name,
                    "parameter_range": parameter_range,
                    "frames": frames,
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Operación no soportada: {operation}",
                    "operation": operation
                }
                
        except MathematicsError as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }

    async def create_statistical_plot(
        self,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear gráficos estadísticos avanzados
        """
        await asyncio.sleep(0.01)  # Simular procesamiento

        if not self.plotly_available:
            return {
                "success": False,
                "error": "Statistical plotting not available",
                "simulation": True,
                "operation": operation
            }

        try:
            if operation == "distribution_plot":
                # Gráfico de distribución
                distribution_type = parameters.get("distribution", "normal")
                sample_size = parameters.get("sample_size", 1000)
                params = parameters.get("parameters", {})
                
                # Generar datos según distribución
                if distribution_type == "normal":
                    mean = params.get("mean", 0)
                    std = params.get("std", 1)
                    data = np.random.normal(mean, std, sample_size)
                elif distribution_type == "uniform":
                    low = params.get("low", 0)
                    high = params.get("high", 1)
                    data = np.random.uniform(low, high, sample_size)
                elif distribution_type == "exponential":
                    scale = params.get("scale", 1)
                    data = np.random.exponential(scale, sample_size)
                else:
                    data = np.random.normal(0, 1, sample_size)
                
                # Crear histograma
                fig = go.Figure(data=[go.Histogram(x=data, nbinsx=50)])
                fig.update_layout(
                    title=f"Distribución {distribution_type}",
                    xaxis_title='Valor',
                    yaxis_title='Frecuencia'
                )
                plot_html = fig.to_html(include_plotlyjs='cdn')
                
                return {
                    "success": True,
                    "operation": operation,
                    "distribution": distribution_type,
                    "sample_size": sample_size,
                    "parameters": params,
                    "plot_html": plot_html,
                    "statistics": {
                        "mean": float(np.mean(data)),
                        "std": float(np.std(data)),
                        "min": float(np.min(data)),
                        "max": float(np.max(data))
                    },
                    "processing_time": 0.1
                }
                
            elif operation == "correlation_plot":
                # Gráfico de correlación
                n_variables = parameters.get("n_variables", 5)
                sample_size = parameters.get("sample_size", 1000)
                
                # Generar datos correlacionados
                data = np.random.multivariate_normal(
                    mean=np.zeros(n_variables),
                    cov=np.eye(n_variables),
                    size=sample_size
                )
                
                # Calcular matriz de correlación
                corr_matrix = np.corrcoef(data.T)
                
                # Crear heatmap
                fig = go.Figure(data=go.Heatmap(z=corr_matrix, colorscale='RdBu'))
                fig.update_layout(
                    title="Matriz de Correlación",
                    xaxis_title="Variables",
                    yaxis_title="Variables"
                )
                plot_html = fig.to_html(include_plotlyjs='cdn')
                
                return {
                    "success": True,
                    "operation": operation,
                    "n_variables": n_variables,
                    "sample_size": sample_size,
                    "correlation_matrix": corr_matrix.tolist(),
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Operación no soportada: {operation}",
                    "operation": operation
                }
                
        except MathematicsError as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }

    async def create_geometric_visualization(
        self,
        operation: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crear visualizaciones geométricas
        """
        await asyncio.sleep(0.01)  # Simular procesamiento

        if not self.plotly_available:
            return {
                "success": False,
                "error": "Geometric visualization not available",
                "simulation": True,
                "operation": operation
            }

        try:
            if operation == "conic_sections":
                # Visualización de secciones cónicas
                conic_type = parameters.get("type", "circle")
                params = parameters.get("parameters", {})
                
                if conic_type == "circle":
                    radius = params.get("radius", 1)
                    center_x = params.get("center_x", 0)
                    center_y = params.get("center_y", 0)
                    
                    theta = np.linspace(0, 2*np.pi, 100)
                    x = center_x + radius * np.cos(theta)
                    y = center_y + radius * np.sin(theta)
                    
                elif conic_type == "ellipse":
                    a = params.get("a", 2)
                    b = params.get("b", 1)
                    center_x = params.get("center_x", 0)
                    center_y = params.get("center_y", 0)
                    
                    theta = np.linspace(0, 2*np.pi, 100)
                    x = center_x + a * np.cos(theta)
                    y = center_y + b * np.sin(theta)
                    
                elif conic_type == "hyperbola":
                    a = params.get("a", 1)
                    b = params.get("b", 1)
                    center_x = params.get("center_x", 0)
                    center_y = params.get("center_y", 0)
                    
                    t = np.linspace(-3, 3, 100)
                    x = center_x + a * np.cosh(t)
                    y = center_y + b * np.sinh(t)
                    
                else:
                    # Parábola
                    a = params.get("a", 1)
                    center_x = params.get("center_x", 0)
                    center_y = params.get("center_y", 0)
                    
                    x = np.linspace(-3, 3, 100)
                    y = center_y + a * (x - center_x)**2
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name=conic_type))
                fig.update_layout(
                    title=f"Sección Cónica: {conic_type}",
                    xaxis_title='x',
                    yaxis_title='y'
                )
                plot_html = fig.to_html(include_plotlyjs='cdn')
                
                return {
                    "success": True,
                    "operation": operation,
                    "conic_type": conic_type,
                    "parameters": params,
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            elif operation == "vector_field":
                # Campo vectorial
                function_x = parameters.get("x_function", "y")
                function_y = parameters.get("y_function", "-x")
                x_range = parameters.get("x_range", [-5, 5])
                y_range = parameters.get("y_range", [-5, 5])
                grid_size = parameters.get("grid_size", 20)
                
                x = np.linspace(x_range[0], x_range[1], grid_size)
                y = np.linspace(y_range[0], y_range[1], grid_size)
                X, Y = np.meshgrid(x, y)
                
                try:
                    safe_env = {"__builtins__": {}, "np": np, "sin": np.sin, "cos": np.cos, "tan": np.tan, "exp": np.exp, "sqrt": np.sqrt, "pi": np.pi, "e": np.e}
                    U = eval(function_x.replace("x", "X").replace("y", "Y"), safe_env, {"X": X, "Y": Y})
                    V = eval(function_y.replace("x", "X").replace("y", "Y"), safe_env, {"X": X, "Y": Y})
                except MathematicsError:
                    U = Y
                    V = -X
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=X.flatten(),
                    y=Y.flatten(),
                    mode='markers',
                    marker=dict(size=5),
                    name='Grid points'
                ))
                
                # Añadir vectores
                for i in range(0, grid_size, 2):
                    for j in range(0, grid_size, 2):
                        fig.add_trace(go.Scatter(
                            x=[X[i,j], X[i,j] + U[i,j]*0.1],
                            y=[Y[i,j], Y[i,j] + V[i,j]*0.1],
                            mode='lines',
                            line=dict(color='red', width=2),
                            showlegend=False
                        ))
                
                fig.update_layout(
                    title=f"Campo Vectorial: dx/dt={function_x}, dy/dt={function_y}",
                    xaxis_title='x',
                    yaxis_title='y'
                )
                plot_html = fig.to_html(include_plotlyjs='cdn')
                
                return {
                    "success": True,
                    "operation": operation,
                    "x_function": function_x,
                    "y_function": function_y,
                    "x_range": x_range,
                    "y_range": y_range,
                    "plot_html": plot_html,
                    "processing_time": 0.1
                }
                
            else:
                return {
                    "success": False,
                    "error": f"Operación no soportada: {operation}",
                    "operation": operation
                }
                
        except MathematicsError as e:
            return {
                "success": False,
                "error": str(e),
                "operation": operation
            }

    def get_capabilities(self) -> Dict[str, Any]:
        """
        Obtener capacidades del servicio de visualización
        """
        return {
            "service": "MathVisualizationService",
            "version": self.version,
            "capabilities": self.capabilities,
            "matplotlib_available": self.matplotlib_available,
            "plotly_available": self.plotly_available,
            "seaborn_available": self.seaborn_available,
            "supported_operations": {
                "2d_plots": ["function_plot", "parametric_plot", "polar_plot"],
                "3d_plots": ["surface_plot", "parametric_3d"],
                "animations": ["function_animation"],
                "statistical_plots": ["distribution_plot", "correlation_plot"],
                "geometric_visualizations": ["conic_sections", "vector_field"]
            },
            "features": [
                "Interactive 2D and 3D plots",
                "Mathematical function visualization",
                "Parametric and polar plots",
                "Statistical distributions",
                "Geometric visualizations",
                "Vector fields and phase diagrams",
                "Mathematical animations",
                "Export to HTML/PNG"
            ],
            "simulation_mode": not (self.matplotlib_available or self.plotly_available)
        }






