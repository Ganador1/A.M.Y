"""
Tests for infrastructure exceptions
"""
import pytest
from app.exceptions.infrastructure.database import (
    DatabaseError,
    DatabaseConnectionError,
    SessionError,
    QueryError,
    MigrationError
)
from app.exceptions.infrastructure.cache import CacheError, RedisError
from app.exceptions.infrastructure.api import APIError, RateLimitError
from app.exceptions.infrastructure.storage import StorageError
from app.exceptions.base import AtlasInfrastructureError


class TestDatabaseExceptions:
    """Test database exceptions"""

    def test_database_error_basic(self):
        """Test basic DatabaseError"""
        exc = DatabaseError("Database operation failed")
        assert isinstance(exc, AtlasInfrastructureError)
        assert exc.error_code == "DatabaseError"

    def test_database_connection_error(self):
        """Test DatabaseConnectionError"""
        exc = DatabaseConnectionError(
            "Failed to connect to database",
            details={
                "host": "localhost",
                "port": 5432,
                "database": "atlas",
                "error": "connection_refused"
            }
        )
        assert isinstance(exc, DatabaseError)
        assert exc.details["port"] == 5432

    def test_session_error(self):
        """Test SessionError"""
        exc = SessionError(
            "Database session expired",
            details={"session_id": "abc123", "duration": 3600}
        )
        assert isinstance(exc, DatabaseError)
        assert exc.details["session_id"] == "abc123"

    def test_query_error(self):
        """Test QueryError"""
        exc = QueryError(
            "SQL query failed",
            details={
                "query": "SELECT * FROM experiments WHERE id = ?",
                "params": [12345],
                "error": "table_not_found"
            }
        )
        assert isinstance(exc, DatabaseError)
        assert "query" in exc.details

    def test_migration_error(self):
        """Test MigrationError"""
        exc = MigrationError(
            "Database migration failed",
            details={
                "migration_id": "abc123def456",
                "version": "2025_01_01_create_tables",
                "error": "column_already_exists"
            }
        )
        assert isinstance(exc, DatabaseError)
        assert "migration_id" in exc.details


class TestCacheExceptions:
    """Test cache exceptions"""

    def test_cache_error_basic(self):
        """Test basic CacheError"""
        exc = CacheError("Cache operation failed")
        assert isinstance(exc, AtlasInfrastructureError)

    def test_redis_error(self):
        """Test RedisError"""
        exc = RedisError(
            "Redis connection failed",
            details={
                "host": "localhost",
                "port": 6379,
                "db": 0,
                "error": "connection_timeout"
            }
        )
        assert isinstance(exc, CacheError)
        assert exc.details["port"] == 6379

    def test_cache_miss_scenario(self):
        """Test cache miss scenario"""
        exc = CacheError(
            "Cache miss for key",
            details={"key": "experiment:12345", "ttl": 3600}
        )
        assert exc.details["key"] == "experiment:12345"


class TestAPIExceptions:
    """Test API exceptions"""

    def test_api_error_basic(self):
        """Test basic APIError"""
        exc = APIError("API request failed")
        assert isinstance(exc, AtlasInfrastructureError)

    def test_api_error_with_status_code(self):
        """Test APIError with HTTP status code"""
        exc = APIError(
            "API request failed",
            details={
                "endpoint": "/api/experiments",
                "method": "POST",
                "status_code": 500,
                "response": {"error": "Internal server error"}
            }
        )
        assert exc.details["status_code"] == 500

    def test_rate_limit_error(self):
        """Test RateLimitError"""
        exc = RateLimitError(
            "Rate limit exceeded",
            details={
                "endpoint": "/api/quantum-physics/simulate",
                "limit": 100,
                "window": 3600,
                "retry_after": 1800
            }
        )
        assert isinstance(exc, APIError)
        assert exc.details["limit"] == 100
        assert exc.details["retry_after"] == 1800


