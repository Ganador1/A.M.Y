"""
Matplotlib Service - Visualización Científica
Proporciona generación de gráficos y visualizaciones
"""

from typing import Dict, Any
import logging
import io
import base64

from app.core.real_matplotlib import get_real_pyplot

logger = logging.getLogger(__name__)


class MatplotlibService:
    """Servicio para visualización de datos usando Matplotlib"""
    
    def __init__(self):
        self.service_name = "MatplotlibService"
        logger.info(f"✅ {self.service_name} initialized")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de visualización
        
        Operaciones soportadas:
        - 'create_line_plot' / 'line_plot': Gráfico de línea
        - 'create_scatter_plot' / 'scatter_plot': Gráfico de dispersión
        - 'create_histogram' / 'histogram': Histograma
        - 'create_bar_plot' / 'bar_plot': Gráfico de barras
        - 'create_heatmap' / 'heatmap': Mapa de calor
        - 'create_contour_plot' / 'contour_plot': Gráfico de contornos
        - 'create_3d_surface' / '3d_surface': Superficie 3D
        """
        # Soportar tanto 'action' como 'operation' para compatibilidad
        operation = request_data.get('operation') or request_data.get('action')
        
        # Normalizar aliases para retrocompatibilidad
        if operation in ('line_plot', 'create_line_plot'):
            return await self.create_line_plot(request_data)
        elif operation in ('scatter_plot', 'create_scatter_plot'):
            return await self.create_scatter_plot(request_data)
        elif operation in ('histogram', 'create_histogram'):
            return await self.create_histogram(request_data)
        elif operation in ('bar_plot', 'create_bar_plot'):
            return await self.create_bar_plot(request_data)
        elif operation in ('heatmap', 'create_heatmap'):
            return await self.create_heatmap(request_data)
        elif operation in ('contour_plot', 'create_contour_plot'):
            return await self.create_contour_plot(request_data)
        elif operation in ('3d_surface', 'create_3d_surface'):
            return await self.create_3d_surface(request_data)
        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}",
                "supported_operations": ['create_line_plot', 'create_scatter_plot', 'create_histogram', 'create_bar_plot', 'create_heatmap', 'create_contour_plot', 'create_3d_surface']
            }
    
    def _fig_to_base64(self, fig) -> str:
        """Convertir figura matplotlib a base64"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()
        return img_base64
    
    async def create_line_plot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear gráfico de líneas"""
        try:
            plt = get_real_pyplot()
            import numpy as np
            
            # Datos de ejemplo
            x = np.linspace(0, 10, 100)
            y1 = np.sin(x)
            y2 = np.cos(x)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(x, y1, label='sin(x)', linewidth=2)
            ax.plot(x, y2, label='cos(x)', linewidth=2)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title('Trigonometric Functions')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Convertir a base64
            img_data = self._fig_to_base64(fig)
            plt.close(fig)
            
            return {
                "success": True,
                "operation": "line_plot",
                "plot_type": "line",
                "data_points": len(x),
                "image_base64": img_data,
                "dimensions": "10x6"
            }
            
        except Exception as e:
            logger.error(f"Error creating line plot: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "line_plot"
            }
    
    async def create_scatter_plot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear gráfico de dispersión"""
        try:
            plt = get_real_pyplot()
            import numpy as np
            
            # Datos de ejemplo
            n_points = 200
            x = np.random.randn(n_points)
            y = 2 * x + np.random.randn(n_points) * 0.5
            colors = np.random.rand(n_points)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            scatter = ax.scatter(x, y, c=colors, cmap='viridis', alpha=0.6, s=50)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title('Scatter Plot with Color Mapping')
            plt.colorbar(scatter, ax=ax, label='Color Value')
            ax.grid(True, alpha=0.3)
            
            img_data = self._fig_to_base64(fig)
            plt.close(fig)
            
            return {
                "success": True,
                "operation": "scatter_plot",
                "plot_type": "scatter",
                "data_points": n_points,
                "image_base64": img_data
            }
            
        except Exception as e:
            logger.error(f"Error creating scatter plot: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "scatter_plot"
            }
    
    async def create_histogram(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear histograma"""
        try:
            plt = get_real_pyplot()
            import numpy as np
            
            # Datos de ejemplo - distribución normal
            data = np.random.normal(100, 15, 1000)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            n, bins, patches = ax.hist(data, bins=30, edgecolor='black', alpha=0.7)
            ax.set_xlabel('Value')
            ax.set_ylabel('Frequency')
            ax.set_title('Histogram - Normal Distribution')
            ax.grid(True, alpha=0.3, axis='y')
            
            img_data = self._fig_to_base64(fig)
            plt.close(fig)
            
            return {
                "success": True,
                "operation": "histogram",
                "plot_type": "histogram",
                "data_points": len(data),
                "bins": 30,
                "mean": float(np.mean(data)),
                "std": float(np.std(data)),
                "image_base64": img_data
            }
            
        except Exception as e:
            logger.error(f"Error creating histogram: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "histogram"
            }
    
    async def create_bar_plot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear gráfico de barras"""
        try:
            plt = get_real_pyplot()
            import numpy as np
            
            # Datos de ejemplo
            categories = ['A', 'B', 'C', 'D', 'E']
            values = [23, 45, 56, 78, 32]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(categories, values, color='steelblue', alpha=0.7)
            ax.set_xlabel('Categories')
            ax.set_ylabel('Values')
            ax.set_title('Bar Plot')
            ax.grid(True, alpha=0.3, axis='y')
            
            # Añadir valores sobre las barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom')
            
            img_data = self._fig_to_base64(fig)
            plt.close(fig)
            
            return {
                "success": True,
                "operation": "bar_plot",
                "plot_type": "bar",
                "categories": len(categories),
                "total_value": sum(values),
                "image_base64": img_data
            }
            
        except Exception as e:
            logger.error(f"Error creating bar plot: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "bar_plot"
            }
    
    async def create_heatmap(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear mapa de calor"""
        try:
            plt = get_real_pyplot()
            import numpy as np
            
            # Datos de ejemplo - matriz de correlación
            size = 10
            data = np.random.rand(size, size)
            
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(data, cmap='coolwarm', aspect='auto')
            ax.set_title('Heatmap')
            plt.colorbar(im, ax=ax, label='Value')
            
            # Añadir grid
            ax.set_xticks(np.arange(size))
            ax.set_yticks(np.arange(size))
            ax.grid(False)
            
            img_data = self._fig_to_base64(fig)
            plt.close(fig)
            
            return {
                "success": True,
                "operation": "heatmap",
                "plot_type": "heatmap",
                "matrix_size": f"{size}x{size}",
                "min_value": float(np.min(data)),
                "max_value": float(np.max(data)),
                "image_base64": img_data
            }
            
        except Exception as e:
            logger.error(f"Error creating heatmap: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "heatmap"
            }
    
    async def create_contour_plot(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear gráfico de contornos"""
        try:
            plt = get_real_pyplot()
            import numpy as np
            
            # Datos de ejemplo - función 2D
            x = np.linspace(-3, 3, 100)
            y = np.linspace(-3, 3, 100)
            X, Y = np.meshgrid(x, y)
            Z = np.sin(np.sqrt(X**2 + Y**2))
            
            fig, ax = plt.subplots(figsize=(10, 8))
            contour = ax.contourf(X, Y, Z, levels=20, cmap='viridis')
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_title('Contour Plot - sin(sqrt(x² + y²))')
            plt.colorbar(contour, ax=ax, label='Z value')
            
            img_data = self._fig_to_base64(fig)
            plt.close(fig)
            
            return {
                "success": True,
                "operation": "contour_plot",
                "plot_type": "contour",
                "grid_size": "100x100",
                "levels": 20,
                "image_base64": img_data
            }
            
        except Exception as e:
            logger.error(f"Error creating contour plot: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "contour_plot"
            }
    
    async def create_3d_surface(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear superficie 3D"""
        try:
            plt = get_real_pyplot()
            from mpl_toolkits.mplot3d import Axes3D
            import numpy as np
            
            # Datos de ejemplo
            x = np.linspace(-5, 5, 50)
            y = np.linspace(-5, 5, 50)
            X, Y = np.meshgrid(x, y)
            Z = np.sin(np.sqrt(X**2 + Y**2))
            
            fig = plt.figure(figsize=(12, 9))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
            ax.set_xlabel('X')
            ax.set_ylabel('Y')
            ax.set_zlabel('Z')
            ax.set_title('3D Surface Plot')
            fig.colorbar(surf, ax=ax, label='Z value')
            
            img_data = self._fig_to_base64(fig)
            plt.close(fig)
            
            return {
                "success": True,
                "operation": "3d_surface",
                "plot_type": "3d_surface",
                "grid_size": "50x50",
                "image_base64": img_data
            }
            
        except Exception as e:
            logger.error(f"Error creating 3D surface: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": "3d_surface"
            }
