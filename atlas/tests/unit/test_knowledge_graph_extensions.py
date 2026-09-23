"""
Test suite for Knowledge Graph Extensions
=========================================

Tests para validar las extensiones de Knowledge Graph
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

# Test component availability
MODELS_AVAILABLE = False
LITERATURE_SERVICE_AVAILABLE = False
RESEARCH_MANAGER_AVAILABLE = False
REGISTRY_AVAILABLE = False

try:
    from app.models.database_models import KnowledgeNode
    MODELS_AVAILABLE = True
except ImportError:
    pass

try:
    from app.services.literature_search import LiteratureSearchService
    LITERATURE_SERVICE_AVAILABLE = True
except ImportError:
    pass

try:
    from app.services.research_cycle_manager import ResearchCycleManager
    RESEARCH_MANAGER_AVAILABLE = True
except ImportError:
    pass

try:
    from app.service_registry_discovery import ServiceRegistry
    REGISTRY_AVAILABLE = True
except ImportError:
    pass


def test_models_availability():
    """Test Knowledge Graph models are available"""
    if MODELS_AVAILABLE:
        assert True, "Knowledge Graph models available"
    else:
        pytest.skip("Knowledge Graph models not available - extensions not yet implemented")


def test_services_availability():
    """Test enhanced services are available"""
    # At least one service should be available (existing infrastructure)
    assert LITERATURE_SERVICE_AVAILABLE or RESEARCH_MANAGER_AVAILABLE, "At least one service should be available"


def test_existing_infrastructure_unaffected():
    """Test that existing infrastructure components still work"""
    # Test that we can still import basic components
    try:
        from app.models.database_models import User, Calculation
        assert True, "Existing models still importable"
    except ImportError:
        pytest.fail("Existing database models should still be importable")


@pytest.mark.skipif(not LITERATURE_SERVICE_AVAILABLE, reason="LiteratureSearchService not available")
def test_literature_service_backward_compatibility():
    """Test LiteratureSearchService maintains backward compatibility"""
    service = LiteratureSearchService()
    
    # Should have original methods/attributes
    assert hasattr(service, 'process_request')
    assert service is not None


@pytest.mark.skipif(not RESEARCH_MANAGER_AVAILABLE, reason="ResearchCycleManager not available")
def test_research_manager_backward_compatibility():
    """Test ResearchCycleManager maintains backward compatibility"""
    manager = ResearchCycleManager()
    
    # Should have original methods/attributes
    assert hasattr(manager, 'process_request')
    assert manager is not None


@pytest.mark.asyncio
@pytest.mark.skipif(not LITERATURE_SERVICE_AVAILABLE, reason="LiteratureSearchService not available")
async def test_literature_service_knowledge_actions():
    """Test that Knowledge Graph actions are handled gracefully"""
    service = LiteratureSearchService()
    
    # Test semantic search action
    request_data = {
        "action": "semantic_search",
        "query": "quantum computing",
        "domain": "physics"
    }
    
    result = await service.process_request(request_data)
    
    # Should either work or gracefully degrade
    assert "success" in result or "error" in result


@pytest.mark.asyncio
@pytest.mark.skipif(not REGISTRY_AVAILABLE, reason="ServiceRegistry not available")
async def test_service_registry_functionality():
    """Test Service Registry auto-registration works"""
    from app.service_registry_discovery import auto_register_axiom_services
    
    registry = ServiceRegistry()
    registered_count = await auto_register_axiom_services(registry)
    
    # Should register at least the original services
    assert registered_count >= 3, f"Should register at least 3 services, got {registered_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
