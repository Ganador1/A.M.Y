"""
Unit tests for Knowledge Graph Service

Tests covering:
- Knowledge node CRUD operations
- Knowledge relation management
- Graph search and analysis
- Subgraph extraction
- Statistics calculation

Author: AXIOM Development Team
Date: September 12, 2025
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock

from app.services.knowledge_graph_service import KnowledgeGraphService
from app.models.database_models import KnowledgeNode, KnowledgeRelation


class TestKnowledgeGraphService:
    """Test suite for Knowledge Graph Service functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.kg_service = KnowledgeGraphService()

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service proper initialization"""
        assert self.kg_service.name == "KnowledgeGraph"
        assert self.kg_service.version == "1.0.0"
        assert isinstance(self.kg_service.valid_node_types, list)
        assert isinstance(self.kg_service.valid_relation_types, list)
        assert "hypothesis" in self.kg_service.valid_node_types
        assert "supports" in self.kg_service.valid_relation_types

    @pytest.mark.asyncio
    async def test_create_knowledge_node_success(self):
        """Test successful knowledge node creation"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock no existing node
            mock_session.query.return_value.filter.return_value.first.return_value = None
            
            # Mock new node
            mock_node = Mock()
            mock_node.id = 1
            mock_node.name = "Test Hypothesis"
            mock_node.concept_type = "hypothesis"
            mock_node.domain = "physics"
            mock_node.confidence_score = 0.8
            mock_node.is_validated = False
            
            mock_session.refresh = Mock()
            mock_session.refresh.side_effect = lambda node: setattr(node, 'id', 1)

            request_data = {
                "name": "Test Hypothesis",
                "type": "hypothesis",
                "domain": "physics",
                "confidence_score": 0.8,
                "properties": {"description": "Test hypothesis for quantum mechanics"}
            }

            result = await self.kg_service.create_knowledge_node(request_data)

            assert result["success"] is True
            assert result["node_id"] == 1
            assert result["node"]["name"] == "Test Hypothesis"
            assert result["node"]["type"] == "hypothesis"
            assert result["node"]["domain"] == "physics"
            
            # Verify database interactions
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_knowledge_node_duplicate(self):
        """Test creation fails when node already exists"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock existing node
            existing_node = Mock()
            existing_node.name = "Test Hypothesis"
            mock_session.query.return_value.filter.return_value.first.return_value = existing_node

            request_data = {
                "name": "Test Hypothesis",
                "type": "hypothesis",
                "domain": "physics"
            }

            result = await self.kg_service.create_knowledge_node(request_data)

            assert result["success"] is False
            assert "already exists" in result["error"]
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_knowledge_node_invalid_type(self):
        """Test creation fails with invalid node type"""
        request_data = {
            "name": "Test Node",
            "type": "invalid_type",
            "domain": "physics"
        }

        result = await self.kg_service.create_knowledge_node(request_data)

        assert result["success"] is False
        assert "Invalid node type" in result["error"]

    @pytest.mark.asyncio
    async def test_get_knowledge_node_success(self):
        """Test successful knowledge node retrieval"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock found node
            mock_node = Mock()
            mock_node.id = 1
            mock_node.name = "Test Hypothesis"
            mock_node.concept_type = "hypothesis"
            mock_node.domain = "physics"
            mock_node.properties = {"description": "Test"}
            mock_node.confidence_score = 0.8
            mock_node.source_papers = []
            mock_node.created_by = "test_user"
            mock_node.is_validated = False
            mock_node.validation_count = 0
            mock_node.outgoing_relations = []
            mock_node.incoming_relations = []
            
            mock_query = Mock()
            mock_session.query.return_value = mock_query
            mock_query.options.return_value.filter.return_value.first.return_value = mock_node

            request_data = {"node_id": 1}

            result = await self.kg_service.get_knowledge_node(request_data)

            assert result["success"] is True
            assert result["node"]["id"] == 1
            assert result["node"]["name"] == "Test Hypothesis"
            assert result["node"]["type"] == "hypothesis"
            assert result["node"]["domain"] == "physics"
            assert "outgoing_relations" in result["node"]
            assert "incoming_relations" in result["node"]
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_knowledge_node_not_found(self):
        """Test retrieval fails when node doesn't exist"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock not found
            mock_query = Mock()
            mock_session.query.return_value = mock_query
            mock_query.options.return_value.filter.return_value.first.return_value = None

            request_data = {"node_id": 999}

            result = await self.kg_service.get_knowledge_node(request_data)

            assert result["success"] is False
            assert "not found" in result["error"]
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_search_knowledge_nodes_success(self):
        """Test successful knowledge node search"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock found nodes
            mock_node1 = Mock()
            mock_node1.id = 1
            mock_node1.name = "Quantum Hypothesis"
            mock_node1.concept_type = "hypothesis"
            mock_node1.domain = "physics"
            mock_node1.confidence_score = 0.9
            mock_node1.is_validated = True
            mock_node1.validation_count = 3
            
            mock_node2 = Mock()
            mock_node2.id = 2
            mock_node2.name = "Quantum Method"
            mock_node2.concept_type = "method"
            mock_node2.domain = "physics"
            mock_node2.confidence_score = 0.7
            mock_node2.is_validated = False
            mock_node2.validation_count = 1

            mock_query = Mock()
            mock_session.query.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.count.return_value = 2
            mock_query.offset.return_value.limit.return_value.all.return_value = [mock_node1, mock_node2]

            request_data = {
                "query": "quantum",
                "domain": "physics",
                "limit": 10,
                "offset": 0
            }

            result = await self.kg_service.search_knowledge_nodes(request_data)

            assert result["success"] is True
            assert result["total_count"] == 2
            assert result["returned_count"] == 2
            assert len(result["nodes"]) == 2
            assert result["nodes"][0]["id"] == 1
            assert result["nodes"][1]["id"] == 2
            assert result["has_more"] is False
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_knowledge_relation_success(self):
        """Test successful knowledge relation creation"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock subject and object nodes
            subject_node = Mock()
            subject_node.id = 1
            subject_node.name = "Subject Node"
            
            object_node = Mock()
            object_node.id = 2
            object_node.name = "Object Node"
            
            mock_session.query.return_value.filter.side_effect = [
                Mock(first=Mock(return_value=subject_node)),  # subject node query
                Mock(first=Mock(return_value=object_node)),   # object node query
                Mock(first=Mock(return_value=None))           # no existing relation
            ]
            
            # Mock new relation
            mock_relation = Mock()
            mock_relation.id = 1
            mock_relation.subject_id = 1
            mock_relation.object_id = 2
            mock_relation.predicate = "supports"
            mock_relation.strength = 0.8
            mock_relation.is_bidirectional = False
            
            mock_session.refresh = Mock()
            mock_session.refresh.side_effect = lambda rel: setattr(rel, 'id', 1)

            request_data = {
                "subject_id": 1,
                "object_id": 2,
                "predicate": "supports",
                "strength": 0.8
            }

            result = await self.kg_service.create_knowledge_relation(request_data)

            assert result["success"] is True
            assert result["relation_id"] == 1
            assert result["relation"]["subject_id"] == 1
            assert result["relation"]["object_id"] == 2
            assert result["relation"]["predicate"] == "supports"
            assert result["relation"]["strength"] == 0.8
            
            mock_session.add.assert_called_once()
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_knowledge_relation_invalid_predicate(self):
        """Test relation creation fails with invalid predicate"""
        request_data = {
            "subject_id": 1,
            "object_id": 2,
            "predicate": "invalid_predicate",
            "strength": 0.8
        }

        result = await self.kg_service.create_knowledge_relation(request_data)

        assert result["success"] is False
        assert "Invalid predicate" in result["error"]

    @pytest.mark.asyncio
    async def test_get_subgraph_success(self):
        """Test successful subgraph extraction"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock root node
            root_node = Mock()
            root_node.id = 1
            root_node.name = "Root Node"
            
            # Mock nodes in subgraph
            node1 = Mock()
            node1.id = 1
            node1.name = "Root Node"
            node1.concept_type = "hypothesis"
            node1.domain = "physics"
            node1.confidence_score = 0.9
            
            node2 = Mock()
            node2.id = 2
            node2.name = "Connected Node"
            node2.concept_type = "method"
            node2.domain = "physics"
            node2.confidence_score = 0.8
            
            # Mock relation
            relation = Mock()
            relation.id = 1
            relation.subject_id = 1
            relation.object_id = 2
            relation.predicate = "supports"
            relation.strength = 0.8
            relation.is_bidirectional = False
            
            # Set up query mocks
            mock_session.query.side_effect = [
                Mock(filter=Mock(return_value=Mock(first=Mock(return_value=root_node)))),  # root node
                Mock(filter=Mock(return_value=Mock(first=Mock(return_value=node1)))),      # node 1
                Mock(filter=Mock(return_value=Mock(all=Mock(return_value=[relation])))),   # relations
                Mock(filter=Mock(return_value=Mock(first=Mock(return_value=node2)))),      # node 2
                Mock(filter=Mock(return_value=Mock(all=Mock(return_value=[]))))            # no more relations
            ]

            request_data = {
                "root_node_id": 1,
                "max_depth": 2,
                "min_strength": 0.1
            }

            result = await self.kg_service.get_subgraph(request_data)

            assert result["success"] is True
            assert result["subgraph"]["root_node_id"] == 1
            assert result["subgraph"]["root_node_name"] == "Root Node"
            assert result["subgraph"]["max_depth"] == 2
            assert "nodes" in result["subgraph"]
            assert "relations" in result["subgraph"]
            assert "metrics" in result["subgraph"]
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_graph_statistics_success(self):
        """Test successful graph statistics calculation"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            mock_session = Mock()
            mock_get_db.return_value = mock_session
            
            # Mock statistics queries
            mock_session.query.side_effect = [
                Mock(count=Mock(return_value=100)),  # total nodes
                Mock(filter=Mock(return_value=Mock(count=Mock(return_value=75)))),  # validated nodes
                Mock(count=Mock(return_value=150)),  # total relations
                Mock(scalar=Mock(return_value=0.85)),  # avg confidence
                Mock(scalar=Mock(return_value=0.2)),   # min confidence
                Mock(scalar=Mock(return_value=1.0))    # max confidence
            ]

            request_data = {}

            result = await self.kg_service.get_graph_statistics(request_data)

            assert result["success"] is True
            assert "statistics" in result
            stats = result["statistics"]
            assert stats["total_nodes"] == 100
            assert stats["validated_nodes"] == 75
            assert stats["total_relations"] == 150
            assert stats["avg_confidence_score"] == 0.85
            assert stats["min_confidence_score"] == 0.2
            assert stats["max_confidence_score"] == 1.0
            assert "validation_percentage" in stats
            assert "graph_density" in stats
            assert "generated_at" in result
            
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_request_invalid_action(self):
        """Test process_request with invalid action"""
        request_data = {"action": "invalid_action"}
        
        result = await self.kg_service.process_request(request_data)
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
        assert "available_actions" in result

    @pytest.mark.asyncio
    async def test_bidirectional_predicate_helper(self):
        """Test bidirectional predicate helper function"""
        assert self.kg_service._is_bidirectional_predicate("similar_to") is True
        assert self.kg_service._is_bidirectional_predicate("supports") is False
        assert self.kg_service._is_bidirectional_predicate("related_to") is True
        assert self.kg_service._is_bidirectional_predicate("derives_from") is False

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in service methods"""
        with patch('app.services.knowledge_graph_service.get_db_session') as mock_get_db:
            # Mock database error
            mock_get_db.side_effect = Exception("Database connection error")

            request_data = {"name": "Test Node", "type": "hypothesis"}
            
            result = await self.kg_service.create_knowledge_node(request_data)
            
            assert result["success"] is False
            assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__])
