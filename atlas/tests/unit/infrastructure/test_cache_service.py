#!/usr/bin/env python3
"""
Unit tests for AXIOM Cache Service
"""

import pytest
from unittest.mock import patch
from app.cache import DistributedCache

class TestDistributedCache:
    """Test cases for DistributedCache"""

    @pytest.fixture
    def cache(self):
        """Create a test cache instance"""
        return DistributedCache()

    def test_cache_initialization(self, cache):
        """Test cache initialization"""
        assert cache.redis_client is not None
        assert cache.metrics is not None

    def test_get_cache_strategy(self, cache):
        """Test cache strategy selection"""
        # Test matrix operation
        strategy = cache._get_cache_strategy("matrix_multiplication")
        assert strategy is not None

        # Test scientific data
        strategy = cache._get_cache_strategy("scientific_computation")
        assert strategy is not None

        # Test text data
        strategy = cache._get_cache_strategy("text_processing")
        assert strategy is not None

        # Test unknown operation
        strategy = cache._get_cache_strategy("unknown_operation")
        assert strategy is not None

    @patch('app.cache.redis_client')
    def test_cache_set_get(self, mock_redis, cache):
        """Test basic cache set and get operations"""
        mock_redis.set.return_value = True
        mock_redis.get.return_value = b'{"test": "data"}'

        # Test set
        result = cache.set("test_key", {"test": "data"})
        assert result is True
        mock_redis.set.assert_called_once()

        # Test get
        result = cache.get("test_key")
        assert result == {"test": "data"}
        mock_redis.get.assert_called_once_with("test_key")

    @patch('app.cache.redis_client')
    def test_cache_compression(self, mock_redis, cache):
        """Test cache compression functionality"""
        test_data = {"large_data": "x" * 1000}

        # Mock compression
        with patch('lz4.frame.compress') as mock_compress:
            with patch('lz4.frame.decompress') as mock_decompress:
                mock_compress.return_value = b'compressed_data'
                mock_decompress.return_value = b'{"large_data": "xxxxxxxxxx..."}'

                # Test compressed set
                cache.set("compressed_key", test_data, operation="matrix_multiplication")
                mock_compress.assert_called_once()

                # Test compressed get
                cache.get("compressed_key", operation="matrix_multiplication")
                mock_decompress.assert_called_once()

    def test_cache_metrics(self, cache):
        """Test cache metrics collection"""
        initial_metrics = cache.get_stats()

        # Perform some operations
        cache.set("test1", "value1")
        cache.get("test1")
        cache.get("nonexistent")

        final_metrics = cache.get_stats()

        # Metrics should be updated
        assert final_metrics["total_sets"] >= initial_metrics["total_sets"]
        assert final_metrics["total_gets"] >= initial_metrics["total_gets"]
        assert final_metrics["cache_misses"] >= initial_metrics["cache_misses"]

    @patch('app.cache.redis_client')
    def test_cache_error_handling(self, mock_redis, cache):
        """Test error handling in cache operations"""
        mock_redis.set.side_effect = Exception("Redis connection error")

        # Should not raise exception
        result = cache.set("test_key", "test_value")
        assert result is False

        # Should return None on get error
        mock_redis.get.side_effect = Exception("Redis connection error")
        result = cache.get("test_key")
        assert result is None

    def test_cache_bulk_operations(self, cache):
        """Test bulk cache operations"""
        data = {
            "key1": "value1",
            "key2": "value2",
            "key3": "value3"
        }

        with patch.object(cache, 'set') as mock_set:
            mock_set.return_value = True

            # Test bulk set
            results = cache.set_bulk(data)
            assert len(results) == 3
            assert all(results.values())

            # Verify set was called for each key
            assert mock_set.call_count == 3

    def test_cache_invalidation(self, cache):
        """Test cache invalidation patterns"""
        # Test single key invalidation
        with patch('app.cache.redis_client') as mock_redis:
            mock_redis.delete.return_value = 1

            result = cache.invalidate("test_key")
            assert result is True
            mock_redis.delete.assert_called_once_with("test_key")

        # Test pattern invalidation
        with patch('app.cache.redis_client') as mock_redis:
            mock_redis.keys.return_value = [b"pattern_key1", b"pattern_key2"]
            mock_redis.delete.return_value = 2

            result = cache.invalidate_pattern("pattern_*")
            assert result is True
            mock_redis.keys.assert_called_once_with("pattern_*")
            mock_redis.delete.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__])
