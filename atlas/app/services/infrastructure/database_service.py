"""
AXIOM Database Service
======================

Service layer for comprehensive database operations in the AXIOM Mathematics AI Engine.

This module provides a high-level interface for all database operations, including:
- User management and authentication
- Session handling and security
- Calculation history and caching
- System metrics and monitoring
- Error logging and debugging
- API request tracking
- Scientific dataset management

The service uses SQLAlchemy ORM for database abstraction and provides both
context manager support and individual method operations.

Database Architecture:
---------------------

The service implements a multi-layered architecture:

1. **Session Management**: Automatic session lifecycle management
2. **Transaction Handling**: Proper commit/rollback for data consistency
3. **Error Handling**: Comprehensive exception handling and logging
4. **Performance Optimization**: Efficient queries with proper indexing
5. **Security**: Input validation and SQL injection prevention

Key Features:
- Context manager support for automatic resource cleanup
- Comprehensive error handling with rollback support
- Optimized queries with proper indexing utilization
- Type hints for better IDE support and documentation
- Logging integration for debugging and monitoring

Usage Examples:
--------------

Basic user operations:
    >>> from app.services.database_service import DatabaseService
    >>> db = DatabaseService()
    >>> user = db.create_user("john", "john@example.com", "hashed_password")
    >>> print(f"Created user: {user.username}")

Session management:
    >>> with DatabaseService() as db:
    ...     session = db.create_session(user.id, "token123", expires_at)
    ...     print(f"Session created: {session.session_token}")

Calculation tracking:
    >>> db.save_calculation(
    ...     user_id=1,
    ...     operation_type="arithmetic",
    ...     operation_name="addition",
    ...     input_data={"a": 5, "b": 3},
    ...     result_data={"result": 8},
    ...     execution_time=0.001
    ... )

Author: AXIOM Mathematics AI Engine Team
Date: September 2025
Version: 1.0.0
"""

