"""
Servicio de Visualización VR/AR para Matemáticas
Proporciona experiencias inmersivas de visualización matemática usando WebXR y A-Frame
"""

import numpy as np
import json
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
from dataclasses import dataclass
from enum import Enum
import asyncio
import time
from app.services.base_service import BaseService
from app.exceptions.domain.mathematics import MathematicsError

# Dependencias opcionales para VR/AR
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.offline import plot
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    import three
    THREEJS_AVAILABLE = True
except ImportError:
    THREEJS_AVAILABLE = False


class VRPlatform(Enum):
    """Plataformas VR/AR soportadas"""
    WEBXR = "webxr"
    AFRAME = "aframe"
    THREEJS = "threejs"
    BABYLONJS = "babylonjs"
    UNITY_WEBGL = "unity_webgl"


class VisualizationType(Enum):
    """Tipos de visualización VR/AR"""
    GEOMETRIC_3D = "geometric_3d"
    FUNCTION_SURFACE = "function_surface"
    VECTOR_FIELD = "vector_field"
    FRACTAL_3D = "fractal_3d"
    MOLECULAR_STRUCTURE = "molecular_structure"
    GRAPH_NETWORK = "graph_network"
    STATISTICAL_CLOUD = "statistical_cloud"
    QUANTUM_STATE = "quantum_state"


@dataclass
class VRScene:
    """Configuración de escena VR"""
    scene_id: str
    title: str
    description: str
    platform: VRPlatform
    visualization_type: VisualizationType
    objects: List[Dict[str, Any]]
    lighting: Dict[str, Any]
    camera: Dict[str, Any]
    interactions: List[Dict[str, Any]]
    physics: Optional[Dict[str, Any]] = None
    audio: Optional[Dict[str, Any]] = None


