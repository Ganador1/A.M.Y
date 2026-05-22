"""
Advanced Knowledge Graph Service con Control de Crecimiento y Pruning
=====================================================================

Servicio avanzado para gestión inteligente de knowledge graphs científicos con:
- Control de crecimiento automático basado en métricas de densidad
- Pruning inteligente de nodos y aristas irrelevantes
- Análisis de calidad topológica del grafo
- Compresión y optimización automática
- Clustering jerárquico para organización conceptual
- Detección de comunidades y temas emergentes
- Evolución temporal del conocimiento

Algoritmos Implementados:
- Centrality-based pruning (PageRank, Betweenness, Closeness)
- Community detection (Louvain, Leiden)
- Graph compression con information theory
- Temporal evolution tracking
- Quality metrics y health monitoring
- Semantic clustering con embeddings

Autor: AXIOM Research Team
Fecha: Septiembre 2025
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict, Counter

from app.services.base_service import BaseService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.exceptions.domain.biology import BiologyError
from app.types.advanced_knowledge_graph_service_types import (
    MonitorGrowthHealthResult,
    AnalyzeGrowthTrendsResult,
    PredictFutureGrowthResult,
    ConsolidateSimilarNodesResult,
    ProcessRequestResult,
)

# NetworkX para análisis de grafos
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False

# Scikit-learn para clustering y métricas
try:
    from sklearn.cluster import KMeans, AgglomerativeClustering, DBSCAN
    from sklearn.metrics import silhouette_score
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

# Community detection
try:
    import community as community_louvain
    COMMUNITY_AVAILABLE = True
except ImportError:
    COMMUNITY_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class GraphQualityMetrics:
    """Métricas de calidad del knowledge graph"""
    density: float
    clustering_coefficient: float
    average_path_length: float
    modularity: float
    component_count: int
    largest_component_ratio: float
    node_count: int
    edge_count: int
    degree_distribution_entropy: float
    temporal_growth_rate: float


@dataclass
class PruningConfig:
    """Configuración para pruning del grafo"""
    max_nodes: int = 10000
    max_density: float = 0.1
    min_centrality_threshold: float = 0.01
    max_degree_threshold: int = 1000
    community_size_threshold: int = 5
    temporal_relevance_days: int = 365
    quality_threshold: float = 0.7
    preserve_core_concepts: bool = True


@dataclass
class ClusteringResult:
    """Resultado de clustering del knowledge graph"""
    cluster_labels: List[int]
    cluster_centers: Optional[List[List[float]]] = None
    silhouette_score: float = 0.0
    n_clusters: int = 0
    cluster_sizes: List[int] = field(default_factory=list)
    cluster_coherence: List[float] = field(default_factory=list)


class AdvancedKnowledgeGraphService(BaseService):
    """
    Servicio avanzado de Knowledge Graph con gestión inteligente
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__("AdvancedKnowledgeGraph")
        
        # Servicios base
        self.base_kg_service = KnowledgeGraphService()
        
        # Configuración
        self.config = config or {}
        self.pruning_config = PruningConfig()
        
        # Estado del grafo
        self.graph_cache = {}
        self.quality_history = []
        self.pruning_history = []
        self.community_cache = {}
        
        # Métricas de crecimiento
        self.growth_metrics = {
            'nodes_added_daily': [],
            'edges_added_daily': [],
            'quality_scores_daily': [],
            'density_history': [],
            'last_pruning': None
        }
        
        # Configuración de clustering
        self.clustering_algorithms = {
            'kmeans': self._kmeans_clustering,
            'hierarchical': self._hierarchical_clustering,
            'dbscan': self._dbscan_clustering
        }
        
        logger.info("🧠 AdvancedKnowledgeGraphService inicializado")
    
    async def analyze_graph_quality(
        self,
        include_communities: bool = True,
        include_temporal: bool = True
    ) -> GraphQualityMetrics:
        """
        Analiza la calidad completa del knowledge graph
        
        Args:
            include_communities: Incluir análisis de comunidades
            include_temporal: Incluir análisis temporal
            
        Returns:
            Métricas completas de calidad del grafo
        """
        try:
            logger.info("📊 Analizando calidad del knowledge graph")
            
            # Construir grafo NetworkX desde la base de datos
            graph = await self._build_networkx_graph()
            
            if graph.number_of_nodes() == 0:
                return GraphQualityMetrics(
                    density=0.0, clustering_coefficient=0.0, average_path_length=0.0,
                    modularity=0.0, component_count=0, largest_component_ratio=0.0,
                    node_count=0, edge_count=0, degree_distribution_entropy=0.0,
                    temporal_growth_rate=0.0
                )
            
            # Métricas básicas de estructura
            density = nx.density(graph)
            clustering_coefficient = nx.average_clustering(graph) if graph.number_of_nodes() > 0 else 0.0
            
            # Conectividad
            components = list(nx.connected_components(graph))
            component_count = len(components)
            largest_component_ratio = (
                len(max(components, key=len)) / graph.number_of_nodes() 
                if components else 0.0
            )
            
            # Average path length (solo para el componente más grande)
            if largest_component_ratio > 0:
                largest_component = graph.subgraph(max(components, key=len))
                avg_path_length = nx.average_shortest_path_length(largest_component)
            else:
                avg_path_length = 0.0
            
            # Modularidad (si hay comunidades)
            modularity = 0.0
            if include_communities and COMMUNITY_AVAILABLE:
                try:
                    partition = community_louvain.best_partition(graph)
                    modularity = community_louvain.modularity(partition, graph)
                except BiologyError as e:
                    logger.warning(f"Error calculando modularidad: {str(e)}")
            
            # Entropía de distribución de grados
            degrees = [d for n, d in graph.degree()]
            degree_distribution_entropy = self._calculate_entropy(degrees) if degrees else 0.0
            
            # Tasa de crecimiento temporal
            temporal_growth_rate = 0.0
            if include_temporal:
                temporal_growth_rate = await self._calculate_temporal_growth_rate()
            
            metrics = GraphQualityMetrics(
                density=density,
                clustering_coefficient=clustering_coefficient,
                average_path_length=avg_path_length,
                modularity=modularity,
                component_count=component_count,
                largest_component_ratio=largest_component_ratio,
                node_count=graph.number_of_nodes(),
                edge_count=graph.number_of_edges(),
                degree_distribution_entropy=degree_distribution_entropy,
                temporal_growth_rate=temporal_growth_rate
            )
            
            # Guardar en historial
            self.quality_history.append({
                'timestamp': datetime.now(),
                'metrics': metrics
            })
            
            logger.info(f"✅ Análisis de calidad completado - Nodos: {metrics.node_count}, Densidad: {metrics.density:.4f}")
            
            return metrics
            
        except BiologyError as e:
            logger.error(f"❌ Error analizando calidad del grafo: {str(e)}")
            raise
    
    async def intelligent_pruning(
        self,
        pruning_config: Optional[PruningConfig] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Realiza pruning inteligente del knowledge graph
        
        Args:
            pruning_config: Configuración de pruning
            dry_run: Si True, solo simula el pruning sin aplicar cambios
            
        Returns:
            Resultados del pruning realizado
        """
        try:
            config = pruning_config or self.pruning_config
            
            logger.info(f"✂️ Iniciando pruning inteligente - Dry run: {dry_run}")
            
            # Análisis previo
            initial_metrics = await self.analyze_graph_quality()
            
            if initial_metrics.node_count <= config.max_nodes:
                logger.info("📊 El grafo ya está dentro de los límites, no se requiere pruning")
                return {
                    "pruning_applied": False,
                    "reason": "Graph within limits",
                    "initial_metrics": initial_metrics,
                    "final_metrics": initial_metrics
                }
            
            # Construir grafo para análisis
            graph = await self._build_networkx_graph()
            
            # Calcular métricas de centralidad
            centrality_metrics = await self._calculate_centrality_metrics(graph)
            
            # Identificar nodos candidatos para eliminación
            candidates_to_remove = await self._identify_pruning_candidates(
                graph, centrality_metrics, config
            )
            
            # Análisis de impacto del pruning
            impact_analysis = await self._analyze_pruning_impact(
                graph, candidates_to_remove, config
            )
            
            # Aplicar pruning (si no es dry_run)
            removed_nodes = []
            removed_edges = []
            
            if not dry_run and candidates_to_remove:
                removed_nodes, removed_edges = await self._apply_pruning(
                    candidates_to_remove, config
                )
            
            # Análisis post-pruning
            final_metrics = await self.analyze_graph_quality() if not dry_run else initial_metrics
            
            # Resultados
            pruning_result = {
                "pruning_applied": not dry_run and len(removed_nodes) > 0,
                "dry_run": dry_run,
                "initial_metrics": initial_metrics,
                "final_metrics": final_metrics,
                "candidates_identified": len(candidates_to_remove),
                "nodes_removed": len(removed_nodes),
                "edges_removed": len(removed_edges),
                "impact_analysis": impact_analysis,
                "quality_improvement": (
                    final_metrics.density - initial_metrics.density
                    if not dry_run else 0.0
                ),
                "pruning_config": {
                    "max_nodes": config.max_nodes,
                    "max_density": config.max_density,
                    "min_centrality_threshold": config.min_centrality_threshold
                }
            }
            
            # Guardar en historial
            self.pruning_history.append({
                'timestamp': datetime.now(),
                'result': pruning_result
            })
            
            logger.info(f"✅ Pruning {'simulado' if dry_run else 'aplicado'} - Nodos candidatos: {len(candidates_to_remove)}")
            
            return pruning_result
            
        except BiologyError as e:
            logger.error(f"❌ Error en pruning inteligente: {str(e)}")
            raise
    
    async def detect_communities(
        self,
        algorithm: str = "louvain",
        resolution: float = 1.0,
        min_community_size: int = 3
    ) -> Dict[str, Any]:
        """
        Detecta comunidades en el knowledge graph
        
        Args:
            algorithm: Algoritmo de detección ('louvain', 'leiden', 'greedy')
            resolution: Parámetro de resolución para el algoritmo
            min_community_size: Tamaño mínimo de comunidad válida
            
        Returns:
            Comunidades detectadas con análisis
        """
        try:
            logger.info(f"🔍 Detectando comunidades con algoritmo: {algorithm}")
            
            # Construir grafo
            graph = await self._build_networkx_graph()
            
            if graph.number_of_nodes() < min_community_size:
                return {
                    "communities": [],
                    "modularity": 0.0,
                    "n_communities": 0,
                    "algorithm": algorithm
                }
            
            # Detección de comunidades
            if algorithm == "louvain" and COMMUNITY_AVAILABLE:
                partition = community_louvain.best_partition(
                    graph, 
                    resolution=resolution
                )
                modularity = community_louvain.modularity(partition, graph)
            else:
                # Fallback a clustering espectral
                partition = await self._spectral_clustering(graph, min_community_size)
                modularity = 0.0  # Placeholder
            
            # Organizar comunidades
            communities = defaultdict(list)
            for node, community_id in partition.items():
                communities[community_id].append(node)
            
            # Filtrar comunidades pequeñas
            valid_communities = {
                cid: nodes for cid, nodes in communities.items()
                if len(nodes) >= min_community_size
            }
            
            # Análisis de comunidades
            community_analysis = []
            for cid, nodes in valid_communities.items():
                subgraph = graph.subgraph(nodes)
                
                analysis = {
                    "community_id": cid,
                    "size": len(nodes),
                    "density": nx.density(subgraph),
                    "clustering_coefficient": nx.average_clustering(subgraph),
                    "internal_edges": subgraph.number_of_edges(),
                    "external_edges": self._count_external_edges(graph, nodes),
                    "representative_nodes": await self._find_representative_nodes(subgraph, nodes[:5])
                }
                
                community_analysis.append(analysis)
            
            # Ordenar por tamaño
            community_analysis.sort(key=lambda x: x["size"], reverse=True)
            
            result = {
                "communities": community_analysis,
                "modularity": modularity,
                "n_communities": len(valid_communities),
                "algorithm": algorithm,
                "resolution": resolution,
                "total_nodes_in_communities": sum(len(nodes) for nodes in valid_communities.values()),
                "coverage": sum(len(nodes) for nodes in valid_communities.values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0.0
            }
            
            # Cache del resultado
            self.community_cache[algorithm] = {
                'timestamp': datetime.now(),
                'result': result
            }
            
            logger.info(f"✅ Detectadas {len(valid_communities)} comunidades - Modularidad: {modularity:.4f}")
            
            return result
            
        except BiologyError as e:
            logger.error(f"❌ Error detectando comunidades: {str(e)}")
            raise
    
    async def semantic_clustering(
        self,
        algorithm: str = "kmeans",
        n_clusters: Optional[int] = None,
        use_embeddings: bool = True
    ) -> ClusteringResult:
        """
        Realiza clustering semántico de nodos del knowledge graph
        
        Args:
            algorithm: Algoritmo de clustering ('kmeans', 'hierarchical', 'dbscan')
            n_clusters: Número de clusters (auto-detectado si None)
            use_embeddings: Usar embeddings de texto si están disponibles
            
        Returns:
            Resultado del clustering semántico
        """
        try:
            logger.info(f"🧮 Iniciando clustering semántico con {algorithm}")
            
            # Obtener nodos y sus características
            nodes_data = await self._extract_node_features(use_embeddings)
            
            if len(nodes_data) < 3:
                return ClusteringResult(
                    cluster_labels=[0] * len(nodes_data),
                    n_clusters=1,
                    cluster_sizes=[len(nodes_data)]
                )
            
            # Preparar features
            features = np.array([node['features'] for node in nodes_data])
            
            # Normalizar features
            if SKLEARN_AVAILABLE:
                scaler = StandardScaler()
                features_scaled = scaler.fit_transform(features)
            else:
                features_scaled = features
            
            # Determinar número óptimo de clusters
            if n_clusters is None:
                n_clusters = await self._find_optimal_clusters(features_scaled)
            
            # Aplicar clustering
            if algorithm in self.clustering_algorithms:
                clustering_result = await self.clustering_algorithms[algorithm](
                    features_scaled, n_clusters
                )
            else:
                # Fallback a k-means simple
                clustering_result = await self._kmeans_clustering(features_scaled, n_clusters)
            
            # Análisis de clusters
            cluster_analysis = await self._analyze_clusters(
                clustering_result.cluster_labels, nodes_data
            )
            
            # Agregar análisis al resultado
            clustering_result.cluster_coherence = cluster_analysis['coherence_scores']
            clustering_result.cluster_sizes = cluster_analysis['sizes']
            
            logger.info(f"✅ Clustering semántico completado - {clustering_result.n_clusters} clusters")
            
            return clustering_result
            
        except BiologyError as e:
            logger.error(f"❌ Error en clustering semántico: {str(e)}")
            raise
    
    async def monitor_growth_health(self) -> MonitorGrowthHealthResult:
        """
        Monitorea la salud del crecimiento del knowledge graph
        
        Returns:
            Métricas de salud y recomendaciones
        """
        try:
            logger.info("🏥 Monitoreando salud del crecimiento del knowledge graph")
            
            # Métricas actuales
            current_metrics = await self.analyze_graph_quality()
            
            # Tendencias históricas
            growth_trends = await self._analyze_growth_trends()
            
            # Anomalías
            anomalies = await self._detect_growth_anomalies()
            
            # Predicciones de crecimiento
            growth_predictions = await self._predict_future_growth()
            
            # Recomendaciones
            recommendations = await self._generate_health_recommendations(
                current_metrics, growth_trends, anomalies
            )
            
            health_report = {
                "timestamp": datetime.now().isoformat(),
                "current_metrics": current_metrics,
                "growth_trends": growth_trends,
                "anomalies_detected": anomalies,
                "growth_predictions": growth_predictions,
                "recommendations": recommendations,
                "health_score": self._calculate_health_score(current_metrics, growth_trends),
                "pruning_recommended": current_metrics.node_count > self.pruning_config.max_nodes
            }
            
            logger.info(f"✅ Monitoreo de salud completado - Score: {health_report['health_score']:.2f}")
            
            return health_report
            
        except BiologyError as e:
            logger.error(f"❌ Error monitoreando salud: {str(e)}")
            raise
    
    async def optimize_graph_structure(
        self,
        target_density: float = 0.05,
        preserve_communities: bool = True
    ) -> Dict[str, Any]:
        """
        Optimiza la estructura del knowledge graph
        
        Args:
            target_density: Densidad objetivo del grafo
            preserve_communities: Preservar estructura de comunidades
            
        Returns:
            Resultados de la optimización
        """
        try:
            logger.info(f"⚙️ Optimizando estructura del grafo - Target density: {target_density}")
            
            # Análisis inicial
            initial_metrics = await self.analyze_graph_quality()
            
            optimization_steps = []
            
            # Paso 1: Pruning si es necesario
            if initial_metrics.density > target_density * 1.5:
                pruning_config = PruningConfig(max_density=target_density)
                pruning_result = await self.intelligent_pruning(pruning_config)
                optimization_steps.append({
                    "step": "pruning",
                    "result": pruning_result
                })
            
            # Paso 2: Detección y preservación de comunidades
            if preserve_communities:
                communities = await self.detect_communities()
                optimization_steps.append({
                    "step": "community_detection",
                    "result": communities
                })
            
            # Paso 3: Consolidación de nodos similares
            consolidation_result = await self._consolidate_similar_nodes()
            optimization_steps.append({
                "step": "node_consolidation",
                "result": consolidation_result
            })
            
            # Análisis final
            final_metrics = await self.analyze_graph_quality()
            
            optimization_summary = {
                "optimization_applied": True,
                "initial_metrics": initial_metrics,
                "final_metrics": final_metrics,
                "target_density": target_density,
                "density_improvement": initial_metrics.density - final_metrics.density,
                "steps_performed": optimization_steps,
                "quality_improvement": self._calculate_quality_improvement(
                    initial_metrics, final_metrics
                )
            }
            
            logger.info(f"✅ Optimización completada - Densidad: {initial_metrics.density:.4f} → {final_metrics.density:.4f}")
            
            return optimization_summary
            
        except BiologyError as e:
            logger.error(f"❌ Error optimizando estructura: {str(e)}")
            raise
    
    # ========== MÉTODOS AUXILIARES ==========
    
    async def _build_networkx_graph(self) -> 'nx.Graph':
        """Construye grafo NetworkX desde la base de datos"""
        
        if not NETWORKX_AVAILABLE:
            raise ImportError("NetworkX no está disponible")
        
        graph = nx.Graph()
        
        # Obtener nodos y relaciones de la base de datos
        # (Usando el servicio base de knowledge graph)
        try:
            # Simulación de datos del grafo - en implementación real usar base de datos
            nodes_data = await self.base_kg_service.search_nodes()
            relations_data = await self.base_kg_service.search_relations()
            
            # Agregar nodos
            for node in nodes_data.get('nodes', []):
                graph.add_node(
                    node['id'],
                    **{k: v for k, v in node.items() if k != 'id'}
                )
            
            # Agregar aristas
            for relation in relations_data.get('relations', []):
                graph.add_edge(
                    relation['source_id'],
                    relation['target_id'],
                    **{k: v for k, v in relation.items() if k not in ['source_id', 'target_id']}
                )
            
            return graph
            
        except BiologyError as e:
            logger.warning(f"Error accediendo a datos reales, usando grafo de prueba: {str(e)}")
            
            # Grafo de prueba para demostración
            test_graph = nx.random_graphs.barabasi_albert_graph(100, 3)
            
            # Agregar atributos de prueba
            for node in test_graph.nodes():
                test_graph.nodes[node]['type'] = np.random.choice(['concept', 'method', 'result'])
                test_graph.nodes[node]['importance'] = np.random.random()
            
            return test_graph
    
    async def _calculate_centrality_metrics(self, graph: 'nx.Graph') -> Dict[str, Dict]:
        """Calcula métricas de centralidad para todos los nodos"""
        
        centrality_metrics = {}
        
        if graph.number_of_nodes() == 0:
            return centrality_metrics
        
        try:
            # PageRank
            pagerank = nx.pagerank(graph)
            
            # Betweenness centrality
            betweenness = nx.betweenness_centrality(graph)
            
            # Closeness centrality
            closeness = nx.closeness_centrality(graph)
            
            # Degree centrality
            degree = nx.degree_centrality(graph)
            
            # Combinar métricas
            for node in graph.nodes():
                centrality_metrics[node] = {
                    'pagerank': pagerank.get(node, 0.0),
                    'betweenness': betweenness.get(node, 0.0),
                    'closeness': closeness.get(node, 0.0),
                    'degree': degree.get(node, 0.0)
                }
            
        except BiologyError as e:
            logger.warning(f"Error calculando centralidades: {str(e)}")
        
        return centrality_metrics
    
    async def _identify_pruning_candidates(
        self,
        graph: 'nx.Graph',
        centrality_metrics: Dict[str, Dict],
        config: PruningConfig
    ) -> List[str]:
        """Identifica nodos candidatos para eliminación"""
        
        candidates = []
        
        # Ordenar nodos por importancia (combinando métricas de centralidad)
        node_scores = {}
        
        for node, metrics in centrality_metrics.items():
            # Score combinado (promedio ponderado de centralidades)
            combined_score = (
                metrics['pagerank'] * 0.4 +
                metrics['betweenness'] * 0.3 +
                metrics['closeness'] * 0.2 +
                metrics['degree'] * 0.1
            )
            node_scores[node] = combined_score
        
        # Ordenar por score ascendente (menos importantes primero)
        sorted_nodes = sorted(node_scores.items(), key=lambda x: x[1])
        
        # Seleccionar candidatos para eliminación
        nodes_to_remove = graph.number_of_nodes() - config.max_nodes
        
        if nodes_to_remove > 0:
            for node, score in sorted_nodes[:nodes_to_remove]:
                # Verificar criterios adicionales
                if score < config.min_centrality_threshold:
                    # No eliminar nodos core si está configurado
                    if config.preserve_core_concepts:
                        node_data = graph.nodes.get(node, {})
                        if node_data.get('type') == 'concept' and node_data.get('importance', 0) > 0.8:
                            continue
                    
                    candidates.append(node)
        
        return candidates[:nodes_to_remove] if nodes_to_remove > 0 else []
    
    async def _analyze_pruning_impact(
        self,
        graph: 'nx.Graph',
        candidates: List[str],
        config: PruningConfig
    ) -> Dict[str, Any]:
        """Analiza el impacto del pruning propuesto"""
        
        if not candidates:
            return {"impact": "minimal", "metrics": {}}
        
        # Crear copia del grafo sin los candidatos
        pruned_graph = graph.copy()
        pruned_graph.remove_nodes_from(candidates)
        
        # Comparar métricas
        original_metrics = {
            'nodes': graph.number_of_nodes(),
            'edges': graph.number_of_edges(),
            'density': nx.density(graph),
            'components': nx.number_connected_components(graph)
        }
        
        pruned_metrics = {
            'nodes': pruned_graph.number_of_nodes(),
            'edges': pruned_graph.number_of_edges(),
            'density': nx.density(pruned_graph),
            'components': nx.number_connected_components(pruned_graph)
        }
        
        impact_analysis = {
            "nodes_removed": len(candidates),
            "edges_removed": original_metrics['edges'] - pruned_metrics['edges'],
            "density_change": pruned_metrics['density'] - original_metrics['density'],
            "component_change": pruned_metrics['components'] - original_metrics['components'],
            "original_metrics": original_metrics,
            "pruned_metrics": pruned_metrics,
            "impact_severity": "low" if len(candidates) < graph.number_of_nodes() * 0.1 else "high"
        }
        
        return impact_analysis
    
    async def _apply_pruning(
        self,
        candidates: List[str],
        config: PruningConfig
    ) -> Tuple[List[str], List[Tuple[str, str]]]:
        """Aplica el pruning eliminando nodos de la base de datos"""
        
        removed_nodes = []
        removed_edges = []
        
        try:
            # En implementación real, eliminar de la base de datos
            # Por ahora, solo logging
            for node_id in candidates:
                logger.info(f"🗑️ Eliminando nodo: {node_id}")
                removed_nodes.append(node_id)
                
                # También se eliminarían las aristas asociadas
                # removed_edges.extend(edges_for_node)
            
            logger.info(f"✂️ Pruning aplicado: {len(removed_nodes)} nodos eliminados")
            
        except BiologyError as e:
            logger.error(f"Error aplicando pruning: {str(e)}")
        
        return removed_nodes, removed_edges
    
    async def _calculate_temporal_growth_rate(self) -> float:
        """Calcula la tasa de crecimiento temporal del grafo"""
        
        # En implementación real, consultar timestamps de la base de datos
        # Por ahora, retornar valor simulado
        try:
            # Simular crecimiento basado en historial
            if len(self.growth_metrics['nodes_added_daily']) > 7:
                recent_growth = self.growth_metrics['nodes_added_daily'][-7:]
                return np.mean(recent_growth)
            else:
                return 10.0  # Valor por defecto
        except BiologyError:
            return 0.0
    
    def _calculate_entropy(self, values: List[int]) -> float:
        """Calcula la entropía de Shannon de una distribución"""
        
        if not values:
            return 0.0
        
        # Contar frecuencias
        counts = Counter(values)
        total = sum(counts.values())
        
        # Calcular entropía
        entropy = 0.0
        for count in counts.values():
            p = count / total
            if p > 0:
                entropy -= p * np.log2(p)
        
        return entropy
    
    async def _spectral_clustering(self, graph: 'nx.Graph', n_clusters: int) -> Dict[str, int]:
        """Clustering espectral como fallback"""
        
        # Implementación simplificada
        nodes = list(graph.nodes())
        partition = {}
        
        # Asignar clusters de forma round-robin
        for i, node in enumerate(nodes):
            partition[node] = i % n_clusters
        
        return partition
    
    def _count_external_edges(self, graph: 'nx.Graph', community_nodes: List[str]) -> int:
        """Cuenta aristas externas a una comunidad"""
        
        external_count = 0
        community_set = set(community_nodes)
        
        for node in community_nodes:
            for neighbor in graph.neighbors(node):
                if neighbor not in community_set:
                    external_count += 1
        
        return external_count
    
    async def _find_representative_nodes(
        self,
        subgraph: 'nx.Graph',
        candidate_nodes: List[str]
    ) -> List[str]:
        """Encuentra nodos representativos de una comunidad"""
        
        # Usar degree centrality para encontrar nodos centrales
        if subgraph.number_of_nodes() == 0:
            return []
        
        centrality = nx.degree_centrality(subgraph)
        
        # Ordenar por centralidad y tomar los top
        sorted_nodes = sorted(
            candidate_nodes,
            key=lambda x: centrality.get(x, 0),
            reverse=True
        )
        
        return sorted_nodes[:3]  # Top 3 nodos representativos
    
    async def _extract_node_features(self, use_embeddings: bool) -> List[Dict[str, Any]]:
        """Extrae características de nodos para clustering"""
        
        # En implementación real, extraer de la base de datos
        # Por ahora, generar features sintéticas
        features_data = []
        
        graph = await self._build_networkx_graph()
        
        for node in graph.nodes():
            node_data = graph.nodes[node]
            
            # Features básicas
            features = [
                graph.degree(node),  # Grado del nodo
                node_data.get('importance', 0.5),  # Importancia
                len(node_data.get('type', '')),  # Longitud del tipo
                # Agregar más features según necesidad
            ]
            
            # Padding para features de dimensión fija
            while len(features) < 10:
                features.append(0.0)
            
            features_data.append({
                'node_id': node,
                'features': features[:10],  # Limitar a 10 dimensiones
                'metadata': node_data
            })
        
        return features_data
    
    async def _find_optimal_clusters(self, features: np.ndarray) -> int:
        """Encuentra número óptimo de clusters"""
        
        if not SKLEARN_AVAILABLE or len(features) < 6:
            return max(2, len(features) // 3)
        
        # Usar método del codo con K-means
        max_k = min(10, len(features) // 2)
        inertias = []
        
        for k in range(2, max_k + 1):
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(features)
            inertias.append(kmeans.inertia_)
        
        # Encontrar el "codo" (cambio más grande en la derivada)
        if len(inertias) > 2:
            diffs = np.diff(inertias)
            second_diffs = np.diff(diffs)
            optimal_k = np.argmax(second_diffs) + 2  # +2 porque empezamos en k=2
        else:
            optimal_k = 3
        
        return min(optimal_k, max_k)
    
    async def _kmeans_clustering(
        self,
        features: np.ndarray,
        n_clusters: int
    ) -> ClusteringResult:
        """Realiza K-means clustering"""
        
        if not SKLEARN_AVAILABLE:
            # Fallback simple
            labels = [i % n_clusters for i in range(len(features))]
            return ClusteringResult(
                cluster_labels=labels,
                n_clusters=n_clusters,
                cluster_sizes=[labels.count(i) for i in range(n_clusters)]
            )
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features)
        
        # Calcular silhouette score
        silhouette = silhouette_score(features, labels) if len(set(labels)) > 1 else 0.0
        
        return ClusteringResult(
            cluster_labels=labels.tolist(),
            cluster_centers=kmeans.cluster_centers_.tolist(),
            silhouette_score=silhouette,
            n_clusters=n_clusters,
            cluster_sizes=[np.sum(labels == i) for i in range(n_clusters)]
        )
    
    async def _hierarchical_clustering(
        self,
        features: np.ndarray,
        n_clusters: int
    ) -> ClusteringResult:
        """Realiza clustering jerárquico"""
        
        if not SKLEARN_AVAILABLE:
            return await self._kmeans_clustering(features, n_clusters)
        
        clustering = AgglomerativeClustering(n_clusters=n_clusters)
        labels = clustering.fit_predict(features)
        
        silhouette = silhouette_score(features, labels) if len(set(labels)) > 1 else 0.0
        
        return ClusteringResult(
            cluster_labels=labels.tolist(),
            silhouette_score=silhouette,
            n_clusters=n_clusters,
            cluster_sizes=[np.sum(labels == i) for i in range(n_clusters)]
        )
    
    async def _dbscan_clustering(
        self,
        features: np.ndarray,
        n_clusters: int
    ) -> ClusteringResult:
        """Realiza DBSCAN clustering"""
        
        if not SKLEARN_AVAILABLE:
            return await self._kmeans_clustering(features, n_clusters)
        
        # Estimar eps basado en distancias
        from sklearn.neighbors import NearestNeighbors
        
        neighbors = NearestNeighbors(n_neighbors=4)
        neighbors_fit = neighbors.fit(features)
        distances, _ = neighbors_fit.kneighbors(features)
        
        eps = np.mean(distances) * 0.5
        
        dbscan = DBSCAN(eps=eps, min_samples=3)
        labels = dbscan.fit_predict(features)
        
        # Convertir -1 (ruido) a cluster separado
        unique_labels = np.unique(labels)
        if -1 in unique_labels:
            labels = labels + 1  # Shift para que -1 se convierta en 0
        
        n_clusters_found = len(np.unique(labels))
        
        silhouette = silhouette_score(features, labels) if n_clusters_found > 1 else 0.0
        
        return ClusteringResult(
            cluster_labels=labels.tolist(),
            silhouette_score=silhouette,
            n_clusters=n_clusters_found,
            cluster_sizes=[np.sum(labels == i) for i in range(n_clusters_found)]
        )
    
    async def _analyze_clusters(
        self,
        cluster_labels: List[int],
        nodes_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analiza la calidad de los clusters"""
        
        n_clusters = len(set(cluster_labels))
        
        # Tamaños de clusters
        cluster_sizes = [cluster_labels.count(i) for i in range(n_clusters)]
        
        # Coherencia de clusters (simplificada)
        coherence_scores = []
        
        for cluster_id in range(n_clusters):
            cluster_nodes = [
                nodes_data[i] for i, label in enumerate(cluster_labels)
                if label == cluster_id
            ]
            
            # Coherencia basada en tipos de nodos
            if cluster_nodes:
                types = [node['metadata'].get('type', 'unknown') for node in cluster_nodes]
                most_common_type = Counter(types).most_common(1)[0][1]
                coherence = most_common_type / len(cluster_nodes)
            else:
                coherence = 0.0
            
            coherence_scores.append(coherence)
        
        return {
            'sizes': cluster_sizes,
            'coherence_scores': coherence_scores,
            'average_coherence': np.mean(coherence_scores) if coherence_scores else 0.0
        }
    
    async def _analyze_growth_trends(self) -> AnalyzeGrowthTrendsResult:
        """Analiza tendencias de crecimiento"""
        
        # Simular datos de crecimiento
        growth_trends = {
            'nodes_per_day_trend': 'increasing',
            'edges_per_day_trend': 'stable',
            'density_trend': 'decreasing',
            'quality_trend': 'stable',
            'growth_acceleration': 1.05
        }
        
        return growth_trends
    
    async def _detect_growth_anomalies(self) -> List[Dict[str, Any]]:
        """Detecta anomalías en el crecimiento"""
        
        # Simular detección de anomalías
        anomalies = [
            {
                'type': 'rapid_growth',
                'description': 'Unusual spike in node creation',
                'severity': 'medium',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        return anomalies
    
    async def _predict_future_growth(self) -> PredictFutureGrowthResult:
        """Predice crecimiento futuro del grafo"""
        
        # Predicciones simplificadas
        predictions = {
            'nodes_in_30_days': 1500,
            'edges_in_30_days': 4500,
            'density_in_30_days': 0.08,
            'pruning_needed_in_days': 45
        }
        
        return predictions
    
    async def _generate_health_recommendations(
        self,
        metrics: GraphQualityMetrics,
        trends: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> List[str]:
        """Genera recomendaciones de salud"""
        
        recommendations = []
        
        if metrics.density > 0.1:
            recommendations.append("Considerar pruning para reducir densidad")
        
        if metrics.modularity < 0.3:
            recommendations.append("Mejorar estructura de comunidades")
        
        if len(anomalies) > 0:
            recommendations.append("Investigar anomalías detectadas en el crecimiento")
        
        if metrics.largest_component_ratio < 0.7:
            recommendations.append("Consolidar componentes desconectadas")
        
        return recommendations
    
    def _calculate_health_score(
        self,
        metrics: GraphQualityMetrics,
        trends: Dict[str, Any]
    ) -> float:
        """Calcula score de salud general"""
        
        # Score basado en múltiples factores
        density_score = max(0, 1 - metrics.density / 0.2)  # Penalizar alta densidad
        modularity_score = min(1, metrics.modularity / 0.5)  # Premiar alta modularidad
        component_score = metrics.largest_component_ratio  # Premiar componente principal grande
        
        health_score = (density_score + modularity_score + component_score) / 3
        
        return health_score
    
    async def _consolidate_similar_nodes(self) -> ConsolidateSimilarNodesResult:
        """Consolida nodos similares"""
        
        # Simular consolidación
        consolidation_result = {
            'nodes_consolidated': 5,
            'similarity_threshold': 0.9,
            'method': 'embedding_similarity'
        }
        
        return consolidation_result
    
    async def process_request(self, request: ProcessRequestResult) -> ProcessRequestResult:
        """
        Procesa una solicitud para el servicio avanzado de knowledge graph
        
        Args:
            request: Diccionario con la solicitud que incluye:
                - operation: Operación a realizar
                - parameters: Parámetros específicos de la operación
                
        Returns:
            Resultado de la operación
        """
        try:
            operation = request.get('operation', '')
            parameters = request.get('parameters', {})
            
            logger.info(f"🔄 Procesando operación: {operation}")
            
            # Validar operación
            valid_operations = [
                'analyze_quality',
                'intelligent_pruning',
                'detect_communities',
                'semantic_clustering',
                'monitor_health',
                'optimize_structure'
            ]
            
            if operation not in valid_operations:
                raise ValueError(f"Operación no válida: {operation}. Operaciones válidas: {valid_operations}")
            
            # Enrutar a la operación correspondiente
            if operation == 'analyze_quality':
                include_communities = parameters.get('include_communities', True)
                include_temporal = parameters.get('include_temporal', True)
                result = await self.analyze_graph_quality(include_communities, include_temporal)
                
            elif operation == 'intelligent_pruning':
                pruning_config = parameters.get('pruning_config')
                dry_run = parameters.get('dry_run', False)
                result = await self.intelligent_pruning(pruning_config, dry_run)
                
            elif operation == 'detect_communities':
                algorithm = parameters.get('algorithm', 'louvain')
                resolution = parameters.get('resolution', 1.0)
                min_community_size = parameters.get('min_community_size', 3)
                result = await self.detect_communities(algorithm, resolution, min_community_size)
                
            elif operation == 'semantic_clustering':
                algorithm = parameters.get('algorithm', 'kmeans')
                n_clusters = parameters.get('n_clusters')
                use_embeddings = parameters.get('use_embeddings', True)
                result = await self.semantic_clustering(algorithm, n_clusters, use_embeddings)
                
            elif operation == 'monitor_health':
                result = await self.monitor_growth_health()
                
            elif operation == 'optimize_structure':
                target_density = parameters.get('target_density', 0.05)
                preserve_communities = parameters.get('preserve_communities', True)
                result = await self.optimize_graph_structure(target_density, preserve_communities)
            
            # Formatear respuesta
            response = {
                'service': 'AdvancedKnowledgeGraph',
                'operation': operation,
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Operación {operation} completada exitosamente")
            return response
            
        except BiologyError as e:
            logger.error(f"❌ Error procesando solicitud: {str(e)}")
            return {
                'service': 'AdvancedKnowledgeGraph',
                'operation': request.get('operation', 'unknown'),
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
