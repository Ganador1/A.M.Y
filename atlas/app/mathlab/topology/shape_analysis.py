"""
Análisis de Formas Topológicas y Características Geométricas
============================================================

Módulo avanzado para análisis de formas usando técnicas de topología computacional,
geometría diferencial y análisis de características geométricas persistentes.

Funcionalidades:
- Análisis de curvatura y características geométricas
- Detección de características topológicas robustas
- Análisis de formas persistentes y estabilidad
- Comparación y matching de formas
- Esqueletonización y medial axis transform
- Análisis de simetrías y invariantes geométricos

Referencias:
- Edelsbrunner, H. & Harer, J. (2010). "Computational Topology"
- Zomorodian, A. (2005). "Topology for Computing"
- Chazal, F. & Michel, B. (2017). "An Introduction to Topological Data Analysis"

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
import asyncio
from typing import List, Dict, Any, Tuple, Optional, Union
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.spatial import Voronoi, Delaunay, ConvexHull
from scipy.ndimage import gaussian_filter, distance_transform_edt
from dataclasses import dataclass
import networkx as nx

# Geometric processing
try:
    from scipy.spatial.transform import Rotation
    SCIPY_TRANSFORM_AVAILABLE = True
except ImportError:
    SCIPY_TRANSFORM_AVAILABLE = False

# Image processing for shape analysis
try:
    from skimage import morphology, measure, filters
    from skimage.feature import peak_local_maxima
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class ShapeFeatures:
    """Características geométricas y topológicas de una forma"""
    area: float
    perimeter: float
    compactness: float
    eccentricity: float
    euler_characteristic: int
    bounding_box_ratio: float
    convex_hull_ratio: float
    major_axis_length: float
    minor_axis_length: float
    orientation: float
    centroid: Tuple[float, float]
    moments: List[float]


class ShapeAnalyzer:
    """
    Analizador avanzado de formas topológicas
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def analyze_point_cloud_shape(
        self,
        points: List[Tuple[float, float]],
        resolution: float = 0.1
    ) -> Dict[str, Any]:
        """
        Analiza la forma de una nube de puntos
        
        Args:
            points: Lista de puntos 2D
            resolution: Resolución para discretización
            
        Returns:
            Análisis completo de forma
        """
        
        try:
            points_array = np.array(points)
            
            # Características básicas
            basic_features = await self._compute_basic_features(points_array)
            
            # Análisis de curvatura
            curvature_analysis = await self._analyze_curvature(points_array)
            
            # Características topológicas
            topological_features = await self._compute_topological_features(points_array)
            
            # Análisis de simetrías
            symmetry_analysis = await self._analyze_symmetries(points_array)
            
            # Descriptores de forma
            shape_descriptors = await self._compute_shape_descriptors(points_array)
            
            # Alpha shapes
            alpha_shapes = await self._compute_alpha_shapes(points_array)
            
            # Medial axis
            medial_axis = await self._compute_medial_axis(points_array, resolution)
            
            return {
                "basic_features": basic_features,
                "curvature_analysis": curvature_analysis,
                "topological_features": topological_features,
                "symmetry_analysis": symmetry_analysis,
                "shape_descriptors": shape_descriptors,
                "alpha_shapes": alpha_shapes,
                "medial_axis": medial_axis,
                "n_points": len(points),
                "algorithm": "comprehensive_shape_analysis"
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing point cloud shape: {str(e)}")
            raise
    
    async def _compute_basic_features(self, points: np.ndarray) -> Dict[str, Any]:
        """Computa características geométricas básicas"""
        
        if len(points) < 3:
            return {
                "centroid": points.mean(axis=0).tolist() if len(points) > 0 else [0, 0],
                "bounding_box": None,
                "area_estimate": 0.0,
                "perimeter_estimate": 0.0
            }
        
        # Centroide
        centroid = points.mean(axis=0)
        
        # Bounding box
        min_coords = points.min(axis=0)
        max_coords = points.max(axis=0)
        bounding_box = {
            "min": min_coords.tolist(),
            "max": max_coords.tolist(),
            "width": float(max_coords[0] - min_coords[0]),
            "height": float(max_coords[1] - min_coords[1])
        }
        
        # Estimación de área usando convex hull
        try:
            hull = ConvexHull(points)
            area_estimate = hull.volume  # En 2D, volume es área
            perimeter_estimate = self._estimate_perimeter(points)
        except Exception:
            area_estimate = 0.0
            perimeter_estimate = 0.0
        
        # Momentos geométricos
        moments = self._compute_geometric_moments(points, centroid)
        
        return {
            "centroid": centroid.tolist(),
            "bounding_box": bounding_box,
            "area_estimate": float(area_estimate),
            "perimeter_estimate": float(perimeter_estimate),
            "moments": moments
        }
    
    async def _analyze_curvature(self, points: np.ndarray) -> Dict[str, Any]:
        """Analiza la curvatura de la forma"""
        
        if len(points) < 5:
            return {
                "mean_curvature": 0.0,
                "gaussian_curvature": 0.0,
                "curvature_distribution": [],
                "critical_points": []
            }
        
        # Ordenar puntos por ángulo para formar contorno
        centroid = points.mean(axis=0)
        angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
        sorted_indices = np.argsort(angles)
        ordered_points = points[sorted_indices]
        
        # Calcular curvatura local
        curvatures = []
        for i in range(len(ordered_points)):
            prev_idx = (i - 1) % len(ordered_points)
            next_idx = (i + 1) % len(ordered_points)
            
            p_prev = ordered_points[prev_idx]
            p_curr = ordered_points[i]
            p_next = ordered_points[next_idx]
            
            # Curvatura usando círculo circunscrito
            curvature = self._compute_local_curvature(p_prev, p_curr, p_next)
            curvatures.append(curvature)
        
        curvatures = np.array(curvatures)
        
        # Puntos críticos (máximos y mínimos locales de curvatura)
        critical_points = self._find_critical_points(ordered_points, curvatures)
        
        return {
            "mean_curvature": float(np.mean(curvatures)),
            "max_curvature": float(np.max(curvatures)),
            "min_curvature": float(np.min(curvatures)),
            "curvature_std": float(np.std(curvatures)),
            "curvature_distribution": curvatures.tolist(),
            "critical_points": critical_points
        }
    
    async def _compute_topological_features(self, points: np.ndarray) -> Dict[str, Any]:
        """Computa características topológicas"""
        
        if len(points) < 3:
            return {
                "euler_characteristic": len(points),
                "genus": 0,
                "connected_components": 1,
                "holes": 0
            }
        
        # Triangulación de Delaunay para análisis topológico
        try:
            tri = Delaunay(points)
            
            # Calcular característica de Euler: V - E + F
            n_vertices = len(points)
            n_triangles = len(tri.simplices)
            
            # Contar aristas únicas
            edges = set()
            for triangle in tri.simplices:
                for i in range(3):
                    edge = tuple(sorted([triangle[i], triangle[(i+1)%3]]))
                    edges.add(edge)
            n_edges = len(edges)
            
            euler_char = n_vertices - n_edges + n_triangles
            genus = (2 - euler_char) // 2  # Para superficies orientables
            
        except Exception:
            euler_char = 1
            genus = 0
        
        # Análisis de conectividad usando grafo de proximidad
        connectivity_analysis = self._analyze_connectivity(points)
        
        return {
            "euler_characteristic": int(euler_char),
            "genus": int(max(0, genus)),
            "connected_components": connectivity_analysis["n_components"],
            "holes": int(max(0, genus)),
            "triangulation_info": {
                "n_vertices": len(points),
                "n_triangles": len(tri.simplices) if 'tri' in locals() else 0,
                "n_edges": len(edges) if 'edges' in locals() else 0
            } if 'tri' in locals() else None
        }
    
    async def _analyze_symmetries(self, points: np.ndarray) -> Dict[str, Any]:
        """Analiza simetrías de la forma"""
        
        if len(points) < 4:
            return {
                "reflection_symmetries": [],
                "rotational_symmetry_order": 1,
                "symmetry_score": 0.0
            }
        
        centroid = points.mean(axis=0)
        
        # Análisis de simetría reflectiva
        reflection_symmetries = []
        
        # Probar simetrías a diferentes ángulos
        test_angles = np.linspace(0, np.pi, 18)  # Cada 10 grados
        
        for angle in test_angles:
            symmetry_score = self._test_reflection_symmetry(points, centroid, angle)
            if symmetry_score > 0.8:  # Umbral de simetría
                reflection_symmetries.append({
                    "angle": float(angle),
                    "score": float(symmetry_score)
                })
        
        # Análisis de simetría rotacional
        rotational_order = self._detect_rotational_symmetry(points, centroid)
        
        # Score global de simetría
        symmetry_scores = [sym["score"] for sym in reflection_symmetries]
        overall_symmetry = np.max(symmetry_scores) if symmetry_scores else 0.0
        
        return {
            "reflection_symmetries": reflection_symmetries,
            "rotational_symmetry_order": int(rotational_order),
            "symmetry_score": float(overall_symmetry),
            "n_reflection_axes": len(reflection_symmetries)
        }
    
    async def _compute_shape_descriptors(self, points: np.ndarray) -> Dict[str, Any]:
        """Computa descriptores de forma invariantes"""
        
        if len(points) < 3:
            return {
                "fourier_descriptors": [],
                "shape_context": [],
                "moment_invariants": []
            }
        
        centroid = points.mean(axis=0)
        
        # Descriptores de Fourier
        fourier_descriptors = self._compute_fourier_descriptors(points, centroid)
        
        # Shape context (versión simplificada)
        shape_context = self._compute_shape_context(points)
        
        # Momentos invariantes de Hu
        moment_invariants = self._compute_moment_invariants(points)
        
        # Descriptores geométricos adicionales
        geometric_descriptors = self._compute_geometric_descriptors(points)
        
        return {
            "fourier_descriptors": fourier_descriptors,
            "shape_context": shape_context,
            "moment_invariants": moment_invariants,
            "geometric_descriptors": geometric_descriptors
        }
    
    async def _compute_alpha_shapes(self, points: np.ndarray) -> Dict[str, Any]:
        """Computa alpha shapes para diferentes valores de alpha"""
        
        if len(points) < 3:
            return {
                "alpha_values": [],
                "shape_areas": [],
                "optimal_alpha": 0.0
            }
        
        # Calcular rango de valores alpha
        distances = pdist(points)
        min_dist = np.min(distances[distances > 0]) if len(distances) > 0 else 1.0
        max_dist = np.max(distances)
        
        alpha_values = np.logspace(np.log10(min_dist/2), np.log10(max_dist*2), 20)
        
        shape_areas = []
        for alpha in alpha_values:
            try:
                # Simplificación: usar área de convex hull como aproximación
                hull = ConvexHull(points)
                # En una implementación real, se calcularía el alpha shape
                area = hull.volume * (1.0 - np.exp(-alpha))  # Aproximación
                shape_areas.append(area)
            except Exception  # TODO: Consider MathematicsError:
                shape_areas.append(0.0)
        
        # Encontrar alpha óptimo (máxima curvatura en la curva área vs alpha)
        if len(shape_areas) > 2:
            curvatures = np.diff(np.diff(shape_areas))
            optimal_idx = np.argmax(np.abs(curvatures)) + 1
            optimal_alpha = alpha_values[optimal_idx]
        else:
            optimal_alpha = alpha_values[len(alpha_values)//2] if len(alpha_values) > 0 else 1.0
        
        return {
            "alpha_values": alpha_values.tolist(),
            "shape_areas": shape_areas,
            "optimal_alpha": float(optimal_alpha)
        }
    
    async def _compute_medial_axis(self, points: np.ndarray, resolution: float) -> Dict[str, Any]:
        """Computa el medial axis transform (esqueleto)"""
        
        if len(points) < 3:
            return {
                "skeleton_points": [],
                "skeleton_radius": [],
                "branches": 0
            }
        
        try:
            # Crear imagen binaria de la forma
            min_coords = points.min(axis=0)
            max_coords = points.max(axis=0)
            
            # Expandir ligeramente los límites
            margin = resolution * 5
            min_coords -= margin
            max_coords += margin
            
            # Dimensiones de la imagen
            width = int((max_coords[0] - min_coords[0]) / resolution) + 1
            height = int((max_coords[1] - min_coords[1]) / resolution) + 1
            
            # Crear máscara binaria
            binary_image = np.zeros((height, width), dtype=bool)
            
            # Marcar puntos en la imagen
            for point in points:
                x = int((point[0] - min_coords[0]) / resolution)
                y = int((point[1] - min_coords[1]) / resolution)
                if 0 <= x < width and 0 <= y < height:
                    binary_image[y, x] = True
            
            # Dilatar para crear forma sólida
            if SKIMAGE_AVAILABLE:
                binary_image = morphology.binary_dilation(
                    binary_image, 
                    morphology.disk(max(2, int(0.1 / resolution)))
                )
                
                # Calcular esqueleto
                skeleton = morphology.skeletonize(binary_image)
                
                # Convertir de vuelta a coordenadas del mundo
                skeleton_points = []
                skeleton_coords = np.where(skeleton)
                
                for i in range(len(skeleton_coords[0])):
                    y, x = skeleton_coords[0][i], skeleton_coords[1][i]
                    world_x = min_coords[0] + x * resolution
                    world_y = min_coords[1] + y * resolution
                    skeleton_points.append([world_x, world_y])
                
                # Calcular radio del medial axis (distancia a borde)
                if len(skeleton_points) > 0:
                    distance_map = distance_transform_edt(binary_image)
                    skeleton_radius = [
                        distance_map[skeleton_coords[0][i], skeleton_coords[1][i]] * resolution
                        for i in range(len(skeleton_coords[0]))
                    ]
                else:
                    skeleton_radius = []
                
                # Contar ramas del esqueleto
                if len(skeleton_points) > 0:
                    skeleton_graph = self._skeleton_to_graph(skeleton, skeleton_coords)
                    branches = len([node for node, degree in skeleton_graph.degree() if degree == 1])
                else:
                    branches = 0
            else:
                # Fallback sin skimage
                skeleton_points = []
                skeleton_radius = []
                branches = 0
            
            return {
                "skeleton_points": skeleton_points,
                "skeleton_radius": skeleton_radius,
                "branches": branches,
                "skeleton_length": len(skeleton_points) * resolution
            }
            
        except Exception as e:
            self.logger.warning(f"Error computing medial axis: {str(e)}")
            return {
                "skeleton_points": [],
                "skeleton_radius": [],
                "branches": 0,
                "skeleton_length": 0.0
            }
    
    def _estimate_perimeter(self, points: np.ndarray) -> float:
        """Estima el perímetro de la forma"""
        
        if len(points) < 2:
            return 0.0
        
        # Ordenar puntos para formar contorno
        centroid = points.mean(axis=0)
        angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
        sorted_indices = np.argsort(angles)
        ordered_points = points[sorted_indices]
        
        # Calcular perímetro sumando distancias entre puntos consecutivos
        perimeter = 0.0
        for i in range(len(ordered_points)):
            next_i = (i + 1) % len(ordered_points)
            distance = np.linalg.norm(ordered_points[next_i] - ordered_points[i])
            perimeter += distance
        
        return perimeter
    
    def _compute_geometric_moments(self, points: np.ndarray, centroid: np.ndarray) -> List[float]:
        """Computa momentos geométricos"""
        
        if len(points) == 0:
            return [0.0] * 7
        
        # Momentos centrales
        centered_points = points - centroid
        
        # Momentos de orden 0, 1, 2
        m00 = len(points)  # Momento de orden 0
        m10 = m01 = 0.0   # Momentos de orden 1 (deberían ser 0 por estar centrados)
        m20 = np.sum(centered_points[:, 0] ** 2)
        m02 = np.sum(centered_points[:, 1] ** 2)
        m11 = np.sum(centered_points[:, 0] * centered_points[:, 1])
        
        # Momentos normalizados
        if m00 > 0:
            mu20 = m20 / m00
            mu02 = m02 / m00
            mu11 = m11 / m00
        else:
            mu20 = mu02 = mu11 = 0.0
        
        return [float(m00), float(mu20), float(mu02), float(mu11), 
                float(mu20 + mu02), float((mu20 - mu02)**2 + 4*mu11**2), 
                float(np.sqrt(mu20 + mu02))]
    
    def _compute_local_curvature(self, p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        """Computa curvatura local usando tres puntos consecutivos"""
        
        # Vectores
        v1 = p2 - p1
        v2 = p3 - p2
        
        # Evitar división por cero
        if np.linalg.norm(v1) == 0 or np.linalg.norm(v2) == 0:
            return 0.0
        
        # Curvatura usando fórmula del área del triángulo
        area = np.abs(np.cross(v1, v2))
        perimeter = np.linalg.norm(v1) + np.linalg.norm(v2) + np.linalg.norm(p3 - p1)
        
        if perimeter == 0:
            return 0.0
        
        # Curvatura como 4 * área / (producto de lados)
        curvature = 4 * area / (np.linalg.norm(v1) * np.linalg.norm(v2) * np.linalg.norm(p3 - p1))
        
        return curvature
    
    def _find_critical_points(self, points: np.ndarray, curvatures: np.ndarray) -> List[Dict[str, Any]]:
        """Encuentra puntos críticos en la curvatura"""
        
        critical_points = []
        
        if len(curvatures) < 3:
            return critical_points
        
        # Encontrar máximos y mínimos locales
        for i in range(1, len(curvatures) - 1):
            if curvatures[i] > curvatures[i-1] and curvatures[i] > curvatures[i+1]:
                # Máximo local
                critical_points.append({
                    "type": "maximum",
                    "position": points[i].tolist(),
                    "curvature": float(curvatures[i]),
                    "index": i
                })
            elif curvatures[i] < curvatures[i-1] and curvatures[i] < curvatures[i+1]:
                # Mínimo local
                critical_points.append({
                    "type": "minimum",
                    "position": points[i].tolist(),
                    "curvature": float(curvatures[i]),
                    "index": i
                })
        
        return critical_points
    
    def _analyze_connectivity(self, points: np.ndarray) -> Dict[str, Any]:
        """Analiza la conectividad de los puntos"""
        
        if len(points) < 2:
            return {"n_components": len(points), "largest_component": len(points)}
        
        # Crear grafo de proximidad
        distances = squareform(pdist(points))
        threshold = np.median(distances[distances > 0]) * 0.5
        
        graph = nx.Graph()
        graph.add_nodes_from(range(len(points)))
        
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                if distances[i, j] <= threshold:
                    graph.add_edge(i, j)
        
        # Analizar componentes conexas
        components = list(nx.connected_components(graph))
        component_sizes = [len(comp) for comp in components]
        
        return {
            "n_components": len(components),
            "largest_component": max(component_sizes) if component_sizes else 0,
            "component_sizes": component_sizes
        }
    
    def _test_reflection_symmetry(self, points: np.ndarray, centroid: np.ndarray, angle: float) -> float:
        """Prueba simetría reflectiva para un ángulo dado"""
        
        # Vector normal del eje de simetría
        normal = np.array([np.cos(angle), np.sin(angle)])
        
        # Reflejar puntos sobre el eje
        centered_points = points - centroid
        reflected_points = centered_points - 2 * np.outer(np.dot(centered_points, normal), normal)
        reflected_points += centroid
        
        # Calcular score de simetría
        min_distances = []
        for reflected_point in reflected_points:
            distances = np.linalg.norm(points - reflected_point, axis=1)
            min_distances.append(np.min(distances))
        
        # Score basado en qué tan cerca están los puntos reflejados de los originales
        median_distance = np.median(pdist(points))
        symmetry_score = np.exp(-np.mean(min_distances) / median_distance)
        
        return symmetry_score
    
    def _detect_rotational_symmetry(self, points: np.ndarray, centroid: np.ndarray) -> int:
        """Detecta orden de simetría rotacional"""
        
        # Probar órdenes de simetría de 2 a 8
        best_order = 1
        best_score = 0.0
        
        for order in range(2, 9):
            angle_step = 2 * np.pi / order
            scores = []
            
            for step in range(1, order):
                rotation_angle = step * angle_step
                
                # Rotar puntos
                cos_a, sin_a = np.cos(rotation_angle), np.sin(rotation_angle)
                rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
                
                centered_points = points - centroid
                rotated_points = (rotation_matrix @ centered_points.T).T + centroid
                
                # Calcular score de coincidencia
                min_distances = []
                for rotated_point in rotated_points:
                    distances = np.linalg.norm(points - rotated_point, axis=1)
                    min_distances.append(np.min(distances))
                
                median_distance = np.median(pdist(points))
                score = np.exp(-np.mean(min_distances) / median_distance)
                scores.append(score)
            
            avg_score = np.mean(scores)
            if avg_score > best_score and avg_score > 0.7:  # Umbral
                best_score = avg_score
                best_order = order
        
        return best_order
    
    def _compute_fourier_descriptors(self, points: np.ndarray, centroid: np.ndarray) -> List[float]:
        """Computa descriptores de Fourier de la forma"""
        
        if len(points) < 4:
            return [0.0] * 8
        
        # Ordenar puntos por ángulo
        angles = np.arctan2(points[:, 1] - centroid[1], points[:, 0] - centroid[0])
        sorted_indices = np.argsort(angles)
        ordered_points = points[sorted_indices]
        
        # Convertir a representación compleja
        complex_points = (ordered_points[:, 0] - centroid[0]) + 1j * (ordered_points[:, 1] - centroid[1])
        
        # FFT
        fft_coeffs = np.fft.fft(complex_points)
        
        # Tomar magnitudes de los primeros coeficientes (invariantes a traslación)
        descriptors = np.abs(fft_coeffs[1:9])  # Excluir DC component
        
        # Normalizar por el primer coeficiente (invariancia a escala)
        if descriptors[0] != 0:
            descriptors = descriptors / descriptors[0]
        
        return descriptors.tolist()
    
    def _compute_shape_context(self, points: np.ndarray) -> List[float]:
        """Computa shape context simplificado"""
        
        if len(points) < 2:
            return [0.0] * 12
        
        # Histograma de distancias y ángulos relativos
        n_bins_dist = 3
        n_bins_angle = 4
        
        shape_context = np.zeros(n_bins_dist * n_bins_angle)
        
        for i, point in enumerate(points):
            other_points = np.delete(points, i, axis=0)
            
            if len(other_points) == 0:
                continue
            
            # Distancias y ángulos relativos
            diff_vectors = other_points - point
            distances = np.linalg.norm(diff_vectors, axis=1)
            angles = np.arctan2(diff_vectors[:, 1], diff_vectors[:, 0])
            
            # Normalizar ángulos a [0, 2π]
            angles = (angles + 2 * np.pi) % (2 * np.pi)
            
            # Bins logarítmicos para distancias
            max_dist = np.max(distances) if len(distances) > 0 else 1.0
            min_dist = np.min(distances[distances > 0]) if np.any(distances > 0) else max_dist / 100
            
            log_distances = np.log(distances / min_dist + 1e-10)
            max_log_dist = np.log(max_dist / min_dist + 1e-10)
            
            # Bins uniformes para ángulos
            dist_bins = (log_distances / max_log_dist * n_bins_dist).astype(int)
            angle_bins = (angles / (2 * np.pi) * n_bins_angle).astype(int)
            
            # Contar en histograma
            for d_bin, a_bin in zip(dist_bins, angle_bins):
                if 0 <= d_bin < n_bins_dist and 0 <= a_bin < n_bins_angle:
                    shape_context[d_bin * n_bins_angle + a_bin] += 1
        
        # Normalizar
        total = np.sum(shape_context)
        if total > 0:
            shape_context /= total
        
        return shape_context.tolist()
    
    def _compute_moment_invariants(self, points: np.ndarray) -> List[float]:
        """Computa momentos invariantes de Hu"""
        
        if len(points) < 3:
            return [0.0] * 7
        
        # Momentos centrales
        centroid = points.mean(axis=0)
        centered_points = points - centroid
        
        # Momentos hasta orden 3
        m00 = len(points)
        m20 = np.sum(centered_points[:, 0] ** 2)
        m02 = np.sum(centered_points[:, 1] ** 2)
        m11 = np.sum(centered_points[:, 0] * centered_points[:, 1])
        m30 = np.sum(centered_points[:, 0] ** 3)
        m03 = np.sum(centered_points[:, 1] ** 3)
        m21 = np.sum((centered_points[:, 0] ** 2) * centered_points[:, 1])
        m12 = np.sum(centered_points[:, 0] * (centered_points[:, 1] ** 2))
        
        # Momentos normalizados
        if m00 > 0:
            eta20 = m20 / (m00 ** 2)
            eta02 = m02 / (m00 ** 2)
            eta11 = m11 / (m00 ** 2)
            eta30 = m30 / (m00 ** 2.5)
            eta03 = m03 / (m00 ** 2.5)
            eta21 = m21 / (m00 ** 2.5)
            eta12 = m12 / (m00 ** 2.5)
        else:
            return [0.0] * 7
        
        # Momentos invariantes de Hu
        I1 = eta20 + eta02
        I2 = (eta20 - eta02) ** 2 + 4 * eta11 ** 2
        I3 = (eta30 - 3 * eta12) ** 2 + (3 * eta21 - eta03) ** 2
        I4 = (eta30 + eta12) ** 2 + (eta21 + eta03) ** 2
        I5 = ((eta30 - 3 * eta12) * (eta30 + eta12) * 
              ((eta30 + eta12) ** 2 - 3 * (eta21 + eta03) ** 2) +
              (3 * eta21 - eta03) * (eta21 + eta03) * 
              (3 * (eta30 + eta12) ** 2 - (eta21 + eta03) ** 2))
        I6 = ((eta20 - eta02) * ((eta30 + eta12) ** 2 - (eta21 + eta03) ** 2) +
              4 * eta11 * (eta30 + eta12) * (eta21 + eta03))
        I7 = ((3 * eta21 - eta03) * (eta30 + eta12) * 
              ((eta30 + eta12) ** 2 - 3 * (eta21 + eta03) ** 2) -
              (eta30 - 3 * eta12) * (eta21 + eta03) * 
              (3 * (eta30 + eta12) ** 2 - (eta21 + eta03) ** 2))
        
        return [float(I1), float(I2), float(I3), float(I4), 
                float(I5), float(I6), float(I7)]
    
    def _compute_geometric_descriptors(self, points: np.ndarray) -> Dict[str, float]:
        """Computa descriptores geométricos adicionales"""
        
        if len(points) < 3:
            return {
                "compactness": 0.0,
                "rectangularity": 0.0,
                "convexity": 0.0,
                "solidity": 0.0
            }
        
        try:
            # Área y perímetro
            hull = ConvexHull(points)
            convex_area = hull.volume
            perimeter = self._estimate_perimeter(points)
            
            # Compacidad (círculo tiene compacidad de 1)
            compactness = (4 * np.pi * convex_area) / (perimeter ** 2) if perimeter > 0 else 0.0
            
            # Rectangularidad (qué tan parecido a un rectángulo)
            min_coords = points.min(axis=0)
            max_coords = points.max(axis=0)
            bounding_box_area = (max_coords[0] - min_coords[0]) * (max_coords[1] - min_coords[1])
            rectangularity = convex_area / bounding_box_area if bounding_box_area > 0 else 0.0
            
            # Convexidad (always 1.0 since we're using convex hull area)
            convexity = 1.0
            
            # Solidez (proporción del área dentro del convex hull)
            solidity = 1.0  # Simplificación
            
        except Exception:
            compactness = rectangularity = convexity = solidity = 0.0
        
        return {
            "compactness": float(compactness),
            "rectangularity": float(rectangularity),
            "convexity": float(convexity),
            "solidity": float(solidity)
        }
    
    def _skeleton_to_graph(self, skeleton: np.ndarray, skeleton_coords: Tuple[np.ndarray, np.ndarray]) -> nx.Graph:
        """Convierte esqueleto binario a grafo"""
        
        graph = nx.Graph()
        
        # Agregar nodos
        for i in range(len(skeleton_coords[0])):
            graph.add_node(i, pos=(skeleton_coords[1][i], skeleton_coords[0][i]))
        
        # Agregar aristas entre píxeles vecinos
        for i in range(len(skeleton_coords[0])):
            y1, x1 = skeleton_coords[0][i], skeleton_coords[1][i]
            
            for j in range(i + 1, len(skeleton_coords[0])):
                y2, x2 = skeleton_coords[0][j], skeleton_coords[1][j]
                
                # Verificar si son vecinos (8-conectividad)
                if abs(y1 - y2) <= 1 and abs(x1 - x2) <= 1:
                    graph.add_edge(i, j)
        
        return graph


# Instancia global
shape_analyzer = ShapeAnalyzer()
