"""
Unit tests for Graph Theory Service
Tests all graph algorithms and visualization functionality
"""

import pytest
from unittest.mock import patch, MagicMock
from app.services.graph_theory import (
    find_shortest_path,
    calculate_maximum_flow,
    detect_communities,
    calculate_centrality,
    visualize_graph
)


class TestGraphTheoryService:
    """Test suite for graph theory service functions"""

    def test_find_shortest_path_simple_graph(self):
        """Test finding shortest path in a simple undirected graph"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('A', 'D')]

        result = find_shortest_path(nodes, edges, 'A', 'C')

        assert isinstance(result, list)
        assert result == ['A', 'B', 'C'] or result == ['A', 'D', 'C']

    def test_find_shortest_path_weighted_graph(self):
        """Test finding shortest path in a weighted graph"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B', 1), ('B', 'C', 2), ('C', 'D', 1), ('A', 'D', 4)]

        result = find_shortest_path(nodes, edges, 'A', 'D')

        assert isinstance(result, list)
        assert result == ['A', 'D']  # Shortest path by weight: A-D (4) vs A-B-C-D (1+2+1=4)

    def test_find_shortest_path_no_path(self):
        """Test finding shortest path when no path exists"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('C', 'D')]  # No connection between A-B and C-D

        result = find_shortest_path(nodes, edges, 'A', 'D')

        assert isinstance(result, dict)
        assert "error" in result
        assert "No path found" in result["error"]

    def test_find_shortest_path_node_not_found(self):
        """Test finding shortest path with non-existent node"""
        nodes = ['A', 'B', 'C']
        edges = [('A', 'B'), ('B', 'C')]

        result = find_shortest_path(nodes, edges, 'A', 'Z')

        assert isinstance(result, dict)
        assert "error" in result

    def test_calculate_maximum_flow_simple(self):
        """Test maximum flow calculation in a simple directed graph"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B', 10), ('B', 'C', 5), ('C', 'D', 10), ('A', 'C', 5)]

        result = calculate_maximum_flow(nodes, edges, 'A', 'D')

        assert isinstance(result, dict)
        assert "maximum_flow" in result
        assert isinstance(result["maximum_flow"], dict)

    def test_calculate_maximum_flow_no_path(self):
        """Test maximum flow when no path exists"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B', 10), ('C', 'D', 10)]  # No path from A to D

        result = calculate_maximum_flow(nodes, edges, 'A', 'D')

        assert isinstance(result, dict)
        assert "maximum_flow" in result
        # When no path exists, flow should be 0
        assert result["maximum_flow"] == {'A': {'B': 0}, 'B': {}, 'C': {'D': 0}, 'D': {}}

    def test_calculate_maximum_flow_invalid_capacity(self):
        """Test maximum flow with edges without capacity (should default to 1)"""
        nodes = ['A', 'B', 'C']
        edges = [('A', 'B'), ('B', 'C')]  # Missing capacity, should default to 1

        result = calculate_maximum_flow(nodes, edges, 'A', 'C')

        assert isinstance(result, dict)
        assert "maximum_flow" in result
        # Should work with default capacity of 1
        assert 'A' in result["maximum_flow"]

    def test_detect_communities_simple_graph(self):
        """Test community detection in a simple graph"""
        nodes = ['A', 'B', 'C', 'D', 'E', 'F']
        edges = [('A', 'B'), ('B', 'C'), ('D', 'E'), ('E', 'F'), ('C', 'D')]

        result = detect_communities(nodes, edges)

        assert isinstance(result, list)
        assert len(result) > 0
        # Each community should be a list of nodes
        for community in result:
            assert isinstance(community, list)

    def test_detect_communities_disconnected_graph(self):
        """Test community detection in a disconnected graph"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('C', 'D')]  # Two separate components

        result = detect_communities(nodes, edges)

        assert isinstance(result, list)
        assert len(result) >= 2  # At least two communities

    def test_detect_communities_empty_graph(self):
        """Test community detection in an empty graph"""
        nodes = []
        edges = []

        result = detect_communities(nodes, edges)

        assert isinstance(result, list)
        assert len(result) == 0

    def test_calculate_centrality_simple_graph(self):
        """Test centrality calculation in a simple graph"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('A', 'C')]

        result = calculate_centrality(nodes, edges)

        assert isinstance(result, dict)
        assert len(result) == 4  # All nodes should have centrality values
        assert all(isinstance(v, float) for v in result.values())
        assert all(0 <= v <= 1 for v in result.values())  # Centrality should be between 0 and 1

    def test_calculate_centrality_star_graph(self):
        """Test centrality calculation in a star graph"""
        nodes = ['center', 'A', 'B', 'C', 'D']
        edges = [('center', 'A'), ('center', 'B'), ('center', 'C'), ('center', 'D')]

        result = calculate_centrality(nodes, edges)

        assert isinstance(result, dict)
        assert result['center'] == 1.0  # Center node should have maximum centrality
        assert all(result[node] == 0.25 for node in ['A', 'B', 'C', 'D'])  # Leaf nodes equal centrality

    def test_calculate_centrality_empty_graph(self):
        """Test centrality calculation in an empty graph"""
        nodes = []
        edges = []

        result = calculate_centrality(nodes, edges)

        assert isinstance(result, dict)
        assert len(result) == 0

    def test_visualize_graph_simple(self):
        """Test graph visualization with simple graph"""
        nodes = ['A', 'B', 'C']
        edges = [('A', 'B'), ('B', 'C')]

        with patch('app.services.graph_theory.os.makedirs'), \
             patch('app.services.graph_theory.os.path.join') as mock_join, \
             patch('app.services.graph_theory.hashlib.sha256') as mock_sha256, \
             patch('app.services.graph_theory.Network') as mock_network:

            mock_join.return_value = '/tmp/test_graph.html'
            mock_sha256.return_value.hexdigest.return_value = 'abcd1234'

            mock_net = MagicMock()
            mock_network.return_value = mock_net
            mock_net.save_graph.return_value = None

            result = visualize_graph(nodes, edges, "basic")

            assert isinstance(result, str)
            assert "graph_visualization" in result
            assert result.endswith('.html')

            # Verify Network was created and configured
            mock_network.assert_called_once()
            mock_net.from_nx.assert_called_once()
            mock_net.set_options.assert_called_once()
            mock_net.save_graph.assert_called_once()

    def test_visualize_graph_with_shortest_path(self):
        """Test graph visualization highlighting shortest path"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D')]

        with patch('app.services.graph_theory.os.makedirs'), \
             patch('app.services.graph_theory.os.path.join') as mock_join, \
             patch('app.services.graph_theory.hashlib.sha256') as mock_sha256, \
             patch('app.services.graph_theory.Network') as mock_network:

            mock_join.return_value = '/tmp/test_graph.html'
            mock_sha256.return_value.hexdigest.return_value = 'abcd1234'

            mock_net = MagicMock()
            mock_network.return_value = mock_net
            mock_net.save_graph.return_value = None
            mock_net.get_node.return_value = {'color': 'blue', 'size': 25}

            result = visualize_graph(nodes, edges, "shortest_path", "A", "D")

            assert isinstance(result, str)
            assert "graph_visualization" in result

            # Verify path highlighting was attempted
            mock_net.get_node.assert_called()

    def test_visualize_graph_error_handling(self):
        """Test graph visualization error handling"""
        nodes = ['A', 'B']
        edges = [('A', 'B')]

        with patch('app.services.graph_theory.os.makedirs'), \
             patch('app.services.graph_theory.os.path.join') as mock_join, \
             patch('app.services.graph_theory.hashlib.sha256') as mock_sha256, \
             patch('app.services.graph_theory.Network') as mock_network:

            mock_join.return_value = '/tmp/test_graph.html'
            mock_sha256.return_value.hexdigest.return_value = 'abcd1234'

            mock_net = MagicMock()
            mock_network.return_value = mock_net
            # Mock save_graph to raise an exception that will be caught
            mock_net.save_graph.side_effect = OSError("File system error")

            result = visualize_graph(nodes, edges, "basic")

            assert isinstance(result, dict)
            assert "error" in result
            assert "Graph visualization failed" in result["error"]

    def test_visualize_graph_empty_graph(self):
        """Test graph visualization with empty graph"""
        nodes = []
        edges = []

        with patch('app.services.graph_theory.os.makedirs'), \
             patch('app.services.graph_theory.os.path.join') as mock_join, \
             patch('app.services.graph_theory.hashlib.sha256') as mock_sha256, \
             patch('app.services.graph_theory.Network') as mock_network:

            mock_join.return_value = '/tmp/test_graph.html'
            mock_sha256.return_value.hexdigest.return_value = 'abcd1234'

            mock_net = MagicMock()
            mock_network.return_value = mock_net
            mock_net.save_graph.return_value = None

            result = visualize_graph(nodes, edges, "basic")

            assert isinstance(result, str)
            mock_net.from_nx.assert_called_once()

    def test_integration_shortest_path_and_visualization(self):
        """Integration test combining shortest path and visualization"""
        nodes = ['A', 'B', 'C', 'D']
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D')]

        # First find the path
        path = find_shortest_path(nodes, edges, 'A', 'D')
        assert isinstance(path, list)
        assert path == ['A', 'B', 'C', 'D']

        # Then visualize (mocked)
        with patch('app.services.graph_theory.os.makedirs'), \
             patch('app.services.graph_theory.os.path.join') as mock_join, \
             patch('app.services.graph_theory.hashlib.sha256') as mock_sha256, \
             patch('app.services.graph_theory.Network') as mock_network:

            mock_join.return_value = '/tmp/test_graph.html'
            mock_sha256.return_value.hexdigest.return_value = 'abcd1234'

            mock_net = MagicMock()
            mock_network.return_value = mock_net

            result = visualize_graph(nodes, edges, "shortest_path", 'A', 'D')

            assert isinstance(result, str)
            mock_net.get_node.assert_called()

    def test_error_handling_invalid_inputs(self):
        """Test error handling with various invalid inputs"""

        # Test with None inputs
        result = find_shortest_path(None, None, None, None)
        assert isinstance(result, dict)
        assert "error" in result

        result = calculate_maximum_flow(None, None, None, None)
        assert isinstance(result, dict)
        assert "error" in result

        result = detect_communities(None, None)
        assert isinstance(result, list)  # Should handle gracefully and return empty list

        result = calculate_centrality(None, None)
        assert isinstance(result, dict)  # Should handle gracefully and return empty dict

        # Test visualization with invalid operation
        with patch('app.services.graph_theory.os.makedirs'), \
             patch('app.services.graph_theory.os.path.join') as mock_join, \
             patch('app.services.graph_theory.hashlib.sha256') as mock_sha256, \
             patch('app.services.graph_theory.Network') as mock_network:

            mock_join.return_value = '/tmp/test_graph.html'
            mock_sha256.return_value.hexdigest.return_value = 'abcd1234'

            mock_net = MagicMock()
            mock_network.return_value = mock_net

            result = visualize_graph(['A'], [('A', 'B')], "invalid_operation")
            assert isinstance(result, str)  # Should still work
