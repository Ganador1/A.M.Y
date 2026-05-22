"""
Graphing service
Servicio para generar gráficos matemáticos
"""

import matplotlib
from app.exceptions.domain.biology import BiologyError
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
import numpy as np
import sympy as sp
import os
from typing import List, Optional, Dict
from app.models import GraphingRequest, GraphResponse


class GraphingService:
    """Servicio para generar gráficos matemáticos"""
    
    @staticmethod
    def generate_graph(request: GraphingRequest) -> GraphResponse:
        """
        Genera un gráfico de una función matemática
        
        Args:
            request: Solicitud con parámetros del gráfico
            
        Returns:
            Respuesta con información del gráfico generado
        """
        try:
            # Crear símbolo para la variable
            var = sp.Symbol(request.variable)
            
            # Parsear la expresión
            expression = sp.sympify(request.expression)
            
            # Generar puntos x
            x_values = np.linspace(request.x_min, request.x_max, request.points)
            
            # Convertir la expresión a función NumPy
            func = sp.lambdify(var, expression, 'numpy')
            
            # Calcular valores y
            y_values = func(x_values)
            
            # Crear el gráfico
            plt.figure(figsize=(10, 6))
            plt.plot(x_values, y_values, 'b-', linewidth=2)
            plt.grid(True, alpha=0.3)
            plt.xlabel(f'{request.variable}')
            plt.ylabel(f'f({request.variable})')
            
            # Título del gráfico
            title = request.title if request.title else f'Gráfico de {request.expression}'
            plt.title(title)
            
            # Configurar ejes
            plt.axhline(y=0, color='k', linewidth=0.5)
            plt.axvline(x=0, color='k', linewidth=0.5)
            
            # Guardar el gráfico
            os.makedirs('static/graphs', exist_ok=True)
            image_filename = f'graph_{hash(request.expression)}_{request.x_min}_{request.x_max}.png'
            image_path = f'static/graphs/{image_filename}'
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            # Calcular rango y
            y_min = float(np.min(y_values)) if not np.isnan(np.min(y_values)) else 0
            y_max = float(np.max(y_values)) if not np.isnan(np.max(y_values)) else 0
            
            return GraphResponse(
                expression=request.expression,
                image_path=image_path,
                x_range=[request.x_min, request.x_max],
                y_range=[y_min, y_max],
                points_count=request.points
            )
            
        except BiologyError as e:
            raise ValueError(f"Error generando gráfico: {str(e)}")
    
    @staticmethod
    def generate_multiple_graphs(expressions: List[str], x_min: float = -10, x_max: float = 10, 
                                points: int = 1000, variable: str = 'x') -> dict:
        """
        Genera múltiples gráficos en una misma figura
        
        Args:
            expressions: Lista de expresiones matemáticas
            x_min: Valor mínimo de x
            x_max: Valor máximo de x
            points: Número de puntos
            variable: Variable independiente
            
        Returns:
            Diccionario con información del gráfico
        """
        try:
            # Crear símbolo para la variable
            var = sp.Symbol(variable)
            
            # Generar puntos x
            x_values = np.linspace(x_min, x_max, points)
            
            # Crear figura
            plt.figure(figsize=(12, 8))
            
            colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
            
            for i, expr_str in enumerate(expressions):
                try:
                    # Parsear expresión
                    expression = sp.sympify(expr_str)
                    
                    # Convertir a función NumPy
                    func = sp.lambdify(var, expression, 'numpy')
                    
                    # Calcular valores y
                    y_values = func(x_values)
                    
                    # Graficar
                    color = colors[i % len(colors)]
                    plt.plot(x_values, y_values, color=color, linewidth=2, label=expr_str)
                    
                except BiologyError as e:
                    print(f"Error graficando {expr_str}: {e}")
                    continue
            
            # Configurar gráfico
            plt.grid(True, alpha=0.3)
            plt.xlabel(variable)
            plt.ylabel(f'f({variable})')
            plt.title('Gráfico de múltiples funciones')
            plt.legend()
            plt.axhline(y=0, color='k', linewidth=0.5)
            plt.axvline(x=0, color='k', linewidth=0.5)
            
            # Guardar gráfico
            os.makedirs('static/graphs', exist_ok=True)
            image_filename = f'multiple_graph_{hash(str(expressions))}_{x_min}_{x_max}.png'
            image_path = f'static/graphs/{image_filename}'
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "expressions": expressions,
                "image_path": image_path,
                "x_range": [x_min, x_max],
                "points_count": points
            }
            
        except BiologyError as e:
            raise ValueError(f"Error generando gráficos múltiples: {str(e)}")
    
    @staticmethod
    def generate_3d_graph(expression: str, x_min: float = -5, x_max: float = 5,
                         y_min: float = -5, y_max: float = 5, points: int = 50,
                         colorscale: Optional[str] = None, opacity: Optional[float] = None) -> dict:
        """
        Genera un gráfico 3D interactivo de una función de dos variables usando Plotly
        
        Args:
            expression: Expresión matemática con variables x e y
            x_min, x_max: Rango de x
            y_min, y_max: Rango de y
            points: Número de puntos por eje
            colorscale: Escala de colores para la superficie
            opacity: Opacidad de la superficie
            
        Returns:
            Diccionario con información del gráfico 3D interactivo
        """
        try:
            import plotly.graph_objects as go
            
            # Crear símbolos
            x, y = sp.symbols('x y')
            
            # Parsear expresión
            expr = sp.sympify(expression)
            
            # Crear malla de puntos
            x_vals = np.linspace(x_min, x_max, points)
            y_vals = np.linspace(y_min, y_max, points)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Convertir a función NumPy
            func = sp.lambdify((x, y), expr, 'numpy')
            
            # Calcular valores z
            Z = func(X, Y)
            
            # Crear gráfico 3D interactivo
            surface_data = go.Surface(z=Z, x=X, y=Y)
            if colorscale: surface_data.colorscale = colorscale
            if opacity: surface_data.opacity = opacity

            fig = go.Figure(data=[surface_data])
            fig.update_layout(
                title=f'Gráfico 3D Interactivo: {expression}',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='f(x,y)'
                )
            )
            
            # Guardar el gráfico como HTML
            os.makedirs('static/graphs', exist_ok=True)
            html_filename = f'3d_graph_interactive_{hash(expression)}_{x_min}_{x_max}_{y_min}_{y_max}.html'
            html_path = f'static/graphs/{html_filename}'
            fig.write_html(html_path, auto_open=False)
            
            return {
                "expression": expression,
                "html_path": html_path,
                "x_range": [x_min, x_max],
                "y_range": [y_min, y_max],
                "points_count": points
            }
            
        except BiologyError as e:
            raise ValueError(f"Error generando gráfico 3D interactivo: {str(e)}")
    
    @staticmethod
    def generate_3d_surface(expression: str, x_min: float = -5, x_max: float = 5,
                           y_min: float = -5, y_max: float = 5, points: int = 50,
                           colorscale: Optional[str] = None, opacity: Optional[float] = None) -> dict:
        """
        Genera un gráfico 3D de superficie interactivo con Plotly
        
        Args:
            expression: Expresión matemática con variables x e y
            x_min, x_max: Rango de x
            y_min, y_max: Rango de y
            points: Número de puntos por eje
            colorscale: Escala de colores para la superficie
            opacity: Opacidad de la superficie
            
        Returns:
            Diccionario con información del gráfico 3D de superficie interactivo
        """
        try:
            import plotly.graph_objects as go
            
            # Crear símbolos
            x, y = sp.symbols('x y')
            
            # Parsear expresión
            expr = sp.sympify(expression)
            
            # Crear malla de puntos
            x_vals = np.linspace(x_min, x_max, points)
            y_vals = np.linspace(y_min, y_max, points)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Convertir a función NumPy
            func = sp.lambdify((x, y), expr, 'numpy')
            
            # Calcular valores z
            Z = func(X, Y)
            
            # Crear gráfico 3D interactivo de superficie
            surface_data = go.Surface(z=Z, x=X, y=Y)
            if colorscale: surface_data.colorscale = colorscale
            if opacity: surface_data.opacity = opacity

            fig = go.Figure(data=[surface_data])
            fig.update_layout(
                title=f'Superficie 3D Interactiva: {expression}',
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='f(x,y)'
                )
            )
            
            # Guardar el gráfico como HTML
            os.makedirs('static/graphs', exist_ok=True)
            html_filename = f'3d_surface_interactive_{hash(expression)}_{x_min}_{x_max}_{y_min}_{y_max}.html'
            html_path = f'static/graphs/{html_filename}'
            fig.write_html(html_path, auto_open=False)
            
            return {
                "expression": expression,
                "html_path": html_path,
                "x_range": [x_min, x_max],
                "y_range": [y_min, y_max],
                "points_count": points
            }
            
        except BiologyError as e:
            raise ValueError(f"Error generando superficie 3D interactiva: {str(e)}")

    @staticmethod
    def generate_3d_parametric(x_expr: str, y_expr: str, z_expr: str,
                              t_min: float = 0, t_max: float = 6.28, points: int = 1000) -> dict:
        """
        Genera un gráfico 3D paramétrico
        
        Args:
            x_expr: Expresión paramétrica para x
            y_expr: Expresión paramétrica para y
            z_expr: Expresión paramétrica para z
            t_min, t_max: Rango del parámetro t
            points: Número de puntos
            
        Returns:
            Diccionario con información del gráfico 3D paramétrico
        """
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            
            # Crear símbolo para el parámetro
            t = sp.Symbol('t')
            
            # Parsear expresiones
            x_func = sp.sympify(x_expr)
            y_func = sp.sympify(y_expr)
            z_func = sp.sympify(z_expr)
            
            # Generar valores del parámetro
            t_vals = np.linspace(t_min, t_max, points)
            
            # Convertir a funciones NumPy
            x_numpy = sp.lambdify(t, x_func, 'numpy')
            y_numpy = sp.lambdify(t, y_func, 'numpy')
            z_numpy = sp.lambdify(t, z_func, 'numpy')
            
            # Calcular valores
            x_vals = x_numpy(t_vals)
            y_vals = y_numpy(t_vals)
            z_vals = z_numpy(t_vals)
            
            # Crear gráfico 3D
            fig = plt.figure(figsize=(12, 9))
            ax = fig.add_subplot(111, projection='3d')
            
            # Curva paramétrica 3D
            ax.plot(x_vals, y_vals, z_vals, 'b-', linewidth=2)
            
            # Configurar ejes
            ax.set_xlabel('x', fontsize=12)
            ax.set_ylabel('y', fontsize=12)
            ax.set_zlabel('z', fontsize=12)
            ax.set_title(f'Curva 3D Paramétrica\nx = {x_expr}, y = {y_expr}, z = {z_expr}', fontsize=12)
            
            # Guardar gráfico
            os.makedirs('static/graphs', exist_ok=True)
            image_filename = f'3d_parametric_{hash(x_expr + y_expr + z_expr)}_{t_min}_{t_max}.png'
            image_path = f'static/graphs/{image_filename}'
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "x_expression": x_expr,
                "y_expression": y_expr,
                "z_expression": z_expr,
                "image_path": image_path,
                "t_range": [t_min, t_max],
                "points_count": points
            }
            
        except BiologyError as e:
            raise ValueError(f"Error generando curva 3D paramétrica: {str(e)}")

    @staticmethod
    def generate_2d_parametric(x_expr: str, y_expr: str,
                              t_min: float = 0, t_max: float = 6.28, points: int = 1000) -> dict:
        """
        Genera un gráfico 2D paramétrico
        
        Args:
            x_expr: Expresión paramétrica para x
            y_expr: Expresión paramétrica para y
            t_min, t_max: Rango del parámetro t
            points: Número de puntos
            
        Returns:
            Diccionario con información del gráfico 2D paramétrico
        """
        try:
            # Crear símbolo para el parámetro
            t = sp.Symbol('t')
            
            # Parsear expresiones
            x_func = sp.sympify(x_expr)
            y_func = sp.sympify(y_expr)
            
            # Generar valores del parámetro
            t_vals = np.linspace(t_min, t_max, points)
            
            # Convertir a funciones NumPy
            x_numpy = sp.lambdify(t, x_func, 'numpy')
            y_numpy = sp.lambdify(t, y_func, 'numpy')
            
            # Calcular valores
            x_vals = x_numpy(t_vals)
            y_vals = y_numpy(t_vals)
            
            # Crear gráfico 2D
            plt.figure(figsize=(10, 8))
            plt.plot(x_vals, y_vals, 'b-', linewidth=2)
            
            # Configurar ejes
            plt.xlabel('x', fontsize=12)
            plt.ylabel('y', fontsize=12)
            plt.title(f'Curva 2D Paramétrica\nx = {x_expr}, y = {y_expr}', fontsize=12)
            plt.grid(True, alpha=0.3)
            
            # Ejes
            plt.axhline(y=0, color='k', linewidth=0.5)
            plt.axvline(x=0, color='k', linewidth=0.5)
            
            # Guardar gráfico
            os.makedirs('static/graphs', exist_ok=True)
            image_filename = f'2d_parametric_{hash(x_expr + y_expr)}_{t_min}_{t_max}.png'
            image_path = f'static/graphs/{image_filename}'
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "x_expression": x_expr,
                "y_expression": y_expr,
                "image_path": image_path,
                "t_range": [t_min, t_max],
                "points_count": points
            }
            
        except BiologyError as e:
            raise ValueError(f"Error generando curva 2D paramétrica: {str(e)}")

    @staticmethod
    def generate_polar_graph(expression: str, theta_min: float = 0, 
                             theta_max: float = 6.28, points: int = 1000) -> dict:
        """
        Genera un gráfico polar
        
        Args:
            expression: Expresión en coordenadas polares (e.g., "1 + cos(theta)")
            theta_min, theta_max: Rango de theta
            points: Número de puntos
            
        Returns:
            Diccionario con información del gráfico polar
        """
        try:
            # Crear símbolo para theta
            theta = sp.Symbol('theta')
            
            # Parsear expresión
            expr = sp.sympify(expression)
            
            # Generar valores de theta
            theta_vals = np.linspace(theta_min, theta_max, points)
            
            # Convertir a función NumPy
            r_func = sp.lambdify(theta, expr, 'numpy')
            
            # Calcular valores de r
            r_vals = r_func(theta_vals)
            
            # Crear gráfico polar
            plt.figure(figsize=(10, 10))
            ax = plt.subplot(111, polar=True)
            ax.plot(theta_vals, r_vals, 'b-', linewidth=2)
            
            # Configurar gráfico
            ax.set_title(f'Gráfico Polar: {expression}', fontsize=14)
            ax.grid(True, alpha=0.4)
            
            # Guardar gráfico
            os.makedirs('static/graphs', exist_ok=True)
            image_filename = f'polar_graph_{hash(expression)}_{theta_min}_{theta_max}.png'
            image_path = f'static/graphs/{image_filename}'
            plt.savefig(image_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            return {
                "expression": expression,
                "image_path": image_path,
                "theta_range": [theta_min, theta_max],
                "points_count": points
            }
            
        except BiologyError as e:
            raise ValueError(f"Error generando gráfico polar: {str(e)}")

    @staticmethod
    def generate_multi_surface_3d(surfaces_data: List[Dict], title: str = "Múltiples Superficies 3D") -> Dict:
        """
        Genera un gráfico 3D interactivo con múltiples superficies usando Plotly
        
        Args:
            surfaces_data: Lista de diccionarios, cada uno con datos para una superficie
            title: Título del gráfico
            
        Returns:
            Diccionario con información del gráfico 3D interactivo
        """
        try:
            import plotly.graph_objects as go
            
            fig = go.Figure()
            
            for surface_info in surfaces_data:
                expression = surface_info["expression"]
                x_min = surface_info.get("x_min", -5)
                x_max = surface_info.get("x_max", 5)
                y_min = surface_info.get("y_min", -5)
                y_max = surface_info.get("y_max", 5)
                colorscale = surface_info.get("colorscale")
                opacity = surface_info.get("opacity")
                
                x, y = sp.symbols('x y')
                expr = sp.sympify(expression)
                
                x_vals = np.linspace(x_min, x_max, 50)
                y_vals = np.linspace(y_min, y_max, 50)
                X, Y = np.meshgrid(x_vals, y_vals)
                
                func = sp.lambdify((x, y), expr, 'numpy')
                Z = func(X, Y)
                
                surface = go.Surface(z=Z, x=X, y=Y, name=expression) # Añadir nombre para la leyenda
                if colorscale: surface.colorscale = colorscale
                if opacity: surface.opacity = opacity
                
                fig.add_trace(surface)
            
            fig.update_layout(
                title=title,
                scene=dict(
                    xaxis_title='X',
                    yaxis_title='Y',
                    zaxis_title='Z'
                )
            )
            
            os.makedirs('static/graphs', exist_ok=True)
            html_filename = f'multi_surface_3d_interactive_{hash(str(surfaces_data))}.html'
            html_path = f'static/graphs/{html_filename}'
            fig.write_html(html_path, auto_open=False)
            
            return {
                "html_path": html_path,
                "title": title,
                "surfaces_count": len(surfaces_data)
            }
            
        except BiologyError as e:
            raise ValueError(f"Error generando múltiples superficies 3D interactivas: {str(e)}")

    @staticmethod
    def get_graph_examples() -> List[dict]:
        """
        Devuelve ejemplos de gráficos
        
        Returns:
            Lista de ejemplos
        """
        return [
            {
                "expression": "x**2",
                "description": "Parábola simple",
                "type": "2D"
            },
            {
                "expression": "sin(x)",
                "description": "Función seno",
                "type": "2D"
            },
            {
                "expression": "cos(x)",
                "description": "Función coseno",
                "type": "2D"
            },
            {
                "expression": "x**3 - 3*x",
                "description": "Función cúbica",
                "type": "2D"
            },
            {
                "expression": "exp(x)",
                "description": "Función exponencial",
                "type": "2D"
            },
            {
                "expression": "log(x)",
                "description": "Función logarítmica",
                "type": "2D"
            },
            {
                "expression": "x**2 + y**2",
                "description": "Paraboloide",
                "type": "3D"
            },
            {
                "expression": "1 + cos(theta)",
                "description": "Cardioide",
                "type": "Polar"
            }
        ]