class TestStorageExceptions:
    """Test storage exceptions"""

    def test_storage_error_basic(self):
        """Test basic StorageError"""
        exc = StorageError("Storage operation failed")
        assert isinstance(exc, AtlasInfrastructureError)

    def test_storage_error_with_file(self):
        """Test StorageError with file context"""
        exc = StorageError(
            "Failed to write file",
            details={
                "file_path": "/data/experiments/exp_001.json",
                "operation": "write",
                "error": "permission_denied"
            }
        )
        assert exc.details["operation"] == "write"

    def test_storage_error_with_s3(self):
        """Test StorageError with S3 context"""
        exc = StorageError(
            "S3 upload failed",
            details={
                "bucket": "axiom-data",
                "key": "experiments/2025/exp_001.json",
                "size_bytes": 1024000,
                "error": "access_denied"
            }
        )
        assert exc.details["bucket"] == "axiom-data"


class TestInfrastructureExceptionHierarchy:
    """Test infrastructure exception hierarchy"""

    def test_all_inherit_from_infrastructure_error(self):
        """Test that all inherit from AtlasInfrastructureError"""
        exceptions = [
            DatabaseError("test"),
            CacheError("test"),
            APIError("test"),
            StorageError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, AtlasInfrastructureError)

    def test_specialized_inherit_from_base(self):
        """Test specialized exceptions inherit from base"""
        assert isinstance(DatabaseConnectionError("test"), DatabaseError)
        assert isinstance(SessionError("test"), DatabaseError)
        assert isinstance(QueryError("test"), DatabaseError)
        assert isinstance(RedisError("test"), CacheError)
        assert isinstance(RateLimitError("test"), APIError)


class TestInfrastructureExceptionUseCases:
    """Test real-world use cases"""

    def test_database_connection_retry(self):
        """Test database connection retry scenario"""
        def connect_to_db(max_retries=3):
            for attempt in range(max_retries):
                try:
                    # Simulate connection failure
                    if attempt < 2:
                        raise DatabaseConnectionError(
                            f"Connection attempt {attempt + 1} failed",
                            details={
                                "attempt": attempt + 1,
                                "max_retries": max_retries,
                                "error": "connection_refused"
                            }
                        )
                    return "connected"
                except DatabaseConnectionError:
                    if attempt == max_retries - 1:
                        raise

        with pytest.raises(DatabaseConnectionError) as exc_info:
            connect_to_db(max_retries=2)

        assert exc_info.value.details["attempt"] == 2

    def test_cache_fallback(self):
        """Test cache fallback to database"""
        def get_data(key: str, use_cache=True):
            if use_cache:
                raise CacheError(
                    "Cache unavailable",
                    details={"key": key, "fallback": "database"}
                )
            return {"data": "from_database"}

        with pytest.raises(CacheError) as exc_info:
            get_data("test_key")

        assert exc_info.value.details["fallback"] == "database"

    def test_api_rate_limit_handling(self):
        """Test API rate limit handling"""
        def api_call(endpoint: str):
            raise RateLimitError(
                "Too many requests",
                details={
                    "endpoint": endpoint,
                    "limit": 100,
                    "window": 60,
                    "retry_after": 30
                }
            )

        with pytest.raises(RateLimitError) as exc_info:
            api_call("/api/quantum-physics/simulate")

        # Client should wait retry_after seconds
        retry_after = exc_info.value.details["retry_after"]
        assert retry_after == 30

    def test_storage_quota_exceeded(self):
        """Test storage quota exceeded scenario"""
        def save_experiment(size_mb: int):
            quota_mb = 1000
            if size_mb > quota_mb:
                raise StorageError(
                    "Storage quota exceeded",
                    details={
                        "size_requested_mb": size_mb,
                        "quota_mb": quota_mb,
                        "available_mb": 0
                    }
                )

        with pytest.raises(StorageError) as exc_info:
            save_experiment(2000)

        assert exc_info.value.details["quota_mb"] == 1000


class TestInfrastructureExceptionSerialization:
    """Test exception serialization for APIs"""

    def test_database_error_to_dict(self):
        """Test DatabaseError serialization"""
        exc = DatabaseConnectionError(
            "Connection failed",
            error_code="DB_CONN_001",
            details={"host": "localhost", "port": 5432}
        )
        result = exc.to_dict()

        assert result["error"] == "DB_CONN_001"
        assert result["message"] == "Connection failed"
        assert result["details"]["host"] == "localhost"

    def test_api_error_to_dict(self):
        """Test APIError serialization"""
        exc = RateLimitError(
            "Rate limit exceeded",
            details={"retry_after": 60}
        )
        result = exc.to_dict()

        assert result["error"] == "RateLimitError"
        assert result["details"]["retry_after"] == 60
