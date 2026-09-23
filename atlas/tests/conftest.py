"""
Pytest configuration and fixtures for AXIOM tests
"""

import pytest
import asyncio
import os
import time
import sys
from pathlib import Path
from typing import Any, AsyncGenerator
from unittest.mock import Mock, patch


# Avoid duplicate-module import mismatches when running a single test file.
# The canonical offline-cache unit test lives at tests/unit/test_literature_offline_cache.py.
collect_ignore = [
    "unit/literature/test_literature_offline_cache.py",
]

# Quick guard: clear any already-imported top-level test modules to avoid
# 'import file mismatch' errors when multiple test files share the same
# basename (e.g., tests/unit/autonomous/test_biology_loop.py and
# tests/unit/biology/test_biology_loop.py). This runs early during pytest
# startup and is safe for the collection phase.
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

for _m in list(sys.modules):
    if _m.startswith("test_"):
        sys.modules.pop(_m, None)

# Stub heavy optional packages that cause long delays or blocking during
# import-time collection (brian2, matplotlib backends, etc.). This keeps
# test collection fast and deterministic in CI/local dev environments.
try:
    import brian2  # type: ignore
except Exception:
    import types

    sys.modules["brian2"] = types.ModuleType("brian2")
    sys.modules["brian2.__init__"] = sys.modules["brian2"]

# Also stub matplotlib GUI backends that attempt to open displays
try:
    import matplotlib
except Exception:
    import types

    mpl = types.ModuleType("matplotlib")
    mpl.use = lambda *a, **k: None
    sys.modules["matplotlib"] = mpl


try:
    import httpx  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    httpx = None  # type: ignore
try:
    from fastapi.testclient import TestClient  # type: ignore
    from fastapi import FastAPI  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    TestClient = None  # type: ignore
    FastAPI = None  # type: ignore

try:
    from sqlalchemy import create_engine  # type: ignore
    from sqlalchemy.orm import sessionmaker  # type: ignore
    from sqlalchemy.pool import StaticPool  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    create_engine = None  # type: ignore
    sessionmaker = None  # type: ignore
    StaticPool = None  # type: ignore

# Set environment variables EARLY to disable heavy imports and offline mode
os.environ.setdefault("AXIOM_DISABLE_HF", "1")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("PYTEST_RUNNING", "1")

# IMPORTANT: We use lazy loading for the app to avoid import errors during test collection.
# The main.py has many imports that can fail if optional dependencies are missing.
# Instead of importing app at module level, we defer it to fixtures that actually need it.
_app_instance = None

def _get_app():
    """Lazy-load the FastAPI app to avoid import issues during test collection.
    
    This function delays importing the app until it's actually needed,
    which prevents import errors from breaking test collection entirely.
    """
    global _app_instance
    if _app_instance is not None:
        return _app_instance
    
    import sys

    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    
    try:
        # Try main_refactored first (preferred)
        from main_refactored import app as _app
        _app_instance = _app
    except Exception:
        try:
            # Fallback to main.py
            from main import app as _app  # type: ignore
            _app_instance = _app
        except Exception:
            # Create minimal app for tests that don't need full app
            if FastAPI is not None:
                _app_instance = FastAPI(title="AXIOM Test App")
            else:
                _app_instance = None
    
    return _app_instance

# For backward compatibility, but prefer using _get_app() in fixtures
app = None  # Will be set lazily when needed


# Set test environment variables before importing anything else
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
os.environ["ENABLE_DATABASE"] = "true"
os.environ["DEBUG"] = "true"
os.environ["REDIS_URL"] = "redis://localhost:6379"
os.environ["ENABLE_REDIS_CACHE"] = "false"
os.environ["PYTEST_RUNNING"] = "true"

# Now import after environment is set
from app.config import settings

# Override settings for testing
settings.database_url = "sqlite:///:memory:"
settings.enable_database = True
settings.debug = True
settings.enable_redis_cache = False

# Now import database components si SQLAlchemy está disponible
if create_engine is not None:
    from app.database import Base  # noqa: E402
    from app.observability import metrics as obs_metrics  # noqa: E402

    # Initialize test database
    if not hasattr(Base, 'metadata') or not Base.metadata.tables:
        bootstrap_engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        # Create schema on the bootstrap engine
        Base.metadata.create_all(bind=bootstrap_engine)
        # Ensure core database globals point to bootstrap engine so get_db_session()
        # and other helpers work consistently across the test session.
        try:
            import app.core.database as core_db
            core_db.engine = bootstrap_engine
            core_db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=bootstrap_engine)
        except Exception:
            pass
else:
    Base = type("BaseStub", (), {"metadata": type("MetaStub", (), {"tables": {}})()})  # type: ignore
    obs_metrics = None  # type: ignore


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine"""
    if create_engine is None or StaticPool is None:
        pytest.skip("sqlalchemy no está disponible; se omiten fixtures de base de datos")
    # Use SQLite in-memory database for tests
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session"""
    if sessionmaker is None:
        pytest.skip("sqlalchemy no está disponible; se omiten fixtures de base de datos")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with database session"""
    app_instance = _get_app()
    
    if TestClient is None or app_instance is None:
        pytest.skip("FastAPI no está disponible; pruebas que requieren TestClient se omiten")
    
    def override_get_db():
        yield test_db

    # Try to override if the dependency exists
    try:
        from app.database import get_db as real_get_db
        app_instance.dependency_overrides[real_get_db] = override_get_db
    except ImportError:
        pass

    with TestClient(app_instance) as test_client:
        yield test_client
    
    # Clean up dependency overrides
    try:
        from app.database import get_db as real_get_db
        app_instance.dependency_overrides.pop(real_get_db, None)
    except ImportError:
        pass


@pytest.fixture(scope="session")
async def async_client() -> AsyncGenerator[Any, None]:
    """Create async test client"""
    app_instance = _get_app()
    
    if httpx is None or app_instance is None:
        pytest.skip("Dependencias HTTP async no disponibles; se omiten pruebas async_client")
    async with httpx.AsyncClient(
        app=app_instance,
        base_url="http://testserver"
    ) as client:
        yield client


@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Setup test environment variables"""
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("ENABLE_DATABASE", "true")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
    monkeypatch.setenv("ENABLE_REDIS_CACHE", "false")  # Disable Redis for tests


