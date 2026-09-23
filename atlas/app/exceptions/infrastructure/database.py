"""Database Exceptions"""

from app.exceptions.base import AtlasInfrastructureError


class DatabaseError(AtlasInfrastructureError):
    """Base database error"""
    pass


class DatabaseConnectionError(DatabaseError):
    """Database connection failed."""


class SessionError(DatabaseError):
    """Database session operation failed."""


class QueryError(DatabaseError):
    """Database query execution failed."""


class MigrationError(DatabaseError):
    """Database migration failed."""


class SessionNotFoundError(DatabaseError):
    """Database session not available"""
    pass


class QueryTimeoutError(DatabaseError):
    """Query exceeded timeout"""
    pass


class ConnectionPoolExhaustedError(DatabaseError):
    """No available connections in pool"""
    pass
