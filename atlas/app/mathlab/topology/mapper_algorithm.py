"""
Algoritmo Mapper para Análisis Topológico de Datos (TDA)
======================================================

Implementación del algoritmo Mapper para visualización topológica de datos de alta dimensión.
Mapper es una técnica fundamental en TDA que construye un grafo simplicial para representar
la estructura topológica de datasets complejos.

Referencias:
- Singh, G., Mémoli, F., & Carlsson, G. (2007). "Topological Methods for the Analysis of High Dimensional Data Sets"
- Carlsson, G. (2009). "Topology and data"

Características:
- Funciones de filtro (filter functions) personalizables
- Clustering adaptativo con múltiples algoritmos
- Construcción de complejo nervioso (nerve complex)
- Visualización interactiva del grafo Mapper
- Análisis de estabilidad y persistencia

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
import asyncio
from typing import List, Dict, Any, Tuple, Optional, Callable, Union
import numpy as np
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, fcluster
from dataclasses import dataclass
import networkx as nx

# Clustering algorithms
try:
    from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class MapperConfig:
    """Configuración para el algoritmo Mapper"""
    n_intervals: int = 10
    overlap_fraction: float = 0.3
    cluster_algorithm: str = "kmeans"  # kmeans, dbscan, hierarchical
    cluster_params: Dict[str, Any] = None
    filter_function: str = "pca_1"  # pca_1, pca_2, density, distance_to_point
    resolution: float = 1.0
    gain: float = 0.3


class MapperAlgorithm:
    """
    Implementación completa del algoritmo Mapper para TDA
    """
    
    def __init__(self, config: Optional[MapperConfig] = None):
        self.config = config or MapperConfig()
        self.logger = logging.getLogger(__name__)
        
        # Funciones de filtro disponibles
        self.filter_functions = {
            "pca_1": self._pca_filter_1,
            "pca_2": self._pca_filter_2,
            "density": self._density_filter,
            "distance_to_point": self._distance_filter,
            "eccentricity": self._eccentricity_filter,
            "projection": self._projection_filter
        }
        
        # Algoritmos de clustering disponibles
        self.clustering_algorithms = {
            "kmeans": self._kmeans_clustering,
            "dbscan": self._dbscan_clustering,
            "hierarchical": self._hierarchical_clustering
        }
    
    async def compute_mapper_graph(
        self,
        data: np.ndarray,
        config: Optional[MapperConfig] = None
    ) -> Dict[str, Any]:
        """
        Computa el grafo Mapper completo
        
        Args:
            data: Datos de entrada (n_samples x n_features)
            config: Configuración del algoritmo
            
        Returns:
            Diccionario con el grafo Mapper y metadatos
        """
        
        config = config or self.config
        
        try:
            # Paso 1: Aplicar función de filtro
            filter_values = await self._apply_filter_function(data, config.filter_function)
            
            # Paso 2: Crear cover (cobertura) del rango de filtración
            cover_intervals = self._create_cover(filter_values, config)
            
            # Paso 3: Clustering en cada intervalo del cover
            clustered_intervals = await self._cluster_intervals(data, filter_values, cover_intervals, config)
            
            # Paso 4: Construir complejo nervioso (nerve complex)
            mapper_graph = self._build_nerve_complex(clustered_intervals)
            
            # Paso 5: Análisis adicional
            graph_analysis = await self._analyze_mapper_graph(mapper_graph, data, clustered_intervals)
            
            # Paso 6: Métricas de calidad
            quality_metrics = self._compute_quality_metrics(mapper_graph, data, config)
            
            return {
                "mapper_graph": mapper_graph,
                "cover_intervals": cover_intervals,
                "clustered_intervals": clustered_intervals,
                "filter_values": filter_values.tolist(),
                "graph_analysis": graph_analysis,
                "quality_metrics": quality_metrics,
                "config": {
                    "n_intervals": config.n_intervals,
                    "overlap_fraction": config.overlap_fraction,
                    "cluster_algorithm": config.cluster_algorithm,
                    "filter_function": config.filter_function
                },
                "algorithm": "mapper_tda"
            }
            
        except Exception as e:
            self.logger.error(f"Error computing Mapper graph: {str(e)}")
            raise
    
    async def _apply_filter_function(
        self,
        data: np.ndarray,
        filter_name: str
    ) -> np.ndarray:
        """Aplica función de filtro a los datos"""
        
        if filter_name not in self.filter_functions:
            raise ValueError(f"Unknown filter function: {filter_name}")
        
        return await self.filter_functions[filter_name](data)
    
    async def _pca_filter_1(self, data: np.ndarray) -> np.ndarray:
        """Primera componente principal como función de filtro"""
        if SKLEARN_AVAILABLE:
            pca = PCA(n_components=1)
            return pca.fit_transform(data).flatten()
        else:
            # Implementación propia de PCA para primera componente
            data_centered = data - np.mean(data, axis=0)
            cov_matrix = np.cov(data_centered.T)
            eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
            # Tomar el eigenvector correspondiente al mayor eigenvalue
            first_pc = eigenvectors[:, -1]
            return data_centered @ first_pc
    
    async def _pca_filter_2(self, data: np.ndarray) -> np.ndarray:
        """Segunda componente principal como función de filtro"""
        if SKLEARN_AVAILABLE:
            pca = PCA(n_components=2)
            components = pca.fit_transform(data)
            return components[:, 1]  # Segunda componente
        else:
            # Implementación propia simplificada
            data_centered = data - np.mean(data, axis=0)
            cov_matrix = np.cov(data_centered.T)
            eigenvalues, eigenvectors = np.linalg.eigh(cov_matrix)
            if len(eigenvalues) > 1:
                second_pc = eigenvectors[:, -2]  # Segunda mayor
                return data_centered @ second_pc
            else:
                return np.zeros(len(data))
    
    async def _density_filter(self, data: np.ndarray) -> np.ndarray:
        """Estimación de densidad local como función de filtro"""
        
        # Calcular matriz de distancias
        dist_matrix = squareform(pdist(data))
        
        # Radio adaptativo basado en la mediana de distancias
        median_dist = np.median(dist_matrix[dist_matrix > 0])
        radius = median_dist * 0.5
        
        # Contar puntos dentro del radio para cada punto
        density = np.sum(dist_matrix <= radius, axis=1)
        
        return density.astype(float)
    
    async def _distance_filter(self, data: np.ndarray) -> np.ndarray:
        """Distancia a un punto de referencia"""
        
        # Usar el centroide como punto de referencia
        centroid = np.mean(data, axis=0)
        
        # Calcular distancias
        distances = np.linalg.norm(data - centroid, axis=1)
        
        return distances
    
    async def _eccentricity_filter(self, data: np.ndarray) -> np.ndarray:
        """Excentricidad (distancia máxima a otros puntos)"""
        
        dist_matrix = squareform(pdist(data))
        eccentricity = np.max(dist_matrix, axis=1)
        
        return eccentricity
    
    async def _projection_filter(self, data: np.ndarray) -> np.ndarray:
        """Proyección en dirección aleatoria"""
        
        # Vector de proyección aleatorio normalizado
        projection_vector = np.random.normal(size=data.shape[1])
        projection_vector /= np.linalg.norm(projection_vector)
        
        # Proyectar datos
        projections = data @ projection_vector
        
        return projections
    
    def _create_cover(
        self,
        filter_values: np.ndarray,
        config: MapperConfig
    ) -> List[Tuple[float, float]]:
        """Crea cover (cobertura) del rango de filtración"""
        
        min_val = np.min(filter_values)
        max_val = np.max(filter_values)
        
        # Calcular longitud de intervalo y solapamiento
        total_range = max_val - min_val
        interval_length = total_range / (config.n_intervals * (1 - config.overlap_fraction) + config.overlap_fraction)
        step_size = interval_length * (1 - config.overlap_fraction)
        
        intervals = []
        for i in range(config.n_intervals):
            start = min_val + i * step_size
            end = start + interval_length
            intervals.append((start, min(end, max_val)))
        
        return intervals
    
    async def _cluster_intervals(
        self,
        data: np.ndarray,
        filter_values: np.ndarray,
        cover_intervals: List[Tuple[float, float]],
        config: MapperConfig
    ) -> Dict[int, List[Dict[str, Any]]]:
        """Aplica clustering en cada intervalo del cover"""
        
        clustered_intervals = {}
        
        for i, (start, end) in enumerate(cover_intervals):
            # Filtrar puntos en este intervalo
            mask = (filter_values >= start) & (filter_values <= end)
            interval_data = data[mask]
            interval_indices = np.where(mask)[0]
            
            if len(interval_data) == 0:
                clustered_intervals[i] = []
                continue
            
            # Aplicar clustering
            clusters = await self._apply_clustering(interval_data, config)
            
            # Organizar clusters con metadatos
            interval_clusters = []
            for cluster_id in range(max(clusters) + 1):
                cluster_mask = clusters == cluster_id
                cluster_points = interval_indices[cluster_mask]
                
                if len(cluster_points) > 0:
                    cluster_info = {
                        "interval_id": i,
                        "cluster_id": cluster_id,
                        "point_indices": cluster_points.tolist(),
                        "size": len(cluster_points),
                        "centroid": np.mean(interval_data[cluster_mask], axis=0).tolist(),
                        "filter_range": (float(np.min(filter_values[cluster_points])),
                                       float(np.max(filter_values[cluster_points])))
                    }
                    interval_clusters.append(cluster_info)
            
            clustered_intervals[i] = interval_clusters
        
        return clustered_intervals
    
    async def _apply_clustering(
        self,
        data: np.ndarray,
        config: MapperConfig
    ) -> np.ndarray:
        """Aplica algoritmo de clustering específico"""
        
        if config.cluster_algorithm not in self.clustering_algorithms:
            raise ValueError(f"Unknown clustering algorithm: {config.cluster_algorithm}")
        
        return await self.clustering_algorithms[config.cluster_algorithm](data, config.cluster_params or {})
    
    async def _kmeans_clustering(self, data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """K-means clustering"""
        
        n_clusters = params.get("n_clusters", min(len(data), 3))
        
        if SKLEARN_AVAILABLE:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            return kmeans.fit_predict(data)
        else:
            # Implementación K-means simplificada
            return self._simple_kmeans(data, n_clusters)
    
    async def _dbscan_clustering(self, data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """DBSCAN clustering"""
        
        if not SKLEARN_AVAILABLE:
            return np.zeros(len(data))  # Fallback a un solo cluster
        
        eps = params.get("eps", 0.5)
        min_samples = params.get("min_samples", 3)
        
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        labels = dbscan.fit_predict(data)
        
        # Convertir -1 (ruido) a cluster separado
        unique_labels = np.unique(labels)
        label_mapping = {label: i for i, label in enumerate(unique_labels)}
        
        return np.array([label_mapping[label] for label in labels])
    
    async def _hierarchical_clustering(self, data: np.ndarray, params: Dict[str, Any]) -> np.ndarray:
        """Hierarchical clustering"""
        
        n_clusters = params.get("n_clusters", min(len(data), 3))
        
        if SKLEARN_AVAILABLE:
            clustering = AgglomerativeClustering(n_clusters=n_clusters)
            return clustering.fit_predict(data)
        else:
            # Implementación usando scipy
            if len(data) < 2:
                return np.zeros(len(data))
            
            linkage_matrix = linkage(data, method='ward')
            clusters = fcluster(linkage_matrix, n_clusters, criterion='maxclust')
            
            return clusters - 1  # Convertir a indexado desde 0
    
    def _simple_kmeans(self, data: np.ndarray, k: int) -> np.ndarray:
        """Implementación simple de K-means"""
        
        if len(data) <= k:
            return np.arange(len(data))
        
        # Inicializar centroides aleatoriamente
        centroids = data[np.random.choice(len(data), k, replace=False)]
        
        max_iters = 100
        for _ in range(max_iters):
            # Asignar puntos a centroides más cercanos
            distances = np.linalg.norm(data[:, None] - centroids, axis=2)
            labels = np.argmin(distances, axis=1)
            
            # Actualizar centroides
            new_centroids = np.array([data[labels == i].mean(axis=0) if np.any(labels == i) 
                                    else centroids[i] for i in range(k)])
            
            # Verificar convergencia
            if np.allclose(centroids, new_centroids):
                break
            
            centroids = new_centroids
        
        return labels
    
    def _build_nerve_complex(
        self,
        clustered_intervals: Dict[int, List[Dict[str, Any]]]
    ) -> nx.Graph:
        """Construye el complejo nervioso (nerve complex) del Mapper"""
        
        graph = nx.Graph()
        
        # Crear nodos para cada cluster
        node_id = 0
        node_mapping = {}
        
        for interval_id, clusters in clustered_intervals.items():
            for cluster in clusters:
                graph.add_node(node_id, **cluster)
                node_mapping[(interval_id, cluster["cluster_id"])] = node_id
                node_id += 1
        
        # Crear aristas entre clusters que comparten puntos
        nodes = list(graph.nodes(data=True))
        
        for i, (node1_id, node1_data) in enumerate(nodes):
            for j, (node2_id, node2_data) in enumerate(nodes[i+1:], i+1):
                # Verificar intersección de puntos
                points1 = set(node1_data["point_indices"])
                points2 = set(node2_data["point_indices"])
                
                intersection = points1 & points2
                
                if len(intersection) > 0:
                    # Crear arista con peso basado en tamaño de intersección
                    weight = len(intersection) / len(points1 | points2)
                    graph.add_edge(
                        node1_id, 
                        node2_id,
                        weight=weight,
                        intersection_size=len(intersection),
                        intersection_points=list(intersection)
                    )
        
        return graph
    
    async def _analyze_mapper_graph(
        self,
        graph: nx.Graph,
        data: np.ndarray,
        clustered_intervals: Dict[int, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """Analiza propiedades del grafo Mapper"""
        
        analysis = {
            "n_nodes": graph.number_of_nodes(),
            "n_edges": graph.number_of_edges(),
            "n_components": nx.number_connected_components(graph),
            "density": nx.density(graph) if graph.number_of_nodes() > 1 else 0.0
        }
        
        if graph.number_of_nodes() > 0:
            # Métricas de centralidad
            if graph.number_of_nodes() > 1:
                betweenness = nx.betweenness_centrality(graph)
                closeness = nx.closeness_centrality(graph)
                degree = dict(graph.degree())
                
                analysis.update({
                    "avg_degree": np.mean(list(degree.values())),
                    "max_degree": max(degree.values()) if degree else 0,
                    "avg_betweenness": np.mean(list(betweenness.values())),
                    "max_betweenness": max(betweenness.values()) if betweenness else 0,
                    "avg_closeness": np.mean(list(closeness.values())),
                })
            
            # Componentes conexas
            components = list(nx.connected_components(graph))
            component_sizes = [len(comp) for comp in components]
            
            analysis.update({
                "component_sizes": component_sizes,
                "largest_component_size": max(component_sizes) if component_sizes else 0,
                "avg_component_size": np.mean(component_sizes) if component_sizes else 0
            })
            
            # Clustering coefficient
            if graph.number_of_edges() > 0:
                clustering_coeff = nx.average_clustering(graph)
                analysis["clustering_coefficient"] = clustering_coeff
        
        return analysis
    
    def _compute_quality_metrics(
        self,
        graph: nx.Graph,
        data: np.ndarray,
        config: MapperConfig
    ) -> Dict[str, float]:
        """Computa métricas de calidad del Mapper"""
        
        metrics = {}
        
        # Cobertura de datos
        covered_points = set()
        for node_id, node_data in graph.nodes(data=True):
            covered_points.update(node_data["point_indices"])
        
        coverage = len(covered_points) / len(data) if len(data) > 0 else 0.0
        metrics["data_coverage"] = coverage
        
        # Resolución (número promedio de puntos por nodo)
        if graph.number_of_nodes() > 0:
            node_sizes = [len(node_data["point_indices"]) for _, node_data in graph.nodes(data=True)]
            metrics["avg_node_size"] = np.mean(node_sizes)
            metrics["resolution_score"] = 1.0 / (1.0 + np.std(node_sizes))
        else:
            metrics["avg_node_size"] = 0.0
            metrics["resolution_score"] = 0.0
        
        # Conectividad
        if graph.number_of_nodes() > 1:
            n_components = nx.number_connected_components(graph)
            connectivity_score = 1.0 - (n_components - 1) / (graph.number_of_nodes() - 1)
            metrics["connectivity_score"] = connectivity_score
        else:
            metrics["connectivity_score"] = 1.0
        
        # Score global de calidad
        quality_components = [
            metrics.get("data_coverage", 0.0),
            metrics.get("resolution_score", 0.0),
            metrics.get("connectivity_score", 0.0)
        ]
        
        metrics["overall_quality"] = np.mean(quality_components)
        
        return metrics


# Instancia global del algoritmo Mapper
mapper_algorithm = MapperAlgorithm()