@dataclass
class VRObject:
    """Objeto 3D para VR"""
    object_id: str
    geometry_type: str
    position: Tuple[float, float, float]
    rotation: Tuple[float, float, float]
    scale: Tuple[float, float, float]
    material: Dict[str, Any]
    animation: Optional[Dict[str, Any]] = None
    physics: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class VRARVisualizationService(BaseService):
    """
    Servicio de Visualización VR/AR para Matemáticas
    
    Proporciona:
    - Visualización inmersiva de funciones matemáticas
    - Experiencias VR/AR interactivas
    - Renderizado 3D/4D avanzado
    - Simulaciones matemáticas inmersivas
    - Colaboración en espacios virtuales
    - Gamificación de conceptos matemáticos
    """
    
    def __init__(self):
        super().__init__("VRARVisualizationService")
        self.logger = logging.getLogger(__name__)
        self.scenes = {}
        self.active_sessions = {}
        self.supported_platforms = [platform.value for platform in VRPlatform]
        
        # Configuración por defecto
        self.default_camera = {
            "position": [0, 1.6, 3],
            "rotation": [0, 0, 0],
            "fov": 80
        }
        
        self.default_lighting = {
            "ambient": {"color": "#404040", "intensity": 0.4},
            "directional": {"color": "#ffffff", "intensity": 0.8, "position": [1, 1, 1]}
        }

    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa solicitudes de visualización VR/AR
        """
        action = request_data.get("action")
        
        if action == "create_function_surface":
            # This method is synchronous, so we can call it directly
            # But we need to handle parameters
            scene = self.create_function_surface_vr(
                function=request_data.get("function"),
                x_range=tuple(request_data.get("x_range", [-5, 5])),
                y_range=tuple(request_data.get("y_range", [-5, 5])),
                resolution=request_data.get("resolution", 50)
            )
            return {"success": True, "scene": scene.__dict__}
            
        return {"success": False, "error": f"Unknown action: {action}"}
    
    # === CREACIÓN DE ESCENAS VR ===
    
    def create_function_surface_vr(self, 
                                  function: str,
                                  x_range: Tuple[float, float] = (-5, 5),
                                  y_range: Tuple[float, float] = (-5, 5),
                                  resolution: int = 50,
                                  platform: VRPlatform = VRPlatform.AFRAME) -> VRScene:
        """
        Crear visualización VR de superficie de función
        
        Args:
            function: Función matemática (ej: "x**2 + y**2")
            x_range: Rango en X
            y_range: Rango en Y
            resolution: Resolución de la malla
            platform: Plataforma VR
        
        Returns:
            Escena VR configurada
        """
        try:
            # Generar datos de la superficie
            x = np.linspace(x_range[0], x_range[1], resolution)
            y = np.linspace(y_range[0], y_range[1], resolution)
            X, Y = np.meshgrid(x, y)
            
            # Evaluar función
            Z = self._evaluate_function(function, X, Y)
            
            # Crear geometría de superficie
            vertices, faces = self._create_surface_geometry(X, Y, Z)
            
            # Configurar objeto VR
            surface_object = VRObject(
                object_id="function_surface",
                geometry_type="mesh",
                position=(0, 0, 0),
                rotation=(0, 0, 0),
                scale=(1, 1, 1),
                material={
                    "type": "gradient",
                    "colors": ["#0066cc", "#00cc66", "#cc6600"],
                    "wireframe": False,
                    "opacity": 0.8
                },
                metadata={
                    "function": function,
                    "vertices": vertices.tolist(),
                    "faces": faces.tolist()
                }
            )
            
            # Crear escena
            scene = VRScene(
                scene_id=f"function_surface_{int(time.time())}",
                title=f"Superficie: {function}",
                description=f"Visualización VR de la función {function}",
                platform=platform,
                visualization_type=VisualizationType.FUNCTION_SURFACE,
                objects=[surface_object.__dict__],
                lighting=self.default_lighting,
                camera=self.default_camera,
                interactions=[
                    {
                        "type": "grab",
                        "target": "function_surface",
                        "action": "rotate"
                    },
                    {
                        "type": "pinch",
                        "target": "function_surface",
                        "action": "scale"
                    }
                ]
            )
            
            self.scenes[scene.scene_id] = scene
            return scene
            
        except MathematicsError as e:
            self.logger.error(f"Error creando superficie VR: {e}")
            raise
    
    def create_vector_field_vr(self,
                              vector_function: Tuple[str, str, str],
                              bounds: Tuple[Tuple[float, float], Tuple[float, float], Tuple[float, float]],
                              density: int = 10,
                              platform: VRPlatform = VRPlatform.AFRAME) -> VRScene:
        """
        Crear visualización VR de campo vectorial 3D
        
        Args:
            vector_function: Tupla de funciones (Fx, Fy, Fz)
            bounds: Límites ((x_min, x_max), (y_min, y_max), (z_min, z_max))
            density: Densidad de vectores
            platform: Plataforma VR
        
        Returns:
            Escena VR del campo vectorial
        """
        try:
            # Generar puntos de muestreo
            x = np.linspace(bounds[0][0], bounds[0][1], density)
            y = np.linspace(bounds[1][0], bounds[1][1], density)
            z = np.linspace(bounds[2][0], bounds[2][1], density)
            X, Y, Z = np.meshgrid(x, y, z)
            
            # Evaluar campo vectorial
            Fx = self._evaluate_function(vector_function[0], X, Y, Z)
            Fy = self._evaluate_function(vector_function[1], X, Y, Z)
            Fz = self._evaluate_function(vector_function[2], X, Y, Z)
            
            # Crear objetos de vectores
            vector_objects = []
            for i in range(density):
                for j in range(density):
                    for k in range(density):
                        if i % 2 == 0 and j % 2 == 0 and k % 2 == 0:  # Reducir densidad
                            pos = (X[i,j,k], Y[i,j,k], Z[i,j,k])
                            direction = (Fx[i,j,k], Fy[i,j,k], Fz[i,j,k])
                            magnitude = np.linalg.norm(direction)
                            
                            if magnitude > 0.1:  # Solo vectores significativos
                                vector_obj = VRObject(
                                    object_id=f"vector_{i}_{j}_{k}",
                                    geometry_type="arrow",
                                    position=pos,
                                    rotation=self._vector_to_rotation(direction),
                                    scale=(0.1, 0.1, magnitude * 0.5),
                                    material={
                                        "type": "color",
                                        "color": self._magnitude_to_color(magnitude),
                                        "opacity": 0.7
                                    },
                                    metadata={
                                        "vector": direction,
                                        "magnitude": magnitude
                                    }
                                )
                                vector_objects.append(vector_obj.__dict__)
            
            # Crear escena
            scene = VRScene(
                scene_id=f"vector_field_{int(time.time())}",
                title="Campo Vectorial 3D",
                description=f"Visualización VR del campo vectorial {vector_function}",
                platform=platform,
                visualization_type=VisualizationType.VECTOR_FIELD,
                objects=vector_objects,
                lighting=self.default_lighting,
                camera=self.default_camera,
                interactions=[
                    {
                        "type": "teleport",
                        "target": "scene",
                        "action": "navigate"
                    }
                ]
            )
            
            self.scenes[scene.scene_id] = scene
            return scene
            
        except MathematicsError as e:
            self.logger.error(f"Error creando campo vectorial VR: {e}")
            raise
    
    def create_fractal_vr(self,
                         fractal_type: str = "mandelbrot",
                         iterations: int = 100,
                         zoom: float = 1.0,
                         center: Tuple[float, float] = (0, 0),
                         platform: VRPlatform = VRPlatform.AFRAME) -> VRScene:
        """
        Crear visualización VR de fractales 3D
        
        Args:
            fractal_type: Tipo de fractal
            iterations: Número de iteraciones
            zoom: Factor de zoom
            center: Centro del fractal
            platform: Plataforma VR
        
        Returns:
            Escena VR del fractal
        """
        try:
            if fractal_type == "mandelbrot":
                fractal_data = self._generate_mandelbrot_3d(iterations, zoom, center)
            elif fractal_type == "julia":
                fractal_data = self._generate_julia_3d(iterations, zoom, center)
            elif fractal_type == "sierpinski":
                fractal_data = self._generate_sierpinski_3d(iterations)
            else:
                raise ValueError(f"Tipo de fractal no soportado: {fractal_type}")
            
            # Crear objetos del fractal
            fractal_objects = []
            for i, point in enumerate(fractal_data["points"]):
                if i % 10 == 0:  # Reducir densidad para VR
                    fractal_obj = VRObject(
                        object_id=f"fractal_point_{i}",
                        geometry_type="sphere",
                        position=point,
                        rotation=(0, 0, 0),
                        scale=(0.02, 0.02, 0.02),
                        material={
                            "type": "color",
                            "color": fractal_data["colors"][i],
                            "emissive": True,
                            "opacity": 0.8
                        }
                    )
                    fractal_objects.append(fractal_obj.__dict__)
            
            # Crear escena
            scene = VRScene(
                scene_id=f"fractal_{fractal_type}_{int(time.time())}",
                title=f"Fractal {fractal_type.title()} 3D",
                description=f"Visualización VR del fractal {fractal_type}",
                platform=platform,
                visualization_type=VisualizationType.FRACTAL_3D,
                objects=fractal_objects,
                lighting={
                    "ambient": {"color": "#202020", "intensity": 0.2},
                    "point": {"color": "#ffffff", "intensity": 1.0, "position": [0, 5, 0]}
                },
                camera=self.default_camera,
                interactions=[
                    {
                        "type": "fly",
                        "target": "scene",
                        "action": "navigate"
                    }
                ]
            )
            
            self.scenes[scene.scene_id] = scene
            return scene
            
        except MathematicsError as e:
            self.logger.error(f"Error creando fractal VR: {e}")
            raise
    
    def create_quantum_state_vr(self,
                               state_vector: np.ndarray,
                               basis_labels: Optional[List[str]] = None,
                               platform: VRPlatform = VRPlatform.AFRAME) -> VRScene:
        """
        Crear visualización VR de estados cuánticos
        
        Args:
            state_vector: Vector de estado cuántico
            basis_labels: Etiquetas de la base
            platform: Plataforma VR
        
        Returns:
            Escena VR del estado cuántico
        """
        try:
            n_qubits = int(np.log2(len(state_vector)))
            
            if basis_labels is None:
                basis_labels = [format(i, f'0{n_qubits}b') for i in range(len(state_vector))]
            
            # Crear esfera de Bloch para cada qubit
            bloch_objects = []
            
            for i in range(n_qubits):
                # Calcular estado reducido del qubit i
                reduced_state = self._trace_out_other_qubits(state_vector, i, n_qubits)
                
                # Convertir a coordenadas de Bloch
                bloch_coords = self._state_to_bloch_coords(reduced_state)
                
                # Crear esfera de Bloch
                sphere_obj = VRObject(
                    object_id=f"bloch_sphere_{i}",
                    geometry_type="sphere",
                    position=(i * 3, 0, 0),
                    rotation=(0, 0, 0),
                    scale=(1, 1, 1),
                    material={
                        "type": "wireframe",
                        "color": "#4080ff",
                        "opacity": 0.3
                    }
                )
                
                # Vector de estado en la esfera
                vector_obj = VRObject(
                    object_id=f"state_vector_{i}",
                    geometry_type="arrow",
                    position=(i * 3, 0, 0),
                    rotation=self._bloch_to_rotation(bloch_coords),
                    scale=(0.05, 0.05, 1),
                    material={
                        "type": "color",
                        "color": "#ff4040",
                        "emissive": True
                    },
                    animation={
                        "type": "rotation",
                        "axis": "y",
                        "speed": 0.5
                    }
                )
                
                bloch_objects.extend([sphere_obj.__dict__, vector_obj.__dict__])
            
            # Crear escena
            scene = VRScene(
                scene_id=f"quantum_state_{int(time.time())}",
                title="Estado Cuántico",
                description=f"Visualización VR de estado cuántico de {n_qubits} qubits",
                platform=platform,
                visualization_type=VisualizationType.QUANTUM_STATE,
                objects=bloch_objects,
                lighting=self.default_lighting,
                camera=self.default_camera,
                interactions=[
                    {
                        "type": "grab",
                        "target": "state_vector_*",
                        "action": "manipulate_state"
                    }
                ]
            )
            
            self.scenes[scene.scene_id] = scene
            return scene
            
        except MathematicsError as e:
            self.logger.error(f"Error creando estado cuántico VR: {e}")
            raise
    
    # === GENERACIÓN DE CÓDIGO VR/AR ===
    
    def generate_aframe_html(self, scene: VRScene) -> str:
        """
        Generar código HTML A-Frame para la escena
        
        Args:
            scene: Escena VR
        
        Returns:
            Código HTML A-Frame
        """
        try:
            html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="description" content="{description}">
    <script src="https://aframe.io/releases/1.4.0/aframe.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/donmccurdy/aframe-extras@v6.1.1/dist/aframe-extras.min.js"></script>
</head>
<body>
    <a-scene vr-mode-ui="enabled: true" embedded style="height: 600px; width: 100%;">
        <!-- Assets -->
        <a-assets>
            {assets}
        </a-assets>
        
        <!-- Lighting -->
        {lighting}
        
        <!-- Camera -->
        <a-entity id="cameraRig" position="{camera_position}">
            <a-camera look-controls wasd-controls></a-camera>
            <a-entity laser-controls="hand: right" raycaster="objects: .interactive"></a-entity>
        </a-entity>
        
        <!-- Objects -->
        {objects}
        
        <!-- Environment -->
        <a-sky color="#001122"></a-sky>
        <a-plane position="0 -2 0" rotation="-90 0 0" width="20" height="20" color="#333" opacity="0.5"></a-plane>
    </a-scene>
</body>
</html>
            """
            
            # Generar lighting
            lighting_html = ""
            if "ambient" in scene.lighting:
                ambient = scene.lighting["ambient"]
                lighting_html += f'<a-light type="ambient" color="{ambient["color"]}" intensity="{ambient["intensity"]}"></a-light>\n'
            
            if "directional" in scene.lighting:
                directional = scene.lighting["directional"]
                pos = directional["position"]
                lighting_html += f'<a-light type="directional" color="{directional["color"]}" intensity="{directional["intensity"]}" position="{pos[0]} {pos[1]} {pos[2]}"></a-light>\n'
            
            # Generar objetos
            objects_html = ""
            for obj in scene.objects:
                objects_html += self._generate_aframe_object(obj) + "\n"
            
            # Formatear HTML
            camera_pos = " ".join(map(str, scene.camera["position"]))
            
            html = html_template.format(
                title=scene.title,
                description=scene.description,
                assets="",
                lighting=lighting_html,
                camera_position=camera_pos,
                objects=objects_html
            )
            
            return html
            
        except MathematicsError as e:
            self.logger.error(f"Error generando HTML A-Frame: {e}")
            raise
    
    def generate_webxr_code(self, scene: VRScene) -> Dict[str, str]:
        """
        Generar código WebXR para la escena
        
        Args:
            scene: Escena VR
        
        Returns:
            Diccionario con HTML, CSS y JavaScript
        """
        try:
            html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>{css}</style>