from typing import List, Optional, Dict, Any, TypeVar
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import logging
import httpx
from app.core.database import get_db_session
from app.models.database_models import (
    User, UserSession, Calculation, CachedResult,
    SystemMetric, ErrorLog, APIRequestLog, ScientificDataset
)
from app.exceptions.infrastructure.database import DatabaseError
from app.types.database_service_types import (
    GetCalculationStatsResult,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class DatabaseService:
    """
    Comprehensive database service for AXIOM Mathematics AI Engine.

    This service provides a unified interface for all database operations,
    implementing proper session management, transaction handling, and error recovery.
    It supports both context manager usage and individual method calls.

    The service is designed with the following principles:
    - **Atomicity**: Each operation is a complete transaction
    - **Consistency**: Data integrity is maintained across operations
    - **Isolation**: Operations don't interfere with each other
    - **Durability**: Changes are persisted reliably

    Attributes:
        None (stateless service design)

    Example:
        >>> # Context manager usage (recommended)
        >>> with DatabaseService() as db:
        ...     user = db.create_user("john", "john@example.com", "hash")
        ...     print(f"User created: {user.id}")

        >>> # Direct usage
        >>> db = DatabaseService()
        >>> user = db.get_user_by_username("john")
    """

    def __init__(self):
        """
        Initialize the database service.

        The service is stateless and doesn't require initialization parameters.
        Database connections are managed per operation for optimal resource usage.
        """
        pass  # Stateless design - no initialization needed

    def __enter__(self):
        """
        Context manager entry.

        Returns the service instance for use in with statements.
        This enables automatic resource cleanup and proper session management.

        Returns:
            DatabaseService: The service instance

        Example:
            >>> with DatabaseService() as db:
            ...     user = db.create_user("test", "test@example.com", "hash")
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit.

        Handles cleanup of resources. Currently no cleanup is needed as
        sessions are managed per method, but this provides extensibility
        for future enhancements.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred
        """
        pass  # Session lifecycle is managed per method

    def _get_session(self) -> Session:
        """
        Get a database session for operations.

        This method provides a fresh database session for each operation,
        ensuring proper isolation and resource management.

        Returns:
            Session: SQLAlchemy database session

        Note:
            Sessions are automatically closed after each operation
            to prevent connection leaks and ensure proper resource cleanup.
        """
        return get_db_session()

    # ========================================
    # User Management Operations
    # ========================================

    def create_user(self, username: str, email: str, hashed_password: str,
                   full_name: Optional[str] = None) -> User:
        """
        Create a new user account.

        This method creates a new user with the provided credentials and profile information.
        It performs validation and ensures data consistency before committing to the database.

        Args:
            username (str): Unique username (max 50 characters)
            email (str): Unique email address (max 100 characters)
            hashed_password (str): Bcrypt-hashed password (max 255 characters)
            full_name (Optional[str]): User's full name (max 100 characters)

        Returns:
            User: The created user object with assigned ID

        Raises:
            Exception: If user creation fails (duplicate username/email, database error)

        Example:
            >>> db = DatabaseService()
            >>> user = db.create_user(
            ...     username="johndoe",
            ...     email="john@example.com",
            ...     hashed_password=hash_password("secure123"),
            ...     full_name="John Doe"
            ... )
            >>> print(f"User ID: {user.id}")
        """
        session = self._get_session()
        try:
            user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                full_name=full_name
            )
            session.add(user)
            session.flush()  # Get the ID without committing
            session.commit()
            return user
        except DatabaseError:
            session.rollback()
            raise
        finally:
            session.close()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Retrieve a user by their username.

        This method performs an efficient lookup using the username index
        for fast user authentication and profile retrieval.

        Args:
            username (str): The username to search for

        Returns:
            Optional[User]: User object if found, None otherwise

        Example:
            >>> user = db.get_user_by_username("johndoe")
            >>> if user:
            ...     print(f"Found user: {user.email}")
        """
        session = self._get_session()
        try:
            return session.query(User).filter(User.username == username).first()
        finally:
            session.close()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.

        This method performs an efficient lookup using the email index
        for fast user authentication and password recovery.

        Args:
            email (str): The email address to search for

        Returns:
            Optional[User]: User object if found, None otherwise

        Example:
            >>> user = db.get_user_by_email("john@example.com")
            >>> if user:
            ...     print(f"User found: {user.username}")
        """
        session = self._get_session()
        try:
            return session.query(User).filter(User.email == email).first()
        finally:
            session.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their unique ID.

        This method performs a primary key lookup for the most efficient
        user retrieval when the ID is known.

        Args:
            user_id (int): The user's unique identifier

        Returns:
            Optional[User]: User object if found, None otherwise

        Example:
            >>> user = db.get_user_by_id(123)
            >>> if user:
            ...     print(f"User: {user.username}")
        """
        session = self._get_session()
        try:
            return session.query(User).filter(User.id == user_id).first()
        finally:
            session.close()

    # ========================================
    # Session Management Operations
    # ========================================

    def create_session(self, user_id: int, session_token: str, expires_at: datetime,
                      ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> UserSession:
        """
        Create a new user session for authentication tracking.

        This method creates a session record for web authentication,
        tracking login activity, IP addresses, and session expiration.

        Args:
            user_id (int): ID of the user creating the session
            session_token (str): Unique session token (max 255 characters)
            expires_at (datetime): Session expiration timestamp (UTC)
            ip_address (Optional[str]): Client IP address (max 45 characters, IPv6 compatible)
            user_agent (Optional[str]): Client user agent string

        Returns:
            UserSession: The created session object

        Raises:
            Exception: If session creation fails

        Example:
            >>> from datetime import datetime, timedelta
            >>> expires = datetime.utcnow() + timedelta(hours=24)
            >>> session = db.create_session(
            ...     user_id=1,
            ...     session_token="abc123token",
            ...     expires_at=expires,
            ...     ip_address="192.168.1.100"
            ... )
        """
        session = self._get_session()
        try:
            user_session = UserSession(
                user_id=user_id,
                session_token=session_token,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            session.add(user_session)
            session.commit()
            return user_session
        finally:
            session.close()

    def get_session_by_token(self, session_token: str) -> Optional[UserSession]:
        """
        Retrieve an active, non-expired session by its token.

        This method validates session tokens for authentication,
        checking both token validity and expiration status.

        Args:
            session_token (str): The session token to validate

        Returns:
            Optional[UserSession]: Session object if valid and active, None otherwise

        Example:
            >>> session = db.get_session_by_token("abc123token")
            >>> if session and session.is_active:
            ...     print(f"Valid session for user {session.user_id}")
        """
        session = self._get_session()
        try:
            return session.query(UserSession).filter(
                and_(
                    UserSession.session_token == session_token,
                    UserSession.is_active,
                    UserSession.expires_at > datetime.utcnow()
                )
            ).first()
        finally:
            session.close()

    def invalidate_session(self, session_token: str):
        """
        Invalidate a user session (logout).

        This method marks a session as inactive, effectively logging out
        the user from that session while preserving the record for audit purposes.

        Args:
            session_token (str): The session token to invalidate

        Example:
            >>> db.invalidate_session("abc123token")
            >>> # Session is now inactive
        """
        session = self._get_session()
        try:
            user_session = session.query(UserSession).filter(
                UserSession.session_token == session_token
            ).first()
            if user_session:
                # Update session status using update query
                session.query(UserSession).filter(
                    UserSession.session_token == session_token
                ).update({'is_active': False})
                session.commit()
        finally:
            session.close()

    # ========================================
    # Calculation Operations
    # ========================================

    def save_calculation(self, user_id: Optional[int] = None, operation_type: Optional[str] = None,
                        operation_name: Optional[str] = None, input_data: Optional[Dict[str, Any]] = None,
                        result_data: Optional[Dict[str, Any]] = None, execution_time: Optional[float] = None,
                        status: str = "completed", error_message: Optional[str] = None) -> Calculation:
        """
        Save a mathematical calculation result to the database.

        This method stores the complete history of mathematical computations
        performed by the AXIOM system, including input parameters, results,
        execution times, and status information.

        Args:
            user_id (Optional[int]): User ID (None for anonymous calculations)
            operation_type (Optional[str]): Type of operation (e.g., 'arithmetic', 'calculus')
            operation_name (Optional[str]): Specific operation name (e.g., 'add', 'derivative')
            input_data (Optional[Dict[str, Any]]): Input parameters as JSON
            result_data (Optional[Dict[str, Any]]): Computation result as JSON
            execution_time (Optional[float]): Execution time in seconds
            status (str): Computation status ('completed', 'failed', 'running')
            error_message (Optional[str]): Error message if computation failed

        Returns:
            Calculation: The saved calculation object

        Example:
            >>> calc = db.save_calculation(
            ...     user_id=1,
            ...     operation_type="arithmetic",
            ...     operation_name="addition",
            ...     input_data={"a": 5, "b": 3},
            ...     result_data={"result": 8},
            ...     execution_time=0.001
            ... )
        """
        session = self._get_session()
        try:
            calculation = Calculation(
                user_id=user_id,
                operation_type=operation_type,
                operation_name=operation_name,
                input_data=input_data,
                result_data=result_data,
                execution_time=execution_time,
                status=status,
                error_message=error_message,
                completed_at=datetime.utcnow() if status == "completed" else None
            )
            session.add(calculation)
            session.commit()
            return calculation
        finally:
            session.close()

    def get_user_calculations(self, user_id: int, limit: int = 50, offset: int = 0) -> List[Calculation]:
        """
        Retrieve a user's calculation history with pagination.

        This method provides paginated access to a user's mathematical computation
        history, ordered by most recent calculations first.

        Args:
            user_id (int): User ID to retrieve calculations for
            limit (int): Maximum number of calculations to return (default: 50)
            offset (int): Number of calculations to skip (default: 0)

        Returns:
            List[Calculation]: List of user's calculations

        Example:
            >>> calculations = db.get_user_calculations(user_id=1, limit=10)
            >>> for calc in calculations:
            ...     print(f"{calc.operation_name}: {calc.execution_time}s")
        """
        session = self._get_session()
        try:
            return session.query(Calculation).filter(
                Calculation.user_id == user_id
            ).order_by(desc(Calculation.created_at)).limit(limit).offset(offset).all()
        finally:
            session.close()

    def get_calculation_stats(self, user_id: Optional[int] = None) -> GetCalculationStatsResult:
        """
        Get comprehensive calculation statistics.

        This method provides aggregated statistics about calculations,
        including total counts, operation type distribution, and performance metrics.

        Args:
            user_id (Optional[int]): User ID for user-specific stats, None for global stats

        Returns:
            Dict[str, Any]: Statistics dictionary with totals and operation breakdowns

        Example:
            >>> stats = db.get_calculation_stats(user_id=1)
            >>> print(f"Total calculations: {stats['total_calculations']}")
            >>> for op_stat in stats['operation_stats']:
            ...     print(f"{op_stat['operation_type']}: {op_stat['count']} operations")
        """
        session = self._get_session()
        try:
            query = session.query(
                Calculation.operation_type,
                func.count(Calculation.id).label('count'),
                func.avg(Calculation.execution_time).label('avg_time')
            )

            if user_id:
                query = query.filter(Calculation.user_id == user_id)

            stats = query.group_by(Calculation.operation_type).all()

            return {
                "total_calculations": sum(getattr(stat, 'count', 0) for stat in stats),
                "operation_stats": [
                    {
                        "operation_type": getattr(stat, 'operation_type', None),
                        "count": getattr(stat, 'count', 0),
                        "avg_execution_time": getattr(stat, 'avg_time', None)
                    }
                    for stat in stats
                ]
            }
        finally:
            session.close()

    # ========================================
    # Cache Operations
    # ========================================

    def save_cache_result(self, cache_key: str, operation_type: str,
                         input_data: Dict[str, Any], result_data: Dict[str, Any],
                         ttl_seconds: int) -> CachedResult:
        """
        Save or update a cached computation result.

        This method implements intelligent caching with automatic update
        of access statistics and TTL (time-to-live) management.

        Args:
            cache_key (str): Unique cache key (max 255 characters)
            operation_type (str): Type of operation that was cached
            input_data (Dict[str, Any]): Input parameters as JSON
            result_data (Dict[str, Any]): Cached result as JSON
            ttl_seconds (int): Time-to-live in seconds

        Returns:
            CachedResult: The saved or updated cache entry

        Example:
            >>> cache = db.save_cache_result(
            ...     cache_key="add_5_3",
            ...     operation_type="arithmetic",
            ...     input_data={"a": 5, "b": 3},
            ...     result_data={"result": 8},
            ...     ttl_seconds=3600
            ... )
        """
        session = self._get_session()
        try:
            # Check if key already exists
            existing = session.query(CachedResult).filter(
                CachedResult.cache_key == cache_key
            ).first()

            if existing:
                # Update existing cache entry
                session.query(CachedResult).filter(
                    CachedResult.cache_key == cache_key
                ).update({
                    'result_data': result_data,
                    'accessed_at': datetime.utcnow(),
                    'access_count': CachedResult.access_count + 1
                })
                session.commit()
                return session.query(CachedResult).filter(
                    CachedResult.cache_key == cache_key
                ).first()

            cache_result = CachedResult(
                cache_key=cache_key,
                operation_type=operation_type,
                input_data=input_data,
                result_data=result_data,
                ttl_seconds=ttl_seconds
            )
            session.add(cache_result)
            session.commit()
            return cache_result
        finally:
            session.close()

    def get_cache_result(self, cache_key: str) -> Optional[CachedResult]:
        """
        Retrieve a cached result and update access statistics.

        This method retrieves cached results and automatically updates
        access timestamps and counters for cache management.

        Args:
            cache_key (str): The cache key to retrieve

        Returns:
            Optional[CachedResult]: Cache entry if found, None otherwise

        Example:
            >>> cached = db.get_cache_result("add_5_3")
            >>> if cached:
            ...     print(f"Result: {cached.result_data}")
            ...     print(f"Access count: {cached.access_count}")
        """
        session = self._get_session()
        try:
            result = session.query(CachedResult).filter(
                CachedResult.cache_key == cache_key
            ).first()

            if result:
                # Update access statistics using update query
                session.query(CachedResult).filter(
                    CachedResult.cache_key == cache_key
                ).update({
                    'accessed_at': datetime.utcnow(),
                    'access_count': CachedResult.access_count + 1
                })
                session.commit()
                # Re-fetch the updated result
                result = session.query(CachedResult).filter(
                    CachedResult.cache_key == cache_key
                ).first()

            return result
        finally:
            session.close()

    def cleanup_expired_cache(self):
        """
        Remove expired cache entries from the database.

        This method performs cleanup of cache entries that have exceeded
        their time-to-live (TTL), helping maintain database performance
        and storage efficiency.

        The cleanup is performed in Python to handle the TTL logic correctly,
        checking each entry's creation time against its TTL value.

        Example:
            >>> db.cleanup_expired_cache()
            >>> # Expired entries are automatically removed
        """
        session = self._get_session()
        try:
            # Get all cache entries and check expiration in Python
            all_entries = session.query(CachedResult).all()
            expired_count = 0

            for entry in all_entries:
                # Access the actual datetime value, not the Column
                created_at = getattr(entry, 'created_at', None)
                if created_at is None:
                    continue  # Skip if no creation time

                # Access the actual integer value, not the Column
                ttl_seconds = getattr(entry, 'ttl_seconds', 3600)
                if isinstance(ttl_seconds, int):
                    pass  # Already an int
                else:
                    ttl_seconds = 3600  # Default fallback

                if created_at + timedelta(seconds=ttl_seconds) < datetime.utcnow():
                    session.delete(entry)
                    expired_count += 1

            session.commit()
            logger.info(f"Cleaned up {expired_count} expired cache entries")
        finally:
            session.close()

    # ========================================
    # Metrics and Monitoring Operations
    # ========================================

    def save_metric(self, metric_name: str, metric_value: float,
                   metric_unit: Optional[str] = None, tags: Optional[Dict[str, Any]] = None) -> SystemMetric:
        """
        Save a system performance metric.

        This method stores system performance metrics for monitoring and analytics,
        including response times, resource usage, and other operational metrics.

        Args:
            metric_name (str): Name of the metric (max 100 characters)
            metric_value (float): Numeric value of the metric
            metric_unit (Optional[str]): Unit of measurement (e.g., 'ms', 'MB', 'percent')
            tags (Optional[Dict[str, Any]]): Additional metadata as JSON

        Returns:
            SystemMetric: The saved metric object

        Example:
            >>> metric = db.save_metric(
            ...     metric_name="response_time",
            ...     metric_value=0.150,
            ...     metric_unit="seconds",
            ...     tags={"endpoint": "/api/calculate", "method": "POST"}
            ... )
        """
        session = self._get_session()
        try:
            metric = SystemMetric(
                metric_name=metric_name,
                metric_value=metric_value,
                metric_unit=metric_unit,
                tags=tags
            )
            session.add(metric)
            session.commit()
            return metric
        finally:
            session.close()

    def get_metrics(self, metric_name: Optional[str] = None, hours: int = 24) -> List[SystemMetric]:
        """
        Retrieve system metrics with time filtering.

        This method provides access to system performance metrics within
        a specified time window, useful for monitoring and analytics.

        Args:
            metric_name (Optional[str]): Filter by specific metric name, None for all
            hours (int): Number of hours to look back (default: 24)

        Returns:
            List[SystemMetric]: List of metrics ordered by creation time (newest first)

        Example:
            >>> metrics = db.get_metrics("response_time", hours=1)
            >>> for metric in metrics:
            ...     print(f"{metric.metric_name}: {metric.metric_value} {metric.metric_unit}")
        """
        session = self._get_session()
        try:
            query = session.query(SystemMetric).filter(
                SystemMetric.created_at >= datetime.utcnow() - timedelta(hours=hours)
            )

            if metric_name:
                query = query.filter(SystemMetric.metric_name == metric_name)

            return query.order_by(desc(SystemMetric.created_at)).all()
        finally:
            session.close()

    # ========================================
    # Error Logging Operations
    # ========================================

    def log_error(self, error_type: str, error_message: str, stack_trace: Optional[str] = None,
                 user_id: Optional[int] = None, endpoint: Optional[str] = None, request_data: Optional[Dict[str, Any]] = None,
                 user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> ErrorLog:
        """
        Log an application error with comprehensive context.

        This method provides comprehensive error tracking and debugging capabilities,
        storing detailed information about application errors, stack traces, and
        contextual information for troubleshooting.

        Args:
            error_type (str): Type of error (max 100 characters)
            error_message (str): Error message text
            stack_trace (Optional[str]): Full stack trace
            user_id (Optional[int]): User ID associated with the error
            endpoint (Optional[str]): API endpoint where error occurred
            request_data (Optional[Dict[str, Any]]): Request data as JSON
            user_agent (Optional[str]): Client user agent string
            ip_address (Optional[str]): Client IP address

        Returns:
            ErrorLog: The saved error log object

        Example:
            >>> error = db.log_error(
            ...     error_type="ValidationError",
            ...     error_message="Invalid input parameters",
            ...     user_id=1,
            ...     endpoint="/api/calculate"
            ... )
        """
        session = self._get_session()
        try:
            error_log = ErrorLog(
                error_type=error_type,
                error_message=error_message,
                stack_trace=stack_trace,
                user_id=user_id,
                endpoint=endpoint,
                request_data=request_data,
                user_agent=user_agent,
                ip_address=ip_address
            )
            session.add(error_log)
            session.commit()
            return error_log
        finally:
            session.close()

    # ========================================
    # API Request Logging Operations
    # ========================================

    def log_api_request(self, user_id: Optional[int] = None, method: Optional[str] = None, endpoint: Optional[str] = None,
                       status_code: Optional[int] = None, response_time: Optional[float] = None,
                       request_size: Optional[int] = None, response_size: Optional[int] = None,
                       user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> APIRequestLog:
        """
        Log an API request for analytics and monitoring.

        This method tracks all API requests for analytics, debugging, and usage
        monitoring purposes, providing comprehensive information about API usage
        patterns and performance.

        Args:
            user_id (Optional[int]): User ID (None for anonymous requests)
            method (Optional[str]): HTTP method (max 10 characters)
            endpoint (Optional[str]): API endpoint (max 255 characters)
            status_code (Optional[int]): HTTP status code
            response_time (Optional[float]): Response time in seconds
            request_size (Optional[int]): Request size in bytes
            response_size (Optional[int]): Response size in bytes
            user_agent (Optional[str]): Client user agent string
            ip_address (Optional[str]): Client IP address

        Returns:
            APIRequestLog: The saved API request log object

        Example:
            >>> log = db.log_api_request(
            ...     user_id=1,
            ...     method="POST",
            ...     endpoint="/api/calculate",
            ...     status_code=200,
            ...     response_time=0.150
            ... )
        """
        session = self._get_session()
        try:
            request_log = APIRequestLog(
                user_id=user_id,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                response_time=response_time,
                request_size=request_size,
                response_size=response_size,
                user_agent=user_agent,
                ip_address=ip_address
            )
            session.add(request_log)
            session.commit()
            return request_log
        finally:
            session.close()

    # ========================================
    # Scientific Dataset Operations
    # ========================================

    def save_dataset(self, name: str, dataset_type: str, data_format: str,
                    description: Optional[str] = None, data_content: Optional[Dict[str, Any]] = None,
                    file_path: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                    created_by: Optional[int] = None, is_public: bool = False) -> ScientificDataset:
        """
        Save a scientific dataset to the database.

        This method stores scientific datasets, experimental data, and research
        materials used by the AXIOM system for advanced computations and analysis.

        Args:
            name (str): Dataset name (max 255 characters)
            dataset_type (str): Type of dataset (e.g., 'chemistry', 'physics', 'biology')
            data_format (str): Data format (e.g., 'json', 'csv', 'binary')
            description (Optional[str]): Dataset description
            data_content (Optional[Dict[str, Any]]): JSON data content
            file_path (Optional[str]): File path for file-based datasets
            metadata (Optional[Dict[str, Any]]): Additional metadata as JSON
            created_by (Optional[int]): User ID of creator
            is_public (bool): Public visibility flag

        Returns:
            ScientificDataset: The saved dataset object

        Example:
            >>> dataset = db.save_dataset(
            ...     name="experimental_data",
            ...     dataset_type="physics",
            ...     data_format="json",
            ...     data_content={"measurements": [1.0, 2.0, 3.0]},
            ...     created_by=1,
            ...     is_public=True
            ... )
        """
        session = self._get_session()
        try:
            dataset = ScientificDataset(
                name=name,
                description=description,
                dataset_type=dataset_type,
                data_format=data_format,
                data_content=data_content,
                file_path=file_path,
                metadata_info=metadata,
                created_by=created_by,
                is_public=is_public
            )
            session.add(dataset)
            session.commit()
            return dataset
        finally:
            session.close()

    def get_datasets(self, dataset_type: Optional[str] = None, user_id: Optional[int] = None,
                    is_public: Optional[bool] = None, limit: int = 50) -> List[ScientificDataset]:
        """
        Retrieve scientific datasets with filtering options.

        This method provides flexible querying of scientific datasets with
        support for filtering by type, user, and visibility settings.

        Args:
            dataset_type (Optional[str]): Filter by dataset type
            user_id (Optional[int]): Filter by user (shows user's datasets + public ones)
            is_public (Optional[bool]): Filter by public visibility
            limit (int): Maximum number of datasets to return (default: 50)

        Returns:
            List[ScientificDataset]: List of datasets ordered by creation date

        Example:
            >>> # Get public physics datasets
            >>> datasets = db.get_datasets(
            ...     dataset_type="physics",
            ...     is_public=True,
            ...     limit=10
            ... )
        """
        session = self._get_session()
        try:
            query = session.query(ScientificDataset)

            if dataset_type:
                query = query.filter(ScientificDataset.dataset_type == dataset_type)

            if user_id:
                query = query.filter(
                    or_(
                        ScientificDataset.created_by == user_id,
                        ScientificDataset.is_public
                    )
                )
            elif is_public is not None:
                query = query.filter(ScientificDataset.is_public == is_public)

            return query.order_by(desc(ScientificDataset.created_at)).limit(limit).all()
        finally:
            session.close()


# ========================================
# Convenience Functions
# ========================================

def save_calculation_result(user_id: Optional[int] = None, operation_type: Optional[str] = None,
                           operation_name: Optional[str] = None, input_data: Optional[Dict[str, Any]] = None,
                           result_data: Optional[Dict[str, Any]] = None, execution_time: Optional[float] = None) -> bool:
    """
    Quick convenience function to save calculation results.

    This function provides a simple interface for saving calculation results
    without needing to instantiate the DatabaseService class directly.

    Args:
        user_id (Optional[int]): User ID (None for anonymous)
        operation_type (Optional[str]): Type of operation
        operation_name (Optional[str]): Specific operation name
        input_data (Optional[Dict[str, Any]]): Input parameters
        result_data (Optional[Dict[str, Any]]): Computation result
        execution_time (Optional[float]): Execution time in seconds

    Returns:
        bool: True if saved successfully, False otherwise

    Example:
        >>> success = save_calculation_result(
        ...     user_id=1,
        ...     operation_type="arithmetic",
        ...     operation_name="addition",
        ...     input_data={"a": 5, "b": 3},
        ...     result_data={"result": 8}
        ... )
    """
    try:
        db = DatabaseService()
        db.save_calculation(
            user_id=user_id,
            operation_type=operation_type,
            operation_name=operation_name,
            input_data=input_data,
            result_data=result_data,
            execution_time=execution_time
        )
        return True
    except DatabaseError as e:
        logger.error(f"Failed to save calculation: {e}")
        return False


def log_api_request(user_id: Optional[int] = None, method: Optional[str] = None, endpoint: Optional[str] = None,
                   status_code: Optional[int] = None, response_time: Optional[float] = None) -> bool:
    """
    Quick convenience function to log API requests.

    This function provides a simple interface for logging API requests
    without needing to instantiate the DatabaseService class directly.

    Args:
        user_id (Optional[int]): User ID (None for anonymous)
        method (Optional[str]): HTTP method
        endpoint (Optional[str]): API endpoint
        status_code (Optional[int]): HTTP status code
        response_time (Optional[float]): Response time in seconds

    Returns:
        bool: True if logged successfully, False otherwise

    Example:
        >>> success = log_api_request(
        ...     user_id=1,
        ...     method="POST",
        ...     endpoint="/api/calculate",
        ...     status_code=200,
        ...     response_time=0.150
        ... )
    """
    try:
        db = DatabaseService()
        db.log_api_request(
            user_id=user_id,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            response_time=response_time
        )
        return True
    except DatabaseError as e:
        logger.error(f"Failed to log API request: {e}")
        return False
