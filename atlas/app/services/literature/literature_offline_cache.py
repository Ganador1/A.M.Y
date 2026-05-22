"""
Literature Offline Cache Service
Provides offline caching for scientific literature and papers

ROADMAP 5: Migrated to async with aiosqlite for non-blocking database operations.
All database operations now use aiosqlite.connect() with async/await pattern.
"""

import json
import hashlib
import aiosqlite
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import msgpack
import logging
import gzip
import asyncio
from app.exceptions.infrastructure.cache import CacheError
from app.types.literature_offline_cache_types import (
    SaveContentResult,
    GetStatsResult,
    GetBatchResult,
)

logger = logging.getLogger(__name__)

class CacheEntry:
    """Represents a cached literature entry"""

    def __init__(self,
                 key: str,
                 content: Any,
                 metadata: Dict[str, Any],
                 ttl: Optional[int] = None):
        self.key = key
        self.content = content
        self.metadata = metadata
        self.created_at = datetime.now()
        self.expires_at = None
        if ttl:
            self.expires_at = self.created_at + timedelta(seconds=ttl)
        self.access_count = 0
        self.last_accessed = self.created_at

    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def touch(self):
        """Update access information"""
        self.access_count += 1
        self.last_accessed = datetime.now()

class LiteratureOfflineCache:
    """Offline cache for scientific literature"""

    def __init__(self, cache_dir: str = "./literature_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / "cache.db"
        self.content_dir = self.cache_dir / "content"
        self.content_dir.mkdir(exist_ok=True)

        # Initialize database synchronously in constructor
        # This is acceptable as it's a one-time setup operation
        asyncio.run(self._init_database())

    async def _init_database(self):
        """Initialize SQLite database for metadata (async)"""
        async with aiosqlite.connect(self.db_path) as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    content_path TEXT,
                    metadata TEXT,
                    created_at TEXT,
                    expires_at TEXT,
                    access_count INTEGER,
                    last_accessed TEXT,
                    content_hash TEXT,
                    content_size INTEGER
                )
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires_at ON cache_entries(expires_at)
            """)

            await conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_last_accessed ON cache_entries(last_accessed)
            """)

            await conn.commit()

    def _get_content_path(self, key: str) -> Path:
        """Get content file path for a key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return self.content_dir / f"{key_hash}.msgpack.gz"

    def _save_content(self, content: Any, path: Path) -> SaveContentResult:
        """Save content to compressed file"""
        try:
            with gzip.open(path, 'wb') as f:
                msgpack.pack(content, f)

            file_size = path.stat().st_size
            content_hash = hashlib.sha256(msgpack.packb(content)).hexdigest()

            return {
                "content_hash": content_hash,
                "content_size": file_size
            }
        except CacheError as e:
            logger.error(f"Error saving content to {path}: {e}")
            return {}

    def _load_content(self, path: Path) -> Any:
        """Load content from compressed file"""
        try:
            if not path.exists():
                return None

            with gzip.open(path, 'rb') as f:
                return msgpack.unpack(f)
        except CacheError as e:
            logger.error(f"Error loading content from {path}: {e}")
            return None

    async def put(self,
            key: str,
            content: Any,
            metadata: Optional[Dict[str, Any]] = None,
            ttl: Optional[int] = None) -> bool:
        """Store content in cache (async)"""
        if metadata is None:
            metadata = {}

        try:
            # Save content to file
            content_path = self._get_content_path(key)
            content_info = self._save_content(content, content_path)

            if not content_info:
                return False

            # Store metadata in database
            now = datetime.now().isoformat()
            expires_at = None
            if ttl:
                expires_at = (datetime.now() + timedelta(seconds=ttl)).isoformat()

            async with aiosqlite.connect(self.db_path) as conn:
                await conn.execute("""
                    INSERT OR REPLACE INTO cache_entries
                    (key, content_path, metadata, created_at, expires_at,
                     access_count, last_accessed, content_hash, content_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    key, str(content_path), json.dumps(metadata), now, expires_at,
                    0, now, content_info["content_hash"], content_info["content_size"]
                ))
                await conn.commit()

            logger.info(f"Cached entry: {key}")
            return True

        except CacheError as e:
            logger.error(f"Error caching entry {key}: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """Retrieve content from cache (async)"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("""
                    SELECT content_path, metadata, expires_at, access_count
                    FROM cache_entries WHERE key = ?
                """, (key,))

                row = await cursor.fetchone()
                if not row:
                    return None

                content_path, _metadata_json, expires_at, access_count = row

                # Check expiration
                if expires_at:
                    expires_dt = datetime.fromisoformat(expires_at)
                    if datetime.now() > expires_dt:
                        await self.delete(key)
                        return None

                # Load content
                content = self._load_content(Path(content_path))
                if content is None:
                    await self.delete(key)
                    return None

                # Update access stats
                now = datetime.now().isoformat()
                await conn.execute("""
                    UPDATE cache_entries
                    SET access_count = ?, last_accessed = ?
                    WHERE key = ?
                """, (access_count + 1, now, key))
                await conn.commit()

                return content

        except CacheError as e:
            logger.error(f"Error retrieving entry {key}: {e}")
            return None

    async def get_metadata(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a cached entry (async)"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("""
                    SELECT metadata, created_at, expires_at, access_count,
                           last_accessed, content_hash, content_size
                    FROM cache_entries WHERE key = ?
                """, (key,))

                row = await cursor.fetchone()
                if not row:
                    return None

                metadata_json, created_at, expires_at, access_count, last_accessed, content_hash, content_size = row

                return {
                    "metadata": json.loads(metadata_json),
                    "created_at": created_at,
                    "expires_at": expires_at,
                    "access_count": access_count,
                    "last_accessed": last_accessed,
                    "content_hash": content_hash,
                    "content_size": content_size
                }

        except CacheError as e:
            logger.error(f"Error getting metadata for {key}: {e}")
            return None

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache (async)"""
        metadata = await self.get_metadata(key)
        return metadata is not None

    async def delete(self, key: str) -> bool:
        """Delete entry from cache (async)"""
        try:
            # Get content path
            content_path = self._get_content_path(key)

            # Delete from database
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                await conn.commit()
                deleted = cursor.rowcount > 0

            # Delete content file
            if content_path.exists():
                content_path.unlink()

            if deleted:
                logger.info(f"Deleted cache entry: {key}")

            return deleted

        except CacheError as e:
            logger.error(f"Error deleting entry {key}: {e}")
            return False

    async def clear_expired(self) -> int:
        """Clear all expired entries (async)"""
        try:
            now = datetime.now().isoformat()

            async with aiosqlite.connect(self.db_path) as conn:
                # Get expired entries
                cursor = await conn.execute("""
                    SELECT key, content_path FROM cache_entries
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (now,))

                expired_entries = await cursor.fetchall()

                # Delete expired entries
                await conn.execute("""
                    DELETE FROM cache_entries
                    WHERE expires_at IS NOT NULL AND expires_at < ?
                """, (now,))
                await conn.commit()

                # Delete content files
                for _key, content_path in expired_entries:
                    try:
                        Path(content_path).unlink(missing_ok=True)
                    except CacheError as e:
                        logger.error(f"Error deleting expired content file {content_path}: {e}")

                logger.info(f"Cleared {len(expired_entries)} expired entries")
                return len(expired_entries)

        except CacheError as e:
            logger.error(f"Error clearing expired entries: {e}")
            return 0

    async def get_stats(self) -> GetStatsResult:
        """Get cache statistics (async)"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                cursor = await conn.execute("""
                    SELECT
                        COUNT(*) as total_entries,
                        SUM(content_size) as total_size,
                        AVG(access_count) as avg_access_count,
                        COUNT(CASE WHEN expires_at IS NOT NULL AND expires_at < ? THEN 1 END) as expired_count
                    FROM cache_entries
                """, (datetime.now().isoformat(),))

                stats = await cursor.fetchone()

                return {
                    "total_entries": stats[0] or 0,
                    "total_size_bytes": stats[1] or 0,
                    "average_access_count": stats[2] or 0,
                    "expired_entries": stats[3] or 0
                }

        except CacheError as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    async def list_keys(self, pattern: Optional[str] = None) -> List[str]:
        """List all cache keys, optionally filtered by pattern (async)"""
        try:
            async with aiosqlite.connect(self.db_path) as conn:
                if pattern:
                    cursor = await conn.execute("""
                        SELECT key FROM cache_entries WHERE key LIKE ?
                    """, (f"%{pattern}%",))
                else:
                    cursor = await conn.execute("SELECT key FROM cache_entries")

                rows = await cursor.fetchall()
                return [row[0] for row in rows]

        except CacheError as e:
            logger.error(f"Error listing keys: {e}")
            return []

    async def put_batch(self, entries: List[Dict[str, Any]]) -> Dict[str, bool]:
        """
        Store multiple entries in cache in parallel using asyncio.gather.

        Args:
            entries: List of dicts with keys: 'key', 'content', 'metadata' (optional), 'ttl' (optional)

        Returns:
            Dictionary mapping keys to success status

        Example:
            entries = [
                {"key": "paper1", "content": {...}, "metadata": {...}},
                {"key": "paper2", "content": {...}, "ttl": 3600}
            ]
            results = await cache.put_batch(entries)
            # Returns: {"paper1": True, "paper2": True}
        """
        tasks = []
        keys = []

        for entry in entries:
            key = entry["key"]
            content = entry["content"]
            metadata = entry.get("metadata")
            ttl = entry.get("ttl")

            tasks.append(self.put(key, content, metadata, ttl))
            keys.append(key)

        logger.info(f"Caching {len(entries)} entries in parallel")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                result_dict[key] = False
                logger.error(f"Error caching {key}: {result}")
            else:
                result_dict[key] = result

        return result_dict

    async def get_batch(self, keys: List[str]) -> GetBatchResult:
        """
        Retrieve multiple entries from cache in parallel using asyncio.gather.

        Args:
            keys: List of cache keys to retrieve

        Returns:
            Dictionary mapping keys to their content (or None if not found)

        Example:
            results = await cache.get_batch(["paper1", "paper2", "paper3"])
            # Returns: {"paper1": {...}, "paper2": {...}, "paper3": None}
        """
        logger.info(f"Retrieving {len(keys)} entries in parallel")

        tasks = [self.get(key) for key in keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                result_dict[key] = None
                logger.error(f"Error retrieving {key}: {result}")
            else:
                result_dict[key] = result

        return result_dict

    async def delete_batch(self, keys: List[str]) -> Dict[str, bool]:
        """
        Delete multiple entries from cache in parallel using asyncio.gather.

        Args:
            keys: List of cache keys to delete

        Returns:
            Dictionary mapping keys to deletion success status
        """
        logger.info(f"Deleting {len(keys)} entries in parallel")

        tasks = [self.delete(key) for key in keys]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                result_dict[key] = False
                logger.error(f"Error deleting {key}: {result}")
            else:
                result_dict[key] = result

        return result_dict

class LiteratureCacheManager:
    """Manager for literature cache instances"""

    def __init__(self):
        self.caches: Dict[str, LiteratureOfflineCache] = {}

    def get_cache(self, cache_name: str = "default") -> LiteratureOfflineCache:
        """Get or create a cache instance"""
        if cache_name not in self.caches:
            self.caches[cache_name] = LiteratureOfflineCache(
                f"./literature_cache/{cache_name}"
            )
        return self.caches[cache_name]

    async def clear_all_expired(self) -> Dict[str, int]:
        """Clear expired entries from all caches (async)"""
        results = {}
        for name, cache in self.caches.items():
            results[name] = await cache.clear_expired()
        return results

# Global cache manager
cache_manager = LiteratureCacheManager()

def get_literature_cache(cache_name: str = "default") -> LiteratureOfflineCache:
    """Get a literature cache instance"""
    return cache_manager.get_cache(cache_name)

async def cache_paper(key: str,
               content: Any,
               metadata: Optional[Dict[str, Any]] = None,
               ttl: Optional[int] = None,
               cache_name: str = "default") -> bool:
    """Cache a paper or literature content (async)"""
    cache = get_literature_cache(cache_name)
    return await cache.put(key, content, metadata, ttl)

async def get_cached_paper(key: str, cache_name: str = "default") -> Optional[Any]:
    """Retrieve cached paper content (async)"""
    cache = get_literature_cache(cache_name)
    return await cache.get(key)