</head>
<body>
    <canvas id="webxr-canvas"></canvas>
    <div id="ui-overlay">
        <button id="vr-button">Enter VR</button>
        <div id="info">{description}</div>
    </div>
    <script>{javascript}</script>
</body>
</html>
            """.format(
                title=scene.title,
                description=scene.description,
                css=self._generate_webxr_css(),
                javascript=self._generate_webxr_js(scene)
            )
            
            return {
                "html": html,
                "css": self._generate_webxr_css(),
                "javascript": self._generate_webxr_js(scene)
            }
            
        except MathematicsError as e:
            self.logger.error(f"Error generando código WebXR: {e}")
            raise
    
    # === MÉTODOS AUXILIARES ===
    
    def _evaluate_function(self, function: str, *args) -> np.ndarray:
        """Evaluar función matemática de forma segura"""
        try:
            # Crear namespace seguro
            namespace = {
                'x': args[0] if len(args) > 0 else 0,
                'y': args[1] if len(args) > 1 else 0,
                'z': args[2] if len(args) > 2 else 0,
                'np': np,
                'sin': np.sin,
                'cos': np.cos,
                'tan': np.tan,
                'exp': np.exp,
                'log': np.log,
                'sqrt': np.sqrt,
                'pi': np.pi,
                'e': np.e
            }
            
            return eval(function, {"__builtins__": {}}, namespace)
            
        except MathematicsError as e:
            self.logger.error(f"Error evaluando función {function}: {e}")
            return np.zeros_like(args[0])
    
    def _create_surface_geometry(self, X: np.ndarray, Y: np.ndarray, Z: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Crear geometría de superficie a partir de datos de malla"""
        vertices = []
        faces = []
        
        rows, cols = X.shape
        
        # Crear vértices
        for i in range(rows):
            for j in range(cols):
                vertices.append([X[i,j], Z[i,j], Y[i,j]])  # Intercambiar Y y Z para VR
        
        # Crear caras (triángulos)
        for i in range(rows - 1):
            for j in range(cols - 1):
                # Índices de vértices
                v1 = i * cols + j
                v2 = i * cols + (j + 1)
                v3 = (i + 1) * cols + j
                v4 = (i + 1) * cols + (j + 1)
                
                # Dos triángulos por cuadrado
                faces.append([v1, v2, v3])
                faces.append([v2, v4, v3])
        
        return np.array(vertices), np.array(faces)
    
    def _vector_to_rotation(self, vector: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Convertir vector a rotación Euler"""
        x, y, z = vector
        
        # Calcular ángulos de Euler
        yaw = np.arctan2(y, x)
        pitch = np.arctan2(z, np.sqrt(x*x + y*y))
        roll = 0  # Asumimos roll = 0
        
        return (np.degrees(pitch), np.degrees(yaw), np.degrees(roll))
    
    def _magnitude_to_color(self, magnitude: float) -> str:
        """Convertir magnitud a color"""
        # Normalizar magnitud a [0, 1]
        normalized = min(magnitude / 2.0, 1.0)
        
        # Interpolación de color (azul -> verde -> rojo)
        if normalized < 0.5:
            r = int(255 * normalized * 2)
            g = 255
            b = int(255 * (1 - normalized * 2))
        else:
            r = 255
            g = int(255 * (2 - normalized * 2))
            b = 0
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _generate_mandelbrot_3d(self, iterations: int, zoom: float, center: Tuple[float, float]) -> Dict[str, Any]:
        """Generar fractal de Mandelbrot 3D"""
        points = []
        colors = []
        
        size = 100
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    # Mapear a coordenadas complejas
                    x = (i - size/2) / (size/4) / zoom + center[0]
                    y = (j - size/2) / (size/4) / zoom + center[1]
                    z = (k - size/2) / (size/4) / zoom
                    
                    c = complex(x, y)
                    z_val = complex(0, z)
                    
                    # Iteración de Mandelbrot
                    for n in range(iterations):
                        if abs(z_val) > 2:
                            break
                        z_val = z_val*z_val + c
                    
                    if n < iterations - 1:
                        points.append([x, z, y])
                        color_intensity = n / iterations
                        colors.append(self._magnitude_to_color(color_intensity * 2))
        
        return {"points": points, "colors": colors}
    
    def _generate_julia_3d(self, iterations: int, zoom: float, center: Tuple[float, float]) -> Dict[str, Any]:
        """Generar fractal de Julia 3D"""
        # Implementación similar a Mandelbrot pero con c fijo
        c = complex(-0.7, 0.27015)
        points = []
        colors = []
        
        size = 80
        for i in range(size):
            for j in range(size):
                for k in range(size):
                    x = (i - size/2) / (size/4) / zoom + center[0]
                    y = (j - size/2) / (size/4) / zoom + center[1]
                    z = (k - size/2) / (size/4) / zoom
                    
                    z_val = complex(x, y) + z * 1j
                    
                    for n in range(iterations):
                        if abs(z_val) > 2:
                            break
                        z_val = z_val*z_val + c
                    
                    if n < iterations - 1:
                        points.append([x, z, y])
                        color_intensity = n / iterations
                        colors.append(self._magnitude_to_color(color_intensity * 2))
        
        return {"points": points, "colors": colors}
    
    def _generate_sierpinski_3d(self, iterations: int) -> Dict[str, Any]:
        """Generar triángulo de Sierpinski 3D"""
        points = []
        colors = []
        
        # Vértices del tetraedro
        vertices = [
            [0, 0, 0],
            [1, 0, 0],
            [0.5, np.sqrt(3)/2, 0],
            [0.5, np.sqrt(3)/6, np.sqrt(6)/3]
        ]
        
        # Punto inicial
        point = [0.5, 0.25, 0.25]
        
        for i in range(iterations * 1000):
            # Elegir vértice aleatorio
            vertex = vertices[np.random.randint(4)]
            
            # Mover hacia el vértice (punto medio)
            point = [(point[j] + vertex[j]) / 2 for j in range(3)]
            
            if i > 100:  # Saltar primeras iteraciones
                points.append(point.copy())
                colors.append("#ff6600")
        
        return {"points": points, "colors": colors}
    
    def _trace_out_other_qubits(self, state_vector: np.ndarray, target_qubit: int, n_qubits: int) -> np.ndarray:
        """Trazar otros qubits para obtener estado reducido"""
        # Implementación simplificada
        # En una implementación completa, se calcularía la matriz de densidad reducida
        n = len(state_vector)
        reduced_dim = 2
        
        # Crear estado reducido aproximado
        reduced_state = np.zeros(reduced_dim, dtype=complex)
        
        for i in range(n):
            bit_string = format(i, f'0{n_qubits}b')
            target_bit = int(bit_string[target_qubit])
            reduced_state[target_bit] += state_vector[i]
        
        # Normalizar
        norm = np.linalg.norm(reduced_state)
        if norm > 0:
            reduced_state /= norm
        
        return reduced_state
    
    def _state_to_bloch_coords(self, state: np.ndarray) -> Tuple[float, float, float]:
        """Convertir estado cuántico a coordenadas de Bloch"""
        if len(state) != 2:
            return (0, 0, 1)  # Estado por defecto
        
        alpha, beta = state[0], state[1]
        
        # Coordenadas de Bloch
        x = 2 * np.real(np.conj(alpha) * beta)
        y = 2 * np.imag(np.conj(alpha) * beta)
        z = np.abs(alpha)**2 - np.abs(beta)**2
        
        return (float(x), float(y), float(z))
    
    def _bloch_to_rotation(self, coords: Tuple[float, float, float]) -> Tuple[float, float, float]:
        """Convertir coordenadas de Bloch a rotación"""
        x, y, z = coords
        
        # Convertir a ángulos esféricos
        theta = np.arccos(z)  # Ángulo polar
        phi = np.arctan2(y, x)  # Ángulo azimutal
        
        return (np.degrees(theta), np.degrees(phi), 0)
    
    def _generate_aframe_object(self, obj: Dict[str, Any]) -> str:
        """Generar elemento A-Frame para un objeto"""
        geometry_type = obj["geometry_type"]
        position = " ".join(map(str, obj["position"]))
        rotation = " ".join(map(str, obj["rotation"]))
        scale = " ".join(map(str, obj["scale"]))
        
        if geometry_type == "sphere":
            return f'<a-sphere position="{position}" rotation="{rotation}" scale="{scale}" color="{obj["material"].get("color", "#ff0000")}" class="interactive"></a-sphere>'
        elif geometry_type == "arrow":
            return f'<a-cone position="{position}" rotation="{rotation}" scale="{scale}" color="{obj["material"].get("color", "#00ff00")}" class="interactive"></a-cone>'
        elif geometry_type == "mesh":
            return f'<a-box position="{position}" rotation="{rotation}" scale="{scale}" color="{obj["material"].get("color", "#0000ff")}" class="interactive"></a-box>'
        else:
            return f'<a-box position="{position}" rotation="{rotation}" scale="{scale}" color="#cccccc" class="interactive"></a-box>'
    
    def _generate_webxr_css(self) -> str:
        """Generar CSS para WebXR"""
        return """
body {
    margin: 0;
    padding: 0;
    background: #000;
    font-family: Arial, sans-serif;
}

#webxr-canvas {
    width: 100vw;
    height: 100vh;
    display: block;
}

