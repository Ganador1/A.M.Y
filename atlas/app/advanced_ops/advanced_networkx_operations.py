"""
Advanced NetworkX Operations Module for AXIOM

This module provides comprehensive advanced NetworkX operations, including:
- Graph creation and manipulation with advanced algorithms
- Centrality measures and network analysis
- Community detection and clustering
- Graph visualization and layout algorithms
- Network flow and connectivity analysis
- Graph isomorphism and matching
- Random graph generation and analysis
- Temporal and dynamic network analysis
- Graph neural network preparation

Author: AXIOM Development Team
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Union, Any
import warnings
warnings.filterwarnings('ignore')


class AdvancedNetworkxOperations:
    """
    Advanced NetworkX operations for comprehensive graph analysis and manipulation.
    """

    def __init__(self):
        """Initialize the advanced NetworkX operations."""
        self.layout_algorithms = [
            'spring', 'circular', 'random', 'shell', 'spectral',
            'kamada_kawai', 'planar', 'spiral', 'multipartite'
        ]
        self.centrality_measures = [
            'degree', 'betweenness', 'closeness', 'eigenvector',
            'katz', 'pagerank', 'percolation'
        ]
        self.community_algorithms = [
            'greedy_modularity', 'louvain', 'label_propagation',
            'girvan_newman', 'fluid_communities'
        ]

    def advanced_graph_pipeline(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive graph analysis and manipulation pipeline.

        Args:
            data: Dictionary containing graph data and configuration

        Returns:
            Dictionary with graph analysis results and metadata
        """
        try:
            # Create or load graph
            graph = self._create_graph_from_data(data)

            # Apply advanced analysis
            analysis_results = self._perform_advanced_analysis(graph, data)

            # Generate visualizations if requested
            if data.get('visualize', False):
                visualization = self._create_advanced_visualization(graph, data)
                analysis_results['visualization'] = visualization

            # Calculate network metrics
            metrics = self._calculate_network_metrics(graph, data)
            analysis_results['metrics'] = metrics

            return {
                'graph': graph,
                'analysis': analysis_results,
                'graph_type': type(graph).__name__,
                'nodes': graph.number_of_nodes(),
                'edges': graph.number_of_edges(),
                'metadata': {
                    'directed': graph.is_directed(),
                    'weighted': nx.is_weighted(graph),
                    'connected': nx.is_connected(graph) if not graph.is_directed() else nx.is_weakly_connected(graph)
                }
            }

        except Exception as e:
            return {'error': f'Advanced graph pipeline failed: {str(e)}'}

    def _create_graph_from_data(self, data: Dict[str, Any]) -> Union[nx.Graph, nx.DiGraph, nx.MultiGraph]:
        """Create graph from various data formats."""
        graph_type = data.get('graph_type', 'undirected')

        if graph_type == 'directed':
            G = nx.DiGraph()
        elif graph_type == 'multigraph':
            G = nx.MultiGraph()
        else:
            G = nx.Graph()

        # Add nodes and edges from data
        if 'nodes' in data:
            G.add_nodes_from(data['nodes'])

        if 'edges' in data:
            if isinstance(data['edges'][0], tuple):
                G.add_edges_from(data['edges'])
            else:
                # Handle edge list with attributes
                for edge in data['edges']:
                    if len(edge) == 2:
                        G.add_edge(edge[0], edge[1])
                    elif len(edge) == 3:
                        G.add_edge(edge[0], edge[1], weight=edge[2])
                    else:
                        G.add_edge(*edge)

        # Add node attributes
        if 'node_attributes' in data:
            for node, attrs in data['node_attributes'].items():
                if node in G:
                    for attr, value in attrs.items():
                        G.nodes[node][attr] = value

        # Add edge attributes
        if 'edge_attributes' in data:
            for edge, attrs in data['edge_attributes'].items():
                if G.has_edge(*edge):
                    for attr, value in attrs.items():
                        G.edges[edge][attr] = value

        return G

    def _perform_advanced_analysis(self, graph: Union[nx.Graph, nx.DiGraph],
                                 data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive graph analysis."""
        analysis = {}

        # Centrality analysis
        if data.get('centrality_analysis', False):
            analysis['centrality'] = self._calculate_centrality_measures(graph, data)

        # Community detection
        if data.get('community_detection', False):
            analysis['communities'] = self._detect_communities(graph, data)

        # Network flow analysis
        if data.get('flow_analysis', False) and graph.is_directed():
            analysis['flow'] = self._analyze_network_flow(graph, data)

        # Graph isomorphism
        if data.get('isomorphism_check', False) and 'comparison_graph' in data:
            analysis['isomorphism'] = self._check_graph_isomorphism(graph, data['comparison_graph'])

        # Path analysis
        if data.get('path_analysis', False):
            analysis['paths'] = self._analyze_paths(graph, data)

        # Clustering and assortativity
        if data.get('clustering_analysis', False):
            analysis['clustering'] = self._calculate_clustering_coefficients(graph)

        return analysis

    def _calculate_centrality_measures(self, graph: Union[nx.Graph, nx.DiGraph],
                                     data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate various centrality measures."""
        centrality = {}

        try:
            # Degree centrality
            centrality['degree'] = nx.degree_centrality(graph)

            # Betweenness centrality
            centrality['betweenness'] = nx.betweenness_centrality(graph)

            # Closeness centrality
            centrality['closeness'] = nx.closeness_centrality(graph)

            # Eigenvector centrality
            try:
                centrality['eigenvector'] = nx.eigenvector_centrality(graph)
            except Exception:
                centrality['eigenvector'] = 'Not calculable (disconnected graph)'

            # PageRank
            centrality['pagerank'] = nx.pagerank(graph)

            # Katz centrality
            try:
                centrality['katz'] = nx.katz_centrality(graph)
            except Exception:
                centrality['katz'] = 'Not calculable'

        except Exception as e:
            centrality['error'] = f'Centrality calculation failed: {str(e)}'

        return centrality

    def _detect_communities(self, graph: Union[nx.Graph, nx.DiGraph],
                           data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect communities in the graph."""
        communities = {}

        try:
            # Greedy modularity communities
            from networkx.algorithms.community import greedy_modularity_communities
            communities['greedy_modularity'] = list(greedy_modularity_communities(graph))

            # Label propagation
            from networkx.algorithms.community import label_propagation_communities
            communities['label_propagation'] = list(label_propagation_communities(graph))

            # Girvan-Newman algorithm (first few levels)
            from networkx.algorithms.community import girvan_newman
            gn_communities = girvan_newman(graph)
            communities['girvan_newman'] = [next(gn_communities) for _ in range(min(3, len(list(gn_communities))))]

            # Modularity score
            if communities.get('greedy_modularity'):
                from networkx.algorithms.community import modularity
                communities['modularity_score'] = modularity(graph, communities['greedy_modularity'])

        except Exception as e:
            communities['error'] = f'Community detection failed: {str(e)}'

        return communities

    def _analyze_network_flow(self, graph: nx.DiGraph, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network flow in directed graphs."""
        flow_analysis = {}

        try:
            if 'source' in data and 'sink' in data:
                source, sink = data['source'], data['sink']

                # Maximum flow
                flow_value, flow_dict = nx.maximum_flow(graph, source, sink)
                flow_analysis['max_flow'] = flow_value
                flow_analysis['flow_dict'] = flow_dict

                # Minimum cut
                cut_value, partition = nx.minimum_cut(graph, source, sink)
                flow_analysis['min_cut'] = cut_value
                flow_analysis['partition'] = partition

        except Exception as e:
            flow_analysis['error'] = f'Flow analysis failed: {str(e)}'

        return flow_analysis

    def _check_graph_isomorphism(self, graph1: Union[nx.Graph, nx.DiGraph],
                               graph2: Union[nx.Graph, nx.DiGraph]) -> Dict[str, Any]:
        """Check if two graphs are isomorphic."""
        isomorphism = {}

        try:
            # Check isomorphism
            isomorphism['is_isomorphic'] = nx.is_isomorphic(graph1, graph2)

            # Find isomorphism mapping if isomorphic
            if isomorphism['is_isomorphic']:
                from networkx.algorithms.isomorphism import GraphMatcher
                if graph1.is_directed():
                    matcher = GraphMatcher(graph1, graph2)
                else:
                    matcher = GraphMatcher(graph1, graph2)

                if matcher.is_isomorphic():
                    isomorphism['mapping'] = matcher.mapping

        except Exception as e:
            isomorphism['error'] = f'Isomorphism check failed: {str(e)}'

        return isomorphism

    def _analyze_paths(self, graph: Union[nx.Graph, nx.DiGraph],
                      data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze paths in the graph."""
        paths = {}

        try:
            # Shortest paths
            if data.get('source') and data.get('target'):
                source, target = data['source'], data['target']

                if nx.has_path(graph, source, target):
                    paths['shortest_path'] = nx.shortest_path(graph, source, target)
                    paths['shortest_path_length'] = nx.shortest_path_length(graph, source, target)

                    # All shortest paths
                    paths['all_shortest_paths'] = list(nx.all_shortest_paths(graph, source, target))

            # Average shortest path length
            if nx.is_connected(graph):
                paths['average_shortest_path'] = nx.average_shortest_path_length(graph)
            elif graph.is_directed() and nx.is_weakly_connected(graph):
                paths['average_shortest_path'] = nx.average_shortest_path_length(graph.to_undirected())

            # Diameter
            if nx.is_connected(graph):
                paths['diameter'] = nx.diameter(graph)
            elif graph.is_directed() and nx.is_weakly_connected(graph):
                paths['diameter'] = nx.diameter(graph.to_undirected())

        except Exception as e:
            paths['error'] = f'Path analysis failed: {str(e)}'

        return paths

    def _calculate_clustering_coefficients(self, graph: Union[nx.Graph, nx.DiGraph]) -> Dict[str, Any]:
        """Calculate clustering coefficients."""
        clustering = {}

        try:
            # Local clustering coefficients
            clustering['local'] = nx.clustering(graph)

            # Average clustering coefficient
            clustering['average'] = nx.average_clustering(graph)

            # Global clustering coefficient (transitivity)
            clustering['transitivity'] = nx.transitivity(graph)

            # Square clustering
            clustering['square'] = nx.square_clustering(graph)

        except Exception as e:
            clustering['error'] = f'Clustering calculation failed: {str(e)}'

        return clustering

    def _create_advanced_visualization(self, graph: Union[nx.Graph, nx.DiGraph],
                                     data: Dict[str, Any]) -> Dict[str, Any]:
        """Create advanced graph visualization."""
        visualization = {}

        try:
            fig, ax = plt.subplots(figsize=data.get('figsize', (12, 8)))

            # Choose layout algorithm
            layout_algorithm = data.get('layout', 'spring')
            if layout_algorithm == 'spring':
                pos = nx.spring_layout(graph)
            elif layout_algorithm == 'circular':
                pos = nx.circular_layout(graph)
            elif layout_algorithm == 'random':
                pos = nx.random_layout(graph)
            elif layout_algorithm == 'kamada_kawai':
                pos = nx.kamada_kawai_layout(graph)
            else:
                pos = nx.spring_layout(graph)

            # Draw nodes
            node_colors = data.get('node_colors', 'lightblue')
            node_sizes = data.get('node_sizes', 300)
            nx.draw_networkx_nodes(graph, pos, node_color=node_colors,
                                 node_size=node_sizes, ax=ax)

            # Draw edges
            edge_colors = data.get('edge_colors', 'gray')
            edge_widths = data.get('edge_widths', 1)
            nx.draw_networkx_edges(graph, pos, edge_color=edge_colors,
                                 width=edge_widths, ax=ax)

            # Draw labels
            if data.get('show_labels', True):
                nx.draw_networkx_labels(graph, pos, ax=ax)

            # Add title and styling
            ax.set_title(data.get('title', 'Graph Visualization'))
            ax.axis('off')

            visualization['figure'] = fig
            visualization['layout'] = layout_algorithm
            visualization['nodes_drawn'] = graph.number_of_nodes()
            visualization['edges_drawn'] = graph.number_of_edges()

        except Exception as e:
            visualization['error'] = f'Visualization failed: {str(e)}'

        return visualization

    def _calculate_network_metrics(self, graph: Union[nx.Graph, nx.DiGraph],
                                 data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive network metrics."""
        metrics = {}

        try:
            # Basic metrics
            metrics['number_of_nodes'] = graph.number_of_nodes()
            metrics['number_of_edges'] = graph.number_of_edges()
            metrics['density'] = nx.density(graph)

            # Degree metrics
            degrees = dict(graph.degree())
            metrics['average_degree'] = np.mean(list(degrees.values()))
            metrics['degree_variance'] = np.var(list(degrees.values()))

            # Connectivity metrics
            if not graph.is_directed():
                metrics['is_connected'] = nx.is_connected(graph)
                if metrics['is_connected']:
                    metrics['number_of_components'] = 1
                else:
                    metrics['number_of_components'] = nx.number_connected_components(graph)
            else:
                metrics['is_weakly_connected'] = nx.is_weakly_connected(graph)
                metrics['is_strongly_connected'] = nx.is_strongly_connected(graph)

            # Assortativity
            try:
                metrics['degree_assortativity'] = nx.degree_assortativity_coefficient(graph)
            except Exception:
                metrics['degree_assortativity'] = 'Not calculable'

            # Small world metrics
            if nx.is_connected(graph):
                metrics['sigma'] = nx.sigma(graph)  # Small-world coefficient
                metrics['omega'] = nx.omega(graph)  # Small-world coefficient alternative

        except Exception as e:
            metrics['error'] = f'Metrics calculation failed: {str(e)}'

        return metrics

    def random_graph_generation(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate random graphs with advanced properties.

        Args:
            config: Dictionary containing generation parameters

        Returns:
            Dictionary with generated graph and properties
        """
        try:
            graph_type = config.get('type', 'erdos_renyi')
            n = config.get('n', 100)
            p = config.get('p', 0.1)

            if graph_type == 'erdos_renyi':
                G = nx.erdos_renyi_graph(n, p)
            elif graph_type == 'barabasi_albert':
                m = config.get('m', 2)
                G = nx.barabasi_albert_graph(n, m)
            elif graph_type == 'watts_strogatz':
                k = config.get('k', 4)
                beta = config.get('beta', 0.1)
                G = nx.watts_strogatz_graph(n, k, beta)
            elif graph_type == 'powerlaw_cluster':
                m = config.get('m', 2)
                p = config.get('p', 0.1)
                G = nx.powerlaw_cluster_graph(n, m, p)
            else:
                G = nx.erdos_renyi_graph(n, 0.1)

            # Calculate properties
            properties = {
                'type': graph_type,
                'nodes': G.number_of_nodes(),
                'edges': G.number_of_edges(),
                'density': nx.density(G),
                'average_clustering': nx.average_clustering(G),
                'is_connected': nx.is_connected(G)
            }

            if nx.is_connected(G):
                properties['average_shortest_path'] = nx.average_shortest_path_length(G)
                properties['diameter'] = nx.diameter(G)

            return {
                'graph': G,
                'properties': properties,
                'config': config
            }

        except Exception as e:
            return {'error': f'Random graph generation failed: {str(e)}'}

    def graph_neural_network_preparation(self, graph: Union[nx.Graph, nx.DiGraph],
                                       features: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Prepare graph data for Graph Neural Networks (GNNs).

        Args:
            graph: Input graph
            features: Node and edge features

        Returns:
            Dictionary with GNN-ready data
        """
        try:
            # Convert to adjacency matrix
            adj_matrix = nx.adjacency_matrix(graph).toarray()

            # Node features
            if features and 'node_features' in features:
                node_features = features['node_features']
            else:
                # Use node degrees as default features
                degrees = dict(graph.degree())
                node_features = np.array([[deg] for deg in degrees.values()])

            # Edge features
            if features and 'edge_features' in features:
                edge_features = features['edge_features']
            else:
                edge_features = np.ones((graph.number_of_edges(), 1))

            # Node labels (if available)
            node_labels = None
            if features and 'node_labels' in features:
                node_labels = features['node_labels']

            # Train/validation/test splits
            n_nodes = graph.number_of_nodes()
            indices = np.arange(n_nodes)
            np.random.shuffle(indices)

            train_split = int(0.6 * n_nodes)
            val_split = int(0.8 * n_nodes)

            train_indices = indices[:train_split]
            val_indices = indices[train_split:val_split]
            test_indices = indices[val_split:]

            return {
                'adjacency_matrix': adj_matrix,
                'node_features': node_features,
                'edge_features': edge_features,
                'node_labels': node_labels,
                'train_indices': train_indices,
                'val_indices': val_indices,
                'test_indices': test_indices,
                'graph_info': {
                    'n_nodes': n_nodes,
                    'n_edges': graph.number_of_edges(),
                    'is_directed': graph.is_directed()
                }
            }

        except Exception as e:
            return {'error': f'GNN preparation failed: {str(e)}'}

    def temporal_network_analysis(self, temporal_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze temporal network evolution.

        Args:
            temporal_data: List of graph snapshots over time

        Returns:
            Dictionary with temporal analysis results
        """
        try:
            temporal_analysis = {
                'snapshots': len(temporal_data),
                'evolution_metrics': []
            }

            for i, snapshot in enumerate(temporal_data):
                graph = self._create_graph_from_data(snapshot)
                metrics = self._calculate_network_metrics(graph, {})

                temporal_analysis['evolution_metrics'].append({
                    'timestamp': snapshot.get('timestamp', i),
                    'metrics': metrics
                })

            # Calculate evolution trends
            if len(temporal_data) > 1:
                temporal_analysis['trends'] = self._calculate_temporal_trends(temporal_analysis['evolution_metrics'])

            return temporal_analysis

        except Exception as e:
            return {'error': f'Temporal analysis failed: {str(e)}'}

    def _calculate_temporal_trends(self, evolution_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate trends in temporal network evolution."""
        trends = {}

        try:
            # Extract metric values over time
            densities = [m['metrics'].get('density', 0) for m in evolution_metrics]
            avg_degrees = [m['metrics'].get('average_degree', 0) for m in evolution_metrics]

            # Calculate trends
            trends['density_trend'] = np.polyfit(range(len(densities)), densities, 1)[0]
            trends['degree_trend'] = np.polyfit(range(len(avg_degrees)), avg_degrees, 1)[0]

            # Volatility measures
            trends['density_volatility'] = np.std(densities)
            trends['degree_volatility'] = np.std(avg_degrees)

        except Exception as e:
            trends['error'] = f'Trend calculation failed: {str(e)}'

        return trends
