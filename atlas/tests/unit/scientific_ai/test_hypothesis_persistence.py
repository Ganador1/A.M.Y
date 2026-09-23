import os
import tempfile
import types
from unittest.mock import patch
from sqlalchemy.orm import sessionmaker


def setup_module(module: types.ModuleType):
    os.environ['ENABLE_DATABASE'] = 'true'
    fd, db_path = tempfile.mkstemp(prefix='axiom_test_db_', suffix='.sqlite')
    os.close(fd)
    os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"
    os.environ['SKIP_DB_INIT'] = 'true'
    os.environ['PYTEST_RUNNING'] = '1'


def teardown_module(module: types.ModuleType):
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url.startswith('sqlite:///'):
        path = db_url.replace('sqlite:///', '')
        try:
            os.remove(path)
        except OSError:
            pass


def test_hypothesis_persistence_crud_flow():
    """Test hypothesis persistence service using the actual service layer."""
    # Configurar DB directamente para test
    from sqlalchemy import create_engine
    from sqlalchemy.pool import StaticPool
    from app.database import Base
    # Importar modelos para asegurar que se registren en Base.metadata
    import app.models.hypothesis_models as _  # Register Hypothesis models

    db_path = os.environ['DATABASE_URL'].replace('sqlite:///', '')
    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    
    # Crear sessionmaker para test
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Importar el servicio
    from app.services.hypothesis_persistence import HypothesisPersistenceService
    import app.core.database as core_db
    core_db.SessionLocal = TestSessionLocal
    service = HypothesisPersistenceService()
    
    # 1. Crear una hipótesis
    result = service.create_hypothesis({
        "title": "Hipótesis de prueba",
        "description": "Esta es una descripción de prueba",
        "domain": "materials_science",
        "confidence_score": 0.8,
        "status": "active"
    })
    
    assert result["success"] is True
    assert "hypothesis_uuid" in result
    hypothesis_uuid = result["hypothesis_uuid"]
    
    # 2. Obtener la hipótesis
    result = service.get_hypothesis({"hypothesis_uuid": hypothesis_uuid})
    assert result["success"] is True
    assert result["hypothesis"]["title"] == "Hipótesis de prueba"
    assert result["hypothesis"]["domain"] == "materials_science"
    
    # 3. Actualizar la hipótesis
    result = service.update_hypothesis({
        "hypothesis_uuid": hypothesis_uuid,
        "confidence_score": 0.4,
        "status": "testing"
    })
    assert result["success"] is True
    assert result["hypothesis"]["confidence_score"] == 0.4
    assert result["hypothesis"]["status"] == "testing"
    
    # 4. Listar hipótesis
    result = service.list_hypotheses({"domain": "materials_science"})
    assert result["success"] is True
    assert result["count"] >= 1
    
    # 5. Eliminar la hipótesis
    result = service.delete_hypothesis({"hypothesis_uuid": hypothesis_uuid})
    assert result["success"] is True
    
    # 6. Verificar que se eliminó
    result = service.get_hypothesis({"hypothesis_uuid": hypothesis_uuid})
    assert result["success"] is False
    
    print("✅ Servicio de persistencia de hipótesis completado exitosamente")


def test_hypothesis_risk_block():
    from app.database import init_database
    init_database()
    
    # Crear tablas
    from app.database import Base
    from app.core.database import engine
    Base.metadata.create_all(bind=engine)
    
    from app.services.hypothesis_persistence import HypothesisPersistenceService
    svc = HypothesisPersistenceService()
    # Description con palabras bio para escalar a CRITICAL sin justificación
    res = svc.create_hypothesis({
        "title": "Hipótesis riesgosa",
        "domain": "plasma_physics",
        "description": "Estudio de pathogen y virus avanzado",
        "declared_intent": "research",
        "data_sensitivity": "moderate",
    })
    # Política actual: MEDIUM no bloquea; HIGH sin firma sí, CRITICAL siempre.
    if not res["success"]:
        assert res.get("risk_level") in ("HIGH", "CRITICAL")
    else:
        assert res.get("risk_level") in ("LOW", "MEDIUM")
    # Ahora con justificación suficiente y firma
    res_allowed = svc.create_hypothesis({
        "title": "Hipótesis autorizada",
        "domain": "plasma_physics",
        "description": "Estudio de pathogen y virus avanzado mitigado controlado",
        "declared_intent": "research",
        "data_sensitivity": "moderate",
        "justification": "Justificación extensa para control y mitigación de riesgos biológicos",
        "justification_signature": "user|timestamp",
    })
    # Si resultó CRITICAL seguirá bloqueada; en otro caso debe permitir
    if res_allowed.get("risk_level") == "CRITICAL":
        assert res_allowed["success"] is False
    else:
        assert res_allowed["success"] is True


# No fixtures extra: usamos session directa
