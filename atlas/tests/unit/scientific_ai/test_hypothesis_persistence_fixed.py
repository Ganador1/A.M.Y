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
    # Importar después de configurar env y configurar solo los modelos necesarios
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.hypothesis_models import HypothesisRecord
    
    # Crear engine y session directamente para evitar conflictos con DatabaseService
    engine = create_engine(os.environ['DATABASE_URL'], echo=False)
    
    # Solo crear tablas de hipótesis para este test
    HypothesisRecord.metadata.create_all(engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as session:
        # 1. Crear una hipótesis
        hypothesis_uuid = "test-hypothesis-uuid-1234"
        new_hypothesis = HypothesisRecord(
            hypothesis_uuid=hypothesis_uuid,
            title='Hipótesis de prueba',
            description='Esta es una descripción de prueba',
            domain='materials_science',
            confidence_score=0.8,
            status='active',
            variables=['dopant_concentration'],
            assumptions=['dispersión uniforme'],
            expected_outcome='mejora 20%'
        )
        session.add(new_hypothesis)
        session.commit()
        session.refresh(new_hypothesis)
        
        # Verificar que se creó con ID
        assert new_hypothesis.id is not None
        hypothesis_id = new_hypothesis.id
        
        # 2. Buscar por UUID
        retrieved = session.query(HypothesisRecord).filter(
            HypothesisRecord.hypothesis_uuid == hypothesis_uuid
        ).first()
        assert retrieved is not None
        assert retrieved.title == 'Hipótesis de prueba'
        assert retrieved.domain == 'materials_science'
        
        # 3. Actualizar la hipótesis
        retrieved.confidence_score = 0.4
        retrieved.status = 'testing'
        session.commit()
        session.refresh(retrieved)
        
        # 4. Verificar actualización
        updated = session.query(HypothesisRecord).filter(
            HypothesisRecord.hypothesis_uuid == hypothesis_uuid
        ).first()
        assert updated is not None
        assert updated.confidence_score == 0.4
        assert updated.status == 'testing'
        
        # 5. Eliminar la hipótesis  
        session.delete(retrieved)
        session.commit()
        
        # 6. Verificar que se eliminó
        deleted = session.query(HypothesisRecord).filter(
            HypothesisRecord.hypothesis_uuid == hypothesis_uuid
        ).first()
        assert deleted is None
        
    print("✅ CRUD de hipótesis completado exitosamente usando SQLAlchemy directo")
