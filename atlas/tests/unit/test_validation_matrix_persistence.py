"""Tests para ValidationMatrixPersistence"""
import pytest
import tempfile
import time
import os
from app.validation_matrix_persistence import (
    ValidationSnapshot, 
    ValidationMatrixPersistence, 
    ValidationMatrixRecorder,
    get_validation_persistence
)


@pytest.fixture
def temp_persistence():
    """Fixture con persistence temporal"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    persistence = ValidationMatrixPersistence(db_path)
    yield persistence
    
    # Cleanup
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


def test_validation_snapshot_serialization():
    """Test serialización de snapshots"""
    snapshot = ValidationSnapshot(
        timestamp=1234567890.0,
        total_score=85.5,
        integrity_score=90.0,
        services_count=5,
        lineage_quality=80.0,
        metadata={"test": "data"}
    )
    
    data = snapshot.to_dict()
    restored = ValidationSnapshot.from_dict(data)
    
    assert restored.timestamp == snapshot.timestamp
    assert restored.total_score == snapshot.total_score
    assert restored.metadata == snapshot.metadata


def test_persistence_save_and_retrieve(temp_persistence):
    """Test guardado y recuperación de snapshots"""
    snapshot = ValidationSnapshot(
        timestamp=time.time(),
        total_score=75.0,
        integrity_score=85.0,
        services_count=3,
        lineage_quality=70.0,
        metadata={"source": "test"}
    )
    
    # Save
    success = temp_persistence.save_snapshot(snapshot)
    assert success
    
    # Retrieve
    snapshots = temp_persistence.get_snapshots(hours_back=1)
    assert len(snapshots) == 1
    assert snapshots[0].total_score == 75.0
    assert snapshots[0].metadata["source"] == "test"


def test_persistence_filtering_by_time(temp_persistence):
    """Test filtrado por tiempo"""
    now = time.time()
    
    # Snapshot reciente
    recent = ValidationSnapshot(now, 80.0, 80.0, 5, 75.0)
    temp_persistence.save_snapshot(recent)
    
    # Snapshot viejo (simulate 2 horas atrás)
    old = ValidationSnapshot(now - 7200, 70.0, 70.0, 3, 65.0)
    temp_persistence.save_snapshot(old)
    
    # Get recent (1 hora)
    recent_snapshots = temp_persistence.get_snapshots(hours_back=1)
    assert len(recent_snapshots) == 1
    assert recent_snapshots[0].total_score == 80.0
    
    # Get all (24 horas)
    all_snapshots = temp_persistence.get_snapshots(hours_back=24)
    assert len(all_snapshots) == 2


def test_trend_analysis(temp_persistence):
    """Test análisis de tendencias"""
    now = time.time()
    
    # Create a declining trend
    temp_persistence.save_snapshot(ValidationSnapshot(
        now - 3600, 90.0, 90.0, 5, 85.0  # 1 hora atrás
    ))
    temp_persistence.save_snapshot(ValidationSnapshot(
        now - 1800, 80.0, 80.0, 5, 75.0  # 30 min atrás
    ))
    temp_persistence.save_snapshot(ValidationSnapshot(
        now, 70.0, 70.0, 4, 65.0  # ahora
    ))
    
    trends = temp_persistence.get_trend_analysis(hours_back=2)
    
    assert trends["trend"] == "analyzed"
    assert trends["snapshots_count"] == 3
    assert trends["total_score"]["first"] == 90.0
    assert trends["total_score"]["last"] == 70.0
    assert trends["total_score"]["trend"] == "degrading"
    assert trends["services_count"]["change"] == -1


def test_trend_analysis_insufficient_data(temp_persistence):
    """Test análisis con datos insuficientes"""
    trends = temp_persistence.get_trend_analysis()
    assert trends["trend"] == "insufficient_data"
    assert trends["snapshots_count"] == 0


def test_cleanup_old_snapshots(temp_persistence):
    """Test limpieza de snapshots antiguos"""
    now = time.time()
    
    # Snapshot reciente
    temp_persistence.save_snapshot(ValidationSnapshot(now, 80.0, 80.0, 5, 75.0))
    
    # Snapshot muy antiguo
    old_time = now - (35 * 24 * 3600)  # 35 días atrás
    temp_persistence.save_snapshot(ValidationSnapshot(old_time, 70.0, 70.0, 3, 65.0))
    
    # Verify both exist
    all_snapshots = temp_persistence.get_snapshots(hours_back=24*40)  # 40 días
    assert len(all_snapshots) == 2
    
    # Cleanup (default retention 30 días)
    deleted = temp_persistence.cleanup_old_snapshots()
    assert deleted == 1
    
    # Verify only recent remains
    remaining = temp_persistence.get_snapshots(hours_back=24*40)
    assert len(remaining) == 1
    assert remaining[0].total_score == 80.0


def test_persistence_stats(temp_persistence):
    """Test estadísticas de persistencia"""
    # Add some data
    temp_persistence.save_snapshot(ValidationSnapshot(
        time.time(), 80.0, 80.0, 5, 75.0
    ))
    
    stats = temp_persistence.get_stats()
    assert stats["total_snapshots"] == 1
    assert stats["oldest_timestamp"] is not None
    assert stats["newest_timestamp"] is not None
    assert stats["retention_days"] >= 30
    assert "db_path" in stats


def test_validation_recorder(temp_persistence):
    """Test ValidationMatrixRecorder"""
    recorder = ValidationMatrixRecorder(temp_persistence)
    
    # Force interval to allow recording
    recorder.persistence.snapshot_interval = 0
    
    # Record state
    success = recorder.record_current_state({"test": "recorder"})
    assert success
    
    # Verify recorded
    snapshots = temp_persistence.get_snapshots(hours_back=1)
    assert len(snapshots) == 1
    assert snapshots[0].metadata["test"] == "recorder"


def test_should_record_interval():
    """Test intervalo de recording"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    
    try:
        persistence = ValidationMatrixPersistence(db_path)
        persistence.snapshot_interval = 10  # 10 segundos
        
        recorder = ValidationMatrixRecorder(persistence)
        
        # Should record first time
        assert recorder.should_record()
        
        # Record and update timestamp
        recorder._last_snapshot = time.time()
        
        # Should not record immediately
        assert not recorder.should_record()
        
        # Wait and check again (simulate)
        recorder._last_snapshot = time.time() - 15  # 15 segundos atrás
        assert recorder.should_record()
        
    finally:
        try:
            os.unlink(db_path)
        except FileNotFoundError:
            pass


def test_global_persistence_instance():
    """Test instancia global"""
    persistence = get_validation_persistence()
    assert persistence is not None
    assert hasattr(persistence, 'save_snapshot')
    assert hasattr(persistence, 'get_snapshots')


if __name__ == "__main__":
    pytest.main([__file__])