#ui-overlay {
    position: absolute;
    top: 20px;
    left: 20px;
    z-index: 100;
}

#vr-button {
    padding: 10px 20px;
    background: #007acc;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
}

#vr-button:hover {
    background: #005a99;
}

#info {
    color: white;
    margin-top: 10px;
    max-width: 300px;
}
        """
    
    def _generate_webxr_js(self, scene: VRScene) -> str:
        """Generar JavaScript para WebXR"""
        return f"""
// WebXR Scene: {scene.title}
const canvas = document.getElementById('webxr-canvas');
const vrButton = document.getElementById('vr-button');

// Configuración básica de Three.js
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({{ canvas: canvas, antialias: true }});

renderer.setSize(window.innerWidth, window.innerHeight);
renderer.xr.enabled = true;

// Configurar cámara
camera.position.set({scene.camera["position"][0]}, {scene.camera["position"][1]}, {scene.camera["position"][2]});

// Agregar objetos de la escena
{self._generate_threejs_objects(scene.objects)}

// Configurar iluminación
const ambientLight = new THREE.AmbientLight(0x404040, 0.4);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
directionalLight.position.set(1, 1, 1);
scene.add(directionalLight);

// Configurar WebXR
vrButton.addEventListener('click', function() {{
    if (navigator.xr) {{
        navigator.xr.requestSession('immersive-vr').then(function(session) {{
            renderer.xr.setSession(session);
        }});
    }} else {{
        alert('WebXR no está soportado en este navegador');
    }}
}});

