import os
import tempfile
import types


def setup_module(module: types.ModuleType):
    # Forzar BD sqlite temporal y habilitar DB
    os.environ['ENABLE_DATABASE'] = 'true'
    fd, db_path = tempfile.mkstemp(prefix='axiom_test_db_', suffix='.sqlite')
    os.close(fd)
    os.environ['DATABASE_URL'] = f"sqlite:///{db_path}"
    # Evitar init automático en import (rompe ciclos); inicializamos explícitamente en el test
    os.environ['SKIP_DB_INIT'] = 'true'
    # Señalizar ejecución de pytest para evitar auto init
    os.environ['PYTEST_RUNNING'] = '1'


def teardown_module(module: types.ModuleType):
    # Limpiar archivo sqlite
    db_url = os.environ.get('DATABASE_URL', '')
    if db_url.startswith('sqlite:///'):
        path = db_url.replace('sqlite:///', '')
        try:
            os.remove(path)
        except OSError:
            pass


def test_hypothesis_persistence_crud_flow():
    """Test hypothesis persistence service using the actual service layer."""
    # Configurar e inicializar DB manualmente
    from app.database import init_database
    init_database()
    
    # Importar el servicio
    from app.services.hypothesis_persistence import HypothesisPersistenceService
    
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
