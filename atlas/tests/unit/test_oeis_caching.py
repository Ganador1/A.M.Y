"""
Tests for OEIS caching functionality
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.cache import cache

client = TestClient(app)


def test_oeis_cache_key_generation():
    """Test that cache keys are generated consistently"""
    from app.routers.sequence_oeis import _generate_cache_key
    
    # Test with same inputs produces same key
    terms1 = [1, 2, 3, 4, 5]
    terms2 = [1, 2, 3, 4, 5]
    
    key1 = _generate_cache_key(terms1, 5)
    key2 = _generate_cache_key(terms2, 5)
    
    assert key1 == key2
    
    # Test different inputs produce different keys
    terms3 = [1, 2, 3, 4, 6]
    key3 = _generate_cache_key(terms3, 5)
    
    assert key1 != key3


def test_cache_ttl_strategy():
    """Test intelligent TTL strategy based on results"""
    from app.routers.sequence_oeis import _get_cache_ttl_based_on_results
    
    # Test no results - shorter TTL
    no_results = []
    ttl_no_results = _get_cache_ttl_based_on_results(no_results)
    assert ttl_no_results == 3600  # 1 hour
    
    # Test good results - longer TTL
    good_results = [
        {"id": "A000001", "name": "Test sequence", "data_sample": "1,2,3"}
    ]
    ttl_good = _get_cache_ttl_based_on_results(good_results)
    assert ttl_good == 86400  # 24 hours
    
    # Test mixed results - medium TTL
    mixed_results = [
        {"name": "Test sequence"}  # Missing id
    ]
    ttl_mixed = _get_cache_ttl_based_on_results(mixed_results)
    assert ttl_mixed == 21600  # 6 hours


@patch('app.routers.sequence_oeis.aiohttp.ClientSession')
async def test_oeis_search_caching(mock_session_class):
    """Test that OEIS search results are properly cached"""
    
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        "results": [
            {
                "number": "A000001",
                "name": "Test sequence",
                "data": "1, 2, 3, 4, 5",
                "formula": "a(n) = n",
                "comment": ["Test comment"]
            }
        ]
    })
    
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session_class.return_value = mock_session
    
    # Clear cache before test
    cache.clear("oeis_search:*")
    
    # First request - should hit API
    response1 = client.post("/api/sequences/oeis/search", json={
        "terms": [1, 2, 3, 4, 5],
        "max_results": 5
    })
    
    assert response1.status_code == 200
    assert response1.json()["cached"] == False
    
    # Second request - should hit cache
    response2 = client.post("/api/sequences/oeis/search", json={
        "terms": [1, 2, 3, 4, 5],
        "max_results": 5
    })
    
    assert response2.status_code == 200
    assert response2.json()["cached"] == True
    
    # Verify cache stats
    stats = cache.get_stats()
    assert stats["cache_hits"] >= 1


@patch('app.routers.sequence_oeis.aiohttp.ClientSession')
async def test_oeis_cache_different_parameters(mock_session_class):
    """Test that different search parameters produce different cache keys"""
    
    # Mock the HTTP response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"results": []})
    
    mock_session = AsyncMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = AsyncMock(return_value=mock_response)
    mock_session_class.return_value = mock_session
    
    # Clear cache
    cache.clear("oeis_search:*")
    
    # First search
    response1 = client.post("/api/sequences/oeis/search", json={
        "terms": [1, 2, 3],
        "max_results": 3
    })
    
    # Different search
    response2 = client.post("/api/sequences/oeis/search", json={
        "terms": [1, 2, 3, 4],
        "max_results": 3
    })
    
    # Same search as first but different max_results
    response3 = client.post("/api/sequences/oeis/search", json={
        "terms": [1, 2, 3],
        "max_results": 5
    })
    
    # All should be cache misses (not cached yet)
    assert response1.json()["cached"] == False
    assert response2.json()["cached"] == False  
    assert response3.json()["cached"] == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])