// Loop de renderizado
function animate() {{
    renderer.setAnimationLoop(render);
}}

function render() {{
    renderer.render(scene, camera);
}}

// Manejar redimensionamiento
window.addEventListener('resize', function() {{
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}});

// Iniciar
animate();
        """
    
    def _generate_threejs_objects(self, objects: List[Dict[str, Any]]) -> str:
        """Generar código Three.js para objetos"""
        js_code = ""
        
        for obj in objects:
            geometry_type = obj["geometry_type"]
            position = obj["position"]
            scale = obj["scale"]
            color = obj["material"].get("color", "#ffffff")
            
            if geometry_type == "sphere":
                js_code += f"""
const geometry_{obj["object_id"]} = new THREE.SphereGeometry(0.5, 32, 32);
const material_{obj["object_id"]} = new THREE.MeshLambertMaterial({{ color: '{color}' }});
const mesh_{obj["object_id"]} = new THREE.Mesh(geometry_{obj["object_id"]}, material_{obj["object_id"]});
mesh_{obj["object_id"]}.position.set({position[0]}, {position[1]}, {position[2]});
mesh_{obj["object_id"]}.scale.set({scale[0]}, {scale[1]}, {scale[2]});
scene.add(mesh_{obj["object_id"]});
                """
        
        return js_code
    
    # === GESTIÓN DE SESIONES ===
    
    def start_vr_session(self, scene_id: str, user_id: str) -> Dict[str, Any]:
        """Iniciar sesión VR"""
        try:
            if scene_id not in self.scenes:
                raise ValueError(f"Escena {scene_id} no encontrada")
            
            session_id = f"{user_id}_{scene_id}_{int(time.time())}"
            
            self.active_sessions[session_id] = {
                "scene_id": scene_id,
                "user_id": user_id,
                "start_time": time.time(),
                "status": "active"
            }
            
            return {
                "session_id": session_id,
                "scene": self.scenes[scene_id],
                "status": "started"
            }
            
        except MathematicsError as e:
            self.logger.error(f"Error iniciando sesión VR: {e}")
            raise
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Obtener capacidades del servicio"""
        return {
            "service": "VR/AR Visualization Service",
            "version": "1.0",
            "supported_platforms": self.supported_platforms,
            "visualization_types": [vtype.value for vtype in VisualizationType],
            "features": [
                "immersive_function_visualization",
                "3d_vector_fields",
                "fractal_exploration",
                "quantum_state_visualization",
                "interactive_mathematical_objects",
                "collaborative_vr_spaces",
                "webxr_compatibility",
                "aframe_integration"
            ],
            "active_scenes": len(self.scenes),
            "active_sessions": len(self.active_sessions)
        }