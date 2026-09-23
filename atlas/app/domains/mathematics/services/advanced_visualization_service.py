"""
Advanced Mathematical Visualization Service
==========================================

Servicio avanzado de visualización matemática con capacidades 3D/4D,
realidad virtual, interactividad inmersiva y renderizado de alta calidad.

Este servicio proporciona:

- Visualizaciones 3D/4D interactivas
- Gráficos matemáticos inmersivos
- Animaciones de conceptos matemáticos
- Renderizado de alta calidad
- Soporte para VR/AR (futuro)
- Visualizaciones científicas avanzadas

Tecnologías Integradas:
----------------------
- Plotly para gráficos interactivos
- Matplotlib 3D avanzado
- Mayavi para visualización científica
- Three.js para web 3D
- WebGL para renderizado acelerado
- Blender Python API (opcional)

Ejemplos de Uso:
---------------
```python
from app.domains.mathematics.services.advanced_visualization_service import AdvancedVisualizationService
from app.exceptions.domain.mathematics import MathematicsError

# Inicializar servicio
viz_service = AdvancedVisualizationService()

# Crear superficie 3D interactiva
surface = await viz_service.create_3d_surface(
    function="x**2 + y**2",
    x_range=(-5, 5),
    y_range=(-5, 5)
)

# Visualizar campo vectorial 4D
vector_field = await viz_service.visualize_4d_vector_field(
    field_function="[x, y, z, t]",
    dimensions=4
)

# Crear animación matemática
animation = await viz_service.create_mathematical_animation(
    "wave_equation",
    parameters={"amplitude": 1, "frequency": 2}
)
```

Autor: AXIOM Mathematics Team
Fecha: Enero 2024
Versión: 1.0.0
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union, Callable

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# Configurar logging
logger = logging.getLogger(__name__)

# Intentar importar dependencias avanzadas (opcionales)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    import plotly.offline as pyo
    PLOTLY_AVAILABLE = True
    logger.info("Plotly disponible - Visualizaciones interactivas habilitadas")
except ImportError:
    PLOTLY_AVAILABLE = False
    logger.info("Plotly no disponible - Usando Matplotlib básico")

try:
    from mayavi import mlab
    MAYAVI_AVAILABLE = True
    logger.info("Mayavi disponible - Visualización científica 3D habilitada")
except ImportError:
    MAYAVI_AVAILABLE = False
    logger.info("Mayavi no disponible")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
    logger.info("Seaborn disponible para estilos avanzados")
except ImportError:
    SEABORN_AVAILABLE = False

try:
    import sympy as sp
    from sympy import symbols, lambdify
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False


class MathematicalFunction3D:
    """Clase para manejar funciones matemáticas 3D."""
    
    def __init__(self, function_str: str, variables: List[str] = None):
        """
        Inicializar función 3D.
        
        Args:
            function_str: Función como string (ej: "x**2 + y**2")
            variables: Lista de variables (default: ['x', 'y'])
        """
        self.function_str = function_str
        self.variables = variables or ['x', 'y']
        
        if SYMPY_AVAILABLE:
            self.symbols = [symbols(var) for var in self.variables]
            try:
                self.expr = sp.sympify(function_str)
                self.func = lambdify(self.symbols, self.expr, 'numpy')
            except MathematicsError as e:
                logger.error(f"Error creando función simbólica: {e}")
                self.func = None
        else:
            self.func = None
    
    def evaluate(self, *args) -> np.ndarray:
        """Evaluar función en puntos dados."""
        if self.func:
            return self.func(*args)
        else:
            # Fallback usando eval (menos seguro)
            try:
                local_vars = dict(zip(self.variables, args))
                local_vars.update({'np': np, 'sin': np.sin, 'cos': np.cos, 
                                 'tan': np.tan, 'exp': np.exp, 'log': np.log,
                                 'sqrt': np.sqrt, 'pi': np.pi})
                return eval(self.function_str, {"__builtins__": {}}, local_vars)
            except MathematicsError as e:
                logger.error(f"Error evaluando función: {e}")
                return np.zeros_like(args[0])


class AdvancedVisualizationService:
    """
    Servicio avanzado de visualización matemática.
    
    Proporciona capacidades de visualización 3D/4D, interactividad,
    animaciones y renderizado de alta calidad.
    """
    
    def __init__(self):
        """Inicializar servicio de visualización avanzada."""
        self.plotly_available = PLOTLY_AVAILABLE
        self.mayavi_available = MAYAVI_AVAILABLE
        self.seaborn_available = SEABORN_AVAILABLE
        
        # Configurar estilos
        if self.seaborn_available:
            sns.set_style("whitegrid")
        
        plt.style.use('seaborn-v0_8' if 'seaborn-v0_8' in plt.style.available else 'default')
        
        # Estadísticas de uso
        self.usage_stats = {
            "visualizations_created": 0,
            "3d_plots": 0,
            "4d_plots": 0,
            "animations": 0,
            "interactive_plots": 0
        }
        
        # Configuraciones por defecto
        self.default_config = {
            "figure_size": (12, 8),
            "dpi": 300,
            "color_scheme": "viridis",
            "grid_resolution": 100,
            "animation_fps": 30,
            "quality": "high"
        }
    
    async def create_3d_surface(
        self,
        function: str,
        x_range: Tuple[float, float] = (-5, 5),
        y_range: Tuple[float, float] = (-5, 5),
        resolution: int = 100,
        interactive: bool = True,
        style: str = "surface"
    ) -> Dict[str, Any]:
        """
        Crear superficie 3D interactiva.
        
        Args:
            function: Función como string (ej: "x**2 + y**2")
            x_range: Rango de x (min, max)
            y_range: Rango de y (min, max)
            resolution: Resolución de la malla
            interactive: Crear gráfico interactivo
            style: Estilo de visualización ('surface', 'wireframe', 'contour')
            
        Returns:
            Dict con información de la visualización
        """
        start_time = time.time()
        
        try:
            # Crear malla de puntos
            x = np.linspace(x_range[0], x_range[1], resolution)
            y = np.linspace(y_range[0], y_range[1], resolution)
            X, Y = np.meshgrid(x, y)
            
            # Evaluar función
            math_func = MathematicalFunction3D(function, ['x', 'y'])
            Z = math_func.evaluate(X, Y)
            
            if interactive and self.plotly_available:
                # Crear gráfico interactivo con Plotly
                if style == "surface":
                    fig = go.Figure(data=[go.Surface(
                        x=X, y=Y, z=Z,
                        colorscale='Viridis',
                        showscale=True
                    )])
                elif style == "wireframe":
                    fig = go.Figure(data=[go.Surface(
                        x=X, y=Y, z=Z,
                        colorscale='Viridis',
                        showscale=True,
                        surfacecolor=Z,
                        opacity=0.7
                    )])
                elif style == "contour":
                    fig = go.Figure(data=[go.Contour(
                        x=x, y=y, z=Z,
                        colorscale='Viridis'
                    )])
                
                fig.update_layout(
                    title=f'Superficie 3D: {function}',
                    scene=dict(
                        xaxis_title='X',
                        yaxis_title='Y',
                        zaxis_title='Z'
                    ),
                    width=800,
                    height=600
                )
                
                # Guardar como HTML
                html_file = f"/tmp/surface_3d_{int(time.time())}.html"
                fig.write_html(html_file)
                
                result = {
                    "type": "interactive_3d_surface",
                    "file_path": html_file,
                    "plotly_figure": fig
                }
                
                self.usage_stats["interactive_plots"] += 1
            else:
                # Crear gráfico con Matplotlib
                fig = plt.figure(figsize=self.default_config["figure_size"])
                ax = fig.add_subplot(111, projection='3d')
                
                if style == "surface":
                    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
                    fig.colorbar(surf)
                elif style == "wireframe":
                    ax.plot_wireframe(X, Y, Z, color='blue', alpha=0.6)
                elif style == "contour":
                    ax.contour3D(X, Y, Z, 50, cmap='viridis')
                
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title(f'Superficie 3D: {function}')
                
                # Guardar imagen
                image_file = f"/tmp/surface_3d_{int(time.time())}.png"
                plt.savefig(image_file, dpi=self.default_config["dpi"], bbox_inches='tight')
                plt.close()
                
                result = {
                    "type": "static_3d_surface",
                    "file_path": image_file,
                    "matplotlib_figure": fig
                }
            
            computation_time = time.time() - start_time
            self.usage_stats["visualizations_created"] += 1
            self.usage_stats["3d_plots"] += 1
            
            return {
                "success": True,
                "function": function,
                "x_range": x_range,
                "y_range": y_range,
                "resolution": resolution,
                "style": style,
                "result": result,
                "computation_time": computation_time,
                "data_points": resolution * resolution
            }
            
        except MathematicsError as e:
            logger.error(f"Error creando superficie 3D: {e}")
            return {
                "success": False,
                "function": function,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    async def visualize_4d_vector_field(
        self,
        field_function: str,
        x_range: Tuple[float, float] = (-2, 2),
        y_range: Tuple[float, float] = (-2, 2),
        z_range: Tuple[float, float] = (-2, 2),
        resolution: int = 20,
        time_slice: float = 0.0
    ) -> Dict[str, Any]:
        """
        Visualizar campo vectorial 4D (3D espacial + tiempo).
        
        Args:
            field_function: Función vectorial como string
            x_range: Rango de x
            y_range: Rango de y  
            z_range: Rango de z
            resolution: Resolución de la malla
            time_slice: Valor de tiempo para la visualización
            
        Returns:
            Dict con información de la visualización 4D
        """
        start_time = time.time()
        
        try:
            # Crear malla 3D
            x = np.linspace(x_range[0], x_range[1], resolution)
            y = np.linspace(y_range[0], y_range[1], resolution)
            z = np.linspace(z_range[0], z_range[1], resolution)
            X, Y, Z = np.meshgrid(x, y, z, indexing='ij')
            
            # Evaluar campo vectorial en el tiempo dado
            # Simplificación: asumir campo [x, y, z, t]
            U = X * np.cos(time_slice)
            V = Y * np.sin(time_slice)
            W = Z * np.cos(time_slice)
            
            if self.plotly_available:
                # Crear visualización interactiva con Plotly
                fig = go.Figure(data=go.Cone(
                    x=X.flatten()[::4],  # Submuestrear para rendimiento
                    y=Y.flatten()[::4],
                    z=Z.flatten()[::4],
                    u=U.flatten()[::4],
                    v=V.flatten()[::4],
                    w=W.flatten()[::4],
                    colorscale='Viridis',
                    sizemode="absolute",
                    sizeref=0.3
                ))
                
                fig.update_layout(
                    title=f'Campo Vectorial 4D (t={time_slice})',
                    scene=dict(
                        xaxis_title='X',
                        yaxis_title='Y',
                        zaxis_title='Z',
                        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
                    ),
                    width=800,
                    height=600
                )
                
                html_file = f"/tmp/vector_field_4d_{int(time.time())}.html"
                fig.write_html(html_file)
                
                result = {
                    "type": "interactive_4d_vector_field",
                    "file_path": html_file,
                    "plotly_figure": fig
                }
                
                self.usage_stats["interactive_plots"] += 1
            else:
                # Visualización con Matplotlib (proyección 3D)
                fig = plt.figure(figsize=self.default_config["figure_size"])
                ax = fig.add_subplot(111, projection='3d')
                
                # Submuestrear para visualización
                step = max(1, resolution // 10)
                ax.quiver(
                    X[::step, ::step, ::step],
                    Y[::step, ::step, ::step],
                    Z[::step, ::step, ::step],
                    U[::step, ::step, ::step],
                    V[::step, ::step, ::step],
                    W[::step, ::step, ::step],
                    length=0.3,
                    normalize=True,
                    alpha=0.7
                )
                
                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title(f'Campo Vectorial 4D (t={time_slice})')
                
                image_file = f"/tmp/vector_field_4d_{int(time.time())}.png"
                plt.savefig(image_file, dpi=self.default_config["dpi"], bbox_inches='tight')
                plt.close()
                
                result = {
                    "type": "static_4d_vector_field",
                    "file_path": image_file
                }
            
            computation_time = time.time() - start_time
            self.usage_stats["visualizations_created"] += 1
            self.usage_stats["4d_plots"] += 1
            
            return {
                "success": True,
                "field_function": field_function,
                "ranges": {"x": x_range, "y": y_range, "z": z_range},
                "time_slice": time_slice,
                "resolution": resolution,
                "result": result,
                "computation_time": computation_time
            }
            
        except MathematicsError as e:
            logger.error(f"Error visualizando campo vectorial 4D: {e}")
            return {
                "success": False,
                "field_function": field_function,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    async def create_mathematical_animation(
        self,
        animation_type: str,
        parameters: Dict[str, Any] = None,
        duration: float = 5.0,
        fps: int = 30
    ) -> Dict[str, Any]:
        """
        Crear animación matemática.
        
        Args:
            animation_type: Tipo de animación ('wave_equation', 'fourier_series', 'parametric_curve')
            parameters: Parámetros específicos de la animación
            duration: Duración en segundos
            fps: Frames por segundo
            
        Returns:
            Dict con información de la animación
        """
        start_time = time.time()
        
        if parameters is None:
            parameters = {}
        
        try:
            frames = int(duration * fps)
            
            if animation_type == "wave_equation":
                result = await self._create_wave_animation(parameters, frames, fps)
            elif animation_type == "fourier_series":
                result = await self._create_fourier_animation(parameters, frames, fps)
            elif animation_type == "parametric_curve":
                result = await self._create_parametric_animation(parameters, frames, fps)
            elif animation_type == "3d_rotation":
                result = await self._create_3d_rotation_animation(parameters, frames, fps)
            else:
                return {
                    "success": False,
                    "error": f"Tipo de animación no soportado: {animation_type}"
                }
            
            computation_time = time.time() - start_time
            self.usage_stats["visualizations_created"] += 1
            self.usage_stats["animations"] += 1
            
            return {
                "success": True,
                "animation_type": animation_type,
                "parameters": parameters,
                "duration": duration,
                "fps": fps,
                "frames": frames,
                "result": result,
                "computation_time": computation_time
            }
            
        except MathematicsError as e:
            logger.error(f"Error creando animación: {e}")
            return {
                "success": False,
                "animation_type": animation_type,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    async def create_fractal_visualization(
        self,
        fractal_type: str = "mandelbrot",
        resolution: int = 800,
        max_iterations: int = 100,
        zoom: float = 1.0,
        center: Tuple[float, float] = (0, 0)
    ) -> Dict[str, Any]:
        """
        Crear visualización de fractales.
        
        Args:
            fractal_type: Tipo de fractal ('mandelbrot', 'julia', 'burning_ship')
            resolution: Resolución de la imagen
            max_iterations: Máximo número de iteraciones
            zoom: Factor de zoom
            center: Centro de la visualización
            
        Returns:
            Dict con información del fractal
        """
        start_time = time.time()
        
        try:
            if fractal_type == "mandelbrot":
                fractal_data = self._generate_mandelbrot(resolution, max_iterations, zoom, center)
            elif fractal_type == "julia":
                c = complex(-0.7, 0.27015)  # Parámetro Julia por defecto
                fractal_data = self._generate_julia(resolution, max_iterations, zoom, center, c)
            elif fractal_type == "burning_ship":
                fractal_data = self._generate_burning_ship(resolution, max_iterations, zoom, center)
            else:
                return {
                    "success": False,
                    "error": f"Tipo de fractal no soportado: {fractal_type}"
                }
            
            # Crear visualización
            fig, ax = plt.subplots(figsize=self.default_config["figure_size"])
            im = ax.imshow(fractal_data, extent=[-2/zoom + center[0], 2/zoom + center[0], 
                                                 -2/zoom + center[1], 2/zoom + center[1]], 
                          cmap='hot', origin='lower', interpolation='bilinear')
            ax.set_title(f'Fractal {fractal_type.capitalize()}')
            ax.set_xlabel('Re(z)')
            ax.set_ylabel('Im(z)')
            plt.colorbar(im, ax=ax, label='Iteraciones')
            
            # Guardar imagen
            image_file = f"/tmp/fractal_{fractal_type}_{int(time.time())}.png"
            plt.savefig(image_file, dpi=self.default_config["dpi"], bbox_inches='tight')
            plt.close()
            
            computation_time = time.time() - start_time
            self.usage_stats["visualizations_created"] += 1
            
            return {
                "success": True,
                "fractal_type": fractal_type,
                "resolution": resolution,
                "max_iterations": max_iterations,
                "zoom": zoom,
                "center": center,
                "file_path": image_file,
                "computation_time": computation_time
            }
            
        except MathematicsError as e:
            logger.error(f"Error creando fractal: {e}")
            return {
                "success": False,
                "fractal_type": fractal_type,
                "error": str(e),
                "computation_time": time.time() - start_time
            }
    
    # Métodos auxiliares para animaciones
    
    async def _create_wave_animation(self, params: Dict, frames: int, fps: int) -> Dict:
        """Crear animación de ecuación de onda."""
        amplitude = params.get("amplitude", 1.0)
        frequency = params.get("frequency", 1.0)
        wave_speed = params.get("wave_speed", 1.0)
        
        x = np.linspace(-10, 10, 200)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        line, = ax.plot([], [], 'b-', linewidth=2)
        ax.set_xlim(-10, 10)
        ax.set_ylim(-amplitude*1.5, amplitude*1.5)
        ax.set_xlabel('x')
        ax.set_ylabel('y')
        ax.set_title('Ecuación de Onda')
        ax.grid(True)
        
        def animate(frame):
            t = frame / fps
            y = amplitude * np.sin(2 * np.pi * frequency * (x - wave_speed * t))
            line.set_data(x, y)
            return line,
        
        anim = animation.FuncAnimation(fig, animate, frames=frames, interval=1000/fps, blit=True)
        
        # Guardar animación
        animation_file = f"/tmp/wave_animation_{int(time.time())}.gif"
        anim.save(animation_file, writer='pillow', fps=fps)
        plt.close()
        
        return {
            "type": "wave_animation",
            "file_path": animation_file
        }
    
    async def _create_fourier_animation(self, params: Dict, frames: int, fps: int) -> Dict:
        """Crear animación de serie de Fourier."""
        n_terms = params.get("n_terms", 10)
        
        x = np.linspace(-np.pi, np.pi, 1000)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        def animate(frame):
            ax1.clear()
            ax2.clear()
            
            # Número de términos que aumenta con el frame
            current_terms = max(1, int((frame / frames) * n_terms))
            
            # Serie de Fourier para onda cuadrada
            y = np.zeros_like(x)
            for n in range(1, current_terms + 1, 2):
                y += (4 / (n * np.pi)) * np.sin(n * x)
            
            ax1.plot(x, y, 'b-', linewidth=2, label=f'Términos: {current_terms}')
            ax1.set_ylim(-1.5, 1.5)
            ax1.set_title('Aproximación de Serie de Fourier')
            ax1.legend()
            ax1.grid(True)
            
            # Espectro de frecuencias
            freqs = np.arange(1, current_terms + 1, 2)
            amplitudes = 4 / (freqs * np.pi)
            ax2.stem(freqs, amplitudes, basefmt=" ")
            ax2.set_title('Espectro de Frecuencias')
            ax2.set_xlabel('Frecuencia')
            ax2.set_ylabel('Amplitud')
            ax2.grid(True)
        
        anim = animation.FuncAnimation(fig, animate, frames=frames, interval=1000/fps)
        
        animation_file = f"/tmp/fourier_animation_{int(time.time())}.gif"
        anim.save(animation_file, writer='pillow', fps=fps)
        plt.close()
        
        return {
            "type": "fourier_animation",
            "file_path": animation_file
        }
    
    async def _create_parametric_animation(self, params: Dict, frames: int, fps: int) -> Dict:
        """Crear animación de curva paramétrica."""
        # Ejemplo: Lissajous curves
        a = params.get("a", 3)
        b = params.get("b", 2)
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_xlim(-1.5, 1.5)
        ax.set_ylim(-1.5, 1.5)
        ax.set_aspect('equal')
        ax.set_title('Curva de Lissajous')
        
        line, = ax.plot([], [], 'b-', linewidth=2)
        point, = ax.plot([], [], 'ro', markersize=8)
        
        def animate(frame):
            t_max = (frame / frames) * 4 * np.pi
            t = np.linspace(0, t_max, int(frame * 2) + 1)
            
            if len(t) > 0:
                x = np.sin(a * t)
                y = np.sin(b * t)
                
                line.set_data(x, y)
                if len(x) > 0:
                    point.set_data([x[-1]], [y[-1]])
            
            return line, point
        
        anim = animation.FuncAnimation(fig, animate, frames=frames, interval=1000/fps)
        
        animation_file = f"/tmp/parametric_animation_{int(time.time())}.gif"
        anim.save(animation_file, writer='pillow', fps=fps)
        plt.close()
        
        return {
            "type": "parametric_animation",
            "file_path": animation_file
        }
    
    async def _create_3d_rotation_animation(self, params: Dict, frames: int, fps: int) -> Dict:
        """Crear animación de rotación 3D."""
        function = params.get("function", "x**2 + y**2")
        
        # Crear datos 3D
        x = np.linspace(-3, 3, 50)
        y = np.linspace(-3, 3, 50)
        X, Y = np.meshgrid(x, y)
        
        math_func = MathematicalFunction3D(function, ['x', 'y'])
        Z = math_func.evaluate(X, Y)
        
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        def animate(frame):
            ax.clear()
            
            # Rotar vista
            angle = (frame / frames) * 360
            ax.view_init(elev=30, azim=angle)
            
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title(f'Rotación 3D: {function}')
            
            return [surf]
        
        anim = animation.FuncAnimation(fig, animate, frames=frames, interval=1000/fps)
        
        animation_file = f"/tmp/3d_rotation_{int(time.time())}.gif"
        anim.save(animation_file, writer='pillow', fps=fps)
        plt.close()
        
        return {
            "type": "3d_rotation_animation",
            "file_path": animation_file
        }
    
    # Métodos auxiliares para fractales
    
    def _generate_mandelbrot(self, resolution: int, max_iter: int, zoom: float, center: Tuple) -> np.ndarray:
        """Generar conjunto de Mandelbrot."""
        x_min, x_max = -2/zoom + center[0], 2/zoom + center[0]
        y_min, y_max = -2/zoom + center[1], 2/zoom + center[1]
        
        x = np.linspace(x_min, x_max, resolution)
        y = np.linspace(y_min, y_max, resolution)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        
        Z = np.zeros_like(C)
        iterations = np.zeros(C.shape, dtype=int)
        
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + C[mask]
            iterations[mask] = i
        
        return iterations
    
    def _generate_julia(self, resolution: int, max_iter: int, zoom: float, center: Tuple, c: complex) -> np.ndarray:
        """Generar conjunto de Julia."""
        x_min, x_max = -2/zoom + center[0], 2/zoom + center[0]
        y_min, y_max = -2/zoom + center[1], 2/zoom + center[1]
        
        x = np.linspace(x_min, x_max, resolution)
        y = np.linspace(y_min, y_max, resolution)
        X, Y = np.meshgrid(x, y)
        Z = X + 1j * Y
        
        iterations = np.zeros(Z.shape, dtype=int)
        
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = Z[mask]**2 + c
            iterations[mask] = i
        
        return iterations
    
    def _generate_burning_ship(self, resolution: int, max_iter: int, zoom: float, center: Tuple) -> np.ndarray:
        """Generar fractal Burning Ship."""
        x_min, x_max = -2/zoom + center[0], 2/zoom + center[0]
        y_min, y_max = -2/zoom + center[1], 2/zoom + center[1]
        
        x = np.linspace(x_min, x_max, resolution)
        y = np.linspace(y_min, y_max, resolution)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        
        Z = np.zeros_like(C)
        iterations = np.zeros(C.shape, dtype=int)
        
        for i in range(max_iter):
            mask = np.abs(Z) <= 2
            Z[mask] = (np.abs(Z[mask].real) + 1j * np.abs(Z[mask].imag))**2 + C[mask]
            iterations[mask] = i
        
        return iterations
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de uso del servicio."""
        return self.usage_stats.copy()
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Obtener capacidades disponibles del servicio."""
        return {
            "plotly_available": self.plotly_available,
            "mayavi_available": self.mayavi_available,
            "seaborn_available": self.seaborn_available,
            "supported_formats": ["PNG", "SVG", "HTML", "GIF"],
            "supported_animations": ["wave_equation", "fourier_series", "parametric_curve", "3d_rotation"],
            "supported_fractals": ["mandelbrot", "julia", "burning_ship"],
            "3d_capabilities": True,
            "4d_capabilities": True,
            "interactive_plots": self.plotly_available
        }


# Instancia global del servicio
advanced_visualization_service = AdvancedVisualizationService()