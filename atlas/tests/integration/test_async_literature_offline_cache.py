"""
Integration tests for Literature Offline Cache Service (Async)

Tests the async version of LiteratureOfflineCache with aiosqlite.
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from app.services.literature_offline_cache import (
    LiteratureOfflineCache,
    cache_paper,
    get_cached_paper,
    get_literature_cache,
)


@pytest.fixture
async def temp_cache_dir():
    """Create a temporary cache directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
async def cache(temp_cache_dir):
    """Create a test cache instance"""
    return LiteratureOfflineCache(cache_dir=temp_cache_dir)


@pytest.mark.asyncio
class TestAsyncLiteratureOfflineCache:
    """Test suite for async literature offline cache operations"""

    async def test_put_and_get_basic(self, cache):
        """Test basic put and get operations"""
        key = "test_paper_1"
        content = {"title": "Test Paper", "abstract": "This is a test", "authors": ["Alice", "Bob"]}
        metadata = {"source": "arxiv", "year": 2024}

        # Put content
        result = await cache.put(key, content, metadata)
        assert result is True

        # Get content
        retrieved = await cache.get(key)
        assert retrieved is not None
        assert retrieved["title"] == "Test Paper"
        assert len(retrieved["authors"]) == 2

    async def test_get_nonexistent_key(self, cache):
        """Test getting a key that doesn't exist"""
        result = await cache.get("nonexistent_key")
        assert result is None

    async def test_put_with_ttl_not_expired(self, cache):
        """Test putting content with TTL that hasn't expired"""
        key = "test_ttl_valid"
        content = {"data": "test"}
        ttl = 10  # 10 seconds

        await cache.put(key, content, ttl=ttl)
        retrieved = await cache.get(key)

        assert retrieved is not None
        assert retrieved["data"] == "test"

    async def test_put_with_ttl_expired(self, cache):
        """Test putting content with TTL that has expired"""
        key = "test_ttl_expired"
        content = {"data": "test"}
        ttl = -1  # Already expired

        await cache.put(key, content, ttl=ttl)

        # Wait a bit to ensure expiration check happens
        await asyncio.sleep(0.1)

        retrieved = await cache.get(key)
        assert retrieved is None  # Should be deleted due to expiration

    async def test_get_metadata(self, cache):
        """Test getting metadata for a cached entry"""
        key = "test_metadata"
        content = {"data": "test"}
        metadata = {"source": "test_source", "type": "paper"}

        await cache.put(key, content, metadata)
        meta = await cache.get_metadata(key)

        assert meta is not None
        assert meta["metadata"]["source"] == "test_source"
        assert meta["metadata"]["type"] == "paper"
        assert "created_at" in meta
        assert "access_count" in meta
        assert meta["access_count"] == 0  # Not accessed yet

    async def test_exists(self, cache):
        """Test checking if a key exists"""
        key = "test_exists"
        content = {"data": "test"}

        # Should not exist initially
        exists_before = await cache.exists(key)
        assert exists_before is False

        # Put content
        await cache.put(key, content)

        # Should exist now
        exists_after = await cache.exists(key)
        assert exists_after is True

    async def test_delete(self, cache):
        """Test deleting an entry"""
        key = "test_delete"
        content = {"data": "test"}

        # Put content
        await cache.put(key, content)
        assert await cache.exists(key) is True

        # Delete
        deleted = await cache.delete(key)
        assert deleted is True

        # Should not exist anymore
        assert await cache.exists(key) is False

        # Deleting again should return False
        deleted_again = await cache.delete(key)
        assert deleted_again is False

    async def test_clear_expired(self, cache):
        """Test clearing expired entries"""
        # Put some entries with different TTLs
        await cache.put("valid_1", {"data": "test1"}, ttl=100)
        await cache.put("valid_2", {"data": "test2"}, ttl=100)
        await cache.put("expired_1", {"data": "test3"}, ttl=-1)
        await cache.put("expired_2", {"data": "test4"}, ttl=-1)

        # Clear expired
        cleared_count = await cache.clear_expired()

        assert cleared_count == 2

        # Valid entries should still exist
        assert await cache.exists("valid_1") is True
        assert await cache.exists("valid_2") is True

        # Expired entries should be gone
        assert await cache.exists("expired_1") is False
        assert await cache.exists("expired_2") is False

    async def test_get_stats(self, cache):
        """Test getting cache statistics"""
        # Put some entries
        await cache.put("stats_1", {"data": "test1"}, metadata={"size": 100})
        await cache.put("stats_2", {"data": "test2"}, metadata={"size": 200})
        await cache.put("stats_3", {"data": "test3"}, ttl=-1)  # Expired

        stats = await cache.get_stats()

        assert stats["total_entries"] == 3
        assert stats["total_size_bytes"] > 0
        assert stats["expired_entries"] == 1

    async def test_list_keys_all(self, cache):
        """Test listing all cache keys"""
        # Put some entries
        await cache.put("paper_1", {"data": "test1"})
        await cache.put("paper_2", {"data": "test2"})
        await cache.put("article_1", {"data": "test3"})

        keys = await cache.list_keys()

        assert len(keys) == 3
        assert "paper_1" in keys
        assert "paper_2" in keys
        assert "article_1" in keys

    async def test_list_keys_with_pattern(self, cache):
        """Test listing cache keys with a filter pattern"""
        # Put some entries
        await cache.put("paper_1", {"data": "test1"})
        await cache.put("paper_2", {"data": "test2"})
        await cache.put("article_1", {"data": "test3"})

        keys = await cache.list_keys(pattern="paper")

        assert len(keys) == 2
        assert "paper_1" in keys
        assert "paper_2" in keys
        assert "article_1" not in keys

    async def test_access_count_increment(self, cache):
        """Test that access count increments on each get"""
        key = "test_access_count"
        content = {"data": "test"}

        await cache.put(key, content)

        # Get multiple times
        await cache.get(key)
        await cache.get(key)
        await cache.get(key)

        meta = await cache.get_metadata(key)
        assert meta["access_count"] == 3

    async def test_parallel_puts(self, cache):
        """Test parallel put operations"""
        keys = [f"parallel_put_{i}" for i in range(5)]
        contents = [{"data": f"test_{i}"} for i in range(5)]

        # Put in parallel
        results = await asyncio.gather(
            *[cache.put(k, c) for k, c in zip(keys, contents)]
        )

        assert all(results)

        # Verify all were stored
        for key in keys:
            exists = await cache.exists(key)
            assert exists is True

    async def test_parallel_gets(self, cache):
        """Test parallel get operations"""
        # Put some entries first
        keys = [f"parallel_get_{i}" for i in range(5)]
        contents = [{"data": f"test_{i}"} for i in range(5)]

        for k, c in zip(keys, contents):
            await cache.put(k, c)

        # Get in parallel
        results = await asyncio.gather(
            *[cache.get(k) for k in keys]
        )

        assert len(results) == 5
        assert all(r is not None for r in results)
        for i, result in enumerate(results):
            assert result["data"] == f"test_{i}"

    async def test_parallel_mixed_operations(self, cache):
        """Test parallel mixed operations (put, get, delete)"""
        # Prepare some initial data
        await cache.put("mixed_1", {"data": "test1"})
        await cache.put("mixed_2", {"data": "test2"})

        # Run mixed operations in parallel
        results = await asyncio.gather(
            cache.put("mixed_3", {"data": "test3"}),
            cache.get("mixed_1"),
            cache.delete("mixed_2"),
            cache.get_metadata("mixed_1"),
            cache.list_keys(),
            return_exceptions=True
        )

        # Verify results
        assert results[0] is True  # put succeeded
        assert results[1]["data"] == "test1"  # get succeeded
        assert results[2] is True  # delete succeeded
        assert results[3] is not None  # get_metadata succeeded
        assert len(results[4]) >= 1  # list_keys returned keys


