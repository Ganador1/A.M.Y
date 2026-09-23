"""
Tests unitarios para Database Layer mejorado

Pruebas para:
- DatabaseMetrics: métricas de conexión y consultas
- DatabaseHealth: health checks y estado del sistema
- Circuit breaker y retry logic
- Query performance monitoring
- Connection pool monitoring
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.core.database import (
    DatabaseMetrics,
    DatabaseHealth,
    db_metrics,
    db_health,
    init_database,
    get_database_status,
    _test_connection_with_retry,
    _setup_database_events,
    get_db_session,
    close_database
)


class TestDatabaseMetrics:
    """Tests para la clase DatabaseMetrics"""

    def test_metrics_initialization(self):
        """Test inicialización de métricas"""
        metrics = DatabaseMetrics()

        assert metrics.total_connections == 0
        assert metrics.failed_connections == 0
        assert metrics.total_queries == 0
        assert metrics.slow_queries == 0
        assert metrics.connection_pool_size == 0
        assert metrics.active_connections == 0
        assert isinstance(metrics._lock, threading.Lock)

    def test_record_connection_success(self):
        """Test registro de conexión exitosa"""
        metrics = DatabaseMetrics()

        metrics.record_connection(success=True)

        assert metrics.total_connections == 1
        assert metrics.failed_connections == 0

        # Verificar thread safety
        def concurrent_connection():
            for _ in range(10):
                metrics.record_connection(success=True)

        threads = [threading.Thread(target=concurrent_connection) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert metrics.total_connections == 51  # 1 + 50

    def test_record_connection_failure(self):
        """Test registro de conexión fallida"""
        metrics = DatabaseMetrics()

        metrics.record_connection(success=False)

        assert metrics.total_connections == 1
        assert metrics.failed_connections == 1

    def test_record_query(self):
        """Test registro de consultas"""
        metrics = DatabaseMetrics()

        # Query normal
        metrics.record_query(duration_ms=100.0, is_slow=False)
        assert metrics.total_queries == 1
        assert metrics.slow_queries == 0

        # Query lenta
        metrics.record_query(duration_ms=1500.0, is_slow=True)
        assert metrics.total_queries == 2
        assert metrics.slow_queries == 1

    def test_update_pool_stats(self):
        """Test actualización de estadísticas del pool"""
        metrics = DatabaseMetrics()

        metrics.update_pool_stats(pool_size=10, active=5)

        assert metrics.connection_pool_size == 10
        assert metrics.active_connections == 5

    def test_get_stats(self):
        """Test obtener estadísticas"""
        metrics = DatabaseMetrics()
        metrics.record_connection(success=True)
        metrics.record_connection(success=False)
        metrics.record_query(500.0, is_slow=False)
        metrics.record_query(1500.0, is_slow=True)
        metrics.update_pool_stats(10, 3)

        stats = metrics.get_stats()

        assert stats["total_connections"] == 2
        assert stats["failed_connections"] == 1
        assert stats["connection_success_rate"] == 50.0
        assert stats["total_queries"] == 2
        assert stats["slow_queries"] == 1
        assert stats["slow_query_rate"] == 50.0
        assert stats["connection_pool_size"] == 10
        assert stats["active_connections"] == 3

    def test_thread_safety(self):
        """Test thread safety de las métricas"""
        metrics = DatabaseMetrics()

        def worker():
            for _ in range(100):
                metrics.record_connection(success=True)
                metrics.record_query(100.0)

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert metrics.total_connections == 1000
        assert metrics.total_queries == 1000


class TestDatabaseHealth:
    """Tests para la clase DatabaseHealth"""

    def test_health_initialization(self):
        """Test inicialización del estado de salud"""
        health = DatabaseHealth()

        assert health.is_healthy is True
        assert health.consecutive_failures == 0
        assert isinstance(health.last_check, float)

    def test_mark_healthy(self):
        """Test marcar como saludable"""
        health = DatabaseHealth()
        health.is_healthy = False
        health.consecutive_failures = 5

        health.mark_healthy()

        assert health.is_healthy is True
        assert health.consecutive_failures == 0

    def test_mark_unhealthy(self):
        """Test marcar como no saludable"""
        health = DatabaseHealth()

        health.mark_unhealthy()

        assert health.is_healthy is False
        assert health.consecutive_failures == 1

    def test_get_status(self):
        """Test obtener estado de salud"""
        health = DatabaseHealth()
        health.consecutive_failures = 3
        initial_time = health.last_check

        status = health.get_status()

        assert status["healthy"] is True
        assert status["consecutive_failures"] == 3
        assert status["last_check"] == initial_time
        assert "time_since_last_check" in status

    def test_consecutive_failures_increment(self):
        """Test incremento de fallos consecutivos"""
        health = DatabaseHealth()

        for i in range(3):
            health.mark_unhealthy()
            assert health.consecutive_failures == i + 1


class TestDatabaseInitialization:
    """Tests para inicialización mejorada de database"""

    @patch('app.core.database.settings')
    def test_init_database_disabled(self, mock_settings):
        """Test inicialización cuando database está deshabilitado"""
        mock_settings.enable_database = False

        # Should not raise exception and return early
        init_database()

    @patch('app.core.database.settings')
    @patch('app.core.database.create_engine')
    def test_init_database_sqlite_config(self, mock_create_engine, mock_settings):
        """Test configuración específica para SQLite"""
        mock_settings.enable_database = True
        mock_settings.database_url = "sqlite:///:memory:"
        mock_settings.debug = True

        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        init_database()

        # Verify SQLite-specific configuration
        mock_create_engine.assert_called_once()
        call_args = mock_create_engine.call_args[1]
        assert call_args['poolclass'] == StaticPool
        assert call_args['pool_size'] == 1
        assert call_args['max_overflow'] == 0
        assert call_args['pool_pre_ping'] is True
        assert call_args['pool_recycle'] == 3600

    @patch('app.core.database.settings')
    @patch('app.core.database.create_engine')
    def test_init_database_postgresql_config(self, mock_create_engine, mock_settings):
        """Test configuración específica para PostgreSQL"""
        mock_settings.enable_database = True
        mock_settings.database_url = "postgresql://user:pass@localhost:5432/db"
        mock_settings.debug = True
        mock_settings.database_pool_size = 10
        mock_settings.database_max_overflow = 20
        mock_settings.database_pool_timeout = 30
        mock_settings.database_pool_recycle = 3600

        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        init_database()

        # Verify PostgreSQL-specific configuration
        call_args = mock_create_engine.call_args[1]
        assert call_args['pool_size'] == 10
        assert call_args['max_overflow'] == 20
        assert call_args['pool_timeout'] == 30
        assert call_args['pool_recycle'] == 3600
        assert call_args['pool_pre_ping'] is True
        assert call_args['pool_reset_on_return'] == 'commit'

    @patch('app.core.database.settings')
    @patch('app.core.database._test_connection_with_retry')
    def test_init_database_connection_success(self, mock_test_connection, mock_settings):
        """Test inicialización exitosa con conexión"""
        mock_settings.enable_database = True
        mock_settings.database_url = "sqlite:///:memory:"

        with patch('app.core.database.create_engine') as mock_create_engine:
            mock_engine = Mock()
            mock_create_engine.return_value = mock_engine

            init_database()

            # Verify connection test was called
            mock_test_connection.assert_called_once_with(mock_engine)
            # Verify metrics were recorded
            assert db_metrics.total_connections == 1
            assert db_health.is_healthy is True

    @patch('app.core.database.settings')
    def test_init_database_connection_failure_fallback(self, mock_settings):
        """Test fallback a in-memory cuando conexión falla"""
        mock_settings.enable_database = True
        mock_settings.database_url = "sqlite:///:memory:"
        mock_settings.debug = True

        with patch('app.core.database.create_engine') as mock_create_engine:
            mock_engine = Mock()
            mock_engine.connect.side_effect = Exception("Connection failed")
            mock_create_engine.return_value = mock_engine

            init_database()

            # Should fallback to in-memory database
            assert db_metrics.total_connections == 1  # Attempt recorded
            assert db_health.is_healthy is False  # Should be marked unhealthy


class TestDatabaseConnectionRetry:
    """Tests para lógica de reintento de conexión"""

    def test_connection_with_retry_success(self):
        """Test conexión exitosa con reintento"""
        engine = create_engine("sqlite:///:memory:")

        # Should succeed on first try
        _test_connection_with_retry(engine, max_retries=3)

    def test_connection_with_retry_failure(self):
        """Test conexión que falla después de reintentos"""
        engine = Mock()
        engine.connect.side_effect = Exception("Connection failed")

        with pytest.raises(Exception):
            _test_connection_with_retry(engine, max_retries=2)

    def test_connection_with_retry_exponential_backoff(self):
        """Test backoff exponencial en reintentos"""
        engine = Mock()
        engine.connect.side_effect = [Exception("Fail 1"), Exception("Fail 2"), None]

        with patch('time.sleep') as mock_sleep:
            _test_connection_with_retry(engine, max_retries=3)

            # Should sleep with exponential backoff: 1, 2, 4 seconds
            assert mock_sleep.call_count == 2
            mock_sleep.assert_any_call(1)  # 2^0
            mock_sleep.assert_any_call(2)  # 2^1


class TestDatabaseStatus:
    """Tests para función de estado de database"""

    def test_get_database_status_not_initialized(self):
        """Test estado cuando database no está inicializado"""
        with patch('app.core.database.engine', None):
            status = get_database_status()

            assert status["status"] == "not_initialized"

    def test_get_database_status_initialized(self):
        """Test estado completo cuando database está inicializado"""
        # Mock engine and pool
        mock_engine = Mock()
        mock_pool = Mock()
        mock_engine.pool = mock_pool
        mock_pool.size.return_value = 10
        mock_pool.checkedin.return_value = 5
        mock_pool.checkedout.return_value = 3
        mock_pool.overflow.return_value = 2

        with patch('app.core.database.engine', mock_engine):
            status = get_database_status()

            assert "status" in status
            assert "health" in status
            assert "metrics" in status
            assert "pool" in status
            assert "engine" in status

            # Verify pool stats
            assert status["pool"]["size"] == 10
            assert status["pool"]["checked_in"] == 5
            assert status["pool"]["checked_out"] == 3
            assert status["pool"]["overflow"] == 2


class TestDatabaseSessionManagement:
    """Tests para manejo de sesiones de database"""

    def test_get_db_session_not_initialized(self):
        """Test obtener sesión cuando database no está inicializado"""
        with patch('app.core.database.SessionLocal', None):
            with pytest.raises(RuntimeError, match="Database not initialized"):
                get_db_session()

    def test_get_db_session_health_check(self):
        """Test que health check se ejecuta automáticamente"""
        with patch('app.core.database.SessionLocal') as mock_session:
            with patch('app.core.database.db_health.last_check', time.time() - 120):  # 2 minutes ago
                with patch('app.core.database._perform_health_check') as mock_health_check:
                    get_db_session()

                    mock_health_check.assert_called_once()

    def test_close_database_with_metrics(self):
        """Test cierre de database con métricas"""
        mock_engine = Mock()
        mock_engine.dispose = Mock()

        with patch('app.core.database.engine', mock_engine):
            with patch.object(db_metrics, 'get_stats') as mock_get_stats:
                mock_get_stats.return_value = {"test": "stats"}

                close_database()

                mock_engine.dispose.assert_called_once()
                mock_get_stats.assert_called_once()


class TestDatabaseEventListeners:
    """Tests para event listeners de database"""

    def test_setup_database_events(self):
        """Test configuración de event listeners"""
        mock_engine = Mock()

        # Should not raise exception
        _setup_database_events(mock_engine)

        # Verify event listeners were set up
        assert len(mock_engine.event_listeners) > 0

    def test_query_timing_events(self):
        """Test event listeners para timing de queries"""
        engine = create_engine("sqlite:///:memory:")
        _setup_database_events(engine)

        with engine.connect() as conn:
            # Execute a simple query
            conn.execute(text("SELECT 1"))

            # Verify query was recorded
            assert db_metrics.total_queries == 1
            assert db_metrics.slow_queries == 0

    def test_slow_query_detection(self):
        """Test detección de consultas lentas"""
        engine = create_engine("sqlite:///:memory:")
        _setup_database_events(engine)

        # Mock a slow query by patching time.time
        with patch('time.time') as mock_time:
            mock_time.side_effect = [1000, 1001.5]  # 1.5 seconds difference

            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

                # Should detect as slow query
                assert db_metrics.slow_queries == 1