@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    """Configure test settings"""
    # Override settings for testing
    settings.debug = True
    settings.enable_database = True
    settings.database_url = "sqlite:///:memory:"
    settings.enable_redis_cache = False
    # Ensure there is a session factory available for tests and that the
    # metadata tables are created on an in-memory engine derived from the
    # current metadata (populated by model imports). This guarantees that
    # get_db_session() will return usable sessions that see the schema.
    try:
        from sqlalchemy import create_engine as _create_engine
        from sqlalchemy.orm import sessionmaker as _sessionmaker
        from app.database import Base
        test_engine = _create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(bind=test_engine)
        import app.core.database as core_db
        core_db.engine = test_engine
        core_db.SessionLocal = _sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    except Exception:
        # If anything goes wrong, we leave the environment to handle skipping DB tests
        pass

@pytest.fixture
def mock_database_metrics():
    """Fixture para mock de métricas de database"""
    with patch('app.core.database.db_metrics') as mock_metrics:
        mock_metrics.total_connections = 0
        mock_metrics.failed_connections = 0
        mock_metrics.total_queries = 0
        mock_metrics.slow_queries = 0
        yield mock_metrics


@pytest.fixture
def mock_database_health():
    """Fixture para mock de health checks de database"""
    with patch('app.core.database.db_health') as mock_health:
        mock_health.is_healthy = True
        mock_health.consecutive_failures = 0
        mock_health.last_check = time.time()
        yield mock_health


@pytest.fixture
def mock_tool_adapter_cache():
    """Fixture para mock de cache de tool adapters"""
    with patch('app.adapters.tool_adapter.tool_adapter_cache') as mock_cache:
        mock_cache.get.return_value = None
        mock_cache.put.return_value = None
        mock_cache.stats.return_value = {"hits": 0, "misses": 0}
        yield mock_cache


@pytest.fixture
def mock_metrics_observability():
    """Fixture para mock de métricas de observabilidad"""
    with patch('app.observability.metrics.metrics') as mock_obs_metrics:
        mock_obs_metrics.record_tool_adapter_execution = Mock()
        mock_obs_metrics.record_database_connection = Mock()
        mock_obs_metrics.record_query_performance = Mock()
        yield mock_obs_metrics


@pytest.fixture
def sample_medical_image():
    """Fixture para imagen médica de ejemplo"""
    from app.domains.medicine.imaging.medical_imaging_types import MedicalImage, ImageModality

    return MedicalImage(
        image_id="test_image_001",
        modality=ImageModality.MRI,
        pixel_spacing=(0.5, 0.5),
        slice_thickness=1.0,
        image_dimensions=(256, 256),
        number_of_frames=5,
        heart_rate=72
    )


@pytest.fixture
def sample_tool_adapter():
    """Fixture para tool adapter de ejemplo"""
    from app.adapters.tool_adapter import EchoAdapter

    return EchoAdapter()


@pytest.fixture
def database_session_with_metrics():
    """Fixture para sesión de database con métricas"""
    from app.core.database import get_db_session, db_metrics

    # Reset metrics
    db_metrics.total_connections = 0
    db_metrics.failed_connections = 0
    db_metrics.total_queries = 0

    session = get_db_session()
    yield session

    # Record metrics on cleanup
    db_metrics.record_query(100.0, is_slow=False)
    session.close()


@pytest.fixture
def circuit_breaker_adapter():
    """Fixture para adapter con circuit breaker configurado"""
    from app.adapters.tool_adapter import ToolAdapter, ToolExecutionConfig

    config = ToolExecutionConfig(
        max_retries=2,
        retry_delay=0.1,
        circuit_breaker_threshold=3,
        circuit_breaker_timeout=30.0
    )

    adapter = ToolAdapter(config=config)
    adapter.name = "test_circuit_breaker"

    # Mock the _run method to avoid NotImplementedError
    adapter._run = Mock(return_value={"result": "success"})

    return adapter


@pytest.fixture
def rate_limited_adapter():
    """Fixture para adapter con rate limiting"""
    from app.adapters.tool_adapter import ToolAdapter, ToolExecutionConfig

    config = ToolExecutionConfig(
        rate_limit=5.0,  # 5 requests per second
        max_retries=1
    )

    adapter = ToolAdapter(config=config)
    adapter.name = "test_rate_limited"

    # Mock the _run method
    adapter._run = Mock(return_value={"result": "success"})

    return adapter


@pytest.fixture(autouse=True)
def cleanup_database_state():
    """Fixture para limpiar estado de database entre tests"""
    # Skip database cleanup for now as db_metrics and db_health don't exist
    yield


@pytest.fixture(autouse=True)
def cleanup_adapter_state():
    """Fixture para limpiar estado de adapters entre tests"""
    from app.adapters.tool_adapter import get_tool_registry

    # Clear registry
    registry = get_tool_registry()
    registry._registry.clear()

    yield

    # Clear registry again after test
    registry._registry.clear()