@pytest.mark.asyncio
class TestAsyncLiteratureCacheHelpers:
    """Test suite for async helper functions"""

    async def test_cache_paper_helper(self, temp_cache_dir):
        """Test cache_paper helper function"""
        key = "helper_test_1"
        content = {"title": "Helper Test", "abstract": "Testing helper"}
        metadata = {"source": "test"}

        result = await cache_paper(key, content, metadata, cache_name="test_helper")
        assert result is True

        # Verify it was cached
        cache = get_literature_cache("test_helper")
        retrieved = await cache.get(key)
        assert retrieved is not None
        assert retrieved["title"] == "Helper Test"

    async def test_get_cached_paper_helper(self, temp_cache_dir):
        """Test get_cached_paper helper function"""
        key = "helper_test_2"
        content = {"title": "Helper Test 2", "abstract": "Testing helper"}

        # Cache using helper
        await cache_paper(key, content, cache_name="test_helper2")

        # Retrieve using helper
        retrieved = await get_cached_paper(key, cache_name="test_helper2")
        assert retrieved is not None
        assert retrieved["title"] == "Helper Test 2"

    async def test_get_cached_paper_nonexistent(self, temp_cache_dir):
        """Test get_cached_paper with nonexistent key"""
        retrieved = await get_cached_paper("nonexistent", cache_name="test_helper3")
        assert retrieved is None


@pytest.mark.asyncio
async def test_cache_initialization(temp_cache_dir):
    """Test that cache initializes database correctly"""
    cache = LiteratureOfflineCache(cache_dir=temp_cache_dir)

    # Verify directories were created
    assert Path(temp_cache_dir).exists()
    assert (Path(temp_cache_dir) / "content").exists()
    assert (Path(temp_cache_dir) / "cache.db").exists()

    # Try to use it
    result = await cache.put("init_test", {"data": "test"})
    assert result is True
